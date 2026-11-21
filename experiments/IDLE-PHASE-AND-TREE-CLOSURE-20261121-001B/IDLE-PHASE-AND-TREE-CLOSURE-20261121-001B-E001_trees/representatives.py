"""Enumerate decorated tree representatives and exact labelled weights."""

from collections import Counter
from math import comb, factorial
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAF = HERE.parent.name
OUT = ROOT / 'artifacts' / LEAF / HERE.name
B251 = 'ERASURE-AND-CLOSING-SIGNS-20261121-001B'
B251_CODE = ROOT / 'experiments' / B251 / f'{B251}-E001_closures'
sys.path.insert(0, str(B251_CODE))
from panels_sources import from_meetings


SIZES = range(4, 9)


def transformed(bits, permutation):
    image = 0
    while bits:
        low = bits & -bits
        image |= 1 << permutation[low.bit_length() - 1]
        bits ^= low
    return image


def source_rows(n, edges, extra):
    degree = Counter(x for pair in edges for x in pair)
    private = tuple(max(0, 3 - degree[h]) + b for h, b in enumerate(extra))
    meetings = tuple((*e, 1) for e in edges)
    return from_meetings(n, meetings, private)


def shape_representatives(n, tree):
    edges = tuple(sorted(tuple(sorted(e)) for e in tree.edges()))
    raw = nx.algorithms.isomorphism.GraphMatcher(tree, tree).isomorphisms_iter()
    automorphisms = tuple(tuple(g[i] for i in range(n)) for g in raw)
    original_labelled, r = divmod(factorial(n), len(automorphisms))
    assert r == 0
    found = Counter()
    available = set(range(1 << n))
    while available:
        choice = min(available)
        pictures = Counter(transformed(choice, g) for g in automorphisms)
        assert set(pictures) <= available
        available -= set(pictures)
        stabilizer = pictures[choice]
        assert all(k == stabilizer for k in pictures.values())
        assert stabilizer * len(pictures) == len(automorphisms)
        labelled, remainder = divmod(factorial(n), stabilizer)
        assert remainder == 0 and labelled == original_labelled * len(pictures)
        k = choice.bit_count()
        extra = tuple(choice >> i & 1 for i in range(n))
        found[k] += labelled
        yield {'n': n, 'edges': edges, 'extra': extra, 'aut': stabilizer, 'labelled': labelled,
               'mass': labelled * 3 ** (n - k), 'uncoloured_aut': len(automorphisms),
               'decoration_orbit_size': len(pictures), 'id': f'{n}:{edges}:{choice}',
               'founder_rows': source_rows(n, edges, extra)}
    assert found == {k: comb(n, k) * original_labelled for k in range(n + 1)}


def representatives(n):
    results = Counter()
    mass = 0
    for preliminary in nx.nonisomorphic_trees(n):
        tree = nx.convert_node_labels_to_integers(preliminary, ordering='sorted')
        for item in shape_representatives(n, tree):
            results[sum(item['extra'])] += item['labelled']
            mass += item['mass']
            yield item
    assert results == {k: comb(n, k) * n ** (n - 2) for k in range(n + 1)}
    assert mass == n ** (n - 2) * 4 ** n
