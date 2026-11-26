"""Reconstruct ordinary growth from the frozen rules and compare the saved runs."""

import argparse
import gzip
import json
import random
import resource
from collections import Counter, defaultdict
from itertools import accumulate, combinations
from pathlib import Path
from time import perf_counter


STUDY = Path(__file__).resolve().parents[1]
HORIZON = 24
CAP = 30_000
SAMPLE_SEED = 130711
READINGS = {"sig0": 5, "sig1": 7}


def start_state(stars):
    if not stars:
        raise ValueError("A census start has at least one knot")
    holders = defaultdict(list)
    for knot, star in enumerate(stars):
        if len(star) < 3 or len(set(star)) != len(star):
            raise ValueError(f"Invalid starting places: {star}")
        for distinction in star:
            holders[distinction].append(knot)

    loose = [0] * len(stars)
    neighbours = [set() for _ in stars]
    for members in holders.values():
        if len(members) == 1:
            loose[members[0]] += 1
        elif len(members) == 2:
            first, second = members
            if second in neighbours[first]:
                raise ValueError(f"Repeated pair of holders: {members}")
            neighbours[first].add(second)
            neighbours[second].add(first)
        else:
            raise ValueError(f"Invalid count of holders: {members}")

    reached = {0}
    pending = [0]
    while pending:
        for neighbour in neighbours[pending.pop()] - reached:
            reached.add(neighbour)
            pending.append(neighbour)
    if len(reached) != len(stars) or not any(loose) or any(count > 3 for count in loose):
        raise ValueError(f"Invalid census start: {stars}")
    live = {knot for knot, count in enumerate(loose) if count}
    return loose, [neighbourhood & live for neighbourhood in neighbours]


def later_met_sets(parent_lists, old_count):
    children = [set() for _ in range(old_count)]
    for child, parents in enumerate(parent_lists):
        for parent in parents:
            children[parent].add(child)
    return children


def join_groups(met_sets):
    joinable = defaultdict(set)
    common_knots = defaultdict(set)
    for common_knot, met_set in enumerate(met_sets):
        if len(met_set) < 2:
            continue
        for member in met_set:
            joinable[member].update(met_set)
            common_knots[member].add(common_knot)
    for member, neighbours in joinable.items():
        neighbours.remove(member)

    # A clique without a common knot remains without one in every larger
    # clique. It suffices to search the maximal cliques of the joinable pairs.
    def maximal_unheld(chosen, possible, excluded, common):
        if len(chosen) + len(possible) < 3:
            return
        if not possible:
            if not excluded and not common:
                yield tuple(sorted(chosen))
            return
        if any(possible <= met_sets[knot] for knot in common):
            return
        pivot = max(possible | excluded, key=lambda member: len(possible & joinable[member]))
        for member in possible - joinable[pivot]:
            member_common = common_knots[member]
            yield from maximal_unheld(
                chosen + (member,),
                possible & joinable[member],
                excluded & joinable[member],
                common & member_common if chosen else member_common,
            )
            possible.remove(member)
            excluded.add(member)

    groups = list(maximal_unheld((), set(joinable), set(), set()))
    covered = {pair for group in groups for pair in combinations(group, 2)}
    groups.extend(
        (first, second)
        for first, neighbours in joinable.items()
        for second in neighbours
        if first < second and (first, second) not in covered
    )
    return sorted(groups)


def births_in_round(loose, groups, knot_law):
    remaining = list(loose)
    for group in groups:
        for member in group:
            remaining[member] -= 1
    if min(remaining) < 0:
        return None
    parents = list(groups)
    parents.extend((member,) for member, count in enumerate(remaining) for _ in range(count))
    next_groups = join_groups(later_met_sets(parents, len(loose)))
    demand = Counter(member for group in next_groups for member in group)
    closes = knot_law == "parity" and len(parents) == 1
    fresh = [
        0 if closes else max(demand[child], 3 - len(source), 1)
        for child, source in enumerate(parents)
    ]
    return parents, fresh, next_groups


def start_signatures(stars):
    return [("start", 0, 0, len(star)) for star in stars]


def round_signatures(parents, fresh, old_signatures):
    plain = [
        ("offshoot" if len(source) == 1 else "join", len(source), count, len(source) + count)
        for source, count in zip(parents, fresh, strict=True)
    ]
    with_parents = Counter(
        (signature, tuple(sorted(old_signatures[parent] for parent in source)))
        for signature, source in zip(plain, parents, strict=True)
    )
    return plain, {"n": len(parents), "sig0": Counter(plain), "sig1": with_parents}


