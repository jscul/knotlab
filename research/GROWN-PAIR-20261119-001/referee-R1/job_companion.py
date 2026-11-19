"""Shared-runner job: the one meet-once table group (of the referee's 81) whose study table hash is also carried by a grown stage
in which two junctions share two distinctions.  The referee regrows that stage (its census index and round read from the study's
results as data), and tests its table and states against the group's arrangements exactly.  This reconciles the referee's 81 with
the study's 80 (the study counts a group only when all its grown arrangements meet once).

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-PAIR-20261119-001/referee-R1/job_companion.py \\
      --out runs/referee-grown-companion --unit referee-grown-companion --workers 1 --case-timeout 900 --case-mem 2G --mem-max 16G
"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
RES = ROOT / "artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs/results_grown-pair.jsonl.gz"
CASE = {}


def setup(params):
    th, byh = {}, defaultdict(list)
    for line in gzip.open(RES, "rt"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for st in r["result"]["stages"]:
            th[(st["index"], st["round"])] = st["table_hash"]
            if st["round"] > 0 and st["max_shared"] >= 2:
                byh[st["table_hash"]].append((st["index"], st["round"]))
    keys = {}
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            for a in r["result"]["arrangements"]:
                keys[a["index"]] = a["key"]
    for line in open(ROOT / "runs/referee-grown-meetonce-groups/results.jsonl"):
        for g in json.loads(line)["result"]["table groups"]:
            comp = [p for h in {th[tuple(p[0])] for p in g["provenance"]} for p in byh[h]]
            if comp:
                CASE["c0"] = {"group": g, "companions": [[ix, rnd, keys[ix]] for ix, rnd in comp]}


def cases():
    yield from CASE.items()


def run(case_id, payload):
    import referee_f as F
    import referee_census as RC
    from job_grown import same_states, stage, relabel
    g = payload["group"]
    tabs = [RC.shore_table(s)[0] for s in g["stars"]]
    out = []
    for ix, rnd, key in payload["companions"]:
        B, n = relabel(stage(key, rnd))
        KB = RC.shore_table(B)[0]
        row = {"index": ix, "round": rnd, "junctions": len(B), "distinctions": n}
        for a, (A, KA) in enumerate(zip(g["stars"], tabs)):
            p = F.isometric(KA, KB)
            row[f"vs {a}: tables isometric"] = p is not None
            row[f"vs {a}: same states"] = same_states(A, B, KA, KB, n)[0] if p is not None else None
        out.append(row)
    return {"group": {"arrangements": g["arrangements"], "provenance": g["provenance"]}, "companions": out}
