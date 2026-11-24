"""P4: the ceiling.  For weight ratio rho = 2, 4, 8 (k = 1, 2, 3 births per setting): the largest score, under exact hiding
of both complete records, over all distributions q on the six old values (x1 x2 x3 y1 y2 y3) and all parity outcomes of the
record (three old values and k fresh ones), with no structure.

Model.  At settings (a, b) the old word (x, y) has weight q(x, y) w_a(x) w_b(y), w_a(x) = rho if x1 != x_{2+a} else 1 (the
number of lawful fresh completions of k not-all-equal births), each lawful completion equally; normalised per setting pair.
Hiding of Alice's complete record <=> q w_0 and q w_1 (vectors over x) are proportional, with ratio c = Z_00 / Z_01; Bob's
likewise with c' = Z_00 / Z_10.  With the ratios of the totals (c, c') held as parameters, hiding is linear and the score
with fixed outcomes is linear in q (totals 1, 1/c, 1/c', 1/(c c')): a linear program.

usage:
  item_p4.py seeded RHO START END   seeded optimisation, starts START..END-1: random (c, c') and outcome choice; alternate
                                    linear program in q and re-choice of outcomes; polish (c, c') by Nelder-Mead; writes
                                    p4_seeded_rho{RHO}_{START}_{END}.json
  item_p4.py relax                  the relaxation used in the proof (classes = weight type x outcome pair, any +-1 outcomes):
                                    linear program on a grid of (c, c'), compared with 2 + 2 T(c) T(c')
  item_p4.py exact                  exact re-verification of the best seeded distribution at each ratio and of the family
  item_p4.py summary
"""
import sys, json, glob, time, math
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog, minimize
import common as c

X1 = np.array([(x >> 2) & 1 for x in range(8)]); X2 = np.array([(x >> 1) & 1 for x in range(8)]); X3 = np.array([x & 1 for x in range(8)])


def setup(rho):
    k = int(round(np.log2(rho))); assert 2 ** k == rho
    L = 3 + k
    w = np.array([np.where(X1 != X2, rho, 1), np.where(X1 != X3, rho, 1)], dtype=np.float64)      # w[a][x]
    A = np.zeros((2, (1 << L) - 1, 8))                                                             # conditional means of parity outcomes
    for a in (0, 1):
        for x in range(8):
            xa = X2[x] if a == 0 else X3[x]
            zs = [z for z in range(1 << k) if X1[x] != xa or z == ((1 << k) - 1 if X1[x] == 0 else 0)]
            # equal inputs: every fresh value is 1 - x1
            for m in range(1, 1 << L):
                A[a, m - 1, x] = np.mean([(-1) ** bin(m & ((x << k) | z)).count('1') for z in zs])
    return dict(rho=rho, k=k, L=L, w=w, A=A, Aw=[A[a] * w[a][None, :] for a in (0, 1)])


def best_choice(P, q):
    """best |CHSH| over parity outcome choices at q, with the actual totals; returns (value, choice)."""
    Z = {(a, b): float(P['w'][a] @ q @ P['w'][b]) for a in (0, 1) for b in (0, 1)}
    E = {(a, b): (P['Aw'][a] @ q @ P['Aw'][b].T) / Z[a, b] for a in (0, 1) for b in (0, 1)}
    best = (-1.0, None)
    for p in range(4):
        s = [1.0] * 4; s[p] = -1.0
        u = s[0] * E[0, 0][:, None, :] + s[2] * E[1, 0][None, :, :]
        v = s[1] * E[0, 1][:, None, :] + s[3] * E[1, 1][None, :, :]
        for sg in (1.0, -1.0):
            tot = (sg * u).max(-1) + (sg * v).max(-1)
            i0, i1 = np.unravel_index(int(tot.argmax()), tot.shape)
            if tot[i0, i1] > best[0]:
                best = (float(tot[i0, i1]), (int(i0), int(i1), int((sg * u)[i0, i1].argmax()), int((sg * v)[i0, i1].argmax()), p, sg))
    return best


def constraints(P, cc, cp):
    w = P['w']
    rows = []
    for x in range(8):
        r = np.zeros((8, 8)); r[x, :] = w[0] - cc * w[1]; rows.append(r.ravel())
    for y in range(8):
        r = np.zeros((8, 8)); r[:, y] = w[0] - cp * w[1]; rows.append(r.ravel())
    rows.append(np.outer(w[0], w[0]).ravel())
    return np.array(rows), np.array([0.0] * 16 + [1.0])


