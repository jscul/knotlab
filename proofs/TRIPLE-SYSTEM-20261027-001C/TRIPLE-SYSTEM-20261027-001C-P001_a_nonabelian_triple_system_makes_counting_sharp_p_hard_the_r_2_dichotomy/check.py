"""Checks for TRIPLE-SYSTEM-20261027-001C-P001.

  1 Dynkin form: for P4 and P4B, (1/3) sum_w M_j(w) [X_w1, [X_w2, X_w3]] expands back to sum_w M_j(w) X_w (so W_j^(3) is that
    Lie element), and W_0^(3) = -[X1, [X2, X3]] for P4
  2 one-parameter subgroups: g -> exp(c(g) A) theta^psi(g) is a homomorphism on Aff(F_p) for random A in n-, for every test algebra
  3 Lemma 5.2: for every nonabelian test algebra there is s* with <B(., ., .), s*> nonzero; for the small ones the count
    #{(pi2, pi3) : <B(pi2, pi3, .), s*> = 0} is at least 1 and strictly below p^(2d)
  4 the abelian test algebras have B = 0 (ticket A's side)
  5 experiment TRIPLE-SYSTEM-20261027-001B-E001 supported, ticket A Proved
Run: python3 -B check.py [--write]"""
import glob
import itertools
import json
import os
import sys
import time
import numpy as np

T_START = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP = glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0]
sys.path.insert(0, EXP)
from tsfix import algebras  # noqa: E402  (experiment B's algebra list, read-only)
from lm import Grp, triple_system  # noqa: E402
import mlib  # noqa: E402

out = {}
ok_all = True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:700], flush=True)


# ---------------------------------------------------------------- 1 Dynkin form of the conjugators' degree-3 parts
def assoc_bracket(a, b):
    outp = {}
    for wa, ca in a.items():
        for wb, cb in b.items():
            outp[wa + wb] = outp.get(wa + wb, 0) + ca * cb
            outp[wb + wa] = outp.get(wb + wa, 0) - ca * cb
    return {w: v for w, v in outp.items() if v}


BIG = (1 << 61) - 1
ok = True
detail = {}
for name, word in (("P4", mlib.P4), ("P4B", mlib.P4B)):
    st = mlib.artin_conj(word, 4)
    for j, (W, g) in enumerate(st):
        mg = mlib.magnus(W, 3, BIG)
        M = {k: (v if v < BIG // 2 else v - BIG) for k, v in mg.items() if len(k) == 3}
        lie = {}
        for (i1, i2, i3), v in M.items():
            br = assoc_bracket({(i1,): 1}, assoc_bracket({(i2,): 1}, {(i3,): 1}))
            for w, c in br.items():
                lie[w] = lie.get(w, 0) + v * c
        lie = {w: c for w, c in lie.items() if c}
        ok &= all(lie.get(w, 0) == 3 * M.get(w, 0) for w in set(lie) | set(M))      # (1/3) * Dynkin = M
        if name == "P4" and j == 0:
            ref = assoc_bracket({(1,): 1}, assoc_bracket({(2,): 1}, {(3,): 1}))
            ok &= all(M.get(w, 0) == -ref.get(w, 0) for w in set(M) | set(ref))
        detail[f"{name} W_{j}"] = {str(k): v for k, v in M.items()}
report("1 Dynkin form", ok, detail)

# ---------------------------------------------------------------- 2 one-parameter subgroups
ok = True
for p in (5, 7):
    rng = np.random.default_rng(p)
    for name, A in algebras(p).items():
        L = A["L"]
        G = Grp(L)
        minus = [k for k in range(L.D) if L.sign[k] == -1]
        Av = np.zeros((1, L.D), dtype=np.int64)
        Av[0, minus] = rng.integers(0, p, len(minus))

        def rho(c, e):                       # (c, e) in Aff(F_p) = F_p x| <-1>: c a left cocycle value, e the parity
            return ((c * Av) % p, e)
        for (c1, e1), (c2, e2) in itertools.product([(int(rng.integers(0, p)), int(rng.integers(0, 2))) for _ in range(6)],
                                                    repeat=2):
            prod = (c1 + (-1) ** e1 * c2) % p, (e1 + e2) % 2           # group law of Aff: (c1, e1)(c2, e2)
            lhs = G.mul(rho(c1, e1), rho(c2, e2))
            rhs = rho(*prod)
            ok &= bool(((lhs[0] - rhs[0]) % p == 0).all()) and lhs[1] == rhs[1]
report("2 one-parameter subgroups", ok, {"algebras": list(algebras(5)), "primes": [5, 7]})

# ---------------------------------------------------------------- 3 and 4: Lemma 5.2 and the abelian side
ok = True
rows = {}
p = 5
for name, A in algebras(p).items():
    L = A["L"]
    minus = [k for k in range(L.D) if L.sign[k] == -1]
    d = len(minus)
    nonab = len(triple_system(L)) > 0
    row = {"d": d, "nonabelian": nonab, "abelian expected": A["abelian"]}
    ok &= nonab == (not A["abelian"])
    if nonab:
        E = np.eye(L.D, dtype=np.int64)
        # B as a tensor on the minus coordinates: B[a, b, c, :] = [[e_a, e_b], e_c]
        Bt = np.zeros((d, d, d, L.D), dtype=np.int64)
        for ia, ib, ic in itertools.product(range(d), repeat=3):
            Bt[ia, ib, ic] = L.br(L.br(E[minus[ia]:minus[ia] + 1], E[minus[ib]:minus[ib] + 1]), E[minus[ic]:minus[ic] + 1])[0]
        star = next(k for k in range(L.D) if Bt[..., k].any())
        assert L.sign[star] == -1
        t = Bt[..., star] % p                               # t[a, b, c] = <B(e_a, e_b, e_c), s*>
        row["s*"] = L.names[star]
        if d <= 5:
            pairs = 0
            P2 = np.array(list(itertools.product(range(p), repeat=d)), dtype=np.int64)
            for v2 in P2:                                   # count (pi2, pi3) with t(pi2, pi3, .) = 0 (B(pi2, pi3, pi1))
                M = np.einsum("a,abc->bc", v2, t) % p       # M[b, c]: coefficient of pi3_b pi1_c for this pi2
                Z = (P2 @ M) % p                            # for every pi3: coefficients of pi1
                pairs += int((~Z.any(axis=1)).sum())
            row["count (pi2, pi3)"] = pairs
            row["bounds"] = [1, p ** (2 * d)]
            ok &= 1 <= pairs < p ** (2 * d)
    rows[name] = row
report("3-4 Lemma 5.2 and abelian side", ok, rows)

# ---------------------------------------------------------------- 5 dependencies
resB = json.load(open(os.path.join(ROOT, "artifacts/TRIPLE-SYSTEM-20261027-001B/TRIPLE-SYSTEM-20261027-001B-E001_triple_system_steering_on_gadget_surgeries/result.json")))
resA = json.load(open(glob.glob(os.path.join(ROOT, "proofs/TRIPLE-SYSTEM-20261027-001A/*P001_*/result.json"))[0]))
report("5 dependencies", resB["verdict"] == "supported" and resA["status"] == "Proved",
       {"experiment B": resB["verdict"], "ticket A": resA["status"]})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "TRIPLE-SYSTEM-20261027-001C-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T_START, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED")
