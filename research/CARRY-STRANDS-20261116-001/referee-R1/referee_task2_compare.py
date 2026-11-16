"""Referee R1: task 2 against the study's recorded run (results.jsonl, data)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.join(ROOT, "artifacts", "CARRY-STRANDS-20261116-001A", "CARRY-STRANDS-20261116-001A-E001_carried",
                   "run", "results.jsonl")
mine = json.load(open(os.path.join(HERE, "referee_task2_structured.json")))
st = {}
for line in open(RES):
    r = json.loads(line)
    if r["case"].split("-")[0] in ("ladder", "pyramid", "subtree"):
        st[r["case"]] = r["result"]
out = {"compared": 0, "equal": 0, "diffs": [], "study_capped": [], "referee_only": []}
for fam, rows in mine.items():
    for key, row in rows.items():
        case = f"{fam}-{key}" if fam != "subtree" else f"subtree-{key}"
        s = st.get(case)
        for law, rec in row.items():
            if not law.startswith("w"):
                continue
            if s is None or law not in s["laws"]:
                out["referee_only"].append((case, law, rec.get("T", rec.get("dp", {}).get("T"))))
                continue
            sl = s["laws"][law]
            if "cap" in sl:
                out["study_capped"].append((case, law, "referee:", rec.get("dp", rec.get("T"))))
                continue
            out["compared"] += 1
            mv = (rec.get("P"), rec.get("T"), rec.get("L"), rec.get("states"))
            sv = (sl["P"], sl["T"], sl["L"], sl["states"])
            if mv == sv:
                out["equal"] += 1
            else:
                out["diffs"].append((case, law, mv, sv))
print(json.dumps(out, indent=1))
with open(os.path.join(HERE, "referee_task2_compare.json"), "w") as fh:
    json.dump(out, fh, indent=1)
