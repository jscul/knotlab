"""Build overlapping groups from live knots and dead knots with prescribed neighbours.

The search uses a connected simple candidate graph. Each maximal clique of three
or more is chosen as either a block or a group. Pair blocks supply the other
candidate pairs. One live knot touching one group gets one leftover distinction
and one endless chain. Other hand-chosen leftovers give only finite points.
"""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
import sys
from time import process_time


def subsets(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask_of(items):
    return sum(1 << a for a in items)


def maximal_cliques(adj):
    def visit(part, possible, excluded):
        if not possible | excluded:
            yield part
            return
        pivot = max(subsets(possible | excluded), key=lambda i: (possible & adj[i]).bit_count())
        for v in subsets(possible & ~adj[pivot]):
            bit = 1 << v
            yield from visit(part | bit, possible & adj[v], excluded & adj[v])
            possible ^= bit
            excluded |= bit
    return list(visit(0, (1 << len(adj)) - 1, 0))


def groups(adj, blocks):
    large = [s for s in maximal_cliques(adj)
             if s.bit_count() > 2 and all(s & ~block for block in blocks)]
    for v, ns in enumerate(adj):
        for w in subsets(ns >> (v + 1)):
            pair = (1 << v) | (1 << (v + 1 + w))
            if all(pair & ~s for s in large):
                large.append(pair)
    return large


def parent_rule(parents):
    owners = {}
    for i, row in enumerate(parents):
        for p in subsets(row):
            owners[p] = owners.get(p, 0) | (1 << i)
    adj = [0] * len(parents)
    for block in owners.values():
        for v in subsets(block):
            adj[v] |= block ^ (1 << v)
    return groups(adj, owners.values())


def pieces(n, blocks):
    adj = [0] * n
    for block in blocks:
        for v in subsets(block):
            adj[v] |= block ^ (1 << v)
    return adj


def generate_starts(rng):
    n = rng.choice([5, 6, 7, 8])
    density = rng.choice([.36, .47, .53, .61, .69, .76, .82])
    adj = [0] * n
    for u, v in combinations(range(n), 2):
        if rng.random() < density:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    seen = 1
    while True:
        enlarged = seen
        for v in subsets(seen):
            enlarged |= adj[v]
        if enlarged == seen:
            break
        seen = enlarged
    if seen.bit_count() < n:
        return
    cliques = maximal_cliques(adj)
    big = [c for c in cliques if c.bit_count() >= 3]
    if not big:
        return
    for _ in range(3):
        kept = [c for c in big if rng.randrange(2)]
        cells = [c for c in big if c not in kept]
        if not cells:
            continue
        blocks = kept[:]
        for i in range(n):
            for j in subsets(adj[i] & ~((1 << (i + 1)) - 1)):
                pair = (1 << i) | (1 << j)
                if all(pair & ~s for s in kept):
                    blocks.append(pair)
        outside = [b for b in blocks if all(b & ~c for c in cells)]
        rank = sum(b.bit_count() - 1 for b in outside + cells) - n + 1
        filled = sum(max(0, (b & c).bit_count() - 1) for b in outside for c in cells)
        if rank != filled:
            continue
        first = groups(adj, blocks)
        d = [sum(bool(s & (1 << i)) for s in first) for i in range(n)]
        ends = [i for i, v in enumerate(d) if v == 1]
        if not ends:
            continue
        site = rng.choice(ends)
        opened = d.copy()
        opened[site] = 2
        if rng.randrange(2):
            other = rng.choice([i for i in range(n) if i != site])
            opened[other] = max(3, d[other] + 1)
        yield {'live': n, 'blocks': [list(subsets(s)) for s in blocks],
               'opened': opened, 'chain_site': site, 'rank': rank, 'filled': filled}


def realize(fixture):
    n, opens = fixture['live'], fixture['opened']
    raw = list(fixture['blocks'])
    for v in range(n):
        deg = sum(v in block for block in raw)
        raw += [[v] for _ in range(max(0, 3 - opens[v] - deg))]
    if len(raw) < 3:
        raise ValueError('at least three dead knots are required for this construction')
    stars = [[] for _ in range(n + len(raw))]
    label = 0
    def share(a, b):
        nonlocal label
        stars[a].append(label)
        stars[b].append(label)
        label += 1
    for j, block in enumerate(raw):
        for v in block:
            share(v, n + j)
        share(n + j, n + (j + 1) % len(raw))
    for v, count in enumerate(opens):
        stars[v].extend(range(label, label + count))
        label += count
    return stars


class TooWide(Exception):
    pass


def core(fixture, horizon, cap):
    n = fixture['live']
    blocks = [mask_of(s) for s in fixture['blocks']]
    first = groups(pieces(n, blocks), blocks)
    supports = [[1 << i for i in range(n)], first.copy()]
    parents = [[] for _ in range(n)], first.copy()
    parents = list(parents)
    point = n
    chain = 0
    for v, count in enumerate(fixture['opened']):
        left = count - sum(bool(s & (1 << v)) for s in first)
        for _ in range(left):
            supports[1].append(1 << v | 1 << point)
            parents[1].append(1 << v)
            if v == fixture['chain_site']:
                chain = 1 << point
            point += 1
    assert chain
    for round_no in range(2, horizon + 2):
        if len(parents[-1]) > cap:
            raise TooWide
        current = parent_rule(parents[-1])
        parents.append(current)
        prev = supports[-1]
        def support(row):
            result = 0
            for v in subsets(row):
                result |= prev[v]
            return result
        supports.append([support(row) for row in current])
    return parents, supports, chain


def check_products(fixture, horizon=7, cap=65):
    parents, supp, chain = core(fixture, horizon, cap)
    grades = []
    for t in range(horizon + 2):
        grades.append([(r, v) for r in range(t + 1) for v, s in enumerate(supp[r])
                       if r == t or s & chain])
    def previous(key, t):
        r, v = key
        out = [(r - 1, a) for a in subsets(parents[r][v])
               if r == t or supp[r - 1][a] & chain]
        return out if r == t else [*out, key]
    for t in range(1, horizon + 1):
        grade = grades[t]
        if len(grade) > cap:
            raise TooWide
        rank = {key: i for i, key in enumerate(grade)}
        oldrank = {key: i for i, key in enumerate(grades[t - 1])}
        previous_sets = [mask_of(oldrank[p] for p in previous(key, t)) for key in grade]
        predicted = [mask_of(rank[p] for p in previous(key, t + 1)) for key in grades[t + 1]]
        actual_groups = parent_rule(previous_sets)
        planned = Counter(row for row in predicted if row.bit_count() > 1)
        actual = Counter(actual_groups)
        if planned != actual:
            return {'round group differs': t + 1, 'missing': [list(subsets(s)) for s in (actual - planned).elements()],
                    'extra': [list(subsets(s)) for s in (planned - actual).elements()],
                    'births': grade, 'parents': [list(subsets(row)) for row in previous_sets]}
        for v, key in enumerate(grade):
            demand = sum(bool(row & (1 << v)) for row in actual_groups)
            children = sum(bool(row & (1 << v)) for row in predicted)
            ordinary = max(demand, 3 - previous_sets[v].bit_count(), 1)
            if ordinary != children:
                return {'round fresh differs': t, 'birth': key, 'predicted': children, 'ordinary': ordinary,
                        'parents': previous(key, t)}
    return None


def explicit_forecast(fixture, stars, horizon):
    parents, support, chain = core(fixture, horizon, 200)
    signatures = {}
    for v in range(fixture['live']):
        signatures[0, v, 0] = ('start', 0, 0, len(stars[v]))
    out = []
    for t in range(1, horizon + 1):
        coarse, detailed = Counter(), Counter()
        for r in range(1, t + 1):
            length = t - r
            for v, mask in enumerate(support[r]):
                carries = bool(mask & chain)
                if length and not carries:
                    continue
                keys = [(r - 1, u, length) for u in subsets(parents[r][v])
                        if not length or support[r - 1][u] & chain]
                if length:
                    keys.append((r, v, length - 1))
                p = len(keys)
                f = sum(bool(row & 1 << v) for row in parents[r + 1]) + int(carries)
                sig = ('offshoot' if p == 1 else 'join', p, f, p + f)
                signatures[r, v, length] = sig
                coarse[sig] += 1
                detailed[(sig, tuple(sorted(signatures[k] for k in keys)))] += 1
        out.append({'n': sum(coarse.values()), 'sig0': sorted([list(s), v] for s, v in coarse.items()),
                    'sig1': sorted([[list(s), [list(a) for a in pp]], v] for (s, pp), v in detailed.items())})
    return out


def certify(fixture, horizon):
    here = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(here / 'LOOK-ALIKE-20261126-001'))
    sys.path.insert(0, str(here / 'LATE-VIEWS-20261126-001'))
    import alike
    import late
    stars = realize(fixture)
    forecast = explicit_forecast(fixture, stars, horizon)
    observed = {}
    for law in ('nae', 'parity'):
        m = late.Map(stars, law)
        reads = alike.grow(stars, rounds=horizon, knot_law=law)
        assert reads['end'] == 'rounds' and m.cls == 'in' and all(t for _, t, _ in m.pieces)
        row_diffs = {}
        for reading in ('sig0', 'sig1'):
            row_diffs[reading] = [i + 1 for i, (actual, predicted) in enumerate(zip(reads['rows'], forecast))
                                  if actual[reading] != predicted[reading]]
        observed[law] = {'map class': m.cls, 'stratum': m.stratum, 'components': m.pieces,
                         'differing rounds': row_diffs, 'rows': reads['rows']}
    return {'fixture': fixture, 'stars': stars, 'predicted': forecast, 'ordinary': observed,
            'first discrepancy in parent rule': check_products(fixture)}


