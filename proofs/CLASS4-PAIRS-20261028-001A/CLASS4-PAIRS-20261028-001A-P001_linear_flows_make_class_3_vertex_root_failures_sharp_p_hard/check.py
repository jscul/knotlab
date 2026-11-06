"""Checks for CLASS4-PAIRS-20261028-001A-P001 (linear flows in class 3).

  1 the census: among the 121 interacting algebras open after Theorem 5 of COPRIME-PAIRS-20261027-001E, 16 (class 3) have an edge
    failing only (V3); 12 of them have such an edge whose dual slot carries no layer-1 data; 8 of these 12 are not decided by
    Theorem 6 (COPRIME-PAIRS-20261027-001F), listed
  2 structure on free class 3 on (1, 1, 4) at d = 5, p = 11, slots (1, 1, 2), where Theorem 6's off-diagonal condition fails: at a
    diagonal, two random and a pair-failing vertex pair, exhaustively over the 11^4 private configurations: endpoint flows are exact
    negatives on solutions; for each slot-1 configuration the slot-2 solutions form a linear subspace; the flow is additive in
    slot-2 data and vanishes at slot-2 data 0; Fourier values at mu = 0 and 300 random mu are real and non-negative; off-diagonal
    flows are nonzero somewhere (so Theorem 6 does not apply)
  3 control: an edge whose dual slot has bracketing layer-1 data (free class 3 on (1, 2, 3) at d = 5, slots (1, 1, 2)): the
    private equations are not homogeneous-affine in slot-2 data (linear algebra, verified at random points), while for (1, 1, 4)
    they are
Run: python3 -B check.py [--write]"""
import glob, itertools, json, os, sys, time
import numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, glob.glob(os.path.join(ROOT, "experiments/COPRIME-PAIRS-20261027-001D/*E001_*"))[0])
from pf_lib import *  # noqa: E402  (read-only)
from cd_lib import ideal_closure, rref, rank, pair_failures, triple_failures  # noqa: E402
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:900], flush=True)


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



def edge_conditions(L, d):
    """for each hard pair (m of class <= 3, no quotient): (failing Theorem 5 conditions, (F0), (F1), (F2))"""
    p = L.p
    M = m_ideal(L, d)
    G = lcs(L, M, 5)
    Z = np.zeros((0, L.D), dtype=np.int64)
    res = []
    if len(G[3]): return res
    G2 = G[1] if len(G[1]) else Z; G3 = G[2] if len(G[2]) else Z
    lay1 = complement_rows(L, M, G2, p); lay2 = complement_rows(L, G2, G3, p)
    for a in range(1, d):
        for b in range(1, d):
            g = (a + b) % d
            if g == 0 or not bracket_chars(L, char_rows(L, lay1, d, [a]), char_rows(L, lay1, d, [b]), G3, d): continue
            RR = {i: R_of(t, d) for i, t in enumerate((a, b, g))}
            L1 = {i: char_rows(L, lay1, d, RR[i]) for i in range(3)}
            L2 = {i: char_rows(L, lay2, d, RR[i]) for i in range(3)}
            Z1 = zero_part(L, L1[2], L1[0], G3, d); Z2 = zero_part(L, L1[0], L1[1], G3, d)
            v3p = any(np.any(L.br(x[None, :], z[None, :])[0] % p)
                      for (Zr, Lx) in ((Z1, L1[1]), (Z2, L1[2])) for c, RA in Lx.items() if c in RR[0] for x in RA for z in Zr)
            t5 = {n for n, bad in (("B0", bool(bracket_chars(L, L1[1], L1[2], G3, d))),
                                   ("B1'", not bracket_chars(L, L1[2], L1[0], G3, d) <= RR[1] | {0}),
                                   ("B2'", not bracket_chars(L, L1[0], L1[1], G3, d) <= RR[2] | {0}),
                                   ("V3", bool(v3_chars(L, L1, L2, G3, Z, d) & RR[0])), ("V3'", v3p)) if bad}
            f0 = len(L2[0]) == 0
            V0 = np.concatenate([L1[0][c] for c in L1[0]]) if L1[0] else np.zeros((0, L.D), dtype=np.int64)

            def inj(D, Lx, R):
                if not Lx: return True
                Y = np.concatenate([Lx[c] for c in Lx])
                mask = np.array([int(L.chars[k]) % d in R for k in range(L.D)])
                A = np.array([np.where(mask, L.br(D[None, :], y[None, :])[0] % p, 0) for y in Y]) % p
                G3r = np.array([np.where(mask, v, 0) for v in G3]) % p if len(G3) else np.zeros((0, L.D), dtype=np.int64)
                base = rank(G3r, p) if len(G3r) else 0
                return (rank(np.vstack([G3r, A]) % p, p) if len(G3r) else rank(A, p)) - base == len(Y)
            f1 = True
            for coef in itertools.product(range(p), repeat=len(V0)):
                if not any(coef): continue
                D = (np.array(coef, dtype=np.int64) @ V0) % p
                if not inj(D, L1[1], RR[2]) or not inj((-D) % p, L1[2], RR[1]): f1 = False; break
            D1, D2 = det_layer2(L, L1[1], G3, d), det_layer2(L, L1[2], G3, d)
            f2 = not ((bracket_chars(L, L1[1], L1[2], Z, d) | bracket_chars(L, D1, L1[2], Z, d) | bracket_chars(L, L1[1], D2, Z, d)) & RR[0])
            res.append(((a, b), frozenset(t5), f0, f1, f2))
    return res



