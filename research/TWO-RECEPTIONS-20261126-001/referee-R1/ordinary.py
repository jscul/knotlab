"""Try the ordinary count against the next actual roster, across starts and takes."""

import argparse
import json
import resource
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter

resource.setrlimit(resource.RLIMIT_AS, (1500 * 1024**2,) * 2)
ROOT = Path(__file__).resolve().parents[3]
ENGINE = next((ROOT / "experiments/WHAT-A-BIRTH-CARRIES-20261125-001B").glob("*/eng.py"))
sys.path.insert(0, str(ENGINE.parent))
import eng

# Each entry lists the distinctions held together, in the start's knot order.
STARTS = {
    "one three-place knot": [[0, 1, 2]],
    "three mutually sharing knots with unequal loose holdings":
        [[0, 1, 3], [0, 2, 4, 5], [1, 2, 6, 7]],
    "four knots with one meeting all three others":
        [[0, 1, 2, 7], [0, 3, 4], [1, 3, 5], [2, 8, 9]],
    "two separate pairs of knots, each pair with a shared distinction":
        [[0, 1, 2], [0, 3, 4], [5, 6, 7], [5, 8, 9]],
}
TAKES = [(None, None), ("MET", "OLDEST"), ("MET", "NEWEST"), ("MET-SOLE", None),
         ("STEPS1-SOLE", None), ("STEPS2-SOLE", None), ("J-EACH-PART", None)]


def grow(stars, ration, take, choice):
    law = eng.Law(ration, "CANCEL-WAIT", take, "nae", choice)
    state = eng.from_stars(stars)
    guard = eng.Guard(4)
    stats = Counter()
    stop = "6 rounds"
    for _ in range(6):
        current = state.copy()
        try:
            record = eng.play_round(current, law, guard)
            # Reconstruct the next roster from actual loose holdings, not its placeholders.
            live = [(u, len(current.usable(u)), 0) for u in range(current.n_knots) if current.usable(u)]
            roster = eng.build_roster(current, live, "next actual roster", guard)
        except eng.GuardStop as exc:
            stop = str(exc)
            break
        counted = Counter(u for group in roster.groups for u in group)
        measured_short = {u for u, h, _ in live if counted[u] > h and current.made[u] > 0}
        stats["made short on following roster"] += len(measured_short)
        stats["short start observations"] += sum(state.made[u] == 0 for u in record["short"])
        stats["births"] += len(record["births"])
        stats["rounds"] += 1
        if record["births"]:
            assert set(map(tuple, roster.groups)) == set(map(tuple, record["demand"].groups))
        for b in record["births"]:
            u = b["id"]
            assert counted[u] == b["D"] and len(current.usable(u)) == b["f"]
            assert all(len(state.holders[d]) >= 2 for d in b["takes"])
            stats["taken distinctions"] += len(b["takes"])
        for u in record["members"]:
            if u not in record["short"]:
                assert not current.usable(u)
        state = current
        if state.n_knots > 500:
            stop = "500 knots exceeded"
            break
    return {"counts": dict(stats), "stop": stop}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    rows = []
    start_time = perf_counter()
    for title, stars in STARTS.items():
        if args.pilot and title != next(iter(STARTS)):
            continue
        for ration, take, choice in [("ORD", t, c) for t, c in TAKES] + [("FLOOR1", None, None)]:
            before = perf_counter()
            result = grow(stars, ration, take, choice)
            rows.append({"start": title, "law": [ration, take, choice], **result,
                         "seconds": round(perf_counter() - before, 4)})
    print(json.dumps({"seconds": round(perf_counter() - start_time, 3),
                      "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
