"""Run 2: the full gate (KD 4) with the scaling condition, the roster count P beside it, checks E, F, R, and the
registered swaps (parent steps; retired knots counted, not stepped through; every live knot for P; thresholds; BOUND
and the doubling reading; HOLD under L3 and L6; bounds of 60 rounds and 20,000 knots; class (d)).
usage: python -B run2.py items                  (lists the items in registered order)
       python -B run2.py run --procs 4 [--only i,j,...] [--limit N]
Writes run2.jsonl.gz (one record per item, the counts themselves included) in the artifact folder."""
from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import kwr
import readings as RD
from run0 import check_E, check_R


def items():
    """Run 2's items in the registered order (PR, runs table): the named starts under L0, L6, L7 at T = 66 (2T =
    132); the bare rings under L0 at 264 and 528; the first 50 five-knot starts of the registered order and the 9 small
    starts under L0, L6, L7 at 66 and 132.  Then the swaps (R 19)."""
    out = []
    named = list(kwr.named()['named_starts'])
    rings = [k for k in named if k.startswith('Ring(') and k.endswith(',2)')]
    for key in named:
        for lab in ('L0', 'L6', 'L7'):
            out.append({'start': key, 'law': lab, 'T': 66, 'kind': 'named'})
    for key in sorted(rings, key=lambda k: int(k[5:-3])):
        out.append({'start': key, 'law': 'L0', 'T': 264, 'kind': 'bare ring'})
    five = kwr.five_order()['order'][:50]
    small = kwr.read_json(os.path.join(kwr.DATA, 'run2_small_starts.json'))
    small_idx = small['degree_2'] + small['degree_3_or_more']
    for i in five + small_idx:
        for lab in ('L0', 'L6', 'L7'):
            out.append({'start': 'census:%d' % i, 'law': lab, 'T': 66, 'kind': 'census'})
    # swaps (named starts): HOLD under L3 and L6; bounds of 60 rounds and 20,000 knots under L0, L6, L7
    for key in named:
        for lab in ('L3', 'L6'):
            out.append({'start': key, 'law': lab, 'T': 66, 'kind': 'swap HOLD', 'release': 'HOLD'})
    for key in named:
        for lab in ('L0', 'L6', 'L7'):
            out.append({'start': key, 'law': lab, 'T': 60, 'kind': 'swap bounds', 'knot_bound': 20000})
    # P9's L1: the roster count only, on run 2's starts (R 20)
    for key in named:
        out.append({'start': key, 'law': 'L1', 'T': 66, 'kind': 'P only'})
    for i in five + small_idx:
        out.append({'start': 'census:%d' % i, 'law': 'L1', 'T': 66, 'kind': 'P only'})
    for k, it in enumerate(out):
        it['item'] = k
    return out


