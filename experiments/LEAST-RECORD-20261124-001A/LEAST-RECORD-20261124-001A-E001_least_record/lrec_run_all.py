"""Every registered process of runs 2, 5, 6 and 7, at most six at once, each with its own 8 GB cap (lrec_run.py sets it).

    python -B lrec_run_all.py [--only SUBSTRING] [--jobs 6]
"""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

import pfh_common as PC

HERE = Path(__file__).resolve().parent
PY = str(PC.ROOT / '.venv' / 'bin' / 'python')
ORDER = [('ORD', 'G'), ('ORD', 'H'), ('ORD', 'P'), ('ORD', 'N'), ('ORD', 'M'),
         ('R3W', 'G'), ('R3W', 'H'), ('R3W', 'P'), ('R3W', 'N'), ('R3W', 'M'),
         ('F1O', 'G'), ('F1O', 'H'), ('F1O', 'P'), ('F1O', 'N'), ('F1O', 'M'),
         ('F1R', 'G'), ('F1R', 'H'), ('F1R', 'P'), ('F1R', 'N'), ('F1R', 'M'),
         ('H-C3W', 'P3'), ('H-R3W', 'P3'), ('H-F1R', 'P3'), ('H-F1O', 'P3')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=None)
    ap.add_argument('--jobs', type=int, default=6)
    a = ap.parse_args()
    todo = [c for c in ORDER if a.only is None or a.only in '%s %s' % c]
    logs = PC.OUT / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    running = []
    t0 = time.time()
    while todo or running:
        while todo and len(running) < a.jobs:
            law, chain = todo.pop(0)
            cmd = ['/usr/bin/time', '-v', PY, '-B', str(HERE / 'lrec_run.py'), '--law', law, '--chain', chain]
            fh = open(logs / ('run_%s_%s.log' % (law, chain)), 'w')
            p = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=str(HERE))
            running.append((p, law, chain, time.time(), fh))
            print('%7.1f start %s %s' % (time.time() - t0, law, chain), flush=True)
        time.sleep(1)
        still = []
        for p, law, chain, ts, fh in running:
            rc = p.poll()
            if rc is None:
                still.append((p, law, chain, ts, fh))
            else:
                fh.close()
                print('%7.1f done  %s %s rc=%d %.1fs' % (time.time() - t0, law, chain, rc, time.time() - ts), flush=True)
        running = still
    print('all done %.1fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
