"""Row G of REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B, parts 1 and 2 (part 3, "support never shrinks along any history", is
checked inside grow_t1.py and t2.py on every history they grow and collected by report.py).

Part 1: each target taken whole gives its recorded score, hidden: its table of old allowed words (computed by contraction,
checked against full enumeration in build_targets.py) is scored by the recorded scorer `evaluate(M)` and by the exact
(Fraction) best score; the exact score must equal the recorded one and both complete records must be hidden.  Where the
census recorded the old table M (of its orbit representative), the table must equal it up to a positive factor and one of
the 32 symmetries of the evaluation.
Part 2: the projected table of a stage agrees with brute-force enumeration on 100 drawn stages: 100 (founder start, grown
stage, law assignment) triples drawn by numpy.random.default_rng(2026112341) among grown stages (t >= 1) of at most 24
distinctions; the stage is written out as knots with laws and every word is enumerated.
Extra checks of the code (not in the frozen row, reported beside it):
  E1 `from_stars_ext` equals the recorded `end_operator.from_stars` on every founder start with at most two holders;
  E2 the contraction with the batch axis equals single contractions on 20 drawn stages and every assignment;
  E3 the evaluator (exact hiding in integers, exact score) equals the recorded `evaluate` (hiding and score) on 2,000
     drawn tables of grown stages.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c  # noqa: E402

t0 = time.time()
ns = c.load_starter()
evaluate = ns['evaluate']
targets = json.loads((c.ART / 'targets.json').read_text())
tk = {t['tid']: t['knots'] for t in c.load_targets()}
starts = [json.loads(l) for l in (c.ART / 'starts.jsonl').open()]
out = {}
ok_all = True
_swap = np.array([((x >> 2) & 1) * 4 + (x & 1) * 2 + ((x >> 1) & 1) for x in range(8)])
_flip = np.array([7 - x for x in range(8)])
ROW_PERMS = [np.arange(8), _swap, _flip, _swap[_flip]]   # COPIED from THIRD-HOLDER-20261123-001B common.py

# ---- part 1 --------------------------------------------------------------------------------------------------------------
p1 = dict(targets=0, score_equal=0, hidden=0, recorded_M_compared=0, recorded_M_equal=0, evaluate_hidden=0,
          evaluate_score_close=0, failures=[])
for t in targets:
    p1['targets'] += 1
    M = np.array(t['table'], dtype=np.int64).reshape(8, 8)
    ex = c.exact_best(M.astype(object))
    hA, hB = c.exact_hidden_obj(M)
    s_float, ns_hidden, tv, _ = evaluate(M)
    rec = Fraction(t['recorded_score'])
    good = (ex == rec) and hA and hB
    p1['score_equal'] += ex == rec
    p1['hidden'] += bool(hA and hB)
    p1['evaluate_hidden'] += bool(ns_hidden)
    p1['evaluate_score_close'] += abs(s_float - float(rec)) < 1e-9
    if t['recorded_M'] is not None:
        p1['recorded_M_compared'] += 1
        R = np.array(t['recorded_M'], dtype=np.int64).reshape(8, 8)
        # the census stored the old table of its orbit representative: compare up to the 32 symmetries of the evaluation
        # (THIRD-HOLDER-20261123-001B deviations item 3; row maps swap x2/x3 and flip all three, likewise for Bob, and
        # Alice/Bob exchange)
        same = any(c.proportional((M if tr == 0 else M.T)[np.ix_(pa, pb)].reshape(64), R.reshape(64))
                   for pa in ROW_PERMS for pb in ROW_PERMS for tr in (0, 1))
        p1['recorded_M_equal'] += same
        good &= same
    if not good or not ns_hidden or abs(s_float - float(rec)) >= 1e-9:
        p1['failures'].append(dict(tid=t['tid'], exact=str(ex), recorded=t['recorded_score'], hidden=[hA, hB],
                                   evaluate=[s_float, ns_hidden]))
p1['ok'] = not p1['failures']
ok_all &= p1['ok']
out['part1_targets_whole'] = p1
print('part 1', {k: v for k, v in p1.items() if k != 'failures'}, len(p1['failures']), flush=True)

# ---- part 2 --------------------------------------------------------------------------------------------------------------
rng = np.random.default_rng(2026112341)
p2 = dict(stages=0, agree=0, failures=[], tried=0, D=[])
order = rng.permutation(len(starts))
for si in order:
    if p2['stages'] >= 100:
        break
    s = starts[int(si)]
    ks = tk[s['tid']]
    stars, laws, names, obs, sub = c.start_stars(ks, s['mask'])
    h = c.grow(stars, 'nae')
    grown = [t for t in range(1, len(h['n_at'])) if h['D_at'][t] <= 24]
    p2['tried'] += 1
    if not grown:
        continue
    t = int(rng.choice(grown))
    n = h['n_at'][t]
    nf = h['n_at'][0]
    a = rng.integers(0, 2, size=n - nf).astype(np.int8)
    T = c.stage_tables(h['stars'], laws, nf, n, a[None, :], obs)[0]
    full_laws = list(laws) + [('even', 'nae')[int(v)] for v in a]
    Tb = c.brute_table(h['stars'][:n], full_laws[:n], obs)
    p2['stages'] += 1
    p2['D'].append(h['D_at'][t])
    if np.array_equal(np.array([int(v) for v in T]), Tb):
        p2['agree'] += 1
    else:
        p2['failures'].append(dict(si=int(si), t=t, laws=full_laws))
p2['ok'] = p2['stages'] == 100 and p2['agree'] == 100
p2['D'] = dict(min=min(p2['D']), max=max(p2['D']), mean=float(np.mean(p2['D'])))
ok_all &= p2['ok']
out['part2_brute_force'] = p2
print('part 2', {k: v for k, v in p2.items() if k != 'failures'}, flush=True)

# ---- E1: from_stars_ext against the recorded from_stars -------------------------------------------------------------------
e1 = dict(compared=0, equal=0)
for s in starts:
    if s['max_holders'] > 2:
        continue
    stars, laws, names, obs, sub = c.start_stars(tk[s['tid']], s['mask'])
    a = c.from_stars_ext(stars)
    b = c.EO.from_stars(stars)
    e1['compared'] += 1
    e1['equal'] += (a.opens == b.opens and a.blocks == b.blocks)
e1['ok'] = e1['compared'] == e1['equal']
ok_all &= e1['ok']
out['E1_from_stars'] = e1
print('E1', e1, flush=True)

# ---- E2: batched contraction against single contractions -----------------------------------------------------------------
e2 = dict(stages=0, assignments=0, equal=0)
for si in rng.permutation(len(starts)):
    if e2['stages'] >= 20:
        break
    s = starts[int(si)]
    stars, laws, names, obs, sub = c.start_stars(tk[s['tid']], s['mask'])
    h = c.grow(stars, 'nae')
    if len(h['n_at']) < 2:
        continue
    t = len(h['n_at']) - 1
    n, nf = h['n_at'][t], h['n_at'][0]
    A, _ = c.assignments(n - nf, (s['tid'], s['mask']))
    A = A[:64]
    T = c.stage_tables(h['stars'], laws, nf, n, A, obs)
    e2['stages'] += 1
    for i in range(len(A)):
        fs = c.founder_factors(h['stars'], laws, nf) + [(h['stars'][k], c.lt(('even', 'nae')[int(A[i, k - nf])], len(h['stars'][k])))
                                                       for k in range(nf, n)]
        U = c.contract(fs, obs).reshape(64)
        e2['assignments'] += 1
        e2['equal'] += np.array_equal(np.array([int(v) for v in T[i]]), np.array([int(v) for v in U]))
e2['ok'] = e2['assignments'] == e2['equal']
ok_all &= e2['ok']
out['E2_batch'] = e2
print('E2', e2, flush=True)

# ---- E3: evaluator against the recorded evaluate ------------------------------------------------------------------------
e3 = dict(tables=0, hidden_equal=0, score_close=0, hidden=0)
ev = c.Evaluator()
pool = []
for si in rng.permutation(len(starts)):
    if len(pool) >= 2000:
        break
    s = starts[int(si)]
    stars, laws, names, obs, sub = c.start_stars(tk[s['tid']], s['mask'])
    h = c.grow(stars, 'nae')
    if len(h['n_at']) < 2:
        continue
    t = len(h['n_at']) - 1
    n, nf = h['n_at'][t], h['n_at'][0]
    A, _ = c.assignments(n - nf, (s['tid'], s['mask']))
    A = A[rng.permutation(len(A))[:8]]
    for row in c.stage_tables(h['stars'], laws, nf, n, A, obs):
        pool.append(c.normalize(row))
for T in pool:
    M = np.array([int(v) for v in T], dtype=np.int64).reshape(8, 8)
    r = evaluate(M)
    if r is None:
        continue
    e = ev.run([T])[0]
    e3['tables'] += 1
    hid = e[0] and e[1]
    e3['hidden'] += hid
    e3['hidden_equal'] += hid == bool(r[1])
    if hid:
        e3['score_close'] += abs(e[2] - r[0]) < 1e-9
    else:
        e3['score_close'] += 1
e3['ok'] = e3['tables'] == e3['hidden_equal'] == e3['score_close']
ok_all &= e3['ok']
out['E3_evaluator'] = e3
print('E3', e3, flush=True)

out['all_ok'] = bool(ok_all)
out['seconds'] = round(time.time() - t0, 1)
(c.ART / 'gates.json').write_text(json.dumps(out, indent=1, default=str))
print('ALL OK' if ok_all else 'GATE FAILURE', out['seconds'])
