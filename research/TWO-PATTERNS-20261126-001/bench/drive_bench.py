"""drive_bench.py OUT [WORKERS]: the bench's first table.  Six pairs of patterns (ring, copier, source, each with
each, a pattern with itself included), joined in two ways (a meeting through a spent knot; a shared distinction) at
one, two and three steps, under 36 laws: the ration (a cap of three, just enough for three places, the ordinary
count), the treatment of a short knot (it waits, it retires, it makes offshoots) and the take (none, or one of the
engine's three takes of a sole candidate, which use no names).  1,296 cases, the 324 with nothing taken first and
with every reading, the 972 with a take without the marks.  Each case is its own run under a memory cap of 8 GB
with no swap and a stop at three minutes; up to 12 rounds, and no further round once a round leaves more than 3,000
knots.  (A first launch with a bound of 8,000 knots was stopped by hand after 123 cases, about a quarter of an
hour in: the cases under the ordinary count cost half a minute each and the whole would have run past two hours.
Its cases are kept as bench_first_launch.jsonl.gz.  A second launch was discarded: it ran while the stub comparison
was being corrected, so its cases were of two versions of this program; it showed that a few cases under the ordinary
count with a shared distinction and waiting take ten minutes at under 3,000 knots, the waiting members piling up,
so the stop was brought down to three minutes.  A case the clock stops is reported as not run.)"""
import json, subprocess, sys, os, time
from concurrent.futures import ThreadPoolExecutor
PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 12
HERE = os.path.dirname(os.path.abspath(__file__))
P = ('ring', 'copier', 'source')
jobs = [{'A': P[i], 'B': P[j], 'steps': s, 'join': jn, 'ration': r, 'treatment': t, 'take': k, 'marks': k is None}
        for k in (None, 'MET-SOLE', 'STEPS1-SOLE', 'STEPS2-SOLE') for jn in ('meeting', 'share')
        for i in range(3) for j in range(i, 3) for s in (1, 2, 3)
        for r in ('CAP-3', 'FLOOR1', 'ORD') for t in ('CANCEL-WAIT', 'CANCEL-RETIRE', 'CANCEL-OFFSHOOT')]
if len(sys.argv) > 3 and sys.argv[3] == 'take-marks':
    # a later pass: the one take that ever took (the take of a sole candidate from a knot the parent meets), with the marks
    jobs = [dict(j, marks=True) for j in jobs if j['take'] == 'MET-SOLE']
def one(j):
    t0 = time.time()
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0',
                        'timeout', '180', PY, '-B', os.path.join(HERE, 'bench.py'), json.dumps(j)], capture_output=True, text=True)
    if p.returncode == 0 and p.stdout.strip():
        return p.stdout.strip().splitlines()[-1]
    return json.dumps({'spec': j, 'not run': 'the clock' if p.returncode == 124 else 'stopped (return code %d)' % p.returncode,
                       'stderr': (p.stderr or '')[-300:], 'seconds': round(time.time() - t0, 1)})
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    for line in ex.map(one, jobs):
        f.write(line + '\n'); f.flush()
print(len(jobs), 'cases done')
