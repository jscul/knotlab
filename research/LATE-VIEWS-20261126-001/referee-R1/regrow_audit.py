"""Compare direct growth with saved growth and the frozen views.

Run from the repository root under a 2.5 GiB address-space limit.
The same code and caps apply to the timed pilot and the full replay.
"""

import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
import gzip
import hashlib
import json
from pathlib import Path
import random
import resource
from time import perf_counter

from regrow import grow


STUDY = Path(__file__).resolve().parent.parent
FREEZE = "d6aefb73dc32220c61166efc94e568c0a6906f48a7ccf7eb508d72c1ab3f699d"
ARCHIVE_CAP = 30_000
EXTENSION_CAP = 100_000
PANEL = {
    "uniform": "held_out",
    "stratified": "grown_stratified",
    "handbuilt": "grown_handbuilt",
    "grow7": "grown_grow7",
    "horizon": "grown_horizon",
}
PILOT = {
    "uniform": {62655, 6408, 82531},
    "stratified": {2041, 30324, 82523},
    "handbuilt": {0, 13, 14},
    "grow7": {0, 344},
    "horizon": {557, 79034},
}
UNIFORM_REPLAY_SEED = 20261132
READINGS = ("n", "sig0", "sig1")
EMPTY_ROUND = {"n": 0, "sig0": [], "sig1": []}


def predictions():
    checksum = hashlib.sha256()
    indexed = {}
    with gzip.open(STUDY / "predictions.jsonl.gz", "rb") as lines:
        for line in lines:
            checksum.update(line)
            row = json.loads(line)
            key = row["set"], row["knot law"], row["index"]
            if key in indexed:
                raise ValueError(f"duplicate frozen prediction {key}")
            indexed[key] = row
    if checksum.hexdigest() != FREEZE:
        raise ValueError("frozen prediction checksum differs")
    return indexed


def uniform_selection(forecasts):
    by_stratum = defaultdict(list)
    for row in forecasts.values():
        if (
            row["set"] == "uniform"
            and row["knot law"] == "nae"
            and row["read"] != "stall"
        ):
            by_stratum[row["read"], row["stratum"]].append(row["index"])
    rng = random.Random(UNIFORM_REPLAY_SEED)
    selected = {6408, 82531}
    for classification, stratum in sorted(by_stratum):
        candidates = sorted(set(by_stratum[classification, stratum]) - selected)
        limit = 30 if classification == "predicted" else 2
        selected.update(rng.sample(candidates, min(limit, len(candidates))))
    return selected


def compare_rows(actual, expected, compare_empty=False):
    differences = {}
    if compare_empty:
        actual = actual + [EMPTY_ROUND] * max(0, len(expected) - len(actual))
    for number, (seen, wanted) in enumerate(zip(actual, expected), 1):
        for reading in READINGS:
            if reading not in differences and seen[reading] != wanted[reading]:
                differences[reading] = number
    return differences


def expected_counts_match(rows):
    return all(
        sum(count for _, count in row[reading]) == row["n"]
        for row in rows
        for reading in ("sig0", "sig1")
    )


