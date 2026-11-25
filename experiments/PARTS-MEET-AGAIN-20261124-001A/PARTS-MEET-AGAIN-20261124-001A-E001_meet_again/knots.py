"""The knot test with any number of holders (definitions section 7), written from the frozen text.

Parity: two methods that must agree on every knot.
  ranks  - rank(H) - rank(H with the columns of S removed) == 1 (SD line 133), H one row per knot over GF(2);
  kernel - a basis of the allowed states (the kernel of H), projected onto S, has rank |S| - 1.
Not-all-equal:
  direct - for each of the 2^|S| assignments of S a SAT solver decides whether it extends to an allowed state of the
           whole structure; the knot passes when exactly the non-constant ones extend (SD lines 137-139);
  birth  - a knot born in round t passes (at t and every later round, when every birth receives a fresh distinction)
           exactly when its inputs that existed before round t are jointly free in the structure before round t
           (D 7, "The birth method"), decided by peeling, pieces and per-piece assignments.
brute  - every assignment of every distinction (small structures only), the reference for both laws.
"""
from __future__ import annotations

from collections import defaultdict

from pysat.solvers import Solver

BIRTH_PIECE_LIMIT = 22     # a piece touching more inputs than this is reported untested (R 12)


# ------------------------------------------------------------------------------------------------------------ GF(2)
class Basis:
    __slots__ = ('piv', 'log')

    def __init__(self):
        self.piv = {}
        self.log = []

    def insert(self, v):
        piv = self.piv
        while v:
            p = v.bit_length() - 1
            b = piv.get(p)
            if b is None:
                piv[p] = v
                self.log.append(p)
                return True
            v ^= b
        return False

    def mark(self):
        return len(self.log)

    def undo(self, m):
        while len(self.log) > m:
            del self.piv[self.log.pop()]

    def rank(self):
        return len(self.piv)


def _knots(S):
    return [u for u in range(S.n_knots) if u not in S.removed]


def parity_ranks(S):
    """{knot: rank(H) - rank(H without the columns of its places)}, columns as bit sets over knot positions."""
    ks = _knots(S)
    pos = {u: i for i, u in enumerate(ks)}
    cols = []
    col_knots = []
    for d, hs in enumerate(S.holders):
        if not hs:
            cols.append(0)
            col_knots.append(())
            continue
        v = 0
        for u in hs:
            v |= 1 << pos[u]
        cols.append(v)
        col_knots.append(tuple(pos[u] for u in hs))
    full = Basis()
    for v in cols:
        if v:
            full.insert(v)
    rk = full.rank()
    N = len(ks)
    out = [0] * N
    B = Basis()
    places_pos = [S.places[u] for u in ks]

    def add(lo, hi, xlo, xhi):
        seen = set()
        for i in range(lo, hi):
            for d in places_pos[i]:
                if d in seen:
                    continue
                seen.add(d)
                if any(xlo <= j < xhi for j in col_knots[d]):
                    continue
                B.insert(cols[d])

    def rec(lo, hi):
        if hi - lo == 1:
            out[lo] = B.rank()
            return
        mid = (lo + hi) // 2
        m = B.mark()
        add(mid, hi, lo, mid)
        # columns touching no knot at all in [lo, hi) were added further up
        rec(lo, mid)
        B.undo(m)
        add(lo, mid, mid, hi)
        rec(mid, hi)
        B.undo(m)

    # columns that touch no knot are zero; the recursion adds, for the range [lo, hi) being split, the columns of the
    # other half that avoid the active half; columns entirely outside [0, N) do not exist.
    if N:
        rec(0, N)
    return {ks[i]: rk - out[i] for i in range(N)}


def parity_kernel(S):
    """{knot: rank of the projection of a basis of the allowed states onto its places}, by full row reduction."""
    ks = _knots(S)
    piv_rows = {}            # pivot bit -> row (fully reduced: no other pivot bit set)
    for u in ks:
        v = 0
        for d in S.places[u]:
            v |= 1 << d
        for p, r in piv_rows.items():
            if (v >> p) & 1:
                v ^= r
        if not v:
            continue
        p = (v & -v).bit_length() - 1
        for q in list(piv_rows):
            r = piv_rows[q]
            if (r >> p) & 1:
                piv_rows[q] = r ^ v
        piv_rows[p] = v
    # kernel basis indexed by free columns: x_f = 1 for one free f; pivot c gets the bit f of its row
    out = {}
    for u in ks:
        B = Basis()
        for d in S.places[u]:
            r = piv_rows.get(d)
            if r is None:
                b = 1 << d
            else:
                b = r ^ (1 << d)
            if b:
                B.insert(b)
        out[u] = B.rank()
    return out