def edge_conditions_lf(L, d):
    """for each hard pair (m of class <= 3): (pair, failing Theorem 5 conditions, dual slot has no layer-1 data)"""
    p = L.p
    M = m_ideal(L, d)
    G = lcs(L, M, 5)
    Z = np.zeros((0, L.D), dtype=np.int64)
    res = []
    if len(G[3]): return res
    G2 = G[1] if len(G[1]) else Z; G3 = G[2] if len(G[2]) else Z
    lay1 = complement_rows(L, M, G2, p); lay2 = complement_rows(L, G2, G3, p)
    for a in range(1, d):
        for b in range(1, d):
            g = (a + b) % d
            if g == 0 or not bracket_chars(L, char_rows(L, lay1, d, [a]), char_rows(L, lay1, d, [b]), G3, d): continue
            RR = {i: R_of(t, d) for i, t in enumerate((a, b, g))}
            L1 = {i: char_rows(L, lay1, d, RR[i]) for i in range(3)}
            L2 = {i: char_rows(L, lay2, d, RR[i]) for i in range(3)}
            Z1 = zero_part(L, L1[2], L1[0], G3, d); Z2 = zero_part(L, L1[0], L1[1], G3, d)
            v3p = any(np.any(L.br(x[None, :], z[None, :])[0] % p)
                      for (Zr, Lx) in ((Z1, L1[1]), (Z2, L1[2])) for c, RA in Lx.items() if c in RR[0] for x in RA for z in Zr)
            t5 = {n for n, bad in (("B0", bool(bracket_chars(L, L1[1], L1[2], G3, d))),
                                   ("B1'", not bracket_chars(L, L1[2], L1[0], G3, d) <= RR[1] | {0}),
                                   ("B2'", not bracket_chars(L, L1[0], L1[1], G3, d) <= RR[2] | {0}),
                                   ("V3", bool(v3_chars(L, L1, L2, G3, Z, d) & RR[0])), ("V3'", v3p)) if bad}
            res.append(((a, b), frozenset(t5), not L1[2]))
    return res


# ---------------------------------------------------------------- 1 the census
census = json.load(open(glob.glob(os.path.join(ROOT, "proofs/COPRIME-PAIRS-20261027-001C/*P001_*/result.json"))[0]))["census"]
PRIMES = {3: 7, 4: 13, 5: 11, 6: 7, 7: 29, 8: 17, 9: 19, 10: 11, 12: 13}
T6 = {(5, (1, 1, 2)), (6, (1, 2, 4)), (7, (1, 1, 4)), (9, (1, 2, 3)), (10, (1, 4, 6)), (10, (2, 2, 4)), (12, (2, 3, 4)), (12, (2, 4, 8))}
v3only, lin = [], []
for r in [r for r in census if r["status"] == "residual, interacting"]:
    d, chars, cls = r["d"], r["generator characters"], r["class"]
    if cls != 3: continue
    L = free_graded(PRIMES[d], d, list(chars), cls)
    failing = [e for e in range(2, d + 1) if d % e == 0 and (pair_failures(L.coarsen(e)) or triple_failures(L.coarsen(e)))]
    rows = [(e,) + x for e in failing for x in edge_conditions_lf(L.coarsen(e), e)]
    if any(not x[2] for x in rows): continue                                 # a clean edge (Theorem 5): decided already
    cand = [x for x in rows if x[2] == frozenset({"V3"})]
    if not cand: continue
    v3only.append((d, tuple(chars)))
    win = [x for x in cand if x[3]]
    if win: lin.append({"d": d, "chars": chars, "edge": [win[0][0], list(win[0][1])], "also Theorem 6": (d, tuple(chars)) in T6})
