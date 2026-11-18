"""Merge FREE-READ-B1 and score P1-P5.   python3 -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

ART = Path(__file__).resolve().parents[3] / "artifacts/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds"


def main(rundir):
    res = [json.loads(l) for l in open(Path(rundir) / "results.jsonl")]
    failed = [r["case"] for r in res if r["status"] != "ok"]
    six = [row for r in res if r["case"].startswith("six") and r["status"] == "ok" for row in r["result"]["rows"]]
    rnd = [row for r in res if r["case"].startswith("rand") and r["status"] == "ok" for row in r["result"]["rows"]]
    cyc = next((r["result"]["cycles"] for r in res if r["case"] == "cycles" and r["status"] == "ok"), [])
    summ = lambda rows: {"bases": len(rows), "pairs": sum(r["pairs"] for r in rows), "off": sum(len(r["off"]) for r in rows),
                         "examples": [dict(laws=r["laws"], off=r["off"][:3]) for r in rows if r["off"]][:5]}
    s6, sr = summ(six), summ(rnd)
    by = {c["name"]: c for c in cyc}
    closed = []
    p3 = True
    for k in range(2, 6):
        c = by[f"closed{k}"]
        r = next(r for r in c["rows"] if r["x"] == 0 and r["y"] == 2 * k)
        closed.append({"k": k, **r})
        p3 &= r["bond_minus_1"] == 1 and abs(r["delta_K"] - k) < 1e-9 and r["delta"] <= 1.1
    rings = {}
    p4 = True
    p5 = True
    for m in range(3, 7):
        P, N, A = by[f"ring{m}-P"], by[f"ring{m}-N"], by[f"ring{m}-alt"]
        p4 &= all(r["bond_minus_1"] is not None and abs(r["bond_minus_1"] - r["delta"]) < 1e-9 for r in P["rows"])
        p4 &= all(r["bond_minus_1"] == r["steps"] for r in N["rows"])
        p4 &= all(r["bond_minus_1"] is not None and r["bond_minus_1"] <= r["steps"] for r in A["rows"])
        p4b = all(r["bond_minus_1"] == r["steps"] for m_ in range(3, 7) for r in by[f"ring{m_}-alt"]["rows"])
        p5 &= any(abs(r["tau"] - r["bond_minus_1"]) > 0.01 for r in N["rows"])
        rings[m] = {lab: [(r["steps"], r["bond_minus_1"], round(r["tau"], 4) if r["tau"] != float("inf") else None,
                           round(r["delta"], 4), round(r["delta_K"], 4) if r["delta_K"] != float("inf") else None)
                          for r in c["rows"]] for lab, c in (("P", P), ("N", N), ("alt", A))}
    clause = [by[f"clause-chain{k}"]["rows"][0] for k in range(2, 5)]
    p6 = all(r["bond_minus_1"] is None for r in clause)
    pred = {"P1": s6["bases"] == 1216 and s6["off"] == 0, "P2": sr["bases"] == 80 and sr["off"] == 0, "P3": p3, "P4": p4,
            "P4b": p4b, "P5": p5, "P6": p6}
    out = {"failed_cases": failed, "six_knots": s6, "random_seven": sr, "closed_paths": closed, "rings": rings, "clause_chains": clause,
           "predictions": {k: ("held" if v else "failed") for k, v in pred.items()}}
    ART.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(ART / "results.json", "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("failed_cases", "six_knots", "random_seven", "closed_paths", "predictions")}, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main(sys.argv[1])
