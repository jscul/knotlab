"""Find and physically replay the first single-spoke loss in the published 104-site host."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = 'LATER-BOND-READING-20261119-001'
sys.path.insert(0, str(ROOT / 'experiments' / OLD / (OLD + '-E001_future')))
sys.path.insert(0, str(ROOT / 'research' / OLD))
from weighted_shield_grouped import layout
from boundary_checks import extend, verify


def widths(deck, drops):
    values = []
    for name, _, middle in deck.edges:
        if name[0] == 'o':
            val = 1 if middle in drops else 4
        elif name[0] == 'h':
            val = 2 if middle in 'abcd' else 6
        elif name[0] == 'v' and middle in 'abcd':
            val = 3
        else:
            val = 1
        values.append(val)
    return np.asarray(values, dtype=np.int16)


def compare(deck, weights):
    prices = deck.cut_matrix @ weights
    order = np.argsort(prices, kind='stable')
    ordered = deck.supports[order]
    sorted_prices = prices[order]
    bitsets = {name: int.from_bytes(np.packbits((ordered >> i) & 1, bitorder='little').tobytes(),
                                    'little') for i, name in enumerate(deck.names)}
    def minimum(query):
        record = bitsets[query[0]]
        for name in query[1:]:
            record &= bitsets[name]
        return int(sorted_prices[(record & -record).bit_length() - 1]) if record else None
    counts = {}
    first = {}
    for k in range(1, 4):
        number = mismatch = 0
        for query in combinations(deck.names, k):
            number += 1
            image = tuple(sorted(deck.swapped.get(x, x) for x in query))
            if tuple(sorted(query)) == image:
                continue
            old, other = minimum(query), minimum(image)
            if old != other:
                mismatch += 1
                if k not in first:
                    first[k] = [query, image, old, other]
        counts[k] = (number, mismatch)
    return counts, first, minimum


def physical(deck, weights, selected):
    index = {u: i for i, u in enumerate(deck.sites)}
    poles = [index[selected], index['o']]
    rows = [set() for _ in index]
    names = {}
    last = 0
    def site():
        rows.append(set())
        return len(rows) - 1
    def add(*ends):
        nonlocal last
        for u in ends:
            rows[u].add(last)
        last += 1
        return last - 1
    for (tag, a, b), count in zip(deck.edges, weights):
        if tag != 'o' + selected:
            names[tag] = [add(index[a], index[b]) for _ in range(count)]
    fixed = last
    r = [site() for _ in range(4)]
    z = site()
    for j in r:
        add(poles[0], j)
    add(r[1], r[2])
    add(r[1], r[3])
    add(r[1], z)
    add(r[2], z)
    for j, width in zip([*r, z], (3, 2, 2, 2, 1)):
        for _ in range(width):
            add(j)
    for _ in range(4):
        u, v, w = site(), site(), site()
        for a, b in ((poles[1], u), (u, v), (u, w), (v, w)):
            add(a, b)
        add(v)
        add(w)
    start = list(map(frozenset, rows))
    here = extend.grow1(start)
    after = extend.grow1(here)
    stages = [verify.Arrangement.parse([sorted(r) for r in phase]) for phase in (start, here, after)]
    replay = [verify.round_replay(a, b) for a, b in zip(stages, stages[1:])]
    assert all(verify.start_audit(a)['census_open_legal'] for a in stages)
    assert all(not record['implied'] for step in replay for record in step)
    change = [(x,y) for a,b in deck.swapped.items() for x,y in zip(names[a],names[b])]
    phi = {x:y for x,y in change}
    for phase in stages:
        assert all(phi.get(x,x)==x for j in phase.live for x in phase.stars[j])
        multiplicities = {frozenset(classes) for classes in by_owners(phase).values()}
        assert {frozenset(phi.get(x,x) for x in cl) for cl in multiplicities} == multiplicities
    cuts = []
    for phase in stages[1:]:
        ends, _, _ = phase.holder_graph()
        g = nx.Graph()
        for x,(a,b) in ends.items():
            if x >= fixed:
                if g.has_edge(a,b): g[a][b]['capacity'] += 1
                else: g.add_edge(a,b,capacity=1)
        cuts.append(int(nx.minimum_cut_value(g,*poles)))
    assert cuts == [4,1]
    return (dict(sizes=[[len(a.stars),len(a.labels)] for a in stages],
                 both_terminal_costs=cuts,projection_all_ages=True,
                 current_live_and_pair_flip_preserved=True), names)


def by_owners(stage):
    groups = {}
    for x, owners in stage.owners.items():
        groups.setdefault(tuple(owners), []).append(x)
    return groups


def run():
    deck = layout((6,6),True,True)
    history = []
    last_reader = None
    for i in range(7):
        weights = widths(deck, {'u'+str(j) for j in range(i)})
        counts, first, reader = compare(deck, weights)
        history.append(dict(repriced=i, tested_and_failed=counts))
        if first:
            assert i and min(first)==3
            q, q2, a, b = first[3]
            selected = 'u'+str(i-1)
            assert 'o'+selected not in q and 'o'+selected not in q2
            old, other = last_reader(q),last_reader(q2)
            assert old == other and a != b
            oldw = widths(deck, {'u'+str(j) for j in range(i-1)})
            replay, names = physical(deck, oldw, selected)
            return dict(host_sites=len(deck.sites),named_classes=len(deck.names),
                        bonds=len(deck.supports), vectors_examined=history,
                        changed_spoke='o'+selected, marks=q,image=q2,
                        literal_marks=[names[n][0] for n in q],
                        literal_image=[names[n][0] for n in q2],
                        current_K=[old,other],next_K=[a,b],physical=replay)
        last_reader = reader
    raise AssertionError('Expected a first loss by the sixth red spoke')


if __name__ == '__main__':
    report = json.dumps(run(), indent=2) + '\n'
    destination = Path(__file__).with_suffix('.json')
    if sys.argv[1:] == ['--check']:
        assert destination.read_text() == report
    else:
        destination.write_text(report)
