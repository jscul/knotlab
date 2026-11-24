"""Shared definitions for THIRD-HOLDER-20261123-001A-E001 (a structure with a third holder: the hidden excess checked in full).

Definitions follow research/THIRD-HOLDER-20261123-001A/preregistration.md (frozen).  The 18-knot structure is the one of the
post hoc check research/REVIEW-LEADS-20261123-001/posthoc/three_holders_check.py (knot lists copied from there).  The score,
hiding and change follow docs/prompts/missed_leads_checks/finished_weighting_chsh.py (`evaluate`), generalised here to k births
per setting and computed from joint tables of complete records rather than from the old-word table.

Engines:
  * `enumerate_counts`: full enumeration of every assignment of every listed distinction, every knot tested on every
    assignment, numpy bit operations on 64 assignments per word, in chunks; counts indexed by the values of chosen
    distinctions (the records).
  * side tables: the same enumeration on each side alone, keyed by the record and the two shared distinctions s1, s2,
    then combined by a product over the shared values.
  * `backtrack_counts`: an exhaustive backtracking search over the whole finished structure (no factorisation by side):
    each assignment is either listed or excluded by a knot that a partial assignment already violates.
"""
import os, itertools, json, math
import numpy as np
from fractions import Fraction

REPO = '/home/jscul/p-vs-np-contact-first'
EXP = os.path.join(REPO, 'experiments/THIRD-HOLDER-20261123-001A/THIRD-HOLDER-20261123-001A-E001_witness')
ART = os.path.join(REPO, 'artifacts/THIRD-HOLDER-20261123-001A/THIRD-HOLDER-20261123-001A-E001_witness')
os.makedirs(ART, exist_ok=True)

# ---- the structure (frozen; copied from the post hoc check) -----------------------------------------------------------------
A_NAMES = 'x1 x2 x3 s1 s2 a b c1 k1 d e c2 c3 n1 n2 g h u v'.split()
A_KNOTS = [('even', ('x1', 'a', 'b')), ('even', ('c1', 'a', 'b')), ('even', ('k1', 'a', 'b')),
           ('even', ('x2', 'd', 'e')), ('odd', ('x3', 'd', 'e')), ('even', ('c2', 'd', 'e')), ('odd', ('c3', 'd', 'e')),
           ('nae', ('c1', 'c2', 'n2')), ('nae', ('k1', 'c3', 'n1')),
           ('even', ('n2', 'g', 'h')), ('odd', ('s2', 'g', 'h')), ('even', ('n1', 'u', 'v')), ('odd', ('s1', 'u', 'v'))]
B_NAMES = 'y1 y2 y3 s1 s2 p q r t'.split()
B_KNOTS = [('even', ('y1', 'p', 'q')), ('even', ('s1', 'p', 'q')),
           ('even', ('y2', 'r', 't')), ('even', ('s2', 'r', 't')), ('odd', ('y3', 'r', 't'))]
SHARED = ['s1', 's2']

# copying pairs for further births (pre-registration: "copies are made by further holders on the copying pairs")
COPY_RULES = {'x1': ('even', ('a', 'b')), 'x2': ('even', ('d', 'e')), 'x3': ('odd', ('d', 'e')),
              'y1': ('even', ('p', 'q')), 'y2': ('even', ('r', 't')), 'y3': ('odd', ('r', 't'))}


def copy_name(v, i):
    """i-th loose copy of old distinction v (i = 1 is v itself)."""
    return v if i == 1 else f'{v}_{i}'


