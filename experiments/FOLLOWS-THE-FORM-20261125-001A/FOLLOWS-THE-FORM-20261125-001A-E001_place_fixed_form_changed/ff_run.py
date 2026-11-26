"""Runs R1, R2, R2u, R3, R4 of FOLLOWS-THE-FORM-20261125-001A-E001: one chunk of a run set per process.

  python -B ff_run.py run  --runset R1 --chunk i/8 [--limit-first ABCDE]   # writes runs_<R>_<i>of<n>.jsonl.gz
  python -B ff_run.py time --runset R1 --every 100                         # times a systematic sample, one process

A chunk is the runs whose index in the registered order is i modulo n (deviations 26).  `--limit-first` keeps only
the runs of the listed first seeds (a prefix of the registered order, used only for a cut recorded beforehand).
"""
import sys

sys.dont_write_bytecode = True

import argparse
import os
import time
import traceback

import ff_core as C


def chunk_runs(runset, i, n, limit_first=None):
    runs = C.runset_runs(runset)
    if limit_first:
        runs = [r for r in runs if r['first'] in limit_first]
    return [r for j, r in enumerate(runs) if j % n == i]


def run_chunk(runset, chunk, limit_first=None):
    i, n = (int(x) for x in chunk.split('/'))
    C.cap_memory(6)
    runs = chunk_runs(runset, i, n, limit_first)
    path = C.out_path('runs_%s_%dof%d.jsonl.gz' % (runset, i, n))
    out = C.JsonLines(path)
    t0 = time.time()
    nerr = 0
    for k, r in enumerate(runs):
        try:
            rec = C.do_run(r)
        except Exception as e:          # recorded, never hidden (a MemoryError would be a deviation)
            nerr += 1
            rec = {k2: r[k2] for k2 in r}
            rec['take'] = C.take_label(r['take'])
            rec['error'] = '%s: %s' % (type(e).__name__, e)
            rec['traceback'] = traceback.format_exc()[-2000:]
        out.write(rec)
        if k % 200 == 0:
            C.log(runset, chunk, k, '/', len(runs), '%.1fs' % (time.time() - t0))
    out.close()
    C.log(runset, chunk, 'done', len(runs), 'runs', 'errors', nerr, '%.1fs' % (time.time() - t0))


def time_sample(runset, every):
    C.cap_memory(6)
    runs = C.runset_runs(runset)
    sample = runs[::every]
    t0 = time.time()
    worst = (0, None)
    for r in sample:
        t1 = time.time()
        C.do_run(r)
        dt = time.time() - t1
        if dt > worst[0]:
            worst = (dt, C.run_key(r))
    tot = time.time() - t0
    per = tot / len(sample)
    est = per * len(runs) / 8
    C.log('%s: %d runs timed of %d; %.3f s a run; estimate on 8 processes %.1f min; slowest %.2f s %s'
          % (runset, len(sample), len(runs), per, est / 60, worst[0], worst[1]))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('run', 'time'))
    ap.add_argument('--runset', required=True, choices=sorted(C.RUNSETS))
    ap.add_argument('--chunk', default='0/1')
    ap.add_argument('--every', type=int, default=100)
    ap.add_argument('--limit-first', default=None)
    a = ap.parse_args()
    C.check_frozen()
    if a.what == 'run':
        run_chunk(a.runset, a.chunk, a.limit_first)
    else:
        time_sample(a.runset, a.every)
