"""RING-READ-20261118-001A: scores the frozen predictions of research/RING-READ-20261118-001/preregistration.md.

Run with the workspace .venv (networkx):
  .venv/bin/python -B check.py gate          -> gate.json
  .venv/bin/python -B check.py T [T ...]      -> round_<T>.json for each T
  .venv/bin/python -B check.py merge          -> results.json (gate + rounds)
beside the artifacts in artifacts/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables/.
"""
import json
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ringread as R  # noqa: E402

OUT = HERE.parents[2] / 'artifacts/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables'
ROUNDS = [10, 12, 14, 15, 16, 18, 20]
MAIN_M = 6


def brute_table(stars, K):
    """Every side J (o excluded) with J and its complement (with o) connected, by bitmask enumeration."""
    n = len(stars)
    adj = R.junction_graph(stars)
    nb = [0] * (n + 1)
    for u in range(n + 1):
        for v in adj[u]:
            nb[u] |= 1 << v
    full = (1 << (n + 1)) - 1
    mask = [sum(1 << b for b in s) for s in stars]

    def connected(side):
        low = side & -side
        seen = frontier = low
        while frontier:
            nxt = 0
            f = frontier
            while f:
                b = f & -f
                nxt |= nb[b.bit_length() - 1]
                f ^= b
            nxt &= side & ~seen
            seen |= nxt
            frontier = nxt
        return seen == side
    span = [0] * (1 << n)
    best = {}
    for side in range(1, 1 << n):
        low = side & -side
        span[side] = span[side ^ low] ^ mask[low.bit_length() - 1]
        if connected(side) and connected(full ^ side):
            w = span[side]
            size = w.bit_count()
            bits = [i for i in range(w.bit_length()) if w >> i & 1]
            for p in combinations(bits, 2):
                if best.get(p, K + 1) > size - 1:
                    best[p] = size - 1
    labels = sorted(R.owners(stars))
    return {p: min(best.get(p, K + 1), K + 1) for p in combinations(labels, 2)}


def gate():
    out = {}
    for T in (1, 2):
        P = R.grow(T)
        st = R.stars_of(P)
        K = max(map(len, st))
        a, _ = R.bond_table(st, MAIN_M, K)
        b = brute_table(st, K)
        out[f'round_{T}_enumeration_equals_brute_force'] = a == b
        out[f'round_{T}_junctions'] = len(st)
    P = R.grow(9)
    st = R.stars_of(P)
    tab, _ = R.bond_table(st, MAIN_M, max(map(len, st)))
    out['r0_exact_at_round_9'] = R.r0(tab) == set(st)
    # mutant: the round-10 table with one entry inside a seven-distinction junction pooled
    P = R.grow(10)
    st = R.stars_of(P)
    K = max(map(len, st))
    tab, _ = R.bond_table(st, MAIN_M, K)
    big = next(s for s in st if len(s) == K)
    pair = tuple(sorted(sorted(big)[:2]))
    mut = dict(tab)
    out['mutant_pair'] = [list(pair), tab[pair]]
    mut[pair] = K + 1
    surv, rep = R.r2(mut, K, MAIN_M, K)
    out['mutant_r2_report'] = rep
    out['mutant_r2_returns_true_junctions'] = any(s == frozenset(st) for s in surv)
    out['gate_passes'] = (out['round_1_enumeration_equals_brute_force'] and out['round_2_enumeration_equals_brute_force']
                          and out['r0_exact_at_round_9'] and not out['mutant_r2_returns_true_junctions'])
    return out


def facts(P, st):
    n = len(st)
    rnd = P.round_of
    f1 = [j for j in range(n) if P.parents[j] == 1 and rnd[j] > 1]
    G = nx.Graph()
    adj = R.junction_graph(st)
    for u in range(n + 1):
        for v in adj[u]:
            G.add_edge(u, v)
    tri_all = sum(nx.triangles(G).values()) // 3
    H = G.copy()
    H.remove_node(n)
    tri_inner = sum(nx.triangles(H).values()) // 3
    shared = Counter(tuple(sorted(js)) for js in R.owners(st).values() if len(js) == 2)
    double = sum(1 for c in shared.values() if c > 1)
    cuts = []
    own = R.owners(st)
    for s in range(P.rounds):
        c = 0
        for b, js in own.items():
            ins = [rnd[j] <= s for j in js]
            if len(js) == 2 and ins[0] != ins[1]:
                c += 1
            elif len(js) == 1 and ins[0]:
                c += 1
        cuts.append(c)
    return {'F1_one_parent_after_round_1': len(f1), 'F2_triangles_with_o': tri_all, 'F2_triangles_without_o': tri_inner,
            'F2_pairs_sharing_two': double, 'F3_layer_cuts': cuts, 'F3_min_layer_cut': min(cuts),
            'P5_vertex_connectivity': nx.node_connectivity(G)}


