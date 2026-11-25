"""The knot test (TD 7, FD 7, SD lines 128-141), written from the frozen text.

Parity, two methods that must agree on every knot:
  ranks  - rank(H) - rank(H with the columns of the knot's places removed) == 1 (SD line 133), computed on the
           matrix left after peeling (a knot with a column outside the removed set held by it alone is deleted with
           that column: the difference of the two ranks does not change, dev 15);
  kernel - a basis of the allowed states (kept as one bit column per distinction over the basis vectors, extended
           knot by knot in birth order), projected onto the knot's places, has rank |S| - 1.
Not-all-equal:
  direct - for each assignment of the knot's places a SAT solver decides whether it extends to an allowed state of the
           whole structure; the knot passes when exactly the non-constant ones extend (SD lines 137-139);
  birth  - a knot born in round t passes (at t and every later round, when every birth receives a fresh distinction)
           exactly when its inputs are jointly free in the structure before round t (FD 7), decided by peeling, pieces
           and per-piece assignments.
brute  - every assignment of every distinction (small structures), the reference for every method.
Extension (SD line 140) is checked for every round: every birth either receives a fresh distinction (it then forbids
no earlier state) or, under parity, its row lies in the span of the rows before the round (IMPLIED).
"""
from __future__ import annotations

from collections import defaultdict

from pysat.solvers import Solver

PIECE_LIMIT = 22
DIRECT_LIMIT = 12


# ------------------------------------------------------------------------------------------------- peeling and cores
class Peel:
    """The global peeling of a structure: knots removed in order, each with the column that was its own when removed.
    core0: the knots that cannot be removed.  Used to find, for a set I of forbidden columns, the knots that cannot be
    removed when the columns of I may not be used (dev 15: exact)."""

    def __init__(self, places, holders, knots):
        self.places, self.holders = places, holders
        alive = set(knots)
        cnt = {}
        for u in alive:
            for d in places[u]:
                cnt[d] = cnt.get(d, 0) + 1
        # count holders among the knots considered (a view may list later holders; they are not in `knots`)
        order = {}
        witness = {}
        stack = []
        for u in sorted(alive, reverse=True):
            for d in places[u]:
                if cnt[d] == 1:
                    stack.append((u, d))
                    break
        removed = set()
        k = 0
        while stack:
            u, d = stack.pop()
            if u in removed:
                continue
            if cnt.get(d) != 1:
                # find another column of u held by it alone
                d = next((e for e in places[u] if cnt[e] == 1), None)
                if d is None:
                    continue
            removed.add(u)
            order[u] = k
            witness[u] = d
            k += 1
            for e in places[u]:
                cnt[e] -= 1
                if cnt[e] == 1:
                    for w in holders[e]:
                        if w in alive and w not in removed:
                            stack.append((w, e))
        self.alive = alive
        self.order = order
        self.witness = witness
        self.core0 = alive - removed

    def core(self, I, keep=()):
        """The knots that cannot be removed when columns in I may not be used and the knots in `keep` stay."""
        I = set(I)
        places, holders, alive, order, wit = self.places, self.holders, self.alive, self.order, self.witness
        reach = set()
        stack = [w for w in keep if w in alive]
        for d in I:
            for w in holders[d]:
                if w in alive and wit.get(w) == d:
                    stack.append(w)
        while stack:
            x = stack.pop()
            if x in reach:
                continue
            reach.add(x)
            ox = order.get(x, -1)
            for c in places[x]:
                for w in holders[c]:
                    if w in alive and w not in reach and wit.get(w) == c and order.get(w, -1) > ox:
                        stack.append(w)
        cand = set(self.core0) | reach
        # peel within the candidates (knots outside them are removed)
        cnt = {}
        for u in cand:
            for d in places[u]:
                if d not in I:
                    cnt[d] = cnt.get(d, 0) + 1
        keep = set(keep)
        removed = set()
        stack = [u for u in cand if u not in keep and any(cnt.get(d) == 1 for d in places[u] if d not in I)]
        while stack:
            u = stack.pop()
            if u in removed or u in keep:
                continue
            if not any(cnt.get(d) == 1 for d in places[u] if d not in I):
                continue
            removed.add(u)
            for d in places[u]:
                if d in I:
                    continue
                cnt[d] -= 1
                if cnt[d] == 1:
                    for w in holders[d]:
                        if w in cand and w not in removed:
                            stack.append(w)
        return cand - removed


