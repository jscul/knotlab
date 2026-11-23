"""Gate row G, part 1 (needs no side tables): the four-type distribution gives 20/9 with hidden settings; the batched
evaluation of common.py agrees with the starter's `evaluate` on random tables (score, hidden flag, largest change);
the control weighting does not exceed 2 on random and on structured tables."""
import itertools, sys, json
import numpy as np
from fractions import Fraction
import common as c

ns = c.load_starter()
evaluate = ns['evaluate']
out = {}
# 1. four-type preparation
M = np.zeros((8, 8), dtype=np.int64)
for x1, x2, x3, y1, y2, y3 in itertools.product((0, 1), repeat=6):
    if x2 != x3 and y2 != y3 and (x1 ^ y1) == ((x1 ^ x3) & (y1 ^ y2)):
        M[x1 * 4 + x2 * 2 + x3, y1 * 4 + y2 * 2 + y3] += 1
s, hid, tv, arg = evaluate(M)
v, combo, pat = c.exact_best(M)
Mf = M[None]
hA, hB = c.hidden_batch(Mf)
score_batch = float(c.score_batch(Mf)[0])
print('four-type M (counts of old words):'); print(M)
print(f'starter evaluate: score {s:.9f}, hidden {hid}, largest change {tv}')
print(f'common batched: score {score_batch:.9f}, hidden (Alice,Bob) {bool(hA[0])},{bool(hB[0])}, tv {c.tv_batch(Mf)[0]}')
print(f'exact best over parity outcomes: {v} = {float(v):.9f}; combo (masks A0,A1,B0,B1) {combo}, pattern {pat}')
g1 = (v == Fraction(20, 9)) and hid and bool(hA[0]) and bool(hB[0]) and abs(s - 20 / 9) < 1e-12 and tv == 0
print('GATE 1 (20/9, hidden):', 'PASS' if g1 else 'FAIL')
ctrl = c.score_batch(Mf, control=True)[0]
vc = c.exact_best(M, control=True)
print(f'control weighting on the four-type M: exact {vc[0]} = {float(vc[0]):.9f}  (float {ctrl:.9f})')
out['four_type'] = dict(score=str(v), hidden=bool(hid), tv=str(tv), control=str(vc[0]), combo=combo, pattern=pat)
# 2. pencil formula check from the starter (rho = 2, 4, 8)
pencil_ok = True
four_types = None
src = open(c.STARTER).read()
i0 = src.index('def four_types'); i1 = src.index('for rho in (2, 4, 8)')
ns2 = {'Fraction': Fraction}; exec(src[i0:i1], ns2)
for rho in (2, 4, 8):
    f = ns2['four_types'](rho)
    exp = 4 - Fraction(8 * rho, (1 + rho) ** 2)
    print(f'  four-type pencil rho={rho}: {f} (formula {exp})', 'ok' if f == exp else 'MISMATCH')
    pencil_ok &= (f == exp)
out['pencil_ok'] = bool(pencil_ok)
# 3. cross-check batched evaluation vs starter on random tables
rng = np.random.default_rng(20261123)
bad = 0; n = 0; maxd = 0.0; hidden_n = 0; ctrl_max = 0.0
Ms = []
for t in range(1500):
    if t % 3 == 0:
        M = rng.integers(0, 4, size=(8, 8))
    elif t % 3 == 1:
        M = (rng.integers(0, 3, size=(8, 4)) @ rng.integers(0, 3, size=(4, 8)))
    else:
        # force hidden: u0 parallel u1 by scaling columns... use rank-2 tables
        M = (rng.integers(0, 3, size=(8, 2)) @ rng.integers(0, 3, size=(2, 8)))
    if M.sum() == 0: continue
    Ms.append(M)
Ms = np.array(Ms)
sc = c.score_batch(Ms); hA, hB = c.hidden_batch(Ms); tvb = c.tv_batch(Ms); scc = c.score_batch(Ms, control=True)
for M, s1, ha, hb, t1, sc_ in zip(Ms, sc, hA, hB, tvb, scc):
    r = evaluate(M)
    if r is None: continue
    n += 1
    s0, h0, t0, _ = r
    d = abs(s0 - s1); maxd = max(maxd, d)
    if d > 1e-9 or bool(ha and hb) != bool(h0) or abs(float(t0) - t1) > 1e-9:
        bad += 1
    hidden_n += bool(h0)
    ctrl_max = max(ctrl_max, sc_)
print(f'cross-check vs starter evaluate on {n} random tables: mismatches {bad}, largest score difference {maxd:.2e}, hidden among them {hidden_n}')
print(f'control weighting: largest score over these {n} tables {ctrl_max:.9f}')
out['crosscheck'] = dict(n=n, mismatches=bad, maxdiff=maxd, hidden=hidden_n, control_max=ctrl_max)
# exact check on a few tables: float vs exact
for M in Ms[:20]:
    v = c.exact_best(M)[0]
    s1 = c.score_batch(M[None])[0]
    assert abs(float(v) - s1) < 1e-9, (v, s1)
for M in Ms[:20]:
    v = c.exact_best(M, control=True)[0]
    s1 = c.score_batch(M[None], control=True)[0]
    assert abs(float(v) - s1) < 1e-9, (v, s1)
print('exact (Fraction) best agrees with float on 20 tables, both weightings')
ok = g1 and pencil_ok and bad == 0 and ctrl_max <= 2 + 1e-9

# 4. C kernel agrees with the numpy batch score (both weightings)
Mr = rng.integers(0, 6, size=(2000, 8, 8))
dk = max(np.abs(c.score_batch(Mr, control=ctl) - c.score_batch_c(Mr, control=ctl)).max() for ctl in (False, True))
print(f'C kernel vs numpy batch score on 2000 random tables, both weightings: largest difference {dk:.2e}')
ok_kernel = dk < 1e-12
# 5. symmetries of the evaluation (32 images: row maps on each side and the exchange of the observers)
import os
sym_bad = 0; sym_n = 0
pool = [Mx for Mx in Ms[:300]]
hf = c.ART + '/pairs_c1_k3_i3_0_495_hidden.npz'
if os.path.exists(hf):
    Hm = np.load(hf)['M'].astype(np.int64)
    pool += [Hm[q] for q in rng.choice(len(Hm), 400, replace=False)]
for Mx in pool:
    ims = np.array(c.sym_images(Mx))
    s_ = c.score_batch_c(ims); sc_ = c.score_batch_c(ims, control=True); ha, hb = c.hidden_batch(ims); h_ = ha & hb; tv_ = c.tv_batch(ims)
    ky, _ = c.canon_keys(ims.reshape(len(ims), 64))
    good = (np.ptp(s_) < 1e-9 and np.ptp(sc_) < 1e-9 and (h_.all() or not h_.any()) and np.ptp(tv_) < 1e-9 and len(set(ky.tolist())) == 1)
    sym_n += 1; sym_bad += (not good)
print(f'symmetry check (32 images each; score, control, hiding, largest change, canonical key): {sym_n} tables, {sym_bad} failures')
ok_sym = sym_bad == 0
out['kernel_ok'] = bool(ok_kernel); out['symmetry'] = dict(tables=sym_n, failures=sym_bad)
ok = ok and ok_kernel and ok_sym
out['pass_part1'] = bool(ok)
print('GATE PART 1:', 'PASS' if ok else 'FAIL')
json.dump(out, open(c.ART + '/gates_a.json', 'w'), indent=1, default=str)
sys.exit(0 if ok else 1)
