"""Influence through hidden copies (research/HIDDEN-COPY-20261112-001/preregistration.md, ticket A).

A harmony H (states W) and one of its kind sets give the one-order stitch R ⊆ W^3. A gadget is a set of stitches among three observed
copies and some hidden copies, every copy a state of H; its relation T ⊆ W^3 is the observed triples that some hidden states complete.
End(W; R): the maps W -> W keeping R; Aut: the bijective ones; G: the shifts and flips."""
import itertools
import random
import sys
from pathlib import Path

import numpy as np
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/BASES-WITHIN-20261112-001A/BASES-WITHIN-20261112-001A-P001_inner_series"))
sys.path.insert(0, str(ROOT / "proofs/LOOP-LOCK-20261112-001A/LOOP-LOCK-20261112-001A-P001_loop_locking"))
import nest_lib as N  # noqa: E402
import loop_lib as LL  # noqa: E402

H = N.H


def harmonies_with_kind_sets(max_span=8, max_period=16, max_states=36):
    """each harmony of period <= max_period with at most max_states states, with every kind set of 1 to 3 kinds and span <= max_span
    that presents it (the census's first one marked)"""
    seen = {}
    for Wsp in range(2, max_span + 1):
        for S in H.patterns(Wsp):
            st, cyc = H.classify(Wsp, S, "NAE")
            if st != "harmony":
                continue
            key = tuple(sorted(H.canon(c) for c in cyc))
            seen.setdefault(key, []).append([list(k) for k in S])
    out = []
    for key, kinds_list in seen.items():
        P = 1
        for w in key:
            P = P * len(w) // np.gcd(P, len(w))
        if P > max_period:
            continue
        h = {"orbits": ["".join(map(str, w)) for w in key], "kinds": kinds_list[0], "P": int(P)}
        if len(N.states(h)) > max_states:
            continue
        uniq = []
        for k in kinds_list:
            if k not in uniq:
                uniq.append(k)
        out.append({"orbits": h["orbits"], "P": int(P), "kind sets": uniq})
    return sorted(out, key=lambda h: (sum(len(o) for o in h["orbits"]), h["orbits"]))


def setup(orbits, P, kinds):
    h = {"orbits": orbits, "kinds": kinds, "P": P}
    W, R, T = LL.relation(h)
    mask = (1 << P) - 1
    index = {x: i for i, x in enumerate(W)}
    G = []
    for e in (0, 1):
        for a in range(P):
            G.append(tuple(index[LL.rot(x, a, P) ^ (mask if e else 0)] for x in W))
    G = sorted(set(G))
    return {"W": W, "R": set(R), "Rl": sorted(R), "G": G, "n": len(W)}


def _endo_solver(st, extra_clauses, nxt):
    n = st["n"]
    var = lambda u, v: u * n + v + 1
    cl = []
    for u in range(n):
        cl.append([var(u, v) for v in range(n)])
        for v in range(n):
            for v2 in range(v + 1, n):
                cl.append([-var(u, v), -var(u, v2)])
    return cl + extra_clauses, var


def _lazy(st, cl, var, max_rounds):
    """solve with R-preservation added lazily; returns (map or None, settled)"""
    n, R = st["n"], st["R"]
    by_xy = {}
    for (x, y, z) in R:
        by_xy.setdefault((x, y), []).append(z)
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        for _ in range(max_rounds):
            if not s.solve():
                return None, True
            m = set(l for l in s.get_model() if l > 0)
            f = [next(v for v in range(n) if var(u, v) in m) for u in range(n)]
            bad = None
            for (a, b, c) in st["Rl"]:
                if (f[a], f[b], f[c]) not in R:
                    bad = (a, b, c)
                    break
            if bad is None:
                return f, True
            a, b, c = bad
            s.add_clause([-var(a, f[a]), -var(b, f[b])] + [var(c, z) for z in by_xy.get((f[a], f[b]), [])])
    return None, False


