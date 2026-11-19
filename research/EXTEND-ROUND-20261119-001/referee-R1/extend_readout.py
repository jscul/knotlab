"""Read-out of runs/referee-extend (job_extend.py) into referee_extend.json, with the study's extend.json read as data for the
pair-by-pair comparison of the reached pairs (no study code run).

  .venv/bin/python -B research/EXTEND-ROUND-20261119-001/referee-R1/extend_readout.py
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = ROOT / "artifacts/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend/extend.json"


def main():
    rows = []
    for line in open(ROOT / "runs/referee-extend/results.jsonl"):
        r = json.loads(line)
        assert r["status"] == "ok", r["case"]
        for x in r["result"]["rows"]:
            x["case"] = r["case"]
            rows.append(x)
    study = {}
    for r in json.loads(STUDY.read_text())["rows"]:
        if r["kind"].startswith("reached"):
            study[(tuple(r["meta"]["prov"][0]), tuple(r["meta"]["prov"][1]))] = r
    s = Counter()
    for x in rows:
        if x["case"].startswith("S"):
            g = "static"
        else:
            kind = "created" if x["kind"].startswith("created") else "carried"
            g = f"reached {kind} " + ("small" if max(x.get("junctions", [0])) + 1 <= 15 else "larger")
        s[f"{g}: pairs"] += 1
        if not x["both grow a round"]:
            continue
        s[f"{g}: both grow"] += 1
        s[f"{g}: isometries"] += x["isometries"]
        s[f"{g}: isometries keeping R (F whole)"] += x["keep R (F whole)"]
        s[f"{g}: isometries keeping R (maximal members)"] += x["keep R (maximal members of F)"]
        kr = x["keep R (maximal members of F)"] > 0
        s[f"{g}: pairs with an R-keeping isometry"] += kr
        s[f"{g}: extensions tested"] += x["extensions that are isometries of the next tables"] + x["extensions that are not"] + \
            x["rounds do not correspond"]
        s[f"{g}: extensions that are isometries"] += x["extensions that are isometries of the next tables"]
        s[f"{g}: extensions that are not"] += x["extensions that are not"]
        s[f"{g}: rounds do not correspond"] += x["rounds do not correspond"]
        s[f"{g}: control refused"] += x.get("control", False) is True
        s[f"{g}: control run"] += "control" in x
        iso = x.get("next tables isometric")
        s[f"{g}: next isometric, with R kept"] += bool(iso) and kr
        s[f"{g}: next isometric, without R kept"] += bool(iso) and not kr
        s[f"{g}: next part, without R kept"] += (not iso) and not kr
        s[f"{g}: next part, with R kept"] += (not iso) and kr
        s[f"{g}: next isometric and some isometry carries old onto old"] += bool(x.get("some next isometry carries old onto old"))
        s[f"{g}: next tables by flow-bounded bonds"] += any("bonds of at most" in h for h in x["next tables by"])
        if g.startswith("reached") and "starts" in x:
            key = (tuple(x["starts"][0]), tuple(x["starts"][1]))
            st = study.get(key) or study.get(key[::-1])
            if st is not None:
                same = (st["isometries"] == x["isometries"] and st["keeping_reading"] == x["keep R (maximal members of F)"] and
                        bool(st.get("next_tables_isometric")) == bool(iso) and
                        bool(st.get("next_isometry_respects_age")) == bool(x.get("some next isometry carries old onto old")))
                s[f"{g}: agrees with the study's row"] += same
                s[f"{g}: study's tested extensions"] += st["extensions"].get("extension_is_isometry", 0)
    out = {"summary": dict(sorted(s.items())), "rows": rows}
    (HERE / "referee_extend.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
