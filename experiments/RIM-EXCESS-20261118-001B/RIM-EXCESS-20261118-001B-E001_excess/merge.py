"""Merge RIM-EXCESS-B1 and score R1-R5.   .venv/bin/python -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[3] / "artifacts/RIM-EXCESS-20261118-001B/RIM-EXCESS-20261118-001B-E001_excess"


def main(rundir):
    res = {}
    for line in open(Path(rundir) / "results.jsonl"):
        r = json.loads(line)
        res[r["case"]] = r
    failed = sorted(c for c, r in res.items() if r["status"] != "ok")
    ok = {c: r["result"] for c, r in res.items() if r["status"] == "ok"}
    pick = lambda pre: [v for c, v in ok.items() if c.startswith(pre)]
    lem = {k: sum(v[k] for v in pick("lemmaP-")) for k in ("discs", "bonds", "fail")}
    alg = {k: sum(v[k] for v in pick("algo-")) for k in ("discs", "pairs", "compared", "mismatch", "timeouts")}
    alg["examples"] = [e for v in pick("algo-") for e in v["examples"]][:3]
    exc = {}
    for k in (11, 12):
        vs = [v for c, v in ok.items() if c.startswith(f"excess-k{k}-")]
        e = {key: sum(v[key] for v in vs) for key in ("discs", "pairs", "excess_pairs", "excess_not_facing", "unbonded_not_facing")}
        e["max_excess"] = max((v["max_excess"] for v in vs), default=None)
        by = {}
        for v in vs:
            for kk, n in v["by_excess"].items():
                by[kk] = by.get(kk, 0) + n
        e["by_excess"] = by
        e["examples"] = [x for v in vs for x in v["examples"]][:3]
        exc[k] = e
    rnd = pick("random-")
    hist = {}
    for v in rnd:
        for kk, n in v["hist"].items():
            hist[kk] = hist.get(kk, 0) + n
    random_ = {"patches": sum(v["patches"] for v in rnd), "facing_pairs": sum(v["facing_pairs"] for v in rnd), "hist": hist,
               "max_excess": max((v["max_excess"] for v in rnd), default=None),
               "example": max(rnd, key=lambda v: v["max_excess"])["example"] if rnd else None}
    climbs = [{"best_excess": v["best_excess"], "steps": v["steps"]} for v in pick("climb-")]
    pred = {
        "R1": lem["bonds"] > 0 and lem["fail"] == 0,
        "R2": alg["compared"] > 0 and alg["mismatch"] == 0,
        "R3": all(exc[k]["discs"] > 0 and exc[k]["excess_not_facing"] == 0 and exc[k]["unbonded_not_facing"] == 0 for k in (11, 12)),
        "R4": exc[12]["max_excess"] == 2,
        "R5": random_["max_excess"] is not None and random_["max_excess"] <= 2,
    }
    out = {"failed_cases": failed, "cases": len(res), "lemmaP": lem, "algorithm": alg, "excess": exc, "random": random_, "climbs": climbs,
           "predictions": {k: ("held" if v else "failed") for k, v in pred.items()}}
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "results.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("failed_cases", "cases", "predictions")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
