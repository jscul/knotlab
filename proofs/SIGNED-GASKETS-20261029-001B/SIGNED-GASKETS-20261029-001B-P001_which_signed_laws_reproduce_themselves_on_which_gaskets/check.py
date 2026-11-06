"""Checks for SIGNED-GASKETS-20261029-001B-P001 (which signed laws reproduce themselves on which gaskets).

Setting as in SIGNED-GASKETS-20261029-001A (gasket_lib.py, copied from it and extended with the census tools).
  0 dependency artifacts bound by the hashes recorded in manifest.json
  1 1,168 signed laws (34 knots, weights +-1, first allowed tuple +1); the engine agrees with brute-force enumeration on 40 random
    laws at k = 2 and 3
  2 census: every signed law decided on SG_k for k = 2 to 12, exactly (integers by the Chinese remainder theorem)
  3 the families, built from their definitions, match the census exactly:
      F1 signed not-all-equal and its rotations (3 laws): every k;
      F2 their relabelings by position parity (9 laws): odd k;
      F3 (-1)^a [NAE] and its rotations (3 laws): k = 1, 2 mod 4;
      F4 their relabelings (9 laws): k = 1 mod 4;
      P  unsigned even and odd parity (2 laws): k = 2, 4, 8;
    the rest are sporadic: 30 three-excluded laws exact only at k = 3 and 12 not-all-equal laws exact only at k = 5
  4 (-1)^a [NAE] for k = 1 to 16: exact exactly when k = 1, 2 mod 4; at k = 0, 3 mod 4 its corner relation is a nonzero multiple of
    (-1)^(x_B + x_C) c(E), c = -2 at E = +-3 and 1 at E = +-1; its factor is nonzero for every k = 1, 2 mod 4 up to 22 (residues)
  5 parity (Lucas): unsigned even and odd parity are exact exactly at powers of 2 for k = 1 to 16, with factor 2^(k-1); elsewhere
    their corner relation allows all eight corner triples
  6 relabeling lemma: for every law of F1 and F3 and every relabeling, at k = 3, 5, 7, 9 the relabeled law has the parent's factor
    up to sign
  7 controls that must fire: a relabeled law of F1 is not exact at k = 4; the rotation of a non-symmetric exact law is a different
    law that is exact at the same levels (the symmetry acts nontrivially); a law with one weight changed is not exact
Run: .venv/bin/python -B check.py [--write]   (numpy)"""
import hashlib, itertools, json, os, random, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import gasket_lib as G  # noqa: E402

T0 = time.time()
out, ok_all = {}, True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:2500], flush=True)


TU = G.TUPLES
idx = lambda t: t[0] * 4 + t[1] * 2 + t[2]
name = lambda w: " ".join(("+" if w[idx(t)] > 0 else "-") + "".join(map(str, t)) for t in TU if w[idx(t)] != 0)

# ---------------------------------------------------------------- 0
man = json.load(open(os.path.join(HERE, "manifest.json")))
mism = {r: d for r, d in man["parent_bindings"].items()
        if hashlib.sha256(open(os.path.join(ROOT, r), "rb").read()).hexdigest() != d}
report("0 dependency artifacts bound by hash", not mism, {"parents": len(man["parent_bindings"]), "mismatched": mism})

# ---------------------------------------------------------------- 1 laws and engine
LAWS = G.signed_laws()


def brute(k, w):
    V = [(i, j) for i in range(k + 1) for j in range(k + 1 - i)]
    tris = [((i, j), (i + 1, j), (i, j + 1)) for i in range(k) for j in range(k - i)]
    corners = [(0, 0), (k, 0), (0, k)]
    internal = [v for v in V if v not in corners]
    R = np.zeros((2, 2, 2), dtype=object)
    for cv in TU:
        tot = 0
        for bits in itertools.product((0, 1), repeat=len(internal)):
            val = dict(zip(internal, bits)); val.update(zip(corners, cv))
            term = 1
            for (a, b, c) in tris:
                term *= w[idx((val[a], val[b], val[c]))]
                if term == 0:
                    break
            tot += term
        R[cv] = tot
    return R


rng = random.Random(29)
eng_bad = 0
for w in rng.sample(LAWS, 40):
    for k in (2, 3):
        Re, Rb = G.corner_relation(k, list(w), primes=G.PRIMES[:2]), brute(k, w)
        if any(Re[t] != Rb[t] for t in TU):
            eng_bad += 1
