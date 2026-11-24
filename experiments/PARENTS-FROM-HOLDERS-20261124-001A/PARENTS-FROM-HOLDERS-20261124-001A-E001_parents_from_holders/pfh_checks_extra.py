"""An extra check, beyond the three registered checks of run 1: on looks too large to try every renaming (from P2 rounds up to 6 and from 150 states of each serial run), the code's
verdict against networkx's VF2 isomorphism test (an independent exact matcher) on the compressed forms, with the same
colours (without the unfoldings) and edge labels.  Pairs are drawn to be hard: two places of the same structure-free
kind of look whose compressed colour multisets (without unfoldings) and unfoldings are equal; pairs are drawn until 150
of them are told apart by the code (by the colours of item 35, the refinement or the search) or 4,000 pairs are compared.

    python -B pfh_checks_extra.py       # writes artifacts/.../checks_extra.json
"""
from __future__ import annotations

import json
import random
import time
from collections import defaultdict

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

import pfh_common as PC
import pfh_iso as ISO
import pfh_look as LK
import pfh_views as VW
from pfh_classes import greedy_renaming
from pfh_struct import Struct

E = PC.E


def nxg(G):
    H = nx.Graph()
    for v in range(G.n):
        H.add_node(v, c=G.colour[v])
    for v in range(G.n):
        for w, lab in G.adj[v]:
            if v < w:
                H.add_edge(v, w, l=lab)
    return H


def code_verdict(LA, LB, intern):
    ra, ua = VW.in_look(LA, intern)
    rb, ub = VW.in_look(LB, intern)
    GA, IA = LK.compress(LA, extra=ua)
    GB, IB = LK.compress(LB, extra=ub)
    if GA.n != GB.n or sorted(GA.colour) != sorted(GB.colour):
        return False, 'colours'
    m = greedy_renaming(GA, GB)
    how = 'matching'
    if m is None:
        m = ISO.find_renaming(GA, GB)
        how = 'search'
    if m is None:
        return False, 'search'
    km, dm = LK.full_renaming(LA, IA, LB, IB, m)
    ok, why = LK.check_renaming(LA, LB, km, dm)
    if not ok:
        raise AssertionError(why)
    return True, how


def main(seed=11, want_neg=150, max_pairs=4000):
    PC.check_frozen()
    rng = random.Random(seed)
    t0 = time.time()
    sources = []
    for start, fam, rc in PC.gate_pairs():
        S = PC.start_struct(start)
        law = PC.ref_law(fam)
        for t in range(1, 7):
            S, rec = E.round_step(S, law)
            if S.n_knots > 700 or rec['stopped']:
                break
            sources.append((start, fam, t, Struct.from_engine(S)))
    import pfh_pop as PP
    for cid, start, fam, r in PP.serial_configs():
        SR = PP.SerialRun(cid, start, fam, r)
        idx = list(range(len(SR.states)))
        rng.shuffle(idx)
        for i in idx[:150]:
            sources.append((cid, fam, 'state %d' % i, SR.struct(i)))
    pairs = []
    rows = []
    agree = 0
    stats = defaultdict(int)
    intern = {v: {} for v in LK.VARIANTS}
    buckets = defaultdict(list)
    tries = 0
    while tries < 400000:
        tries += 1
        start, fam, t, T = sources[rng.randrange(len(sources))]
        if not T.items:
            continue
        x, a = T.items[rng.randrange(len(T.items))]
        d = rng.randint(2, 4)
        v = LK.VARIANTS[rng.randrange(3)]
        L = LK.extract(T, x, a, d, v)
        if not 9 <= len(L.knots) <= 150:
            continue
        root, unr = VW.in_look(L, intern[v])
        G, _ = LK.compress(L)
        key = (v, d, fam, root, tuple(sorted(G.colour)))   # equal unfolding and equal colours without unfoldings
        buckets[key].append((start, t, x, a, T.kinds[T.item_index[(x, a)]], L))
    keys = [k for k, b in buckets.items() if len(b) >= 2]
    rng.shuffle(keys)
    nneg = 0
    for k in keys:
        b = buckets[k]
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                if nneg >= want_neg or len(rows) >= max_pairs:
                    break
                A = b[i]
                B = b[j]
                if (A[0], A[1], A[2], A[3]) == (B[0], B[1], B[2], B[3]):
                    continue
                c, how = code_verdict(A[5], B[5], intern[k[0]])
                GA, _ = LK.compress(A[5])
                GB, _ = LK.compress(B[5])
                gm = GraphMatcher(nxg(GA), nxg(GB), node_match=lambda p, q: p['c'] == q['c'],
                                  edge_match=lambda p, q: p['l'] == q['l'])
                vf = gm.is_isomorphic()
                nneg += (not c)
                agree += (c == vf)
                stats['alike' if vf else 'not alike'] += 1
                stats['decided by ' + how + (' (alike)' if c else ' (not alike)')] += 1
                rows.append({'look': k[0], 'd': k[1], 'law': PC.LAW_NAMES[k[2]], 'knots': len(A[5].knots),
                             'a': [A[0], A[1], A[2], A[3], A[4]], 'b': [B[0], B[1], B[2], B[3], B[4]],
                             'code': c, 'vf2': vf, 'code_decided_by': how})
            if nneg >= want_neg or len(rows) >= max_pairs:
                break
        if nneg >= want_neg or len(rows) >= max_pairs:
            break
    out = {'pass': agree == len(rows) and len(rows) > 0, 'pairs': len(rows), 'agree': agree, 'stats': dict(stats),
           'knots_range': [min(r['knots'] for r in rows), max(r['knots'] for r in rows)] if rows else None,
           'disagreements': [r for r in rows if r['code'] != r['vf2']],
           'sample_not_alike': [r for r in rows if not r['code']][:40], 'sample_alike': [r for r in rows if r['code']][:20],
           'seconds': round(time.time() - t0, 1)}
    PC.write_json(PC.OUT / 'checks_extra.json', out)
    print('extra check (VF2):', 'PASS' if out['pass'] else 'FAIL', out['pairs'], 'pairs', out['stats'],
          'knots', out['knots_range'], out['seconds'], 's')


if __name__ == '__main__':
    main()
