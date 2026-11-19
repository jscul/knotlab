"""GROW-SMALL-20261119-001A, check outside the pipeline (the frozen protocol for a failure of G1), on the collisions with other
states that targeted.py found: for each static other-states group, its members grown to rounds 1, 2 and 3; every two grown members
in different state groups whose full tables (by bonds, PARENT-RULE's plib, when at most 15 vertices) are isomorphic:
- the renaming found by VF2 written out and checked entry by entry;
- non-isomorphism of the two arrangements by a second encoding (the junction graph with the outside vertex marked and edge
  multiplicities);
- other states by an invariant: the weight enumerators of the two equation spaces (every word, when the rank is at most 20), and,
  when those agree, every table isomorphism on twin classes by rank (plib.states);
- regrowth from relabelled starts gives isomorphic stages.
Run: .venv/bin/python -B verify_t.py -> verify_t.json."""
import json
import random
import sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pairs_grow as PG  # noqa: E402
GJ, L = PG.GJ, PG.L
SRC = ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/static_pairs.json'


def weights(stars):
    labels = sorted(L.owners(stars))
    idx = {b: i for i, b in enumerate(labels)}
    basis = []
    for s in stars:
        w = sum(1 << idx[b] for b in s)
        for v in basis:
            w = min(w, w ^ v)
        if w:
            basis.append(w)
    if len(basis) > 20:
        return None
    c = Counter()
    for mask in range(1 << len(basis)):
        w = 0
        for i, v in enumerate(basis):
            if mask >> i & 1:
                w ^= v
        c[bin(w).count('1')] += 1
    return tuple(sorted(c.items()))


def marked_graph(stars):
    g = L.junction_graph(stars)
    for v in g.nodes:
        g.nodes[v]['o'] = v == 'o'
    return g


def table_renaming(a, b):
    ta, la = L.table(a)
    tb, lb = L.table(b)
    ga, gb = L.coloured(ta, la), L.coloured(tb, lb)
    m = isomorphism.GraphMatcher(ga, gb, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
    for phi in m.isomorphisms_iter():
        ok = all(ta[(x, y)] == tb[tuple(sorted((phi[x], phi[y])))] for (x, y) in ta)
        return phi, ok, ta, tb
    return None, False, ta, tb


def check_pair(a, b):
    nv = max(L.graph_of(a)[0], L.graph_of(b)[0])
    if nv > 15:
        return {'skipped': 'more than 15 vertices'}
    phi, ok, ta, tb = table_renaming(a, b)
    if phi is None:
        return {'full_tables_isomorphic': False}
    ga, gb = marked_graph(a), marked_graph(b)
    noniso = not isomorphism.GraphMatcher(ga, gb, node_match=lambda x, y: x['o'] == y['o'],
                                          edge_match=lambda x, y: x['m'] == y['m']).is_isomorphic()
    wa, wb = weights(a), weights(b)
    st = 'other (weight enumerators differ)' if (wa is not None and wb is not None and wa != wb) else L.states(a, b, ta, tb)
    return {'full_tables_isomorphic': True, 'renaming_checked_entry_by_entry': ok, 'non_isomorphic_second_encoding': noniso,
            'states': st, 'junctions': [len(a), len(b)], 'distinctions': len(ta) and len(L.owners(a))}


def relabel_control(start, rounds):
    other = GJ.grow(GJ.relabelled(start, 12345), rounds)
    mine = GJ.grow(start, rounds)
    return len(other) == len(mine) and all(GJ.same_arrangement(x, y) for x, y in zip(mine, other))


def one(g):
    ms = g['members']
    starts = [[frozenset(s) for s in m['stars']] for m in ms]
    sgs = [m['state_group'] for m in ms]
    grown = [GJ.grow(s, 3) for s in starts]
    out = []
    for i, j in combinations(range(len(ms)), 2):
        if sgs[i] == sgs[j]:
            continue
        for rnd in (1, 2, 3):
            if len(grown[i]) >= rnd and len(grown[j]) >= rnd:
                a, b = grown[i][rnd - 1], grown[j][rnd - 1]
                if len(L.owners(a)) != len(L.owners(b)):
                    continue
                r = check_pair(a, b)
                if r.get('full_tables_isomorphic'):
                    r.update({'round': rnd, 'starts': [ms[i]['row']['loose'], ms[j]['row']['loose']],
                              'start_atlas': [ms[i]['row']['atlas'], ms[j]['row']['atlas']],
                              'relabel_ok': relabel_control(starts[i], rnd) and relabel_control(starts[j], rnd),
                              'stars': [[sorted(s) for s in a], [sorted(s) for s in b]],
                              'meet_once': L.max_shared(a) < 2 and L.max_shared(b) < 2})
                    out.append(r)
    return out


def main():
    groups = json.loads(SRC.read_text())['other_states_groups']
    with Pool(8) as pool:
        rows = [x for r in pool.map(one, groups, chunksize=4) for x in r]
    s = Counter()
    for r in rows:
        k = f"round_{r['round']}"
        s[k + '_pairs_full_tables_isomorphic'] += 1
        s[k + '_other_states'] += str(r['states']).startswith('other')
        s[k + '_other_by_weights'] += 'weight' in str(r['states'])
        s[k + '_renaming_ok'] += r['renaming_checked_entry_by_entry']
        s[k + '_non_isomorphic'] += r['non_isomorphic_second_encoding']
        s[k + '_relabel_ok'] += r['relabel_ok']
        s[k + '_meet_once'] += r['meet_once']
    dest = ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow'
    (dest / 'verify_t.json').write_text(json.dumps({'summary': dict(sorted(s.items())), 'pairs': rows}, indent=1))
    print(json.dumps(dict(sorted(s.items())), indent=1))


if __name__ == '__main__':
    main()
