"""Merge BOND-METRIC-B1 and score P1-P6 (P3 and P3b).   .venv/bin/python -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[3] / "artifacts/BOND-METRIC-20261118-001B/BOND-METRIC-20261118-001B-E001_triangles"


def main(rundir):
    res = {}
    for line in open(Path(rundir) / "results.jsonl"):
        r = json.loads(line)
        res[r["case"]] = r  # the latest record per case is final
    failed = sorted(c for c, r in res.items() if r["status"] != "ok")
    ok = {c: r["result"] for c, r in res.items() if r["status"] == "ok"}
    par = [v for c, v in ok.items() if c.startswith("parity")]
    parity = {"bases": sum(v["bases"] for v in par), "failing_b": sum(v["failing_b"] for v in par),
              "failing_b1": sum(v["failing_b1"] for v in par),
              "examples_b1": [e for v in par for e in v["examples_b1"]][:3]}
    classes = {}
    for c, v in ok.items():
        if not c.startswith("lang-"):
            continue
        t = classes.setdefault(v["law"], {"by_n_k": {}, "smallest": None, "example": None, "min_abs_corr_inf": None,
                                          "inf_all_correlated": True, "smallest_once": None, "example_once": None})
        key = f"n{v['n']}-k{v['k']}"
        cell = t["by_n_k"].setdefault(key, [0, 0])
        cell[0] += v["bases"]
        cell[1] += v["failing_b"]
        if v["failing_b"] and (t["smallest"] is None or (v["n"], v["k"]) < tuple(t["smallest"])):
            t["smallest"], t["example"] = [v["n"], v["k"]], v["examples_b"][0]
        if v["failing_once"] and (t["smallest_once"] is None or (v["n"], v["k"]) < tuple(t["smallest_once"])):
            t["smallest_once"], t["example_once"] = [v["n"], v["k"]], v["example_once"]
        if v["min_abs_corr_inf"] is not None:
            t["min_abs_corr_inf"] = v["min_abs_corr_inf"] if t["min_abs_corr_inf"] is None else min(t["min_abs_corr_inf"], v["min_abs_corr_inf"])
        t["inf_all_correlated"] &= v["inf_all_correlated"]
    once = {"n7": {}, "n8": {}, "rings_n8": {}, "examples": [], "min_abs_corr_inf": None, "inf_all_correlated": True}
    for c, v in ok.items():
        if not c.startswith("nae-once"):
            continue
        cell = once[f"n{v['n']}"].setdefault(str(v["k"]), [0, 0])
        cell[0] += v["bases"]
        cell[1] += v["failing_b"]
        once["examples"] += v["examples_b"][:1]
        for key, cnt in v.get("shortest_ring_by_outcome", {}).items():
            once["rings_n8"][f"k{v['k']}|{key}"] = once["rings_n8"].get(f"k{v['k']}|{key}", 0) + cnt
        if v["min_abs_corr_inf"] is not None:
            once["min_abs_corr_inf"] = v["min_abs_corr_inf"] if once["min_abs_corr_inf"] is None else min(once["min_abs_corr_inf"], v["min_abs_corr_inf"])
        once["inf_all_correlated"] &= v["inf_all_correlated"]
    once["examples"] = once["examples"][:5]
    weaves = {c: {k: v[k] for k in ("L", "W", "knots", "failing_b", "triples_b", "inf_triples", "min_abs_corr_inf", "inf_all_correlated", "examples_b")}
              for c, v in ok.items() if c.startswith("weave")}
    mix = [v for c, v in ok.items() if c.startswith("mixed")]
    mixed = {"bases": sum(v["bases"] for v in mix), "failing_b": sum(v["failing_b"] for v in mix),
             "failing_b1": sum(v["failing_b1"] for v in mix),
             "once": [sum(v["bases_and_failing_by_meeting"]["once"][i] for v in mix) for i in (0, 1)],
             "not_once": [sum(v["bases_and_failing_by_meeting"]["not"][i] for v in mix) for i in (0, 1)]}
    nae_inf = [classes.get("NAE", {}).get("min_abs_corr_inf"), once["min_abs_corr_inf"]] + [w["min_abs_corr_inf"] for w in weaves.values()]
    nae_all = classes.get("NAE", {}).get("inf_all_correlated", False) and once["inf_all_correlated"] and all(w["inf_all_correlated"] for w in weaves.values())
    small = lambda l: classes.get(l, {}).get("smallest")
    r5_small = lambda l: [c for key, c in classes.get(l, {}).get("by_n_k", {}).items() if int(key.split("-")[0][1:]) <= 6]
    pred = {
        "P1": parity["bases"] > 0 and parity["failing_b"] == 0,
        "P2": parity["bases"] > 0 and parity["failing_b1"] == 0,
        "P3": all(small(l) == [4, 2] for l in ("NAE", "betweenness", "clause", "clause-twisted", "R6", "R6-twisted")),
        "P3b": all(r5_small(l) and sum(c[1] for c in r5_small(l)) == 0 for l in ("R5", "R5-twisted")),
        "P4": sum(c[0] for c in once["n7"].values()) > 0 and sum(c[1] for c in once["n7"].values()) == 0,
        "P5": all(once["n8"].get(str(k), [0, 0])[1] == 0 for k in (3, 4)) and once["n8"].get("4", [0, 0])[0] > 0,
        "P6": any(x is not None for x in nae_inf) and nae_all,
    }
    out = {"failed_cases": failed, "cases": len(res), "parity": parity, "classes": classes, "nae_meeting_once": once,
           "weaves": weaves, "mixed_random": mixed, "predictions": {k: ("held" if v else "failed") for k, v in pred.items()}}
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "results.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("failed_cases", "cases", "parity", "predictions")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