# ------------------------------------------------------------------------------------------------ one structure
def classes_at(gr, t, s, members, ended_kind, seedkey, lab, k=64):
    """KD 2.3: (a) every start knot; (b) made knots with s <= s_min/4; (c) floor(s_min/2) - 2 <= s <= floor(s_min/2);
    (d) floor(3 s_min/4) - 2 <= s <= floor(3 s_min/4); members never; each sampled from the candidates sorted by name
    (seeds KD 2.4)."""
    S = gr.S
    Nt = gr.n_knots[t]
    mset = set(members)
    n0 = S.n_start
    if not members:
        return {'a': list(range(n0)), 'b': [], 'c': [], 'd': []}, None
    smin = int(min(s[u] for u in members))
    made = [u for u in range(n0, Nt) if u not in mset and np.isfinite(s[u])]
    cand = {'b': [u for u in made if 4 * int(s[u]) <= smin],
            'c': [u for u in made if smin // 2 - 2 <= int(s[u]) <= smin // 2],
            'd': [u for u in made if (3 * smin) // 4 - 2 <= int(s[u]) <= (3 * smin) // 4]}
    out = {'a': list(range(n0))}
    for c in ('b', 'c', 'd'):
        out[c] = kwr.sample_sorted(kwr.rng_for(seedkey, lab, 'nae', c), cand[c], k)
    out['_candidates'] = {c: len(v) for c, v in cand.items()}
    return out, smin


def read_counts(G, srcs, ell, ended, steps='hs', blocked=None):
    if steps == 'hs':
        D = G.hs(srcs)
    elif steps == 'ps':
        D = G.ps(srcs)
    else:
        D = G.hs_not_through(srcs, blocked)
    return {u: kwr.counts_from(D[u], ell[u]) for u in srcs}, D


def ell_of(srcs, s, smin, ended, D):
    if ended:
        return {u: kwr.greatest(D[u]) for u in srcs}
    return {u: smin - int(s[u]) for u in srcs}


def roster_count(gr, t, seedkey, lab, live=False):
    """KD 2.2 / 4.6: P_t(u, r) from up to 8 sampled members (class `members`), by witnessed steps in u's part; the
    number of parts and the members per part.  live=True: every live knot (barred included) as the roster (swap)."""
    S = gr.S
    Nt = gr.n_knots[t]
    if live:
        mem = sorted(u for u in range(Nt) if any(len([w for w in S.holders[d] if w < Nt]) == 1
                                                   for d in S.places[u]))
    else:
        mem = gr.members[t]
    if not mem:
        return {'members': 0, 'parts': 0}
    ms = kwr.met_sets(S, mem, Nt)
    parts = kwr.parts_of(S, mem, Nt, ms)
    src = kwr.sample_sorted(kwr.rng_for(seedkey, lab, 'nae', 'members'), mem, 8)
    W, idx = kwr.ws_from(S, mem, src, Nt, ms)
    out = {'members': len(mem), 'parts': len(parts), 'part_sizes': sorted((len(p) for p in parts), reverse=True)[:50],
           'counted_from': []}
    for u in src:
        row = W[u]
        fin = row[np.isfinite(row)].astype(int)
        g = int(fin.max())
        P = [int(x) for x in np.cumsum(np.bincount(fin, minlength=g + 1))]
        if g + 1 < 8:
            v = {'verdict': 'ALL WITHIN r', 'r': g}
        else:
            v = RD.read(P, 0, kind='P', with_bound=False)
        out['counted_from'].append({'member': u, 'greatest_ws': g, 'P': P, 'reading': v, 'label': RD.label(v)
                                    if v['verdict'] != 'ALL WITHIN r' else 'ALL WITHIN r'})
    return out


def at_round(gr, t, it, Gt=None, want_swaps=True):
    """Every reading of run 2 on the structure after round t (or the last round reached)."""
    S = gr.S
    key, lab = it['start'], it['law']
    seedkey = key
    t = min(t, gr.rounds_done)
    Nt = gr.n_knots[t]
    G = Gt if Gt is not None else kwr.Graphs(S, Nt)
    s = G.steps_from_start(S.n_start)
    members = gr.members[t]
    ended = gr.ended is not None and t == gr.rounds_done
    cls, smin = classes_at(gr, t, s, members, gr.ended, seedkey, lab)
    srcs = sorted(set(cls['a'] + cls['b'] + cls['c'] + cls['d']))
    Dh = G.hs(srcs)
    if ended or smin is None:
        ell = {u: kwr.greatest(Dh[u]) for u in srcs}
    else:
        ell = {u: smin - int(s[u]) for u in srcs}
    ell = {u: max(0, v) for u, v in ell.items()}
    H = {u: kwr.counts_from(Dh[u], ell[u]) for u in srcs}
    rec = {'round': t, 'knots': Nt, 's_min': smin, 'ended_here': ended, 'classes': {c: cls[c] for c in 'abcd'},
           'candidates': cls.get('_candidates'), 'ell': {str(u): ell[u] for u in srcs},
           'H': {str(u): H[u] for u in srcs}}
    # per-knot readings
    rec['reading'] = {str(u): RD.read(H[u], 0, ended=ended) for u in srcs}
    rec['bound'] = {str(u): RD.bound(H[u], 0) for u in srcs}
    rec['doubling'] = {str(u): RD.doubling(H[u], 0) for u in srcs}
    labels = {u: ('start' if u < S.n_start else 'made') for u in srcs}
    gate_knots = sorted(set(cls['a'] + cls['b'] + cls['c']))
    C = {u: H[u] for u in gate_knots}
    g = RD.gate(C, labels=labels)
    g['k_by_class'] = _k_by_class(C, g, cls)
    rec['gate'] = _short(g)
    if want_swaps:
        g2 = RD.gate(C, factor=4, limit=3, labels=labels)
        rec['gate_swap_thresholds'] = _short(g2)
        # parent steps (KD 1.6: null outside the start's meetings)
        Dp = G.ps(gate_knots)
        Hp = {u: kwr.counts_from(Dp[u], ell[u]) for u in gate_knots}
        rec['H_parent_steps_differs'] = [u for u in gate_knots if Hp[u] != H[u]]
        rec['H_parent_steps'] = {str(u): Hp[u] for u in rec['H_parent_steps_differs']}
        rec['gate_parent_steps'] = _short(RD.gate(Hp, labels=labels))
        if gr.retired:
            blocked = [x for x in gr.retired if x < Nt]
            Dr = G.hs_not_through(gate_knots, blocked)
            Hr = {u: kwr.counts_from(Dr[u], ell[u]) for u in gate_knots}
            rec['H_retired_not_stepped_differs'] = [u for u in gate_knots if Hr[u] != H[u]]
            rec['H_retired_not_stepped'] = {str(u): Hr[u] for u in rec['H_retired_not_stepped_differs']}
            rec['gate_retired_not_stepped'] = _short(RD.gate(Hr, labels=labels))
    return rec, G, s, srcs, ell, H


def _k_by_class(C, g, cls):
    out = {}
    if not g.get('holds'):
        return None
    j, (a, z) = g['j'], g['range']
    for c in ('a', 'b', 'c'):
        ks = [u for u in cls[c] if u in C]
        out[c] = {'K': len(ks), 'k': sum(1 for u in ks if RD.ratio_ok(C[u], 0, a, z, j)[0])}
    return out


def _short(g):
    keep = ('holds', 'j', 'range', 'k', 'K', 'reason', 'spread', 'k_by_j_on_widest', 'least_l', 'zmax', 'j_best',
            'widest', 'k_by_class', 'per_knot_ratio_max')
    out = {k: g[k] for k in keep if k in g}
    if 'earlier' in g:
        out['earlier'] = [{k: e[k] for k in ('j', 'range', 'spread') if k in e} for e in g['earlier']]
    return out


def check_F(gr, t, srcs, ell, H):
    """KD 7.7 check F: H after round t and after round t + 10 agree on the kept range."""
    t2 = min(t + 10, gr.rounds_done)
    if t2 <= t:
        return {'t': t, 't2': t2, 'checked': 0, 'note': 'no later round'}
    G2 = kwr.Graphs(gr.S, gr.n_knots[t2])
    D2 = G2.hs(srcs)
    bad = [u for u in srcs if kwr.counts_from(D2[u], ell[u]) != H[u]]
    return {'t': t, 't2': t2, 'checked': len(srcs), 'bad': bad[:20], 'n_bad': len(bad)}


def run_item(it):
    t0 = time.time()
    key, lab, T = it['start'], it['law'], it['T']
    law = kwr.make_law(lab, release=it.get('release', 'RELEASE'))
    kb = it.get('knot_bound', kwr.KNOT_BOUND)
    target = 2 * T + 10
    gr = kwr.Grown(key, law, target, knot_bound=kb)
    rec = {'item': it['item'], 'start': key, 'law': lab, 'release': law.release, 'T': T, 'kind': it['kind'],
           'knot_bound': kb, 'rounds_done': gr.rounds_done, 'stop': gr.stop, 'ended': gr.ended, 'guard': gr.guard,
           'knots_final': gr.S.n_knots, 'births': gr.births(), 'parity_closing_round': gr.parity_closing_round,
           'parts_per_round': [len(p) for p in gr.parts],
           'largest_part_per_round': [max((len(x) for x in p), default=0) for p in gr.parts],
           'members_per_round': [len(m) for m in gr.members]}
    rec['births_reading'] = RD.read(gr.births(), 1, ended=gr.ended is not None, kind='b') if gr.births() else None
    if it['kind'] == 'P only':
        for TT in (T, 2 * T):
            if gr.reached(TT) or gr.ended:
                rec['P_%d' % TT] = roster_count(gr, min(TT, gr.rounds_done), key, lab)
                rec['P_%d_round' % TT] = min(TT, gr.rounds_done)
        rec['seconds'] = round(time.time() - t0, 2)
        return rec
    # the reached rounds: T and 2T are read only if reached, or if the run ended before them
    for TT, name in ((T, 'at_T'), (2 * T, 'at_2T')):
        reached = gr.reached(TT)
        if not reached and gr.ended is None:
            rec[name] = {'round': TT, 'not_reached': True, 'last_round': gr.rounds_done}
            continue
        r, G, s, srcs, ell, H = at_round(gr, TT, it)
        r['check_F'] = check_F(gr, r['round'], srcs, ell, H)
        r['P'] = roster_count(gr, r['round'], key, lab)
        r['P_live_swap'] = roster_count(gr, r['round'], key, lab, live=True)
        rec[name] = r
    # checks E and R on the final structure
    Gf = kwr.Graphs(gr.S)
    sf = Gf.steps_from_start(gr.S.n_start)
    rec['check_E'] = check_E(gr.S)[:5]
    rec['check_R'] = check_R(gr, Gf, sf)[:5]
    rec['verdict'] = verdict(rec)
    rec['seconds'] = round(time.time() - t0, 2)
    return rec


def verdict(rec):
    """The claim's question 2: both / gate only (range does not lengthen, or set by the start) / no gate /
    undecided (the least l below 32, or the run at 2T past the knot bound)."""
    A, B = rec.get('at_T'), rec.get('at_2T')
    if not isinstance(A, dict) or A.get('not_reached'):
        return {'answer': 'undecided', 'why': 'T past the knot bound or the guard (last round %s)' % rec['rounds_done']}
    g = A['gate']
    if not g.get('holds'):
        if 'below' in str(g.get('reason', '')):
            return {'answer': 'undecided', 'why': 'least kept range %s below 32' % g.get('zmax')}
        return {'answer': 'no gate', 'k': g.get('k'), 'K': g.get('K'), 'j_best': g.get('j_best')}
    if not isinstance(B, dict) or B.get('not_reached'):
        return {'answer': 'undecided', 'why': 'gate at T holds; 2T past the knot bound or the guard', 'j': g['j'],
                'range_T': g['range']}
    g2 = B['gate']
    if g2.get('holds') and g2['j'] == g['j'] and g2['range'][1] >= 1.8 * g['range'][1]:
        return {'answer': 'both', 'j': g['j'], 'range_T': g['range'], 'range_2T': g2['range']}
    return {'answer': 'gate only', 'j': g['j'], 'range_T': g['range'],
            'range_2T': g2.get('range'), 'gate_2T_holds': g2.get('holds'), 'j_2T': g2.get('j'),
            'why': 'range does not lengthen' if g2.get('holds') else 'no gate at 2T'}


def _small_one(i):
    gr = kwr.Grown('census:%d' % i, kwr.make_law('L0'), 40, parts_every_round=False)
    b = gr.births()
    v = RD.read(b, 1, ended=gr.ended is not None, kind='b') if b else {'verdict': 'ENDED'}
    return i, v, gr.rounds_done, gr.stop


def recompute_small(procs):
    """PR, Starts and files: the 9 three- and four-knot census starts whose births under L0, not-all-equal, 40 rounds,
    at most 50,000 knots, read POWER(j >= 2); recomputed before run 2 and compared with run2_small_starts.json."""
    reg = kwr.read_json(os.path.join(kwr.DATA, 'run2_small_starts.json'))
    with mp.Pool(procs, initializer=_init) as pool:
        res = pool.map(_small_one, kwr.small_census())
    d2 = sorted(i for i, v, _, _ in res if v['verdict'] == 'POWER' and v['j'] == 2)
    d3 = sorted(i for i, v, _, _ in res if v['verdict'] == 'POWER' and v['j'] >= 3)
    out = {'degree_2': d2, 'degree_3_or_more': d3, 'registered': reg,
           'same': d2 == reg['degree_2'] and d3 == reg['degree_3_or_more'],
           'readings': {str(i): {'label': RD.label(v), 'segment': v.get('segment'), 'rounds': r, 'stop': st}
                        for i, v, r, st in res}}
    kwr.write_json(kwr.out_path('run2_small_recomputed.json'), out)
    kwr.log('small starts recomputed: degree 2 %s, degree >= 3 %s; same as registered: %s' % (d2, d3, out['same']))


def _init():
    kwr.cap_memory(6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--only', default=None)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--out', default='run2.jsonl.gz')
    a = ap.parse_args()
    its = items()
    if a.cmd == 'items':
        for it in its:
            print(it)
        print(len(its), 'items')
        return
    if a.cmd == 'recompute':
        recompute_small(a.procs)
        return
    if a.only:
        want = {int(x) for x in a.only.split(',')}
        its = [it for it in its if it['item'] in want]
    if a.limit:
        its = its[:a.limit]
    path = kwr.out_path(a.out)
    done = {r['item'] for r in kwr.read_jsonl(path)}
    its = [it for it in its if it['item'] not in done]
    kwr.log('run 2: %d items to run, %d done before' % (len(its), len(done)))
    W = kwr.JsonlWriter(path)
    t0 = time.time()
    with mp.Pool(a.procs, initializer=_init, maxtasksperchild=20) as pool:
        for k, rec in enumerate(pool.imap_unordered(run_item, its)):
            W.write(rec)
            kwr.log('item %d %s %s T=%d: %s; %.1fs (%d/%d, %.0fs)' % (rec['item'], rec['start'], rec['law'], rec['T'],
                    rec.get('verdict', {}).get('answer', '-'), rec['seconds'], k + 1, len(its), time.time() - t0))
    W.close()


if __name__ == '__main__':
    main()
