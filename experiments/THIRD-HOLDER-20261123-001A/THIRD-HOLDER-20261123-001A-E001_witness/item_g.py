"""Row G (checks of the code, not predictions), one birth per setting.

1. Each of the 18 knots passes the canonical K1-K3 test (tools/knotlab), with every choice of contact place.
2. Full enumeration of each of the four finished structures (26 old and 2 fresh distinctions, 2^28 assignments, every knot
   on every assignment) agrees exactly with the side-table computation (each side enumerated alone, combined over s1 s2),
   and with an exhaustive backtracking search over the whole structure.  The old-word table also agrees with the starter's
   `evaluate` (docs/prompts/missed_leads_checks/finished_weighting_chsh.py).
3. The control weighting (old words equal, divided among extensions) and parity births in place of not-all-equal births
   (even and odd) give a score of at most 2.
Writes artifacts/.../joint_k1_full.json (the four joint tables of complete records) and item_g.json.
"""
import json, time, sys
import numpy as np
from fractions import Fraction
import common as c

t0 = time.time()
out = {}
ok_all = True

# 1. canonical test
S = c.build(1)
knots18 = S['a_knots'] + S['b_knots']
assert len(knots18) == 18
chk = []
for law, mem in knots18:
    r = c.canonical_check(law, mem)
    chk.append(dict(law=law, members=list(mem), every_role_a_knot=all(x['knot'] for x in r), allowed=r[0]['allowed']))
births = [k for s in (0, 1) for k in S['births_A'][s] + S['births_B'][s]]
chk_b = []
for law, mem in births:
    r = c.canonical_check(law, mem)
    chk_b.append(dict(law=law, members=list(mem), every_role_a_knot=all(x['knot'] for x in r)))
g1 = all(x['every_role_a_knot'] for x in chk) and all(x['every_role_a_knot'] for x in chk_b)
print(f'1. canonical test: {sum(x["every_role_a_knot"] for x in chk)}/18 knots pass with every choice of contact; '
      f'births {sum(x["every_role_a_knot"] for x in chk_b)}/{len(chk_b)}:', 'PASS' if g1 else 'FAIL')
for x in chk:
    print(f'   {x["law"]}({",".join(x["members"])}): allowed {x["allowed"]}')
out['canonical'] = dict(knots=chk, births=chk_b, passed=g1)
ok_all &= g1

# holders
h_old = c.holders(knots18)
extra, over = c.extra_holders(knots18)
print(f'   distinctions: {len(c.old_names(S))} old; holders above two: {over}; extra holders {extra}')
out['old_distinctions'] = len(c.old_names(S)); out['extra_holders_old'] = extra; out['held_more_than_twice'] = over

# 2. full enumeration vs side tables vs backtracking
J_full = {}; J_side = {}; J_bt = {}; info = {}
for sa in (0, 1):
    for sb in (0, 1):
        t1 = time.time()
        J, nv, nk = c.full_joint(S, sa, sb)
        tf = time.time() - t1
        TA, TB, Js = c.side_tables(S, sa, sb)
        names, kn = c.finished(S, sa, sb)
        bt, nodes = c.backtrack_counts(names, kn, S['recA'] + S['recB'])
        bt = bt.reshape(J.shape)
        J_full[sa, sb] = J; J_side[sa, sb] = Js; J_bt[sa, sb] = bt
        same = bool(np.array_equal(J, Js)) and bool(np.array_equal(J, bt))
        info[f'{sa}{sb}'] = dict(distinctions=nv, knots=nk, assignments=2 ** nv, allowed=int(J.sum()), full_eq_side=bool(np.array_equal(J, Js)),
                                 full_eq_backtrack=bool(np.array_equal(J, bt)), backtrack_nodes=nodes, seconds_full=round(tf, 1))
        print(f'2. settings ({sa},{sb}): {nv} distinctions, {nk} knots, 2^{nv} assignments; allowed words {int(J.sum())}; '
              f'full = side tables: {np.array_equal(J, Js)}; full = backtracking: {np.array_equal(J, bt)} ({tf:.1f}s)', flush=True)
        ok_all &= same
g2 = all(v['full_eq_side'] and v['full_eq_backtrack'] for v in info.values())
out['enumeration'] = info
c.save_joint(f'{c.ART}/joint_k1_full.json', J_full)

# old table and the starter's evaluate
M = c.old_table(S)
src = open(f'{c.REPO}/docs/prompts/missed_leads_checks/finished_weighting_chsh.py').read().split('# ---- 1.')[0]
ns = {}; exec(src, ns)
s_st, hid_st, tv_st, _ = ns['evaluate'](M)
# old table from the full enumeration of the finished structures: sum over fresh values, divided by the lawful counts
recon_ok = True
for (sa, sb), J in J_full.items():
    Mx = np.zeros((8, 8), dtype=np.int64)
    for rA in range(16):
        for rB in range(16):
            Mx[rA >> 1, rB >> 1] += J[rA, rB]
    W = np.array([[c.lawful_count(1, x, sa) * c.lawful_count(1, y, sb) for y in range(8)] for x in range(8)])
    recon_ok &= bool(np.array_equal(Mx, M * W))
print(f'   old structure: {int(M.sum())} allowed old words (2^26 assignments); finished tables = old table x lawful counts: {recon_ok}')
print(f'   starter evaluate on the old table: score {s_st:.9f}, hidden {hid_st}, largest change {tv_st}')
out['old_words'] = int(M.sum()); out['old_table'] = M.tolist(); out['finished_equals_old_times_lawful'] = recon_ok
out['starter_evaluate'] = dict(score=s_st, hidden=bool(hid_st), change=str(tv_st))
g2 = g2 and recon_ok
print('2. full enumeration = side tables = backtracking:', 'PASS' if g2 else 'FAIL')
ok_all &= g2

# 3. control weighting and parity births
ev = c.evaluate_tables(J_full, 1)
ctrl = c.evaluate_tables(c.control_tables(J_full, 1), 1)
print(f'3. control weighting: score {ctrl["score"]} = {ctrl["score_float"]:.6f}; hidden {ctrl["hidden_alice"]},{ctrl["hidden_bob"]}')
out['control'] = ctrl
par = {}
for law in ('even', 'odd'):
    Sp = c.build(1, birth_law=law)
    Jp = {}
    for sa in (0, 1):
        for sb in (0, 1):
            Jp[sa, sb], _, _ = c.full_joint(Sp, sa, sb)
    e = c.evaluate_tables(Jp, 1)
    par[law] = e
    print(f'   {law} births: score {e["score"]} = {e["score_float"]:.6f}; totals {e["totals"]}; hidden {e["hidden_alice"]},{e["hidden_bob"]}')
out['parity_births'] = par
g3 = Fraction(ctrl['score']) <= 2 and all(Fraction(v['score']) <= 2 for v in par.values())
print('3. control weighting and parity births at most 2:', 'PASS' if g3 else 'FAIL')
ok_all &= g3
out['G'] = dict(canonical=g1, enumeration_agrees=g2, controls_at_most_2=g3, passed=bool(ok_all))
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(f'{c.ART}/item_g.json', 'w'), indent=1)
print('ROW G:', 'PASS' if ok_all else 'FAIL', f'({time.time() - t0:.0f}s)')
sys.exit(0 if ok_all else 1)
