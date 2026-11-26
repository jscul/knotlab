"""Regrow sampled pair identities and compare all recorded measurements."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import random
import resource
from time import perf_counter, process_time

from growth import LAWS, measure


HERE = Path(__file__).resolve().parent
SEED = 20261126
PARTS = {
    "census": ("hold_runs.jsonl.gz", 12, 1500, (1, 2, 3)),
    "linked": ("linked_runs.jsonl.gz", 24, 6000, (3, 5, 8)),
}
CONTROLS = {
    "linked under inheritance": [("n4:g14:1322@0", "g6:122@0")],
    "cap hearings": [
        ("n3:g7:122@0", "g6:122@0"),
        ("n3:g7:122@0", "g7:122@0"),
        ("n4:g17:1212@0", "g6:122@0"),
        ("n4:g17:1212@0", "g7:122@0"),
    ],
}


def archive_rows(path):
    with gzip.open(path, "rt") as handle:
        return [json.loads(line) for line in handle]


def identity(row):
    return row["A"], row["B"]


def ration_name(spec):
    return spec[1] if spec[0] == "HOLD" else spec[0]


def replay(part, count, pilot):
    filename, rounds, bound, edits_after = PARTS[part]
    path = HERE.parent / filename
    rows = archive_rows(path)
    population = sorted({identity(row) for row in rows})
    sample = random.Random(SEED).sample(population, count)
    deliberate = {}
    if part == "census":
        deliberate = {goal: pairs[:1] if pilot else pairs for goal, pairs in CONTROLS.items()}
    selected = list(dict.fromkeys(sample + [pair for pairs in deliberate.values() for pair in pairs]))
    by_pair = {pair: [] for pair in selected}
    tallies = {}
    for row in rows:
        pair = identity(row)
        if pair in by_pair:
            by_pair[pair].append(row)

    rebuilt = []
    for pair in selected:
        expected = {"INHERIT", "NET-OWING", "CAP-3"}
        if part == "census":
            expected.add("ORD")
        originals = by_pair[pair]
        assert len(originals) == len(expected)
        assert {ration_name(row["law"]) for row in originals} == expected
        for stored in originals:
            started = perf_counter()
            name = ration_name(stored["law"])
            observed, edits = measure(*pair, LAWS[name], rounds=rounds,
                                      bound=bound, edits_after=edits_after)
            observed.update(A=pair[0], B=pair[1], law=stored["law"])
            differing = sorted(k for k in observed.keys() | stored.keys()
                               if observed.get(k) != stored.get(k))
            tally = tallies.setdefault(name, Counter())
            tally["compared"] += 1
            tally["equal"] += not differing
            tally["linked after round 3"] += len(observed["linked"]) >= 3 and observed["linked"][2] is True
            tally["pairs with a short knot made after the start"] += any(observed["made short"])
            tally["changes"] += len(observed["changes"])
            for change in observed["changes"]:
                heard = change["heard"]
                tally["heard"] += heard is not None
                if heard is not None and heard > 6:
                    tally["late"] += 1
                    tally["late with later births in both"] += (
                        any(observed["births"][heard:]) and any(change["births with"][heard:])
                    )
            rebuilt.append({
                "row": observed, "differing fields": differing, "edits": edits,
                "stored differing values": {key: stored.get(key) for key in differing},
                "seconds": round(perf_counter() - started, 4),
            })
    return {
        "archive": filename, "sha256": sha256(path.read_bytes()).hexdigest(),
        "population pairs": len(population), "uniform sample": sample,
        "deliberate": deliberate, "round bound": rounds, "knot bound": bound,
        "guard multiplier": 4, "changes after rounds": edits_after,
        "tallies": tallies, "rebuilt": rebuilt,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=int, default=8)
    parser.add_argument("--linked", type=int, default=5)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    memory = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (570, 575))
    started, cpu = perf_counter(), process_time()
    result = {"seed": SEED, "pilot": args.pilot, "address space cap bytes": memory}
    for part in PARTS:
        result[part] = replay(part, getattr(args, part), args.pilot)
    result.update({
        "seconds": round(perf_counter() - started, 3),
        "cpu seconds": round(process_time() - cpu, 3),
        "peak RSS KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    })
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"seconds": result["seconds"], "cpu seconds": result["cpu seconds"],
                      "peak RSS KiB": result["peak RSS KiB"],
                      **{p: result[p]["tallies"] for p in PARTS}}))
    return any(entry["differing fields"] for part in PARTS for entry in result[part]["rebuilt"])


if __name__ == "__main__":
    raise SystemExit(main())