def build(k, birth_law='nae'):
    """The structure with k births per setting.  Returns a dict with the old structure, the copies, and the births of each
    setting of each observer.  birth_law: 'nae' (the study), 'even' or 'odd' (the parity-birth control)."""
    a_names = list(A_NAMES); a_knots = list(A_KNOTS)
    b_names = list(B_NAMES); b_knots = list(B_KNOTS)
    for i in range(2, k + 1):
        for v in ('x1', 'x2', 'x3'):
            law, pair = COPY_RULES[v]; cv = copy_name(v, i)
            a_names.append(cv); a_knots.append((law, (cv,) + pair))
        for v in ('y1', 'y2', 'y3'):
            law, pair = COPY_RULES[v]; cv = copy_name(v, i)
            b_names.append(cv); b_knots.append((law, (cv,) + pair))
    zA = [f'z{i}' for i in range(1, k + 1)]
    zB = [f'w{i}' for i in range(1, k + 1)]
    births_A = {s: [(birth_law, (copy_name('x1', i), copy_name('x2' if s == 0 else 'x3', i), zA[i - 1])) for i in range(1, k + 1)]
                for s in (0, 1)}
    births_B = {s: [(birth_law, (copy_name('y1', i), copy_name('y2' if s == 0 else 'y3', i), zB[i - 1])) for i in range(1, k + 1)]
                for s in (0, 1)}
    recA = ['x1', 'x2', 'x3'] + zA
    recB = ['y1', 'y2', 'y3'] + zB
    return dict(k=k, birth_law=birth_law, a_names=a_names, a_knots=a_knots, b_names=b_names, b_knots=b_knots,
                zA=zA, zB=zB, births_A=births_A, births_B=births_B, recA=recA, recB=recB)


def old_names(S):
    return S['a_names'] + [v for v in S['b_names'] if v not in S['a_names']]


def finished(S, sa, sb):
    """(names, knots) of the finished structure at settings (sa, sb): every distinction, every knot."""
    names = old_names(S) + S['zA'] + S['zB']
    knots = S['a_knots'] + S['b_knots'] + S['births_A'][sa] + S['births_B'][sb]
    return names, knots


def holders(knots):
    h = {}
    for _, mem in knots:
        for m in mem:
            h[m] = h.get(m, 0) + 1
    return h


def extra_holders(knots):
    h = holders(knots)
    return sum(max(0, n - 2) for n in h.values()), {v: n for v, n in sorted(h.items()) if n > 2}


# ---- full enumeration by numpy bit operations ------------------------------------------------------------------------------
ALL = np.uint64(0xFFFFFFFFFFFFFFFF)
ZERO = np.uint64(0)
INNER_PAT = [np.uint64(p) for p in (0xAAAAAAAAAAAAAAAA, 0xCCCCCCCCCCCCCCCC, 0xF0F0F0F0F0F0F0F0,
                                    0xFF00FF00FF00FF00, 0xFFFF0000FFFF0000, 0xFFFFFFFF00000000)]


def _law_ok(law, P, buf, tmp):
    """bit plane of the assignments that satisfy the knot; P: list of planes (np.uint64 scalars or arrays)."""
    if law in ('even', 'odd'):
        r = P[0] ^ P[1]
        for p in P[2:]:
            r = r ^ p
        return ~r if law == 'even' else r
    if law == 'nae':
        o = P[0] | P[1]; n = P[0] & P[1]
        for p in P[2:]:
            o = o | p; n = n & p
        return o & ~n
    raise ValueError(law)


def enumerate_counts(names, knots, outer, max_lo=20, progress=None, outer_range=None):
    """Every assignment of all of `names` (2^len(names)) is tested against every knot of `knots` (no early exit).
    Returns an integer array of length 2^len(outer): the number of allowed assignments for each value of the `outer`
    distinctions (first listed = most significant bit).  With outer_range = (lo, hi) only the outer values lo..hi-1 are
    enumerated (the other entries are -1), so that a long enumeration can be split into runs."""
    names = list(names)
    assert len(set(names)) == len(names)
    for _, mem in knots:
        for m in mem:
            assert m in names, m
    rest = [v for v in names if v not in outer]
    inner = rest[:6]; mid = rest[6:]
    lo = mid[:max_lo]; hi = mid[max_lo:]
    lanes = 1 << len(inner)
    valid = ALL if lanes == 64 else np.uint64((1 << lanes) - 1)
    idx = np.arange(1 << len(lo), dtype=np.uint64)
    lo_planes = {v: np.where((idx >> np.uint64(j)) & np.uint64(1), ALL, ZERO).astype(np.uint64) for j, v in enumerate(lo)}
    planes = {v: INNER_PAT[j] for j, v in enumerate(inner)}
    planes.update(lo_planes)
    no = len(outer); nh = len(hi)
    out = np.zeros(1 << no, dtype=np.int64)
    o_lo, o_hi = outer_range if outer_range is not None else (0, 1 << no)
    if outer_range is not None:
        out[:] = -1
    for o in range(o_lo, o_hi):
        for j, v in enumerate(outer):
            planes[v] = ALL if (o >> (no - 1 - j)) & 1 else ZERO
        tot = 0
        for h in range(1 << nh):
            for j, v in enumerate(hi):
                planes[v] = ALL if (h >> j) & 1 else ZERO
            mask = np.full(1 << len(lo), valid, dtype=np.uint64)
            for law, mem in knots:
                ok = _law_ok(law, [planes[m] for m in mem], None, None)
                mask &= ok
            tot += int(np.bitwise_count(mask).sum())
        out[o] = tot
        if progress and (o + 1 - o_lo) % progress == 0:
            print(f'   outer {o + 1}/{1 << no}', flush=True)
    return out