def knots_upto(S, t):
    """Knots of S made by round t (ids are in birth order)."""
    n = 0
    while n < len(S.made) and S.made[n] <= t:
        n += 1
    return n


def holders_upto(S, nk):
    """holders restricted to knots < nk (a view without copying, as lists)."""
    return [[w for w in hs if w < nk] if (hs and hs[-1] >= nk) else hs for hs in S.holders]


# ----------------------------------------------------------------------------------------------------------- GF(2)
def gf2_rank(vectors):
    piv = {}
    r = 0
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            b = piv.get(p)
            if b is None:
                piv[p] = v
                r += 1
                break
            v ^= b
    return r


def rank_difference(places, knots, cols_removed):
    """rank(H) - rank(H without the columns in cols_removed), H the rows of `knots` (columns = distinctions)."""
    rows_full = []
    rows_cut = []
    cr = set(cols_removed)
    # compress column indices for speed
    cols = sorted({d for u in knots for d in places[u]})
    idx = {d: i for i, d in enumerate(cols)}
    for u in knots:
        a = b = 0
        for d in places[u]:
            a |= 1 << idx[d]
            if d not in cr:
                b |= 1 << idx[d]
        rows_full.append(a)
        rows_cut.append(b)
    return gf2_rank(rows_full) - gf2_rank(rows_cut)


# --------------------------------------------------------------------------------------------------- parity: ranks
def parity_ranks_at_birth(S, peels):
    """For every knot u: the ranks method at u's birth round m on the structure after round m (knots made after m
    are absent), after peeling (exact).  peels[m] is the Peel of the structure after round m.  Returns {u: rank diff}."""
    out = {}
    for u in range(S.n_knots):
        m = S.made[u]
        pl = peels[m]
        K = pl.core(S.places[u], keep=(u,))
        out[u] = rank_difference(S.places, sorted(K), S.places[u])
    return out


# -------------------------------------------------------------------------------------------------- parity: kernel
class Kernel:
    """A basis of the allowed states (parity), one bit column per distinction: col[d] has bit i when basis vector i is
    1 at d.  Built knot by knot in birth order; a knot with a fresh distinction extends every vector; a knot whose
    places hold no fresh distinction cuts the basis by its syndrome (none when its row lies in the span)."""

    def __init__(self):
        self.col = {}
        self.nvec = 0
        self.cuts = []

    def start(self, S, knots):
        """Kernel of the start structure by elimination: free columns give the basis."""
        dists = sorted({d for u in knots for d in S.places[u]})
        idx = {d: i for i, d in enumerate(dists)}
        piv = {}            # pivot column index -> row (bit set over column indices), fully reduced
        for u in knots:
            v = 0
            for d in S.places[u]:
                v ^= 1 << idx[d]
            for p, r in piv.items():
                if (v >> p) & 1:
                    v ^= r
            if not v:
                continue
            p = (v & -v).bit_length() - 1
            for q in list(piv):
                if (piv[q] >> p) & 1:
                    piv[q] ^= v
            piv[p] = v
        free = [i for i in range(len(dists)) if i not in piv]
        col = {d: 0 for d in dists}
        for j, f in enumerate(free):
            col[dists[f]] |= 1 << j
            for p, r in piv.items():
                if (r >> f) & 1:
                    col[dists[p]] |= 1 << j
        self.col = col
        self.nvec = len(free)

    def add_knot(self, places, fresh, round_):
        col = self.col
        if fresh:
            for f in fresh:
                col[f] = 0
            f1 = fresh[0]
            acc = 0
            for d in places:
                if d != f1:
                    if d in fresh:
                        col[d] = 1 << self.nvec
                        self.nvec += 1
                    acc ^= col[d]
            col[f1] = acc
            return
        syn = 0
        for d in places:
            syn ^= col[d]
        if syn:
            j = (syn & -syn).bit_length() - 1
            for d in col:
                if (col[d] >> j) & 1:
                    col[d] ^= syn
            self.cuts.append(round_)

    def proj_rank(self, places):
        return gf2_rank([self.col[d] for d in places])


