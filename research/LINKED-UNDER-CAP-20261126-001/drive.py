"""drive.py OUT [WORKERS]: linked.py census for each cap's switch kind over the 646 far ends (in blocks of 27), and
linked.py receivers over the 646 receivers (in blocks of 27), each block under a memory cap of 6 GB with no swap and a
stop at twenty minutes."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
blocks = [(i, min(i + 27, 646)) for i in range(0, 646, 27)]
jobs = [['census', str(a), str(i), str(j)] for a in (1, 2, 3, 4, 5) for i, j in blocks] + [['receivers', str(i), str(j)] for i, j in blocks]
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=6G', '-p', 'MemorySwapMax=0', 'timeout', '1200',
                        PY, '-B', os.path.join(HERE, 'linked.py')] + j, capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
    if p.returncode: lines.append(json.dumps({'job': j, 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode, 'lines read': len(lines)}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs): f.write('\n'.join(lines) + '\n'); f.flush()
print(len(jobs), 'blocks done')
