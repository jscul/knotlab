#!/usr/bin/env python3
"""Referee FAR-BOUND-R1, F2 recounted from the census's records (far.jsonl, recheck.jsonl) with the referee's reading of the frozen
rule: a base is bounded far away when every far target with a certified bond has b_cert at most its largest near b_cert + 1 and at
least 80% of its far targets have one; it grows when some certified far b_cert exceeds that; certificates are missing when fewer than
80% have one; dropped when the cap stopped it. Also, for each growing base, whether its window values (b_win) rise too.

    python3 -B ref_far_recount.py      (writes result_recount.json)"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parents[2] / "artifacts" / "FAR-BOUND-20261112-001A" / "FAR-BOUND-20261112-001A-E001_bounded_far"


def main():
    rc = {(r["sample"], r["r"]): r for r in map(json.loads, (ART / "recheck.jsonl").read_text().splitlines())}
    rows = []
    for d in map(json.loads, (ART / "far.jsonl").read_text().splitlines()):
        k = (d["sample"], d["r"])
        near = max(v["b_cert"] for v in rc[k]["profile"].values() if v["b_cert"] is not None)
        if "far" not in d:
            rows.append({"base": k, "outcome": "dropped", "near max": near})
            continue
        bc = [v["b_cert"] for v in d["far"].values()]
        bw = [v["b_win"] for v in d["far"].values()]
        share = sum(b is not None for b in bc) / len(bc)
        if share < 0.8:
            o = "certificates missing"
        elif all(b <= near + 1 for b in bc if b is not None):
            o = "bounded"
        else:
            o = "grows by 2 or more"
        rows.append({"base": k, "outcome": o, "near max": near, "far certified max": max(b for b in bc if b is not None),
                     "far window max": max(b for b in bw if b is not None), "certified share": round(share, 3),
                     "window rises by 2 or more": max(b for b in bw if b is not None) >= near + 2})
    out = {"outcomes": dict(Counter(r["outcome"] for r in rows)), "growing: window rises too": [r["base"] for r in rows if r["outcome"] == "grows by 2 or more" and r["window rises by 2 or more"]],
           "growing: window stays within near + 1": [r["base"] for r in rows if r["outcome"] == "grows by 2 or more" and not r["window rises by 2 or more"]],
           "rows": rows}
    (HERE / "result_recount.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
