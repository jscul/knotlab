"""The exact readings of a count (KD 3) and the gate (KD 4), on integer sequences.  Everything is exact: integers and
Fractions; floats are used only to locate a candidate, never to decide (R 12).

A sequence is given as (vals, r0): vals[i] is F(r0 + i).  The final segment ends at the last value (the end of the kept
range, or the greatest r of a stage reading).
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np

RATIO_FLOOR = Fraction(5, 4)


# --------------------------------------------------------------------------------------------------- polynomials
def _diffs(v, k):
    for _ in range(k):
        v = [v[i + 1] - v[i] for i in range(len(v) - 1)]
    return v


def longest_poly_suffix(vals, j):
    """Length of the longest suffix of vals on which a polynomial of degree <= j agrees."""
    n = len(vals)
    if n <= j + 1:
        return n
    d = _diffs(vals, j + 1)
    k = len(d) - 1
    while k >= 0 and d[k] == 0:
        k -= 1
    return n - (k + 1)


def poly_coeffs(rs, vals, j):
    """Coefficients c_0..c_j (Fractions) of the polynomial of degree <= j through the points (rs[i], vals[i]),
    fitted on the first j + 1 points (exact)."""
    pts = list(zip(rs[:j + 1], vals[:j + 1]))
    n = j + 1
    A = [[Fraction(r) ** e for e in range(n)] + [Fraction(v)] for r, v in pts]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c] != 0)
        A[c], A[p] = A[p], A[c]
        for i in range(n):
            if i != c and A[i][c] != 0:
                f = A[i][c] / A[c][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    return [A[i][n] / A[i][i] for i in range(n)]


def _fstr(c):
    return str(c.numerator) if c.denominator == 1 else '%d/%d' % (c.numerator, c.denominator)


def poly_str(cs):
    return '[' + ', '.join(_fstr(c) for c in cs) + ']'


def power_plain(vals, r0):
    """POWER(j), plain form: the least j in 0..3 whose longest suffix of degree <= j has at least j + 8 values; the
    polynomial there then has degree exactly j (a smaller degree would have been found first).  F == 0 is no POWER."""
    n = len(vals)
    for j in range(4):
        L = longest_poly_suffix(vals, j)
        if L >= j + 8:
            seg = vals[n - L:]
            if all(x == 0 for x in seg):
                return None
            dj = _diffs(seg, j)
            if not dj or all(x == 0 for x in dj):
                continue
            a = r0 + n - L
            rs = list(range(a, a + L))
            return {'verdict': 'POWER', 'j': j, 'm': 1, 'segment': [a, r0 + n - 1],
                    'poly': poly_str(poly_coeffs(rs, seg, j))}
    return None


def power_phase(vals, r0, m):
    """The m-phase form: F(m*i + q) = p_q(i) for every residue q, each p_q of degree exactly j with >= j + 8 values on
    the common final segment [a, z]; least j.  Residues are of r itself."""
    n = len(vals)
    z = r0 + n - 1
    for j in range(4):
        starts = []
        for q in range(m):
            rs = [r for r in range(r0, z + 1) if r % m == q]
            sub = [vals[r - r0] for r in rs]
            L = longest_poly_suffix(sub, j)
            if L == 0:
                starts = None
                break
            starts.append(rs[len(rs) - L])
        if starts is None:
            continue
        a = max(max(starts) - m + 1, r0)
        ok = True
        polys = []
        for q in range(m):
            rs = [r for r in range(a, z + 1) if r % m == q]
            sub = [vals[r - r0] for r in rs]
            if len(sub) < j + 8 or all(x == 0 for x in sub):
                ok = False
                break
            dj = _diffs(sub, j)
            if all(x == 0 for x in dj):
                ok = False
                break
            ii = [(r - q) // m for r in rs]
            polys.append(poly_str(poly_coeffs(ii, sub, j)))
        if ok:
            return {'verdict': 'POWER', 'j': j, 'm': m, 'segment': [a, z], 'poly_by_phase': polys}
    return None


def power(vals, r0):
    p = power_plain(vals, r0)
    if p is not None:
        return p
    for m in (2, 3, 4):
        p = power_phase(vals, r0, m)
        if p is not None:
            return p
    return None


# --------------------------------------------------------------------------------------------------- recurrences
def _solve(A, b):
    n = len(A)
    M = [list(map(Fraction, A[i])) + [Fraction(b[i])] for i in range(n)]
    for c in range(n):
        p = next((i for i in range(c, n) if M[i][c] != 0), None)
        if p is None:
            return None
        M[c], M[p] = M[p], M[c]
        for i in range(n):
            if i != c and M[i][c] != 0:
                f = M[i][c] / M[c][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def largest_root(cs):
    k = len(cs)
    if k == 1:
        return float(cs[0]), True
    coeffs = [1.0] + [-float(c) for c in cs]
    roots = np.roots(coeffs)
    i = int(np.argmax(np.abs(roots)))
    r = roots[i]
    return (float(r.real) if abs(r.imag) < 1e-12 else complex(r)), abs(r.imag) < 1e-12


def linrec(vals, r0, kmax=3, verify=8):
    """LINREC(k), least k first: fitted exactly on the last 2k terms, verified on at least `verify` further terms; the
    segment is the longest suffix on which the fitted recurrence holds."""
    n = len(vals)
    for k in range(1, kmax + 1):
        if n < 2 * k + verify:
            continue
        A = [[vals[r - i] for i in range(1, k + 1)] for r in range(n - k, n)]
        b = [vals[r] for r in range(n - k, n)]
        cs = _solve(A, b)
        if cs is None:
            continue
        start = 0
        for idx in range(n - k - 1, k - 1, -1):
            if Fraction(vals[idx]) != sum(c * vals[idx - i - 1] for i, c in enumerate(cs)):
                start = idx - k + 1
                break
        verified = n - 2 * k - start
        if verified >= verify:
            root, real = largest_root(cs)
            return {'verdict': 'LINREC', 'k': k, 'coeffs': [_fstr(c) for c in cs], 'segment': [r0 + start, r0 + n - 1],
                    'fitted': 2 * k, 'verified': verified,
                    'root': root if real else str(root), 'root_modulus': float(abs(complex(root)))}
    return None


# ------------------------------------------------------------------------------------------------------- bounds
def ratio_ok(vals, r0, a, z, j, limit=2):
    """Exact: max F(r)/r^j <= limit * min F(r)/r^j on [a, z] (F > 0 there).  Returns (ok, Cmax, cmin) as Fractions."""
    best_hi = best_lo = None
    for r in range(a, z + 1):
        f = Fraction(vals[r - r0], r ** j)
        if best_hi is None or f > best_hi:
            best_hi = f
        if best_lo is None or f < best_lo:
            best_lo = f
    if best_lo <= 0:
        return False, best_hi, best_lo
    return best_hi <= limit * best_lo, best_hi, best_lo


def bound(vals, r0, amin=4, factor=8, limit=2):
    """BOUND(j): c r^j <= F <= C r^j on [a, z], z the end, a >= 4, z >= 8a, C/c <= 2; least a.  j is unique when it
    exists (z >= 8a and C/c <= 2 fix it); the least such j is returned and any second one flagged."""
    n = len(vals)
    z = r0 + n - 1
    found = []
    for j in range(4):
        amax = z // factor
        lo_a = max(amin, r0)
        if amax < lo_a:
            continue
        if any(vals[r - r0] <= 0 for r in range(amax, z + 1)):
            continue
        ok, C, c = ratio_ok(vals, r0, amax, z, j, limit)
        if not ok:
            continue
        a = amax
        while a - 1 >= lo_a:
            if vals[a - 1 - r0] <= 0:
                break
            ok2, C2, c2 = ratio_ok(vals, r0, a - 1, z, j, limit)
            if not ok2:
                break
            a, C, c = a - 1, C2, c2
        found.append({'verdict': 'BOUND', 'j': j, 'segment': [a, z], 'c': float(c), 'C': float(C),
                      'C_over_c': float(C / c), 'note': 'admits exponents within a third of j'})
    if not found:
        return None
    out = found[0]
    if len(found) > 1:
        out['also_j'] = [f['j'] for f in found[1:]]
    return out


def increments(vals, r0):
    """S(r) = F(r) - F(r - 1), r from r0 + 1 (KD 3.1)."""
    return [vals[i] - vals[i - 1] for i in range(1, len(vals))], r0 + 1


def ratio(svals, s0, floor=RATIO_FLOOR, minlen=8):
    """RATIO(x) on the longest final segment [a, z] of S with S(r+1) >= floor*S(r), S > 0, z - a >= 8; x the least
    ratio there.  Otherwise 'rising' (strictly rising S on a final segment with z - a >= 8) or None."""
    n = len(svals)
    if n < 2:
        return None
    i = n - 1
    while i - 1 >= 0 and svals[i - 1] > 0 and svals[i] >= floor * svals[i - 1]:
        i -= 1
    if (n - 1) - i >= minlen:
        x = min(Fraction(svals[k + 1], svals[k]) for k in range(i, n - 1))
        return {'verdict': 'RATIO', 'x': float(x), 'x_exact': _fstr(x), 'segment': [s0 + i, s0 + n - 1]}
    i = n - 1
    while i - 1 >= 0 and svals[i - 1] > 0 and svals[i] > svals[i - 1]:
        i -= 1
    if (n - 1) - i >= minlen:
        x = min(Fraction(svals[k + 1], svals[k]) for k in range(i, n - 1))
        return {'verdict': 'UNDECIDED', 'rising': True, 'least_ratio': float(x), 'segment': [s0 + i, s0 + n - 1]}
    return None


# ------------------------------------------------------------------------------------------------- the precedence
def read(vals, r0=0, ended=False, kind='H', floor=RATIO_FLOOR, with_bound=True, earlier=True):
    """The verdict of a count on its final segment by KD 3.6's precedence: ENDED; POWER(j); LINREC(k); BOUND(j);
    RATIO(x); UNDECIDED.  kind 'H' and 'P': RATIO on the increments S; kind 'b': RATIO on b itself (R 5).
    Exact readings on earlier, disjoint segments are listed nearest first (R 6)."""
    vals = [int(v) for v in vals]
    out = None
    if ended:
        out = {'verdict': 'ENDED', 'segment': [r0, r0 + len(vals) - 1]}
    if out is None:
        out = power(vals, r0)
    if out is None:
        out = linrec(vals, r0)
    if out is None and with_bound:
        out = bound(vals, r0)
    if out is None:
        if kind == 'b':
            out = ratio(vals, r0, floor)
        else:
            s, s0 = increments(vals, r0)
            out = ratio(s, s0, floor)
    if out is None:
        out = {'verdict': 'UNDECIDED', 'segment': [r0, r0 + len(vals) - 1]}
    if earlier and out['verdict'] in ('POWER', 'LINREC', 'ENDED'):
        a = out['segment'][0] if out['verdict'] != 'ENDED' else None
        out['earlier'] = earlier_exact(vals, r0, a) if a is not None else []
    return out


def earlier_exact(vals, r0, a):
    """Exact readings (POWER, LINREC) on earlier disjoint segments ending at a - 1, a' - 1, ..., nearest first."""
    out = []
    while a is not None and a - r0 >= 1:
        sub = vals[:a - r0]
        e = power(sub, r0) or linrec(sub, r0)
        if e is None:
            break
        out.append(e)
        a = e['segment'][0]
        if a <= r0:
            break
    return out


