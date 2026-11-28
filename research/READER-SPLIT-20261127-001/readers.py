"""readers.py: do the odd birth choices split into separated readers? (READER-SPLIT-20261127-001; README.md, frozen
predictions G, P1-P6).

A birth choice (LOCAL-COMMUTE-20261127-001) is a set of failing pairs with every two knots' checks commuting. A split
of an odd birth choice is a set of disjoint readers (sets of distinctions) with (i) every failing pair inside one reader
and (ii) no knot holding two distinctions of one reader. A split is strict when the failing pairs are disjoint (each
reader holds exactly two values, which fail to commute). For each closure: the fewest readers in a strict split (exact
integer program, cross-checked by satisfiability), whether a split of either kind exists (satisfiability with a
same-reader relation), the fewest readers in any split (satisfiability with r labels), the fewest failing pairs among
odd birth choices (P6), enumeration of small codes, and a certificate for each split: a realization local to the
readers and the readers' game of certainty (README, items 5 and 6).
    readers.py [--limit N] [--enum 14] [--out DIR]
Writes results.jsonl, census_types.jsonl, fixtures.json, gates.json and summary.json next to this file.
"""
import argparse
import itertools
import json
import resource
import sys
import threading
import time
from pathlib import Path

import numpy as np
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, lil_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LC = ROOT / "research" / "LOCAL-COMMUTE-20261127-001"
sys.path.insert(0, str(LC))
sys.path.insert(0, str(ROOT / "research" / "FORBID-EDITS-20261126-001"))
import forbid  # noqa: E402  (the archived ordinary engine)
import local_commute as lc  # noqa: E402  (Structure: holders, decidable pairs, rows, cost)

TIME = 60          # seconds per integer program or satisfiability call
MAX_READERS = 12   # the label search stops here


class Unsettled(Exception):
    pass


def popcount(x):
    return bin(x).count("1")


# ---------------------------------------------------------------- the code of a closure

class Code:
    """Birth (or whole) choices over `pairs`: one parity check per pair of knots, the interleaving cost, holders."""

    def __init__(self, st, pairs):
        self.st = st
        self.pairs = list(pairs)
        self.n = len(self.pairs)
        rows, _ = st.rows(self.pairs)
        self.H = [r for r in rows.values() if r]
        self.cost = st.cost(self.pairs)
        self.knots = st.knots
        self.D = st.D
        self.at = {d: [j for j, p in enumerate(self.pairs) if d in p] for d in range(self.D)}
        self.coheld = set()
        for k in self.knots:
            for a, b in itertools.combinations(sorted(k), 2):
                self.coheld.add((a, b))
        self.unheld = set(st.unheld)

    def is_word(self, w):
        return all(popcount(r & w) % 2 == 0 for r in self.H)

    def sign(self, w):
        return popcount(self.cost & w) % 2

    def failing(self, w):
        return [self.pairs[j] for j in range(self.n) if (w >> j) & 1]


def is_strict(code, w):
    return all(popcount(w & sum(1 << j for j in code.at[d])) <= 1 for d in range(code.D))


def components(F):
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in F:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    groups = {}
    for a in list(parent):
        groups.setdefault(find(a), set()).add(a)
    return list(groups.values())


def splits_by_components(code, F):
    """the finest readers (the groups of failing pairs) satisfy condition (ii)"""
    groups = components(F)
    owner = {d: i for i, g in enumerate(groups) for d in g}
    for k in code.knots:
        seen = set()
        for d in k:
            if d in owner:
                if owner[d] in seen:
                    return None
                seen.add(owner[d])
    return groups


def fewest_labels(code, groups):
    """the fewest readers into which the groups can be merged under (ii): exact colouring of their conflict graph"""
    m = len(groups)
    owner = {d: i for i, g in enumerate(groups) for d in g}
    conflict = [set() for _ in range(m)]
    for k in code.knots:
        gs = sorted({owner[d] for d in k if d in owner})
        for a, b in itertools.combinations(gs, 2):
            conflict[a].add(b)
            conflict[b].add(a)
    for r in range(1, m + 1):
        colour = [-1] * m
        order = sorted(range(m), key=lambda i: -len(conflict[i]))

        def place(t):
            if t == m:
                return True
            i = order[t]
            for c in range(r):
                if all(colour[j] != c for j in conflict[i]):
                    colour[i] = c
                    if place(t + 1):
                        return True
                    colour[i] = -1
            return False
        if place(0):
            return r
    return m


# ---------------------------------------------------------------- exact integer programs

