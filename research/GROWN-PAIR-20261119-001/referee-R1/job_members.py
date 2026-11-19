"""Shared-runner job: the full membership of the 152 other-state groups, for the lineage statement ("no other-states group has two
members from the same start").  other_states.json lists one representative per state group, and its lineage test compares the
representatives only.  Here every grown stage carrying the group's study table hash (index and round read from the study's results
as data) is regrown by the referee's engine; those whose exact table is isometric to the representatives' join the group, and each
is placed in a state group by exact same-states search against the two representatives.  A start that reaches both state groups
would pair two stages of one start.

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-PAIR-20261119-001/referee-R1/job_members.py \\
      --out runs/referee-grown-members --unit referee-grown-members --workers 6 --case-timeout 900 --case-mem 2G --mem-max 16G
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
ART = ROOT / "artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs"
CASES = {}


def setup(params):
    th, byh = {}, defaultdict(list)
    for line in gzip.open(ART / "results_grown-pair.jsonl.gz", "rt"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for st in r["result"]["stages"]:
            th[(st["index"], st["round"])] = st["table_hash"]
            if st["round"] > 0:
                byh[st["table_hash"]].append((st["index"], st["round"]))
    keys = {}
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            for a in r["result"]["arrangements"]:
                keys[a["index"]] = a["key"]
    for i, g in enumerate(json.load(open(ART / "other_states.json"))["group_list"]):
        h = th[tuple(g["reps"][0]["prov"][0])]
        CASES[f"g{i:03d}"] = {"reps": [rep["stars"] for rep in g["reps"]],
                              "members": [[ix, rnd, keys[ix]] for ix, rnd in byh[h]]}


def cases():
    yield from CASES.items()


def run(case_id, payload):
    import referee_f as F
    import referee_census as RC
    from job_grown import same_states, stage, relabel
    reps = [relabel(s) for s in payload["reps"]]         # other_states.json lists two; a member matching neither opens a third
    rtabs = [RC.shore_table(A)[0] for A, _ in reps]
    starts = [set() for _ in reps]
    other, undecided = 0, 0
    for ix, rnd, key in payload["members"]:
        B, n = relabel(stage(key, rnd))
        KB = RC.shore_table(B)[0]
        if F.isometric(rtabs[0], KB) is None:
            other += 1
            continue
        placed = []
        for k, ((A, _), KA) in enumerate(zip(reps, rtabs)):
            r, _ = same_states(A, B, KA, KB, n)
            if r is None:
                undecided += 1
            if r:
                placed.append(k)
        if len(placed) > 1:
            return {"error": f"stage {ix}/{rnd} placed in {placed}"}
        if not placed:
            reps.append((B, n))
            rtabs.append(KB)
            starts.append(set())
            placed = [len(reps) - 1]
        starts[placed[0]].add(ix)
    shared = sorted({ix for a in range(len(starts)) for b in range(a + 1, len(starts)) for ix in starts[a] & starts[b]})
    return {"stages in the hash bucket": len(payload["members"]), "not isometric (hash collision)": other,
            "state groups": len(reps), "stages per state group": [len(s) for s in starts],
            "starts in two state groups": shared, "undecided searches": undecided}
