"""Recheck first families for finished exceptions in the weighting replay, and a shorter rank limit."""
import argparse
from collections import Counter
import json
import random

from rebuild import HERE, first_failure
from sampling import draw_start, start_check, failure_mask


def shorter(limit):
    rng = random.Random(2026112701)
    tally = Counter()
    for _ in range(limit):
        stars = draw_start("tree+", 11, rng)
        status, _, _, pieces = start_check(stars, 5000, 250000, 10, "all", "nae")
        label = "+".join(failure_mask(pieces)) or "class"
        tally[label if status == "finished" else status] += 1
    return dict(weighting="tree+", knots=11, seed=2026112701, prefix=limit,
                node_limit=5000, pair_limit=250000, rank_limit=10, counts=tally)


def firsts(path, limit):
    rows = json.loads(path.read_text())["exceptions"]
    out = []
    for row in rows[:limit]:
        r = first_failure(row["stars"], horizon=18, width_cap=900)
        out.append(dict(weighting=row["weighting"], knots=row["knots"], draw=row["draw"],
                        flags=row["failures"], result=r["status"], child_round=r.get("child_round"),
                        twins=r.get("twins", []), splits=r.get("splits", []),
                        uncovered=sum(len(r.get(k, [])) for k in
                                      ("unexplained_gains", "unexplained_losses", "repeated_parent_sets"))))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--prefix", type=int, default=150)
    parser.add_argument("--source", type=str)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    evidence = {"shorter_rank": shorter(args.prefix)}
    if args.source:
        evidence["first_families"] = firsts(HERE / args.source, args.limit)
    if args.output:
        (HERE / args.output).write_text(json.dumps(evidence, separators=(",", ":")) + "\n")
    print(evidence["shorter_rank"], Counter(r["result"] for r in evidence.get("first_families", [])))
