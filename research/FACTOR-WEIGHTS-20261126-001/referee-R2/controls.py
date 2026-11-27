"""Exact comparisons of single distinctions, full readers, and recorded counting rules."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path
import resource
from time import perf_counter


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
BITS = (0, 1)


def states(width, rules):
    for word in product(BITS, repeat=width):
        for law, row in rules:
            total = sum(word[i] for i in row)
            if law == "nae":
                ok = 0 < total < len(row)
            else:
                assert law in ("odd", "even")
                ok = total % 2 == (law == "odd")
            if not ok:
                break
        else:
            yield word


def minors(weights, scopes):
    width = len(next(iter(weights)))
    pairs = nonempty = full = failed = 0
    for i, j in combinations(range(width), 2):
        if any(i in row and j in row for row in scopes):
            continue
        pairs += 1
        tables = defaultdict(lambda: [0] * 4)
        for word, weight in weights.items():
            rest = tuple(v for n, v in enumerate(word) if n != i and n != j)
            tables[rest][2 * word[i] + word[j]] = weight
        for a, b, c, d in tables.values():
            nonempty += 1
            full += bool(a and b and c and d)
            failed += a * d != b * c
    return dict(pairs=pairs, nonempty=nonempty, full=full, failed=failed)


def rank_controls():
    rows = [(0, 1, 2), (3, 4, 5)]
    base = list(states(6, [('even', row) for row in rows]))
    w = {s: 1 + (s == (0,) * 6) for s in base}
    small = (0, 0, 0), (0, 1, 1)
    block = [[w[a + b] for b in small] for a in small]
    assert block == [[2, 1], [1, 1]]
    together = list(states(4, [('even', (0, 2, 3)), ('even', (1, 2, 3))]))
    marginal = [[0] * 2 for _ in BITS]
    for a, b, m, n in together:
        marginal[a][b] += 1
    three = [(0, 1, 3), (1, 2, 4), (2, 0, 5)]
    tied = {s: 1 + (s[:3] == (1, 1, 1)) for s in states(6, [('nae', row) for row in three])}
    return dict(disjoint=dict(states=len(w), mass=sum(w.values()), block=block, **minors(w, rows)),
                two_shared=dict(states=len(together), marginal=marginal),
                three_shared=dict(states=len(tied), mass=sum(tied.values()), **minors(tied, three)))


def fair_reveal(allowed, order):
    prefixes = {(): Fraction(1)}
    for end in range(1, len(order) + 1):
        next_values = defaultdict(set)
        for word in allowed:
            prefix = tuple(word[i] for i in order[:end - 1])
            next_values[prefix].add(word[order[end - 1]])
        prefixes = {p + (v,): prefixes[p] / len(choices)
                    for p, choices in next_values.items() for v in choices}
    return {s: prefixes[tuple(s[i] for i in order)] for s in allowed}


def fair_controls():
    rows = [(0, 2, 3), (1, 2, 3)]
    allowed = list(states(4, [('nae', row) for row in rows]))
    failing_orders = 0
    pooled = Counter()
    for order in permutations(range(4)):
        weights = fair_reveal(allowed, order)
        assert sum(weights.values()) == 1
        failing_orders += bool(minors(weights, rows)['failed'])
        pooled.update(weights)
    w = fair_reveal(allowed, range(4))
    table = [[w[(a, b, 1, 0)] for b in BITS] for a in BITS]
    return dict(states=len(w), orders=24, failing_orders=failing_orders, table=table,
                determinant=table[0][0]*table[1][1] - table[0][1]*table[1][0],
                pooled=minors(pooled, rows))


def swap_witness(weights, scopes):
    """Swap distinct whole groups of values. Every rule must keep its two local words."""
    for u, v in combinations(weights, 2):
        groups = [{i} for i in range(len(u)) if u[i] != v[i]]
        for row in scopes:
            hits = [g for g in groups if any(i in row for i in g)]
            if len(hits) > 1:
                groups = [g for g in groups if g not in hits] + [set.union(*hits)]
        for g in groups if len(groups) > 1 else ():
            x = tuple(v[i] if i in g else u[i] for i in range(len(u)))
            y = tuple(u[i] if i in g else v[i] for i in range(len(u)))
            assert x in weights and y in weights
            if weights[u]*weights[v] != weights[x]*weights[y]:
                for row in scopes:
                    before = sorted(tuple(s[i] for i in row) for s in (u, v))
                    after = sorted(tuple(s[i] for i in row) for s in (x, y))
                    assert before == after
                return dict(words=[''.join(map(str, s)) for s in (u, v, x, y)],
                            weights=[weights[s] for s in (u, v, x, y)])


def log_fit(weights, scopes):
    """Check consistency of the exact linear system for base-two log weights on support."""
    basis = {}
    for word, weight in weights.items():
        assert weight in (1, Fraction(1, 2))
        row = {(k, tuple(word[i] for i in scope)): Fraction(1)
               for k, scope in enumerate(scopes)}
        rhs = Fraction(0 if weight == 1 else -1)
        while row:
            key = min(row)
            coefficient = row[key]
            if key not in basis:
                basis[key] = ({p: c / coefficient for p, c in row.items()}, rhs / coefficient)
                break
            other, value = basis[key]
            for p, c in other.items():
                row[p] = row.get(p, 0) - coefficient * c
                if not row[p]:
                    del row[p]
            rhs -= coefficient * value
        else:
            if rhs != 0:
                return False
    return True


def shared_fresh(limit):
    rows = json.loads((RESEARCH / 'TWO-COUNTINGS-20261125-001A/structures.json').read_text())['eleven (start)']
    names = sorted(set(d for _, row in rows for d in row))
    old = [(law, tuple(names.index(d) for d in row)) for law, row in rows]
    n = len(names)
    source = list(states(n, old))
    result = []
    for a, b in list(product((2, 3), repeat=2))[:limit]:
        new = [(names.index('x1'), names.index(f'x{a}'), n),
               (names.index('y1'), names.index(f'y{b}'), n)]
        scopes = [row for _, row in old] + new
        weights = {}
        lost = 0
        for s in source:
            children = [s + (z,) for z in BITS
                        if all(0 < sum((s + (z,))[i] for i in row) < 3 for row in new)]
            if not children:
                lost += 1
            for c in children:
                weights[c] = Fraction(1, len(children))
        result.append(dict(settings=[a-2, b-2], old=len(source), lost=lost, children=len(weights),
                           scale='unit weight per old state before losses', **minors(weights, scopes),
                           swap=swap_witness(weights, scopes), log_fit=log_fit(weights, scopes)))
    return dict(names=names + ['z'], histories=result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--histories', type=int, choices=range(1, 5), required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2**30, 2**30))
    start = perf_counter()
    result = dict(rank=rank_controls(), fair_reveal=fair_controls(), shared_fresh=shared_fresh(args.histories))
    result.update(seconds=round(perf_counter()-start, 4),
                  peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print(json.dumps(result, indent=2, default=str))
