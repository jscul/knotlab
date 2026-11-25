"""The growing end (KD 5): exact counts of allowed states under not-all-equal by contraction, the pair readings kappa,
gamma and rho in integers, enumeration for checks N and I, the history weighting, arrival delay, strata, the order
comparisons, the member shuffle and the pair shuffle, L-W and betweenness.

Counting.  Under a taking-free law every shared distinction has two holders.  A knot u with shared places S_u and
lambda_u loose places (usable and barred) contributes, after its loose places are summed, the weight
    w_u(x) = 2^lambda_u - [x_{S_u} all 0] - [x_{S_u} all 1]     (S_u empty: 2^lambda_u - 2),
so the number of allowed states is Z = sum over the shared distinctions of prod_u w_u.  Sums are computed by variable
elimination on residues modulo primes below 2^31 (numpy int64; every product of two residues is below 2^62) and rebuilt
exactly by the Chinese remainder theorem with enough primes for 4Z (R 13).  Nothing is rounded.

Pair readings.  For members u, v (one loose distinction a of u and b of v), with Z00 = the sum with S_u and S_v pinned
all 0 and Z01 = the sum with S_u all 0 and S_v all 1, the sum over states of g_u g_v is 2(Z00 - Z01) by the global flip
(gamma Z); splitting the sum for N(a != b) by linearity over the loose places gives
    N(a != b) = (Z - gamma Z / ((2^lambda_u - 1)(2^lambda_v - 1))) / 2,
an integer (checked on every pair).  rho = N/Z, kappa = 1 - 2 rho.  Check I compares Z, gamma Z and N with enumeration
of every state on every stage of at most 20 distinctions; check N compares Lemma N with enumeration there (R 14).
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction

import numpy as np

# primes below 2^31 (largest first)
PRIMES = []


def _primes():
    if PRIMES:
        return PRIMES
    from sympy import prevprime
    p = 2 ** 31
    while len(PRIMES) < 40:
        p = prevprime(p)
        PRIMES.append(p)
    return PRIMES


MAX_WIDTH = 23


class WidthExceeded(Exception):
    pass


class StageCount:
    """The weighted sums of one structure S (taking-free, at most two holders), knots < N."""

    def __init__(self, S, N=None, nd=None):
        self.S = S
        N = S.n_knots if N is None else N
        nd = S.n_distinctions if nd is None else nd
        self.N, self.nd = N, nd
        var = {}
        self.shared = {}      # knot -> sorted list of variable indices
        self.lam = {}         # knot -> loose count (usable + barred)
        for u in range(N):
            sh, lam = [], 0
            for d in S.places[u]:
                hh = [w for w in S.holders[d] if w < N]
                if len(hh) >= 2:
                    assert len(hh) == 2, 'more than two holders: not a taking-free structure'
                    sh.append(var.setdefault(d, len(var)))
                else:
                    lam += 1
            self.shared[u] = sorted(sh)
            self.lam[u] = lam
        self.var_of = var
        self.V = len(var)
        primes = _primes()
        need = nd + 4
        k = 1
        prod = primes[0]
        while prod.bit_length() <= need:
            prod *= primes[k]
            k += 1
        self.P = np.array(primes[:k], dtype=np.int64)
        self.M = prod
        self.order = self._order()

    def _order(self):
        """Greedy elimination order (least degree, then least fill) on the variables' interaction graph."""
        nb = {v: set() for v in range(self.V)}
        for u, sh in self.shared.items():
            for a in sh:
                nb[a].update(b for b in sh if b != a)
        left = set(range(self.V))
        order = []
        while left:
            def key(v):
                ns = nb[v] & left
                fill = 0
                L = list(ns)
                for i in range(len(L)):
                    for j in range(i + 1, len(L)):
                        if L[j] not in nb[L[i]]:
                            fill += 1
                return (len(ns), fill, v)
            v = min(left, key=key)
            ns = nb[v] & left
            for a in ns:
                nb[a].update(b for b in ns if b != a)
            left.discard(v)
            order.append(v)
        return order

    def _factor(self, u, pins, override=None):
        """(free vars, table) of knot u's weight with the pinned variables substituted (residues, shape (k,2,..,2)).
        override: (alpha, beta0, beta1) for w = alpha - beta0 [all 0] - beta1 [all 1]."""
        sh = self.shared[u]
        lam = self.lam[u]
        alpha, b0, b1 = override if override is not None else (2 ** lam, 1, 1)
        free = [v for v in sh if v not in pins]
        pv = [pins[v] for v in sh if v in pins]
        can0 = all(x == 0 for x in pv)
        can1 = all(x == 1 for x in pv)
        P = self.P
        shape = (len(P),) + (2,) * len(free)
        T = np.empty(shape, dtype=np.int64)
        T[...] = (alpha % P).reshape((len(P),) + (1,) * len(free))
        if can0:
            idx = (slice(None),) + (0,) * len(free)
            T[idx] = (T[idx] - b0) % P
        if can1:
            idx = (slice(None),) + (1,) * len(free)
            T[idx] = (T[idx] - b1) % P
        return free, T

    def contract(self, pins=None, overrides=None):
        """The exact sum over the free shared variables of the product of the knots' weights (pinned variables fixed).
        Returns a Python int (signed by the CRT range)."""
        pins = pins or {}
        overrides = overrides or {}
        P = self.P
        k = len(P)
        factors = []
        scalar = np.ones(k, dtype=np.int64)
        for u in range(self.N):
            free, T = self._factor(u, pins, overrides.get(u))
            if not free:
                scalar = (scalar * T) % P
            else:
                factors.append((tuple(free), T))
        buckets = {}
        pos = {v: i for i, v in enumerate(self.order)}
        for f in factors:
            first = min(f[0], key=lambda v: pos[v])
            buckets.setdefault(first, []).append(f)
        for v in self.order:
            if v in pins:
                continue
            fs = buckets.pop(v, [])
            if not fs:
                scalar = (scalar * 2) % P      # a free variable no knot holds (not reached)
                continue
            U = sorted(set().union(*[set(f[0]) for f in fs]), key=lambda x: pos[x])
            if len(U) > MAX_WIDTH:
                raise WidthExceeded(len(U))
            Uix = {x: i for i, x in enumerate(U)}
            acc = None
            for vars_, T in fs:
                # bring T's axes into U's order
                perm = sorted(range(len(vars_)), key=lambda i: Uix[vars_[i]])
                Tt = np.transpose(T, [0] + [1 + i for i in perm])
                shape = [k] + [1] * len(U)
                for i in perm:
                    shape[1 + Uix[vars_[i]]] = 2
                Tt = Tt.reshape(shape)
                acc = Tt if acc is None else (acc * Tt) % P.reshape((k,) + (1,) * len(U))
            acc = np.broadcast_to(acc, (k,) + (2,) * len(U)) if acc.ndim == len(U) + 1 else acc
            ax = 1 + Uix[v]
            red = acc.sum(axis=ax) % P.reshape((k,) + (1,) * (len(U) - 1))
            rest = tuple(x for x in U if x != v)
            if not rest:
                scalar = (scalar * red) % P
            else:
                first = rest[0]
                buckets.setdefault(first, []).append((rest, red))
        return self._crt([int(x) for x in scalar])

    def _crt(self, res):
        M = self.M
        x = 0
        for r, p in zip(res, [int(p) for p in self.P]):
            Mi = M // p
            x = (x + r * Mi * pow(Mi, -1, p)) % M
        if x > M // 2:
            x -= M
        return x

    def Z(self):
        if not hasattr(self, '_Z'):
            self._Z = self.contract()
        return self._Z

    def pair(self, u, v):
        """(gamma Z, N(a != b)) for members u, v."""
        Su, Sv = self.shared[u], self.shared[v]
        pins00 = {x: 0 for x in Su}
        pins00.update({x: 0 for x in Sv})
        Z00 = self.contract(pins00)
        conflict = bool(set(Su) & set(Sv))
        if conflict:
            Z01 = 0
        else:
            pins01 = {x: 0 for x in Su}
            pins01.update({x: 1 for x in Sv})
            Z01 = self.contract(pins01)
        gZ = 2 * (Z00 - Z01)
        Du, Dv = 2 ** self.lam[u] - 1, 2 ** self.lam[v] - 1
        Z = self.Z()
        num = Z * Du * Dv - gZ
        den = 2 * Du * Dv
        assert num % den == 0, 'N(a != b) not an integer: %r / %r' % (num, den)
        return gZ, num // den

    def direct_N(self, u, v):
        """N(a = 0, b = 1) + N(a = 1, b = 0) by contraction with a and b explicit (weights pinned on a, b); for checks."""
        lu, lv = self.lam[u], self.lam[v]
        # w_u with a = 0: 2^(l-1) - [all 0]; with a = 1: 2^(l-1) - [all 1]
        o = {u: (2 ** (lu - 1), 1, 0), v: (2 ** (lv - 1), 0, 1)}
        n01 = self.contract(overrides=o)
        o = {u: (2 ** (lu - 1), 0, 1), v: (2 ** (lv - 1), 1, 0)}
        n10 = self.contract(overrides=o)
        return n01 + n10


