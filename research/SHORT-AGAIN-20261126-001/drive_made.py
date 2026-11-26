"""drive_made.py bench|census OUT [WORKERS]: the bench's 6 pairs, 3 distances and 2 joins under the five made rations
and the three treatments, with the marks (540 cases, a stop at three minutes each); or the census's 990 pairs under
ODD-FEWER and BUSY-FEWER (12 cases a pair, a stop at 150 seconds a pair).  Each run under a memory cap of 8 GB."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; mode, out = sys.argv[1], sys.argv[2]; workers = int(sys.argv[3]) if len(sys.argv) > 3 else 16
HERE = os.path.dirname(os.path.abspath(__file__))
P = ('ring', 'copier', 'source')
def run(args, clock, want):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', str(clock),
                        PY, '-B', os.path.join(HERE, 'made.py')] + args, capture_output=True, text=True)
    lines = []
    for l in p.stdout.splitlines():
        try: json.loads(l); lines.append(l)
        except ValueError: pass
    if len(lines) < want: lines.append(json.dumps({'args': args, 'not run': want - len(lines), 'why': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
if mode == 'bench':
    jobs = [(['bench', json.dumps({'A': P[i], 'B': P[j], 'steps': s, 'join': jn, 'ration': r, 'treatment': t})], 180, 1)
            for r in ('ODD-FEWER', 'BUSY-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'THIRD-FEWER') for jn in ('meeting', 'share')
            for i in range(3) for j in range(i, 3) for s in (1, 2, 3) for t in ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT')]
else:
    jobs = [(['pair', str(i), str(j)], 150, 12) for i in range(44) for j in range(i, 44)]
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(lambda j: run(*j), jobs):
        f.write('\n'.join(lines) + '\n'); f.flush()
print(len(jobs), 'runs done')
