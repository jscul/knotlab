# Thread's separate census of one added knot (study C, arm 2) on a sample of starts.
# Own enumeration of each start's allowed words; a not-all-equal knot on T with one fresh distinction counts an old
# word twice when T is not all equal in it and once when it is.  Only evaluate(M) (the recorded scorer) is shared.
# Run from the repository root:
#   .venv/bin/python -B research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/thread_checks/added_knot_sample.py SEED COUNT OUT.json
import gzip, json, glob, collections, itertools, os, sys, random, time
import numpy as np
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reach_enumeration as v
OBS = ('x1', 'x2', 'x3', 'y1', 'y2', 'y3')
W = v.ns['W']
def hidden(M):
    for a in (0, 1):
        g = [W[a] * (M @ W[b]) for b in (0, 1)]
        if any(int(x.sum()) == 0 for x in g): return False
        if not np.array_equal(g[0] * int(g[1].sum()), g[1] * int(g[0].sum())): return False
    for b in (0, 1):
        g = [W[b] * (M.T @ W[a]) for a in (0, 1)]
        if not np.array_equal(g[0] * int(g[1].sum()), g[1] * int(g[0].sum())): return False
    return True
def census(knots):
    names = sorted({m for _, mem in knots for m in mem}); n = len(names); idx = {x: i for i, x in enumerate(names)}
    Wd = np.arange(1 << n, dtype=np.int64); ok = np.ones(1 << n, dtype=bool)
    for law, mem in knots:
        s = sum((Wd >> idx[m]) & 1 for m in mem)
        ok &= ((s > 0) & (s < len(mem))) if law == 'nae' else ((s & 1) == (0 if law == 'even' else 1))
    words = Wd[ok]
    bits = {x: (words >> idx[x]) & 1 for x in names}
    cell = (bits['x1'] * 4 + bits['x2'] * 2 + bits['x3']) * 8 + bits['y1'] * 4 + bits['y2'] * 2 + bits['y3']
    M = np.bincount(cell, minlength=64).reshape(8, 8).astype(np.int64)
    hold = collections.Counter(m for _, mem in knots for m in mem)
    gains = []; sets = 0; hid = 0
    for size in (2, 3, 4):
        for T in itertools.combinations(names, size):
            sets += 1
            s = sum(bits[x] for x in T); eq = (s == 0) | (s == size)
            MT = np.bincount(cell[eq], minlength=64).reshape(8, 8).astype(np.int64)
            M2 = 2 * M - MT
            if not hidden(M2): continue
            hid += 1
            sc = v.evaluate(M2)
            if sc[0] > 2 - 1e-6:
                fr = Fraction(sc[0]).limit_denominator(100000)
                if fr > 2: gains.append((list(T), str(fr), sum(hold[x] >= 2 for x in T), sum(x in OBS for x in T)))
    return M, sets, hid, gains
if __name__ == '__main__':
    seed, count, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    H = [json.loads(l) for f in sorted(glob.glob(v.A + 't1_c3_*.jsonl.gz')) for l in gzip.open(f, 'rt')]
    pop = [h for h in H if v.starts[h['si']]['max_holders'] <= 2 and not h['stage0_excess']]
    rng = random.Random(seed); sample = rng.sample(pop, count) if count < len(pop) else pop
    known = [h for h in pop if 135 <= h['tid'] <= 144 and h['start_support_size'] == h['target_support_size']]
    rows = []; t0 = time.time()
    for h in known + sample:
        tk = [v.parse(k) for k in v.targets[h['tid']]['knots']]
        fk = [tk[i] for i in range(len(tk)) if h['mask'] >> i & 1]
        M, sets, hid, gains = census(fk)
        s0 = v.evaluate(M)
        rows.append(dict(si=h['si'], tid=h['tid'], mask=h['mask'], knots=len(fk), sets=sets, hidden_sets=hid, gains=gains,
                         start_hidden=bool(s0[1]) if s0 else None))
    json.dump(dict(seed=seed, count=count, known=len(known), rows=rows, seconds=round(time.time() - t0, 1)), open(out, 'w'))
    g = [r for r in rows if r['gains']]
    print('starts', len(rows), '(known', len(known), ') sets', sum(r['sets'] for r in rows), 'hidden sets', sum(r['hidden_sets'] for r in rows),
          'starts with a gain', len(g), 'gains', sum(len(r['gains']) for r in rows), 'seconds', round(time.time() - t0, 1))