def replay_rows(grown, forecast, rounds, full, summary, errors, misses, extensions):
    index = grown["index"]
    law, dataset = forecast["knot law"], forecast["set"]
    identity = {"set": dataset, "law": law, "index": index}
    full_replay = full or not grown["rows"]
    target = rounds if full_replay else 1
    started = perf_counter()
    replay = grow(grown["stars"], target, law, ARCHIVE_CAP, trace_rounds=2)
    summary["growth seconds"] += perf_counter() - started
    actual_rows = replay["rows"]
    cap_stop = grown["end"] == "bound"
    raw_rows = grown["rows"] if full_replay else grown["rows"][:1]

    counts = summary["counts"]
    counts["records"] += 1
    counts["birth rounds compared"] += min(len(raw_rows), len(actual_rows))
    counts["births compared"] += sum(row["n"] for row in actual_rows)
    counts["full replay requested" if full_replay else "first round only"] += 1
    summary["knot counts"][len(grown["stars"])] += 1
    summary["archive ends"][grown["end"]] += 1
    if cap_stop:
        summary["archive cap stops"].append({
            "index": index,
            "rounds": len(grown["rows"]),
            "knots": grown["knots"],
            "frozen classification": forecast["read"],
        })

    archive_differences = compare_rows(actual_rows, raw_rows)
    if len(actual_rows) != len(raw_rows):
        archive_differences["number of rounds"] = [len(actual_rows), len(raw_rows)]
    if full_replay and replay["end"] != grown["end"]:
        archive_differences["end"] = [replay["end"], grown["end"]]
    if full_replay and replay["knots"] != grown["knots"]:
        archive_differences["knots"] = [replay["knots"], grown["knots"]]
    if archive_differences:
        errors.append({**identity, "differences": archive_differences, "stars": grown["stars"]})
    elif full_replay:
        counts["full archive matched"] += 1
    else:
        counts["first round matched"] += 1

    read = forecast["read"]
    summary["classifications"][read] += 1
    if read == "stall":
        counts["frozen stall matched"] += replay["end"] == "stalls at round 1"
    if read != "predicted":
        return replay
    predicted_rows = forecast["rows"]
    expected_length = rounds
    if len(predicted_rows) != expected_length:
        raise ValueError(f"wrong frozen horizon {identity}")
    if not expected_counts_match(predicted_rows):
        raise ValueError(f"frozen histogram mass differs from its total {identity}")
    differences = compare_rows(
        actual_rows, predicted_rows, compare_empty=replay["end"].startswith("closes")
    )
    if replay["end"].startswith("stalls"):
        differences["stall"] = len(actual_rows) + 1
    if differences:
        counts["frozen view differs"] += 1
        first = min(differences.values())
        misses.append({
            **identity,
            "sample selected for": grown.get("drawn for"),
            "archive descriptions": forecast["rare strata"],
            "frozen stratum": forecast["stratum"],
            "first differences": differences,
            "stars": grown["stars"],
            "parents and fresh distinctions at first difference": (
                replay["traces"][first - 1] if first <= len(replay["traces"]) else None
            ),
            "direct row": actual_rows[first - 1] if first <= len(actual_rows) else EMPTY_ROUND,
            "frozen row": predicted_rows[first - 1],
        })
    else:
        counts["frozen view matches compared rounds"] += 1
        counts["frozen view matches saved prefix"] += full_replay
        if len(actual_rows) == rounds or replay["end"].startswith("closes"):
            counts["frozen view matches requested horizon"] += 1

    if cap_stop and full_replay:
        projected = len(grown["stars"]) + sum(row["n"] for row in predicted_rows)
        extra = {
            **identity,
            "original rounds": len(actual_rows),
            "target rounds": rounds,
            "projected knots at target": projected,
        }
        if projected > EXTENSION_CAP:
            extra["extension"] = "not run: frozen count above extension cap"
        elif dataset not in ("stratified", "horizon"):
            extra["extension"] = "not run: extension of this set outside review scope"
        else:
            started = perf_counter()
            extended = grow(grown["stars"], rounds, law, EXTENSION_CAP)
            extra["seconds"] = perf_counter() - started
            extra["extension"] = extended["end"]
            extra["rounds reached"] = len(extended["rows"])
            extra["knots"] = extended["knots"]
            extra["saved prefix matched"] = extended["rows"][:len(raw_rows)] == raw_rows
            extra["frozen differences"] = compare_rows(
                extended["rows"], predicted_rows, compare_empty=extended["end"].startswith("closes")
            )
            extra["births after saved prefix"] = sum(
                row["n"] for row in extended["rows"][len(raw_rows):]
            )
            summary["extension seconds"] += extra["seconds"]
        extensions.append(extra)
    return replay