def label(v):
    """A short label of a verdict: 'POWER(2)', 'POWER(1) 2-phase', 'LINREC(1) root 2', 'ENDED', ..."""
    if v is None:
        return 'none'
    t = v['verdict']
    if t == 'POWER':
        return 'POWER(%d)' % v['j'] + ('' if v.get('m', 1) == 1 else ' %d-phase' % v['m'])
    if t == 'LINREC':
        return 'LINREC(%d)' % v['k']
    if t == 'BOUND':
        return 'BOUND(%d)' % v['j']
    if t == 'RATIO':
        return 'RATIO'
    if t == 'UNDECIDED':
        return 'UNDECIDED rising' if v.get('rising') else 'UNDECIDED'
    return t


# ------------------------------------------------------------------------------------------- the doubling reading
def doubling(vals, r0=0, amin=4, tol=0.3):
    """KD 3.7 (swap): eps(r) = log2(F(2r)/F(r)); maximal runs of r with |eps - j| <= 0.3 for one whole j, starting at
    r >= 4, kept when the run spans a doubling (z >= 2a, R 7); reported as [a, 2z], nearest the end first."""
    n = len(vals)
    zmax = (r0 + n - 1) // 2
    eps = {}
    for r in range(max(amin, r0, 1), zmax + 1):
        f1, f2 = vals[r - r0], vals[2 * r - r0]
        if f1 > 0 and f2 > 0:
            eps[r] = math.log2(f2 / f1)
    runs = []
    r = zmax
    while r >= amin:
        if r not in eps:
            r -= 1
            continue
        j = round(eps[r])
        if abs(eps[r] - j) > tol:
            r -= 1
            continue
        z = r
        while r - 1 >= amin and (r - 1) in eps and abs(eps[r - 1] - j) <= tol:
            r -= 1
        a = r
        if z >= 2 * a:
            runs.append({'j': int(j), 'range': [a, 2 * z]})
        r = a - 1
    return runs


