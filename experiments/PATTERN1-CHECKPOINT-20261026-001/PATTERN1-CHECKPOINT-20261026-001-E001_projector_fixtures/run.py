"""PATTERN1-CHECKPOINT-20261026-001-E001: run the frozen contract.

1. machinery controls (validate.py): any failure makes the run invalid;
2. the fixtures K2 and the digon built by the projector construction: H1, psi, twisted cohomology dimensions, the actual
   lifting obstruction of the free class-2 group on three generators in the sectors psi^1 and psi^5, and leaf purity;
3. the discriminating controls: bases without claspers, an unbalanced band (digon), reversed windings (K2), and
   unprojected leaves (K2).
Writes rows.json, result.json and the surgery descriptions to the artifact directory given as the first argument.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py <artifact_dir>
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

import pc_core as PC  # noqa: E402  (puts cp_lib on the path)
from pc_core import Comp, Diagram, rank_mod, P
from pc_fixtures import build_fixture, surgery_counts, leaf_functionals
import validate

FIX = {
    "K2": (["x", "x", "y", "t"], [(0, 1, 2, 3)]),
    "digon": (["x", "x", "y", "y", "t", "t"], [(0, 1, 2, 4), (0, 1, 3, 5)]),
}
SLOT_CHI = {"l": 3, "y": 2, "t": 6}
S1, S5 = "psi^1 (zeta, zeta^2, zeta^3)", "psi^5 (zeta^5, zeta^4, zeta^3)"

EXPECT = {
    ("K2", "projector"): {S1: 133, S5: 2401, "dims": {3: 2, 2: 1, 6: 1, 4: 1, 5: 2}},
    ("digon", "projector"): {S1: 2737, S5: 117649, "dims": {3: 2, 2: 2, 6: 2, 4: 2, 5: 2}},
    ("K2", "base only"): {S1: 2401, S5: 2401, "dims": {3: 2, 2: 1, 6: 1, 4: 1, 5: 2}},
    ("digon", "base only"): {S1: 117649, S5: 117649, "dims": {3: 2, 2: 2, 6: 2, 4: 2, 5: 2}},
    ("digon", "unbalanced band"): {S1: 361, S5: 117649, "dims": {3: 2, 2: 2, 6: 2, 4: 2, 5: 2}},
    ("K2", "reversed windings"): {S1: 2401, S5: 133, "dims": {3: 2, 2: 1, 6: 1, 4: 1, 5: 2}},
    ("K2", "unprojected leaves"): {S1: 133, S5: 133, "dims": {3: 2, 2: 1, 6: 1, 4: 1, 5: 2}},
}
VARIANTS = {"projector": {"wdir": -1}, "unbalanced band": {"wdir": -1, "unbalanced_edge": 1},
            "reversed windings": {"wdir": 1}, "unprojected leaves": {"wdir": -1, "simple": True}}


def describe(comps, info):
    return {"base braid word": info["word"], "strands": info["n"], "arc choice (summand: (gap after crossing k, position q))":
            {str(k): list(v) for k, v in info["choice"].items()}, "layout crossing heights": info["layout_y"],
            "components": [{"name": c.name, "role": c.role, "framing": c.framing, "psi on meridian": c.psi,
                            "polygon": [[round(x, 6) for x in p] for p in c.pts]} for c in comps]}


def purity(comps):
    """functionals of the leaves on all five nontrivial characters, B components dropped and leaves forgotten"""
    K = comps[0]
    leaves = [c for c in comps if c.role == "leaf"]
    F, _ = leaf_functionals(K, leaves)
    rows, ok = {}, True
    for lf in leaves:
        want = SLOT_CHI[lf.name[0]]
        supp = {chi: [int(x) for x in F[chi][lf.name]] for chi in F}
        good = any(supp[want]) and all(not any(v) for chi, v in supp.items() if chi != want)
        rows[lf.name] = {"slot character": want, "functional by character": supp, "pure": good}
        ok &= good
    return rows, ok, F


def main(outdir):
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = {"machinery": validate.main()}
    print("machinery ok:", out["machinery"]["ok"], flush=True)
    rows = {}
    for fix, (slots, edges) in FIX.items():
        for variant in ("base only", "projector", "unbalanced band", "reversed windings", "unprojected leaves"):
            if (fix, variant) not in EXPECT:
                continue
            comps, info, L, base = build_fixture(slots, edges, **VARIANTS.get(variant, {"wdir": -1}))
            if variant == "base only":
                comps = comps[:1]
            res = surgery_counts(comps, f"{fix} / {variant}")
            exp = EXPECT[(fix, variant)]
            res["expected"] = {S1: exp[S1], S5: exp[S5], "dims": exp["dims"]}
            res["matches"] = {
                "H1 = Z/6": res["H1_invariant_factors"] == [6],
                "clasper-only H1 trivial": res["clasper_only_H1_factors"] == [],
                "psi well defined and onto": res["psi_well_defined"] and res["meridian_psi"] == 1,
                "dims": res["dims"] == exp["dims"],
                S1: res["sectors"][S1]["free3"] == exp[S1],
                S5: res["sectors"][S5]["free3"] == exp[S5],
            }
            if variant in ("projector", "unbalanced band"):
                prow, pok, F = purity(comps)
                res["leaf purity"] = prow
                res["matches"]["leaves pure"] = pok
                if fix == "digon":
                    l0, l1 = np.array(F[3]["l0"]), np.array(F[3]["l1"])
                    prop = rank_mod(np.array([l0, l1])) == 1
                    res["matches"]["ell_1 and ell_2 proportional on V_zeta (balanced)"] = prop if variant == "projector" else (not prop)
                    res["matches"]["y_1, y_2 independent; t_1, t_2 independent"] = (
                        rank_mod(np.array([F[2]["y0"], F[2]["y1"]])) == 2 and rank_mod(np.array([F[6]["t0"], F[6]["t1"]])) == 2)
            if variant == "projector":
                (outdir / f"surgery_{fix}.json").write_text(json.dumps(describe(comps, info)) + "\n")
            res["ok"] = all(res["matches"].values())
            rows[f"{fix} / {variant}"] = res
            print(f"{fix} / {variant}:", {k: v for k, v in res["matches"].items()}, res["sectors"][S1]["free3"],
                  res["sectors"][S5]["free3"], res["seconds"], "s", flush=True)
    out["rows"] = rows
    fixtures_ok = all(rows[f"{f} / projector"]["ok"] for f in FIX)
    controls_ok = all(r["ok"] for k, r in rows.items() if not k.endswith("/ projector"))
    pre = out["machinery"]["ok"] and all(rows[k]["matches"]["H1 = Z/6"] and rows[k]["matches"]["psi well defined and onto"]
                                         for k in rows)
    verdict = "invalid" if not pre else ("supported" if fixtures_ok and controls_ok else "refuted")
    out["verdict"] = verdict
    out["seconds"] = round(time.time() - t0, 1)
    (outdir / "rows.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    summary = {"schema_version": 1, "experiment_id": "PATTERN1-CHECKPOINT-20261026-001-E001", "verdict": verdict,
               "N_psi": {f: rows[f"{f} / projector"]["sectors"][S1]["free3"] for f in FIX},
               "predicted": {"K2": 133, "digon": 2737},
               "fixtures_ok": fixtures_ok, "controls_ok": controls_ok, "machinery_ok": out["machinery"]["ok"],
               "failed": [f"{k}: {m}" for k, r in rows.items() for m, v in r["matches"].items() if not v],
               "seconds": out["seconds"]}
    (outdir / "result.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0 if verdict == "supported" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out"))