def one_round(T):
    t0 = time.time()
    P = R.grow(T)
    st = R.stars_of(P)
    truth = frozenset(st)
    K = max(map(len, st))
    res = {'T': T, 'junctions': len(st), 'distinctions': len(R.owners(st)), 'largest_junction': K,
           'junction_sizes': dict(sorted(Counter(map(len, st)).items()))}
    tables = {}
    for m in (6, 7) + ((8,) if T <= 14 else ()):
        t = time.time()
        tables[m], stats = R.bond_table(st, m, K)
        res[f'table_m{m}_seconds'] = round(time.time() - t, 1)
        res[f'table_m{m}_stats'] = stats
    tab = tables[MAIN_M]
    res['P1_tables_agree'] = all(tables[m] == tab for m in tables)
    res['P1_entries_differing'] = {m: sum(1 for p in tab if tables[m][p] != tab[p]) for m in tables if m != MAIN_M}
    res['distance_histogram'] = dict(sorted(Counter(tab.values()).items()))
    res.update(facts(P, st))
    r1 = R.r1(tab, K)
    res['P2_r1'] = {'exact': r1 == set(truth), 'missed': len(truth - r1), 'spurious': len(r1 - truth),
                    'spurious_sizes': dict(Counter(map(len, r1 - truth)))}
    r1l = R.r1_linear(tab, K)
    res['P3prime_r1_linear'] = {'exact': r1l == set(truth), 'missed': len(truth - r1l), 'spurious': len(r1l - truth)}
    surv, rep = R.r2(tab, K, MAIN_M, K)
    res['P3_r2_report'] = rep
    res['P3_r2_survivors'] = len(surv)
    res['P3_r2_works'] = len(surv) == 1 and surv[0] == truth
    if len(surv) > 1:
        res['P3_survivor_differences'] = [sorted(map(sorted, s ^ truth)) for s in surv if s != truth][:5]
    true_next = R.true_next_round(T)
    res['P4_history_free_step_on_true_junctions'] = R.next_round(st) == true_next
    res['P4_regrown_round_equals_true'] = bool(res['P3_r2_works']) and R.next_round(surv[0]) == true_next
    res['P4_true_next_round_junctions'] = sum(true_next.values())
    # P6: the least horizon at which R2 still works
    works = {}
    for H in range(K - 1, 2, -1):
        pt = R.pooled(tab, H)
        s2, rep2 = R.r2(pt, H + 1, MAIN_M, H)
        works[H] = len(s2) == 1 and s2[0] == truth
        if not works[H]:
            break
    res['P6_r2_works_by_horizon'] = works
    good = [H for H, w in works.items() if w]
    res['P6_least_working_horizon'] = min(good) if good and all(works[h] for h in range(min(good), K)) else None
    res['P6_predicted'] = K - 1
    res['seconds'] = round(time.time() - t0, 1)
    return res


def default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    raise TypeError(type(o))


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == 'gate':
        g = gate()
        (OUT / 'gate.json').write_text(json.dumps(g, indent=1, default=default))
        print(json.dumps(g, indent=1, default=default))
    elif sys.argv[1] == 'merge':
        merged = {'gate': json.loads((OUT / 'gate.json').read_text()),
                  'rounds': [json.loads((OUT / f'round_{T}.json').read_text()) for T in ROUNDS]}
        (OUT / 'results.json').write_text(json.dumps(merged, indent=1))
        print('merged', len(merged['rounds']), 'rounds')
    else:
        for T in map(int, sys.argv[1:]):
            r = one_round(T)
            (OUT / f'round_{T}.json').write_text(json.dumps(r, indent=1, default=default))
            print(json.dumps({k: v for k, v in r.items() if k not in ('F3_layer_cuts',)}, default=default), flush=True)
