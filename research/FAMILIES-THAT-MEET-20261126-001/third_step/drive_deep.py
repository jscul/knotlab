"""drive_deep.py OUT [WORKERS]: every start of the third step with reach_deep.py: d in 1, 2, 3; m in 1, 2, 3; the
ordinary count and caps of 4, 5, 6, 7, 8, 9, 10 and 12; the three treatments of a short knot.  243 starts, each its
own run under a memory cap of 8 GB with no swap and a stop at ten minutes, up to 14 rounds, and no further round
once a round leaves more than 60,000 knots.  A start the memory cap or the clock stops keeps the rounds it had
printed; its line says how it ended."""
import json, subprocess, sys, os, time
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [{'d': d, 'm': m, 'ration': r, 'treatment': t, 'rounds': 14, 'bound': 60000}
        for d in (1, 2, 3) for r in ['ORD'] + ['CAP-%d' % c for c in (4, 5, 6, 7, 8, 9, 10, 12)]
        for t in ('CANCEL-RETIRE', 'CANCEL-OFFSHOOT', 'CANCEL-WAIT') for m in (1, 2, 3)]
def one(j):
    t0 = time.time()
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0',
                        'timeout', '600', PY, '-B', os.path.join(HERE, 'reach_deep.py'), json.dumps(j)], capture_output=True, text=True)
    rounds = []; stop = None
    for l in p.stdout.splitlines():
        try: x = json.loads(l)
        except ValueError: continue                      # a line cut short when the run was stopped
        if 'stop' in x: stop = x['stop']
        else: rounds.append(x)
    if stop is None: stop = 'the clock' if p.returncode == 124 else 'the memory cap (return code %d)' % p.returncode
    return {'spec': j, 'ended by': stop, 'rounds read': len(rounds), 'seconds': round(time.time() - t0, 1), 'rounds': rounds}
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for r in ex.map(one, jobs):
        f.write(json.dumps(r) + '\n'); f.flush()
print(len(jobs), 'starts done')
