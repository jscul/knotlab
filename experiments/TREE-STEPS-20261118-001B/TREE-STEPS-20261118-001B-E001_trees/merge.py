"""Merge TREE-STEPS-B1's results and score P1-P4.   python3 -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[3] / "artifacts/TREE-STEPS-20261118-001B/TREE-STEPS-20261118-001B-E001_trees"


def main(rundir):
    res = [json.loads(l) for l in open(Path(rundir) / "results.jsonl")]
    six = [row for r in res if r["case"].startswith("six") and r["status"] == "ok" for row in r["result"]["rows"]]
    rnd = [row for r in res if r["case"].startswith("rand") and r["status"] == "ok" for row in r["result"]["rows"]]
    failed = [r["case"] for r in res if r["status"] != "ok"]
    def summ(rows):
        return {"bases": len(rows), "pairs": sum(r["pairs"] for r in rows),
                "delta_off": sum(len(r["delta_off"]) for r in rows), "deltaK_off": sum(len(r["deltaK_off"]) for r in rows),
                "differ": sum(r["differ"] for r in rows),
                "examples_delta_off": [dict(laws=r["laws"], off=r["delta_off"][:3]) for r in rows if r["delta_off"]][:5],
                "examples_deltaK_off": [dict(laws=r["laws"], off=r["deltaK_off"][:3]) for r in rows if r["deltaK_off"]][:5]}
    s6, sr = summ(six), summ(rnd)
    pred = {"P1": s6["bases"] == 1216 and s6["delta_off"] == 0, "P2": s6["bases"] == 1216 and s6["deltaK_off"] == 0,
            "P3": sr["bases"] == 80 and sr["delta_off"] == 0 and sr["deltaK_off"] == 0,
            "P4": s6["differ"] == 0 and sr["differ"] == 0}
    out = {"failed_cases": failed, "six_knots": s6, "random_seven": sr,
           "predictions": {k: ("held" if v else "failed") for k, v in pred.items()}}
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "results.json", "w"), indent=1)
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main(sys.argv[1])