def projection_gates(stars):
    """Any local allowed row extends if each remaining component has a loose distinction.

    Hold the proposed row fixed. In each remaining component choose a knot with
    a loose distinction as root. Assign arbitrary values off a spanning tree,
    reserving that loose distinction. Each nonroot knot, visited after its
    children, can satisfy either law by setting its one distinction shared
    with its parent. At the root use the reserved loose distinction.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'tools'))
    from knotlab.cli import main as canonical_check
    owners = {}
    for v, row in enumerate(stars):
        for d in row:
            owners.setdefault(d, []).append(v)
    assert all(1 <= len(w) <= 2 for w in owners.values()) and min(map(len, stars)) >= 3
    loose = {w[0] for w in owners.values() if len(w) == 1}
    neighbours = [set() for _ in stars]
    for w in owners.values():
        if len(w) == 2:
            a, b = w
            neighbours[a].add(b)
            neighbours[b].add(a)
    for removed in range(len(stars)):
        unseen = set(range(len(stars))) - {removed}
        while unseen:
            comp = set()
            stack = [next(iter(unseen))]
            while stack:
                v = stack.pop()
                if v not in unseen:
                    continue
                unseen.remove(v)
                comp.add(v)
                stack.extend(neighbours[v] & unseen)
            assert comp & loose
    checks = {}
    for m in sorted(set(map(len, stars))):
        labels = ['x' + str(i) for i in range(m)]
        for law in ('nae', 'parity'):
            # The extension argument identifies the entire projection with this local law.
            excluded = [row for row in product((0, 1), repeat=m)
                        if (len(set(row)) == 1 if law == 'nae' else sum(row) % 2)]
            cnf = ';'.join(' '.join(('~' if v else '') + s for s, v in zip(labels, row))
                           for row in excluded)
            with redirect_stdout(StringIO()) as buf:
                canonical_check(['check', '--cnf', cnf, '--loops', *labels[:-1],
                                 '--contact', labels[-1], '--json'])
            result = json.loads(buf.getvalue())
            assert result['is_knot']
            checks[f'{law} {m}'] = [result['binding'], result['loss_on_erasure'], result['coexistence']]
    return checks


def review(sample_path, horizon, check_gates):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import order
    import twins
    result = {}
    first = json.loads(sample_path.read_text())['fixture']
    for label in ('drawn start', 'one fewer loose distinction at live knot 1'):
        fixture = {**first, 'opened': first['opened'].copy()}
        if label != 'drawn start':
            fixture['opened'][1] -= 1
        run = certify(fixture, horizon)
        parents, _, _ = core(fixture, horizon, 200)
        entry = {'open counts': fixture['opened'], 'core sizes including grade zero': list(map(len, parents)),
                 'forecast totals': [r['n'] for r in run['predicted']], 'laws': {}}
        for law, actual in run['ordinary'].items():
            prediction, why = order.predict_nodes(run['stars'], horizon, law, groups=True)
            assert why == 'predicted' and prediction == run['predicted']
            entry['laws'][law] = {'growth totals': [r['n'] for r in actual['rows']],
                                  'differing rounds': actual['differing rounds'], 'matches study forecast': True,
                                  'shared-parent test in study': twins.twins(run['stars'], law)}
        if check_gates:
            entry['projected starting laws by arity, K1 K2 K3'] = projection_gates(run['stars'])
        result[label] = entry
    return result


def search(args):
    rng = random.Random(args.seed)
    counts = Counter()
    best, best_size = None, (10**6, 10**6)
    for index in range(args.count):
        for fixture in generate_starts(rng):
            counts['admitted chain starts'] += 1
            stars = realize(fixture)
            size = (len(stars), max(map(len, stars)))
            if args.small and size >= best_size:
                continue
            try:
                gap = check_products(fixture)
            except TooWide:
                counts['width limit'] += 1
                continue
            if gap:
                row = {'graph draw': index + 1, 'fixture': fixture, 'difference': gap}
                if args.small:
                    best, best_size = row, size
                else:
                    return {**row, 'starts': counts}
    if best:
        return {**best, 'graph draws': args.count, 'starts': counts}
    return {'graph draws': args.count, 'starts': counts}


if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (100, 105))
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--seed', type=int, default=684307)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--rounds', type=int, default=8)
    parser.add_argument('--review', action='store_true')
    parser.add_argument('--gates', action='store_true')
    args = parser.parse_args()
    start = process_time()
    if args.review:
        result = review(args.input, args.rounds, args.gates)
    elif args.input:
        result = certify(json.loads(args.input.read_text())['fixture'], args.rounds)
    else:
        result = search(args)
    result['CPU seconds'] = process_time() - start
    print(json.dumps(result))