def parity_kernel(S):
    """{u: rank of the projection of the allowed states onto u's places}, at the last round (equal to every round from
    u's birth when no cut happens after round 0: columns of earlier distinctions never change, dev 15)."""
    K = Kernel()
    ns = S.n_start
    K.start(S, list(range(ns)))
    for u in range(ns, S.n_knots):
        fresh = [d for d in S.places[u] if S.holders[d][0] == u]
        K.add_knot(S.places[u], fresh, S.made[u])
    return {u: K.proj_rank(S.places[u]) for u in range(S.n_knots)}, K.cuts


# ------------------------------------------------------------------------------------------------- not-all-equal
def _nae_clauses(sat, places_list):
    for P in places_list:
        vs = [d + 1 for d in P]
        sat.add_clause(vs)
        sat.add_clause([-v for v in vs])


def pieces_free(S_places, holders, K, I, limit=PIECE_LIMIT):
    """Whether every assignment of I extends to an allowed state (not-all-equal) of the knots K.  Pieces of K linked by
    distinctions outside I; per piece, every assignment of the distinctions of I it touches (half, by flipping all).
    True / False / None (a piece touches more than `limit` of I: untested)."""
    I = set(I)
    parent = {u: u for u in K}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    first = {}
    for u in K:
        for d in S_places[u]:
            if d in I:
                continue
            q = first.get(d)
            if q is None:
                first[d] = u
            else:
                a, b = find(q), find(u)
                if a != b:
                    parent[b] = a
    groups = defaultdict(list)
    for u in K:
        groups[find(u)].append(u)
    for piece in groups.values():
        touched = sorted({d for u in piece for d in S_places[u] if d in I})
        if len(touched) > limit:
            return None
        sat = Solver(name='minisat22')
        try:
            _nae_clauses(sat, [S_places[u] for u in piece])
            if not touched:
                if not sat.solve():
                    return False
                continue
            m = len(touched)
            for mask in range(1 << (m - 1)):
                assum = [(d + 1) if (mask >> i) & 1 else -(d + 1) for i, d in enumerate(touched)]
                if not sat.solve(assumptions=assum):
                    return False
        finally:
            sat.delete()
    return True


def nae_birth(S, peels):
    """The birth method for every knot made after round 0: {u: True/False/None}."""
    out = {}
    for u in range(S.n_start, S.n_knots):
        m = S.made[u]
        pl = peels[m - 1]
        fresh = set(d for d in S.places[u] if S.holders[d][0] == u)
        I = [d for d in S.places[u] if d not in fresh]
        K = pl.core(I)
        out[u] = pieces_free(S.places, pl.holders, K, I)
    return out


class NaeDirect:
    def __init__(self, places_list):
        self.sat = Solver(name='minisat22')
        _nae_clauses(self.sat, places_list)
        self.calls = 0

    def close(self):
        self.sat.delete()

    def passes(self, P):
        m = len(P)
        full = (1 << m) - 1
        # half of the assignments suffice (flipping every distinction maps allowed states to allowed states)
        for mask in range(1 << (m - 1)):
            assum = [(d + 1) if (mask >> i) & 1 else -(d + 1) for i, d in enumerate(P)]
            self.calls += 1
            ext = self.sat.solve(assumptions=assum)
            constant = mask == 0 or mask == full
            if ext == constant:
                return False
        return True


def nae_direct_at(S, t, knots=None, limit=DIRECT_LIMIT):
    """The direct test on the structure after round t, for knots (made by t) of at most `limit` places."""
    nk = knots_upto(S, t)
    sv = NaeDirect([S.places[u] for u in range(nk)])
    try:
        ks = range(nk) if knots is None else [u for u in knots if u < nk]
        return {u: sv.passes(S.places[u]) for u in ks if len(S.places[u]) <= limit}, sv.calls
    finally:
        sv.close()


# ------------------------------------------------------------------------------------------------------------ brute
def _popcount(x):
    import numpy as np
    x = x - ((x >> 1) & 0x55555555)
    x = (x & 0x33333333) + ((x >> 2) & 0x33333333)
    x = (x + (x >> 4)) & 0x0F0F0F0F
    return ((x * 0x01010101) & 0xFFFFFFFF) >> 24


