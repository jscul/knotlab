"""TRIPLE-GROWN-20261119-001A: do three-way readings separate the meet-once collisions with other states?

The three-way reading of three distinctions is the smallest bond containing all three, less one, or none (THREE-WAY's reading,
in its referee's wording).  Pairs:
- static: every two members in different state groups of PARENT-RULE part S's 472 groups (1,034 pairs);
- reached: every two members in different state groups of GROW-SMALL's 67 groups (87 pairs; state groups rebuilt from the tests).
Readings: from every bond (PARENT-RULE's plib) when both members have at most 15 vertices (exact); otherwise, for both members,
from every bond of at most 9 distinctions (the exact_table_v2 enumeration, returning the bonds), readings above 8 and none pooled
together.  Also reported: the rank of the three-distinction bonds against the rank of the equation space (the advisor's check).  A pooled reading
is a function of the exact one, so a pair that no renaming keeps under pooled readings is separated exactly; one that pooled
readings do not separate is 'undecided'.
Test (THREE-WAY's): the pair table as a complete graph with Weisfeiler-Leman colours, every triple with a reading (not none, not
pooled) attached as a vertex labelled by it; some isomorphism between the two such graphs = a renaming keeping both readings.
Run: .venv/bin/python -B triples.py -> triples.json beside the artifacts."""
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PR = ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'
sys.path.insert(0, str(PR))
import plib as L  # noqa: E402
SRC_STATIC = ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/static_pairs.json'
SRC_GROWN = ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/grow_pairs.json'
LMAX = 9


