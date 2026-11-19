"""Read-out of runs/referee-created (job_created.py) into referee_created.json, with the study's isos.json read as data for the
pair-by-pair comparison (no study code run).

  .venv/bin/python -B research/CREATED-PAIR-20261119-001/referee-R1/created_readout.py
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = ROOT / "artifacts/CREATED-PAIR-20261119-001A/CREATED-PAIR-20261119-001A-E001_isos/isos.json"


def main():
    rows = {}
    for line in open(ROOT / "runs/referee-created/results.jsonl"):
        r = json.loads(line)
        assert r["status"] == "ok", r["case"]
        rows[r["case"]] = r["result"]
    study = {}
    for r in json.loads(STUDY.read_text())["rows"]:
        study[(tuple(r["prov"][0]), tuple(r["prov"][1]))] = r
    s = Counter()
    per = []
    unmatched = Counter()
    for cid, r in sorted(rows.items()):
        if cid.startswith("L"):
            continue
        kind = "created" if r["kind"].startswith("created") else "carried"
        small = max(r["vertices"]) <= 15
        size = "small" if small else "large"
        key = (tuple(r["starts"][0]), tuple(r["starts"][1]))
        if key in study:
            d, st = "A to B", study[key]
        else:
            d, st = "B to A", study.get(key[::-1])
        x = r[d]
        c = x["counts"]
        g = f"{kind} {size}"
        s[f"{g}: pairs"] += 1
        s[f"{g}: isometries"] += x["isometries"]
        s[f"{g}: capped"] += c.get("capped", 0)
        s[f"{g}: isometries keeping loose"] += c.get("keeps loose", 0)
        s[f"{g}: constrained search agrees"] += x["constrained search: isometries keeping loose"] == c.get("keeps loose", 0)
        s[f"{g}: pairs with an isometry keeping loose"] += c.get("keeps loose", 0) > 0
        s[f"{g}: pairs with an isometry keeping the growing end (study's direction)"] += c.get("keeps growing end", 0) > 0
        other = r["B to A" if d == "A to B" else "A to B"]
        s[f"{g}: pairs with an isometry keeping the growing end (either direction)"] += \
            c.get("keeps growing end", 0) > 0 or other["counts"].get("keeps growing end", 0) > 0
        s[f"{g}: most junctions kept = all but two"] += x["most junctions kept"] == x["junctions"][0] - 2
        s[f"{g}: most junctions kept = all but one"] += x["most junctions kept"] == x["junctions"][0] - 1
        s[f"{g}: an isometry carries the states"] += c.get("carries states", 0) > 0
        s[f"{g}: weight counts of the equation spaces differ"] += not x["weight counts equal"]
        s[f"{g}: E0 loose counts and classes equal"] += x["E0"]["loose"][0] == x["E0"]["loose"][1] and \
            x["E0"]["loose classes"][0] == x["E0"]["loose classes"][1]
        for (lv, dist, kl), v in x["unmatched at n-2 (live, distance to a live junction, keeps loose)"]:
            unmatched[(g, "live" if lv else f"closed, distance {dist}", "keeps loose" if kl else "moves loose")] += v
        row = {"case": cid, "kind": kind, "size": size, "starts": r["starts"], "junctions": x["junctions"][0],
               "isometries": x["isometries"], "keeps loose": c.get("keeps loose", 0),
               "keeps growing end": c.get("keeps growing end", 0), "most junctions kept": x["most junctions kept"]}
        if st is not None and "skipped" in st:
            s[f"{g}: skipped by the study"] += 1
        elif st is not None:
            same = (st["isometries"] == x["isometries"] and st["counts"].get("keeps_loose", 0) == c.get("keeps loose", 0) and
                    st["counts"].get("keeps_growing_end", 0) == c.get("keeps growing end", 0) and
                    st["most_junctions_kept"] == x["most junctions kept"] and
                    st["counts"].get("carries_states", 0) == c.get("carries states", 0))
            row["agrees with the study's row"] = same
            s[f"{g}: agrees with the study's row"] += same
        per.append(row)
    created = next(r for r in rows.values() if r.get("kind", "").startswith("created"))
    out = {"summary": dict(sorted(s.items())),
           "unmatched junctions under isometries keeping all but two": [[list(k), v] for k, v in sorted(unmatched.items())],
           "created pair, regrown": {d: {k: v for k, v in created[d].items() if k != "stars"} for d in ("A to B", "B to A")},
           "created pair, regrown, stars and rounds": {"stars": created["A to B"]["stars"], "rounds": created["rounds of junctions"]},
           "created pair, the study's literal lists": rows["L-000"]["literal"],
           "pairs": per}
    (HERE / "referee_created.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["summary"], indent=1))
    print(json.dumps(out["unmatched junctions under isometries keeping all but two"], indent=0))


if __name__ == "__main__":
    main()
