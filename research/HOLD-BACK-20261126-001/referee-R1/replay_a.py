"""Rebuild recorded pairs under the five local taking rules."""

import argparse
from collections import defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import random
import resource
from time import perf_counter, process_time

from growth import TAKE_LAWS, measure


ARCHIVE = Path(__file__).resolve().parent.parent / "takes_runs.jsonl.gz"
SEED = 20261126
ROUNDS, KNOTS, EDITS = 12, 1500, (1, 2, 3)
OLDEST = ("ORD", "MET", "OLDEST")
NEWEST = ("ORD", "MET", "NEWEST")


def identity(row):
    return row["A"], row["B"], tuple(row["law"])


def draw(rows, count):
    return random.Random(SEED).sample(sorted(rows, key=identity), count)


def heard_after(row, after):
    return any(change["t0"] == after and change["heard"] is not None
               for change in row["changes"])


def select(rows):
    by_law = defaultdict(list)
    for row in rows:
        by_law[tuple(row["law"])].append(row)

    first, second, late = [], [], []
    for law in TAKE_LAWS:
        choices = by_law[law]
        a, b = draw(choices, 2)
        first.append(a)
        second.append(b)
        observable = [row for row in choices if any(c["rounds"] > 6 for c in row["changes"])]
        late.extend(draw(observable, 1))

    second_round = [row for row in by_law[NEWEST] if heard_after(row, 2)]
    first_round = draw([row for row in by_law[NEWEST] if heard_after(row, 1)], 1)
    full_horizon = [row for row in by_law[NEWEST] if any(c["rounds"] == ROUNDS for c in row["changes"])]
    cheapest = min(full_horizon, key=lambda row: (sum(c["rounds"] for c in row["changes"]),
                                                  identity(row)))
    return {
        "first uniform draw": first,
        "second uniform draw": second,
        "late-observable draw": late,
        "positive after round 1": first_round,
        "positive after round 2": second_round,
        "newest full-horizon control": [cheapest],
    }


def comparison(stored, edit_limit):
    receiver, far, law = identity(stored)
    started, cpu = perf_counter(), process_time()
    observed, edits = measure(receiver, far, TAKE_LAWS[law], rounds=ROUNDS,
                              bound=KNOTS, edits_after=EDITS, edit_limit=edit_limit)
    observed.update(A=receiver, B=far, law=list(law))
    if edit_limit is not None:
        stored = dict(stored, changes=stored["changes"][:edit_limit])
    comparable = observed.copy()
    missing_baseline_births = "births" not in stored
    if missing_baseline_births:
        del comparable["births"]
    missing_changed_births = {i for i, change in enumerate(stored["changes"]) if "births with" not in change}
    comparable["changes"] = [
        {k: v for k, v in change.items() if k != "births with" or i not in missing_changed_births}
        for i, change in enumerate(observed["changes"])
    ]
    unequal = sorted(k for k in comparable.keys() | stored.keys()
                     if k not in comparable or k not in stored or comparable[k] != stored[k])
    return {
        "record": "comparison" if edit_limit is None else "prefix comparison",
        "row": observed,
        "differing fields": unequal,
        "stored differing values": {key: stored.get(key) for key in unequal},
        "edits": edits,
        "archive omits baseline birth vector": missing_baseline_births,
        "archive omits changed birth vector at edit indices": sorted(missing_changed_births),
        "seconds": round(perf_counter() - started, 4),
        "cpu seconds": round(process_time() - cpu, 4),
        "peak RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", required=True,
                        choices=("pilot", "uniform", "late-pilot", "late", "late-full"))
    parser.add_argument("--prefix-edits", type=int)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.prefix_edits is not None and args.prefix_edits < 1:
        parser.error("--prefix-edits must be positive")
    memory = 3 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (540, 545))
    started, cpu = perf_counter(), process_time()
    with gzip.open(ARCHIVE, "rt") as handle:
        rows = [row for line in handle if "law" in (row := json.loads(line))]
    assert len({identity(row) for row in rows}) == len(rows)
    strata = select(rows)
    if args.panel == "pilot":
        selected = strata["positive after round 2"] + strata["positive after round 1"] + strata["first uniform draw"]
    elif args.panel == "uniform":
        selected = strata["second uniform draw"]
    elif args.panel == "late-pilot":
        selected = [row for row in strata["late-observable draw"] if tuple(row["law"]) == NEWEST]
    elif args.panel == "late-full":
        selected = strata["newest full-horizon control"]
    else:
        selected = [row for row in strata["late-observable draw"] if tuple(row["law"]) != NEWEST]
        selected.sort(key=lambda row: tuple(row["law"]) == OLDEST)

    chosen = {identity(row): row for row in selected}
    matches = count = 0
    with args.out.open("x", buffering=1) as handle:
        def write(row):
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")

        write({
            "record": "selection", "panel": args.panel, "archive": ARCHIVE.name,
            "archive SHA-256": sha256(ARCHIVE.read_bytes()).hexdigest(),
            "archived rows": len(rows), "seed": SEED,
            "weightings": {
                "uniform": "within each archived law, two distinct rows without replacement",
                "late-observable": "within each archived law, one row uniformly among rows with an edit compared past round 6",
                "positive after round 1": "one row uniformly among newest-candidate rows that heard a change made after round 1",
                "positive after round 2": "all newest-candidate rows that heard a change made after round 2",
                "newest full-horizon control": (
                    "one newest-candidate row with at least one edit compared through round 12, "
                    "minimizing total recorded compared edit rounds, then pair identity"
                ),
            },
            "identity and all memberships": [
                {"identity": key, "strata": [s for s, choices in strata.items() if row in choices]}
                for key, row in chosen.items()
            ],
            "round bound": ROUNDS, "knot bound": KNOTS, "guard multiplier": 4,
            "changes after rounds": EDITS, "address space cap bytes": memory,
            "edit prefix limit": args.prefix_edits,
        })
        for key, row in chosen.items():
            cell = comparison(row, args.prefix_edits)
            write(cell)
            count += 1
            matches += not cell["differing fields"]
            print(json.dumps({"identity": key, "exact": not cell["differing fields"],
                              "seconds": cell["seconds"], "peak RSS KiB": cell["peak RSS KiB"]}), flush=True)
        write({
            "record": "summary", "compared": count, "exact": matches,
            "seconds": round(perf_counter() - started, 4),
            "cpu seconds": round(process_time() - cpu, 4),
            "peak RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        })
    return count != matches


if __name__ == "__main__":
    raise SystemExit(main())
