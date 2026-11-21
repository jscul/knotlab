"""Independent attached-rooted-tree enumeration, with a literal six-holder Prüfer audit."""

from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, combinations_with_replacement, product
from math import comb, factorial, prod
from pathlib import Path
import heapq
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name


def compositions(total, parts, at_least=1):
    if parts == 1:
        if total >= at_least:
            yield (total,)
        return
    for first in range(at_least, total - (parts - 1) * at_least + 1):
        for tail in compositions(total - first, parts - 1, at_least):
            yield (first,) + tail


def partitions(total, floor=1):
    if total == 0:
        yield ()
    else:
        for first in range(floor, total + 1):
            for tail in partitions(total - first, first):
                yield (first,) + tail


@cache
def rooted(size):
    result = []
    for lengths in partitions(size - 1):
        blocks = (combinations_with_replacement(rooted(n), copies)
                  for n, copies in Counter(lengths).items())
        for order in product(*blocks):
            branches = tuple(sorted(x for group in order for x in group))
            result.extend((flag, branches) for flag in (0, 1))
    return tuple(result)


def images(cycle):
    for seq in (cycle, tuple(reversed(cycle))):
        for start in range(len(cycle)):
            yield seq[start:] + seq[:start]


@cache
def canonical(cycle):
    return min(images(cycle))


@cache
def rooted_aut(tree):
    _, branches = tree
    return prod(rooted_aut(x) for x in branches) * prod(factorial(n) for n in Counter(branches).values())


@cache
def rooted_extras(tree):
    flag, branches = tree
    return flag + sum(rooted_extras(x) for x in branches)


def automorphisms(code):
    return sum(seq == code for seq in images(code)) * prod(rooted_aut(x) for x in code)


@cache
def undecorated_branch(tree):
    return (0, tuple(sorted(undecorated_branch(x) for x in tree[1])))


def undecorated(code):
    return canonical(tuple(undecorated_branch(x) for x in code))


def decorated_codes(n):
    seen = set()
    for length in range(3, n + 1):
        for sizes in compositions(n, length):
            for sequence in product(*(rooted(s) for s in sizes)):
                code = canonical(sequence)
                if code not in seen:
                    seen.add(code)
                    yield code


def encode(n, pairs, flags):
    adj = [set() for _ in range(n)]
    for a, b in pairs:
        adj[a].add(b)
        adj[b].add(a)
    degree = list(map(len, adj))
    leaves = [u for u, d in enumerate(degree) if d == 1]
    while leaves:
        u = leaves.pop()
        if degree[u] == 0:
            continue
        degree[u] = 0
        for v in adj[u]:
            if degree[v]:
                degree[v] -= 1
                if degree[v] == 1:
                    leaves.append(v)
    core = {v for v, d in enumerate(degree) if d}
    assert len(core) >= 3 and all(degree[v] == 2 for v in core)
    start = min(core)
    u, v = start, min(adj[start] & core)
    order = [start]
    while v != start:
        order.append(v)
        u, v = v, next(z for z in adj[v] & core if z != u)

    def branch(u, parent):
        return (flags[u], tuple(sorted(branch(v, u) for v in adj[u] if v != parent and v not in core)))
    return canonical(tuple(branch(v, None) for v in order))


def labelled_trees(n):
    for word in product(range(n), repeat=n - 2):
        deg = [1] * n
        for x in word:
            deg[x] += 1
        leaves = [h for h, d in enumerate(deg) if d == 1]
        heapq.heapify(leaves)
        edges = []
        for x in word:
            leaf = heapq.heappop(leaves)
            edges.append(tuple(sorted((leaf, x))))
            deg[x] -= 1
            if deg[x] == 1:
                heapq.heappush(leaves, x)
        edges.append(tuple(sorted(leaves)))
        yield frozenset(edges)


def six_literal(expected):
    n = 6
    all_pairs = frozenset(combinations(range(n), 2))
    origin_sets = []
    for tree in labelled_trees(n):
        origin_sets.extend(tree | {added} for added in all_pairs - tree)
    multiplicity = Counter(origin_sets)
    distinct, histories, encodings = Counter(), Counter(), {}
    for pairs, l in multiplicity.items():
        codes = [encode(n, pairs, flags) for flags in product((0, 1), repeat=n)]
        assert all(len(c) == l for c in codes)
        distinct.update(codes)
        encodings[pairs] = codes
    for pairs in origin_sets:
        histories.update(encodings[pairs])
    assert distinct == {code: data['distinct'] for code, data in expected.items()}
    assert histories == {code: data['histories'] for code, data in expected.items()}
    return {'trees': n ** (n - 2), 'absent_pairs_per_tree': comb(n, 2) - (n - 1),
            'labelled_tree_pair_origins': len(origin_sets), 'distinct_labelled_holdings': len(encodings),
            'raw_all_decorated_origins': sum(histories.values()), 'raw_all_decorated_holdings': sum(distinct.values()),
            'every_distinct_class_and_every_origin_mass_matched': True}


def cycle_label_count(n, length):
    root_forests = length * n ** (n - length - 1) if length < n else 1
    return comb(n, length) * factorial(length - 1) // 2 * root_forests


def classes(n):
    data = {}
    for code in decorated_codes(n):
        size = automorphisms(code)
        labelled, remainder = divmod(factorial(n), size)
        assert remainder == 0
        k = sum(rooted_extras(c) for c in code)
        data[code] = {'aut': size, 'distinct': labelled, 'histories': len(code) * labelled, 'extras': k}
    return data


def run():
    output = {}
    for n in (6, 7, 8):
        catalog = classes(n)
        by = defaultdict(Counter)
        for c, row in catalog.items():
            k = row['extras']
            cell = by[(len(c), k)]
            cell['classes'] += 1
            for field in ('histories', 'distinct'):
                cell[field] += row[field]
                cell[field + '_mass'] += 3 ** (n - k) * row[field]
        for (length, k), cell in by.items():
            assert cell['distinct'] == cycle_label_count(n, length) * comb(n, k)
            assert cell['histories'] == length * cell['distinct']
        assert sum(c['histories_mass'] for c in by.values()) == n ** (n - 2) * (comb(n, 2) - n + 1) * 4 ** n
        assert sum(c['distinct_mass'] for c in by.values()) == 4 ** n * sum(cycle_label_count(n, i) for i in range(3, n + 1))
        output[n] = {'classes': len(catalog), 'uncoloured': len(set(map(undecorated, catalog))),
                     'cycle_length_and_flags': [{'length': l, 'extras': k, **z} for (l, k), z in sorted(by.items())]}
        if n == 6:
            output[n]['labelled_literal'] = six_literal(catalog)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'cycle_multiplicities.json').write_text(json.dumps(output, indent=2) + '\n')
    print({n: (r['uncoloured'], r['classes']) for n, r in output.items()})


if __name__ == '__main__':
    run()