def grow(stars, knot_law, *, rounds=HORIZON, cap=CAP, observe=None):
    """Report completed rounds, with parent IDs relative to the previous round."""
    if knot_law not in {"nae", "parity"}:
        raise ValueError(f"Unknown knot law: {knot_law}")
    loose, met_sets = start_state(stars)
    groups = join_groups(met_sets)
    old_signatures = start_signatures(stars)
    rows = []
    knot_count = len(stars)
    end = "rounds"
    for round_no in range(1, rounds + 1):
        if not any(loose):
            end = f"closes at round {round_no}"
            break
        result = births_in_round(loose, groups, knot_law)
        if result is None:
            end = f"stalls at round {round_no}"
            break
        parents, loose, groups = result
        old_signatures, row = round_signatures(parents, loose, old_signatures)
        if observe is not None:
            observe(round_no, parents, loose)
        rows.append(row)
        knot_count += len(parents)
        if knot_count > cap:
            end = "bound"
            break
    return {"rows": rows, "end": end, "knots": knot_count}


def read_archive(path):
    def tuple_signature(signature):
        if isinstance(signature, list):
            return tuple(map(tuple_signature, signature))
        return signature

    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            for row in record["rows"]:
                for reading in READINGS:
                    row[reading] = {tuple_signature(signature): count for signature, count in row[reading]}
            yield record


def classify(rows, end):
    terminal = end.split(" at round ")[0]
    if terminal in {"closes", "stalls"}:
        return terminal
    counts = [row["n"] for row in rows]
    if len(counts) >= 8:
        differences = counts[-8:]
        for dimension in range(1, 5):
            if differences[0] > 0 and len(set(differences)) == 1:
                return f"dim {dimension}"
            differences = [right - left for left, right in zip(differences, differences[1:])]
    if len(counts) >= 5:
        ratios = [right / left for left, right in zip(counts[-5:-1], counts[-4:])]
        if min(ratios) > 1.05 and max(ratios) - min(ratios) <= 0.01:
            return f"rate {ratios[-1]:.2f}"
    return "unread"


def settling_round(rows, reading, dimension, least):
    # A degree-at-most-D-minus-one fit agrees after K iff the D-th difference
    # ending at any round beyond K vanishes in each multiset coordinate.
    differences = [row[reading] for row in rows]
    for _ in range(dimension):
        next_differences = []
        for left, right in zip(differences, differences[1:]):
            delta = Counter(right)
            delta.subtract(left)
            next_differences.append({signature: count for signature, count in delta.items() if count})
        differences = next_differences
    last_disagreement = max(
        (round_no for round_no, delta in enumerate(differences, dimension + 1) if delta),
        default=0,
    )
    return max(least, dimension, last_disagreement)


def terminal_issues(record):
    rows, label = record["rows"], record["end"]
    counts = [row["n"] for row in rows]
    totals = list(accumulate(counts, initial=record["n knots"]))
    issues = []
    if totals[-1] != record["knots"] or len(rows) > HORIZON or any(count <= 0 for count in counts):
        issues.append("run totals")
    if any(
        any(sum(row[reading].values()) != row["n"] for reading in READINGS)
        for row in rows
    ):
        issues.append("birth multiset totals")
    zero_fresh = [
        round_no
        for round_no, row in enumerate(rows, 1)
        if any(signature[2] == 0 for signature in row["sig0"])
    ]
    if label.startswith("closes"):
        if (
            record["knot law"] != "parity"
            or label != f"closes at round {len(rows) + 1}"
            or zero_fresh != [len(rows)]
            or not counts
            or counts[-1] != 1
        ):
            issues.append("closing round convention")
    elif zero_fresh:
        issues.append("zero fresh without closure")
    if label.startswith("stalls") and (rows or label != "stalls at round 1"):
        issues.append("stall convention")
    if label == "rounds" and len(rows) != HORIZON:
        issues.append("round limit")
    if label not in {"rounds", "bound"} and not label.startswith(("closes", "stalls")):
        issues.append("unknown ending")
    crossings = [round_no for round_no, total in enumerate(totals) if total > CAP]
    if (label == "bound" and crossings != [len(rows)]) or (label != "bound" and crossings):
        issues.append("knot cap")
    return issues


def coverage_key(record):
    end = record["end"]
    terminal = end if end.startswith("closes") else end.split(" at round ")[0]
    return terminal, record["kind"]


def misses_bound(kind, rows, reading, cut):
    return kind.startswith("dim ") and settling_round(rows, reading, int(kind[4:]), least=3) > cut


