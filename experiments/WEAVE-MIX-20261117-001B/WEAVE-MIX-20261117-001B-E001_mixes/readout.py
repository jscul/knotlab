"""Read-out of WEAVE-MIX-20261117-001B-E001's frozen results against Q0-Q5, with a labelled post hoc re-reading.

Frozen part: Q0-Q5 exactly as pre-registered, from results.json.  Q5 needs a threshold the pre-registration did not fix; the one
used is stated (a correlation counts as not decaying when its value at the farthest distance is above 0.01 and above half its
value at the first distance).

Post hoc part (written after the read-out, labelled): the frozen classification compared width 12 with the next smaller width,
whose number of column periods has the other parity, so the twist around the cylinder changes between them.  The re-reading
compares width 12 only with the width of the same parity (6 for column periods 1 and 3, 8 for column period 2), with the frozen
thresholds otherwise.  It also computes the referee's 2 x 2 law (index 3 on the up knot of one cell in each 2 x 2 block, index
0 elsewhere).

    .venv/bin/python -B readout.py      (writes artifacts/.../readout.json)
"""
import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "WEAVE-MIX-20261117-001B", "WEAVE-MIX-20261117-001B-E001_mixes")
sys.path.insert(0, HERE)
import mixlib as M  # noqa: E402
import run as RUN  # noqa: E402

fin = lambda x: isinstance(x, (int, float)) and math.isfinite(x)


def same_parity_class(spec, pc):
    by = {s["width"]: s for s in spec}
    top = by[12]
    if top.get("empty"):
        return "empty"
    if top["per_site"] < 1.01:
        return "frozen"
    ref = by[6] if pc in (1, 3) else by[8]
    sg, eg = top.get("spin_gap"), top.get("energy_gap")
    if ref.get("empty") or not all(fin(x) for x in (sg, eg, ref.get("spin_gap"), ref.get("energy_gap"))):
        return "unresolved"
    if sg < 0.01 and eg > 0.05:
        return "ordered"
    if sg > 0.05 and eg > 0.05 and abs(sg - ref["spin_gap"]) < 0.1 * sg and abs(eg - ref["energy_gap"]) < 0.1 * eg:
        return "disordered"
    if sg < ref["spin_gap"] and abs(sg * 12 - ref["spin_gap"] * ref["width"]) < 0.15 * sg * 12:
        return "critical"
    return "unresolved"


def decays(corr):
    for d in corr.values():
        vals = [v for _, v in d["correlation"] if v is not None]
        if vals and abs(vals[-1]) > 0.01 and abs(vals[-1]) > 0.5 * abs(vals[0]):
            return False
    return True


def main():
    R = json.load(open(os.path.join(OUT, "results.json")))
    out = {"frozen": {}, "post_hoc": {}}
    tot = collections.Counter()
    survivors = []
    for fam, F in R["families"].items():
        pc = int(fam.split("x")[0])
        rows = F["rows"]
        groups = collections.defaultdict(list)
        for r in rows:
            groups[str(r["inconsistent_set"])].append(r["spectra"][0])
        dev, maxdev = 0, 0.0
        for g in groups.values():
            bad = False
            for s in g[1:]:
                for key in ("empty", "per_site", "spin_gap", "energy_gap"):
                    x, y = g[0].get(key), s.get(key)
                    if fin(x) and fin(y):
                        maxdev = max(maxdev, abs(x - y))
                        bad |= abs(x - y) > 1e-9
                    elif x != y:
                        bad = True
            dev += bad
        cls = lambda pred: dict(collections.Counter(r["class"] for r in rows if pred(r)))
        dis = [r for r in rows if r["class"] == "disordered"]
        nondecay = [r for r in dis if "error" in r.get("correlation", {}) or not decays(r["correlation"])]
        out["frozen"][fam] = {
            "arrangements": len(rows), "inconsistent_sets": len(groups),
            "Q0_groups_differing": dev, "Q0_max_finite_difference": maxdev,
            "Q1_inconsistent_set_empty": cls(lambda r: not r["inconsistent_set"]),
            "Q2_more_than_two_per_cell": cls(lambda r: r["inconsistent_per_cell"] > 2),
            "Q3_all_even": cls(lambda r: r["all_degrees_even"]),
            "Q4_some_odd": cls(lambda r: not r["all_degrees_even"]),
            "Q5_disordered": len(dis), "Q5_not_decaying": len(nondecay),
            "Q5_not_decaying_same_parity_class": dict(collections.Counter(same_parity_class(r["spectra"], pc) for r in nondecay))}
        ph = collections.Counter()
        for r in rows:
            c2 = same_parity_class(r["spectra"], pc)
            ph[f"{r['class']} -> {c2}, {'even' if r['all_degrees_even'] else 'odd'}{', I empty' if not r['inconsistent_set'] else ''}"] += 1
            if c2 == "disordered":
                survivors.append({"family": fam, "arrangement": r["arrangement"], "inconsistent_per_cell": r["inconsistent_per_cell"],
                                  "all_degrees_even": r["all_degrees_even"],
                                  "spectra": {s["width"]: {k: s.get(k) for k in ("per_site", "spin_gap", "energy_gap")} for s in r["spectra"]},
                                  "correlation": r.get("correlation")})
        out["post_hoc"][fam] = dict(sorted(ph.items()))
        for k in ("Q3_all_even", "Q4_some_odd"):
            tot[k] += out["frozen"][fam][k].get("disordered", 0)
    out["frozen"]["totals_disordered"] = dict(tot)
    out["post_hoc"]["survivors"] = survivors
    arr = {(i, j, t): 0 for i in range(2) for j in range(2) for t in "UD"}
    arr[(0, 0, "U")] = 3
    spec = [M.sector_spectrum(w, arr, 2, 2) for w in (6, 8, 10, 12)]
    bad, even = M.inconsistent_set(arr, 2, 2)
    out["post_hoc"]["referee_2x2_law"] = {"inconsistent_per_cell": len(bad) / 4, "all_degrees_even": even,
                                          "frozen_rule": RUN.classify(spec), "same_parity_rule": same_parity_class(spec, 2),
                                          "spectra": {s["width"]: {k: s.get(k) for k in ("per_site", "spin_gap", "energy_gap")} for s in spec}}
    json.dump(out, open(os.path.join(OUT, "readout.json"), "w"), indent=1, default=str)
    print(json.dumps(out["frozen"], indent=1, default=str))
    print(json.dumps({k: v for k, v in out["post_hoc"].items() if k != "survivors"}, indent=1, default=str))
    print("survivors", len(survivors))


if __name__ == "__main__":
    main()
