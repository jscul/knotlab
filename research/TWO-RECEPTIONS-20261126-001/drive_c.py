"""drive_b.py OUT [WORKERS]: parity.py run over the 100 sampled receivers, two a job, each under a memory cap of 6 GB
with no swap and a stop at twenty-five minutes."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 10
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [(i, i + 2) for i in range(0, 100, 2)]
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=6G', '-p', 'MemorySwapMax=0', 'timeout', '1500',
                        PY, '-B', os.path.join(HERE, 'parity.py'), 'run', str(j[0]), str(j[1])], capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
    if p.returncode: lines.append(json.dumps({'job': list(j), 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode, 'lines read': len(lines)}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs): f.write('\n'.join(lines) + '\n'); f.flush()
print('done')
