"""Part 6: two rings with descent (DH 6.4; P9).  Ring(5,3) and Ring(7,3) under the two and the three added rules (C3W,
C3WF), base and both barred forms, parity, 14 rounds.  Returns searched as SD lines 85-88 with barred marks; the period
formula's hypotheses checked.  Writes part6.json.  Readings: deviations 27.

python -B part6.py
"""
from __future__ import annotations

import math
import time
from collections import defaultdict

import networkx as nx

from dh_common import STARTS_JSON, lr_core, write, log
import dh_engine as E

STARS = {k: v['stars'] for k, v in STARTS_JSON['starts'].items()}
RINGS = ['Ring(5,3)', 'Ring(7,3)']
RLAWS = ['C3W', 'C3WF']
R6 = 14


def roster_at(S, t):
    K = S.k_at[t]
    H = S.holders

    def ht(d):
        return [h for h in H[d] if h < K]
    members = {}
    for u in range(K):
        h = k = 0
        for d in S.places[u]:
            if len(ht(d)) == 1:
                if S.bround[d] is not None and S.bround[d] <= t:
                    k += 1
                else:
                    h += 1
        if h:
            members[u] = (h, k)
    acc = defaultdict(set)
    meets_member = False
    for u in members:
        for d in S.places[u]:
            for w in ht(d):
                if w != u:
                    acc[w].add(u)
                    if w in members:
                        meets_member = True
    fam = {frozenset(s) for s in acc.values() if len(s) >= 2}
    parts = lr_core.components(list(members), fam) if members else []
    return members, fam, parts, not meets_member


def part_graph(members, fam, part):
    sets = [M for M in fam if M <= part]
    maxi = [M for M in sets if not any(M < M2 for M2 in sets)]
    maxi = sorted(set(maxi), key=lambda M: sorted(M))
    G = nx.Graph()
    for u in part:
        G.add_node(('m', u), lab=('m',) + members[u])
    for i, M in enumerate(maxi):
        G.add_node(('s', i), lab=('s', len(M)))
        for u in M:
            G.add_edge(('m', u), ('s', i))
    return G


def same_parts(G1, G2):
    if G1.number_of_nodes() != G2.number_of_nodes() or G1.number_of_edges() != G2.number_of_edges():
        return None
    gm = nx.algorithms.isomorphism.GraphMatcher(G1, G2, node_match=lambda a, b: a['lab'] == b['lab'])
    if not gm.is_isomorphic():
        return None
    return gm


def descendants(S, Y, K):
    seen = set(Y)
    st = list(Y)
    while st:
        u = st.pop()
        for c in S.kids[u]:
            if c < K and c not in seen:
                seen.add(c)
                st.append(c)
    return seen


def find_return(S):
    R = S.round
    rosters = {t: roster_at(S, t) for t in range(0, R + 1)}
    for s in range(1, R):
        mem_s, fam_s, parts_s, past = rosters[s]
        if not past or not parts_s:
            continue
        graphs_s = [(Y, part_graph(mem_s, fam_s, Y)) for Y in parts_s]
        for t in range(s + 1, R + 1):
            mem_t, fam_t, parts_t, _ = rosters[t]
            for Y, GY in graphs_s:
                desc = descendants(S, Y, S.k_at[t])
                for Z in parts_t:
                    if not Z <= desc:
                        continue
                    gm = same_parts(GY, part_graph(mem_t, fam_t, Z))
                    if gm is None:
                        continue
                    first = None
                    any_common = None
                    for i, mp in enumerate(gm.isomorphisms_iter()):
                        qs = {S.ps[v[1]] - S.ps[u[1]] for u, v in mp.items() if u[0] == 'm'}
                        if first is None:
                            first = (mp, qs)
                        if len(qs) == 1 and any_common is None:
                            any_common = next(iter(qs))
                        if i >= 500:
                            break
                    mp, qs = first
                    q = next(iter(qs)) if len(qs) == 1 else 'not common'
                    agree3 = len({S.ps[u] % 3 for u in Y}) == 1
                    return {'s': s, 't': t, 'period': t - s, 'part_members': len(Y),
                            'renaming_found': sorted([u[1], v[1]] for u, v in mp.items() if u[0] == 'm'),
                            'q': q, 'some_renaming_with_common_q': any_common,
                            'members_agree_in_parent_steps_counted_in_threes': agree3,
                            'h_k_of_members': sorted(mem_s[u] for u in Y)}
    return None


def job(args):
    start, ln, form = args
    L = E.LAW[ln]
    S, recs, end = E.grow(STARS[start], L, form, 'parity', R=R6, N=10 ** 9)
    ret = find_return(S)
    return {'start': start, 'law': ln, 'form': E.FORM_NAMES[form], 'rounds': S.round, 'knots': len(S.places),
            'end': end, 'births': [r['births'] for r in recs], 'first_return': ret}


def main():
    t0 = time.time()
    rows = [job((s, ln, f)) for s in RINGS for ln in RLAWS for f in (None, 'PB', 'BB')]
    verdicts = []
    for s in RINGS:
        for ln in RLAWS:
            b = next(r for r in rows if r['start'] == s and r['law'] == ln and r['form'] == 'base')
            br = b['first_return']
            T = br['period'] if br else None
            q = br['q'] if br else None
            hyp = bool(br) and isinstance(q, int) and br['members_agree_in_parent_steps_counted_in_threes']
            pred = T * 3 // math.gcd(3, q) if hyp else None
            for f in ('NEXT3-PLACES (barred)', 'NEXT3-BARRED'):
                r = next(x for x in rows if x['start'] == s and x['law'] == ln and x['form'] == f)
                obs = r['first_return']['period'] if r['first_return'] else None
                verdicts.append({'start': s, 'law': ln, 'form': f, 'T_base': T, 'q': q, 'hypotheses_hold': hyp,
                                 'predicted_period': pred, 'observed_period': obs,
                                 'P9': T == 2 and q == 1 and hyp and obs == 6})
    out = {'part': 6, 'rows': rows, 'formula': verdicts, 'P9': all(v['P9'] for v in verdicts),
           'seconds': round(time.time() - t0, 1)}
    write('part6.json', out)
    log('part 6', out['P9'], [(v['start'], v['law'], v['form'][:12], v['T_base'], v['q'], v['observed_period'])
                               for v in verdicts], out['seconds'])


if __name__ == '__main__':
    main()