def lp(P, cc, cp, choice):
    kA0, kA1, kB0, kB1, p, sg = choice
    s = [1.0] * 4; s[p] = -1.0
    Zf = {(0, 0): 1.0, (0, 1): 1 / cc, (1, 0): 1 / cp, (1, 1): 1 / (cc * cp)}
    kA = (kA0, kA1); kB = (kB0, kB1)
    C = np.zeros((8, 8))
    for i, (a, b) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        C += s[i] * np.outer(P['Aw'][a][kA[a]], P['Aw'][b][kB[b]]) / Zf[a, b]
    Aeq, beq = constraints(P, cc, cp)
    res = linprog(-sg * C.ravel(), A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
    if res.status != 0:
        return None, None
    return -res.fun, res.x.reshape(8, 8)


def hidden_float(P, q, tol=1e-7):
    w = P['w']
    m0, m1 = q @ w[0], q @ w[1]; n0, n1 = w[0] @ q, w[1] @ q
    def par(u, v):
        return np.abs(u / u.sum() - v / v.sum()).max() < tol
    return par(m0, m1) and par(n0, n1)


def run_start(P, seed):
    rng = np.random.default_rng(seed)
    lr = np.log(P['rho'])
    lc, lcp = rng.uniform(-lr, lr, size=2)
    n = (1 << P['L']) - 1
    choice = (int(rng.integers(n)), int(rng.integers(n)), int(rng.integers(n)), int(rng.integers(n)), int(rng.integers(4)), float(rng.choice([-1.0, 1.0])))
    val = -np.inf; q = None
    for it in range(12):
        v, qq = lp(P, np.exp(lc), np.exp(lcp), choice)
        if v is None: return None
        bv, bc = best_choice(P, qq)
        q = qq; val = bv
        if bc == choice or bv <= v + 1e-12:
            break
        choice = bc
    for rnd in range(2):
        def f(t):
            t = np.clip(t, -lr + 1e-9, lr - 1e-9)
            v, _ = lp(P, np.exp(t[0]), np.exp(t[1]), choice)
            return -v if v is not None else 10.0
        r = minimize(f, np.array([lc, lcp]), method='Nelder-Mead', options=dict(maxfev=40, xatol=1e-7, fatol=1e-12))
        t = np.clip(r.x, -lr + 1e-9, lr - 1e-9)
        v, qq = lp(P, np.exp(t[0]), np.exp(t[1]), choice)
        if v is None: break
        bv, bc = best_choice(P, qq)
        if bv > val + 1e-13:
            val, q, lc, lcp = bv, qq, t[0], t[1]
        if bc == choice: break
        choice = bc
    v_final, ch_final = best_choice(P, q)
    return dict(seed=seed, value=float(v_final), c=float(np.exp(lc)), cp=float(np.exp(lcp)), choice=[int(v) for v in ch_final[:5]] + [float(ch_final[5])], hidden=bool(hidden_float(P, q)), q=q.tolist())


def T(rho, cc):
    return (rho - cc) * (rho * cc - 1) / (cc * (rho ** 2 - 1))


def family_q():
    M = np.zeros((8, 8), dtype=np.int64)
    for x in range(8):
        for y in range(8):
            x1, x2, x3 = X1[x], X2[x], X3[x]; y1, y2, y3 = X1[y], X2[y], X3[y]
            if x2 != x3 and y2 != y3 and (x1 ^ y1) == ((x1 ^ x3) & (y1 ^ y2)): M[x, y] = 1
    return M


def joint_from_q(Q, k):
    """integer joint record tables J_ab[(x, z), (y, w)] = Q[x, y] when z (w) is lawful for setting a (b); Q integer 8 x 8."""
    L = 3 + k; J = {}
    lawA = {}
    for a in (0, 1):
        f = np.zeros((8, 1 << L), dtype=np.int64)
        for x in range(8):
            xa = X2[x] if a == 0 else X3[x]
            for z in range(1 << k):
                zb = [(z >> (k - 1 - i)) & 1 for i in range(k)]
                if all(c.LAW_FN['nae']([X1[x], xa, zi]) for zi in zb): f[x, (x << k) | z] = 1
        lawA[a] = f
    for a in (0, 1):
        for b in (0, 1):
            J[a, b] = lawA[a].T @ Q @ lawA[b]
    return J


mode = sys.argv[1]
if mode == 'seeded':
    rho, s0, s1 = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    P = setup(rho)
    t0 = time.time(); rows = []; best = None
    for seed in range(s0, s1):
        r = run_start(P, 1_000_000 * rho + seed)
        if r is None: rows.append(dict(seed=seed, value=None)); continue
        bound = 2 + 2 * T(rho, r['c']) * T(rho, r['cp'])
        rows.append(dict(seed=seed, value=r['value'], c=r['c'], cp=r['cp'], hidden=r['hidden'], bound_2_2TT=bound))
        if r['hidden'] and (best is None or r['value'] > best['value']): best = r
        if (seed - s0 + 1) % 250 == 0:
            print(f'rho {rho}: {seed - s0 + 1} starts, {time.time() - t0:.0f}s, best {best["value"] if best else None}', flush=True)
    json.dump(dict(rho=rho, starts=[s0, s1], rows=rows, best=best, seconds=round(time.time() - t0, 1)),
              open(f'{c.ART}/p4_seeded_rho{rho}_{s0}_{s1}.json', 'w'))
    vals = [r['value'] for r in rows if r.get('value') is not None and r.get('hidden')]
    print(f'rho {rho}: starts {s0}..{s1 - 1}: {len(vals)} hidden results; best {max(vals):.12f}; family {4 * (1 + rho ** 2) / (1 + rho) ** 2:.12f}; '
          f'above 2+2T(c)T(c\') by more than 1e-9: {sum(1 for r in rows if r.get("value") is not None and r["value"] > r["bound_2_2TT"] + 1e-9)}; {time.time() - t0:.0f}s')

elif mode == 'relax':
    out = {}
    for rho in (2, 4, 8):
        cls = [(f0, f1, a0, a1) for f0, f1 in ((1, 1), (rho, 1), (1, rho), (rho, rho)) for a0 in (1, -1) for a1 in (1, -1)]
        CA = np.array(cls, dtype=float)
        grid = np.exp(np.linspace(-np.log(rho), np.log(rho), 41))[1:-1]
        maxdev = 0.0; best = (0, None); n = 0
        for cc in grid:
            for cp in grid:
                F0 = CA[:, 0]; F1 = CA[:, 1] * cp; G0 = CA[:, 0]; G1 = CA[:, 1] * cc
                A0, A1 = CA[:, 2], CA[:, 3]
                obj = (np.outer(F0 * A0, G0 * A0) + np.outer(F0 * A0, G1 * A1) + np.outer(F1 * A1, G0 * A0) - np.outer(F1 * A1, G1 * A1)).ravel()
                rows = []
                for i in range(16):
                    r = np.zeros((16, 16)); r[i, :] = G0 - G1; rows.append(r.ravel())
                for j in range(16):
                    r = np.zeros((16, 16)); r[:, j] = F0 - F1; rows.append(r.ravel())
                rows.append(np.outer(F0, G0).ravel())
                res = linprog(-obj, A_eq=np.array(rows), b_eq=np.array([0.0] * 32 + [1.0]), bounds=(0, None), method='highs')
                v = -res.fun; n += 1
                maxdev = max(maxdev, abs(v - (2 + 2 * T(rho, cc) * T(rho, cp))))
                if v > best[0]: best = (v, (float(cc), float(cp)))
        out[rho] = dict(grid_points=n, max_abs_deviation_from_2_2TT=maxdev, best=best[0], at=best[1],
                        family=4 * (1 + rho ** 2) / (1 + rho) ** 2)
        print(f'rho {rho}: relaxation LP on {n} grid points of (c, c\'): largest |V - (2 + 2T(c)T(c\'))| = {maxdev:.2e}; '
              f'grid maximum {best[0]:.12f} at {best[1]}; family {out[rho]["family"]:.12f}', flush=True)
    json.dump(out, open(f'{c.ART}/p4_relax.json', 'w'), indent=1)

elif mode == 'exact':
    import sympy as sp
    out = {}
    for rho in (2, 4, 8):
        P = setup(rho); k = P['k']
        fam = c.evaluate_tables(joint_from_q(family_q(), k), k)
        print(f'rho {rho}: family distribution (the four-type table: 8 old words, equal weights): score {fam["score"]}, hidden {fam["hidden_alice"]},{fam["hidden_bob"]}')
        bests = [json.load(open(f))['best'] for f in sorted(glob.glob(f'{c.ART}/p4_seeded_rho{rho}_*.json'))]
        bests = [b for b in bests if b is not None]
        b = max(bests, key=lambda r: r['value'])
        cc = Fraction(b['c']).limit_denominator(50); cp = Fraction(b['cp']).limit_denominator(50)
        v, q = lp(P, float(cc), float(cp), tuple(b['choice'][:5]) + (float(b['choice'][5]),))
        supp = [i for i in range(64) if q.ravel()[i] > 1e-10]
        # exact constraint matrix at the rational ratios
        w = [[int(v_) for v_ in P['w'][a]] for a in (0, 1)]
        rows = []
        for x in range(8):
            rows.append([(Fraction(w[0][j % 8]) - cc * w[1][j % 8]) if j // 8 == x else 0 for j in range(64)])
        for y in range(8):
            rows.append([(Fraction(w[0][j // 8]) - cp * w[1][j // 8]) if j % 8 == y else 0 for j in range(64)])
        rows.append([Fraction(w[0][j // 8] * w[0][j % 8]) for j in range(64)])
        Mx = sp.Matrix([[sp.Rational(r[j].numerator, r[j].denominator) if isinstance(r[j], Fraction) else sp.Integer(r[j]) for j in supp] for r in rows])
        rhs = sp.Matrix([0] * 16 + [1])
        sol, params = Mx.gauss_jordan_solve(rhs)
        free = sorted(sol.free_symbols, key=lambda s_: s_.name)
        # free parameters: set to the rationalised float values of the corresponding entries
        sol_f = sol
        if free:
            # identify each free parameter with a column of supp by solving at the float point
            idx_free = [i for i in range(len(supp)) if sol[i] in free]
            vals = {sol[i]: sp.Rational(str(Fraction(q.ravel()[supp[i]]).limit_denominator(10 ** 6))) for i in idx_free}
            sol_f = sol.subs(vals)
        qex = [Fraction(0)] * 64
        for i, j in enumerate(supp):
            r_ = sp.Rational(sol_f[i]); qex[j] = Fraction(int(r_.p), int(r_.q))
        nonneg = all(v_ >= 0 for v_ in qex)
        den = 1
        for v_ in qex: den = den * v_.denominator // math.gcd(den, v_.denominator)
        Q = np.array([int(v_ * den) for v_ in qex], dtype=object).reshape(8, 8)
        Qi = np.array(Q.tolist(), dtype=np.int64) if max(abs(int(v_)) for v_ in Q.ravel()) < 2 ** 40 else None
        ev = c.evaluate_tables(joint_from_q(Qi, k), k) if Qi is not None else None
        out[rho] = dict(family=fam, best_seeded_float=b['value'], best_seeded_c=b['c'], best_seeded_cp=b['cp'], rational_c=str(cc), rational_cp=str(cp),
                        support=len(supp), free_parameters=len(free), exact_nonnegative=nonneg, exact_q_integer_scaled=Q.tolist(),
                        exact_evaluation=ev)
        print(f'   best seeded: {b["value"]:.12f} at c={b["c"]:.9f}, c\'={b["cp"]:.9f}; rationalised ratios {cc}, {cp}; support {len(supp)}, '
              f'free parameters {len(free)}; exact q non-negative {nonneg}; exact: {None if ev is None else (ev["score"], ev["hidden_alice"], ev["hidden_bob"], ev["totals"])}')
        print('   exact distribution (integer weights q(x, y), rows x = x1x2x3, columns y = y1y2y3):')
        print(np.array(Q.tolist()))
    json.dump({str(k_): v_ for k_, v_ in out.items()}, open(f'{c.ART}/p4_exact.json', 'w'), indent=1, default=str)

elif mode == 'summary':
    out = {}
    for rho in (2, 4, 8):
        rows = []; secs = 0
        for f in sorted(glob.glob(f'{c.ART}/p4_seeded_rho{rho}_*.json')):
            d = json.load(open(f)); rows += d['rows']; secs += d['seconds']
        vals = [r['value'] for r in rows if r.get('value') is not None and r.get('hidden')]
        fam = 4 * (1 + rho ** 2) / (1 + rho) ** 2
        above = sum(1 for r in rows if r.get('value') is not None and r['value'] > r['bound_2_2TT'] + 1e-9)
        above7 = sum(1 for r in rows if r.get('value') is not None and r['value'] > r['bound_2_2TT'] + 1e-7)
        exc = max((r['value'] - r['bound_2_2TT'], r['value'], r['c'], r['cp']) for r in rows if r.get('value') is not None)
        out[rho] = dict(starts=len(rows), hidden_results=len(vals), best=max(vals), family=fam, family_exact=str(Fraction(4 * (1 + rho ** 2), (1 + rho) ** 2)),
                        within_1e6_of_family=sum(1 for v in vals if abs(v - fam) < 1e-6), above_family_1e9=sum(1 for v in vals if v > fam + 1e-9),
                        above_2_2TT_1e9=above, above_2_2TT_1e7=above7, largest_excess_over_2_2TT=exc, at_2_within_1e6=sum(1 for v in vals if abs(v - 2) < 1e-6),
                        seconds=secs)
        print(f'rho {rho}: {len(rows)} starts, {len(vals)} hidden results; best {max(vals):.12f}; family {fam:.12f}; '
              f'starts within 1e-6 of the family value: {out[rho]["within_1e6_of_family"]}; above it by 1e-9: {out[rho]["above_family_1e9"]}; '
              f'at 2 (1e-6): {out[rho]["at_2_within_1e6"]}; above 2 + 2T(c)T(c\') by 1e-9: {above}, by 1e-7: {above7}; largest excess {exc}')
    json.dump({str(k_): v_ for k_, v_ in out.items()}, open(f'{c.ART}/p4_seeded_summary.json', 'w'), indent=1)