def brute(places_list, law):
    """{index: passes} by every assignment of every distinction (at most 22), vectorised."""
    import numpy as np
    dists = sorted({d for P in places_list for d in P})
    idx = {d: i for i, d in enumerate(dists)}
    D = len(dists)
    assert D <= 22
    a = np.arange(1 << D, dtype=np.int64)
    ok = np.ones(1 << D, dtype=bool)
    rows = []
    for P in places_list:
        r = 0
        for d in P:
            r |= 1 << idx[d]
        rows.append(r)
        x = a & r
        if law == 'parity':
            ok &= (_popcount(x) & 1) == 0
        else:
            ok &= (x != 0) & (x != r)
    al = a[ok]
    out = {}
    for i, r in enumerate(rows):
        proj = np.unique(al & r)
        m = bin(r).count('1')
        if law == 'parity':
            out[i] = len(proj) == (1 << (m - 1)) and bool(np.all((_popcount(proj) & 1) == 0))
        else:
            out[i] = len(proj) == (1 << m) - 2 and not bool(np.any(proj == 0)) and not bool(np.any(proj == r))
    return out


def brute_slow(places_list, law):
    """{index: passes} by every assignment of every distinction (at most 22)."""
    dists = sorted({d for P in places_list for d in P})
    idx = {d: i for i, d in enumerate(dists)}
    D = len(dists)
    assert D <= 22
    rows = []
    for P in places_list:
        r = 0
        for d in P:
            r |= 1 << idx[d]
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
            elif x == 0 or x == r:
                ok = False
                break
        if ok:
            allowed.append(a)
    out = {}
    for i, r in enumerate(rows):
        proj = {a & r for a in allowed}
        m = bin(r).count('1')
        if law == 'parity':
            out[i] = len(proj) == (1 << (m - 1)) and all(bin(x).count('1') % 2 == 0 for x in proj)
        else:
            out[i] = len(proj) == (1 << m) - 2 and 0 not in proj and r not in proj
    return out


# ----------------------------------------------------------------------------------------------- a run's knot test
def extension_ok(S, records, law):
    """Every round extends (SD line 140): every birth has a fresh distinction or (parity) is IMPLIED.  Returns the list
    of rounds that might not extend (none expected)."""
    bad = []
    for rec in records:
        for b in rec['births']:
            if b['f'] == 0 and not (law.knot_law == 'parity' and b['implied']):
                bad.append(rec['round'])
                break
    return bad


def make_peels(S, rounds):
    out = {}
    for m in rounds:
        nk = knots_upto(S, m)
        H = holders_upto(S, nk)
        out[m] = Peel(S.places, H, range(nk))
    return out


