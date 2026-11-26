"""Read the supplied records, preserving pair identity and the recorded placement order."""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SEED = 20261126017


def records(path):
    with gzip.open(path, "rt") as stream:
        for line in stream:
            yield json.loads(line)


def panel(name):
    paths = [STUDY / f"{name}_runs.jsonl.gz"]
    if name == "linked":
        paths.append(STUDY / "places_runs.jsonl.gz")
    pairs = defaultdict(dict)
    for path in paths:
        for row in records(path):
            laws = pairs[row["A"], row["B"]]
            assert row["law"] not in laws
            laws[row["law"]] = row
    return pairs


def hearings(row):
    return [change for change in row["changes"] if change["heard"] is not None]


def normalized(row):
    return {key: value for key, value in row.items()
            if key not in {"law", "binds on the growth with no change"}}


def audit(name):
    pairs = panel(name)
    laws = sorted(next(iter(pairs.values())))
    assert all(sorted(rows) == laws for rows in pairs.values())
    counts = {}
    for law in laws:
        rows = [v[law] for v in pairs.values()]
        changes = [c for row in rows for c in row["changes"]]
        hits = [c for c in changes if c["heard"] is not None]
        counts[law] = {
            "records": len(rows), "placements": len(changes),
            "first_hearings": dict(sorted(Counter(c["heard"] for c in hits).items())),
            "common_endpoints": dict(sorted(Counter(c["rounds"] for c in changes).items())),
            "hearings_with_later_births_in_both": sum(
                any(c["births with"][c["heard"]:]) and any(row["births"][c["heard"]:])
                for row in rows for c in hearings(row)),
        }
    comparisons = {}
    for left, right in [("HALF","CAP-3"), ("PLACES","CAP-3"), ("PLACES","ORD"),
                        ("PLACES","PLACES-JOINS"), ("ORD","PLACES-OFFSHOOTS")]:
        if right not in laws:
            continue
        stats = Counter()
        for rows in pairs.values():
            a,b = rows[left], rows[right]
            stats["equal_unchanged_counts"] += a["births"] == b["births"]
            stats["equal_unchanged_readings"] += all(a[x] == b[x] for x in
                ["births", "linked", "ended", "made short", "rounds"])
            eq = normalized(a) == normalized(b)
            stats["equal_recorded_outcomes"] += eq
            if not eq:
                stats["different_recorded_outcomes"] += 1
                stats["different_outcomes_with_either_law_hearing"] += bool(hearings(a) or hearings(b))
        comparisons[f"{left}/{right}"] = dict(stats)
    return {"counts":counts, "comparisons":comparisons}


def draws(name):
    pairs = panel(name)
    rng = Random(SEED if name == "linked" else SEED + 1)
    simple = rng.sample(sorted(pairs), 5 if name == "linked" else 10)
    if name == "census":
        supplement = sorted(key for key, rows in pairs.items() if hearings(rows["HALF"]))
    else:
        supplement = sorted(key for key, rows in pairs.items()
                            if rows["PLACES"]["births"] != rows["ORD"]["births"])
    return {"uniform":simple, "targeted":supplement}


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--draw", action="store_true")
    args = cli.parse_args()
    print(json.dumps({name: (draws if args.draw else audit)(name) for name in
                      ["linked", "census"]}, indent=2))