def endo_large_witness(st, max_rounds=20000):
    """a non-injective, non-constant endomorphism, or None (and whether settled)"""
    n = st["n"]
    base, var = _endo_solver(st, [], 0)
    nxt = n * n + 1
    extra = []
    # non-injective: some pair u < u' with the same image
    pairs = []
    for u in range(n):
        for u2 in range(u + 1, n):
            for v in range(n):
                p = nxt
                nxt += 1
                pairs.append(p)
                extra += [[-p, var(u, v)], [-p, var(u2, v)]]
    extra.append(pairs)
    # non-constant: some u with image different from u = 0's image
    nc = []
    for u in range(1, n):
        for v in range(n):
            q = nxt
            nxt += 1
            nc.append(q)
            extra += [[-q, var(u, v)], [-q, -var(0, v)]]
    extra.append(nc)
    return _lazy(st, base + extra, var, max_rounds)


def aut_outside_G(st, blocked, max_rounds=20000):
    """a bijective endomorphism (an automorphism) not in the blocked list, or None"""
    n = st["n"]
    base, var = _endo_solver(st, [], 0)
    extra = []
    for v in range(n):
        extra.append([var(u, v) for u in range(n)])
    for g in blocked:
        extra.append([-var(u, g[u]) for u in range(n)])
    return _lazy(st, base + extra, var, max_rounds)


def automorphisms(st, cap=200):
    """G and every further automorphism found (up to cap); complete if the search ended"""
    found = list(st["G"])
    complete = True
    while len(found) < cap:
        f, settled = aut_outside_G(st, found)
        if not settled:
            complete = False
            break
        if f is None:
            break
        found.append(tuple(f))
    else:
        complete = False
    return found, complete


def orbits(n, perms):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for p in perms:
        for u in range(n):
            a, b = find(u), find(p[u])
            if a != b:
                parent[a] = b
    return len({find(u) for u in range(n)}), [find(u) for u in range(n)]


def essential_binary(st, max_rounds=20000):
    """a binary polymorphism depending on both arguments (lazy over pairs of stitch triples), or None"""
    n, R = st["n"], st["R"]
    var = lambda a, b, v: (a * n + b) * n + v + 1
    cl = []
    for a in range(n):
        for b in range(n):
            cl.append([var(a, b, v) for v in range(n)])
            for v in range(n):
                for v2 in range(v + 1, n):
                    cl.append([-var(a, b, v), -var(a, b, v2)])
    nxt = n * n * n + 1
    # depends on the second argument: f(a, b) != f(a, b') for some a, b, b'; and on the first likewise
    for side in (0, 1):
        sel = []
        for a in range(n):
            for b in range(n):
                for b2 in range(b + 1, n):
                    for v in range(n):
                        p = nxt
                        nxt += 1
                        sel.append(p)
                        if side == 0:
                            cl += [[-p, var(a, b, v)], [-p, -var(a, b2, v)]]
                        else:
                            cl += [[-p, var(b, a, v)], [-p, -var(b2, a, v)]]
        cl.append(sel)
    Rl = st["Rl"]
    by_xy = {}
    for (x, y, z) in R:
        by_xy.setdefault((x, y), []).append(z)
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        for _ in range(max_rounds):
            if not s.solve():
                return None, True
            m = set(l for l in s.get_model() if l > 0)
            f = {}
            for a in range(n):
                for b in range(n):
                    f[(a, b)] = next(v for v in range(n) if var(a, b, v) in m)
            bad = None
            for t1 in Rl:
                for t2 in Rl:
                    if (f[(t1[0], t2[0])], f[(t1[1], t2[1])], f[(t1[2], t2[2])]) not in R:
                        bad = (t1, t2)
                        break
                if bad:
                    break
            if bad is None:
                return f, True
            t1, t2 = bad
            x, y = f[(t1[0], t2[0])], f[(t1[1], t2[1])]
            s.add_clause([-var(t1[0], t2[0], x), -var(t1[1], t2[1], y)] + [var(t1[2], t2[2], z) for z in by_xy.get((x, y), [])])
    return None, False


def is_affine_x_minus_y_plus_z(st, f2):
    return None  # not used: an essential binary polymorphism is reported, and its kind examined after the run


# ---------------------------------------------------------------- gadgets

