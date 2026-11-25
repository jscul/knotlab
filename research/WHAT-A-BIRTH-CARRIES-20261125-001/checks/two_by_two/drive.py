import json, subprocess, sys, time
from multiprocessing.pool import ThreadPool
PY = sys.executable
RINGS = ['Ring(5,3)', 'Ring(5,3)+1', 'Ring(5,3)+1+2', 'D2(5,3)', 'Ring(7,3)']
ALL = ['two-knot', 'made-3', 'three-knot', 'made-4'] + RINGS
jobs = []
which = sys.argv[1]
if which == 'main':
    for s in RINGS:
        for kl in ('nae', 'parity'):
            for ration in ('PARENT-OWING', 'PARENT-OWING-PLAIN', 'PARENT-OWING-CAP4'):
                jobs.append({'start': s, 'ration': ration, 'treatment': 'CANCEL-OFFSHOOT', 'take': 'MET-SOLE', 'knot_law': kl})
            jobs.append({'start': s, 'ration': 'FLOOR1', 'treatment': 'CANCEL-WAIT', 'take': 'MET-SOLE', 'knot_law': kl})
elif which == 'planted':
    for s in ALL:
        for ration in ('FLOOR1', 'CAP-3', 'ORD'):
            for tr in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
                jobs.append({'start': s, 'ration': ration, 'treatment': tr, 'take': 'J-EACH-PART', 'knot_law': 'nae', 'rounds': 4, 's_range': [1, 2, 3]})
if which == 'census':
    lo, hi = int(sys.argv[3]), int(sys.argv[4])
    for i in range(lo, hi):
        jobs.append({'start': 'census:%d' % i, 'ration': 'PARENT-OWING', 'treatment': 'CANCEL-OFFSHOOT', 'take': 'MET-SOLE', 'knot_law': 'nae'})
def run(j):
    p = subprocess.run(['timeout', '240', PY, '-B', 'tbt.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-400:], 'returncode': p.returncode})
    d = json.loads(p.stdout.strip().splitlines()[-1]); d['spec'] = j
    return json.dumps(d)
t0 = time.time()
with ThreadPool(6) as pool, open(sys.argv[2], 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'runs in', round(time.time() - t0, 1), 's')
