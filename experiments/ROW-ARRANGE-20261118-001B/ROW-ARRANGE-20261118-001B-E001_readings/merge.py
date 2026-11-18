"""Merge the shared runner's results for ROW-ARRANGE-20261118-001B-E001 into results.json and score the frozen predictions.

    python3 -B merge.py <runner out dir>"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = ROOT / "artifacts/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings"
sys.path.insert(0, str(HERE))
import readings as RD  # noqa: E402

NAMES = ["a", "N1", "W2", "WL", "BW4"] + [f"B{r}" for r in (2, 4, 6, 8, 10, 12, 14)]


def assess(rows):
    """rows: one per distinct class, with k, lam, N and reading names."""
    out = {}
    for name in NAMES:
        groups = {}
        for r in rows:
            groups.setdefault(r[name], []).append(r)
        multi = [g for g in groups.values() if len(g) > 1]
        out[name] = {"groups": len(groups), "classes": len(rows), "multi": len(multi),
                     "mix_k": sum(len({x["k"] for x in g}) > 1 for g in multi),
                     "mix_lam": sum(len({x["lam"] for x in g}) > 1 for g in multi),
                     "mix_N": sum(len({x["N"] for x in g}) > 1 for g in multi)}
        ex = next((g for g in multi if len({x["k"] for x in g}) > 1), None)
        out[name]["example_mix_k"] = [{"k": x["k"], "lam": x["lam"], "N": x["N"], "states": x.get("states")} for x in ex[:2]] if ex else None
    out["_rows_distinct"] = sum(bool(r.get("rows_distinct")) for r in rows)
    lm = {}
    for r in rows:
        lm[r.get("least_row_max")] = lm.get(r.get("least_row_max"), 0) + 1
    out["_least_row_max"] = dict(sorted(lm.items(), key=lambda kv: (kv[0] is None, kv[0])))
    return out


def main(rundir):
    res = [json.loads(l) for l in open(Path(rundir) / "results.jsonl")]
    bad = [r["case"] for r in res if r["status"] != "ok"]
    full, fam = {}, {8: [], 9: []}
    for r in res:
        if r["status"] != "ok":
            continue
        c = r["case"]
        if c.startswith("family"):
            fam[int(c[6])] += r["result"]["bases"]
        else:
            key = "cheap-" + c.split("-")[1] if c.startswith("cheap") else "one-split-" + c.split("-")[1]
            full.setdefault(key, []).extend(r["result"]["rows"])
    pops = {k: assess(v) for k, v in sorted(full.items())}
    for mm, bases in fam.items():
        canon = RD.R.Canon()
        seen = {}
        for b in bases:
            seen.setdefault(canon.cid(b["states"], mm), b)
        key = f"families-{mm}"
        pops[key] = assess(list(seen.values()))
        pops[key]["_children"] = len(bases)
        pops[key]["_distinct_classes"] = len(seen)
    pred = {}
    out = {"failed_cases": bad, "populations": pops, "predictions": pred}
    json.dump(out, open(ART / "results.json", "w"), indent=1)
    for p, v in pops.items():
        print(p, {n: (x["groups"], x["mix_k"], x["mix_lam"]) for n, x in v.items() if not n.startswith("_")},
              {n: x for n, x in v.items() if n.startswith("_")})


if __name__ == "__main__":
    ART.mkdir(parents=True, exist_ok=True)
    main(sys.argv[1])
