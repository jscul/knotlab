"""drive_switch.py OUT [WORKERS]: switch.py for every swap (distance 2 to 6, two joins, cap of three or four, three
treatments, two sites: 120 runs of 48 senders), each under a memory cap of 8 GB with no swap and a stop at ten minutes."""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [(d, join, law, tr, site) for law in ('CAP-3', 'CAP-4') for tr in ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT')
        for join in ('meeting', 'share') for site in (0, 1) for d in range(2, 7)]
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', '600',
                        PY, '-B', os.path.join(HERE, 'switch.py'), 'one'] + [str(x) for x in j], capture_output=True, text=True)
    lines = []
    for l in p.stdout.splitlines():
        try: json.loads(l); lines.append(l)
        except ValueError: pass
    if len(lines) < 48:
        lines.append(json.dumps({'job': list(j), 'not run': 48 - len(lines), 'why': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs):
        f.write('\n'.join(lines) + '\n'); f.flush()
print(len(jobs), 'runs done')
