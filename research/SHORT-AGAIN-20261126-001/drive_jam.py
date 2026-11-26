"""drive_jam.py OUT D JOIN all|sample [WORKERS]: jam.py pair for every ordered pair (47 receivers, 48 senders with the
stub: 2,256 runs of seven laws) or for the seeded sample of 400, at distance D, each under a memory cap of 4 GB with
no swap and a stop at five minutes.  A run the clock stops keeps the cases it had printed."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; D = sys.argv[2]; JOIN = sys.argv[3]; workers = int(sys.argv[5]) if len(sys.argv) > 5 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if sys.argv[4] == 'all': jobs = [(i, j) for i in range(47) for j in range(48)]
else:
    import random
    pairs = [(i, j) for i in range(47) for j in range(48)]; jobs = sorted(random.Random(20261126).sample(pairs, 400))
def one(job):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=4G', '-p', 'MemorySwapMax=0', 'timeout', '300',
                        PY, '-B', os.path.join(HERE, 'jam.py'), 'pair', str(job[0]), str(job[1]), D, JOIN], capture_output=True, text=True)
    lines = []
    for l in p.stdout.splitlines():
        try: json.loads(l); lines.append(l)
        except ValueError: pass
    if len(lines) < 7:
        lines.append(json.dumps({'job': list(job), 'd': int(D), 'join': JOIN, 'not run': 7 - len(lines), 'why': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs):
        f.write('\n'.join(lines) + '\n'); f.flush()
print(len(jobs), 'runs done')
