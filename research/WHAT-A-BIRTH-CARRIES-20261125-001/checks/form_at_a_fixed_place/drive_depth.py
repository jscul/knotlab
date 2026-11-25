import json, subprocess, sys, time, os
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo = sys.argv[1], sys.argv[2]
takes = json.loads(sys.argv[3]); firsts = json.loads(sys.argv[4]); extra = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
jobs = []
for k in takes:
    for r in ('ORD', 'CAP-3', 'FLOOR1'):
        for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
            for f in firsts:
                j = {'ration': r, 'treatment': t, 'take': k, 'first': f, 'L': 4}; j.update(extra); jobs.append(j)
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'depth.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(int(os.environ.get('PROBE_THREADS', '8'))) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'studies in', round(time.time() - t0, 1), 's')
