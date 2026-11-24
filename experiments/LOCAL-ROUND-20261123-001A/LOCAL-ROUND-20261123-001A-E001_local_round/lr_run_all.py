"""Run every registered configuration (items 2 to 4, and the extra for P4), up to 8 processes at once.

    python -B lr_run_all.py [--only SUBSTRING] [--jobs 8]

Each configuration runs as its own process (lr_run.py) with an 8 GB address-space cap and writes its log to
artifacts/.../logs/<slug>.log.  A configuration whose output already exists is skipped.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lr_configs as K  # noqa: E402
from lr_run import OUT, slug  # noqa: E402

PY = str(HERE.parents[2] / '.venv' / 'bin' / 'python')
LOGS = OUT.parent / 'logs'
BUDGET_TABLE = 420
BUDGET_OTHER = 300


def configs():
    out = []
    for row, start, fam, cuts in K.TABLE:
        for r in cuts:
            for law in K.LAWS6:
                out.append(('%s__r%d__%s' % (row, r, law), start, fam, r, law, K.CAP_TABLE, BUDGET_TABLE))
    for start in K.TD_STARTS:
        for d in K.TD_DS:
            law = 'T(%d)' % d
            out.append(('TD-%s__r1__%s' % (start, law), start, K.R3W, 1, law, K.CAP_OTHER, BUDGET_OTHER))
    for row, start, fam, r in K.BEYOND:
        for law in ('R1', 'R2', 'R3'):
            out.append(('%s__%s' % (row, law), start, fam, r, law, K.CAP_OTHER, BUDGET_OTHER))
    for row, start, fam, r, law in K.EXTRA:
        out.append(('%s__r%d__%s' % (row.replace('-R3L', ''), r, law), start, fam, r, law, K.CAP_OTHER, BUDGET_OTHER))
    return out


def weight(c):
    cid, start, fam, r, law, cap, budget = c
    cheap = law in ('R0', 'CONTROL')
    return (cheap, -r, cid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=None)
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    cs = configs()
    if a.only:
        cs = [c for c in cs if a.only in c[0]]
    cs.sort(key=weight)
    if a.list:
        for c in cs:
            print(c)
        print(len(cs))
        return
    LOGS.mkdir(parents=True, exist_ok=True)
    todo = [c for c in cs if not (OUT / (slug(c[0]) + '.json')).exists()
            and not (OUT / (slug(c[0]) + '.json.gz')).exists()]
    running = []
    t0 = time.time()
    while todo or running:
        while todo and len(running) < a.jobs:
            cid, start, fam, r, law, cap, budget = todo.pop(0)
            cmd = [PY, '-B', str(HERE / 'lr_run.py'), '--start', start, '--ration', fam[0], '--treatment', fam[1],
                   '--cutoff', str(r), '--law', law, '--cap', str(cap), '--budget', str(budget), '--id', cid]
            log = open(LOGS / (slug(cid) + '.log'), 'w')
            p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=str(HERE))
            running.append((p, cid, time.time(), log))
            print('%7.1f start %s (pid %d)' % (time.time() - t0, cid, p.pid), flush=True)
        time.sleep(0.5)
        still = []
        for p, cid, ts, log in running:
            rc = p.poll()
            if rc is None:
                still.append((p, cid, ts, log))
            else:
                log.close()
                print('%7.1f done  %s rc=%d %.1fs' % (time.time() - t0, cid, rc, time.time() - ts), flush=True)
        running = still
    print('all done in %.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
