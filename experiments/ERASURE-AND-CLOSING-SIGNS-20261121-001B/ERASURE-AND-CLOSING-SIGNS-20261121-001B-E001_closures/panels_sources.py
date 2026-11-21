"""Generate and check the four frozen named founder panels."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
from random import Random
import sys

import networkx as nx
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAF = HERE.parent.name
OUT = ROOT / 'artifacts' / LEAF / HERE.name
PRIOR = 'STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B'
sys.path.insert(0, str(ROOT / 'experiments' / PRIOR / f'{PRIOR}-E001_pair_growth'))
from explosive_stages import indexed_rings, ring_source, width
from explosive_verify import BinaryReduction, independent_parity


COUNTS = {'T': 256, 'E': 128, 'M': 128, 'S': 32}
LAWS = ('parity', 'nae')
RINGS = tuple(indexed_rings())


def seed_for(panel):
    return sha256(f'{LEAF}|{panel}|physical-draws|20261121'.encode()).hexdigest()


def from_meetings(holders, meetings, private):
    rows = [[] for _ in range(holders)]
    at = 0
    for a, b, amount in meetings:
        names = range(at, at + amount)
        rows[a].extend(names)
        rows[b].extend(names)
        at += amount
    for h, count in enumerate(private):
        rows[h].extend(range(at, at + count))
        at += count
    return tuple(map(tuple, rows))


def tree(rng):
    k = rng.randrange(4, 9)
    prufer = tuple(rng.randrange(k) for _ in range(k - 2))
    tree = nx.from_prufer_sequence(prufer)
    extras = tuple(int(rng.random() < 0.25) for _ in range(k))
    joins = tuple((a, b, 1) for a, b in sorted(tuple(sorted(e)) for e in tree.edges()))
    private = tuple(max(0, 3 - tree.degree(h)) + extras[h] for h in range(k))
    return from_meetings(k, joins, private), {'prufer': prufer, 'extra_private': extras,
                                            'private_counts': private, 'original_meetings': joins}


def simple_positive_family(rng):
    joins = tuple((a, b, 1 + (rng.random() < 0.125)) for a, b in combinations(range(4), 2))
    return from_meetings(4, joins, (1,) * 4), {'original_meetings': joins}


def ring(rng):
    assert len(RINGS) == 40
    index = rng.randrange(len(RINGS))
    specs = RINGS[index]
    return ring_source(specs).rows, {'ring_index_zero_based': index, 'indexed_ring': specs}


def sources(panel):
    rng = Random(int(seed_for(panel), 16))
    for draw in range(1, COUNTS[panel] + 1):
        if panel == 'T':
            original, attributes = tree(rng)
        elif panel in ('E', 'M'):
            original, attributes = ring(rng)
        else:
            original, attributes = simple_positive_family(rng)
        holder_order = list(range(len(original)))
        if panel == 'S':
            rng.shuffle(holder_order)
        if panel == 'M':
            companion_arities = tuple(rng.randrange(3, 5) for _ in range(2))
            at = width(original)
            companions = []
            for count in companion_arities:
                companions.append(tuple(range(at, at + count)))
                at += count
            original = (*original, *companions)
            attributes['companion_arities'] = companion_arities
        perm = list(range(width(original)))
        rng.shuffle(perm)
        if panel == 'M':
            component_order = [0, 1, 2]
            rng.shuffle(component_order)
            groups = (tuple(range(5)), (5,), (6,))
            holder_order = [h for i in component_order for h in groups[i]]
            attributes['component_order_to_original'] = component_order
        named = tuple(tuple(sorted(perm[x] for x in original[h])) for h in holder_order)
        yield {'panel': panel, 'draw': draw, 'source_rows': named, 'before_permutation': original,
               'source_name_permutation': perm, 'source_holder_order_to_original': holder_order,
               'seed_sha256': seed_for(panel), **attributes}


def rank(vectors):
    basis = {}
    for v in vectors:
        while v:
            pivot = v.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = v
                break
            v ^= basis[pivot]
    return len(basis)


def founder_check(draw, law):
    rows = tuple(map(tuple, draw['source_rows']))
    using = Counter(x for row in rows for x in row)
    width_n = width(rows)
    assert set(using) == set(range(width_n))
    assert all(c in (1, 2) for c in using.values())
    assert all(len(row) >= 3 and len(set(row)) == len(row) for row in rows)
    mapping = draw['source_name_permutation']
    holder_order = draw['source_holder_order_to_original']
    assert sorted(mapping) == list(range(width_n)) and sorted(holder_order) == list(range(len(rows)))
    assert rows == tuple(tuple(sorted(mapping[x] for x in draw['before_permutation'][h])) for h in holder_order)
    if law == 'parity':
        kernel, total = independent_parity(rows)
        sizes = tuple(1 << rank(kernel[x] for x in row) for row in rows)
        essential = all(rank(sum(1 << x for x in row) for i, row in enumerate(rows) if i != j) <
                        width_n - (total.bit_length() - 1) for j in range(len(rows)))
        full = sizes == tuple(1 << (len(row) - 1) for row in rows)
        return {'lawful': full and total > 0, 'founder_words': total, 'projection_sizes': sizes, 'essential': essential}
    factors = BinaryReduction(rows, (len(rows),), 'uniform')
    total = factors.contract()
    sizes = []
    essential = []
    for h, row in enumerate(rows):
        tested = (tuple(zip(row, bits, strict=True)) for bits in product((0, 1), repeat=len(row)) if min(bits) != max(bits))
        sizes.append(sum(factors.contract(pinned=pinned) > 0 for pinned in tested))
        original = factors.data[width_n + h]
        factors.data[width_n + h] = np.ones_like(original)
        essential.append(factors.contract(pinned=tuple((x, 0) for x in row)) > 0)
        factors.data[width_n + h] = original
    full = sizes == [(1 << len(row)) - 2 for row in rows]
    return {'lawful': full and total > 0, 'founder_words': total, 'projection_sizes': sizes, 'essential': all(essential)}