def candidates(records, late, size, pilot):
    randomizer = random.Random(SAMPLE_SEED + size)
    uniform_indices = {
        record["index"] for record in randomizer.sample(records, 6 if pilot else {5: 128, 6: 96}[size])
    }
    categories = defaultdict(list)
    for record in records:
        categories[coverage_key(record)].append(record)
    controls = set()
    for category, members in categories.items():
        if not pilot or category[0] == "bound":
            controls.add(max(members, key=lambda record: (record["knots"], record["index"]))["index"])
        if not pilot and category[0] == "bound":
            controls.add(min(members, key=lambda record: (record["knots"], record["index"]))["index"])
    if not pilot and size == 5:
        controls.update(record["index"] for record in records if record["M"] == 10)
    return uniform_indices, controls | (set(sorted(late)[:1]) if pilot else late)


def audit_archive(records, reference, size, pilot, other_law_misses):
    recorded_misses = {case[0] for case in reference["bound misses"]}
    selected, controls = candidates(records, recorded_misses | other_law_misses, size, pilot)
    replay_indices = selected | controls
    archive_slice = [record for record in records if record["index"] in replay_indices] if pilot else records
    totals = Counter()
    component_which_larger = Counter()
    departures = {reading: Counter() for reading in READINGS}
    misses = []
    mismatches = []
    controls_covered = Counter()
    cost = Counter()
    close_rounds = Counter()
    late_close_rounds = Counter()
    cap_totals = []
    exact_cap_ties = 0
    strict_cap_kind_changes = Counter()
    strict_cap_miss_changes = Counter()
    mismatch_count = 0
    witness = None
    replay_seconds = 0.0
    started = perf_counter()

    def check(condition, reason, index):
        nonlocal mismatch_count
        if not condition:
            mismatch_count += 1
            if len(mismatches) < 20:
                mismatches.append([index, reason])

    for record in archive_slice:
        index, stars, law = (record[field] for field in ("index", "stars", "knot law"))
        rows, end = record["rows"], record["end"]
        loose, met_sets = start_state(stars)
        check(loose == record["loose"], "loose counts", index)
        initial_largest = max(map(len, met_sets))
        first = births_in_round(loose, join_groups(met_sets), law)
        first_largest = max(first[1]) if first is not None else 0
        bound = max(initial_largest, first_largest)
        check(bound == record["M"], f"M was {bound}, archive gives {record['M']}", index)
        component_which_larger.update(
            ["start" if initial_largest > first_largest else "first birth" if first_largest > initial_largest else "equal"]
        )
        if first is None:
            check(not rows and end == "stalls at round 1", "first round stall", index)
        else:
            parents, fresh, _ = first
            _, computed_first = round_signatures(parents, fresh, start_signatures(stars))
            check(bool(rows) and computed_first == rows[0], "first round birth multisets", index)
        for issue in terminal_issues(record):
            check(False, issue, index)
        if end.startswith("closes"):
            close_rounds[len(rows)] += 1
            if index in other_law_misses:
                late_close_rounds[len(rows)] += 1
        if end == "bound":
            cap_totals.append(record["knots"])
        totals_after_births = accumulate((row["n"] for row in rows), initial=record["n knots"])
        exact_cap_ties += CAP in totals_after_births

        kind = classify(rows, end)
        totals[kind] += 1
        check(kind == record["kind"], f"classified {kind}, archive gives {record['kind']}", index)
        if end == "bound":
            strict_kind = classify(rows[:-1], end)
            if strict_kind != kind:
                strict_cap_kind_changes[f"{kind} -> {strict_kind}"] += 1
            for reading, margin in READINGS.items():
                cut = bound + margin
                if misses_bound(strict_kind, rows[:-1], reading, cut) != misses_bound(kind, rows, reading, cut):
                    strict_cap_miss_changes[reading] += 1
        if kind.startswith("dim "):
            dimension = int(kind[4:])
            for reading, margin in READINGS.items():
                unfloored = settling_round(rows, reading, dimension, least=1)
                settled = max(3, unfloored)
                if settled != unfloored:
                    departures[reading]["onsets delayed"] += 1
                if (settled > bound + margin) != (unfloored > bound + margin):
                    departures[reading]["verdicts changed"] += 1
                if settled > bound + margin:
                    misses.append([index, kind, reading, bound, settled, len(rows)])
                    excess = settled - (bound + margin)
                    if witness is None or excess > witness["excess"]:
                        witness = {
                            "index": index, "stars": stars, "M": bound,
                            "largest live-neighbour set": initial_largest,
                            "largest round-1 fresh count": first_largest,
                            "reading": reading, "settles": settled, "excess": excess,
                            "birth counts": [row["n"] for row in rows],
                        }

        if index in replay_indices:
            tick = perf_counter()
            computed = grow(stars, law)
            replay_seconds += perf_counter() - tick
            cost["starts"] += 1
            cost["saved rounds"] += len(rows)
            cost["saved births"] += sum(row["n"] for row in rows)
            controls_covered[" / ".join(coverage_key(record))] += 1
            check(computed["end"] == end, f"end was {computed['end']}, archive gives {end}", index)
            check(computed["knots"] == record["knots"], "full replay knot total", index)
            check(len(computed["rows"]) == len(rows), "full replay round count", index)
            for round_no, (new, old) in enumerate(zip(computed["rows"], rows), 1):
                check(new == old, f"full replay birth multisets at round {round_no}", index)

    if not pilot:
        dimension_counts = {kind: count for kind, count in totals.items() if kind.startswith("dim ")}
        check(dimension_counts == reference["kinds"], "dimension totals", None)
        check(misses == reference["bound misses"], "bound misses, in archive order", None)
    return {
        "archived starts audited": len(archive_slice),
        "kinds": totals,
        "M larger input": component_which_larger,
        "bound misses": misses,
        "largest excess example": witness,
        "effect of floor at round 3": departures,
        "closing birth round histogram": close_rounds,
        "closing birth round for misses in the other law": late_close_rounds,
        "cap overshoot": {
            "runs": len(cap_totals),
            "runs reaching exactly the cap": exact_cap_ties,
            "least knot total in passing round": min(cap_totals, default=None),
            "most knots in passing round": max(cap_totals, default=None),
            "kind changes if passing round is omitted": strict_cap_kind_changes,
            "miss verdict changes if passing round is omitted": strict_cap_miss_changes,
        },
        "full replay": cost,
        "uniform replay start indices": sorted(selected),
        "full replay additional controls by start index": sorted(controls - selected),
        "full replay categories": controls_covered,
        "mismatch count": mismatch_count,
        "first mismatches": mismatches,
        "wall seconds": round(perf_counter() - started, 3),
        "full replay wall seconds": round(replay_seconds, 3),
    }


