"""Compare the frozen growth archive with an independent replay of the census."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from random import Random
import resource
from time import monotonic

from growth_replay import (
    ARCHIVE, HERE, LAWS, advance, census_starts, holders, stage_funding, stage_status, stages,
)


CHUNKS = 8
THROUGH = 6
PILOT_SIZE = 150
PILOT_SEED = 11
GROWTH_FIELDS = ("start", "closed after round", "status", "knots", "start knots", "distinctions", "places")


def dimensions(supports):
    names = holders(supports)
    return len(supports), len(names), sum(len(knots) == 1 for knots in names.values())


def describe(census_id, trace, status):
    grown = trace[-1][1]
    return {
        "start": f"census {census_id}",
        "closed after round": trace[-1][0],
        "status": status,
        "knots": len(grown),
        "start knots": len(trace[0][1]),
        "distinctions": len(holders(grown)),
        "places": sorted(map(len, grown)),
    }


def newly_closed(census_id, law, trace):
    round_number, supports = trace[-1]
    return {
        "law": law,
        "census_id": census_id,
        "round": round_number,
        "start_knots": len(trace[0][1]),
        "supports": supports,
        "last_birth_knots": list(range(len(trace[-2][1]), len(supports))),
    }


def outcome(status, round_number):
    if status == "closed":
        return f"closed after round {round_number}" if round_number else "closed at start"
    return f"{status} at round {round_number}"


def archived_outcome(status, round_number):
    if round_number == THROUGH:
        return "funded through round 6"
    if status == "closed":
        return "closed by growth" if round_number else "closed at round 0, no loose"
    if status != "stalled":
        raise ValueError((status, round_number))
    return f"stalled at round {round_number}"


def source_fingerprints():
    study = HERE.parent
    root = HERE.parents[2]
    frozen = {}
    for line in (study / "frozen.sha256").read_text().splitlines():
        expected, filename = line.split()
        observed = sha256((root / filename).read_bytes()).hexdigest()
        frozen[filename] = {"expected": expected, "observed": observed, "matches": expected == observed}
    return {"census SHA-256": sha256(ARCHIVE.read_bytes()).hexdigest(), "study freeze": frozen}


def compare_rows(expected):
    errors = []
    checked = Counter()
    for (law, chunk), replay in expected.items():
        path = HERE.parent / "out" / f"{law}_{chunk}.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        data, tally = rows[:-1], rows[-1]
        parsed = [{field: row[field] for field in GROWTH_FIELDS} for row in data]
        if parsed != replay["rows"]:
            by_start = {row["start"]: row for row in parsed}
            expected_by_start = {row["start"]: row for row in replay["rows"]}
            order_or_uniqueness_differs = list(by_start) != list(expected_by_start)
            duplicates = len(by_start) != len(parsed) or len(expected_by_start) != len(replay["rows"])
            for start in sorted(by_start.keys() | expected_by_start.keys()):
                source, observed = by_start.get(start), expected_by_start.get(start)
                if source != observed:
                    errors.append({"source": path.name, "row": source, "replay": observed})
            if order_or_uniqueness_differs or duplicates:
                errors.append({"source": path.name, "row order or uniqueness mismatch": True})
        if tally != {"tally": replay["tally"]}:
            errors.append({"source": path.name, "raw tally": tally, "replayed tally": replay["tally"]})
        checked.update({"chunks": 1, "closed rows": len(data)})
    return {"checked": checked, "compared row fields": GROWTH_FIELDS, "mismatches": errors}


def meeting_pattern(supports):
    """Forget distinction IDs while preserving the indexed knots."""
    return Counter(tuple(names) for names in holders(supports).values())


def different_allotments(first, second):
    """Record the first differing fresh counts using the common previous stage."""
    differences = []
    for left, right in zip(first.births, second.births, strict=True):
        if (left.parents, left.inputs, left.demand) != (right.parents, right.inputs, right.demand):
            raise ValueError("Both cuts must start from the same ordinary proposals")
        if len(left.fresh) != len(right.fresh):
            differences.append((left.knot, len(left.parents), left.demand, len(left.fresh), len(right.fresh)))
    return differences


def audit(ids, *, compare_archive):
    starts = census_starts()
    if len(starts) != 7075:
        raise ValueError(f"Census has {len(starts)} starts")

    closed = []
    expected = {(law, chunk): {"rows": [], "tally": Counter()} for law in LAWS for chunk in range(CHUNKS)}
    exact = {law: Counter() for law in LAWS}
    archived = {law: Counter() for law in LAWS}
    reached = {law: Counter() for law in LAWS}
    at_six = {law: Counter(closed=0, stalled=0, funded=0) for law in LAWS}
    closed_sizes = {law: {key: Counter() for key in ("knots", "distinctions", "start knots")} for law in LAWS}
    closed_types = {law: Counter() for law in LAWS}
    peak = {law: {} for law in LAWS}
    paired_outcomes = Counter()
    all_pairs = Counter()
    first_difference = Counter()
    first_support_difference = Counter()
    allotments = Counter()
    first_shortages = Counter()
    example = None
    ranked_example = None
    closed_pair_matches = Counter()

    for census_id in ids:
        start = starts[census_id]
        traces = {}
        endpoints = []
        for law in LAWS:
            trace = list(stages(start, law, through=THROUGH))
            last_round, final = trace[-1]
            status = stage_status(final)
            exact[law][outcome(status, last_round)] += 1
            endpoints.append(outcome(status, last_round))
            old_label = archived_outcome(status, last_round)
            archived[law][old_label] += 1
            if last_round == THROUGH:
                at_six[law][status] += 1
            chunk = expected[law, census_id % CHUNKS]
            chunk["tally"][old_label] += 1
            traces[law] = trace
            reached[law].update(round_number for round_number, _ in trace)
            if last_round not in peak[law] or len(final) > peak[law][last_round][0]:
                peak[law][last_round] = [len(final), census_id]
            if status == "closed" and last_round > 0:
                row = describe(census_id, trace, status)
                closed.append(newly_closed(census_id, law, trace))
                for key, counts in closed_sizes[law].items():
                    counts[row[key]] += 1
                repeated_meetings = max(meeting_pattern(final).values()) > 1
                three_places_only = set(row["places"]) == {3}
                closed_types[law][three_places_only, repeated_meetings] += 1
                if last_round < THROUGH:
                    chunk["rows"].append(row)

        paired_outcomes[tuple(endpoints)] += 1
        first_trace, second_trace = (traces[law] for law in LAWS)
        first_different_support_round = None
        first_different_round = None
        for (round_number, first), (_, second) in zip(first_trace, second_trace):
            if first == second:
                all_pairs["identical supports"] += 1
                continue
            if first_different_support_round is None:
                first_different_support_round = round_number
                previous = first_trace[round_number - 1][1]
                birth_lists = [advance(previous, law) for law in LAWS]
                differences = different_allotments(*birth_lists)
                allotments.update(tuple(details) for _, *details in differences)
                first_shortage, second_shortage = [stage_funding(supports)[1] for supports in (first, second)]
                if set(first_shortage) == {knot for knot, *_ in differences} and not second_shortage:
                    first_shortages["A129 falls short only at the differing births; A130 has no shortage"] += 1
            if meeting_pattern(first) == meeting_pattern(second):
                all_pairs["different distinction IDs only"] += 1
                continue
            all_pairs["different indexed meeting patterns"] += 1
            if first_different_round is None:
                first_different_round = round_number
            first_sizes, second_sizes = dimensions(first), dimensions(second)
            if first_sizes != second_sizes:
                all_pairs["different counts of knots, distinctions or loose distinctions"] += 1
                candidate = (round_number, max(first_sizes[0], second_sizes[0]), census_id)
                if ranked_example is None or candidate < ranked_example:
                    ranked_example = candidate
                    example = {
                        "census id": census_id, "start supports": start,
                        "first round with different dimensions": round_number,
                        "endpoint per law": dict(zip(LAWS, endpoints, strict=True)),
                        "dimensions per formed round [round, knots, distinctions, loose distinctions]": {
                            law: [(r, *dimensions(supports)) for r, supports in traces[law]] for law in LAWS
                        },
                        "supports per law at the first difference": dict(zip(LAWS, [first, second], strict=True)),
                        "shortages per law at the first difference": {
                            law: stage_funding(supports)[1] for law, supports in zip(LAWS, [first, second], strict=True)
                        },
                    }
        no_difference = "no difference at shared rounds"
        first_support_difference[first_different_support_round or no_difference] += 1
        first_difference[first_different_round or no_difference] += 1
        if any(endpoint.startswith("closed after") for endpoint in endpoints):
            closed_pair_matches["total starts closed after growth by either law"] += 1
            if endpoints[0] == endpoints[1] and first_trace[-1][1] == second_trace[-1][1]:
                closed_pair_matches["same closure round and identical supports"] += 1

    comparison = compare_rows(expected) if compare_archive else None
    return {
        "starts": len(ids),
        "exact statuses": exact,
        "archived status definitions": archived,
        "round-six endpoints classified before round seven": at_six,
        "formed stages including starts": reached,
        "largest terminal knot count by round [knots, census id]": peak,
        "newly closed sizes": closed_sizes,
        "newly closed membership [only three-place knots, repeated meetings, stages]": {
            law: [(*details, count) for details, count in sorted(counts.items())] for law, counts in closed_types.items()
        },
        "newly closed pairs": closed_pair_matches,
        "paired endpoints [A129, A130, census starts]": [(*pair, count) for pair, count in sorted(paired_outcomes.items())],
        "paired stage differences": all_pairs,
        "first support difference by round": first_support_difference,
        "first indexed meeting-pattern difference by round": first_difference,
        "first differing grants [parents, demand, A129 fresh, A130 fresh, births]": [
            (*details, count) for details, count in sorted(allotments.items())
        ],
        "shortages at first differing stage": first_shortages,
        "paired witness": example,
        "archived comparison": comparison,
    }, closed


def save_json(filename, value):
    path = HERE / filename
    pending = path.with_suffix(".tmp")
    if filename == "growth_stages.json":
        pending.write_text("[\n" + ",\n".join(json.dumps(row) for row in value) + "\n]\n")
    else:
        pending.write_text(json.dumps(value, indent=2) + "\n")
    pending.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", choices=("pilot", "census"))
    args = parser.parse_args()
    start_time = monotonic()
    ids = range(len(census_starts()))
    if args.panel == "pilot":
        ids = Random(PILOT_SEED).sample(ids, PILOT_SIZE)
    result, closed = audit(ids, compare_archive=args.panel == "census")
    result["sources"] = source_fingerprints()
    if args.panel == "pilot":
        result["sample"] = {"seed": PILOT_SEED, "weighting": "each census class equally per draw without replacement", "census ids": ids}
        result["newly closed pilot rows"] = closed
    else:
        closed.sort(key=lambda row: (row["census_id"], row["law"]))
        save_json("growth_stages.json", closed)
    result["wall seconds"] = round(monotonic() - start_time, 3)
    result["peak resident KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    save_json(f"growth_{args.panel}.json", result)
    print(f"{args.panel} growth audit in {result['wall seconds']:.3f} seconds")
    print(json.dumps(result["exact statuses"], indent=2))
    if args.panel == "census":
        print(json.dumps(result["archived comparison"], indent=2))


if __name__ == "__main__":
    main()
