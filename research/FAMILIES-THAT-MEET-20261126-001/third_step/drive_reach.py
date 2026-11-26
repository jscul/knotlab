"""drive_reach.py OUT: every study of the third step, one at a time, each under a memory cap of 8 GB and a stop at
ten minutes.  (One at a time on purpose: the growth engine keeps every round's structure, and a study at the bound
of 40,000 knots holds about 4.5 GB.)"""
import json, subprocess, sys, os
PY = sys.executable; out = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
jobs = []
for d in (1, 2, 3):
    for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT'):
        jobs.append({'d': d, 'ration': 'ORD', 'treatment': t, 'rounds': 7, 'bound': 40000})
        for c in (4, 5, 6, 7, 8, 9, 10, 12):
            jobs.append({'d': d, 'ration': 'CAP-%d' % c, 'treatment': t, 'rounds': 9, 'bound': 40000})
with open(out, 'w') as f:
    for j in jobs:
        p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0',
                            'timeout', '600', PY, '-B', os.path.join(HERE, 'reach.py'), json.dumps(j)], capture_output=True, text=True)
        line = p.stdout.strip().splitlines()[-1] if p.returncode == 0 and p.stdout.strip() else json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
        f.write(line + '\n'); f.flush()
print(len(jobs), 'studies done')
