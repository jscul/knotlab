"""Regrow one archived count-profile counterexample per completed study."""

from argparse import ArgumentParser
from collections import Counter
from gzip import open as open_gzip
import json
import resource
import time

from growth_engine import build_start, grow
from later_regrow_check import (
    ARCHIVE, SEEDS, decode_seed, first_difference, normalize, seed_properties,
)


def archived_examples():
    completed = []
    stopped = []
    with open_gzip(ARCHIVE / "every_seed.jsonl.gz", "rt") as source:
        for line in source:
            study = json.loads(line)
            if "R*" not in study:
                stopped.append(study["spec"])
                continue
            key = next(key for key in study["profiles"] if key.startswith("counts 1:"))
            examples = study["examples"].get(key, [])
            if bool(examples) != bool(study["profiles"][key]["of those told apart"]):
                raise ValueError(f"inconsistent archive example for {study['spec']}")
            completed.append((study, examples[0] if examples else None))
    return completed, stopped


def law_of(study):
    spec = study["spec"]
    return tuple(spec[field] for field in ("ration", "treatment", "take"))


def replay(study, names, seeds, explicit):
    started = time.monotonic()
    spec = study["spec"]
    first = seeds["first"][spec["first"]]
    ration, treatment, take = law_of(study)
    common_round = study["R*"]
    pair = [explicit[name] if name in explicit else decode_seed(name) for name in names]
    held = [seed_properties(seed)[1] for seed in pair]
    runs = [
        grow(
            *build_start(first, seed), ration=ration, treatment=treatment, take=take,
            knot_law="nae", max_rounds=spec["rounds"], knot_limit=3000,
        )
        for seed in pair
    ]
    through = [len(run.rounds) for run in runs]
    profiles = [tuple(sum(round_.values()) for round_ in run.second_only[:common_round]) for run in runs]
    own = [normalize(run.own[:common_round]) for run in runs]
    left_col, right_col = (study["names"].index(name) for name in names)
    expected = next(
        (step for step, ids in enumerate(study["class by round"], 1) if ids[left_col] != ids[right_col]), None,
    )
    actual = first_difference(*own)
    read_common = min(through) >= common_round
    same_profile = held[0] == held[1] and profiles[0] == profiles[1]
    return {
        "study": spec,
        "pair": names,
        "archived common round": common_round,
        "completed rounds": through,
        "stops": [run.stop for run in runs],
        "guards": [run.guard for run in runs],
        "read common window": read_common,
        "held knots": held,
        "second-only birth counts": profiles,
        "first difference": actual,
        "recorded first difference": expected,
        "first differing first-only births": [signature[actual - 1] for signature in own] if actual else None,
        "confirmed": read_common and same_profile and actual is not None and actual == expected,
        "seconds": time.monotonic() - started,
    }


def pilots(witnesses, seeds, explicit):
    sample = {}
    for study, names in witnesses:
        law = law_of(study)
        if law not in sample or study["R*"] < sample[law][0]["R*"]:
            sample[law] = (study, names)
    law_counts = Counter(law_of(study) for study, _ in witnesses)
    timings = [replay(study, names, seeds, explicit) for study, names in sample.values()]
    projected = sum(law_counts[law] * timing["seconds"] for law, timing in zip(sample, timings, strict=True))
    return timings, projected


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--limit", type=int, help="Regrow only this many pairs, in archive order")
    args = parser.parse_args()
    cap = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    started = time.monotonic()
    completed, stopped = archived_examples()
    seeds = json.loads(SEEDS.read_text())
    explicit = {seed["name"]: seed for family in seeds["second"].values() for seed in family}
    witnesses = [(study, example) for study, example in completed if example is not None]
    sample, estimate = pilots(witnesses, seeds, explicit)
    results = {
        "selection": "First archived counterexample to the registered count profile in each completed study",
        "recorded completed studies": len(completed),
        "recorded studies with no counterexample": [
            study["spec"] for study, example in completed if example is None
        ],
        "recorded stopped studies": stopped,
        "pilot projected seconds": estimate,
        "pilot cases": sample,
    }
    if not args.pilot:
        trials = [replay(study, names, seeds, explicit) for study, names in witnesses[:args.limit]]
        tested = sum(row["confirmed"] for row in trials)
        results.update({
            "pairs confirmed": tested,
            "pairs failed": len(trials) - tested,
            "archived candidate pairs not run": len(witnesses) - len(trials),
            "runs stopped by a guard": sum(guard is not None for row in trials for guard in row["guards"]),
            "pairs cut off before archive common round": sum(not row["read common window"] for row in trials),
            "first difference counts": dict(sorted(Counter(row["first difference"] for row in trials if row["confirmed"]).items())),
            "witnesses": trials,
        })
    results["peak resident memory KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    results["execution seconds"] = time.monotonic() - started
    # Keep one JSON record per case on a single line so the evidence remains scannable.
    trials = results.pop("witnesses", [])
    print(json.dumps(results, indent=2)[:-2], end="")
    if trials:
        print(',\n  "witnesses": [')
        print(",\n".join("    " + json.dumps(row, separators=(",", ":")) for row in trials))
        print("  ]")
    else:
        print()
    print("}")
    if not all(row["confirmed"] for row in (*sample, *trials)):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