def full_joint(S, sa, sb, **kw):
    """Joint table of complete records (Alice record x Bob record) of the finished structure (sa, sb), by full enumeration."""
    names, knots = finished(S, sa, sb)
    outer = S['recA'] + S['recB']
    cnt = enumerate_counts(names, knots, outer, **kw)
    return cnt.reshape(1 << len(S['recA']), 1 << len(S['recB'])), len(names), len(knots)


def side_tables(S, sa, sb):
    """Alice's and Bob's side tables keyed by (record, s1 s2) by enumeration of each side alone, and their product."""
    namesA = S['a_names'] + S['zA']; knotsA = S['a_knots'] + S['births_A'][sa]
    namesB = S['b_names'] + S['zB']; knotsB = S['b_knots'] + S['births_B'][sb]
    TA = enumerate_counts(namesA, knotsA, S['recA'] + SHARED).reshape(1 << len(S['recA']), 4)
    TB = enumerate_counts(namesB, knotsB, S['recB'] + SHARED).reshape(1 << len(S['recB']), 4)
    return TA, TB, TA @ TB.T


def old_table(S):
    """Old allowed-word counts by (x1x2x3, y1y2y3), by full enumeration of the old structure."""
    names = old_names(S); knots = S['a_knots'] + S['b_knots']
    return enumerate_counts(names, knots, ['x1', 'x2', 'x3', 'y1', 'y2', 'y3']).reshape(8, 8)


# ---- exhaustive backtracking over the whole finished structure ---------------------------------------------------------
LAW_FN = {'even': lambda v: sum(v) % 2 == 0, 'odd': lambda v: sum(v) % 2 == 1, 'nae': lambda v: 0 < sum(v) < len(v)}


def order_vars(names, knots):
    """Greedy order: next the distinction completing the most knots, ties by most knots touched."""
    left = list(names); done = set(); order = []
    while left:
        def score(v):
            comp = sum(1 for _, mem in knots if v in mem and all(m in done or m == v for m in mem))
            touch = sum(1 for _, mem in knots if v in mem)
            return (comp, touch)
        v = max(left, key=score)
        order.append(v); done.add(v); left.remove(v)
    return order


def backtrack_counts(names, knots, outer, words_out=None):
    """Counts of allowed assignments keyed by the `outer` values, by exhaustive backtracking.  If words_out is a list, every
    allowed assignment is appended to it as a dict."""
    order = order_vars(names, knots)
    pos = {v: i for i, v in enumerate(order)}
    check_at = [[] for _ in order]
    for law, mem in knots:
        last = max(pos[m] for m in mem)
        check_at[last].append((LAW_FN[law], [pos[m] for m in mem]))
    val = [0] * len(order)
    opos = [pos[v] for v in outer]
    out = np.zeros(1 << len(outer), dtype=np.int64)
    n = len(order)
    nodes = [0]

    def rec(i):
        if i == n:
            key = 0
            for p in opos:
                key = key * 2 + val[p]
            out[key] += 1
            if words_out is not None:
                words_out.append({v: val[pos[v]] for v in names})
            return
        for b in (0, 1):
            val[i] = b; nodes[0] += 1
            ok = True
            for fn, ps in check_at[i]:
                if not fn([val[p] for p in ps]):
                    ok = False; break
            if ok:
                rec(i + 1)
    rec(0)
    return out, nodes[0]