def small_bonds(stars, L_):
    """Every bond of at most L_ distinctions: exact_table_v2's enumeration (connected inner side grown by include/exclude with
    max-flow pruning), returning the bonds."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('xt2', ROOT / 'experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/exact_table_v2.py')
    X = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(X)
    n, cap, own = X.capacities(stars)
    o = n
    masks = [sum(1 << b for b in s) for s in stars]
    o_isolated = not cap.get(o)
    out = []

    def complement_connected(J):
        if o_isolated:
            rest = [v for v in range(n) if v not in J]
            if not rest:
                return False
            seen, stack, target = {rest[0]}, [rest[0]], len(rest)
        else:
            seen, stack, target = {o}, [o], n + 1 - len(J)
        while stack:
            x = stack.pop()
            for y in cap.get(x, {}):
                if y not in J and y not in seen:
                    seen.add(y)
                    stack.append(y)
        return len(seen) == target

    def go(J, Xs):
        if X.flow_exceeds(cap, J, Xs | {o}, L_):
            return
        front = {v for u in J for v in cap.get(u, {}) if v != o and v not in J and v not in Xs}
        if not front:
            c = sum(c for u in J for v, c in cap.get(u, {}).items() if v not in J)
            if c <= L_ and complement_connected(J):
                w = 0
                for u in J:
                    w ^= masks[u]
                out.append([i for i in range(w.bit_length()) if w >> i & 1])
            return
        w = max(front, key=lambda v: (sum(cap[v].get(u, 0) for u in J), -v))
        go(J | {w}, Xs)
        go(J, Xs | {w})

    for r in range(n):
        go(frozenset([r]), frozenset(range(r)))
    return out


def rank3(stars, bs):
    """Rank of the span of the three-distinction bonds (the triples read 2) against the rank of the equation space."""
    labels = sorted(L.owners(stars))
    idx = {x: i for i, x in enumerate(labels)}
    r3 = L.rank([sum(1 << idx[x] for x in b) for b in bs if len(b) == 3])
    rc = L.rank([sum(1 << idx[x] for x in s) for s in stars])
    return r3, rc


def readings(stars, exact):
    """exact: every bond (at most 15 vertices); otherwise every bond of at most 9 distinctions, readings above 8 pooled.  The
    regime is chosen per pair, so both members are read the same way."""
    labels = sorted(L.owners(stars))
    bs = L.bonds(stars) if exact else small_bonds(stars, LMAX)
    p2, p3 = {}, {}
    for b in bs:
        k = len(b) - 1
        sb = sorted(b)
        for p in combinations(sb, 2):
            if p2.get(p, 10 ** 9) > k:
                p2[p] = k
        for t in combinations(sb, 3):
            if p3.get(t, 10 ** 9) > k:
                p3[t] = k
    pool = 'none' if exact else 'none or beyond 8'
    pairs = {p: p2.get(p, pool) for p in combinations(labels, 2)}
    return labels, pairs, p3, rank3(stars, bs)


def graph(labels, pairs, triples):
    g = nx.Graph()
    g.add_nodes_from(labels, k='d')
    for (a, b), d in pairs.items():
        g.add_edge(a, b, d=str(d))
    hs = nx.weisfeiler_lehman_subgraph_hashes(g, edge_attr='d', iterations=3)
    for v in labels:
        g.nodes[v]['k'] = ('d', tuple(hs[v]))
    for i, (t, d) in enumerate(sorted(triples.items())):
        g.add_node(('t', i), k=('t', str(d)))
        for x in t:
            g.add_edge(('t', i), x, d='in')
    return g


def iso(g1, g2):
    if g1.number_of_nodes() != g2.number_of_nodes() or g1.number_of_edges() != g2.number_of_edges():
        return False
    if sorted(map(str, (d['k'] for _, d in g1.nodes(data=True)))) != sorted(map(str, (d['k'] for _, d in g2.nodes(data=True)))):
        return False
    return isomorphism.GraphMatcher(g1, g2, node_match=lambda a, b: a['k'] == b['k'],
                                    edge_match=lambda a, b: a.get('d') == b.get('d')).is_isomorphic()


def test_pair(item):
    kind, a, b, meta = item
    a = [frozenset(s) for s in a]
    b = [frozenset(s) for s in b]
    exact = L.graph_of(a)[0] <= 15 and L.graph_of(b)[0] <= 15
    la, pa, ta, ra = readings(a, exact)
    lb, pb, tb, rb = readings(b, exact)
    pair_iso = len(la) == len(lb) and iso(graph(la, pa, {}), graph(lb, pb, {}))
    both_iso = pair_iso and iso(graph(la, pa, ta), graph(lb, pb, tb))
    verdict = 'separated' if pair_iso and not both_iso else ('agree on both' if both_iso else 'pair tables differ')
    if verdict == 'agree on both' and not exact:
        verdict = 'undecided (readings read to 8 agree)'
    return {'kind': kind, 'meta': meta, 'exact': exact, 'distinctions': len(la), 'junctions': [len(a), len(b)],
            'pair_tables_isomorphic': pair_iso, 'verdict': verdict,
            'triples_differing_on_counts': sum((Counter(map(str, ta.values())) - Counter(map(str, tb.values()))).values()),
            'rank_of_three_bonds': [ra[0], rb[0]], 'rank_of_states': [ra[1], rb[1]]}


def static_items():
    out = []
    for gi, g in enumerate(json.loads(SRC_STATIC.read_text())['other_states_groups']):
        ms = g['members']
        for i, j in combinations(range(len(ms)), 2):
            if ms[i]['state_group'] != ms[j]['state_group']:
                out.append(('static', ms[i]['stars'], ms[j]['stars'], {'group': gi}))
    return out


def grown_items():
    out = []
    d = json.loads(SRC_GROWN.read_text())
    for gi, g in enumerate(x for x in d['groups'] if x.get('other_states_collision')):
        sg = {i: i for i in range(g['classes'])}
        for rep, i, v, _ in g['tests']:
            if v == 'same':
                sg[i] = sg[rep]
        ms = g['members']
        for i, j in combinations(range(len(ms)), 2):
            if sg[i] != sg[j]:
                out.append(('reached', ms[i]['stars'], ms[j]['stars'], {'group': gi, 'prov': [ms[i]['prov'][0], ms[j]['prov'][0]]}))
    return out


def main():
    items = static_items() + grown_items()
    with Pool(8) as pool:
        rows = pool.map(test_pair, items, chunksize=2)
    s = defaultdict(Counter)
    for r in rows:
        s[r['kind']]['pairs'] += 1
        s[r['kind']][r['verdict']] += 1
        s[r['kind']]['exact'] += r['exact']
        s[r['kind']]['pair_tables_isomorphic'] += r['pair_tables_isomorphic']
        s[r['kind']]['separated_by_triple_counts_alone'] += r['triples_differing_on_counts'] > 0
        s[r['kind']]['three_bonds_span_both'] += r['rank_of_three_bonds'] == r['rank_of_states']
        if r['kind'] == 'reached' and sorted(x[1] for x in r['meta']['prov']) == [448, 581]:  # GROW-SMALL's created pair
            s['created_pair_candidates'][r['verdict']] += 1
    summary = {k: dict(v) for k, v in s.items()}
    dest = ROOT / 'artifacts/TRIPLE-GROWN-20261119-001A/TRIPLE-GROWN-20261119-001A-E001_triples'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'triples.json').write_text(json.dumps({'summary': summary, 'rows': rows}, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
