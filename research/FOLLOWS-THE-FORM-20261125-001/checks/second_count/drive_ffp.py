import json, subprocess, sys, time, os
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo, plan = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])     # plan: [[family, "ABCDE", rounds, linked, knot_law], ...]
jobs = []
for fam, firsts, rounds, linked, kl in plan:
    for k in (None, 'MET-SOLE'):
        for r in ('FLOOR1', 'CAP-3', 'ORD'):
            for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
                for f in firsts:
                    jobs.append({'ration': r, 'treatment': t, 'take': k, 'first': f, 'family': fam, 'rounds': rounds, 'linked': linked, 'knot_law': kl})
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'ffp.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(int(os.environ.get('PROBE_THREADS', '10'))) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'studies in', round(time.time() - t0, 1), 's')
