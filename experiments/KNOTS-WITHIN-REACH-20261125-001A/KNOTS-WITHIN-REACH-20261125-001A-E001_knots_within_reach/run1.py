"""Run 1: the screen and the start-by-start table.  L0 to L7 and L9 to L11 on the 219 three- and four-knot census
starts and the first 1,000 five-knot starts of the registered order (in that order, the laws in the order of the table
within each start), L8 on the 219 only; not-all-equal (parity derived, Settled 4); 100 rounds, 50,000 knots, the guard;
H from every start knot and 16 made knots (8 of class (b), 8 of class (c)); b(t) exact, with births and members by part.
usage: python -B run1.py run --procs 4 [--starts N] [--limit N]      writes run1.jsonl.gz"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import time

import numpy as np

import kwr
import readings as RD
from run0 import check_E
from run2 import classes_at

LAWS1 = ('L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8', 'L9', 'L10', 'L11')
ROUNDS = 100


def starts_in_order():
    small = kwr.small_census()
    five = kwr.five_order()['order'][:1000]
    return [('census:%d' % i, i, True) for i in small] + [('census:%d' % i, i, False) for i in five]


def items(n_starts=None):
    out = []
    st = starts_in_order()
    if n_starts is not None:
        st = st[:n_starts]
    for key, i, small in st:
        for lab in LAWS1:
            if lab == 'L8' and not small:
                continue
            out.append({'start': key, 'index': i, 'small': small, 'law': lab})
    for k, it in enumerate(out):
        it['item'] = k
    return out


def run_item(it):
    t0 = time.time()
    key, lab = it['start'], it['law']
    gr = kwr.Grown(key, kwr.make_law(lab), ROUNDS)
    S = gr.S
    t = gr.rounds_done
    b = gr.births()
    ended = gr.ended is not None
    rec = {'item': it['item'], 'start': key, 'index': it['index'], 'small': it['small'], 'law': lab,
           'rounds_done': t, 'stop': gr.stop, 'ended': gr.ended, 'guard': gr.guard, 'knots': S.n_knots, 'births': b,
           'parity_closing_round': gr.parity_closing_round,
           'parts_per_round': [len(p) for p in gr.parts],
           'part_sizes_per_round': [sorted((len(x) for x in p), reverse=True)[:8] for p in gr.parts],
           'births_by_part': [r['births_by_part'][:8] if r['births_by_part'] else [] for r in gr.recs],
           'members_per_round': [len(m) for m in gr.members]}
    rec['births_reading'] = RD.read(b, 1, ended=ended, kind='b') if b else {'verdict': 'ENDED', 'segment': [1, 0]}
    rec['births_reading_swaps'] = {'ratio_1.1': RD.read(b, 1, ended=ended, kind='b', floor=RD.Fraction(11, 10))
                                   if b else None,
                                   'ratio_1.5': RD.read(b, 1, ended=ended, kind='b', floor=RD.Fraction(3, 2))
                                   if b else None}
    # H from start knots and 16 made knots on the structure after the last round
    G = kwr.Graphs(S)
    s = G.steps_from_start(S.n_start)
    cls, smin = classes_at(gr, t, s, gr.members[t], gr.ended, key, lab, k=8)
    srcs = sorted(set(cls['a'] + cls['b'] + cls['c']))
    D = G.hs(srcs)
    if ended or smin is None:
        ell = {u: kwr.greatest(D[u]) for u in srcs}
    else:
        ell = {u: max(0, smin - int(s[u])) for u in srcs}
    H = {u: kwr.counts_from(D[u], ell[u]) for u in srcs}
    rec.update({'s_min': smin, 'classes': {c: cls[c] for c in 'abc'}, 'ell': {str(u): ell[u] for u in srcs},
                'H': {str(u): H[u] for u in srcs}})
    rec['reading'] = {str(u): RD.read(H[u], 0, ended=ended) for u in srcs}
    rec['reading_swaps'] = {str(u): {'ratio_1.1': RD.label(RD.read(H[u], 0, ended=ended, floor=RD.Fraction(11, 10),
                                                                    earlier=False)),
                                     'ratio_1.5': RD.label(RD.read(H[u], 0, ended=ended, floor=RD.Fraction(3, 2),
                                                                    earlier=False)),
                                     'doubling': RD.doubling(H[u], 0)} for u in srcs}
    labels = {u: ('start' if u < S.n_start else 'made') for u in srcs}
    g = RD.gate(H, labels=labels)
    rec['screen'] = {k: g[k] for k in ('holds', 'j', 'range', 'k', 'K', 'reason', 'spread', 'k_by_j_on_widest',
                                       'zmax', 'j_best') if k in g}
    Dp = G.ps(srcs)
    Hp = {u: kwr.counts_from(Dp[u], ell[u]) for u in srcs}
    rec['parent_steps_differ'] = [u for u in srcs if Hp[u] != H[u]]
    rec['parent_steps_reading'] = {str(u): RD.label(RD.read(Hp[u], 0, ended=ended, earlier=False))
                                   for u in rec['parent_steps_differ']}
    rec['check_E'] = check_E(S)[:5]
    if it['small'] or lab == 'L0':
        pass
    rec['seconds'] = round(time.time() - t0, 2)
    return rec


def _init():
    kwr.cap_memory(6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--starts', type=int, default=None, help='the first N starts of the registered order')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--out', default='run1.jsonl.gz')
    a = ap.parse_args()
    its = items(a.starts)
    if a.limit:
        its = its[:a.limit]
    path = kwr.out_path(a.out)
    done = {r['item'] for r in kwr.read_jsonl(path)}
    its = [it for it in its if it['item'] not in done]
    kwr.log('run 1: %d items to run, %d done before' % (len(its), len(done)))
    W = kwr.JsonlWriter(path)
    t0 = time.time()
    with mp.Pool(a.procs, initializer=_init, maxtasksperchild=50) as pool:
        for k, rec in enumerate(pool.imap_unordered(run_item, its, chunksize=2)):
            W.write(rec)
            if (k + 1) % 100 == 0 or k + 1 == len(its):
                kwr.log('run 1: %d/%d items, %.0fs' % (k + 1, len(its), time.time() - t0))
    W.close()


if __name__ == '__main__':
    main()
