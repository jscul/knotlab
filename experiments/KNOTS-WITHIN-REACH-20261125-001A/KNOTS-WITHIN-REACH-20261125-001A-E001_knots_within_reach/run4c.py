"""Run 4c (PR, runs table; the swap of uniform takes): T9 and T10 under the 4n numberings of KD 7.3 on the 17 named
starts; T1 to T8 under OLDEST and NEWEST with the first 10 numberings of KD 7.3's list (no run of run 4 is "held by
hubs", so not all 4n); both knot laws; 100 rounds, 50,000 knots.  Read: the claim-3 verdict of each run, and how many
numberings change it against the start's own numbering.
usage: python -B run4c.py run --procs 4      writes run4c.jsonl.gz"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import time

import enum4b
import kwr
from run4 import READ_ROUNDS, greatest_steps
from run5 import _View


def items():
    out = []
    for key in kwr.named()['named_starts']:
        stars = kwr.start_stars(key)
        nb = enum4b.numberings(stars)
        for kl in ('parity', 'nae'):
            for lab in ('T9', 'T10'):
                for k, nbg in enumerate(nb):
                    out.append({'start': key, 'law': lab, 'choice': 'OLDEST', 'knot_law': kl, 'numbering': nbg['id'],
                                'k': k})
            for lab in ('T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'):
                for ch in ('OLDEST', 'NEWEST'):
                    for k, nbg in enumerate(nb[:10]):
                        out.append({'start': key, 'law': lab, 'choice': ch, 'knot_law': kl, 'numbering': nbg['id'],
                                    'k': k})
    for i, it in enumerate(out):
        it['item'] = i
    return out


def run_item(it):
    t0 = time.time()
    stars = kwr.start_stars(it['start'])
    nb = {n['id']: n['stars'] for n in enumerate4b_numberings(stars)}
    S = kwr.pm.from_stars(nb[it['numbering']])
    law = kwr.make_law(it['law'], knot_law=it['knot_law'], choice=it['choice'])
    gr = kwr.Grown(it['start'], law, 100, S=S, parts_every_round=False)
    reads = {}
    for t in (50, 100):
        if t > gr.rounds_done:
            continue
        N = gr.n_knots[t]
        V = _View(gr.S, N, gr.n_dist[t])
        V.parents = gr.S.parents[:N]
        reads[str(t)] = {'knots': N, 'steps': greatest_steps(V, N, range(gr.S.n_start))}
    rec = dict(it)
    rec.update({'rounds_done': gr.rounds_done, 'stop': gr.stop, 'ended': gr.ended, 'reads': reads,
                'seconds': round(time.time() - t0, 3)})
    return rec


_NB = {}


def enumerate4b_numberings(stars):
    key = repr(stars)
    if key not in _NB:
        _NB[key] = enum4b.numberings(stars)
    return _NB[key]


def _init():
    kwr.cap_memory(6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--procs', type=int, default=4)
    ap.add_argument('--limit', type=int, default=None)
    a = ap.parse_args()
    its = items()
    if a.limit:
        its = its[:a.limit]
    path = kwr.out_path('run4c.jsonl.gz')
    done = {r['item'] for r in kwr.read_jsonl(path)}
    its = [x for x in its if x['item'] not in done]
    kwr.log('run 4c: %d items' % len(its))
    W = kwr.JsonlWriter(path)
    t0 = time.time()
    with mp.Pool(a.procs, initializer=_init, maxtasksperchild=500) as pool:
        for k, rec in enumerate(pool.imap_unordered(run_item, its, chunksize=4)):
            W.write(rec)
            if (k + 1) % 1000 == 0 or k + 1 == len(its):
                kwr.log('run 4c: %d/%d, %.0fs' % (k + 1, len(its), time.time() - t0))
    W.close()


if __name__ == '__main__':
    main()
