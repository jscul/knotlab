"""drive.py OUT [WORKERS]: second.py for the switch kind under caps three to seven (and the ordinary count on the
cap-three kind), each far end, under a memory cap of 8 GB with no swap and a stop at fifteen minutes."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [(a, B, 'CAP-%d' % (a + 2)) for a in (1, 2, 3, 4, 5) for B in ('g3:22@0', 'g1:3@0', 'stub')] + [(1, B, 'ORD') for B in ('g3:22@0', 'g1:3@0', 'stub')]
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', '900',
                        PY, '-B', os.path.join(HERE, 'second.py'), 'one', str(j[0]), j[1], j[2]], capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
    if p.returncode: lines.append(json.dumps({'job': list(j), 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs): f.write('\n'.join(lines) + '\n'); f.flush()
print(len(jobs), 'runs done')
