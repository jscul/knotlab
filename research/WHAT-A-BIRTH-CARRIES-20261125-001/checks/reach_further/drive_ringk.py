"""Rings with unequal knots, for the one fruitful rule.  Written BEFORE its first run, after the ring starts gave the
only links wholly the growth's and the course there told only how many.  Every ring of five knots with 2 to 5 loose
distinctions a knot, of six knots with 2 to 4, and of seven knots with 2 or 3, one for each class under turning the
ring and reversing it; under the two laws that respond (the cap of three and 'just enough for three places', with
offshoots).  Asked: is there a test with no start knot on a linking distinction in which the course differs with
which second part is barred?  Expected: yes, where the first part's two sides are not alike."""
import json, subprocess, sys, time, os, itertools
from multiprocessing.pool import ThreadPool
PY = sys.executable
out, tmo = sys.argv[1], sys.argv[2]
def classes(n, vals):
    seen = set(); res = []
    for ks in itertools.product(vals, repeat=n):
        forms = []
        for r in range(n):
            a = ks[r:] + ks[:r]; forms += [a, a[::-1]]
        c = min(forms)
        if c not in seen: seen.add(c); res.append(c)
    return res
starts = ['ringk:' + ','.join(map(str, c)) for n, vals in ((5, (2, 3, 4, 5)), (6, (2, 3, 4)), (7, (2, 3))) for c in classes(n, vals)]
jobs = [{'start': s, 'ration': r, 'treatment': 'CANCEL-OFFSHOOT', 'take': 'MET2-MANY', 'knot_law': 'nae', 'max_tests': 10 ** 6} for s in starts for r in ('CAP-3', 'FLOOR1')]
def run(j):
    p = subprocess.run(['timeout', tmo, PY, '-B', 'links.py', json.dumps(j)], capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        return json.dumps({'spec': j, 'error': (p.stderr or '')[-300:], 'returncode': p.returncode})
    return p.stdout.strip().splitlines()[-1]
t0 = time.time()
with ThreadPool(int(os.environ.get('PROBE_THREADS', '8'))) as pool, open(out, 'w') as f:
    for line in pool.imap(run, jobs):
        f.write(line + '\n'); f.flush()
print(len(starts), 'starts,', len(jobs), 'runs in', round(time.time() - t0, 1), 's')
