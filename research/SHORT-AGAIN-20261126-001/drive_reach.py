"""drive_reach.py OUT [WORKERS]: every receiver and sender (4 by 4) at every distance 1 to 8, each its own run of 18
laws (reach.py run A B D) under a memory cap of 8 GB with no swap and a stop at five minutes.  128 runs, 2,304
cases.  A run the clock stops keeps the cases it had printed."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 20
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [(a, b, d) for d in range(8, 0, -1) for a in range(4) for b in range(4)]
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', '300',
                        PY, '-B', os.path.join(HERE, 'reach.py'), 'run'] + [str(x) for x in j], capture_output=True, text=True)
    lines = []
    for l in p.stdout.splitlines():
        try: json.loads(l); lines.append(l)
        except ValueError: pass
    if len(lines) < 18:
        lines.append(json.dumps({'job': list(j), 'not run': 18 - len(lines), 'why': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs):
        f.write('\n'.join(lines) + '\n'); f.flush()
print(len(jobs), 'runs done')
