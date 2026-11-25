import json, subprocess, sys, time, os
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo = sys.argv[1], sys.argv[2]
takes = json.loads(sys.argv[3]) if len(sys.argv) > 3 else [None, 'MET-SOLE']
FIRSTS = ['A one knot', 'B two knots', 'C ring of three', 'D chain, at the end', 'E chain, in the middle']
if os.environ.get('PROBE_FIRSTS') == 'unseen':
    FIRSTS = ['F one knot, two loose', 'G two knots, the larger', 'H ring of three, other', 'I chain 1,2,2 at the end', 'J two knots, the smaller']
extra = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
jobs = [dict({'ration': r, 'treatment': t, 'take': k, 'first': f}, **extra) for k in takes for r in ('ORD', 'CAP-3', 'FLOOR1') for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT') for f in FIRSTS]
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'form.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(int(os.environ.get('PROBE_THREADS', '8'))) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'studies in', round(time.time() - t0, 1), 's')