# ---- records, outcomes, score, hiding, change ------------------------------------------------------------------------------
def sgn_matrix(L):
    """parity outcomes of an L-bit record: rows masks 1..2^L-1, columns records 0..2^L-1, entries (-1)^{popcount(m & r)}."""
    r = np.arange(1 << L)
    m = np.arange(1, 1 << L)
    pc = np.vectorize(lambda v: bin(int(v)).count('1'))(m[:, None] & r[None, :])
    return (1 - 2 * (pc % 2)).astype(np.int64)


def chsh_best_float(E):
    """E: dict (a,b) -> float array (nA, nB) of correlations.  Best |CHSH| over the outcome choices and the four one-minus
    sign patterns.  Returns (value, (kA0, kA1, kB0, kB1, pattern))."""
    E00, E01, E10, E11 = E[0, 0], E[0, 1], E[1, 0], E[1, 1]
    best = -1.0; arg = None
    for p in range(4):
        s = [1.0] * 4; s[p] = -1.0
        u = s[0] * E00[:, None, :] + s[2] * E10[None, :, :]          # (kA0, kA1, kB0)
        v = s[1] * E01[:, None, :] + s[3] * E11[None, :, :]          # (kA0, kA1, kB1)
        hi = u.max(-1) + v.max(-1); lo = -(u.min(-1) + v.min(-1))
        tot = np.maximum(hi, lo)
        i = np.unravel_index(int(tot.argmax()), tot.shape)
        if tot[i] > best:
            best = float(tot[i]); arg = (int(i[0]), int(i[1]), p)
    return best, arg


def chsh_exact(J, SA, SB, tol=1e-9):
    """Exact best |CHSH| over parity outcomes from integer joint record tables J[(a,b)] (rational, Fractions).
    Every outcome choice whose float value is within tol of the float best is evaluated exactly."""
    num = {ab: SA @ J[ab] @ SB.T for ab in J}
    Z = {ab: int(J[ab].sum()) for ab in J}
    E = {ab: num[ab] / Z[ab] for ab in J}
    fbest, _ = chsh_best_float(E)
    best = (Fraction(-1), None)
    for p in range(4):
        s = [1] * 4; s[p] = -1
        u = s[0] * E[0, 0][:, None, :] + s[2] * E[1, 0][None, :, :]
        v = s[1] * E[0, 1][:, None, :] + s[3] * E[1, 1][None, :, :]
        for sign in (1, -1):
            uu = sign * u; vv = sign * v
            pair = uu.max(-1) + vv.max(-1)
            for kA0, kA1 in np.argwhere(pair >= fbest - tol):
                cb0 = np.nonzero(uu[kA0, kA1] >= uu[kA0, kA1].max() - tol)[0]
                cb1 = np.nonzero(vv[kA0, kA1] >= vv[kA0, kA1].max() - tol)[0]
                for kB0 in cb0:
                    for kB1 in cb1:
                        val = sign * (s[0] * Fraction(int(num[0, 0][kA0, kB0]), Z[0, 0]) + s[1] * Fraction(int(num[0, 1][kA0, kB1]), Z[0, 1])
                                      + s[2] * Fraction(int(num[1, 0][kA1, kB0]), Z[1, 0]) + s[3] * Fraction(int(num[1, 1][kA1, kB1]), Z[1, 1]))
                        if val > best[0]:
                            best = (val, dict(maskA0=int(kA0) + 1, maskA1=int(kA1) + 1, maskB0=int(kB0) + 1, maskB1=int(kB1) + 1,
                                              minus_on=['00', '01', '10', '11'][p], overall_sign=sign))
    assert abs(float(best[0]) - fbest) < 1e-7, (best[0], fbest)
    return best[0], best[1], fbest


