"""Compare rebuilt ordinary growth with the canonical growth engine."""

import argparse
import json
import resource
import sys
import time
from collections import Counter
from pathlib import Path

from growth import Birth, advance, families
from growth_roster import SETS, load_starts


ROOT = Path(__file__).resolve().parents[3]
NAE_GROWTH = (
    ROOT / "experiments" / "NAE-GROWTH-20261119-001B" / "NAE-GROWTH-20261119-001B-E001_nae"
)
ORDINARY = (
    ROOT / "experiments" / "FORBIDDING-JOIN-20261120-001B" / "FORBIDDING-JOIN-20261120-001B-E001_free_readings"
)


def _canonical_growth():
    sys.path[:0] = [str(NAE_GROWTH), str(ORDINARY)]
    import naelib
    from rival_growth import grow

    def canonical(supports):
        stage, record = grow(supports, "parity", "ordinary", naelib)
        if stage is None:
            return supports, record["status"], ()
        births = tuple(
            Birth(
                row["knot"], row["parents"], row["inputs"], row["fresh"],
                row["D"], row["old_inputs_already_imply_law"],
            )
            for row in record["births"]
        )
        return stage, record["status"], births

    return canonical


def _compare_start(name, start, canonical, tallies, errors):
    if len(families(start)) < 2:
        return
    tallies["eligible starts"] += 1
    supports = start
    for round_number in range(1, 5):
        stage, actual_status, actual_births = advance(supports)
        expected, expected_status, expected_births = canonical(supports)
        tallies["status comparisons"] += 1
        if actual_status != expected_status:
            errors.append([name, round_number, "status", actual_status, expected_status])
            break
        tallies["matched statuses"] += 1
        tallies[f"status {actual_status}"] += 1
        if actual_status != "funded":
            break
        tallies["numbered support comparisons"] += 1
        tallies["birth record comparisons"] += len(actual_births)
        if stage != expected or actual_births != expected_births:
            errors.append([name, round_number, "support or birth records disagree", stage != expected])
            break
        tallies["numbered supports matched"] += 1
        tallies["birth records matched"] += len(actual_births)
        if len({name for row in stage for name in row}) > 300:
            tallies["funded transitions passing 300 distinctions"] += 1
            break
        supports = stage


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--pilot", action="store_true")
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    begin = time.monotonic()
    canonical = _canonical_growth()
    panels = {}
    for which in SETS:
        started = time.monotonic()
        errors = []
        tally = Counter()
        for index, (name, start) in enumerate(load_starts(which)):
            if args.pilot and index % (1 if which == "built" else 35):
                continue
            tally["starts"] += 1
            _compare_start(name, start, canonical, tally, errors)
        panels[which] = {
            "counts": tally,
            "discrepancies": errors,
            "seconds including roster generation": round(time.monotonic() - started, 4),
        }
    result = {
        "method": "Compare literal numbered supports and every funded birth's parents, paid distinctions, fresh distinctions, lookahead demand and implication flag. Both methods read the same rebuilt starts. The canonical growth engine is used only here.",
        "scope": "Frozen stages through round four, stopping at closure, stall or more than 300 distinctions. Starts with fewer than two families were skipped as in the frozen study.",
        "run": "pilot" if args.pilot else "full",
        "totals": sum((panel["counts"] for panel in panels.values()), Counter()),
        "panels": panels,
        "seconds": round(time.monotonic() - begin, 4),
        "peak RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "totals": result["totals"],
        "discrepancy counts": {which: len(panel["discrepancies"]) for which, panel in panels.items()},
        "seconds": result["seconds"],
        "peak RSS KiB": result["peak RSS KiB"],
    }, indent=2))


if __name__ == "__main__":
    main()
