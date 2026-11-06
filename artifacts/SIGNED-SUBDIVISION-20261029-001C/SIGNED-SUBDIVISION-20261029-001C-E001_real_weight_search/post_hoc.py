"""Post-hoc analysis of SIGNED-SUBDIVISION-20261029-001C-E001 (exploratory, not part of the frozen decision rule).
(1) The single open-shape candidate (S1 atom excluding 000 on both orientations, scale 3, sign class 7): its 2-torus point, its
    non-degeneracy, and its residual on the coarse 3-torus.  (2) The two exact classes the joint stage missed at scale 2: their
    joint and 4-torus residuals at theta = 0 (the plus-minus-one weighting) and at the recorded best point.
Run: .venv/bin/python -B post_hoc.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "SIGNED-SUBDIVISION-20261029-001C", "SIGNED-SUBDIVISION-20261029-001C-E001_real_weight_search"))
import run as E  # noqa: E402
S, R = E.S, E.R
r = json.load(open(os.path.join(HERE, "result.json")))
shapes = S.rule_shapes()
names = [E.name(*x) for x in shapes]
out = {"open candidates": [], "missed exact classes": []}
for x in r["records"]:
    if x["label"] == "open" and x["best"] < E.CAND:
        s, P1, P2 = shapes[names.index(x["shape"])]
        free, _ = R.slice_free(P1, P2)
        th = np.array(x["theta"])
        rec = {"shape": x["shape"], "scale": x["scale"], "class": x["class"], "magnitudes": np.exp(th).tolist()}
        for m in (2, 3):
            res = E.side_residual(m, x["scale"], *E.weights(P1, P2, tuple(x["sign"]), free, th))
            rec[f"side {m}"] = {"largest residual": float(np.max(np.abs(res))),
                                "non-degeneracy": E.nondegeneracy(th, P1, P2, tuple(x["sign"]), free, x["scale"], m)}
        out["open candidates"].append(rec)
for x in r["records"]:
    if x["label"] == "affine" and x["best"] < E.CAND and not x.get("confirmed") and x["scale"] == 2 and x["class"] == 0:
        s, P1, P2 = shapes[names.index(x["shape"])]
        free, _ = R.slice_free(P1, P2)
        z = np.zeros(len(free)); th = np.array(x["theta"])
        out["missed exact classes"].append({"shape": x["shape"], "class": x["class"], "recorded best theta": x["theta"],
            "joint residual at theta = 0": float(np.linalg.norm(E.resid(z, P1, P2, tuple(x["sign"]), free, 2, (2, 3)))),
            "4-torus residual at theta = 0": float(np.linalg.norm(E.resid(z, P1, P2, tuple(x["sign"]), free, 2, (4,)))),
            "joint residual at the recorded best theta": float(np.linalg.norm(E.resid(th, P1, P2, tuple(x["sign"]), free, 2, (2, 3))))})
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "post_hoc.json"), "w"), indent=1)