NEW = [(5, (1, 1, 4)), (6, (0, 1, 2)), (6, (1, 2, 2)), (7, (1, 1, 6)), (9, (1, 1, 8)), (10, (2, 2, 8)), (12, (0, 2, 4)), (12, (2, 4, 4))]
new = sorted((x["d"], tuple(x["chars"])) for x in lin if not x["also Theorem 6"])
report("1 census (16 vertex-root algebras; 12 with linear-flow edges; 8 new)",
       len(v3only) == 16 and len(lin) == 12 and new == sorted(NEW),
       {"fail only (V3)": len(v3only), "linear-flow edges": lin, "new beyond Theorem 6": new})


# ---------------------------------------------------------------- 2-3 the linear structure
def structure(chars, slots, p=11, d=5, seed=11):
    L = free_graded(p, d, chars, 3)
    G = Gadget(L, d, p, summand_types(p, d, slots), 2, [(0, 1)])
    vs, es = G.var_sites(), G.eq_sites()
    iu = [j for j, s in enumerate(vs) if s == ("v", 0)]; iv = [j for j, s in enumerate(vs) if s == ("v", 1)]
    ip = [j for j, s in enumerate(vs) if s[0] == "e"]
    s1 = [q for q, j in enumerate(ip) if G.kinds[G.var[j][0]][2] == 1]; s2 = [q for q, j in enumerate(ip) if G.kinds[G.var[j][0]][2] == 2]
    cu = [c for c, s in enumerate(es) if s == ("v", 0)]; cv = [c for c, s in enumerate(es) if s == ("v", 1)]; cp = [c for c, s in enumerate(es) if s[0] == "e"]
    combos = np.array(list(itertools.product(range(p), repeat=len(ip))), dtype=np.int64)
    r = np.random.default_rng(seed)
    vu = [j for j in iu if int(L.layer[G.var[j][1]]) == 1 and int(L.chars[G.var[j][1]]) % d == slots[0] % d]
    D = np.zeros(len(iu), dtype=np.int64); D[[iu.index(j) for j in vu]] = r.integers(1, p, len(vu))
    pairs = [("diagonal", (lambda s: (s, s))(r.integers(0, p, len(iu)))), ("random", (r.integers(0, p, len(iu)), r.integers(0, p, len(iu)))),
             ("random", (r.integers(0, p, len(iu)), r.integers(0, p, len(iu)))), ("pair-failing (0, D)", (np.zeros(len(iu), dtype=np.int64), D))]
    out, ok = [], True
    for name, (su, sv) in pairs:
        vals = np.zeros((len(combos), len(G.var)), dtype=np.int64)
        vals[:, iu] = su; vals[:, iv] = sv; vals[:, ip] = combos
        E = evaluate_chunked(G, vals) % p
        sol = ~E[:, cp].any(axis=1)
        S = combos[sol]; fu = E[sol][:, cu]; fv = E[sol][:, cv]
        conserved = bool(((fu + fv) % p == 0).all())
        flow = {tuple(x): tuple(y) for x, y in zip(S.tolist(), fv.tolist())}
        by1 = {}
        for x in S.tolist(): by1.setdefault(tuple(x[q] for q in s1), []).append(tuple(x[q] for q in s2))
        subspace, linear = True, True
        for k1, U in by1.items():
            Us = set(U)
            zero = tuple(0 for _ in s2)
            if zero not in Us: subspace = False; continue
            Ul = list(Us)
            for _ in range(min(60, len(Ul) ** 2)):
                a, b = Ul[r.integers(0, len(Ul))], Ul[r.integers(0, len(Ul))]
                c = tuple((x + y) % p for x, y in zip(a, b))
                if c not in Us: subspace = False; break
                full = lambda u: tuple(k1[s1.index(q)] if q in s1 else u[s2.index(q)] for q in range(len(ip)))
                fa, fb, fc = np.array(flow[full(a)]), np.array(flow[full(b)]), np.array(flow[full(c)])
                if ((fa + fb - fc) % p).any() or np.array(flow[full(zero)]).any(): linear = False
        mus = np.concatenate([np.zeros((1, len(cv)), dtype=np.int64), r.integers(0, p, (300, len(cv)))])
        Nhat = np.exp(2j * np.pi * ((mus @ fv.T) % p) / p).sum(axis=1)
        nonneg = bool(np.abs(Nhat.imag).max() < 1e-6 and Nhat.real.min() > -1e-6)
        rec = {"pair": name, "solutions": int(sol.sum()), "conserved": conserved, "slot-2 solutions are subspaces": subspace,
               "flow linear in slot-2 data": linear, "Fourier non-negative (301 mu)": nonneg, "min Fourier": float(Nhat.real.min()),
               "flow nonzero on solutions": int(fv.any(axis=1).sum())}
        out.append(rec)
        ok &= conserved and subspace and linear and nonneg
    return ok, out


