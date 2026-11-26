"""Recover reader comparisons on the two previously unread tree-plus draws, where feasible."""

import argparse
from collections import Counter
import json
from pathlib import Path
import resource
import signal
import time

from growth import grow
from replay_inputs import cases

HERE = Path(__file__).resolve().parent


def interrupt(_signum, _frame):
    raise TimeoutError


def compare(case, t, law, budget, include_h2):
    roster = case.roster
    reader = case.reader
    cache = {}

    def run(members):
        if members not in cache:
            signal.setitimer(signal.ITIMER_REAL, budget)
            try:
                growth = grow(roster.restrict(members), t, law, cap=3000)
                cache[members] = growth.end, (
                    None if growth.end == "cap" else growth.views(reader, t)), [len(row) for row in growth.rows]
            except (TimeoutError, MemoryError, RecursionError) as exc:
                cache[members] = type(exc).__name__, None, []
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        return cache[members]

    full, view, births = run(frozenset(roster.loose))
    result = {"full_end": full, "full_births_per_round": births}
    if view is not None:
        regions = [("within_t", case.within(t)), ("within_t_plus_one", case.within(t + 1))]
        if include_h2:
            for j, (at_round, members) in enumerate(case.h2 + case.admissions):
                if t == at_round:
                    regions.append((f"admission_{j + 1}", members))
        for name, members in regions:
            end, seen, made = run(members)
            result[name] = {"knots": len(members), "end": end,
                            "agree": None if seen is None else view == seen,
                            "births_per_round": made}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--seconds-per-growth", type=int, default=15)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (900 << 20, 900 << 20))
    signal.signal(signal.SIGALRM, interrupt)
    report = {"seconds_per_growth": args.seconds_per_growth,
              "address_space_MiB": 900, "birth_cap_per_round": 3000, "records": []}
    start = time.monotonic()
    for case in cases("treeplus25"):
        if "not read" not in case.record:
            continue
        row = {"draw_index": case.index, "reader": case.reader,
               "original_omission": case.record["not read"], "laws": {}}
        report["records"].append(row)
        for law in ("nae", "parity"):
            by_round = {}
            row["laws"][law] = by_round
            for t in range(1, (2 if args.pilot else 7) + 1):
                before = time.monotonic()
                out = compare(case, t, law, args.seconds_per_growth, True)
                out["seconds"] = round(time.monotonic() - before, 4)
                by_round[t] = out
                if out["full_end"] in ("cap", "TimeoutError", "MemoryError", "RecursionError"):
                    break
    report["elapsed_seconds"] = round(time.monotonic() - start, 4)
    target = HERE / ("omitted_pilot.json" if args.pilot else "omitted.json")
    target.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
