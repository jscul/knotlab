"""Shared-runner job for the referee's rebuild of GROWN-PAIR-20261119-001's meet-once population: every census arrangement (keys
from runs/census-exact5, in shards of 500), regrown by the referee's own engine; every stage of rounds 1 to 8 with at most 14
junctions in which no two junctions share two distinctions; for each, its stars and the invariant of its exact table (the referee's
closed-aware shore enumeration).  Grouping and the states test run afterwards (meetonce_readout.py).

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-PAIR-20261119-001/referee-R1/job_meetonce.py \\
      --out runs/referee-grown-meetonce --unit referee-grown-meetonce --workers 6 --case-timeout 1800 --case-mem 2G --mem-max 16G
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
KEYS = {}
SHARD = 500
BOUNDS = {"lo": 1, "hi": 14, "all": 0, "notable": 0}   # junctions per stage kept (--param lo=15 --param hi=16 for one size
                                                      # past); --param all=1 keeps every stage, not only meet-once ones;
                                                      # --param notable=1 records the stages without their tables


def setup(params):
    BOUNDS.update({k: int(v) for k, v in params.items() if k in BOUNDS})
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            for a in r["result"]["arrangements"]:
                KEYS[a["index"]] = a["key"]


def cases():
    ix = sorted(KEYS)
    for s in range(0, len(ix), SHARD):
        yield f"shard{s // SHARD:03d}", {"keys": [[i, KEYS[i]] for i in ix[s:s + SHARD]], **BOUNDS}


def meet_once(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    share = Counter(tuple(sorted(v)) for v in own.values() if len(v) == 2)
    return not share or max(share.values()) < 2


def run(case_id, payload):
    import referee_first as RFK
    import referee_census as RC
    import referee_f as F
    out = []
    lo, hi = payload.get("lo", 1), payload.get("hi", 14)
    for ix, key in payload["keys"]:
        G = RFK.Start(RC.stars_of(tuple(map(tuple, key))))
        for rnd in range(1, 9):
            if G.step(RFK.fewest, None, None) != "ok" or len(G.bits) > hi:
                break
            stars = [sorted(s) for s in G.bits]
            if len(stars) < lo or not (payload.get("all") or meet_once(stars)):
                continue
            if payload.get("notable"):
                out.append({"index": ix, "round": rnd, "stars": stars, "meet_once": meet_once(stars)})
                continue
            K, labels = RC.shore_table(stars)
            idx = {b: i for i, b in enumerate(labels)}
            out.append({"index": ix, "round": rnd, "stars": [[idx[b] for b in s] for s in stars], "inv": F.invariant(K),
                        "distinctions": len(labels), "meet_once": meet_once(stars)})
    return {"stages": out}