ok2, rows2 = structure([1, 1, 4], (1, 1, 2))
offdiag_flow = any(r_["flow nonzero on solutions"] > 0 for r_ in rows2 if r_["pair"] != "diagonal")
report("2 linear structure on free class 3 on (1, 1, 4), d = 5 (Theorem 6's off-diagonal condition fails)", ok2 and offdiag_flow,
       {"off-diagonal flows nonzero somewhere": offdiag_flow,
        "per pair [name, solutions, conserved, subspaces, linear, Fourier >= 0, min Fourier, nonzero flows]":
            [[r_["pair"], r_["solutions"], r_["conserved"], r_["slot-2 solutions are subspaces"], r_["flow linear in slot-2 data"],
              r_["Fourier non-negative (301 mu)"], round(r_["min Fourier"], 3), r_["flow nonzero on solutions"]] for r_ in rows2]})
def affine_in_slot2(chars, slots, p=11, d=5, seed=12):
    """for slot-1 data on the slot-1 solution set (slot-2 data zero), test whether the private equations are homogeneous affine
    in slot-2 data (linear algebra on unit vectors, verified at random points)"""
    from cd_lib import nullspace as _ns  # noqa
    L = free_graded(p, d, chars, 3)
    G = Gadget(L, d, p, summand_types(p, d, slots), 2, [(0, 1)])
    vs, es = G.var_sites(), G.eq_sites()
    iu = [j for j, s_ in enumerate(vs) if s_ == ("v", 0)]; iv = [j for j, s_ in enumerate(vs) if s_ == ("v", 1)]
    ip = [j for j, s_ in enumerate(vs) if s_[0] == "e"]
    q1 = [j for j in ip if G.kinds[G.var[j][0]][2] == 1]; q2 = [j for j in ip if G.kinds[G.var[j][0]][2] == 2]
    cp = [c for c, s_ in enumerate(es) if s_[0] == "e"]
    r = np.random.default_rng(seed)
    out = []
    for name, (su, sv) in [("diagonal", (lambda x: (x, x))(r.integers(0, p, len(iu)))), ("random", (r.integers(0, p, len(iu)), r.integers(0, p, len(iu))))]:
        C1 = np.array(list(itertools.product(range(p), repeat=len(q1))), dtype=np.int64)
        vals = np.zeros((len(C1), len(G.var)), dtype=np.int64); vals[:, iu] = su; vals[:, iv] = sv; vals[:, q1] = C1
        E = evaluate_chunked(G, vals) % p
        S1 = C1[~E[:, cp].any(axis=1)]
        bad = 0
        for P1 in S1[r.permutation(len(S1))[:8]]:
            rows = np.zeros((1 + len(q2) + 4, len(G.var)), dtype=np.int64); rows[:, iu] = su; rows[:, iv] = sv; rows[:, q1] = P1
            for i, j in enumerate(q2): rows[1 + i, j] = 1
            rnd = r.integers(0, p, (4, len(q2))); rows[1 + len(q2):, q2] = rnd
            Ex = G.evaluate(rows)[:, cp] % p
            M = ((Ex[1:1 + len(q2)] - Ex[0]) % p).T
            aff = all(((M @ rnd[k] + Ex[0]) % p == Ex[1 + len(q2) + k]).all() for k in range(4))
            bad += int((not aff) or Ex[0].any())
        out.append({"pair": name, "slot-1 solutions": len(S1), "samples not homogeneous-affine in slot-2 data": bad})
    return out


rows3 = affine_in_slot2([1, 2, 3], (1, 1, 2))
rows3pos = affine_in_slot2([1, 1, 4], (1, 1, 2))
report("3 control: dual slot with bracketing layer-1 data (free class 3 on (1, 2, 3), slots (1, 1, 2)): private equations not "
       "homogeneous-affine in slot-2 data, while they are for (1, 1, 4)",
       any(x["samples not homogeneous-affine in slot-2 data"] for x in rows3) and not any(x["samples not homogeneous-affine in slot-2 data"] for x in rows3pos),
       {"control (1, 2, 3)": rows3, "check-2 algebra (1, 1, 4)": rows3pos})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "CLASS4-PAIRS-20261028-001A-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out, "seconds": round(time.time() - T0, 1)}, fh,
                  indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T0, 1), "s")
