"""drive_again.py JAMRUNS OUT [WORKERS]: again.py for every pair and law of the jam study's full pass (three steps by a
meeting, waiting) in which the receiver's own knots hear a change three or more steps away, with the first such change
in jam.py's order as the first change; each under a memory cap of 4 GB with no swap and a stop at five minutes."""
import json, gzip, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; src, out = sys.argv[1], sys.argv[2]; workers = int(sys.argv[3]) if len(sys.argv) > 3 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
names = [l.split()[1] for l in subprocess.run([PY, '-B', os.path.join(HERE, 'jam.py'), 'list'], capture_output=True, text=True).stdout.splitlines()]
idx = {n: i for i, n in enumerate(names)}
jobs = []
for l in (gzip.open(src, 'rt') if src.endswith('.gz') else open(src)):
    r = json.loads(l)
    if 'changes' not in r or r['law'][1] != 'CANCEL-WAIT': continue
    c = next((c for c in r['changes'] if c['heard'] is not None and c['distance'] >= 3), None)
    if c: jobs.append((idx[r['A']], idx[r['B']], r['law'][0], c['at']))
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=4G', '-p', 'MemorySwapMax=0', 'timeout', '300',
                        PY, '-B', os.path.join(HERE, 'again.py'), 'one'] + [str(x) for x in j], capture_output=True, text=True)
    try: return json.dumps(json.loads(p.stdout.strip().splitlines()[-1]))
    except Exception: return json.dumps({'job': list(j), 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode})
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for line in ex.map(one, jobs): f.write(line + '\n'); f.flush()
print(len(jobs), 'runs done')