def gadget_relations(st, h_max=2, s_max=3):
    """every gadget with 3 observed copies (0, 1, 2), h <= h_max hidden copies and 1 to s_max stitches among distinct copies, each
    observed copy in some stitch; yields (h, stitches, T as a boolean w x w x w array)"""
    n = st["n"]
    Rt = np.zeros((n, n, n), dtype=np.int64)
    for (x, y, z) in st["R"]:
        Rt[x, y, z] = 1
    for h in range(1, h_max + 1):
        k = 3 + h
        triples = [t for t in itertools.permutations(range(k), 3)]
        letters = "abcdefg"[:k]
        for s in range(1, s_max + 1):
            for stitches in itertools.combinations(triples, s):
                used = {c for t in stitches for c in t}
                if not {0, 1, 2} <= used or len(used) < k:
                    continue
                expr = ",".join("".join(letters[c] for c in t) for t in stitches) + "->" + letters[:3]
                T = np.einsum(expr, *[Rt] * s, optimize=False) if s > 1 else None
                if s == 1:
                    continue
                yield h, stitches, T > 0


def factor_permutive_z2(st, T, cells):
    """readouts pi_1, pi_2, pi_3: W -> Z_2, constant on the given cells, each non-constant, with pi_1(u) + pi_2(v) + pi_3(w) the same for
    every (u, v, w) in T and every pair projection of T onto readout pairs full: a list of the solutions found (at most 4)"""
    n = st["n"]
    cid = sorted(set(cells))
    k = len(cid)
    idx = {c: j for j, c in enumerate(cid)}
    cell = [idx[c] for c in cells]
    pts = np.argwhere(T)
    if len(pts) == 0:
        return []
    # unknowns: x_1 (k), x_2 (k), x_3 (k), d; equations x_1[c(u)] + x_2[c(v)] + x_3[c(w)] + d = 0
    rows = set()
    for (u, v, w) in pts:
        r = (1 << cell[u]) ^ (1 << (k + cell[v])) ^ (1 << (2 * k + cell[w])) ^ (1 << (3 * k))
        rows.add(r)
    basis = nullspace(list(rows), 3 * k + 1)
    out = []
    for coeffs in itertools.product((0, 1), repeat=len(basis)):
        if len(basis) > 12:
            break
        x = 0
        for c, b in zip(coeffs, basis):
            if c:
                x ^= b
        pi = [[(x >> (j * k + cell[u])) & 1 for u in range(n)] for j in range(3)]
        if any(len(set(p)) < 2 for p in pi):
            continue
        full = True
        for (i, j) in ((0, 1), (0, 2), (1, 2)):
            seen = {(pi[i][t[i]], pi[j][t[j]]) for t in pts}
            if len(seen) < 4:
                full = False
                break
        if full:
            out.append(pi)
            if len(out) >= 4:
                break
    return out


def nullspace(eqs, N):
    piv = {}
    for e in eqs:
        for p, row in piv.items():
            if (e >> p) & 1:
                e ^= row
        if e:
            p = e.bit_length() - 1
            for q in list(piv):
                if (piv[q] >> p) & 1:
                    piv[q] ^= e
            piv[p] = e
    free = [c for c in range(N) if c not in piv]
    basis = []
    for f in free:
        x = 1 << f
        for p, row in piv.items():
            if (row >> f) & 1:
                x |= 1 << p
        basis.append(x)
    return basis


def random_relation(st, seed):
    """a random relation on W with the diagonal, invariant under G, with about as many triples as R: unions of G-orbits of W^3"""
    n = st["n"]
    rng = random.Random(seed)
    orb_of = {}
    orbs = []
    for t in itertools.product(range(n), repeat=3):
        if t in orb_of:
            continue
        o = {tuple(g[x] for x in t) for g in st["G"]}
        for x in o:
            orb_of[x] = len(orbs)
        orbs.append(o)
    diag = {(u, u, u) for u in range(n)}
    rel = set(diag)
    order = list(range(len(orbs)))
    rng.shuffle(order)
    for j in order:
        if len(rel) >= len(st["R"]):
            break
        rel |= orbs[j]
    return rel
