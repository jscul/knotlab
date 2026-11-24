"""Reduction (THIRD-HOLDER-20261123-001B pre-registration, "Reduction"): from a starting structure remove one knot at a time
in a seeded order, dropping distinctions left with no holder, and keep a removal when the structure is still hidden with a
score above 2 (exact).  Passes through the same order are repeated until a whole pass removes nothing, so each final structure
is minimal: no single further removal keeps a hidden excess.  A removal that would leave an observer distinction with no old
holder is not kept (the structure would leave its class; deviations.md, item 6).

usage: reduce.py START SEED0 SEED1        START = eighteen | pencil; seeds SEED0 .. SEED1-1
Evaluation during the reduction uses the side tables (product checked against full enumeration in gates.py); every distinct
final structure is verified by verify_reduced.py with full enumeration of its four finished structures.
"""
import sys, json, time
import numpy as np
from fractions import Fraction
import common as c, structures as st

start = sys.argv[1]; s0 = int(sys.argv[2]); s1 = int(sys.argv[3])
KA0, KB0, cls = st.STARTS[start]
ALL = [('A', k) for k in KA0] + [('B', k) for k in KB0]
n = len(ALL)
t0 = time.time()
side_cache = {}; eval_cache = {}
stats = dict(evaluations=0, side_tables=0, rejected_observer=0)

def side_T(knots, who, shared):
    key = (who, frozenset(knots), shared)
    T = side_cache.get(key)
    if T is None:
        T = c.side_table(list(knots), c.OBS[who], list(shared)); side_cache[key] = T; stats['side_tables'] += 1
    return T

def evaluate(keep):
    """keep: frozenset of indices into ALL.  Returns (ok, info)."""
    if keep in eval_cache: return eval_cache[keep]
    stats['evaluations'] += 1
    kA = [ALL[i][1] for i in sorted(keep) if ALL[i][0] == 'A']; kB = [ALL[i][1] for i in sorted(keep) if ALL[i][0] == 'B']
    hA = c.holders(kA); hB = c.holders(kB)
    obs_ok = all(hA.get(o, 0) >= 1 for o in c.OBS['A']) and all(hB.get(o, 0) >= 1 for o in c.OBS['B'])
    if not obs_ok:
        stats['rejected_observer'] += 1
        r = (False, dict(reason='observer distinction without an old holder')); eval_cache[keep] = r; return r
    shared = tuple(sorted(set(hA) & set(hB)))
    TA = side_T(kA, 'A', shared); TB = side_T(kB, 'B', shared)
    M = TA @ TB.T
    if M.sum() == 0:
        r = (False, dict(reason='no allowed old word')); eval_cache[keep] = r; return r
    hidA, hidB = c.exact_hidden(M)
    if not (hidA and hidB):
        r = (False, dict(reason='not hidden')); eval_cache[keep] = r; return r
    f = float(c.score_batch_c(M[None])[0])
    if f < 2 - 1e-7:
        r = (False, dict(reason='score at most 2', score_float=f)); eval_cache[keep] = r; return r
    v = c.exact_best(M, slack=1e-9)[0]
    r = (v > 2, dict(score=v, shared=shared)); eval_cache[keep] = r
    return r

ok0, info0 = evaluate(frozenset(range(n)))
assert ok0, f'start is not a hidden excess: {info0}'
finals = []
for seed in range(s0, s1):
    order = [int(q) for q in np.random.default_rng(seed).permutation(n)]
    keep = set(range(n)); passes = 0
    while True:
        passes += 1; removed = False
        for q in order:
            if q not in keep: continue
            trial = frozenset(keep - {q})
            ok, info = evaluate(trial)
            if ok:
                keep = set(trial); removed = True
        if not removed: break
    kept = sorted(keep)
    ok, info = evaluate(frozenset(kept))
    kA = [ALL[i][1] for i in kept if ALL[i][0] == 'A']; kB = [ALL[i][1] for i in kept if ALL[i][0] == 'B']
    meas = c.structure_measures(kA, kB)
    finals.append(dict(seed=seed, passes=passes, kept=kept, knots=meas['knots'], extra_holders=meas['extra_holders'],
                       max_holders=meas['max_holders'], cls=meas['cls'], score=str(info['score'])))
    print(f'seed {seed}: passes {passes}, knots {meas["knots"]} ({meas["knots_A"]}+{meas["knots_B"]}), extra holders {meas["extra_holders"]}, '
          f'largest holders {meas["max_holders"]}, class {meas["cls"]}, score {info["score"]}  [{time.time() - t0:.0f}s]', flush=True)
out = dict(start=start, cls=cls, seeds=[s0, s1], start_knots=c.fmt_knots(KA0) + c.fmt_knots(KB0), finals=finals, stats=stats,
           seconds=round(time.time() - t0, 1))
json.dump(out, open(f'{c.ART}/reduce_{start}_{s0}_{s1}.json', 'w'), indent=1)
print(json.dumps(stats), f'{time.time() - t0:.0f}s')
