"""Checks for COPRIME-PAIRS-20261027-001E-P001 (interacting pair failures with a clean edge).

  1 Lemma 3 (Brunnian insertions): in the free group, cable_d([A12, A23]) with one bundle deleted fixes the other strands (bundle 0
    deleted: bundles 1, 2 fixed; bundles 1 and 2 deleted: bundle 0 fixed), d = 2..6
  2 Lemma 2 (zero-jump blocks): on amphichiral and cable summands, base and end colours are 0 and the reading strand is nonzero at
    every root character, copies equal the reading strand; under random pinned representations (layered, class 3) the end strand
    carries the base value and every copy the reading strand's value at every layer
  3 the clean-edge census: among the 176 interacting algebras of COPRIME-PAIRS-20261027-001C, 50 have a clean edge
  4 the 126 open algebras by their minimal sets of failing conditions (over every failing order, quotient option and hard pair);
    4 of them (one algebra up to coarsening) have no hard pair modulo gamma_3
  5 free class 3 on (1, 1) at d = 5, p = 11: the full single-edge matrix F (121 x 121, by exact polynomial interpolation of the
    equations on the gadget, then exhaustive counting): F(s, s) = F_max, F(0, D) < F_max for D != 0, rank F >= 2, rank F F^T >= 2
  6 the blocking conditions are real: on the single-edge gadget at the diagonal (all private data solve the private equations),
    the vertex equations are nonzero at most random points for a (K)-only and a (V3)-only algebra, and zero at every point for a
    (B2)-only algebra
  7 Theorem 5 on the census: with (B1'), (B2') (character 0 allowed) and (V3'), 5 more interacting algebras have a clean edge;
    the 121 still open, by minimal failing sets
  8 Theorem 5 on free class 3 on (0, 1, 4) at d = 5, p = 11: the clean edge uses a character-0 bracket; F(s, s) = F_max,
    F(0, D) < F_max, vertex pairings zero; on the path, with e1's data on its solution set, e0's solutions equal the single edge's
Run: python3 -B check.py [--write]"""
import glob, itertools, json, os, sys, time
import numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, glob.glob(os.path.join(ROOT, "experiments/COPRIME-PAIRS-20261027-001D/*E001_*"))[0])
sys.path.insert(1, glob.glob(os.path.join(ROOT, "proofs/COPRIME-PAIRS-20261027-001C/*P001_*"))[0])
from pf_lib import *  # noqa: E402  (read-only)
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:900], flush=True)


# ---------------------------------------------------------------- 1 Lemma 3
rows, ok = [], True
for d in range(2, 7):
    w = C.cable(mlib.X12_23, d)
    img = mlib.artin(w, 3 * d)
    bundles = [list(range(j * d, j * d + d)) for j in range(3)]

    def delete(word, dead):
        return mlib.red([g for g in word if g[0] not in dead])
    good0 = all(delete(img[q], set(bundles[0])) == [(q, 1)] for q in bundles[1] + bundles[2])
    good12 = all(delete(img[q], set(bundles[1] + bundles[2])) == [(q, 1)] for q in bundles[0])
    rows.append({"d": d, "bundle 0 deleted: others fixed": good0, "bundles 1, 2 deleted: bundle 0 fixed": good12})
    ok &= good0 and good12
report("1 Brunnian insertions", ok, rows)