# ------------------------------------------------------------------------------------------------- enumeration
def enumerate_states(S, N=None, nd=None):
    """Every assignment of the distinctions < nd; the allowed ones under not-all-equal (knots < N).  nd <= 22."""
    N = S.n_knots if N is None else N
    nd = S.n_distinctions if nd is None else nd
    assert nd <= 22
    x = np.arange(1 << nd, dtype=np.int64)
    ok = np.ones(len(x), dtype=bool)
    for u in range(N):
        m = 0
        for d in S.places[u]:
            m |= 1 << d
        y = x & m
        ok &= (y != 0) & (y != m)
    return x[ok]


def enum_pair(S, allowed, u, v, a, b, N=None):
    """(Z, gamma Z, N(a != b)) by enumeration."""
    Nn = S.n_knots if N is None else N

    def g(w):
        sh = [d for d in S.places[w] if len([h for h in S.holders[d] if h < Nn]) >= 2]
        m = 0
        for d in sh:
            m |= 1 << d
        y = allowed & m
        return (y == 0).astype(np.int64) - (y == m).astype(np.int64)
    gz = int(np.sum(g(u) * g(v)))
    neq = int(np.sum(((allowed >> a) ^ (allowed >> b)) & 1))
    return len(allowed), gz, neq


def loose_of(S, u, N=None):
    Nn = S.n_knots if N is None else N
    return sorted(d for d in S.places[u] if len([h for h in S.holders[d] if h < Nn]) == 1)


