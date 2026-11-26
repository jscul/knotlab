"""drive_ring_line.py OUT [WORKERS]: ring_line.py run for d = 1..8, five laws and two joins (80 runs), each under a
memory cap of 8 GB with no swap and a stop at five minutes."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 10
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [(d, law, join) for join in ('meeting', 'share') for law in ('CAP-3', 'REC-ONE-FEWER', 'ONE-FEWER', 'JOIN-FEWER', 'ORD') for d in range(1, 9)]
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', '300',
                        PY, '-B', os.path.join(HERE, 'ring_line.py'), 'run'] + [str(x) for x in j], capture_output=True, text=True)
    try: return json.dumps(json.loads(p.stdout.strip().splitlines()[-1]))
    except Exception: return json.dumps({'job': list(j), 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode})
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for line in ex.map(one, jobs): f.write(line + '\n'); f.flush()
print(len(jobs), 'runs done')
