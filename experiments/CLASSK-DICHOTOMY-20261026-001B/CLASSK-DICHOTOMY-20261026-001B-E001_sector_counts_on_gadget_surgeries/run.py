"""CLASSK-DICHOTOMY-20261026-001B-E001: run the frozen contract.

1. machinery controls (validate.py): any failure makes the run invalid;
2. eight gadget surgeries built by the projector construction (patterns P1, P2, P3; K2, the digon, K2 + K2; (p, r) = (7, 6)
   and (5, 4)): H1, psi, dimensions, leaf purity (K2 fixtures), every cup-product class, for the closed r-surgery and for the
   knot exterior;
3. per fixture, test group and sector k: the measured kernel count against the frozen prediction (predictions.json), closed
   and knot group; and the checkpoint values 133 and 2401 on P1-K2.
Writes rows.json, result.json and the surgery descriptions to the artifact directory given as the first argument.

    /home/jscul/p-vs-np-contact-first/.venv/bin/python -B run.py <artifact_dir>
"""
import json
import sys
import time
from pathlib import Path

import ck_core as PC  # noqa: E402
from ck_core import Comp
from ck_fixtures import Spec, build_fixture, cohomology_data, leaf_functionals, measured_count
from ck_specs import FIXTURES, groups_for, L
import validate

HERE = Path(__file__).resolve().parent


def describe(comps, info):
    return {"base braid word": info["word"], "strands": info["n"],
            "arc choice (summand: (gap after crossing k, position q))": info["choice"],
            "components": [{"name": c.name, "role": c.role, "framing": c.framing, "psi on meridian": c.psi,
                            "polygon": [[round(x, 6) for x in pt] for pt in c.pts]} for c in comps]}


def purity(comps, spec):
    K = comps[0]
    leaves = [c for c in comps if c.role == "leaf"]
    chars = [pow(spec.zeta, e, spec.p) for e in range(1, spec.r)]
    F, _ = leaf_functionals(K, leaves, chars)
    rows, ok = {}, True
    for lf in leaves:
        role = {"l": "x", "y": "y", "t": "t"}[lf.name[0]]
        want = spec.chi[role]
        supp = {chi: [int(x) for x in F[chi][lf.name]] for chi in F}
        good = any(supp[want]) and all(not any(v) for chi, v in supp.items() if chi != want)
        rows[lf.name] = {"slot character": want, "functional by character": supp, "pure": good}
        ok &= good
    return rows, ok


def main(outdir):
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    pred = json.loads((HERE / "predictions.json").read_text())
    out = {"machinery": validate.main()}
    print("machinery ok:", out["machinery"]["ok"], round(time.time() - t0, 1), flush=True)
    rows = {}
    for fname, fx in FIXTURES.items():
        p, r, S, knots, gname, n, E, roles, fedges = fx
        z = 3 if (p, r) == (7, 6) else 2
        spec = Spec(p, r, z, S, knots)
        comps, info, Lay, base = build_fixture(spec, roles, fedges)
        closed = cohomology_data(comps, spec)
        knot = cohomology_data(comps, spec, knot_group=True)
        P = pred[fname]
        res = {"components": closed["components"], "crossings": closed["crossings"], "generators": closed["U"],
               "min_depth_gap": closed["min_depth_gap"], "H1 invariant factors (closed)": closed["H1_invariant_factors"],
               "clasper-only H1 factors (knot exterior)": knot["H1_invariant_factors"],
               "dims closed": closed["dims"], "dims knot": knot["dims"],
               "seconds (cohomology)": closed["seconds"] + knot["seconds"]}
        m = {
            "H1 = Z/r": closed["H1_invariant_factors"] == [r],
            "clasper-only H1 trivial": knot["H1_invariant_factors"] == [],
            "psi well defined and onto": closed["psi_well_defined"] and knot["psi_well_defined"] and closed["meridian_psi"] == 1,
            "dims closed as predicted": {int(k): v for k, v in closed["dims"].items()} == {int(k): v for k, v in P["dims_closed"].items()},
            "dims knot as predicted": {int(k): v for k, v in knot["dims"].items()} == {int(k): v for k, v in P["dims_knot"].items()},
        }
        if gname == "K2":
            prow, pok = purity(comps, spec)
            res["leaf purity"] = prow
            m["leaves pure"] = pok
        counts = {}
        for gname_, G in groups_for(fname).items():
            cr, kr = {}, {}
            for k in range(r):
                cr[k] = measured_count(G, closed, k, L.count_bilinear_zeros)
                kr[k] = measured_count(G, knot, k, L.count_bilinear_zeros)
            pc = {int(k): v for k, v in P["groups"][gname_]["closed"].items()}
            pk = {int(k): v for k, v in P["groups"][gname_]["knot"].items()}
            counts[gname_] = {"closed measured": cr, "closed predicted": pc, "knot measured": kr, "knot predicted": pk}
            m[f"{gname_}: closed counts as predicted"] = cr == pc
            m[f"{gname_}: knot counts as predicted"] = kr == pk
        if fname == "P1-K2":
            c = counts["free class 2 on characters (3, 2, 6)"]["closed measured"]
            m["checkpoint values 133 (psi^1) and 2401 (psi^5)"] = c[1] == 133 and c[5] == 2401
        res["counts"] = counts
        res["matches"] = m
        res["ok"] = all(m.values())
        rows[fname] = res
        (outdir / f"surgery_{fname.replace(' ', '_').replace('=', '')}.json").write_text(json.dumps(describe(comps, info)) + "\n")
        print(fname, {k: v for k, v in m.items() if not v} or "all matches", closed["crossings"], "crossings",
              round(time.time() - t0, 1), "s", flush=True)
    out["rows"] = rows
    pre = out["machinery"]["ok"] and all(rows[f]["matches"]["H1 = Z/r"] and rows[f]["matches"]["psi well defined and onto"]
                                         for f in rows)
    fixtures_ok = all(r["ok"] for r in rows.values())
    verdict = "invalid" if not pre else ("supported" if fixtures_ok else "refuted")
    out["verdict"] = verdict
    out["seconds"] = round(time.time() - t0, 1)
    (outdir / "rows.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    summary = {"schema_version": 1, "experiment_id": "CLASSK-DICHOTOMY-20261026-001B-E001", "verdict": verdict,
               "fixtures": {f: {"crossings": rows[f]["crossings"], "ok": rows[f]["ok"]} for f in rows},
               "count comparisons": sum(1 for f in rows for k in rows[f]["matches"] if "counts as predicted" in k),
               "machinery_ok": out["machinery"]["ok"],
               "failed": [f"{f}: {k}" for f in rows for k, v in rows[f]["matches"].items() if not v],
               "seconds": out["seconds"]}
    (outdir / "result.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0 if verdict == "supported" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out"))
