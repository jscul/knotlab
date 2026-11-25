import json, subprocess, sys, time
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo = sys.argv[1], sys.argv[2]
jobs = []
for st in ['census:%d' % i for i in range(219)] + ['Ring(5,3)', 'Ring(5,3)+1', 'Ring(5,3)+1+2', 'D2(5,3)', 'Ring(7,3)']:
    for s in (2, 3, 4, 5, 6):
        jobs.append({'start': st, 'ration': 'PARENT-OWING', 'treatment': 'CANCEL-OFFSHOOT', 'take': 'MET-SOLE', 'knot_law': 'nae', 's': s, 'explore': True})
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'two_births.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(8) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'runs in', round(time.time() - t0, 1), 's')
