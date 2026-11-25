"""Run probe.py on the 23 fast starts under the given laws.  usage: drive.py L0,L6,L9,L11 nae out.jsonl"""
import json, subprocess, sys, itertools, time
from multiprocessing.pool import ThreadPool
import os
HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
fast = json.load(open(os.path.join(HERE, 'fast_starts.json')))['L0 fast']
laws = sys.argv[1].split(','); knot_law = sys.argv[2]; out = sys.argv[3]
jobs = [(s, l) for s in fast for l in laws]
def run(j):
    s, l = j
    t = time.time()
    p = subprocess.run(['timeout', '600', PY, '-B', os.path.join(HERE, 'probe.py'), s, l, knot_law, '40', '10,15,20,25,30,35,40'], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'start': s, 'law': l, 'knot law': knot_law, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(6) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'runs in', round(time.time() - t0, 1), 's')