def hiding(J):
    """Exact hiding of both complete records and the largest change (total variation, Fraction) of a complete record."""
    Z = {ab: int(J[ab].sum()) for ab in J}
    hidA = hidB = True; tv = Fraction(0)
    for a in (0, 1):
        m0 = J[a, 0].sum(1); m1 = J[a, 1].sum(1)
        if not np.array_equal(m0 * Z[a, 1], m1 * Z[a, 0]): hidA = False
        tv = max(tv, sum(abs(Fraction(int(p), Z[a, 0]) - Fraction(int(q), Z[a, 1])) for p, q in zip(m0, m1)) / 2)
    for b in (0, 1):
        n0 = J[0, b].sum(0); n1 = J[1, b].sum(0)
        if not np.array_equal(n0 * Z[1, b], n1 * Z[0, b]): hidB = False
        tv = max(tv, sum(abs(Fraction(int(p), Z[0, b]) - Fraction(int(q), Z[1, b])) for p, q in zip(n0, n1)) / 2)
    return hidA, hidB, tv


def lawful_count(k, x, s, law='nae'):
    """number of lawful fresh values of k births of the given law on (x1, x_{2+s}) for old record x (3 bits, x1 high)."""
    x1 = (x >> 2) & 1; xs = (x >> 1) & 1 if s == 0 else x & 1
    n = 0
    for z in itertools.product((0, 1), repeat=k):
        if all(LAW_FN[law]([x1, xs, zi]) for zi in z): n += 1
    return n


def control_tables(J, k):
    """Control weighting: each old word has weight 1, divided equally among its extensions.  Returns integer tables scaled by
    (2^k)^2 so that every entry is an integer: J_ab[rA, rB] * (2^k / nA_a(x)) * (2^k / nB_b(y))."""
    L = 3 + k; out = {}
    for (a, b), T in J.items():
        fa = np.array([2 ** k // lawful_count(k, r >> k, a) for r in range(1 << L)], dtype=np.int64)
        fb = np.array([2 ** k // lawful_count(k, r >> k, b) for r in range(1 << L)], dtype=np.int64)
        for r in range(1 << L):
            assert 2 ** k % lawful_count(k, r >> k, a) == 0
        out[a, b] = T * fa[:, None] * fb[None, :]
    return out


def evaluate_tables(J, k):
    L = 3 + k
    S = sgn_matrix(L)
    val, combo, fval = chsh_exact(J, S, S)
    hA, hB, tv = hiding(J)
    totals = {f'{a}{b}': int(J[a, b].sum()) for (a, b) in J}
    return dict(score=str(val), score_float=float(val), outcome_choice=combo, hidden_alice=bool(hA), hidden_bob=bool(hB),
                largest_change=str(tv), totals=totals)


def save_joint(path, J):
    json.dump({f'{a}{b}': J[a, b].tolist() for (a, b) in J}, open(path, 'w'))


def load_joint(path):
    d = json.load(open(path))
    return {(int(key[0]), int(key[1])): np.array(v, dtype=np.int64) for key, v in d.items()}


def knot_cnf(law, mem):
    """CNF text (knotlab syntax) of a three- or four-place parity or not-all-equal knot."""
    cl = []
    for vals in itertools.product((0, 1), repeat=len(mem)):
        if not LAW_FN[law](list(vals)):
            cl.append(' '.join(m if v == 0 else '~' + m for m, v in zip(mem, vals)))
    return '; '.join(cl)


def canonical_check(law, mem):
    """Canonical K1-K3 test (tools/knotlab) of one knot, with every choice of which place is the contact."""
    import sys
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    from knotlab.relations import Relation, parse_cnf
    from knotlab.knots import check_knot
    res = []
    for ci in range(len(mem)):
        loops = [m for j, m in enumerate(mem) if j != ci]; contact = mem[ci]
        rel = Relation.from_cnf(parse_cnf(knot_cnf(law, mem)), [*loops, contact], [])
        rep = check_knot(rel, loops, contact, 'forgetting')
        res.append(dict(loops=loops, contact=contact, K1=rep.binding, K2=rep.loss_on_erasure, K3=rep.coexistence,
                        knot=rep.is_knot, allowed=rel.table()))
    return res
