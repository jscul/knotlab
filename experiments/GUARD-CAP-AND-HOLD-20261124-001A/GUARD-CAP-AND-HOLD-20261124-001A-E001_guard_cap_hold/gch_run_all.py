"""Run every registered configuration (runs 2 to 4), at most 6 processes at once.

    python -B gch_run_all.py [--only SUBSTRING] [--jobs 6] [--list]

Each configuration runs as its own process (gch_run.py) with an 8 GB address-space cap; its log goes to
artifacts/.../logs/<slug>.log and every start and end is written to artifacts/.../run_all.log with the elapsed time.
A configuration whose output already exists is skipped.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gch_configs import configs, FAMILY_NAMES, CAP  # noqa: E402
from gch_run import OUT, slug  # noqa: E402

PY = str(HERE.parents[2] / '.venv' / 'bin' / 'python')
LOGS = OUT.parent / 'logs'


def command(c):
    cid, start, fam, r, g = c
    return [PY, '-B', str(HERE / 'gch_run.py'), '--start', start, '--family', FAMILY_NAMES[fam], '--cutoff', str(r),
            '--law', g.replace("'", 'P'), '--cap', str(CAP), '--id', cid]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=None)
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    cs = configs()
    if a.only:
        cs = [c for c in cs if a.only in c[0]]
    # larger cutoffs first, cheap guards last
    cs.sort(key=lambda c: (c[4] == 'CONTROL', -c[3], c[0]))
    if a.list:
        for c in cs:
            print(' '.join(command(c)))
        print(len(cs))
        return
    LOGS.mkdir(parents=True, exist_ok=True)
    todo = [c for c in cs if not (OUT / (slug(c[0]) + '.json')).exists()]
    running = []
    t0 = time.time()
    while todo or running:
        while todo and len(running) < a.jobs:
            c = todo.pop(0)
            log = open(LOGS / (slug(c[0]) + '.log'), 'w')
            p = subprocess.Popen(command(c), stdout=log, stderr=subprocess.STDOUT, cwd=str(HERE))
            running.append((p, c[0], time.time(), log))
            print('%8.1f start %s (pid %d)' % (time.time() - t0, c[0], p.pid), flush=True)
        time.sleep(0.5)
        still = []
        for p, cid, ts, log in running:
            rc = p.poll()
            if rc is None:
                still.append((p, cid, ts, log))
            else:
                log.close()
                print('%8.1f done  %s rc=%d %.1fs' % (time.time() - t0, cid, rc, time.time() - ts), flush=True)
        running = still
    print('all done in %.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
