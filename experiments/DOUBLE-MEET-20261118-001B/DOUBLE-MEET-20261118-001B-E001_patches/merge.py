"""Merge DOUBLE-MEET-B1 and score P0-P5.   .venv/bin/python -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[3] / "artifacts/DOUBLE-MEET-20261118-001B/DOUBLE-MEET-20261118-001B-E001_patches"
KEYS = ("patches", "pairs", "bonded_off_steps", "below_steps", "unbonded", "unbonded_not_facing", "facing_pairs", "facing_bonded",
        "same_class_unbonded", "not_facing_unbonded", "metric", "metric_iff_no_unbonded", "no_state", "dd_fail", "within_par_pairs",
        "within_par_bonded", "bonded_facing_without_outside")


def main(rundir):
    res = {}
    for line in open(Path(rundir) / "results.jsonl"):
        r = json.loads(line)
        res[r["case"]] = r
    failed = sorted(c for c, r in res.items() if r["status"] != "ok")
    ok = {c: r["result"] for c, r in res.items() if r["status"] == "ok"}
    def total(pre):
        vs = [v for c, v in ok.items() if c.startswith(pre)]
        return {k: sum(v.get(k, 0) for v in vs) for k in KEYS}, [e for v in vs for e in v.get("examples", [])][:6]
    discs, dex = total("disc-")
    rnd, rex = total("random-")
    by_k = {}
    for c, v in ok.items():
        if c.startswith("disc-"):
            b = by_k.setdefault(v["k"], {"patches": 0, "unbonded": 0, "facing_pairs": 0, "facing_bonded": 0})
            for k in b:
                b[k] += v.get(k, 0)
    crit = [v for c, v in ok.items() if c.startswith("criterion-")]
    criterion = {"discs": sum(v["discs"] for v in crit), "sets": sum(v["sets"] for v in crit), "mismatch": sum(v["mismatch"] for v in crit)}
    pars = {c: v for c, v in ok.items() if c.startswith("par-")}
    par_ok = all(len(v["unbonded"]) == 1 and len(v["lone"]) == 2 and sorted(map(tuple, v["unbonded"][0])) == sorted(map(tuple, v["lone"]))
                 and v["off_steps"] == 0 for v in pars.values())
    both = {k: discs[k] + rnd[k] for k in KEYS}
    pred = {
        "P0": criterion["sets"] > 0 and criterion["mismatch"] == 0 and both["dd_fail"] == 0,
        "P1": both["patches"] > 0 and both["bonded_off_steps"] == 0,
        "P2": both["unbonded_not_facing"] == 0,
        "P3": both["within_par_pairs"] > 0 and both["within_par_bonded"] == 0,
        "P4": len(pars) > 0 and par_ok,
        "P5": both["metric_iff_no_unbonded"] == both["patches"] - both["no_state"],
    }
    out = {"failed_cases": failed, "cases": len(res), "discs": discs, "discs_by_knots": by_k, "random": rnd, "examples": dex + rex,
           "criterion": criterion, "parallelograms": pars, "predictions": {k: ("held" if v else "failed") for k, v in pred.items()}}
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "results.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("failed_cases", "cases", "predictions")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
