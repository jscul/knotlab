import json, subprocess, sys, time
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo = sys.argv[1], sys.argv[2]
RINGS = ['Ring(5,3)', 'Ring(5,3)+1', 'Ring(5,3)+1+2', 'D2(5,3)', 'Ring(7,3)']
jobs = []
for s in RINGS:
    for ration in ('FLOOR1', 'CAP-3', 'ORD', 'PARENT-OWING', 'PARENT-OWING-PLAIN', 'PARENT-OWING-1', 'PARENT-OWING-CAP3', 'PARENT-OWING-CAP4', 'OFFSHOOT-TWO', 'OFFSHOOT-THREE'):
        for tr in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            jobs.append({'start': s, 'ration': ration, 'treatment': tr, 'take': 'MET-SOLE', 'knot_law': 'nae'})
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'scan.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(6) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'runs in', round(time.time() - t0, 1), 's')
