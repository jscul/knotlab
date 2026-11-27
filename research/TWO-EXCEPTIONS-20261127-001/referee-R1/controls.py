"""Controls using all subsets and renamed inputs; bounded search on earlier sample files."""
import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from rebuild import HERE, RESEARCH, Reading, families, first_failure


def subsets_rule(parents):
    pairwise = set()
    joint = set()
    for k in range(2, len(parents) + 1):
        for members in combinations(parents, k):
            if all(parents[a] & parents[b] for a, b in combinations(members, 2)):
                members = frozenset(members)
                pairwise.add(members)
                if k >= 3 and not set.intersection(*(set(parents[a]) for a in members)):
                    joint.add(members)
    return {q for q in joint if not any(q < g for g in pairwise)} | {
        q for q in pairwise if len(q) == 2 and not any(q < g for g in joint)}


def fingerprint(result):
    return {k: result.get(k) for k in ("status", "child_round", "twins", "splits",
                                        "twin_absorbed", "history")}


def control(limit):
    rows = []
    path = HERE.parent / "referee_witnesses.jsonl"
    for i, record in enumerate(map(json.loads, path.read_text().splitlines()), 1):
        if limit and i > limit:
            break
        stars = record["stars"]
        renamed = [[-d-1 for d in reversed(s)] for s in reversed(stars)]
        result = first_failure(stars)
        assert fingerprint(result) == fingerprint(first_failure(renamed))
        core = Reading(stars)
        checked = 0
        for _ in range(4):
            rank = core.ranks[-1]
            if len(rank) > 12:
                break
            parents = {x: core.parents[x] for x in rank}
            assert subsets_rule(parents) == families(parents)
            checked += 1
            core.next_rank()
        rows.append([i, result.get("child_round"), checked])
    return dict(witness_controls=rows)


def search(limit, width=90, horizon=11):
    graded = RESEARCH / "GRADED-ORDER-20261126-001"
    cycles = RESEARCH / "CYCLE-READ-20261127-001"
    paths = sorted(graded.glob("fresh*.jsonl")) + sorted(graded.glob("held*.jsonl"))
    paths += [graded / name for name in ["replays.jsonl", "twins7_treeplus.jsonl"]]
    paths += sorted(cycles.glob("cyc*.jsonl")) + sorted(cycles.glob("twin*_draw.jsonl"))
    counts = Counter()
    failed = []
    total = 0
    for path in paths:
        for i, row in enumerate(map(json.loads, path.read_text().splitlines()), 1):
            if limit and total >= limit:
                break
            total += 1
            stars = row["stars"]
            core = Reading(stars)
            if not any(core.chains.values()):
                # With no chain, rule and proposed are the same core construction at every rank.
                counts["pure"] += 1
                continue
            result = first_failure(stars, horizon=horizon, width_cap=width)
            counts[result["status"]] += 1
            if result["status"] == "failure":
                failed.append(dict(file=str(path.relative_to(RESEARCH)), line=i,
                                   child_round=result["child_round"], twins=result["twins"],
                                   splits=result["splits"], other=len(result["unexplained_gains"])
                                   + len(result["unexplained_losses"])))
    return dict(counts=counts, failed=failed, width=width, child_horizon=horizon)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["control", "search"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = (control if args.mode == "control" else search)(args.limit)
    if args.output:
        args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(result.get("counts", result))