# ---------------------------------------------------------------- 2 Lemma 2
rows, ok = [], True
for (p, d, slots) in [(11, 5, (1, 2)), (5, 4, (1, 2)), (7, 3, (1,)), (13, 4, (1, 2))]:
    T = summand_types(p, d, slots)
    zeta = root_of_unity(p, d)
    for i in range(len(slots)):
        w, n, roots, name = T[i]
        B = zero_jump_block(w, n, roots, zeta, p, 3)
        good = True
        for c in roots:
            v = class_vec(B.word, B.n, pow(zeta, c, p), p)
            r = B.tags.index("read"); cps = [q for q, t in enumerate(B.tags) if t == "copy"]
            good &= v is not None and v[0] % p == 0 and v[-1] % p == 0 and v[r] % p != 0 and all((v[q] - v[r]) % p == 0 for q in cps)
        # group level: random layered pinned lifts on the closed block braid for free class 3 on (roots[0], roots[0])
        L = free_graded(p, d, [roots[0], roots[0]], 3)
        A = BraidAlg(L, zeta)
        Mo = CyclicBraidModel(B.word, B.n, A, p)
        rng = np.random.default_rng(7)
        V = np.zeros((16, B.n, L.D), dtype=np.int64)
        okl = np.ones(16, dtype=bool)
        for lay in (1, 2, 3):
            Rr = Mo.run(V)
            for k in [k for k in range(L.D) if L.layer[k] == lay]:
                X, bad = solve_any(Mo.Lin[int(L.chars[k]) % d], (-Rr[:, :, k]).T % p, p)
                okl &= ~bad
                Bc = Mo.cocycles[int(L.chars[k]) % d]
                V[:, :, k] = (X.T + ((rng.integers(0, p, (16, len(Bc))) @ Bc) % p if len(Bc) else 0)) % p
        # pin: conjugate so that the base strand's label is 0 -- compare differences of labels (end vs base, copies vs read)
        r = B.tags.index("read"); cps = [q for q, t in enumerate(B.tags) if t == "copy"]
        same_vals = True
        for s in np.nonzero(okl)[0]:
            same_vals &= not ((V[s, -1] - V[s, 0]) % p).any()
            for q in cps:
                same_vals &= not ((V[s, q] - V[s, r]) % p).any()
        rows.append({"p": p, "d": d, "summand": name, "roots": roots, "colourings": bool(good), "lifted samples": int(okl.sum()),
                     "end = base and copies = read (group values)": bool(same_vals)})
        ok &= good and same_vals and okl.sum() > 0
report("2 zero-jump blocks", ok, rows)

# ---------------------------------------------------------------- 3 clean-edge census
from cd_lib import ideal_closure, rref, rank, pair_failures, triple_failures  # noqa: E402


def span_rows(rows_, p):
    rows_ = [np.array(r, dtype=np.int64) % p for r in rows_ if np.any(np.array(r) % p)]
    return rref(np.array(rows_), p)[0] if rows_ else None


def m_ideal(L, d):
    gens = [L.unit(k)[0] for k in range(L.D) if L.chars[k] % d]
    return ideal_closure(L, gens) if gens else np.zeros((0, L.D), dtype=np.int64)


def lcs(L, M, upto=5):
    p, res, cur = L.p, [M], M
    for _ in range(upto):
        if len(cur) == 0 or len(M) == 0: cur = np.zeros((0, L.D), dtype=np.int64)
        else:
            R = span_rows(np.concatenate([L.br(np.repeat(a[None, :], len(cur), axis=0), cur) for a in M]), p)
            cur = R if R is not None else np.zeros((0, L.D), dtype=np.int64)
        res.append(cur)
    return res


def char_dims(L, R, d):
    return {th: (rank(R[:, [k for k in range(L.D) if L.chars[k] % d == th]] % L.p, L.p)
                 if len(R) and any(L.chars[k] % d == th for k in range(L.D)) else 0) for th in range(d)}


def in_span(R, v, p):
    return (not np.any(v % p)) if len(R) == 0 else rank(np.vstack([R, v[None, :]]) % p, p) == rank(R, p)


def complement_rows(L, R, Rsub, p):
    res, cur = [], (Rsub.copy() if len(Rsub) else np.zeros((0, L.D), dtype=np.int64))
    for row in R:
        if not in_span(cur, row, p):
            res.append(row); cur = np.vstack([cur, row[None, :]]) if len(cur) else row[None, :]
    return np.array(res, dtype=np.int64).reshape(len(res), L.D)


