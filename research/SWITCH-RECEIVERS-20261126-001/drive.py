"""drive.py OUT [WORKERS]: receivers.py all for each of the 646 receivers (20 lines each: five laws, d = 2 to 5), each
under a memory cap of 4 GB with no swap and a stop at five minutes."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
def one(i):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=4G', '-p', 'MemorySwapMax=0', 'timeout', '300',
                        PY, '-B', os.path.join(HERE, 'receivers.py'), 'all', str(i)], capture_output=True, text=True)
    lines = []
    for l in p.stdout.splitlines():
        try: json.loads(l); lines.append(l)
        except ValueError: pass
    if len(lines) < 20:
        lines.append(json.dumps({'receiver': i, 'not run': 20 - len(lines), 'why': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, range(646)):
        f.write('\n'.join(lines) + '\n'); f.flush()
print('646 receivers done')
