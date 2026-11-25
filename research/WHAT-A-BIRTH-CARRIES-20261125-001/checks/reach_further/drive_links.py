"""Runs links.py for every run of the given scan outputs that held at least one four-run test."""
import json, subprocess, sys, time, os
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo, files = sys.argv[1], sys.argv[2], sys.argv[3:]
jobs = []
for fn in files:
    for l in open(fn):
        d = json.loads(l)
        if 'error' not in d and d['tests']: jobs.append(d['spec'])
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'links.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(int(os.environ.get('PROBE_THREADS', '8'))) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'runs in', round(time.time() - t0, 1), 's')
