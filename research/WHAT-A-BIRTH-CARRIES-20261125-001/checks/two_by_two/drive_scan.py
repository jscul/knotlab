import json, subprocess, sys, time
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, lo, hi, tmo = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
extra = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
jobs = []
for i in range(lo, hi):
    j = {'start': 'census:%d' % i, 'ration': 'PARENT-OWING', 'treatment': 'CANCEL-OFFSHOOT', 'take': 'MET-SOLE', 'knot_law': 'nae'}
    j.update(extra); jobs.append(j)
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'scan.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(8) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'runs in', round(time.time() - t0, 1), 's')