report("1 signed laws and the engine", len(LAWS) == 1168 and len(G.knots()) == 34 and eng_bad == 0,
       {"knots": len(G.knots()), "signed laws": len(LAWS), "engine mismatches against brute force (40 laws, k = 2, 3)": eng_bad})

# ---------------------------------------------------------------- 2 census
KMAX = 12
census = {}
lam_of = {}
for w in LAWS:
    lev = []
    for k in range(2, KMAX + 1):
        ok, lam = G.proportional(G.corner_relation(k, list(w), primes=G.PRIMES[:3]), list(w))
        if ok:
            lev.append(k)
            lam_of[(w, k)] = lam
    if lev:
        census[w] = tuple(lev)
patterns = Counter(census.values())
report("2 census of the signed laws on SG_k, k = 2 to 12", True,
       {"laws exact at some level": len(census), "level sets and their sizes": {str(k): v for k, v in sorted(patterns.items())}})

# ---------------------------------------------------------------- 3 families
w1 = tuple(G.NAE_SIGNED)
w5 = tuple(G.law({"100", "101", "110"}, {"000", "111"}))
F1 = G.orbit_s3(w1) | {G.normalize(G.complement(v)) for v in G.orbit_s3(w1)}
F3 = G.orbit_s3(w5) | {G.normalize(G.complement(v)) for v in G.orbit_s3(w5)}
F2 = {G.normalize(G.relabel(v, al, be)) for v in F1 for al, be in ((1, 0), (0, 1), (1, 1))}
F4 = {G.normalize(G.relabel(v, al, be)) for v in F3 for al, be in ((1, 0), (0, 1), (1, 1))}
even = tuple(G.normalize(G.law(set(), {"001", "010", "100", "111"})))
odd = tuple(G.normalize(G.law(set(), {"000", "011", "101", "110"})))
P = {even, odd}
ks = range(2, KMAX + 1)
pred = {}
for fam, levels in ((F1, tuple(ks)), (F2, tuple(k for k in ks if k % 2)), (F3, tuple(k for k in ks if k % 4 in (1, 2))),
                    (F4, tuple(k for k in ks if k % 4 == 1)), (P, (2, 4, 8))):
    for v in fam:
        pred[v] = levels
fam_sizes = {"F1": len(F1), "F2": len(F2), "F3": len(F3), "F4": len(F4), "P": len(P)}
disjoint = len(pred) == sum(fam_sizes.values())
match = all(census.get(v) == lv for v, lv in pred.items())
rest = {w: lv for w, lv in census.items() if w not in pred}
kinds = Counter()
for w, lv in rest.items():
    excl = len([t for t in TU if w[idx(t)] == 0])
    kinds[(excl, lv)] += 1
sporadic_ok = dict(kinds) == {(3, (3,)): 30, (2, (5,)): 12}
report("3 the families match the census; the rest is sporadic",
       disjoint and match and sporadic_ok and len(census) == 68,
       {"family sizes": fam_sizes, "families disjoint": disjoint, "every family law exact exactly at its predicted levels": match,
        "sporadic laws by (number of excluded tuples, levels)": {str(k): v for k, v in kinds.items()},
        "F1": sorted(name(v) for v in F1), "F3": sorted(name(v) for v in F3),
        "sporadic at k = 5": sorted(name(w) for w, lv in rest.items() if lv == (5,))})
out["census"] = {name(w): lv for w, lv in census.items()}

# ---------------------------------------------------------------- 4 (-1)^a [NAE]
c_shape = {t: (-1) ** (t[1] + t[2]) * (-2 if abs(sum((-1) ** x for x in t)) == 3 else 1) for t in TU}
f3 = {}
f3_ok = True
for k in range(1, 17):
    if k <= 14:
        R = G.corner_relation(k, list(w5))
        ok, lam = G.proportional(R, list(w5))
        if k % 4 in (1, 2):
            f3_ok &= ok
            f3[k] = ("exact", lam)
        else:
            mu = R[(0, 0, 1)] // c_shape[(0, 0, 1)]
            shaped = mu != 0 and all(R[t] == mu * c_shape[t] for t in TU)
            f3_ok &= (not ok) and shaped
            f3[k] = ("cosine form", mu)
    else:
        p = G.PRIMES[0]
        R = G.corner_relation_mod(k, list(w5), p)
        if k % 4 in (1, 2):
            lam = int(R[(0, 0, 1)])
            ok = lam != 0 and all((R[t] - lam * w5[idx(t)]) % p == 0 for t in TU)
            f3_ok &= ok
            f3[k] = ("exact mod p", lam)
        else:
            mu = int(R[(0, 0, 1)]) * pow(c_shape[(0, 0, 1)] % p, -1, p) % p
            shaped = mu != 0 and all((R[t] - mu * c_shape[t]) % p == 0 for t in TU)
            f3_ok &= shaped
            f3[k] = ("cosine form mod p", mu)
