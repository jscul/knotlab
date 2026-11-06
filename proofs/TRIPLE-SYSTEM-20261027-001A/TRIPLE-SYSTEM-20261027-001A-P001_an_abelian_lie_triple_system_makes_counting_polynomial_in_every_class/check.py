"""Checks for TRIPLE-SYSTEM-20261027-001A-P001.

  1 Lemma 1 on free nilpotent algebras with prescribed involution signs and on the examples: an abelian triple system kills every
    odd left-normed word of degree 3 and 5 in the minus part, and g = n- + [n-, n-] is a subalgebra with [n-, n-] central in it
  2 independent counts (ticket A's direct layered count, BCH group law, Wirtinger presentations) for the class-3 cross-layer
    algebra at r = 2: sector 1 = |Z1(F_p^-)|^(dim n-), sector 0 = 1
  3 the general braid model (lm.py) on gadget surgeries: the abelian class-3 and class-4 examples never obstruct (random free data
    at every layer lift); the full class-4 algebra does obstruct on the same surgeries (control)
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
sys.path.insert(0, HERE)
EXPB = glob.glob(os.path.join(ROOT, "experiments/BEYOND-CLASS2-20261027-001B/*E001_*"))[0]
sys.path.insert(1, EXPB)
sys.path.insert(2, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/BEYOND-CLASS2-20261027-001A/*P001_*"))[0])
from lm import LieAlg, LieBraidModel, free_nilpotent, triple_system  # noqa: E402
import cp_lib as C  # noqa: E402
import bc_lib as Bc  # noqa: E402
import fixtures as FX  # noqa: E402  (experiment B of the previous epic: braid fixtures, read-only)

out = {}
ok_all = True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + json.dumps(detail, default=str)[:600], flush=True)


def examples(p):
    return {
        "cross3 (x+, y-)": LieAlg(p, "x y z a b".split(), [1, 1, 2, 3, 3], [1, -1, -1, -1, 1],
                                  {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1}}),
        "cross4 mod c3": LieAlg(p, "x y z a b c1 c2".split(), [1, 1, 2, 3, 3, 4, 4], [1, -1, -1, -1, 1, -1, 1],
                                {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1}, ("x", "a"): {"c1": 1},
                                 ("y", "a"): {"c2": 1}, ("x", "b"): {"c2": 1}}),
        "cross4 (x+, y-)": LieAlg(p, "x y z a b c1 c2 c3".split(), [1, 1, 2, 3, 3, 4, 4, 4], [1, -1, -1, -1, 1, -1, 1, -1],
                                  {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1}, ("x", "a"): {"c1": 1},
                                   ("y", "a"): {"c2": 1}, ("x", "b"): {"c2": 1}, ("y", "b"): {"c3": 1}}),
        "four-way u4": LieAlg(p, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [-1, -1, -1, 1, 1, -1],
                              {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}}),
        "heisenberg (y1-, y2-)": LieAlg(p, "y1 y2 z".split(), [1, 1, 2], [-1, -1, 1], {("y1", "y2"): {"z": 1}})}


# ---------------------------------------------------------------- 1 Lemma 1
p = 7
algs = dict(examples(p))
for gens, signs, c in [("xy", [1, -1], 3), ("xy", [1, -1], 4), ("xy", [1, -1], 5), ("yv", [-1, -1], 3),
                       ("xvy", [1, 1, -1], 4), ("xvy", [1, 1, -1], 3)]:
    algs[f"free class {c} on {gens} signs {signs}"] = free_nilpotent(p, list(gens), signs, c)
rows = {}
ok = True
for name, L in algs.items():
    minus = [k for k in range(L.D) if L.sign[k] == -1]
    E = np.eye(L.D, dtype=np.int64)
    abelian = len(triple_system(L)) == 0
    odd3 = odd5 = 0
    for a, b, c in itertools.product(minus, repeat=3):
        odd3 += int(L.br(L.br(E[a:a + 1], E[b:b + 1]), E[c:c + 1]).any())
    if abelian:
        for t in itertools.product(minus, repeat=5):
            v = E[t[0]:t[0] + 1]
            for k in t[1:]:
                v = L.br(v, E[k:k + 1])
            odd5 += int(v.any())
        Zvecs = [L.br(E[a:a + 1], E[b:b + 1])[0] for a, b in itertools.combinations(minus, 2)]
        central = all(not L.br(z[None, :], E[k:k + 1]).any() for z in Zvecs for k in minus) and \
            all(not L.br(z1[None, :], z2[None, :]).any() for z1 in Zvecs for z2 in Zvecs)
        ok &= odd3 == 0 and odd5 == 0 and central
    else:
        central = None
    rows[name] = {"dim": L.D, "minus": len(minus), "class": int(L.layer.max()), "abelian triple system": abelian,
                  "nonzero odd words deg 3": odd3, "deg 5 (if abelian)": odd5, "Z central in g": central}
expected_abelian = {"cross3 (x+, y-)": True, "cross4 mod c3": True, "cross4 (x+, y-)": False, "four-way u4": False,
                    "heisenberg (y1-, y2-)": True}
ok &= all(rows[k]["abelian triple system"] == v for k, v in expected_abelian.items())
report("1 Lemma 1", ok, rows)

# ---------------------------------------------------------------- 2 independent counts (class 3, BCH group law)
ok = True
counts = []
for name, (w, n), q, sector in [("4_1", ([1, -2, 1, -2], 3), 5, 1), ("T(2,5)", ([1] * 5, 2), 5, 1),
                                ("4_1#4_1", C.connected_sum([([1, -2, 1, -2], 3)] * 2), 5, 1),
                                ("T(2,5)#T(2,5)", ([1] * 5 + [2] * 5, 3), 5, 1), ("5_2", ([1, 1, 1, 2, -1, 2], 3), 7, 1),
                                ("4_1 sector 0", ([1, -2, 1, -2], 3), 5, 0)]:
    U, rels, _ = C.presentation(w, n, 2)
    Lc = Bc.cross_layer_algebra(q, 2, 1)
    dz = len(Bc.z1(U, rels, q - 1, q))
    cnt = Bc.direct_count(Lc, U, rels, sector)
    pred = q ** (3 * dz) if sector == 1 else 1
    counts.append({"manifold": f"S^3_2({name})", "p": q, "sector": sector, "dim Z1": dz, "count": cnt, "predicted": pred})
    ok &= cnt == pred
report("2 independent counts", ok, counts)

# ---------------------------------------------------------------- 3 general braid model on gadget surgeries
ok = True
res = []
rng = np.random.default_rng(11)
for q in (5, 7):
    T = FX.tensors(q)
    for gname, (nv, edges) in {"K3": (3, [(1, 2), (2, 3), (1, 3)]), "P3": (3, [(1, 2), (2, 3)])}.items():
        word, nstr, events, leaves, N = FX.gadget(nv, edges, q)
        for name in ("cross3 (x+, y-)", "cross4 mod c3", "cross4 (x+, y-)"):
            L = examples(q)[name]
            Mo = LieBraidModel(word, nstr, L)
            bs = 16
            free = [k for k in range(L.D) if L.sign[k] == -1]
            inputs = {k: (rng.integers(0, q, (bs, len(Mo.Fix))) @ Mo.Fix) % q for k in free}
            if name == "cross4 (x+, y-)":
                meas = [L.idx["c3"]]
                o = Mo.solve({k: v for k, v in inputs.items() if k not in meas}, meas)
                s = (rng.integers(0, q, (bs, len(Mo.Fix))) @ Mo.Fix) % q
                Qv = (o[meas[0]] * Mo.y_of(s)).sum(axis=1) % q
                obstructs = bool(Qv.any())
                res.append({"p": q, "gadget": gname, "algebra": name, "obstructs (control)": obstructs})
                ok &= obstructs
            else:
                try:
                    Mo.solve(inputs, [])
                    lifted = True
                except AssertionError:
                    lifted = False
                res.append({"p": q, "gadget": gname, "algebra": name, "all samples lift": lifted, "samples": bs})
                ok &= lifted
report("3 gadget surgeries", ok, res)

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "TRIPLE-SYSTEM-20261027-001A-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T_START, 1)}, fh, indent=1, default=str)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED")