# ------------------------------------------------------------------------------------------ the history weighting
def history_weights(snaps_alloweds, nds):
    """mu_t over the allowed states of the last stage (KD 5.2): mu_0 uniform on the start's allowed states;
    mu_t(x) = mu_{t-1}(x')/n_t(x').  snaps_alloweds: allowed-state arrays for rounds 0..t; nds: distinction counts.
    Returns (numerators as an object array aligned with the last allowed array, common denominator)."""
    A0 = snaps_alloweds[0]
    num = np.ones(len(A0), dtype=object)
    den = len(A0)
    prev, prev_num = A0, num
    for t in range(1, len(snaps_alloweds)):
        A = snaps_alloweds[t]
        mask = (1 << nds[t - 1]) - 1
        xr = A & mask
        # n_t(x') for each x' and mu_{t-1}(x') looked up
        uniq, inv, cnt = np.unique(xr, return_inverse=True, return_counts=True)
        idx = np.searchsorted(prev, uniq)
        assert np.all(prev[idx] == uniq), 'a later allowed state restricts to a state not allowed before'
        if len(uniq) != len(prev):
            raise AssertionError('a round does not extend (some earlier allowed state has no extension)')
        L = 1
        for c in set(int(c) for c in cnt):
            L = L * c // math.gcd(L, c)
        pn = prev_num[idx]
        new = np.empty(len(A), dtype=object)
        for i in range(len(A)):
            new[i] = pn[inv[i]] * (L // int(cnt[inv[i]]))
        den = den * L
        prev, prev_num = A, new
    return prev_num, den


# --------------------------------------------------------------------------------------------- comparisons
def order_counts(X, Y, mask_pairs=None):
    """Concordant, discordant and tied comparisons over pairs of items (strength X: larger = more strongly related;
    nearness Y: larger = sooner / fewer steps).  X, Y: integer rank arrays.  mask_pairs: boolean matrix of the
    comparisons to count (nested strata)."""
    X = np.asarray(X)
    Y = np.asarray(Y)
    n = len(X)
    if n < 2:
        return 0, 0, 0
    sx = np.sign(X[:, None] - X[None, :])
    sy = np.sign(Y[:, None] - Y[None, :])
    iu = np.triu_indices(n, 1)
    prod = (sx * sy)[iu]
    tie = (sx[iu] == 0) | (sy[iu] == 0)
    if mask_pairs is not None:
        m = mask_pairs[iu]
        prod, tie = prod[m], tie[m]
    return int(np.sum(prod > 0)), int(np.sum(prod < 0)), int(np.sum(tie))


def dense_rank(values):
    """Exact dense ranks of comparable values (ints or Fractions): equal values share a rank."""
    srt = sorted(set(values))
    pos = {v: i for i, v in enumerate(srt)}
    return [pos[v] for v in values]


def kendall_var_pair_shuffle(X, Y):
    """Var(S) when Y is permuted uniformly among the items (ties in both), exact Fraction (the pair shuffle)."""
    n = len(X)
    if n < 3:
        return Fraction(0)
    from collections import Counter
    tx = [c for c in Counter(X).values() if c > 1]
    ty = [c for c in Counter(Y).values() if c > 1]
    v0 = n * (n - 1) * (2 * n + 5)
    vt = sum(t * (t - 1) * (2 * t + 5) for t in tx)
    vu = sum(u * (u - 1) * (2 * u + 5) for u in ty)
    v1 = Fraction(sum(t * (t - 1) * (t - 2) for t in tx) * sum(u * (u - 1) * (u - 2) for u in ty),
                  9 * n * (n - 1) * (n - 2))
    v2 = Fraction(sum(t * (t - 1) for t in tx) * sum(u * (u - 1) for u in ty), 2 * n * (n - 1))
    return Fraction(v0 - vt - vu, 18) + v1 + v2


def shuffle_S(pairs, Xrank, ykey, parts, rng=None, exact_limit=40320, draws=2000):
    """The member shuffle (KD 5.7): within each part, permutations of the part's members applied to the key; X fixed.
    pairs: list of (u, v) within parts; Xrank: strength ranks per pair; ykey: dict (u, v) -> nearness value or None
    (undecided; a comparison needs both decided).  Exact over the product of the parts' permutation groups when its
    size is at most exact_limit, otherwise `draws` draws (R 16).  Returns (S values array, exact flag)."""
    members = sorted({u for p in pairs for u in p})
    mi = {u: i for i, u in enumerate(members)}
    n = len(members)
    Pn = len(pairs)
    if Pn < 2:
        return np.zeros(1, dtype=np.int64), True
    # nearness table over member index pairs (both orders), sentinel for undecided
    NEG = -10 ** 9
    Ytab = np.full((n, n), NEG, dtype=np.int64)
    for (u, v), y in ykey.items():
        if u in mi and v in mi and y is not None:
            Ytab[mi[u], mi[v]] = y
            Ytab[mi[v], mi[u]] = y
    pu = np.array([mi[u] for u, v in pairs])
    pv = np.array([mi[v] for u, v in pairs])
    Xr = np.asarray(Xrank)
    # pairs in increasing X; the first index of each pair's group of equal X (strictly smaller X lies before it)
    order = np.argsort(Xr, kind='stable')
    Xs = Xr[order]
    gstart = np.searchsorted(Xs, Xs, side='left')
    # nearness categories
    vals = sorted({int(y) for y in Ytab.ravel() if y != NEG})
    cat = {y: i for i, y in enumerate(vals)}
    Kc = max(1, len(vals))
    Ctab = np.full((n, n), -1, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            if Ytab[i, j] != NEG:
                Ctab[i, j] = cat[int(Ytab[i, j])]
    part_members = [[mi[u] for u in P if u in mi] for P in parts]
    part_members = [p for p in part_members if len(p) >= 2]
    size = 1
    for p in part_members:
        size *= math.factorial(len(p))
        if size > exact_limit:
            break
    perms_list = []
    exact = size <= exact_limit
    if exact:
        per_part = [list(itertools.permutations(p)) for p in part_members]
        for combo in itertools.product(*per_part):
            perm = np.arange(n)
            for p, img in zip(part_members, combo):
                perm[p] = img
            perms_list.append(perm)
    else:
        for _ in range(draws):
            perm = np.arange(n)
            for p in part_members:
                img = list(p)
                rng.shuffle(img)
                perm[p] = img
            perms_list.append(perm)
    out = np.empty(len(perms_list), dtype=np.int64)
    B = 512
    for s in range(0, len(perms_list), B):
        PM = np.array(perms_list[s:s + B])
        C = Ctab[PM[:, pu], PM[:, pv]][:, order]          # (b, Pn) categories in increasing X, -1 undecided
        b = C.shape[0]
        onehot = np.zeros((b, Pn, Kc), dtype=np.int64)
        dec = C >= 0
        bi, pi = np.nonzero(dec)
        onehot[bi, pi, C[bi, pi]] = 1
        cum = np.cumsum(onehot, axis=1)                    # inclusive prefix over pairs in X order
        cum = np.concatenate([np.zeros((b, 1, Kc), dtype=np.int64), cum], axis=1)
        less = cum[:, gstart, :]                           # counts over pairs with strictly smaller X
        cl = np.cumsum(less, axis=2)                       # by category
        tot = cl[:, :, -1]
        cc = np.where(dec, C, 0)
        below = np.where(cc > 0, np.take_along_axis(cl, np.maximum(cc - 1, 0)[:, :, None], axis=2)[:, :, 0], 0)
        upto = np.take_along_axis(cl, cc[:, :, None], axis=2)[:, :, 0]
        above = tot - upto
        out[s:s + B] = np.sum(np.where(dec, below - above, 0), axis=1)
    return out, exact