def test_run(S, records, law, only_after=None, direct_rounds='last', clock=None):
    """The knot test of one run (structure S after its last round, its records).

    Parity: ranks (at the birth round, peeled) and kernel (at the last round), compared; every round extends.
    Not-all-equal: birth method for every knot made after round 0 (start knots directly at round 0); the direct test on
    every knot of at most 12 places at the rounds in direct_rounds ('last', 'every' or a list), compared.
    only_after: test only knots made after that round (comparison runs; earlier knots keep run A's verdicts)."""
    T = S.round
    out = {'verdicts': 0, 'fails': [], 'disagree': [], 'untested': [], 'compared': 0,
           'extension_bad': extension_ok(S, records, law), 'cuts': []}
    lo = -1 if only_after is None else only_after
    ks = [u for u in range(S.n_knots) if S.made[u] > lo]
    if law.knot_law == 'parity':
        need = sorted({S.made[u] for u in ks})
        peels = make_peels(S, need)
        rk = {}
        for u in ks:
            m = S.made[u]
            K = peels[m].core(S.places[u], keep=(u,))
            rk[u] = rank_difference(S.places, sorted(K), S.places[u])
            if clock is not None and len(rk) % 200 == 0:
                clock.check()
        ke, cuts = parity_kernel(S)
        out['cuts'] = cuts
        for u in ks:
            a = rk[u] == 1
            b = ke[u] == len(S.places[u]) - 1
            out['verdicts'] += 1
            out['compared'] += 1
            if a != b:
                out['disagree'].append({'knot': u, 'methods': 'ranks/kernel', 'ranks': rk[u], 'kernel': ke[u]})
            if not a:
                out['fails'].append(_row(S, u, 'parity'))
        out['rounds'] = 'birth round (ranks), last round (kernel); every round by extension'
        return out
    # not-all-equal
    need = sorted({S.made[u] - 1 for u in ks if S.made[u] >= 1})
    peels = make_peels(S, need)
    birth = {}
    for u in ks:
        m = S.made[u]
        if m == 0:
            continue
        pl = peels[m - 1]
        fresh = set(d for d in S.places[u] if S.holders[d][0] == u)
        I = [d for d in S.places[u] if d not in fresh]
        K = pl.core(I)
        birth[u] = pieces_free(S.places, pl.holders, K, I)
        if clock is not None and len(birth) % 200 == 0:
            clock.check()
    start_ks = [u for u in ks if S.made[u] == 0]
    direct0 = nae_direct_at(S, 0, start_ks, limit=10 ** 6)[0] if start_ks else {}
    if direct_rounds == 'last':
        drounds = [T]
    elif direct_rounds == 'every':
        drounds = list(range(T + 1))
    else:
        drounds = list(direct_rounds)
    direct = {}
    for t in drounds:
        dt, _ = nae_direct_at(S, t, ks)
        direct[t] = dt
        if clock is not None:
            clock.check()
    for u in ks:
        v = birth.get(u) if S.made[u] > 0 else direct0.get(u)
        if v is None:
            out['untested'].append({'knot': u, 'places': len(S.places[u]), 'method': 'birth'})
        for t in drounds:
            dv = direct[t].get(u)
            if dv is not None and v is not None:
                out['compared'] += 1
                if dv != v:
                    out['disagree'].append({'knot': u, 'round': t, 'methods': 'birth/direct', 'birth': v,
                                            'direct': dv})
        verdict = v
        if verdict is None:
            verdict = direct[T].get(u) if T in direct else None
        if verdict is None:
            continue
        out['verdicts'] += 1
        if not verdict:
            out['fails'].append(_row(S, u, 'nae'))
    out['rounds'] = 'birth method at the birth round; direct at %s' % (direct_rounds if isinstance(direct_rounds, str)
                                                                         else 'rounds %s' % drounds)
    return out


def _row(S, u, how):
    return {'knot': u, 'places': len(S.places[u]), 'parents': len(S.parents[u]), 'made': S.made[u],
            'kind': S.kind[u], 'how': how}


def literal_every_round(S, law, clock=None):
    """Both methods applied literally at every round, on the structure after that round, without peeling or the
    incremental kernel: the check of the shortcuts on small runs (dev 15)."""
    T = S.round
    out = {'rounds': T + 1, 'verdicts': 0, 'fails': [], 'disagree': []}
    for t in range(T + 1):
        nk = knots_upto(S, t)
        H = holders_upto(S, nk)
        ks = list(range(nk))
        if law.knot_law == 'parity':
            ke = _kernel_full(S.places, ks)
            for u in ks:
                a = rank_difference(S.places, ks, S.places[u]) == 1
                b = ke[u] == len(S.places[u]) - 1
                out['verdicts'] += 1
                if not a:
                    out['fails'].append({'round': t, 'knot': u})
                if a != b:
                    out['disagree'].append({'round': t, 'knot': u})
        else:
            sv = NaeDirect([S.places[u] for u in ks])
            try:
                for u in ks:
                    if len(S.places[u]) <= DIRECT_LIMIT:
                        v = sv.passes(S.places[u])
                        out['verdicts'] += 1
                        if not v:
                            out['fails'].append({'round': t, 'knot': u})
            finally:
                sv.close()
        if clock is not None:
            clock.check()
    return out


def _kernel_full(places, ks):
    dists = sorted({d for u in ks for d in places[u]})
    idx = {d: i for i, d in enumerate(dists)}
    piv = {}
    for u in ks:
        v = 0
        for d in places[u]:
            v ^= 1 << idx[d]
        for p, r in piv.items():
            if (v >> p) & 1:
                v ^= r
        if not v:
            continue
        p = (v & -v).bit_length() - 1
        for q in list(piv):
            if (piv[q] >> p) & 1:
                piv[q] ^= v
        piv[p] = v
    free = [i for i in range(len(dists)) if i not in piv]
    colv = [0] * len(dists)
    for j, f in enumerate(free):
        colv[f] |= 1 << j
        for p, r in piv.items():
            if (r >> f) & 1:
                colv[p] |= 1 << j
    return {u: gf2_rank([colv[idx[d]] for d in places[u]]) for u in ks}