def program(code, strict=False, nonmatching=False):
    """Fewest failing pairs in an odd birth choice; with `strict`, the failing pairs disjoint; with `nonmatching`, some
    distinction in two failing pairs. Returns (weight, word) or None if there is none; raises Unsettled."""
    n, H, m = code.n, code.H, len(code.H)
    ds = [d for d in range(code.D) if len(code.at[d]) >= 2]
    nz = len(ds) if nonmatching else 0
    nv = n + m + 1 + nz
    rows = m + 1 + (len(ds) if strict else 0) + (nz + 1 if nonmatching else 0)
    A = lil_matrix((rows, nv))
    lo, hi = [], []
    for i, r in enumerate(H):
        for j in range(n):
            if (r >> j) & 1:
                A[i, j] = 1
        A[i, n + i] = -2
        lo.append(0)
        hi.append(0)
    for j in range(n):
        if (code.cost >> j) & 1:
            A[m, j] = 1
    A[m, n + m] = -2
    lo.append(1)
    hi.append(1)
    t = m + 1
    if strict:
        for d in ds:
            for j in code.at[d]:
                A[t, j] = 1
            lo.append(-np.inf)
            hi.append(1)
            t += 1
    if nonmatching:
        for q, d in enumerate(ds):          # sum over d's pairs >= 2 z_d
            for j in code.at[d]:
                A[t, j] = 1
            A[t, n + m + 1 + q] = -2
            lo.append(0)
            hi.append(np.inf)
            t += 1
        for q in range(nz):
            A[t, n + m + 1 + q] = 1
        lo.append(1)
        hi.append(np.inf)
        t += 1
    c = np.zeros(nv)
    c[:n] = 1.0
    upper = np.concatenate([np.ones(n), [popcount(r) // 2 for r in H], [popcount(code.cost) // 2], np.ones(nz)])
    if not ds and nonmatching:
        return None
    res = milp(c, constraints=LinearConstraint(csr_matrix(A), lo, hi), integrality=np.ones(nv),
               bounds=Bounds(np.zeros(nv), upper), options={"mip_rel_gap": 0, "time_limit": TIME})
    if res.status == 2:
        return None
    if res.status != 0:
        raise Unsettled(res.message)
    x = np.round(res.x[:n]).astype(int)
    w = sum(1 << j for j in range(n) if x[j])
    assert code.is_word(w) and code.sign(w) == 1, "an optimum is not an odd birth choice"
    if strict:
        assert is_strict(code, w)
    if nonmatching:
        assert not is_strict(code, w)
    return int(x.sum()), w


# ---------------------------------------------------------------- satisfiability

class Cnf:
    def __init__(self, nvars):
        self.top = nvars
        self.clauses = []

    def new(self):
        self.top += 1
        return self.top

    def xor(self, lits, value):
        """exclusive-or of lits equals value, as a chain"""
        if not lits:
            if value:
                self.clauses.append([])
            return
        acc = lits[0]
        for v in lits[1:]:
            t = self.new()
            self.clauses += [[-t, acc, v], [-t, -acc, -v], [t, -acc, v], [t, acc, -v]]
            acc = t
        self.clauses.append([acc] if value else [-acc])

    def solve(self):
        with Solver(name="cadical153", bootstrap_with=self.clauses) as s:
            timer = threading.Timer(TIME, s.interrupt)
            timer.start()
            ok = s.solve_limited(expect_interrupt=True)
            timer.cancel()
            if ok is None:
                raise Unsettled("satisfiability call interrupted")
            return ok, (s.get_model() if ok else None)


def parity_clauses(code, cnf):
    """x_j is variable j + 1; every check even, the closing sign odd"""
    for r in code.H:
        cnf.xor([j + 1 for j in range(code.n) if (r >> j) & 1], 0)
    cnf.xor([j + 1 for j in range(code.n) if (code.cost >> j) & 1], 1)


def word_of(code, model):
    pos = set(v for v in model if v > 0)
    return sum(1 << j for j in range(code.n) if j + 1 in pos)


def sat_strict(code):
    cnf = Cnf(code.n)
    parity_clauses(code, cnf)
    for d in range(code.D):
        lits = [j + 1 for j in code.at[d]]
        if len(lits) >= 2:
            enc = CardEnc.atmost(lits=lits, bound=1, top_id=cnf.top, encoding=EncType.seqcounter)
            cnf.top = max(cnf.top, enc.nv)
            cnf.clauses += enc.clauses
    ok, model = cnf.solve()
    if not ok:
        return None
    w = word_of(code, model)
    assert code.is_word(w) and code.sign(w) == 1 and is_strict(code, w)
    return w


def sat_general(code):
    """a split of either kind: a same-reader relation y on unheld pairs of candidate distinctions"""
    cnf = Cnf(code.n)
    parity_clauses(code, cnf)
    cand = sorted({d for p in code.pairs for d in p})
    y = {}
    for a, b in itertools.combinations(cand, 2):
        if (a, b) in code.unheld:
            y[(a, b)] = cnf.new()

    def Y(a, b):
        return y.get((min(a, b), max(a, b)))
    for j, (a, b) in enumerate(code.pairs):
        cnf.clauses.append([-(j + 1), Y(a, b)])
    for u, v, w in itertools.combinations(cand, 3):
        for a, mid, b in ((u, v, w), (v, u, w), (u, w, v)):
            p, q, r = Y(a, mid), Y(mid, b), Y(a, b)
            if p is None or q is None:
                continue
            cnf.clauses.append([-p, -q, r] if r is not None else [-p, -q])
    ok, model = cnf.solve()
    if not ok:
        return None
    w = word_of(code, model)
    F = code.failing(w)
    groups = splits_by_components(code, F)
    assert code.is_word(w) and code.sign(w) == 1 and groups is not None, "a split that fails (ii)"
    return w


def sat_readers(code, r):
    """a split of either kind with at most r readers (labels)"""
    cnf = Cnf(code.n)
    parity_clauses(code, cnf)
    cand = sorted({d for p in code.pairs for d in p})
    lab = {(d, c): cnf.new() for d in cand for c in range(r)}
    used = {d: cnf.new() for d in cand}
    for d in cand:
        xs = [j + 1 for j in code.at[d]]
        cnf.clauses.append([-used[d]] + xs)                  # used -> some failing pair at d
        for x in xs:
            cnf.clauses.append([-x, used[d]])
        cnf.clauses.append([-used[d]] + [lab[(d, c)] for c in range(r)])
        for c1, c2 in itertools.combinations(range(r), 2):
            cnf.clauses.append([-lab[(d, c1)], -lab[(d, c2)]])
        for c in range(r):
            cnf.clauses.append([used[d], -lab[(d, c)]])
    for j, (a, b) in enumerate(code.pairs):
        for c in range(r):
            cnf.clauses += [[-(j + 1), -lab[(a, c)], lab[(b, c)]], [-(j + 1), -lab[(b, c)], lab[(a, c)]]]
    for (a, b) in code.coheld:
        if a in used and b in used:
            for c in range(r):
                cnf.clauses.append([-lab[(a, c)], -lab[(b, c)]])
    ok, model = cnf.solve()
    if not ok:
        return None
    w = word_of(code, model)
    pos = set(v for v in model if v > 0)
    readers = {}
    for (d, c), v in lab.items():
        if v in pos:
            readers.setdefault(c, set()).add(d)
    readers = list(readers.values())
    assert code.is_word(w) and code.sign(w) == 1 and len(readers) <= r
    return w, readers


# ---------------------------------------------------------------- enumeration of small codes

def nullspace(code):
    """basis of the words (bit masks over the pairs) with every check even"""
    piv = {}
    for r in code.H:
        while r:
            h = r.bit_length() - 1
            if h in piv:
                r ^= piv[h]
            else:
                piv[h] = r
                break
    # reduce to echelon form with pivots eliminated from other rows
    keys = sorted(piv)
    for h in keys:
        for g in keys:
            if g != h and (piv[g] >> h) & 1:
                piv[g] ^= piv[h]
    free = [j for j in range(code.n) if j not in piv]
    basis = []
    for f in free:
        w = 1 << f
        for h, r in piv.items():
            if (r >> f) & 1:
                w |= 1 << h
        basis.append(w)
    return basis


def enumerate_code(code):
    basis = nullspace(code)
    out = {"free choices": len(basis), "odd words": 0, "strict": False, "fewest strict": None, "general": False,
           "fewest readers": None, "fewest odd": None, "every fewest odd is strict": None, "strict odd words": 0,
           "strict sizes": []}
    w = 0
    fewest_odd = None
    strict_at_fewest = True
    sizes = set()
    memo = {}
    for i in range(1, 1 << len(basis)):
        w ^= basis[(i & -i).bit_length() - 1]
        if not code.sign(w):
            continue
        out["odd words"] += 1
        wt = popcount(w)
        st = is_strict(code, w)
        if fewest_odd is None or wt < fewest_odd:
            fewest_odd, strict_at_fewest = wt, st
        elif wt == fewest_odd:
            strict_at_fewest = strict_at_fewest and st
        if st:
            out["strict"] = True
            out["strict odd words"] += 1
            sizes.add(wt)
            if out["fewest strict"] is None or wt < out["fewest strict"]:
                out["fewest strict"] = wt
        groups = splits_by_components(code, code.failing(w))
        if groups is not None:
            out["general"] = True
            out["odd choices with a split"] = out.get("odd choices with a split", 0) + 1
            shape = tuple(sorted(len(g) for g in groups))
            out.setdefault("their group sizes", set()).add(shape)
            key = frozenset(frozenset(g) for g in groups)
            if key not in memo:
                memo[key] = fewest_labels(code, groups)
            if out["fewest readers"] is None or memo[key] < out["fewest readers"]:
                out["fewest readers"] = memo[key]
    out["fewest odd"] = fewest_odd
    out["every fewest odd is strict"] = strict_at_fewest if fewest_odd is not None else None
    out["strict sizes"] = sorted(sizes)
    out["their group sizes"] = sorted(out.get("their group sizes", set()))
    out.setdefault("odd choices with a split", 0)
    return out


# ---------------------------------------------------------------- the certificate (README items 5 and 6)

def pmul(p, q):
    """i^a X^x Z^z times i^b X^u Z^v"""
    x, z, a = p
    u, v, b = q
    return (x ^ u, z ^ v, (a + b + 2 * popcount(z & u)) % 4)


def commute(p, q):
    return (popcount(p[0] & q[1]) + popcount(p[1] & q[0])) % 2 == 0


def orderfree_sign(code, F):
    T = {}
    for a, b in F:
        for u in code.st.holders[a]:
            for v in code.st.holders[b]:
                T[(u, v)] = T.get((u, v), 0) ^ 1
    symmetric = all(T.get((u, v), 0) == T.get((v, u), 0) for (u, v) in T)
    return symmetric, sum(1 for (u, v), t in T.items() if t and u < v) % 2


def certificate(code, w, readers):
    """Realization local to the readers and the readers' game; every entry must be True."""
    F = code.failing(w)
    fail = {(min(a, b), max(a, b)) for a, b in F}
    owner = {d: i for i, g in enumerate(readers) for d in g}
    out = {}
    out["every failing pair inside one reader"] = all(a in owner and b in owner and owner[a] == owner[b] for a, b in F)
    out["no knot holds two values of one reader"] = all(
        len([d for d in k if d in owner]) == len({owner[d] for d in k if d in owner}) for k in code.knots)
    D = code.D
    val = []
    for d in range(D):
        z = 0
        if d in owner:
            for e in readers[owner[d]]:
                if e < d and (e, d) in fail:
                    z |= 1 << e
        val.append((1 << d, z, 0))
    qubits = [sum(1 << e for e in readers[owner[d]]) if d in owner else 1 << d for d in range(D)]
    out["values local to their readers"] = all(((x | z) & ~qubits[d]) == 0 for d, (x, z, _) in enumerate(val))
    out["values fail exactly on the failing pairs"] = all(
        commute(val[a], val[b]) == ((a, b) not in fail) for a, b in itertools.combinations(range(D), 2))
    checks = []
    for k in code.knots:
        p = (0, 0, 0)
        for d in sorted(k):
            p = pmul(p, val[d])
        checks.append(p)
    out["checks Hermitian"] = all(a % 2 == popcount(x & z) % 2 for x, z, a in checks)
    out["checks commute"] = all(commute(p, q) for p, q in itertools.combinations(checks, 2))
    prod = (0, 0, 0)
    for p in checks:
        prod = pmul(prod, p)
    sym, ofs = orderfree_sign(code, F)
    out["product of checks is -1"] = prod == (0, 0, 2)
    out["interleaving cost odd"] = code.sign(w) == 1
    out["order-free count symmetric and odd"] = sym and ofs == 1
    # only the whole product as a dependency: rank K - 1
    vecs = [(x << D) | z for x, z, _ in checks]
    piv = {}
    for v in vecs:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                break
    out["only the whole product as a dependency"] = len(piv) == len(checks) - 1
    # the readers' game: old checks at +1, values outside readers at signs found greedily
    basis = {}                                    # pivot bit -> signed Pauli taken as +1 in the state

    def reduce(p):
        x, z, a = p
        acc = (x, z, a)
        while acc[0] or acc[1]:
            v = (acc[0] << D) | acc[1]
            h = v.bit_length() - 1
            if h not in basis:
                return acc, h
            acc = pmul(acc, basis[h])
        return acc, None
    for p in checks[:-1]:
        r, h = reduce(p)
        assert h is not None, "old checks are independent"
        basis[h] = r
    signs = {}
    for d in range(D):
        if d in owner:
            continue
        r, h = reduce(val[d])
        if h is None:
            assert r[2] in (0, 2)
            signs[d] = 1 if r[2] == 0 else -1
        else:
            basis[h] = r
            signs[d] = 1
    rclose, hclose = reduce(checks[-1])
    out["closing check is -1 in the state"] = hclose is None and rclose[2] == 2
    parts, values = [], []
    for u, k in enumerate(code.knots):
        p = checks[u]
        s = 1 if u < len(code.knots) - 1 else -1
        for d in sorted(k):
            if d not in owner:
                p = pmul(p, val[d])
                s *= signs[d]
        parts.append(p)
        values.append(s)
    reader_qubits = sum(1 << d for d in owner)
    out["reader parts act on readers' qubits only"] = all(((x | z) & ~reader_qubits) == 0 for x, z, _ in parts)
    rp = (0, 0, 0)
    for p in parts:
        rp = pmul(rp, p)
    out["reader parts multiply to -1"] = rp == (0, 0, 2)
    out["their values multiply to -1"] = int(np.prod(values)) == -1
    # each reader part is definite: its value times the operator reduces to +1 (as a product of stabilizers)
    ok = True
    for p, s in zip(parts, values):
        r, h = reduce(p)
        ok = ok and h is None and r[2] in (0, 2) and ((r[2] == 0) == (s == 1))
    out["reader parts definite with those values"] = ok
    return out


# ---------------------------------------------------------------- four mutually meeting knots

def four_meeting(code, decidable):
    """(any four mutually meeting knots, any such four with a decidable pair in each of their three pairings)"""
    st = code.st
    meet = {}
    for d, h in st.holders.items():
        if len(h) == 2:
            meet.setdefault(tuple(sorted(h)), []).append(d)
    K = len(st.knots)
    adj = {u: set() for u in range(K)}
    for u, v in meet:
        adj[u].add(v)
        adj[v].add(u)
    anyfour = False
    good = False
    for quad in itertools.combinations(range(K), 4):
        if not all(b in adj[a] for a, b in itertools.combinations(quad, 2)):
            continue
        anyfour = True
        a, b, c, d = quad
        ok = True
        for (p, q), (r, s) in (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))):
            ok = ok and any((min(x, y), max(x, y)) in decidable
                            for x in meet[(p, q)] for y in meet[(r, s)])
        if ok:
            good = True
            break
    return anyfour, good


def odd_rings(code, decidable, longest=9):
    """The shortest odd ring r_1..r_n of knots that one knot h meets in full (each r_i meeting r_{i+1}) whose split
    pairs (s_j, e_{j+(n-1)/2}) have decidable representatives (README, item 1); None if there is none."""
    st = code.st
    meet = {}
    for d, h in st.holders.items():
        if len(h) == 2:
            meet.setdefault(tuple(sorted(h)), []).append(d)
    K = len(st.knots)
    adj = {u: set() for u in range(K)}
    for u, v in meet:
        adj[u].add(v)
        adj[v].add(u)

    def ms(u, v):
        return meet.get((min(u, v), max(u, v)), [])

    def decidable_ring(h, ring):
        n = len(ring)
        half = (n - 1) // 2
        for j in range(n):
            a, b = ring[(j + half) % n], ring[(j + half + 1) % n]
            if not any((min(s, e), max(s, e)) in decidable for s in ms(h, ring[j]) for e in ms(a, b)):
                return False
        return True

    def cycles(nodes, L):
        """simple cycles of length L in the meeting graph restricted to nodes, each once (least node first)"""
        nodes = sorted(nodes)
        for s in nodes:
            stack = [(s, [s])]
            while stack:
                v, path = stack.pop()
                if len(path) == L:
                    if s in adj[v] and path[1] < path[-1]:
                        yield path
                    continue
                for w in adj[v]:
                    if w in nodes and w > s and w not in path:
                        stack.append((w, path + [w]))

    for L in range(3, longest + 1, 2):
        for h in range(K):
            if len(adj[h]) < L:
                continue
            for ring in cycles(adj[h], L):
                if decidable_ring(h, ring):
                    return L
    return None


# ---------------------------------------------------------------- one closure

def study(code, label, enum_limit, decidable=None):
    row = {"name": label, "knots": len(code.knots), "largest knot": max(len(k) for k in code.knots),
           "positions": code.n}
    decidable = set(code.pairs) if decidable is None else decidable
    row["four mutually meeting knots"], row["four meeting with decidable pairings"] = four_meeting(code, decidable)
    row["shortest odd ring around a knot"] = odd_rings(code, decidable)
    try:
        fs = program(code, strict=True)
        sw = sat_strict(code)
        row["strict"] = fs is not None
        row["strict: integer program and satisfiability agree"] = (fs is not None) == (sw is not None)
        row["fewest strict readers"] = fs[0] if fs else None
        gw = sat_general(code) if fs is None else (fs[1] if fs else None)
        row["general"] = gw is not None
        if fs is not None:
            g2 = sat_general(code)
            row["general check where strict exists"] = g2 is not None
        fewest = None
        witness = None
        if row["general"]:
            for r in range(1, MAX_READERS + 1):        # from one reader, so a split with fewer than three would show
                got = sat_readers(code, r)
                if got:
                    fewest, witness = r, got
                    break
            if fewest is None:
                raise Unsettled(f"more than {MAX_READERS} readers")
            row["fewest readers: smaller counts excluded"] = fewest - 1
        row["fewest readers"] = fewest
        po = program(code)
        pn = program(code, nonmatching=True)
        row["fewest failing pairs, odd"] = po[0] if po else None
        row["fewest failing pairs, odd, not strict"] = pn[0] if pn else None
        row["every fewest odd is strict"] = (po is not None and fs is not None and fs[0] == po[0]
                                             and (pn is None or pn[0] > po[0]))
        certs = {}
        if fs is not None:
            F = code.failing(fs[1])
            certs["strict"] = certificate(code, fs[1], [set(p) for p in F])
            row["strict readers"] = [list(p) for p in F]
        if gw is not None:
            groups = splits_by_components(code, code.failing(gw))
            certs["general"] = certificate(code, gw, groups)
        if witness is not None:
            certs["fewest readers"] = certificate(code, witness[0], witness[1])
            row["fewest readers' sizes"] = sorted(len(g) for g in witness[1])
        row["certificates pass"] = all(all(c.values()) for c in certs.values())
        if not row["certificates pass"]:
            row["certificate failures"] = {k: [n for n, v in c.items() if not v] for k, c in certs.items()}
    except Unsettled as e:
        row["unsettled"] = str(e)
        return row
    if enum_limit is not None:
        dim = len(nullspace(code))
        row["free choices"] = dim
        if dim <= enum_limit:
            e = enumerate_code(code)
            row["enumeration agrees"] = (e["strict"] == row["strict"] and e["fewest strict"] == row["fewest strict readers"]
                                         and e["general"] == row["general"]
                                         and e["fewest readers"] == row["fewest readers"]
                                         and e["fewest odd"] == row["fewest failing pairs, odd"]
                                         and e["every fewest odd is strict"] == row["every fewest odd is strict"])
            row["strict odd choices"] = e["strict odd words"]
            row["strict sizes"] = e["strict sizes"]
            row["odd choices with a split"] = e["odd choices with a split"]
            row["their group sizes"] = [list(s) for s in e["their group sizes"]]
    return row


# ---------------------------------------------------------------- fixtures and census types

def from_ends(ends):
    n = 1 + max(v for e in ends for v in e)
    return [tuple(i for i, e in enumerate(ends) if u in e) for u in range(n)]


def closed(knots):
    st = lc.Structure([tuple(knots)], [])
    assert all(len(h) == 2 for h in st.holders.values()), "a closed pattern holds every distinction twice"
    return st


def ring_closure(n):
    """ring knots 1..n, closing knot 0 meeting each once: spokes first, then ring meetings"""
    ends = [(0, j) for j in range(1, n + 1)] + [(j, j % n + 1) for j in range(1, n + 1)]
    return from_ends(ends)


FIXTURES = {
    "ring of four's closure": ring_closure(4),
    "ring of five's closure": ring_closure(5),
    "two rings of three joined knot to knot": from_ends([(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5),
                                                        (0, 3), (1, 4), (2, 5)]),
    "three knots each meeting each of three others": from_ends([(a, b) for a in range(3) for b in range(3, 6)]),
}


GROWN_FIXTURES = {
    # a start knot meeting four knots in a chain, one loose distinction at it and at the chain's two ends
    "ring of five's closure, grown": ((0, 1, 2, 3, 7), (0, 4, 8), (1, 4, 5), (2, 5, 6), (3, 6, 9)),
    # four knots meeting pairwise except one pair, each of that pair with one loose distinction
    "closure F, grown": ((0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 6)),
}


def fixtures(enum_limit):
    out = {}
    for name, knots in FIXTURES.items():
        st = closed(knots)
        code = Code(st, st.unheld)
        row = study(code, name, enum_limit)
        row["whole choices attain odd"] = lc.odd_attainable(st, st.unheld)
        if name == "ring of five's closure":       # item 1: meeting s_j with the ring meeting e_{j+2}
            spoke = {j: d for d, h in st.holders.items() for j in [h[1]] if h[0] == 0}
            ring = {}
            for d, h in st.holders.items():
                if 0 not in h:
                    a, b = h
                    ring[a if b == a % 5 + 1 else b] = d
            F = [(spoke[j], ring[(j + 1) % 5 + 1]) for j in range(1, 6)]
            w = sum(1 << code.pairs.index((min(a, b), max(a, b))) for a, b in F)
            row["construction is an odd strict split"] = code.is_word(w) and code.sign(w) == 1 and is_strict(code, w)
            row["construction certificate passes"] = all(certificate(code, w, [set(p) for p in F]).values())
        out[name] = row
    for name, start in GROWN_FIXTURES.items():
        stages, births, end = lc.grow(start, 4, 40)
        row = {"name": name, "end": end, "closing round": len(births)}
        if end == "closed" and births:
            st = lc.Structure(stages, births)
            code = Code(st, st.local)
            row.update(study(code, name, enum_limit, decidable=set(st.local)))
            row["outerplanar"] = lc.outerplanar(st.knots)
            row["birth choices attain odd"] = lc.odd_attainable(st, st.local)
        out[name] = row
    return out


def census_types(enum_limit):
    census = json.loads(lc.CENSUS.read_text())
    rows = []
    for i, t in enumerate(census):
        st = closed(from_ends([tuple(x) for x in t["sharing"]]))
        code = Code(st, st.unheld)
        if not lc.odd_attainable(st, st.unheld):
            rows.append({"type": i, "odd attainable": False})
            continue
        r = study(code, f"type {i}", enum_limit)
        r["type"] = i
        r["odd attainable"] = True
        rows.append(r)
    return rows


# ---------------------------------------------------------------- the grown closures

def population(limit=None):
    """the 1,177 closures where birth choices attain odd, and the 10 later ones where only whole choices do"""
    rows = [json.loads(l) for l in (LC / "results.jsonl").open()]
    closures = [r for r in rows if r["end"] == "closed" and not r.get("closed at round 0")]
    elig = [r for r in closures if r.get("birth choices attain odd")]
    lost = [r for r in closures if r["closing round"] >= 2 and r.get("whole choices attain odd")
            and not r.get("birth choices attain odd")]
    return elig[:limit], (lost if limit is None else [])


def gates(enum_limit):
    out = {}
    stages, births, end = lc.grow(lc.RING3, 4, 40)
    st = lc.Structure(stages, births)
    code = Code(st, st.local)
    row = study(code, "ring of three's closure", enum_limit)
    basis = nullspace(code)
    words = []
    w = 0
    for i in range(1, 1 << len(basis)):
        w ^= basis[(i & -i).bit_length() - 1]
        if code.sign(w):
            words.append(sorted(code.failing(w)))
    out["ring: the only odd birth choice is the readers' matching"] = words == [[(0, 4), (1, 5), (2, 3)]]
    out["ring: strict split with three readers"] = row.get("fewest strict readers") == 3
    out["ring: general search finds it"] = row.get("general") is True and row.get("fewest readers") == 3
    out["ring: certificates pass"] = row.get("certificates pass") is True
    return out, row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--enum", type=int, default=14)
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--skip-census", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    t0 = time.time()
    g, ring_row = gates(args.enum)
    starts = forbid.starts()
    rows = []
    elig, lost = population(args.limit)

    def whole(st, row):
        """whole choices (every unheld pair) at a later closure"""
        wcode = Code(st, st.unheld)
        try:
            ws = program(wcode, strict=True)
            row["whole: strict"] = ws is not None
            row["whole: fewest strict readers"] = ws[0] if ws else None
            row["whole: general"] = (ws is not None) or (sat_general(wcode) is not None)
        except Unsettled as e:
            row["whole: unsettled"] = str(e)

    with (out / "results.jsonl").open("w") as fh:
        for r in elig:
            stages, births, end = lc.grow(forbid.supports_of(starts[r["start"]]), 4, 40)
            st = lc.Structure(stages, births)
            code = Code(st, st.local)
            row = study(code, f"start {r['start']}", args.enum, decidable=set(st.local))
            row["start"] = r["start"]
            row["closing round"] = r["closing round"]
            if r["closing round"] >= 2:
                whole(st, row)
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
    lost_rows = []
    with (out / "whole_only.jsonl").open("w") as fh:
        for r in lost:
            stages, births, end = lc.grow(forbid.supports_of(starts[r["start"]]), 4, 40)
            st = lc.Structure(stages, births)
            row = {"start": r["start"], "closing round": r["closing round"], "knots": len(st.knots)}
            whole(st, row)
            lost_rows.append(row)
            fh.write(json.dumps(row) + "\n")
    fx = fixtures(args.enum)
    (out / "fixtures.json").write_text(json.dumps(fx, indent=1) + "\n")
    types = [] if args.skip_census else census_types(args.enum)
    with (out / "census_types.jsonl").open("w") as fh:
        for r in types:
            fh.write(json.dumps(r) + "\n")
    g.update(gate_summary(rows, types, fx))
    g.update(hand_results(rows, fx))
    (out / "gates.json").write_text(json.dumps(g, indent=1) + "\n")
    s = summarise(rows, types, lost_rows)
    s["seconds"] = round(time.time() - t0, 1)
    s["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (out / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps({"gates": g, "summary": s}, indent=1))


def gate_summary(rows, types, fx):
    allrows = rows + [t for t in types if t.get("odd attainable")] + list(fx.values())
    settled = [r for r in allrows if "unsettled" not in r]
    g = {}
    g["no search unsettled (count unsettled)"] = len(allrows) - len(settled)
    g["integer program and satisfiability agree on strict existence"] = all(
        r["strict: integer program and satisfiability agree"] for r in settled)
    g["every certificate passes"] = all(r["certificates pass"] for r in settled)
    en = [r for r in settled if "enumeration agrees" in r]
    g["enumeration agrees (closures enumerated)"] = [all(r["enumeration agrees"] for r in en), len(en)]
    g["where strict exists the general search agrees"] = all(r.get("general check where strict exists", True)
                                                            for r in settled)
    return g


def hand_results(rows, fx):
    """prediction H: the hand results of items 1-3 and 7, scored on the run"""
    ok = [r for r in rows if "unsettled" not in r]
    h = {}
    ring = [r for r in ok if r["shortest odd ring around a knot"] is not None]
    h["H item 1: closures with an odd ring around a knot (decidable)"] = len(ring)
    h["H item 1: each has a strict split with at most that many readers"] = all(
        r["strict"] and r["fewest strict readers"] <= r["shortest odd ring around a knot"] for r in ring)
    h["H item 2: no split with fewer than three readers"] = all(
        (r["fewest readers"] is None or r["fewest readers"] >= 3)
        and (r["fewest strict readers"] is None or r["fewest strict readers"] >= 3) for r in ok)
    small = [r for r in ok if r["largest knot"] <= 3]
    h["H item 3: closures whose knots hold at most three distinctions"] = len(small)
    h["H item 3: strict split only on four knots"] = all((not r["strict"]) or r["knots"] == 4 for r in small)
    f = {k: v for k, v in fx.items()}

    def get(name, key):
        return f.get(name, {}).get(key)
    c5 = "ring of five's closure"
    h["H item 7: ring of five's closure: fewest strict readers five, the construction the only strict odd choice"] = (
        get(c5, "fewest strict readers") == 5 and get(c5, "strict odd choices") == 1
        and get(c5, "construction is an odd strict split") is True and get(c5, "construction certificate passes") is True)
    g5 = "ring of five's closure, grown"
    h["H item 7: grown ring of five's closure: closes in round 1, no four mutually meeting knots, fewest strict five"] = (
        get(g5, "end") == "closed" and get(g5, "closing round") == 1 and get(g5, "four mutually meeting knots") is False
        and get(g5, "fewest strict readers") == 5)
    c4 = "ring of four's closure"
    h["H item 7: ring of four's closure: odd, no split of either kind"] = (
        get(c4, "whole choices attain odd") is True and get(c4, "strict") is False and get(c4, "general") is False)
    jr = "two rings of three joined knot to knot"
    h["H item 7: joined rings: no strict split, exactly two odd splits of three readers holding three values"] = (
        get(jr, "strict") is False and get(jr, "general") is True and get(jr, "fewest readers") == 3
        and get(jr, "odd choices with a split") == 2 and get(jr, "their group sizes") == [[3, 3, 3]])
    k33 = "three knots each meeting each of three others"
    h["H item 7: three by three: odd under whole choices, no split of either kind"] = (
        get(k33, "whole choices attain odd") is True and get(k33, "strict") is False and get(k33, "general") is False)
    fF = "closure F, grown"
    h["H item 7: closure F: grown, not outerplanar, odd, no split of either kind"] = (
        get(fF, "end") == "closed" and get(fF, "outerplanar") is False and get(fF, "birth choices attain odd") is True
        and get(fF, "strict") is False and get(fF, "general") is False)
    return h


def tally(rows, key=None):
    out = {}
    for r in rows:
        if "unsettled" in r:
            kind = "unsettled"
        elif r["strict"]:
            kind = "strict"
        elif r["general"]:
            kind = "general only"
        else:
            kind = "neither"
        k = "all" if key is None else str(key(r))
        out.setdefault(k, {"strict": 0, "general only": 0, "neither": 0, "unsettled": 0})[kind] += 1
    return out


def summarise(rows, types, lost_rows):
    s = {"closures": len(rows)}
    s["splits"] = tally(rows)
    s["by closing round"] = tally(rows, lambda r: r["closing round"])
    s["by four mutually meeting knots"] = tally(rows, lambda r: r["four mutually meeting knots"])
    s["by shortest odd ring around a knot"] = tally(rows, lambda r: r["shortest odd ring around a knot"])
    s["by largest knot"] = tally(rows, lambda r: r["largest knot"])
    ok = [r for r in rows if "unsettled" not in r]
    strict = [r for r in ok if r["strict"]]
    s["P1 strict splits"] = len(strict)
    s["P1 of them without an odd ring around a knot"] = sum(r["shortest odd ring around a knot"] is None for r in strict)
    s["P1 of them whose fewest strict readers differs from the shortest ring"] = sum(
        r["shortest odd ring around a knot"] is not None
        and r["fewest strict readers"] != r["shortest odd ring around a knot"] for r in strict)
    s["P1 holds"] = s["P1 of them without an odd ring around a knot"] == 0 and \
        s["P1 of them whose fewest strict readers differs from the shortest ring"] == 0
    s["P2 splits of either kind but no strict split"] = sum(r["general"] and not r["strict"] for r in ok)
    s["P2 holds"] = s["P2 splits of either kind but no strict split"] > 0
    s["four meeting with decidable pairings"] = sum(r["four meeting with decidable pairings"] for r in ok)
    hist = {}
    for r in ok:
        if r["strict"]:
            hist.setdefault("strict", {}).setdefault(str(r["fewest strict readers"]), 0)
            hist["strict"][str(r["fewest strict readers"])] += 1
        if r["general"]:
            hist.setdefault("any", {}).setdefault(str(r["fewest readers"]), 0)
            hist["any"][str(r["fewest readers"])] += 1
    s["fewest readers"] = hist
    s["P4 every fewest odd birth choice is strict (closures)"] = sum(r["every fewest odd is strict"] for r in ok)
    s["P4 fewest odd below fewest strict (closures with a strict split)"] = sum(
        1 for r in strict if r["fewest failing pairs, odd"] < r["fewest strict readers"])
    s["P4 fewest failing pairs, odd"] = {}
    for r in ok:
        k = str(r["fewest failing pairs, odd"])
        s["P4 fewest failing pairs, odd"][k] = s["P4 fewest failing pairs, odd"].get(k, 0) + 1
    later = [r for r in ok if r["closing round"] >= 2]
    s["later closures (86): birth strict, whole strict"] = [sum(r["strict"] for r in later),
                                                           sum(r.get("whole: strict", False) for r in later)]
    s["later closures (86): birth either kind, whole either kind"] = [
        sum(r["general"] for r in later), sum(r.get("whole: general", False) for r in later)]
    s["later closures where birth choices lose the odd close (10): whole strict, whole either kind"] = [
        sum(r.get("whole: strict", False) for r in lost_rows), sum(r.get("whole: general", False) for r in lost_rows)]
    s["whole choices unsettled"] = sum(1 for r in later + lost_rows if "whole: unsettled" in r)
    tt = [t for t in types if t.get("odd attainable")]
    s["census types"] = len(types)
    s["census types attaining odd"] = len(tt)
    s["census types: splits"] = tally(tt)
    s["census types: by four mutually meeting knots"] = tally(tt, lambda r: r["four mutually meeting knots"])
    return s


if __name__ == "__main__":
    main()