# ------------------------------------------------------------------------------------------------------- the gate
def gate(counts, lmax=None, amin=4, factor=8, limit=2, labels=None):
    """KD 4.1-4.3.  counts: {knot: list H(u, 0..l(u))}.  The canonical range: z the greatest value allowed (the least
    l(u), or less if no j and a work there), then a the least for that z and j.  Returns the gate (holds or not, j,
    [a, z], k of K with the per-knot least ratios) and the spread in bands; and the gates on earlier ranges [4, a - 1],
    nearest first.  labels: {knot: 'start' | 'made'} for the spread lines."""
    knots_ = sorted(counts)
    K = len(knots_)
    if K == 0:
        return {'holds': False, 'K': 0, 'reason': 'no knots examined'}
    zmax = min(len(counts[u]) - 1 for u in knots_)
    if lmax is not None:
        zmax = min(zmax, lmax)
    res = _gate_scan(counts, knots_, zmax, amin, factor, limit)
    out = dict(res)
    out['K'] = K
    out['least_l'] = min(len(counts[u]) - 1 for u in knots_)
    if res['holds']:
        out['spread'] = spread(counts, knots_, res['j'], res['range'], labels)
        earlier = []
        a = res['range'][0]
        while a - 1 >= amin * factor:
            e = _gate_scan(counts, knots_, a - 1, amin, factor, limit)
            if not e['holds']:
                break
            e['spread'] = spread(counts, knots_, e['j'], e['range'], labels)
            earlier.append(e)
            a = e['range'][0]
        out['earlier'] = earlier
    return out


