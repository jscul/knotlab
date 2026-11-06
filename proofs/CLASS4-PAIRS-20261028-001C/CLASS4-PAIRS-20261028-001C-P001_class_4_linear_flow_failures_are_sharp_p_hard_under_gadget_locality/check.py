"""Checks for CLASS4-PAIRS-20261028-001C-P001 (class-4 linear flows under gadget locality).

  1 character structure of free class 4 on (1, 1), (0, 1, 1), (1, 1, 1) at d = 5 and of (2, 2), (0, 2, 2), (2, 2, 2) at d = 10
    coarsened to order 5: every component of m_d in its layer k <= 4 has character k (mod 5, scaled by the unit 3 for d = 10);
    hence, for slots (1, 1, 2) (scaled), slot 2 has no layer-1 data, no layer-4 component lies at a root of slot 2, and the vertex
    and slot-1 free data (layers 1-3) lie at one character of their root pair
  2 for free class 4 on (1, 1), d = 5, p = 11, slots (1, 1, 2), exhaustively over the 11^5 private configurations at a diagonal and
    at a pair-failing pair: the solution set splits as S_1 x U(pi_1) with U linear, the endpoint terms are linear in slot-2 data with
    no slot-2-free part, 200 random Fourier values Ahat(lambda, lambda') are real and non-negative, F(s, s) = F_max and
    1 <= F(0, D) < F_max
  3 the frozen experiment CLASS4-PAIRS-20261028-001B-E001: contract and result bound by hash; verdict supported
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




# ---------------------------------------------------------------- 1 character structure
def layer_chars(L, d):
    p = L.p
    M = m_ideal(L, d)
    G = lcs(L, M, 5)
    Z = np.zeros((0, L.D), dtype=np.int64)
    out = {}
    for k in range(4):
        hi = G[k + 1] if len(G[k + 1]) else Z
        comp = complement_rows(L, G[k], hi, p) if len(G[k]) else Z
        out[k + 1] = sorted({int(L.chars[c]) % d for row in comp for c in range(L.D) if row[c] % p})
    return out


rows1, ok1 = [], True
for (d0, chars, unit) in [(5, [1, 1], 1), (5, [0, 1, 1], 1), (5, [1, 1, 1], 1), (10, [2, 2], 3), (10, [0, 2, 2], 3), (10, [2, 2, 2], 3)]:
    L = free_graded(11, d0, chars, 4).coarsen(5) if d0 == 10 else free_graded(11, 5, chars, 4)
    lc = layer_chars(L, 5)
    scaled = {k: sorted({(c * unit) % 5 for c in v}) for k, v in lc.items()}
    good = all(scaled[k] == [k % 5] for k in range(1, 5))
    R0 = R_of(1, 5); R2 = R_of(2, 5)
    lf = not (set(scaled[1]) & R2); s2 = not (set(scaled[4]) & R2)
    one = len(set(scaled[1] + scaled[2] + scaled[3]) & R0) == 1
    rows1.append({"d": d0, "chars": chars, "layer characters (scaled to the (1, 1) labelling)": scaled, "layer k at character k": good,
                  "LF": lf, "no slot-2 equations in degree 4": s2, "vertex/slot-1 data at one character": one})
    ok1 &= good and lf and s2 and one
report("1 character structure of the six algebras", ok1, rows1)


# ---------------------------------------------------------------- 2 exhaustive single-edge structure for (1, 1)
p, d = 11, 5
L = free_graded(p, d, [1, 1], 4)
G = Gadget(L, d, p, summand_types(p, d, (1, 1, 2)), 2, [(0, 1)])
vs, es = G.var_sites(), G.eq_sites()
iu = [j for j, s_ in enumerate(vs) if s_ == ("v", 0)]; iv = [j for j, s_ in enumerate(vs) if s_ == ("v", 1)]
ip = [j for j, s_ in enumerate(vs) if s_[0] == "e"]
q1 = [q for q, j in enumerate(ip) if G.kinds[G.var[j][0]][2] == 1]; q2 = [q for q, j in enumerate(ip) if G.kinds[G.var[j][0]][2] == 2]
cu = [c for c, s_ in enumerate(es) if s_ == ("v", 0)]; cv = [c for c, s_ in enumerate(es) if s_ == ("v", 1)]; cp = [c for c, s_ in enumerate(es) if s_[0] == "e"]
combos = np.array(list(itertools.product(range(p), repeat=len(ip))), dtype=np.int64)
r = np.random.default_rng(29)
vk = [iu.index(j) for j in iu if int(L.layer[G.var[j][1]]) == 1 and int(L.chars[G.var[j][1]]) % d == 1]
D = np.zeros(len(iu), dtype=np.int64); D[vk] = r.integers(1, p, len(vk))
rows2, ok2 = [], True
Fmax = p ** len(ip)
for name, (su, sv) in [("diagonal", (lambda x: (x, x))(r.integers(0, p, len(iu)))), ("pair-failing (0, D)", (np.zeros(len(iu), dtype=np.int64), D))]:
    vals = np.zeros((len(combos), len(G.var)), dtype=np.int64); vals[:, iu] = su; vals[:, iv] = sv; vals[:, ip] = combos
    E = evaluate_chunked(G, vals) % p
    z = np.zeros((1, len(G.var)), dtype=np.int64); z[0, iu] = su; z[0, iv] = sv
    E0 = G.evaluate(z)[0] % p
    sol = ~E[:, cp].any(axis=1)
    S = combos[sol]; fu = (E[sol][:, cu] - E0[cu]) % p; fv = (E[sol][:, cv] - E0[cv]) % p
    by1 = {}
    for x, a, b in zip(S.tolist(), fu.tolist(), fv.tolist()):
        by1.setdefault(tuple(x[q] for q in q1), {})[tuple(x[q] for q in q2)] = (tuple(a), tuple(b))
    sub, lin, free0 = True, True, True
    for k1, U in by1.items():
        zero = tuple(0 for _ in q2)
        if zero not in U: sub = False; continue
        if any(U[zero][0]) or any(U[zero][1]): free0 = False
        keys = list(U)
        for _ in range(min(80, len(keys) ** 2)):
            a, b = keys[r.integers(0, len(keys))], keys[r.integers(0, len(keys))]
            c = tuple((x + y) % p for x, y in zip(a, b))
            if c not in U: sub = False; break
            if any((U[a][0][i] + U[b][0][i] - U[c][0][i]) % p for i in range(len(cu))) or \
               any((U[a][1][i] + U[b][1][i] - U[c][1][i]) % p for i in range(len(cv))): lin = False
    lam = r.integers(0, p, (200, len(cu))); lamp = r.integers(0, p, (200, len(cv)))
    ph = (lam @ fu.T + lamp @ fv.T) % p
    Ah = np.exp(2j * np.pi * ph / p).sum(axis=1)
    nonneg = bool(np.abs(Ah.imag).max() < 1e-6 and Ah.real.min() > -1e-6)
    rec = {"pair": name, "solutions": int(sol.sum()), "F_max": Fmax, "split S_1 x U with U linear": sub,
           "endpoint terms linear in slot-2 data": lin, "no slot-2-free part": free0, "Fourier non-negative (200)": nonneg,
           "min Fourier": round(float(Ah.real.min()), 3), "vertex rows at zero data vanish": bool(not E0[cu + cv].any()),
           "zero data solve": bool(not E0[cp].any())}
    rows2.append(rec)
    ok2 &= sub and lin and free0 and nonneg and rec["vertex rows at zero data vanish"] and rec["zero data solve"]
rw = rows2[0]["solutions"] == Fmax and 1 <= rows2[1]["solutions"] < Fmax
report("2 exhaustive single-edge structure, free class 4 on (1, 1)", ok2 and rw, {"pairs": rows2, "F(s, s) = F_max and 1 <= F(0, D) < F_max": rw})

# ---------------------------------------------------------------- 3 the experiment
import hashlib  # noqa: E402
EB = glob.glob(os.path.join(ROOT, "experiments/CLASS4-PAIRS-20261028-001B/*E001_*"))[0]
AB = glob.glob(os.path.join(ROOT, "artifacts/CLASS4-PAIRS-20261028-001B/*E001_*"))[0]
man = json.load(open(os.path.join(HERE, "manifest.json")))
bind = man.get("parent_bindings", {})
paths = [os.path.relpath(os.path.join(EB, "contract.json"), ROOT), os.path.relpath(os.path.join(AB, "result.json"), ROOT)]
bound = all(p_ in bind and hashlib.sha256(open(os.path.join(ROOT, p_), "rb").read()).hexdigest() == bind[p_] for p_ in paths)
verdict = json.load(open(os.path.join(AB, "result.json")))["verdict"]
report("3 experiment CLASS4-PAIRS-20261028-001B-E001 bound and supported", bound and verdict == "supported", {"bound": bound, "verdict": verdict})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "CLASS4-PAIRS-20261028-001C-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out, "seconds": round(time.time() - T0, 1)}, fh,
                  indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T0, 1), "s")
