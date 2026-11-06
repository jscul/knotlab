"""Checks for COPRIME-PAIRS-20261027-001F-P001 (conserved vertex flows).

  1 the flow census: among the 121 interacting algebras open after COPRIME-PAIRS-20261027-001E (Theorem 5), the class-3 algebras
    whose edges fail only (V3) are 16; the flow conditions (F0)-(F2) hold for 8 of them, listed
  2 conservation: on free class 3 on (1, 1, 2) at d = 5, p = 11 (slots (1, 2, 3)), the two endpoints' vertex equations are exact
    negatives on every solution at the diagonal (all private data) and at sampled off-diagonal solutions
  3 off the diagonal the flow vanishes on every sampled solution; random off-diagonal private data with nonzero layer-1 parts never solve
  4 at the diagonal the flow is a bilinear form B(a1, b2) + B'(b1, a2) (exact interpolation, degree <= 3, validated on fresh points);
    its Fourier transform N(mu) = sum_pi omega^<mu, f(pi)> is a positive integer for every mu, computed exactly from the form
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


# ---------------------------------------------------------------- 1 the flow census
census = json.load(open(glob.glob(os.path.join(ROOT, "proofs/COPRIME-PAIRS-20261027-001C/*P001_*/result.json"))[0]))["census"]
PRIMES = {3: 7, 4: 13, 5: 11, 6: 7, 7: 29, 8: 17, 9: 19, 10: 11, 12: 13}
v3only, decided, blocked = [], [], []
for r in [r for r in census if r["status"] == "residual, interacting"]:
    d, chars, cls = r["d"], r["generator characters"], r["class"]
    L = free_graded(PRIMES[d], d, list(chars), cls)
    failing = [e for e in range(2, d + 1) if d % e == 0 and (pair_failures(L.coarsen(e)) or triple_failures(L.coarsen(e)))]
    rows = [(e,) + x for e in failing for x in edge_conditions(L.coarsen(e), e)]
    if any(not x[2] for x in rows): continue                                  # a clean edge (Theorem 5): decided already
    cand = [x for x in rows if x[2] == frozenset({"V3"})]
    if not cand: continue
    v3only.append((d, tuple(chars), cls))
    win = [x for x in cand if x[3] and x[4] and x[5]]
    (decided if win else blocked).append({"d": d, "chars": chars, "class": cls,
                                          "edge": [win[0][0], list(win[0][1])] if win else None,
                                          "(order, pair, F0, F1, F2) per candidate": [[x[0], list(x[1]), x[3], x[4], x[5]] for x in cand]})
DECIDED = [(5, (1, 1, 2)), (6, (1, 2, 4)), (7, (1, 1, 4)), (9, (1, 2, 3)), (10, (1, 4, 6)), (10, (2, 2, 4)), (12, (2, 3, 4)), (12, (2, 4, 8))]
report("1 flow census (16 algebras fail only (V3); (F0)-(F2) decide 8)",
       len(v3only) == 16 and sorted((x["d"], tuple(x["chars"])) for x in decided) == sorted(DECIDED) and all(x["class"] == 3 for x in decided),
       {"fail only (V3)": len(v3only), "decided": decided, "blocked": blocked})

# ---------------------------------------------------------------- 2-4 the example free class 3 on (1, 1, 2), d = 5, p = 11
p, d = 11, 5
L = free_graded(p, d, [1, 1, 2], 3)
G = Gadget(L, d, p, summand_types(p, d, (1, 2, 3)), 2, [(0, 1)])
vs, es = G.var_sites(), G.eq_sites()
iu = [j for j, s in enumerate(vs) if s == ("v", 0)]; iv = [j for j, s in enumerate(vs) if s == ("v", 1)]
ip = [j for j, s in enumerate(vs) if s[0] == "e"]
cu = [c for c, s in enumerate(es) if s == ("v", 0)]; cv = [c for c, s in enumerate(es) if s == ("v", 1)]; cp = [c for c, s in enumerate(es) if s[0] == "e"]
lay = {j: int(L.layer[G.var[j][1]]) for j in ip}
slot = {}
for j in ip:
    bi = G.var[j][0]; slot[j] = G.kinds[bi][2]
ip1 = [j for j in ip if lay[j] == 1]
rng = np.random.default_rng(66)
# diagonal: all private data solve; conservation
N = 600
vals = np.zeros((N, len(G.var)), dtype=np.int64)
s = rng.integers(0, p, len(iu)); vals[:, iu] = s; vals[:, iv] = s; vals[:, ip] = rng.integers(0, p, (N, len(ip)))
E = G.evaluate(vals) % p
diag_solve = int((~E[:, cp].any(axis=1)).sum()); diag_opp = bool(((E[:, cu] + E[:, cv]) % p == 0).all()); diag_nz = int(E[:, cu].any(axis=1).sum())
# off the diagonal: sample with private layer-1 data zero (where solutions lie) and fully random
off = {"solutions": 0, "flow nonzero": 0, "opposite": True, "random-data solutions with nonzero layer-1 parts": 0}
for trial in range(4):
    su, sv = rng.integers(0, p, len(iu)), rng.integers(0, p, len(iv))
    if not (su - sv).any(): continue
    for zero1 in (True, False):
        vals = np.zeros((3000, len(G.var)), dtype=np.int64)
        vals[:, iu] = su; vals[:, iv] = sv; vals[:, ip] = rng.integers(0, p, (3000, len(ip)))
        if zero1: vals[:, ip1] = 0
        E = G.evaluate(vals) % p
        ok = ~E[:, cp].any(axis=1)
        off["solutions"] += int(ok.sum()); off["flow nonzero"] += int(E[ok][:, cu].any(axis=1).sum())
        off["opposite"] &= bool(((E[ok][:, cu] + E[ok][:, cv]) % p == 0).all())
        if not zero1: off["random-data solutions with nonzero layer-1 parts"] += int((ok & vals[:, ip1].any(axis=1)).sum())
report("2 conservation (endpoints opposite)", diag_solve == N and diag_opp and diag_nz > N // 2 and off["opposite"] and off["solutions"] > 0,
       {"diagonal samples": N, "solve": diag_solve, "opposite": diag_opp, "flow nonzero": diag_nz, "off-diagonal": off})
report("3 off the diagonal the flow vanishes on solutions", off["flow nonzero"] == 0 and off["random-data solutions with nonzero layer-1 parts"] == 0,
       off)


# 4 bilinearity at the diagonal and the Fourier transform
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


npv = len(ip)
ms = monos(npv, 3)
X = rng.integers(0, p, (3 * len(ms), npv))
vals = np.zeros((len(X), len(G.var)), dtype=np.int64); vals[:, iu] = s; vals[:, iv] = s; vals[:, ip] = X
Y = G.evaluate(vals)[:, cu] % p
coef, bad = solve_any(evalm(X, ms), Y, p)
Xv = rng.integers(0, p, (300, npv))
vals = np.zeros((len(Xv), len(G.var)), dtype=np.int64); vals[:, iu] = s; vals[:, iv] = s; vals[:, ip] = Xv
exact = (not bad.any()) and bool(((evalm(Xv, ms) @ coef) % p == G.evaluate(vals)[:, cu] % p).all())
used = [m for m, row in zip(ms, coef) if np.any(row % p)]
pos = {j: q for q, j in enumerate(ip)}
bil = all(len(m) == 2 and {lay[ip[m[0]]], lay[ip[m[1]]]} == {1, 2} and slot[ip[m[0]]] != slot[ip[m[1]]] for m in used)
# N(mu) = sum over private data of omega^<mu, f>: bilinear f = sum_m c_m x_i x_j with x_i layer 1 (slot s) and x_j layer 2 (other slot)
k = len(cu)
first = sorted({q for m in used for q in m if lay[ip[q]] == 1})
others = npv - len(first)
Nhat = []
for mu in itertools.product(range(p), repeat=k):
    mu = np.array(mu, dtype=np.int64)
    cnt = 0
    for a in itertools.product(range(p), repeat=len(first)):
        lin = np.zeros(npv, dtype=np.int64)
        for m, row in zip(ms, coef):
            if not np.any(row % p) or len(m) != 2: continue
            i, j = m if lay[ip[m[0]]] == 1 else (m[1], m[0])
            lin[j] = (lin[j] + int((row @ mu) % p) * a[first.index(i)]) % p
        cnt += int(not lin.any())
    Nhat.append(cnt * p ** others)
report("4 diagonal flow bilinear, Fourier transform positive", exact and bil and min(Nhat) >= 1 and Nhat[0] == p ** npv,
       {"exact interpolation": exact, "monomials used": [[f"{lay[ip[i]]}:{slot[ip[i]]}" for i in m] for m in used],
        "bilinear in layer-1 x layer-2 of the other slot": bil, "N(0)": Nhat[0], "F_max": p ** npv, "min N(mu)": min(Nhat),
        "distinct N values": sorted(set(Nhat))})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-PAIRS-20261027-001F-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out, "seconds": round(time.time() - T0, 1)}, fh,
                  indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T0, 1), "s")