nz = {}
for k in [k for k in range(1, 23) if k % 4 in (1, 2)]:
    res = {p: int(G.corner_relation_mod(k, list(w5), p)[(0, 0, 1)]) % p for p in (2, 5, 7, 11, 13, G.PRIMES[0])}
    nz[k] = [p for p, r in res.items() if r != 0][:2]
f3_ok &= all(nz.values())
report("4 (-1)^a [NAE]: exact exactly at k = 1, 2 mod 4 (k <= 16), cosine form otherwise, factor nonzero to k = 22", f3_ok,
       {"by level": f3, "a prime with nonzero residue of the factor": nz})

# ---------------------------------------------------------------- 5 parity (Lucas)
par = {}
par_ok = True
for v in (even, odd):
    for k in range(1, 17):
        if k <= 14:
            R = G.corner_relation(k, list(v))
            ok, lam = G.proportional(R, list(v))
            full = all(R[t] != 0 for t in TU)
        else:
            Rm = G.corner_relation_mod(k, list(v), G.PRIMES[0])
            lam = int(Rm[(0, 0, 0)] if v[0] else Rm[(0, 0, 1)])
            ok = all((Rm[t] - lam * v[idx(t)]) % G.PRIMES[0] == 0 for t in TU) and lam != 0
            full = all(Rm[t] % G.PRIMES[0] != 0 for t in TU)
        power = k & (k - 1) == 0
        par_ok &= (ok == power) and (not power or lam == 2 ** (k - 1)) and (power or full)
        par[f"{'even' if v == even else 'odd'} k={k}"] = "exact, factor 2^(k-1)" if (ok and power) else ("all eight triples" if full else "?")
report("5 unsigned parity is exact exactly at powers of 2 (k <= 16), with factor 2^(k-1)", par_ok, par)

# ---------------------------------------------------------------- 6 relabeling lemma
rel_ok = True
rel = {}
for parent in sorted(F1 | F3):
    for al, be in ((1, 0), (0, 1), (1, 1)):
        child = G.normalize(G.relabel(parent, al, be))
        for k in (3, 5, 7, 9):
            if parent in F3 and k % 4 != 1:
                continue
            okp, lp = G.proportional(G.corner_relation(k, list(parent)), list(parent))
            okc, lc = G.proportional(G.corner_relation(k, list(child)), list(child))
            rel_ok &= okp and okc and abs(lp) == abs(lc)
            rel[f"{name(parent)} -> ({al},{be}) k={k}"] = (lp, lc)
report("6 relabeling lemma: relabeled laws keep the factor up to sign at odd levels", rel_ok, {"cases": len(rel)})

# ---------------------------------------------------------------- 7 controls
ctrl = {}
some = sorted(F2)[0]
ctrl["a relabeled law is not exact at k = 4"] = not G.proportional(G.corner_relation(4, list(some)), list(some))[0]
rot = G.normalize(G.permute(w1, (1, 2, 0)))
ctrl["a rotation of signed not-all-equal is a different law, exact at k = 2 to 6"] = rot != w1 and all(
    G.proportional(G.corner_relation(k, list(rot)), list(rot))[0] for k in range(2, 7))
bad = list(w1); bad[idx((0, 0, 1))] = 2
ctrl["changing one weight of signed not-all-equal to 2 breaks exactness at k = 3"] = not G.proportional(G.corner_relation(3, bad), bad)[0]
report("7 controls fire", all(ctrl.values()), ctrl)

out["ok"] = ok_all
out["seconds"] = round(time.time() - T0, 1)
print("ALL OK" if ok_all else "SOME CHECK FAILED", out["seconds"], "s")
if "--write" in sys.argv:
    json.dump({"schema_version": 1, "artifact_id": "SIGNED-GASKETS-20261029-001B-P001", "status": "Proved" if ok_all else "Failed",
               "checks": out}, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=str)
sys.exit(0 if ok_all else 1)
