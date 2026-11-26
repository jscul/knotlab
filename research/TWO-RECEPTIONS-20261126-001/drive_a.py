"""drive_a.py OUT: two.py run for the 28 pairs under the caps of three and four, two pairs a job, under a memory cap of
8 GB with no swap and a stop at fifteen minutes."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [(law, i, i + 2) for law in ('CAP-3', 'CAP-4') for i in range(0, 28, 2)]
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', '900',
                        PY, '-B', os.path.join(HERE, 'two.py'), 'run', j[0], str(j[1]), str(j[2])], capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
    if p.returncode: lines.append(json.dumps({'job': list(j), 'not run': p.returncode}))
    return lines
with ThreadPoolExecutor(14) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs): f.write('\n'.join(lines) + '\n'); f.flush()
