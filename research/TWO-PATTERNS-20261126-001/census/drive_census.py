"""drive_census.py OUT [WORKERS] [DONE]: every pair of sited starts (census.py), 990 pairs of 44, each pair its own
run of 18 cases under a memory cap of 8 GB with no swap and a stop at 150 seconds.  A pair the clock or the cap
stops keeps the cases it had printed; its missing cases are counted as not run.  DONE is an earlier output: pairs
with all 18 cases there are not run again.  (The first launch, with a stop at ten minutes and the cases in their
plain order, was stopped by hand after 389 pairs: under the ordinary count with a shared distinction and waiting
some cases take minutes at a few hundred knots, and a pair stuck there lost the eight cases after it.  That case
now comes last in a pair.)"""
import json, subprocess, sys, os, time
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 20
HERE = os.path.dirname(os.path.abspath(__file__))
N = 44
jobs = [(i, j) for i in range(N) for j in range(i, N)]
if len(sys.argv) > 3:
    have = {}
    for l in open(sys.argv[3]):
        if l.strip():
            r = json.loads(l)
            if 'reads' in r: have[(r['i'], r['j'])] = have.get((r['i'], r['j']), 0) + 1
    jobs = [ij for ij in jobs if have.get(ij, 0) < 18]
def one(ij):
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', '150',
                        PY, '-B', os.path.join(HERE, 'census.py'), 'pair', str(ij[0]), str(ij[1])], capture_output=True, text=True)
    lines = []
    for l in p.stdout.splitlines():
        try: json.loads(l); lines.append(l)
        except ValueError: pass
    if len(lines) < 18:
        lines.append(json.dumps({'i': ij[0], 'j': ij[1], 'not run': 18 - len(lines), 'why': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode}))
    return lines
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for lines in ex.map(one, jobs):
        f.write('\n'.join(lines) + '\n'); f.flush()
print(len(jobs), 'pairs done')
