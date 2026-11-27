"""Exact checks of archived readings and of both policy endpoints."""
import argparse
import os
import subprocess
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path

from rebuild import BITS, const, marginal, nae, normalized, old_words, table, tv

ROOT = Path(__file__).resolve().parents[3]


def funding(p):
    """Two fair terminal bits suffice for the affected pair of readings."""
    cells = {(x, y): Counter() for x, y in product(BITS, repeat=2)}
    ready = Counter()
    for u, v, r, s in product(BITS, repeat=4):
        mass = (p if v else 1-p) / 8
        for x, y in cells:
            f = (x == u and y == v)
            cells[x, y][(r if f else 0, (s if u and v else r) if f else 0)] += mass
        for choose_short in BITS:
            address = v if choose_short else 1-v
            ready[choose_short] += mass * (u == 0 and address == v)
    return cells, ready


def correlations(cells):
    return tuple(sum((-1)**(a ^ b) * p for (a, b), p in normalized(t).items())
                 for t in cells.values())


def score(e):
    return max(abs(sum(e)-2*x) for x in e)


def guessed(soft):
    def old(x_of_pq, y):
        cells = Counter()
        for p, q, r in product(BITS, repeat=3):
            s = q ^ (p & r)
            x = x_of_pq(p, q)
            a = ((3 if x == p else 1) if soft else int(x == p))
            b = ((3 if y == r else 1) if soft else int(y == r))
            cells[(p, q), (r, s)] += a * b
        return cells
    cells = {}
    for x, y in product(BITS, repeat=2):
        t = Counter()
        for ((p, q), (r, s)), n in old(lambda *_, x=x: x, y).items():
            t[q, s] += n
        cells[x, y] = t
    d = []
    for y in BITS:
        baseline, check = [marginal(old(fn, y), 1)
                           for fn in (lambda *_: 0, lambda p, q: q)]
        d.append(tv(baseline, check))
    return correlations(cells), d


def four_types():
    # Each side's type matches the address with count 2 and otherwise count 1.
    cells = {}
    for x, y in product(BITS, repeat=2):
        out = Counter()
        for i, j, u in product(BITS, repeat=3):
            v = u ^ (i & (1-j))
            a, b = u ^ (x & i), v ^ (y & (1-j))
            out[a, b] += (1 + (x == i)) * (1 + (y == j))
        cells[x, y] = out
    return cells


def post_only():
    # 1/4 gain, a common zero on a stall, and unbiased payload bits on a gain.
    e = (1, Q(1, 2), Q(1, 2), Q(-1, 2))
    cells = {}
    margins = []
    for (x, y), t in zip(product(BITS, repeat=2), e):
        full = Counter({((0, 0), (0, 0)): Q(3, 4)})
        for a, b in product(BITS, repeat=2):
            full[(1, a), (1, b)] = (1 + (-1)**(a ^ b)*t) * Q(1, 16)
        margins.append((marginal(full, 0), marginal(full, 1)))
        out = Counter()
        for ((_, a), (_, b)), p in full.items():
            out[a, b] += p
        cells[x, y] = out
    assert len(set(tuple(sorted(m[0].items())) for m in margins)) == 1
    assert len(set(tuple(sorted(m[1].items())) for m in margins)) == 1
    return correlations(cells)


def diameter(rows, party):
    support = sorted({k[party] for k in rows})
    span = []
    for y in BITS:
        distributions = set()
        for bits in product(BITS, repeat=len(support)):
            settings = [const(y), const(y)]
            settings[party] = dict(zip(support, bits)).__getitem__
            law = marginal(table(rows, *settings), 1-party)
            distributions.add(tuple(sorted(law.items())))
        span.append(max(tv(dict(p), dict(q)) for p, q in combinations(distributions, 2)))
    return span


def rule_checks(pilot):
    # Project all full allowed assignments, then submit that exact projection
    # to the canonical forgetting test. No formula from the study is executed.
    rules = [
        ('N', (0, 1, 6)), ('N', (0, 2, 7)), (0, (1, 8, 9)), (1, (2, 8, 9)),
        (0, (4, 10, 11)), (1, (6, 10, 11)), (1, (3, 4, 5, 7)),
    ]
    def holds(w, rule):
        law, indices = rule
        bits = tuple(w[i] for i in indices)
        return nae(*bits) if law == 'N' else sum(bits) % 2 == law
    old = [w for w in product(BITS, repeat=12) if all(holds(w, r) for r in rules)]
    def check_projected(words, indices):
        import json
        projection = {tuple(w[i] for i in indices) for w in words}
        names = [f'p{i}' for i in range(len(indices))]
        missing = set(product(BITS, repeat=len(indices))) - projection
        cnf = ';'.join(' '.join('~'*v + n for n, v in zip(names, values))
                       for values in sorted(missing))
        raw = subprocess.check_output(
            [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf,
             '--loops', *names[:-1], '--contact', names[-1], '--json'],
            cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT/'tools')),
        )
        result = json.loads(raw)
        assert result['is_knot'], result
    groups = [(old, rules)]
    if not pilot:
        for x, y in product(BITS, repeat=2):
            added = [('N', (0, 1+x, 12)), ('N', (3, 4+y, 13))]
            words = [w + (a,b) for w in old for a,b in product(BITS, repeat=2)
                     if all(holds(w+(a,b), r) for r in added)]
            groups.append((words, rules + added))
    count = 0
    for words, current in groups:
        for _, indices in current[:1] if pilot else current:
            check_projected(words, indices)
            count += 1
    print('projected rules passing K1-K3', count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    rule_checks(args.pilot)
    cells, ready = funding(Q(1, 2))
    print('whole-round counts in 32 units', [[32*t[a,b] for a,b in product(BITS, repeat=2)] for t in cells.values()])
    print('balanced / tilted funding scores', score(correlations(cells)), score(correlations(funding(Q(3,4))[0])))
    print('funding probabilities at fixed Alice if Bob leaves/repairs shortage', dict(ready))
    for soft in BITS:
        e, d = guessed(soft)
        print('guessed settings, soft', soft, 'correlations', *map(str,e), 'CHSH', score(e), 'TV vs fixed', *map(str,d))
    cells = four_types()
    print('four-type scored binary table', *map(str,correlations(cells)), 'outcomes in units of 1/18',
          [[t[a,b] for a,b in product(BITS, repeat=2)] for t in cells.values()])
    print('post-only correlations', *map(str,post_only()), 'CHSH', score(post_only()))
    if not args.pilot:
        rows = old_words(4096)
        for side in BITS:
            print('seven-knot sender', side, 'largest TV between two policies by receiver setting',
                  *map(str, diameter(rows, side)))