def compare_laws(replays, totals):
    nae, parity = replays
    totals["pairs compared"] += 1
    if nae["rows"] == parity["rows"] and nae["end"] == parity["end"]:
        totals["same through compared rounds or end"] += 1
        return
    totals["different"] += 1
    if not parity["rows"] or len(nae["rows"]) < len(parity["rows"]):
        return
    final = parity["rows"][-1]
    signature = final["sig0"]
    expected = (
        len(signature) == 1
        and signature[0][0][2] == 0
        and signature[0][1] == 1
        and final["n"] == 1
        and parity["end"].startswith("closes")
        and nae["rows"][:len(parity["rows"]) - 1] == parity["rows"][:-1]
    )
    if expected:
        continuing = nae["rows"][len(parity["rows"]) - 1]
        kind, parents, _, _ = signature[0][0]
        fresh = max(1, 3 - parents)
        expected = (
            continuing["sig0"] == [[[kind, parents, fresh, parents + fresh], 1]]
            and continuing["sig1"][0][0][1] == final["sig1"][0][0][1]
        )
    if expected:
        totals["differ first at parity's single zero-fresh birth"] += 1


def audit(pilot):
    began = perf_counter()
    frozen = predictions()
    prediction_seconds = perf_counter() - began
    uniform_selected = uniform_selection(frozen)
    errors, misses, extensions = [], [], []
    summaries, law_pairs = {}, {}
    parsed_count = 0
    for dataset, basename in PANEL.items():
        started = perf_counter()
        laws = ("nae",) if dataset == "horizon" else ("nae", "parity")
        rounds = 40 if dataset == "horizon" else 24
        law_pairs[dataset] = Counter()
        summaries[dataset] = {
            law: {
                "counts": Counter(),
                "archive ends": Counter(),
                "archive cap stops": [],
                "classifications": Counter(),
                "knot counts": Counter(),
                "growth seconds": 0.,
                "extension seconds": 0.,
            }
            for law in laws
        }
        with ExitStack() as files:
            sources = [
                files.enter_context(gzip.open(STUDY / f"{basename}_{law}.jsonl.gz", "rt"))
                for law in laws
            ]
            for lines in zip(*sources, strict=True):
                inputs = [json.loads(row) for row in lines]
                index = inputs[0]["index"]
                if any(row["index"] != index or row["stars"] != inputs[0]["stars"] for row in inputs):
                    raise ValueError(f"saved starts differ across laws in {dataset} at {index}")
                if pilot and index not in PILOT[dataset]:
                    continue
                parsed_count += len(inputs)
                replays = []
                for law, grown in zip(laws, inputs, strict=True):
                    if law != grown["knot law"]:
                        raise ValueError(f"wrong law in {dataset} at {index}")
                    forecast = frozen[dataset, law, index]
                    full = dataset != "uniform" or forecast["read"] == "stall" or index in uniform_selected
                    replay = replay_rows(
                        grown, forecast, rounds, full, summaries[dataset][law],
                        errors, misses, extensions,
                    )
                    replays.append(replay)
                if len(replays) == 2:
                    compare_laws(replays, law_pairs[dataset])
        for summary in summaries[dataset].values():
            summary["panel elapsed seconds"] = perf_counter() - started
        print(dataset, law_pairs[dataset], flush=True)
    if not pilot and parsed_count != len(frozen):
        raise ValueError("saved and frozen record counts differ")
    return {
        "selection": "timed pilot" if pilot else (
            "every start checked through round one or stall. Uniform accepted starts: "
            "up to 30 per frozen stratum, the known miss and a cap-truncated start through the saved end. "
            "Uniform cycle-declined starts: up to two per frozen stratum through the saved end. "
            "Every other set replayed through the saved end."
        ),
        "pilot indices": {key: sorted(value) for key, value in PILOT.items()} if pilot else None,
        "uniform nonstalled full indices": sorted(uniform_selected),
        "uniform full replay sample seed": UNIFORM_REPLAY_SEED,
        "knots cap for archived replay": ARCHIVE_CAP,
        "knots cap for extension": EXTENSION_CAP,
        "address space limit bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
        "growth worker processes": 1,
        "frozen prediction sha256": FREEZE,
        "seconds reading predictions": prediction_seconds,
        "seconds elapsed": perf_counter() - began,
        "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "raw parent evidence": (
            "the saved growth contains parent descriptions and counts, but no per-birth parent indices"
        ),
        "panels": summaries,
        "law comparisons": law_pairs,
        "raw archive differences": errors,
        "frozen prediction differences": misses,
        "cap extensions": extensions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.pilot)
    with args.output.open("w") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    if result["raw archive differences"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
