"""Compare a linked prefix across all rations, treatments, takes, and knot laws."""

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path

from growth_engine import build_start, grow
from growth_replay import ARTIFACTS, FIRST, ROOT, TICKET, compare


def replay(limit):
    seeds = json.loads((ROOT / "research" / TICKET / "seeds.json").read_text())
    prefix = {seed["name"]: seed for seed in seeds["second"]["fresh"][:limit]}
    cases = []
    guard_diagnostics = []
    mismatches = []
    for runset in ("R2", "R4"):
        for path in sorted(ARTIFACTS.glob(f"runs_{runset}_*of8.jsonl.gz")):
            with gzip.open(path, "rt") as file:
                for line in file:
                    raw = json.loads(line)
                    if raw["first"] != FIRST or raw["second"] not in prefix:
                        continue
                    start, first_count = build_start(seeds["first"][FIRST], prefix[raw["second"]])
                    law = {key: raw[key] for key in ("ration", "treatment", "take", "knot_law")}
                    run = grow(start, first_count, **law)
                    fields = compare(run, raw, len(start))
                    case = dict(law, runset=runset, second=raw["second"], rounds=len(run.rounds), stop=run.stop)
                    cases.append(case)
                    if "guard" in fields and raw["guard"] is not None and run.guard is not None:
                        guard_diagnostics.append(dict(case, raw=raw["guard"], regrown=run.guard))
                        if raw["guard"]["round"] == run.guard["round"]:
                            fields.remove("guard")
                    if fields:
                        mismatches.append(dict(case, fields=fields))

    assert len(cases) == 36 * len(prefix)
    return {"first": FIRST, "prefix": list(prefix), "cases": cases, "guard_diagnostics": guard_diagnostics,
            "mismatches": mismatches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=6, choices=range(1, 61), metavar="1–60")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = replay(args.limit)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    for runset in ("R2", "R4"):
        cases = [case for case in report["cases"] if case["runset"] == runset]
        print(runset, len(cases), "runs", sum(case["rounds"] for case in cases), "rounds",
              dict(Counter(case["stop"] for case in cases)))
    print(len(report["guard_diagnostics"]), "guard diagnostics differ", len(report["mismatches"]), "other mismatches")
    for mismatch in report["mismatches"]:
        print(json.dumps(mismatch))
    if report["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
