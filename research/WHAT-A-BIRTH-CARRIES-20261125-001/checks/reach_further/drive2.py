"""Driver for scan2.py.  usage: drive2.py OUT TIMEOUT rings | census LO HI [take,take,...]"""
import json, subprocess, sys, time, os
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo, which = sys.argv[1], sys.argv[2], sys.argv[3]
TAKES = ['MET-SOLE', 'MET-ALL', 'MET-FEW', 'MET-MANY', 'MET2-SOLE', 'MET2-ALL', 'MET2-FEW', 'MET2-MANY']
RATIONS = ['FLOOR1', 'CAP-3', 'ORD', 'PARENT-OWING', 'PARENT-OWING-PLAIN']
TREATS = ['CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT']
if which == 'rings':
    starts = ['Ring(5,3)', 'Ring(5,3)+1', 'Ring(5,3)+1+2', 'D2(5,3)', 'Ring(7,3)']
else:
    starts = ['census:%d' % i for i in range(int(sys.argv[4]), int(sys.argv[5]))]
    if len(sys.argv) > 6: TAKES = sys.argv[6].split(',')
jobs = [{'start': s, 'ration': r, 'treatment': t, 'take': k, 'knot_law': 'nae'} for s in starts for k in TAKES for r in RATIONS for t in TREATS]
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'scan2.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(int(os.environ.get('PROBE_THREADS', '8'))) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'runs in', round(time.time() - t0, 1), 's')
