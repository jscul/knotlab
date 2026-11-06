"""Checks for COPRIME-PAIRS-20261027-001C-P001.

  1 Theorem 1 on counts: exact counts of homomorphisms from S^3_(d/p) surgeries agree for G and for exp(m_d) x| C_d when n has a
    trivial-character generator (free class 3 on x (0), y (1) at d = 4, p = 5); m_d has class 2
  2 Lemma 5 on counts: where the kernel's characters avoid the knot's active characters, counts for G and for the quotient differ
    exactly by p^(nonzero-character dimension of the kernel); an interacting control differs
  3 Corollary 4: the examples' ideals, lower central series, quotients, hard pairs or near triples, and kernel characters
  4 the census: 850 free graded algebras (two or three generators, classes 3 and 4, d <= 12, every divisor allowed) by status
Run: python3 -B check.py [--write]"""
import glob, itertools, json, os, sys, time
from collections import Counter
from math import gcd
import numpy as np
T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, glob.glob(os.path.join(ROOT, "proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*"))[0])
sys.path.insert(1, glob.glob(os.path.join(ROOT, "experiments/COPRIME-DICHOTOMY-20261027-001B/*E002_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
from cd_lib import (GLie, BraidAlg, CyclicBraidModel, free_graded, ideal_closure, rref, rank, nullspace, solve_any, quotient,
                    root_of_unity, pair_failures, triple_failures)  # noqa: E402
import gd  # noqa: E402  (read-only: Burau matrices, summand braids)
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:900], flush=True)


# ---------------------------------------------------------------- algebra helpers
def span_rows(rows, p):
    rows = [np.array(r, dtype=np.int64) % p for r in rows if np.any(np.array(r) % p)]
    return rref(np.array(rows), p)[0] if rows else None


def m_ideal(L, d):
    gens = [L.unit(k)[0] for k in range(L.D) if L.chars[k] % d]
    return ideal_closure(L, gens) if gens else np.zeros((0, L.D), dtype=np.int64)


def lcs(L, M, upto=5):
    p, out_, cur = L.p, [M], M
    for _ in range(upto):
        if len(cur) == 0 or len(M) == 0:
            cur = np.zeros((0, L.D), dtype=np.int64)
        else:
            R = span_rows(np.concatenate([L.br(np.repeat(a[None, :], len(cur), axis=0), cur) for a in M]), p)
            cur = R if R is not None else np.zeros((0, L.D), dtype=np.int64)
        out_.append(cur)
    return out_


def char_dims(L, R, d):
    return {th: (rank(R[:, [k for k in range(L.D) if L.chars[k] % d == th]] % L.p, L.p)
                 if len(R) and any(L.chars[k] % d == th for k in range(L.D)) else 0) for th in range(d)}


def in_span(R, v, p):
    return (not np.any(v % p)) if len(R) == 0 else rank(np.vstack([R, v[None, :]]) % p, p) == rank(R, p)


def graded_rows(L, M, keep):
    if len(M) == 0: return np.zeros((0, L.D), dtype=np.int64)
    sub = M.copy()
    sub[:, [k for k in range(L.D) if not keep(k)]] = 0
    R = span_rows(sub, L.p)
    return R if R is not None else np.zeros((0, L.D), dtype=np.int64)


def subquotient(L, M, K):
    """M/K as a GLie on a homogeneous basis (M, K graded; K an ideal of M)"""
    p = L.p
    basis, cur = [], (K.copy() if len(K) else np.zeros((0, L.D), dtype=np.int64))
    for row in rref(M, p)[0]:
        if not in_span(cur, row, p):
            basis.append(row); cur = np.vstack([cur, row[None, :]]) if len(cur) else row[None, :]
    B = np.array(basis, dtype=np.int64)
    n = len(B)
    full = np.vstack([B, K]) if len(K) else B
    C = np.zeros((n, n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            X, bad = solve_any(full.T % p, (L.br(B[i:i + 1], B[j:j + 1])[0] % p)[:, None], p)
            assert not bad.any()
            C[i, j] = X[:n, 0] % p
    chars = np.array([int(L.chars[np.nonzero(b)[0][0]]) for b in B])
    layers = np.array([int(L.layer[np.nonzero(b)[0][0]]) for b in B])
    for b, c, l in zip(B, chars, layers):
        assert all(int(L.chars[k]) == c and int(L.layer[k]) == l for k in np.nonzero(b)[0]), "not homogeneous"
    return GLie(p, L.d, [f"e{i}" for i in range(n)], layers, chars, C, check=False)


def char_order(a, d):
    return d // gcd(a % d, d) if a % d else 1


def summand_roots(a, d):
    """R(a): {+-a} at odd order, {alpha : zeta_d^(alpha k) = -1} at order 2k"""
    o = char_order(a, d)
    if o % 2: return {a % d, (-a) % d}
    k = o // 2
    return {al for al in range(1, d) if (al * k) % d == d // 2}


def class_of(L, M):
    G = lcs(L, M, 5)
    return next((k for k in range(1, len(G)) if len(G[k]) == 0), None)


def transfer(L, d):
    """the instances of Theorem 3 found among the quotients m/gamma_j(m) and m/(m cap L_{>=j})"""
    M = m_ideal(L, d)
    if len(M) == 0: return []
    G = lcs(L, M, 5)
    cands = [(f"gamma_{j}(m)", G[j - 1]) for j in range(3, 6)] + \
            [(f"m cap L>={j}", graded_rows(L, M, lambda k, j=j: int(L.layer[k]) >= j)) for j in range(2, 5)]
    wins = []
    for name, K in cands:
        if len(K) == len(M): continue
        Q = subquotient(L, M, K)
        bad = {t for t, v in char_dims(L, K, d).items() if v and t % d}
        pf = pair_failures(Q, d)
        if pf:
            if len(lcs(Q, np.eye(Q.D, dtype=np.int64), 3)[2]) == 0:          # class 2: Theorem 3(i)
                for (a, b) in pf:
                    AS = {a % d, (-a) % d, b % d, (-b) % d, (a + b) % d, (-a - b) % d}
                    if not AS & bad: wins.append((name, "(i) hard pair", (a, b)))
        else:
            for a in {a % d for (a, b) in triple_failures(Q, d) if b % d in (a % d, (-a) % d)}:
                if not summand_roots(a, d) & bad: wins.append((name, "(ii) near triple", a))
    return wins


# ---------------------------------------------------------------- exact counts
def count_homs(word, n, L, zeta, p, cap=4_000_000):
    """# homomorphisms pi_1 S^3_(d/p)(closure) -> exp(L) x| C_d with every top meridian in the coset N tau"""
    A = BraidAlg(L, zeta)
    Mo = CyclicBraidModel(word, n, A, p)
    V = np.zeros((1, n, A.D), dtype=np.int64)
    for lay in range(1, int(A.layer.max()) + 1):
        for k in [k for k in range(A.D) if A.layer[k] == lay]:
            R = Mo.run(V)
            X, bad = solve_any(Mo.Lin[int(A.chars[k])], (-R[:, :, k]).T % p, p)
            V, X = V[~bad], X[:, ~bad]
            if len(V) == 0: return 0
            V[:, :, k] = X.T % p
            B = Mo.cocycles[int(A.chars[k])]
            if len(B):
                add = (np.array(list(itertools.product(range(p), repeat=len(B))), dtype=np.int64) @ B) % p
                V = np.repeat(V, len(add), axis=0)
                V[:, :, k] = (V[:, :, k] + np.tile(add, (len(V) // len(add), 1))) % p
            assert len(V) <= cap
    assert not (Mo.run(V) % p).any()
    return len(V)


def active(word, n, p, d, zeta):
    return [c for c in range(1, d)
            if len(nullspace((gd.bur_word(word, n, pow(zeta, c, p), p) - np.eye(n, dtype=np.int64)) % p, p)) > 1]


# ---------------------------------------------------------------- 1 Theorem 1
p, d = 5, 4
zeta = root_of_unity(p, d)
L = free_graded(p, d, [0, 1], 3, ["x", "y"])
M = m_ideal(L, d)
Lm = subquotient(L, M, np.zeros((0, L.D), dtype=np.int64))
rows, ok = [], True
for name, (w, nn) in [("C_2 of T(2,5)", gd.torus_cable(5, 2)), ("4_1", gd.AMPH["4_1"]), ("5_2", gd.CHIRAL["5_2"]),
                      ("3_1", gd.CHIRAL["3_1"])]:
    a, b = count_homs(w, nn, L, zeta, p), count_homs(w, nn, Lm, zeta, p)
    rows.append({"knot": name, "active characters": active(w, nn, p, d, zeta), "G": a, "exp(m) x| C_d": b, "equal": a == b})
    ok &= a == b
cls_m = class_of(L, M)
report("1 reduction to m_d (counts)", ok and cls_m == 2 and Lm.D == 4,
       {"algebra": "free class 3 on x (0), y (1), d = 4, p = 5", "dim n": L.D, "dim m": Lm.D, "class of m": cls_m, "rows": rows})

# ---------------------------------------------------------------- 2 Lemma 5
rows, ok = [], True
for (p, d, knots) in [(7, 3, [("6_3", gd.AMPH["6_3"]), ("6_1", gd.CHIRAL["6_1"]), ("3_1", gd.CHIRAL["3_1"])]),
                      (5, 4, [("T(2,5)", ([1] * 5, 2)), ("5_2", gd.CHIRAL["5_2"]), ("C_2 of T(2,5)", gd.torus_cable(5, 2))])]:
    zeta = root_of_unity(p, d)
    L = free_graded(p, d, [1, 1], 3)
    M = m_ideal(L, d)
    K = lcs(L, M, 3)[2]
    kd = char_dims(L, K, d)
    Q = subquotient(L, M, K)
    nz = sum(v for t, v in kd.items() if t % d)
    for name, (w, nn) in knots:
        A = active(w, nn, p, d, zeta)
        inert = not any(kd[t] for t in A)
        a, b = count_homs(w, nn, L, zeta, p), count_homs(w, nn, Q, zeta, p)
        match = a == b * p ** nz
        rows.append({"p": p, "d": d, "knot": name, "active": A, "kernel characters": {t: v for t, v in kd.items() if v},
                     "inert": inert, "G": a, "G/K": b, "matches p^(nonzero kernel dim)": match})
        ok &= match == inert
ok &= any(not r["inert"] for r in rows) and sum(r["inert"] for r in rows) >= 4
report("2 inert lifting (counts, with an interacting control)", ok, rows)

# ---------------------------------------------------------------- 3 Corollary 4
rows, ok = {}, True
for d, p in [(3, 7), (4, 13), (5, 11), (6, 7), (7, 29), (8, 17), (9, 19)]:
    L = free_graded(p, d, [0, 1], 3, ["x", "y"])
    if (2 * 1) % d == 0: continue
    M = m_ideal(L, d)
    good = class_of(L, M) == 2 and any(w[1] == "(i) hard pair" for w in transfer(L, d))
    rows[f"cross-layer group, d={d}"] = good
    ok &= good
for d, p in [(3, 7), (4, 13), (5, 11), (6, 7), (7, 29), (8, 17), (9, 19), (10, 11), (12, 13)]:
    L = free_graded(p, d, [1, 1], 3)
    M = m_ideal(L, d)
    G3 = lcs(L, M, 3)[2]
    chars3 = {t for t, v in char_dims(L, G3, d).items() if v}
    inert_i = any(w[0] == "gamma_3(m)" and w[1] == "(i) hard pair" for w in transfer(L, d))
    predicted = d not in (4, 5)
    rows[f"free class 3 on (1,1), d={d}"] = {"gamma_3 characters": sorted(chars3), "inert (i)": inert_i, "predicted": predicted}
    ok &= inert_i == predicted
for d, p in [(5, 11), (7, 29)]:
    L = free_graded(p, d, [1, d - 1], 4)
    M = m_ideal(L, d)
    G = lcs(L, M, 5)
    Q3 = subquotient(L, M, G[2])
    w = transfer(L, d)
    good = not pair_failures(Q3, d) or len(lcs(Q3, np.eye(Q3.D, dtype=np.int64), 3)[2]) > 0
    has_ii = any(x[0] == "gamma_4(m)" and x[1] == "(ii) near triple" for x in w)
    no_i_at_gamma3 = not any(x[0] == "gamma_3(m)" for x in w)
    rows[f"free class 4 on (1,-1), d={d}"] = {"(ii) through gamma_4": has_ii, "no (i) through gamma_3": no_i_at_gamma3}
    ok &= has_ii and no_i_at_gamma3
L = free_graded(13, 4, [1, 1, 0], 3, ["y", "v", "x"])
yv = L.br(L.unit(L.idx["y"]), L.unit(L.idx["v"]))
Q = quotient(L, [L.br(yv, L.unit(L.idx["y"]))[0], L.br(yv, L.unit(L.idx["v"]))[0]])
M = m_ideal(Q, 4)
crit2 = not pair_failures(Q.coarsen(2)) and not triple_failures(Q.coarsen(2))
good = class_of(Q, M) == 2 and crit2 and bool(pair_failures(Q, 4))
rows["three-generator example, d=4"] = {"criterion at 2": crit2, "P2_4 fails": bool(pair_failures(Q, 4)), "class of m": class_of(Q, M)}
ok &= good
report("3 Corollary 4", ok, rows)

# ---------------------------------------------------------------- 4 census
PRIMES = {3: 7, 4: 13, 5: 11, 6: 7, 7: 29, 8: 17, 9: 19, 10: 11, 12: 13}
census, examples = [], {}
for d in [3, 4, 5, 6, 7, 8, 9, 10, 12]:
    p = PRIMES[d]
    units = [u for u in range(1, d) if gcd(u, d) == 1]
    seen = set()
    for k in (2, 3):
        for chars in itertools.combinations_with_replacement(range(d), k):
            canon = min(tuple(sorted((u * c) % d for c in chars)) for u in units)
            if canon in seen or not any(c % d for c in chars): continue
            seen.add(canon)
            for cls in (3, 4):
                L = free_graded(p, d, list(chars), cls)
                divs = [e for e in range(2, d + 1) if d % e == 0]
                res = {e: (bool(pair_failures(L.coarsen(e))), bool(triple_failures(L.coarsen(e)))) for e in divs}
                failing = [e for e in divs if any(res[e])]
                if not failing: status = "criterion at every order"
                elif any(not res[e][0] and res[e][1] for e in failing): status = "triple theorem at a divisor"
                elif any(transfer(L.coarsen(e), e) for e in failing): status = "residual, decided here"
                else: status = "residual, interacting"
                census.append({"d": d, "generator characters": chars, "class": cls, "status": status})
counts = Counter(r["status"] for r in census)
expected = {"criterion at every order": 10, "triple theorem at a divisor": 511, "residual, decided here": 153,
            "residual, interacting": 176}
ex = [(r["d"], r["generator characters"], r["class"]) for r in census if r["status"] == "residual, interacting"][:12]
report("4 census", dict(counts) == expected, {"algebras": len(census), "counts": dict(counts), "first interacting": ex})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "COPRIME-PAIRS-20261027-001C-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out, "census": census,
                   "seconds": round(time.time() - T0, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED", round(time.time() - T0, 1), "s")
