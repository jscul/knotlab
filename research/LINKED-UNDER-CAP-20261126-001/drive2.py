"""drive2.py OUT [WORKERS]: drive.py resumed: the blocks of drive.py, each given only the far ends (or receivers) whose
lines are not yet in OUT; appends to OUT.  (drive.py was stopped at 1,938 lines when its shell's time ran out; this
runs the rest as its own unit.)"""
import json, subprocess, sys, os
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
done = set()
for l in open(out):
    try: r = json.loads(l)
    except ValueError: continue
    if 'law' in r: done.add((r['law'], r['A'], r['B']))
names = [l.split()[1] for l in subprocess.run([PY, '-B', os.path.join(HERE, 'linked.py'), 'list'], capture_output=True, text=True).stdout.splitlines()]
jobs = []
for a in (1, 2, 3, 4, 5):
    law, A = 'CAP-%d' % (a + 2), 'tri:%d22@0' % a
    for i in range(646):
        if (law, A, names[i]) not in done: jobs.append(['census', str(a), str(i), str(i + 1)])
SEND = ['g1:3@0', 'g3:22@0', 'g6:122@0', 'g7:122@0', 'stub']
for i in range(646):
    if not all(('CAP-3', names[i], B) in done for B in SEND): jobs.append(['receivers', str(i), str(i + 1)])
print(len(jobs), 'jobs to run', flush=True)
def one(j):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=6G', '-p', 'MemorySwapMax=0', 'timeout', '900',
                        PY, '-B', os.path.join(HERE, 'linked.py')] + j, capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
    if p.returncode: lines.append(json.dumps({'job': j, 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'a') as f:
    for lines in ex.map(one, jobs):
        if lines: f.write('\n'.join(lines) + '\n'); f.flush()
print('done', flush=True)