def _gate_scan(counts, knots_, zmax, amin, factor, limit):
    """Scan z from zmax down; for each z and each j the least a with every knot within `limit`; first z that works."""
    if zmax < amin * factor:
        return {'holds': False, 'reason': 'least kept range %d below %d' % (zmax, amin * factor), 'zmax': zmax,
                'best': None}
    K = len(knots_)
    arr = np.array([[counts[u][r] for r in range(zmax + 1)] for u in knots_], dtype=float)
    rr = np.arange(zmax + 1, dtype=float)
    rr[0] = 1.0
    G = [arr / rr ** j for j in range(4)]
    tol = 1 + 1e-9          # floats only rule out; a pass is confirmed exactly below (R 12)
    for z in range(zmax, amin * factor - 1, -1):
        A = z // factor
        for j in range(4):
            g = G[j]
            blk = g[:, A:z + 1]
            hi = blk.max(axis=1)
            lo = blk.min(axis=1)
            if np.any(lo <= 0) or np.any(hi > limit * lo * tol):
                continue
            a_arr = np.full(K, A)
            h, l = hi.copy(), lo.copy()
            alive = np.ones(K, dtype=bool)
            for aa in range(A - 1, amin - 1, -1):
                v = g[:, aa]
                h2, l2 = np.maximum(h, v), np.minimum(l, v)
                okk = alive & (l2 > 0) & (h2 <= limit * l2 * tol)
                a_arr[okk] = aa
                h[okk], l[okk] = h2[okk], l2[okk]
                alive = okk
                if not alive.any():
                    break
            a_need = int(a_arr.max())
            # exact confirmation on [a_need, z] for every knot; step a up if a float misjudged
            a = a_need
            while a <= A:
                exact = [ratio_ok(counts[u], 0, a, z, j, limit) for u in knots_]
                if all(e[0] for e in exact):
                    ratios = {u: float(e[1] / e[2]) for u, e in zip(knots_, exact)}
                    cs = {u: (float(e[2]), float(e[1])) for u, e in zip(knots_, exact)}
                    return {'holds': True, 'j': j, 'range': [a, z], 'k': len(knots_), 'per_knot_ratio_max':
                            max(ratios.values()), 'c_C': cs}
                a += 1
    # no gate: report, at the least kept range, how many knots pass for each j on the widest allowed [a, z]
    # (floats with the tolerance above; descriptive only)
    z = zmax
    A = z // factor
    passing = {}
    for j in range(4):
        blk = G[j][:, A:z + 1]
        hi, lo = blk.max(axis=1), blk.min(axis=1)
        passing[j] = int(np.sum((lo > 0) & (hi <= limit * lo * tol)))
    jbest = max(passing, key=lambda j: passing[j])
    return {'holds': False, 'reason': 'no j and range', 'zmax': zmax, 'k_by_j_on_widest': passing,
            'k': passing[jbest], 'j_best': jbest, 'widest': [A, z]}


def spread(counts, knots_, j, rng, labels=None):
    a, z = rng
    cs, Cs = {}, {}
    for u in knots_:
        ok, C, c = ratio_ok(counts[u], 0, a, z, j, 10 ** 9)
        cs[u], Cs[u] = c, C

    def band(x):
        return 'at most 2' if x <= 2 else ('at most 4' if x <= 4 else 'above 4')
    out = {}
    groups = {'all': knots_}
    if labels:
        groups['start'] = [u for u in knots_ if labels.get(u) == 'start']
        groups['made'] = [u for u in knots_ if labels.get(u) != 'start']
    for g, ks in groups.items():
        if not ks:
            continue
        s = max(Cs[u] for u in ks) / min(cs[u] for u in ks)
        out[g] = {'spread': float(s), 'band': band(s), 'n': len(ks)}
    return out