def check_groups():
    """Compare the clique search with a direct subset scan on small met families."""
    randomizer = random.Random(871)
    for size in range(3, 8):
        for _ in range(35):
            members = range(size)
            mets = [
                {member for member in members if randomizer.randrange(2)}
                for _ in members
            ]
            pairs = {pair for pair in combinations(members, 2) if any(set(pair) <= met for met in mets)}
            valid = [
                set(group)
                for count in range(3, size + 1)
                for group in combinations(members, count)
                if all(pair in pairs for pair in combinations(group, 2))
                and not any(set(group) <= met for met in mets)
            ]
            groups = [tuple(sorted(group)) for group in valid if not any(group < other for other in valid)]
            covered = {pair for group in groups for pair in combinations(group, 2)}
            assert join_groups(mets) == sorted(groups + list(pairs - covered))
    return 175


def run(pilot):
    results = {"direct small group checks": check_groups(), "sample seed base": SAMPLE_SEED, "runs": {}}
    for size in (5, 6):
        law_order = {}
        for file_law in ("nae", "par"):
            dataset = f"g{size}_{file_law}"
            records = list(read_archive(STUDY / f"grown_{dataset}.jsonl.gz"))
            law_order[file_law] = [
                (record["index"], record["graph"], record["loose"], record["stars"]) for record in records
            ]
            own_reference = json.loads((STUDY / f"test_{dataset}.json").read_text(encoding="utf-8"))
            other_file_law = "par" if file_law == "nae" else "nae"
            other_reference = json.loads((STUDY / f"test_g{size}_{other_file_law}.json").read_text(encoding="utf-8"))
            summary = audit_archive(
                records, own_reference, size, pilot, {case[0] for case in other_reference["bound misses"]}
            )
            results["runs"][dataset] = summary
            print(
                dataset, "replayed", summary["full replay"]["starts"],
                "of", len(records), "starts with", summary["mismatch count"], "mismatches",
                flush=True,
            )
            del records
        all_indices = [record[0] for record in law_order["nae"]]
        chosen = list(range(3157)) if size == 5 else random.Random(20261126).sample(range(82656), 1000)
        results[f"{size}-knot archive identities agree between laws"] = law_order["nae"] == law_order["par"]
        results[f"{size}-knot archive indices in declared order"] = chosen == all_indices
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="time a reduced replay with the same rules and limits")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    tick = perf_counter()
    result = run(args.pilot)
    result["pilot"] = args.pilot
    result["wall seconds"] = round(perf_counter() - tick, 3)
    result["peak resident KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if any(summary["mismatch count"] for summary in result["runs"].values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