def char_rows(L, R, d, chars):
    p, res = L.p, {}
    for c in chars:
        idx = [k for k in range(L.D) if L.chars[k] % d == c]
        if not idx or len(R) == 0: continue
        sub = R.copy(); sub[:, [k for k in range(L.D) if k not in idx]] = 0
        S = span_rows(sub, p)
        if S is not None: res[c] = S
    return res


def bracket_chars(L, Asub, Bsub, Kmod, d):
    p, res = L.p, set()
    for c, RA in Asub.items():
        for c2, RB in Bsub.items():
            if any(np.any(L.br(a[None, :], b[None, :])[0] % p) and not in_span(Kmod, L.br(a[None, :], b[None, :])[0], p)
                   for a in RA for b in RB):
                res.add((c + c2) % d)
    return res


def R_of(th, d):
    o = d // int(np.gcd(th % d, d)) if th % d else 1
    if o % 2 == 1: return {th % d, (-th) % d}
    k = o // 2
    return {al for al in range(1, d) if (al * k) % d == d // 2}


def det_layer2(L, L1i, G3, d):
    """{char: rows}: layer-2 parts (mod gamma_3) of brackets of a leaf's own layer-1 components -- the determined part of the
    leaf's layer-2 colour"""
    p = L.p; out = {}
    for c, RA in L1i.items():
        for c2, RB in L1i.items():
            for a in RA:
                for b in RB:
                    v = L.br(a[None, :], b[None, :])[0] % p
                    if np.any(v) and not in_span(G3, v, p): out.setdefault((c + c2) % d, []).append(v)
    return {c: np.array(v, dtype=np.int64) for c, v in out.items()}


def v3_chars(L, L1, L2, G3, Z, d):
    """characters of the layer-3 part of [l1, l2]: free and determined layer-2 parts of both leaves"""
    return (bracket_chars(L, L2[1], L1[2], Z, d) | bracket_chars(L, L1[1], L2[2], Z, d) | bracket_chars(L, L1[1], L1[2], Z, d)
            | bracket_chars(L, det_layer2(L, L1[1], G3, d), L1[2], Z, d) | bracket_chars(L, L1[1], det_layer2(L, L1[2], G3, d), Z, d))


def clean_edges(L, d):
    p = L.p
    M = m_ideal(L, d)
    G = lcs(L, M, 5)
    Z = np.zeros((0, L.D), dtype=np.int64)
    wins = []
    for Kname, K in (("0", Z), ("gamma_4", G[3])):
        if Kname == "0" and len(G[3]): continue
        kchars = {t for t, v in char_dims(L, K, d).items() if v and t % d}

        def mod(R):
            S = span_rows(np.concatenate([R, K]), p) if len(K) else (R if len(R) else None)
            return S if S is not None else Z
        G2 = mod(G[1]); G3 = mod(G[2]) if (len(G[2]) or len(K)) else Z
        lay1 = complement_rows(L, M, G2, p); lay2 = complement_rows(L, G2, G3, p)
        for a in range(1, d):
            for b in range(1, d):
                g = (a + b) % d
                if g == 0 or not bracket_chars(L, char_rows(L, lay1, d, [a]), char_rows(L, lay1, d, [b]), G3, d): continue
                th = {0: a, 1: b, 2: g}
                RR = {i: R_of(th[i], d) for i in range(3)}
                if g not in RR[2] or (RR[0] | RR[1] | RR[2]) & kchars: continue
                L1 = {i: char_rows(L, lay1, d, RR[i]) for i in range(3)}
                L2 = {i: char_rows(L, lay2, d, RR[i]) for i in range(3)}
                good = not bracket_chars(L, L1[1], L1[2], G3, d)                                       # (B0)
                good &= bracket_chars(L, L1[2], L1[0], G3, d) <= RR[1]                                 # (B1)
                good &= bracket_chars(L, L1[0], L1[1], G3, d) <= RR[2]                                 # (B2)
                s3 = v3_chars(L, L1, L2, G3, Z, d)
                good &= not (s3 & RR[0])                                                               # (V3)
                if good: wins.append((Kname, a, b))
    return wins


census = json.load(open(glob.glob(os.path.join(ROOT, "proofs/COPRIME-PAIRS-20261027-001C/*P001_*/result.json"))[0]))["census"]
PRIMES = {3: 7, 4: 13, 5: 11, 6: 7, 7: 29, 8: 17, 9: 19, 10: 11, 12: 13}
inter = [r for r in census if r["status"] == "residual, interacting"]
clean, still = [], []
for r in inter:
    d, chars, cls = r["d"], r["generator characters"], r["class"]
    L = free_graded(PRIMES[d], d, list(chars), cls)
    failing = [e for e in range(2, d + 1) if d % e == 0 and (pair_failures(L.coarsen(e)) or triple_failures(L.coarsen(e)))]
    wins = {e: clean_edges(L.coarsen(e), e) for e in failing}
    (clean if any(wins.values()) else still).append((d, tuple(chars), cls))
by_class = {c: sum(1 for x in clean if x[2] == c) for c in (3, 4)}
report("3 clean-edge census", len(inter) == 176 and len(clean) == 50 and by_class == {3: 46, 4: 4},
       {"interacting": len(inter), "with a clean edge": len(clean), "by class": by_class, "first clean": clean[:8],
        "first open": still[:8]})

# ---------------------------------------------------------------- 4 what blocks the open algebras
def blockers(L, d):
    """failing clean-edge conditions for every hard pair of every quotient option"""
    p = L.p
    M = m_ideal(L, d)
    G = lcs(L, M, 5)
    Z = np.zeros((0, L.D), dtype=np.int64)
    res = []
    for Kname, K in (("0", Z), ("gamma_4", G[3])):
        if Kname == "0" and len(G[3]): continue
        kchars = {t for t, v in char_dims(L, K, d).items() if v and t % d}

        def mod(R):
            S = span_rows(np.concatenate([R, K]), p) if len(K) else (R if len(R) else None)
            return S if S is not None else Z
        G2 = mod(G[1]); G3 = mod(G[2]) if (len(G[2]) or len(K)) else Z
        lay1 = complement_rows(L, M, G2, p); lay2 = complement_rows(L, G2, G3, p)
        for a in range(1, d):
            for b in range(1, d):
                g = (a + b) % d
                if g == 0 or not bracket_chars(L, char_rows(L, lay1, d, [a]), char_rows(L, lay1, d, [b]), G3, d): continue
                RR = {i: R_of(t, d) for i, t in enumerate((a, b, g))}
                L1 = {i: char_rows(L, lay1, d, RR[i]) for i in range(3)}
                L2 = {i: char_rows(L, lay2, d, RR[i]) for i in range(3)}
                s3 = v3_chars(L, L1, L2, G3, Z, d)
                fails = {name for name, bad in (("K", bool((RR[0] | RR[1] | RR[2]) & kchars)),
                                                ("B0", bool(bracket_chars(L, L1[1], L1[2], G3, d))),
                                                ("B1", not bracket_chars(L, L1[2], L1[0], G3, d) <= RR[1]),
                                                ("B2", not bracket_chars(L, L1[0], L1[1], G3, d) <= RR[2]),
                                                ("V3", bool(s3 & RR[0]))) if bad}
                res.append(frozenset(fails))
    return res


cats = {}
for (d, chars, cls) in still:
    L = free_graded(PRIMES[d], d, list(chars), cls)
    sets = [s for e in range(2, d + 1) if d % e == 0 and (pair_failures(L.coarsen(e)) or triple_failures(L.coarsen(e)))
            for s in blockers(L.coarsen(e), e)]
    assert all(s for s in sets)                                   # no clean edge among the open algebras
    minimal = sorted({s for s in sets if not any(t < s for t in sets)}, key=lambda s: (len(s), sorted(s)))
    key = f"class {cls}: " + (" | ".join("+".join(sorted(s)) for s in minimal) if minimal else "no hard pair modulo gamma_3")
    cats[key] = cats.get(key, 0) + 1
EXPECTED = {"class 3: V3": 11, "class 3: B2": 9, "class 3: B0+V3": 9, "class 3: B0+B1+B2+V3": 8, "class 3: B2+V3": 4,
            "class 3: B1+B2 | B0+B2+V3": 2, "class 3: B0+V3 | B1+V3": 2, "class 3: V3 | B0+B1": 1, "class 3: B2 | B0+V3 | B1+V3": 1,
            "class 4: K": 26, "class 4: B0+K+V3": 20, "class 4: B0+B1+B2+K+V3": 8, "class 4: B2+K+V3": 8, "class 4: B2+K": 5,
            "class 4: K+V3": 4, "class 4: B1+B2+K | B0+B2+K+V3": 2, "class 4: K+V3 | B0+B1+K": 2,
            "class 4: no hard pair modulo gamma_3": 4}
report("4 open algebras by minimal sets of failing conditions", cats == EXPECTED and sum(cats.values()) == 126,
       {"categories": dict(sorted(cats.items(), key=lambda kv: -kv[1])), "total": sum(cats.values())})

# ---------------------------------------------------------------- 5 the full edge matrix for free class 3 on (1, 1) at d = 5
p, d = 11, 5
L = free_graded(p, d, [1, 1], 3)
T = summand_types(p, d, (1, 1, 2))
G = Gadget(L, d, p, T, 2, [(0, 1)])
rng = np.random.default_rng(5)
nvar = len(G.var)


def monos(nv, deg):
    o = [()]
    for k in range(1, deg + 1): o += list(itertools.combinations_with_replacement(range(nv), k))
    return o


def evalm(X, ms):
    cols = []
    for m in ms:
        c = np.ones(len(X), dtype=np.int64)
        for i in m: c = c * X[:, i] % p
        cols.append(c)
    return np.stack(cols, axis=1) % p


ms = monos(nvar, 3)
X = rng.integers(0, p, (400, nvar)); Y = G.evaluate(X) % p
coef, bad = solve_any(evalm(X, ms), Y, p)
assert not bad.any()
Xv = rng.integers(0, p, (200, nvar))
exact = bool(((evalm(Xv, ms) @ coef) % p == G.evaluate(Xv) % p).all())
vs = G.var_sites()
iu = [j for j, s in enumerate(vs) if s == ("v", 0)]; iv = [j for j, s in enumerate(vs) if s == ("v", 1)]
ip = [j for j, s in enumerate(vs) if s[0] == "e"]
priv = np.array(list(itertools.product(range(p), repeat=len(ip))), dtype=np.int64)
F = np.zeros((p * p, p * p), dtype=np.int64)
for xu in range(p * p):
    for xv in range(p * p):
        P = np.zeros((len(priv), nvar), dtype=np.int64)
        P[:, iu] = [xu // p, xu % p]; P[:, iv] = [xv // p, xv % p]; P[:, ip] = priv
        F[xu, xv] = int((~((evalm(P, ms) @ coef) % p).any(axis=1)).sum())
Fmax = p ** len(ip)
rF = int(np.linalg.matrix_rank(F.astype(float))); rM = int(np.linalg.matrix_rank((F @ F.T).astype(float)))
ok = exact and (np.diag(F) == Fmax).all() and (F[0, 1:] < Fmax).all() and (F[1:, 0] < Fmax).all() and F.min() >= 1 and rF >= 2 and rM >= 2
report("5 edge matrix (free class 3 on (1,1), d = 5)", ok,
       {"exact interpolation": exact, "F values": sorted(set(F.flatten().tolist())), "F_max": Fmax, "rank F": rF, "rank F F^T": rM})

# ---------------------------------------------------------------- 6 the blocking conditions are real vertex couplings
def diagonal_probe(chars, cls, slots, p=11, d=5, N=400, seed=9):
    L = free_graded(p, d, chars, cls)
    G = Gadget(L, d, p, summand_types(p, d, slots), 2, [(0, 1)])
    vs, es = G.var_sites(), G.eq_sites()
    iu = [j for j, s in enumerate(vs) if s == ("v", 0)]; iv = [j for j, s in enumerate(vs) if s == ("v", 1)]
    ip = [j for j, s in enumerate(vs) if s[0] == "e"]
    cv = [c for c, s in enumerate(es) if s[0] == "v"]; cp = [c for c, s in enumerate(es) if s[0] == "e"]
    r = np.random.default_rng(seed)
    vals = np.zeros((N, len(G.var)), dtype=np.int64)
    su = r.integers(0, p, len(iu)); vals[:, iu] = su; vals[:, iv] = su; vals[:, ip] = r.integers(0, p, (N, len(ip)))
    E = G.evaluate(vals) % p
    return {"private equations hold": int((~E[:, cp].any(axis=1)).sum()), "vertex equations nonzero": int(E[:, cv].any(axis=1).sum()),
            "samples": N, "vertex equation layers": sorted({int(L.layer[k]) for c, (bi, k) in enumerate(G.eqs) if c in cv})}


rows = {"K only: free class 4 on (1, 1), slots (1, 1, 2)": diagonal_probe([1, 1], 4, (1, 1, 2)),
        "V3 only: free class 3 on (1, 1, 2), slots (1, 2, 3)": diagonal_probe([1, 1, 2], 3, (1, 2, 3)),
        "B2 only: free class 3 on (0, 1, 4), slots (1, 1, 2)": diagonal_probe([0, 1, 4], 3, (1, 1, 2))}
k, v3, b2 = rows.values()
ok = (all(x["private equations hold"] == x["samples"] for x in rows.values())
      and k["vertex equations nonzero"] > k["samples"] // 2 and v3["vertex equations nonzero"] > v3["samples"] // 2
      and b2["vertex equations nonzero"] == 0)
report("6 diagonal vertex equations at d = 5, p = 11 (K, V3: nonzero; B2: zero)", ok, rows)

# ---------------------------------------------------------------- 7 Theorem 5: the character-0 refinement on the census
def zero_part(L, A, B, G3, d):
    """vectors spanning the character-0 parts of [A, B] that are nonzero modulo G3"""
    p = L.p; rows_ = []
    for c, RA in A.items():
        for c2, RB in B.items():
            if (c + c2) % d: continue
            for a in RA:
                for b in RB:
                    v = L.br(a[None, :], b[None, :])[0] % p
                    if np.any(v) and not in_span(G3, v, p): rows_.append(v)
    return np.array(rows_, dtype=np.int64).reshape(len(rows_), L.D)


def refined_blockers(L, d, with_pairs=False):
    """failing conditions with (B1'), (B2') (character 0 allowed) and (V3') for every hard pair of every quotient option"""
    p = L.p
    M = m_ideal(L, d)
    G = lcs(L, M, 5)
    Z = np.zeros((0, L.D), dtype=np.int64)
    res = []
    for Kname, K in (("0", Z), ("gamma_4", G[3])):
        if Kname == "0" and len(G[3]): continue
        kchars = {t for t, v in char_dims(L, K, d).items() if v and t % d}

        def mod(R):
            S = span_rows(np.concatenate([R, K]), p) if len(K) else (R if len(R) else None)
            return S if S is not None else Z
        G2 = mod(G[1]); G3 = mod(G[2]) if (len(G[2]) or len(K)) else Z
        lay1 = complement_rows(L, M, G2, p); lay2 = complement_rows(L, G2, G3, p)
        for a in range(1, d):
            for b in range(1, d):
                g = (a + b) % d
                if g == 0 or not bracket_chars(L, char_rows(L, lay1, d, [a]), char_rows(L, lay1, d, [b]), G3, d): continue
                RR = {i: R_of(t, d) for i, t in enumerate((a, b, g))}
                L1 = {i: char_rows(L, lay1, d, RR[i]) for i in range(3)}
                L2 = {i: char_rows(L, lay2, d, RR[i]) for i in range(3)}
                s3 = v3_chars(L, L1, L2, G3, Z, d)
                Z1 = zero_part(L, L1[2], L1[0], G3, d); Z2 = zero_part(L, L1[0], L1[1], G3, d)
                v3p = any(np.any(L.br(x[None, :], z[None, :])[0] % p)
                          for (Zr, Lx) in ((Z1, L1[1]), (Z2, L1[2])) for c, RA in Lx.items() if c in RR[0] for x in RA for z in Zr)
                fails = {name for name, bad in (("K", bool((RR[0] | RR[1] | RR[2]) & kchars)),
                                                ("B0", bool(bracket_chars(L, L1[1], L1[2], G3, d))),
                                                ("B1'", not bracket_chars(L, L1[2], L1[0], G3, d) <= RR[1] | {0}),
                                                ("B2'", not bracket_chars(L, L1[0], L1[1], G3, d) <= RR[2] | {0}),
                                                ("V3", bool(s3 & RR[0])), ("V3'", v3p)) if bad}
                res.append((frozenset(fails), (Kname, a, b, len(Z1), len(Z2))) if with_pairs else frozenset(fails))
    return res


newly, rcats = [], {}
for (d, chars, cls) in still:
    L = free_graded(PRIMES[d], d, list(chars), cls)
    sets = [s for e in range(2, d + 1) if d % e == 0 and (pair_failures(L.coarsen(e)) or triple_failures(L.coarsen(e)))
            for s in refined_blockers(L.coarsen(e), e)]
    if any(not s for s in sets):
        newly.append((d, tuple(chars), cls)); continue
    minimal = sorted({s for s in sets if not any(t < s for t in sets)}, key=lambda s: (len(s), sorted(s)))
    key = f"class {cls}: " + (" | ".join("+".join(sorted(s)) for s in minimal) if minimal else "no hard pair modulo gamma_3")
    rcats[key] = rcats.get(key, 0) + 1
NEWLY = [(5, (0, 1, 4), 3), (7, (0, 1, 6), 3), (9, (0, 1, 8), 3), (10, (0, 2, 8), 3), (10, (2, 5, 8), 3)]
REXPECTED = {"class 3: V3": 15, "class 3: B0+V3": 9, "class 3: B0+V3+V3'": 8, "class 3: B2' | B0+V3+V3'": 3,
             "class 3: B1'+B2' | B0+B2'+V3": 2, "class 3: B0+V3 | B1'+V3": 2, "class 3: B2'": 2, "class 3: V3 | B0+B1'": 1,
             "class 4: K": 26, "class 4: B0+K+V3": 20, "class 4: K+V3": 12, "class 4: B0+K+V3+V3'": 8,
             "class 4: no hard pair modulo gamma_3": 4, "class 4: B2'+K | B0+K+V3+V3'": 3, "class 4: B1'+B2'+K | B0+B2'+K+V3": 2,
             "class 4: K+V3 | B0+B1'+K": 2, "class 4: B2'+K": 2}
report("7 Theorem 5 on the census (5 more clean edges; 121 open by minimal failing sets)",
       sorted(newly) == sorted(NEWLY) and rcats == REXPECTED and sum(rcats.values()) == 121,
       {"newly clean": newly, "open categories": dict(sorted(rcats.items(), key=lambda kv: -kv[1])), "open total": sum(rcats.values())})

# ---------------------------------------------------------------- 8 Theorem 5 on free class 3 on (0, 1, 4) at d = 5, p = 11
p, d = 11, 5
L = free_graded(p, d, [0, 1, 4], 3)
used = [info for s, info in refined_blockers(L, d, with_pairs=True) if not s and info[1:3] == (1, 1)]
T = summand_types(p, d, (1, 1, 2))
K2 = Gadget(L, d, p, T, 2, [(0, 1)]); P3 = Gadget(L, d, p, T, 3, [(0, 1), (1, 2)])
nv = sum(1 for s in K2.var_sites() if s == ("v", 0)); Fmax = p ** sum(1 for s in K2.var_sites() if s[0] == "e")
vu = [j for j, s in enumerate(K2.var_sites()) if s == ("v", 0)]
th0 = [vu.index(j) for j in vu if int(L.layer[K2.var[j][1]]) == 1 and int(L.chars[K2.var[j][1]]) % d == 1]
r8 = np.random.default_rng(8)
s = r8.integers(0, p, nv)
f_diag, vb_diag, _, _ = edge_count(K2, s, s)
D = np.zeros(nv, dtype=np.int64); D[th0] = r8.integers(1, p, len(th0))
f_def, vb_def, _, _ = edge_count(K2, np.zeros(nv, dtype=np.int64), D)
# path locality on the variety: one comparison with e1's data on its single-edge solution set
vs3, eq3 = P3.var_sites(), P3.eq_sites()
i0 = [j for j, x in enumerate(vs3) if x == ("e", 0)]; i1 = [j for j, x in enumerate(vs3) if x == ("e", 1)]
w0, w1, w2 = ([j for j, x in enumerate(vs3) if x == ("v", k)] for k in range(3))
c0 = [c for c, x in enumerate(eq3) if x == ("e", 0)]; c1 = [c for c, x in enumerate(eq3) if x == ("e", 1)]; cv3 = [c for c, x in enumerate(eq3) if x[0] == "v"]
s1, s2, s0 = r8.integers(0, p, len(w1)), r8.integers(0, p, len(w2)), r8.integers(0, p, len(w0))
_, _, _, S1 = edge_count(K2, s1, s2)
pi1 = S1[r8.integers(0, len(S1))]
combos = np.array(list(itertools.product(range(p), repeat=len(i0))), dtype=np.int64)
vals = np.zeros((len(combos), len(P3.var)), dtype=np.int64)
vals[:, i0] = combos; vals[:, w0] = s0; vals[:, w1] = s1; vals[:, w2] = s2; vals[:, i1] = pi1
E3 = evaluate_chunked(P3, vals) % p
sol = ~E3[:, c0].any(axis=1)
_, _, _, S0 = edge_count(K2, s0, s1)
same = set(map(tuple, S0.tolist())) == set(map(tuple, combos[sol].tolist()))
e1bad = int(E3[sol][:, c1].any(axis=1).sum()); vbad3 = int(E3[sol][:, cv3].any(axis=1).sum())
ok = (bool(used) and all(u[4] > 0 or u[3] > 0 for u in used) and f_diag == Fmax and vb_diag == 0 and 1 <= f_def < Fmax and vb_def == 0
      and same and e1bad == 0 and vbad3 == 0 and sol.sum() > 0)
report("8 Theorem 5 on free class 3 on (0, 1, 4), d = 5 (character-0 brackets used; diagonal, deficit, path locality)", ok,
       {"clean refined choices (K, a, b, dim Z1, dim Z2)": used, "F(s, s)": f_diag, "F(0, D)": f_def, "F_max": Fmax,
        "vertex pairings nonzero": vb_diag + vb_def, "path e0 solutions": int(sol.sum()), "path set equals single edge": same,
        "e1 equations nonzero": e1bad, "path vertex pairings nonzero": vbad3})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-PAIRS-20261027-001E-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out, "seconds": round(time.time() - T0, 1)}, fh,
                  indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T0, 1), "s")