def parity_test(S):
    """Both methods; a knot passes when ranks gives 1 and kernel gives |S| - 1."""
    rk = parity_ranks(S)
    ke = parity_kernel(S)
    res = {}
    disagree = []
    for u in rk:
        a = rk[u] == 1
        b = ke[u] == len(S.places[u]) - 1
        res[u] = a
        if a != b:
            disagree.append(u)
    return {'pass': res, 'fail': sorted(u for u, v in res.items() if not v), 'disagree': disagree,
            'n': len(res)}


# ---------------------------------------------------------------------------------------------- not-all-equal: direct
class NaeSolver:
    """One SAT solver holding the whole structure (every knot not all equal)."""

    def __init__(self, S, knots=None):
        self.S = S
        self.sat = Solver(name='minisat22')
        for u in (knots if knots is not None else _knots(S)):
            P = S.places[u]
            vs = [d + 1 for d in P]
            self.sat.add_clause(vs)
            self.sat.add_clause([-v for v in vs])
        self.calls = 0

    def close(self):
        self.sat.delete()

    def extends(self, assum):
        self.calls += 1
        return self.sat.solve(assumptions=assum)

    def knot_passes(self, u):
        P = self.S.places[u]
        m = len(P)
        full = (1 << m) - 1
        for mask in range(1 << m):
            assum = [(d + 1) if (mask >> i) & 1 else -(d + 1) for i, d in enumerate(P)]
            ext = self.extends(assum)
            constant = mask == 0 or mask == full
            if ext == constant:
                return False
        return True


def nae_direct(S, knots):
    if not knots:
        return {}
    sv = NaeSolver(S)
    try:
        return {u: sv.knot_passes(u) for u in knots}
    finally:
        sv.close()


# ------------------------------------------------------------------------------------------ not-all-equal: the births
def jointly_free(S, I, limit=BIRTH_PIECE_LIMIT):
    """Whether every assignment of the distinctions I extends to an allowed state of S (every knot not all equal).
    Returns True, False, or None (a piece touches more than `limit` of I: untested)."""
    I = set(I)
    left = set(_knots(S))
    H = S.holders
    cnt = {}
    for u in left:
        for d in S.places[u]:
            if d not in I:
                cnt[d] = cnt.get(d, 0) + 1
    # peel: remove every knot holding a distinction held by it alone among the knots left and not in I
    stack = [u for u in left if any(cnt.get(d) == 1 for d in S.places[u] if d not in I)]
    removed = set()
    while stack:
        u = stack.pop()
        if u in removed:
            continue
        if not any(cnt.get(d) == 1 for d in S.places[u] if d not in I):
            continue
        removed.add(u)
        for d in S.places[u]:
            if d in I:
                continue
            cnt[d] -= 1
            if cnt[d] == 1:
                for w in H[d]:
                    if w in left and w not in removed:
                        stack.append(w)
    rest = left - removed
    # pieces linked by distinctions outside I
    parent = {u: u for u in rest}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by_d = {}
    for u in rest:
        for d in S.places[u]:
            if d in I:
                continue
            q = by_d.get(d)
            if q is None:
                by_d[d] = u
            else:
                a, b = find(q), find(u)
                if a != b:
                    parent[b] = a
    pieces = defaultdict(list)
    for u in rest:
        pieces[find(u)].append(u)
    for piece in pieces.values():
        touched = sorted({d for u in piece for d in S.places[u] if d in I})
        if len(touched) > limit:
            return None
        sat = Solver(name='minisat22')
        try:
            for u in piece:
                vs = [d + 1 for d in S.places[u]]
                sat.add_clause(vs)
                sat.add_clause([-v for v in vs])
            if not touched:
                if not sat.solve():
                    return False
                continue
            m = len(touched)
            # half of the assignments: flipping every distinction maps allowed states to allowed states
            for mask in range(1 << (m - 1)):
                assum = [(d + 1) if (mask >> i) & 1 else -(d + 1) for i, d in enumerate(touched)]
                if not sat.solve(assumptions=assum):
                    return False
        finally:
            sat.delete()
    return True


