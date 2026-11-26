"""Compare independently grown FF descent with the registered held-out traces."""

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path

from growth_engine import build_start, grow


ROOT = Path(__file__).resolve().parents[3]
TICKET = "FOLLOWS-THE-FORM-20261125-001A"
ARTIFACTS = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_place_fixed_form_changed"
FIRST = "O"
RATION = "CAP-3"
TREATMENT = "CANCEL-WAIT"
TAKES = ("none", "sole")


def raw_cases(runset):
    cases = {}
    for part in sorted(ARTIFACTS.glob(f"runs_{runset}_*of8.jsonl.gz")):
        with gzip.open(part, "rt") as file:
            for line in file:
                row = json.loads(line)
                if (row["first"], row["ration"], row["treatment"]) == (FIRST, RATION, TREATMENT):
                    key = (row["take"], row["second"])
                    if key in cases:
                        raise ValueError(f"Duplicate raw row for {key}")
                    cases[key] = row
    return cases


def raw_counter(entries):
    return Counter({tuple(entry[:-1]): entry[-1] for entry in entries})


def compare(run, raw, start_count):
    own = run.own
    wider = run.wider
    values = {
        "make": own,
        "wider": wider,
        "n_own": [record.total() for record in own],
        "n_of_first": [record.total() for record in wider],
        "n_both": [sum(count for entry, count in record.items() if not entry[-1]) for record in wider],
        "sec_only": [record.total() for record in run.second_only],
        "rounds_read": len(run.rounds),
        "knots": len(run.knots),
        "start_member_final": any(knot < start_count for knot in run.final_members),
        "last_member_round": max(
            (index for index, record in enumerate(run.rounds, start=1) if any(knot < start_count for knot in record.roster)),
            default=0,
        ),
        "stop": run.stop,
        "guard": run.guard,
    }
    mismatches = []
    for key, value in values.items():
        expected = tuple(map(raw_counter, raw[key])) if key in {"make", "wider"} else raw[key]
        if value != expected:
            mismatches.append(key)
    return mismatches


def replay(seed_limit):
    seeds = json.loads((ROOT / "research" / TICKET / "seeds.json").read_text())
    first = seeds["first"][FIRST]
    second_seeds = seeds["second"]["fresh"][:seed_limit]
    report = {
        "first": {"name": FIRST, **first},
        "family": "fresh",
        "ration": RATION,
        "treatment": TREATMENT,
        "knot_law": "nae",
        "max_rounds": 9,
        "knot_limit": 3000,
        "second_seeds": [seed["name"] for seed in second_seeds],
        "comparisons": [],
        "mismatches": [],
    }
    controls = {}
    for take in TAKES:
        controls[take] = grow(*build_start(first), ration=RATION, treatment=TREATMENT, take=take)

    for runset in ("R2", "R2u"):
        cases = raw_cases(runset)
        for take in TAKES:
            bare = controls[take]
            for second in (None, *second_seeds):
                name = None if second is None else second["name"]
                start, first_count = build_start(first, second, unlinked=runset == "R2u")
                run = bare if second is None else grow(start, first_count, ration=RATION, treatment=TREATMENT, take=take)
                raw = cases[take, name]
                mismatches = compare(run, raw, len(start))
                if runset == "R2u":
                    common = min(len(run.rounds), len(bare.rounds))
                    if run.own[:common] != bare.own[:common]:
                        mismatches.append("unlinked own descent differs from bare on common rounds")
                result = {"runset": runset, "take": take, "second": name, "rounds": len(run.rounds)}
                report["comparisons"].append(result)
                if mismatches:
                    report["mismatches"].append(dict(result, fields=mismatches))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=60, choices=range(1, 61), metavar="1–60")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = replay(args.limit)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")

    compared = Counter((row["runset"], row["take"]) for row in report["comparisons"])
    rounds = Counter()
    for row in report["comparisons"]:
        rounds[row["runset"], row["take"]] += row["rounds"]
    for runset, take in compared:
        print(f"{runset} {take}: {compared[runset, take]} records, {rounds[runset, take]} completed rounds")
    print(f"{len(report['mismatches'])} records differ")
    for mismatch in report["mismatches"]:
        print(json.dumps(mismatch))
    if report["mismatches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
