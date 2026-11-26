"""drive_reach_second.py OUT: the second pass of the third step.  The first pass (drive_reach.py) lost its studies at
caps of 10 and 12 to the memory cap: a run stops only after the first round that leaves more than its bound of
knots, and one round there can go from under 40,000 knots to several times that.  This pass grows those studies with
one structure in memory (`lean`) and a bound of 15,000 knots, one at a time, each under 8 GB and a stop at ten
minutes."""
import json, subprocess, sys, os
PY = sys.executable; out = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [{'d': d, 'ration': 'CAP-%d' % c, 'treatment': t, 'rounds': 9, 'bound': 15000, 'lean': True}
        for d in (1, 2, 3) for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT') for c in (10, 12)]
with open(out, 'w') as f:
    for j in jobs:
        p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0',
                            'timeout', '600', PY, '-B', os.path.join(HERE, 'reach.py'), json.dumps(j)], capture_output=True, text=True)
        line = p.stdout.strip().splitlines()[-1] if p.returncode == 0 and p.stdout.strip() else json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
        f.write(line + '\n'); f.flush()
print(len(jobs), 'studies done')