def birth_method(S_before, S_after, u):
    """The birth method for knot u, made in the round that turned S_before into S_after."""
    nd = S_before.n_distinctions
    I = [d for d in S_after.places[u] if d < nd]
    return jointly_free(S_before, I)


# ------------------------------------------------------------------------------------------------------------- brute
def brute(S, law):
    """Every assignment of every distinction: {knot: passes} under the knot law (small structures only)."""
    ks = _knots(S)
    D = S.n_distinctions
    assert D <= 22
    rows = []
    for u in ks:
        r = 0
        for d in S.places[u]:
            r |= 1 << d
        rows.append(r)
    allowed = []
    for a in range(1 << D):
        ok = True
        for r in rows:
            x = a & r
            if law == 'parity':
                if bin(x).count('1') & 1:
                    ok = False
                    break
            else:
                if x == 0 or x == r:
                    ok = False
                    break
        if ok:
            allowed.append(a)
    out = {}
    for u, r in zip(ks, rows):
        proj = {a & r for a in allowed}
        m = len(S.places[u])
        if law == 'parity':
            want = 1 << (m - 1)
            ok = len(proj) == want and all(bin(x).count('1') % 2 == 0 for x in proj)
        else:
            want = (1 << m) - 2
            ok = len(proj) == want and 0 not in proj and r not in proj
        out[u] = ok
    return out, len(allowed)


# ------------------------------------------------------------------------------------------------- a run's knot tests
DIRECT_LIMIT = 12


def _fail_row(S, u, t, how):
    return {'round': t, 'knot': u, 'places': len(S.places[u]), 'parents': len(S.parents[u]), 'made': S.made[u],
            'kind': S.kind[u], 'how': how}


def test_run(snaps, law, rounds=None, only_new_after=None, inherited=None):
    """The knot tests of a run (pre-registration, "Knot tests in every run").

    snaps: structures after rounds 0..R.  rounds: which rounds to test (default every round read).
    Parity: both methods on every knot at every tested round.  Not-all-equal with every birth fresh: the birth method on
    every knot made after round 0 (start knots directly at round 0), the direct test on every knot of at most 12 places
    at every tested round, the two compared; under FLOOR0 and ONE-FEWER: directly at every tested round, every knot.
    only_new_after (comparison runs): test only knots made after that round; inherited: verdicts of the others."""
    R = len(snaps) - 1
    rounds = list(range(R + 1)) if rounds is None else rounds
    out = {'verdicts': 0, 'fails': [], 'disagree': [], 'untested': [], 'birth_vs_direct': 0, 'direct_calls': 0}
    fail_keys = set()
    if law.knot_law == 'parity':
        for t in rounds:
            S = snaps[t]
            pt = parity_test(S)
            ks = [u for u in pt['pass'] if only_new_after is None or S.made[u] > only_new_after]
            out['verdicts'] += len(ks)
            for u in ks:
                if not pt['pass'][u] and (u, t) not in fail_keys:
                    fail_keys.add((u, t))
                    out['fails'].append(_fail_row(S, u, t, 'parity'))
            out['disagree'] += [{'round': t, 'knot': u, 'methods': 'ranks/kernel'} for u in pt['disagree']]
        return out
    every_fresh = law.every_birth_fresh()
    birth = {}
    if every_fresh:
        SR = snaps[R]
        for u in range(SR.n_knots):
            if u in SR.removed:
                continue
            if only_new_after is not None and SR.made[u] <= only_new_after:
                continue
            t = SR.made[u]
            if t == 0:
                v = nae_direct(snaps[0], [u])[u]
            else:
                v = birth_method(snaps[t - 1], snaps[t], u)
            birth[u] = v
            if v is None:
                out['untested'].append({'knot': u, 'places': len(SR.places[u]), 'method': 'birth'})
    for t in rounds:
        S = snaps[t]
        ks = [u for u in range(S.n_knots) if u not in S.removed
              and (only_new_after is None or S.made[u] > only_new_after)]
        if every_fresh:
            small = [u for u in ks if len(S.places[u]) <= DIRECT_LIMIT]
        else:
            small = ks
        sv = NaeSolver(S) if small else None
        try:
            direct = {u: sv.knot_passes(u) for u in small}
        finally:
            if sv is not None:
                out['direct_calls'] += sv.calls
                sv.close()
        for u in ks:
            v = direct.get(u)
            b = birth.get(u) if every_fresh else None
            if v is not None and b is not None:
                out['birth_vs_direct'] += 1
                if v != b:
                    out['disagree'].append({'round': t, 'knot': u, 'methods': 'birth/direct', 'birth': b,
                                            'direct': v})
            verdict = v if v is not None else b
            if verdict is None:
                continue
            out['verdicts'] += 1
            if not verdict and (u, t) not in fail_keys:
                fail_keys.add((u, t))
                out['fails'].append(_fail_row(S, u, t, 'direct' if v is not None else 'birth'))
        if every_fresh:
            # knots larger than the direct limit: the birth method covers every round after the knot's birth
            for u in ks:
                if u not in direct and birth.get(u) is None and u in birth:
                    pass
    return out


def merge_tests(a, b):
    if a is None:
        return b
    for k in ('verdicts', 'birth_vs_direct', 'direct_calls'):
        a[k] += b[k]
    for k in ('fails', 'disagree', 'untested'):
        a[k] += b[k]
    return a


# ----------------------------------------------------------------- not-all-equal: decomposed exact test (deviations 40)
def nae_decomposed(S, u, limit=BIRTH_PIECE_LIMIT):
    """Exact verdict for knot u in S (every knot not all equal), with no hypothesis on fresh distinctions.

    u passes exactly when every non-constant assignment of its places S_u extends to an allowed state of the structure
    without u.  The structure without u is peeled (a knot with a distinction held by it alone among the knots left and
    not in S_u can always be satisfied) and split into pieces linked by distinctions outside S_u; a piece touching T of
    u's places must allow every assignment of T when T is not all of S_u, and every non-constant one when it is.
    Returns True, False or None (a piece touches more than `limit` places: untested)."""
    P = list(S.places[u])
    I = set(P)
    left = set(_knots(S)) - {u}
    H = S.holders
    cnt = {}
    for w in left:
        for d in S.places[w]:
            if d not in I:
                cnt[d] = cnt.get(d, 0) + 1
    stack = [w for w in left if any(cnt.get(d) == 1 for d in S.places[w] if d not in I)]
    removed = set()
    while stack:
        w = stack.pop()
        if w in removed or not any(cnt.get(d) == 1 for d in S.places[w] if d not in I):
            continue
        removed.add(w)
        for d in S.places[w]:
            if d in I:
                continue
            cnt[d] -= 1
            if cnt[d] == 1:
                for x in H[d]:
                    if x in left and x not in removed:
                        stack.append(x)
    rest = left - removed
    parent = {w: w for w in rest}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    by_d = {}
    for w in rest:
        for d in S.places[w]:
            if d in I:
                continue
            q = by_d.get(d)
            if q is None:
                by_d[d] = w
            else:
                a, b = find(q), find(w)
                if a != b:
                    parent[b] = a
    pieces = defaultdict(list)
    for w in rest:
        pieces[find(w)].append(w)
    for piece in pieces.values():
        touched = sorted({d for w in piece for d in S.places[w] if d in I})
        if len(touched) > limit:
            return None
        sat = Solver(name='minisat22')
        try:
            for w in piece:
                vs = [d + 1 for d in S.places[w]]
                sat.add_clause(vs)
                sat.add_clause([-v for v in vs])
            if not touched:
                if not sat.solve():
                    return False
                continue
            m = len(touched)
            whole = (m == len(P))
            for mask in range(1 << (m - 1)):      # half: flipping every distinction maps allowed states to allowed
                if whole and mask == 0:
                    continue                      # the constant assignment of all of u's places is forbidden by u
                assum = [(d + 1) if (mask >> i) & 1 else -(d + 1) for i, d in enumerate(touched)]
                if not sat.solve(assumptions=assum):
                    return False
        finally:
            sat.delete()
    return True
