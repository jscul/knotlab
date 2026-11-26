"""Regrow a stratified and diagnostic sample of run 1 from the frozen starts."""

import argparse
from collections import Counter, deque
import gzip
from hashlib import sha256
import json
from pathlib import Path
from random import Random

from birth_recount import ARTIFACTS, STARTS, LAWS, category, parity_passes, read_sequence
from regrow_engine import Growth


def counts_from(growth, sources, *, parents=False):
    if parents:
        meetings = [set(row) for row in growth.parents]
        for knot, row in enumerate(growth.parents):
            for parent in row:
                meetings[parent].add(knot)
    else:
        meetings = growth.meeting
    pending = deque(sources)
    steps = dict.fromkeys(sources, 0)
    while pending:
        knot = pending.popleft()
        for other in meetings[knot]:
            if other not in steps:
                steps[other] = steps[knot] + 1
                pending.append(other)
    return steps


def curve(steps, limit):
    levels = Counter(steps.values())
    now = 0
    result = []
    for t in range(limit + 1):
        now += levels[t]
        result.append(now)
    return result


def member_parts(growth):
    unseen = set(growth.members)
    neighbors = growth.roster().neighbors
    part_ids = {}
    sizes = []
    while unseen:
        first = unseen.pop()
        seen = [first]
        for member in seen:
            part_ids[member] = len(sizes)
            found = unseen.intersection(neighbors[member])
            unseen.difference_update(found)
            seen.extend(found)
        sizes.append(len(seen))
    return part_ids, sorted(sizes, reverse=True)


def sample(choices, start, law, label, knot_law):
    generator = Random(int.from_bytes(
        sha256(f"KWR|{start}|{law}|{knot_law}|{label}".encode()).digest(), "big"
    ))
    choices = sorted(choices)
    return generator.sample(choices, 8) if len(choices) > 8 else choices


def sample_classes(growth, index, law, n_start, start_steps, knot_law):
    result = {"a": list(range(n_start)), "b": [], "c": []}
    if not growth.members:
        return None, result
    minimum = min(start_steps[u] for u in growth.members)
    made = [u for u in range(n_start, len(growth.places)) if u not in growth.members and u in start_steps]
    result["b"] = sample([u for u in made if 4 * start_steps[u] <= minimum], index, law, "b", knot_law)
    result["c"] = sample(
        [u for u in made if minimum // 2 - 2 <= start_steps[u] <= minimum // 2],
        index, law, "c", knot_law,
    )
    return minimum, result


def replay(record, stars, knot_law, *, short_rounds, full_knots, peak_knots):
    law = record["law"]
    growth = Growth(stars, law=law, knot_law=knot_law)
    round_limit = record["rounds_done"] if record["knots"] <= full_knots else min(
        short_rounds, record["rounds_done"]
    )
    close = record["parity_closing_round"] if knot_law == "parity" else None
    if close is not None:
        round_limit = min(round_limit, close)
    reports = Counter()
    problems = []
    part_ids, sizes = member_parts(growth)
    if (len(growth.members), len(sizes), sizes[:8]) != (
        record["members_per_round"][0], record["parts_per_round"][0], record["part_sizes_per_round"][0]
    ):
        problems.append("initial roster")
    done = 0
    for t in range(1, round_limit + 1):
        first = len(growth.places)
        b = record["births"][t - 1]
        if first + b > peak_knots:
            break
        if growth.status != "running":
            problems.append(["early stop", t, growth.status])
            break
        births = growth.step()
        done = t
        reports["rounds compared"] += 1
        if births != b:
            problems.append(["births", t, births, b])
            break
        if t == close:
            reports["parity closures compared"] += 1
            if growth.status != "stopped" or growth.members or growth.demand[-1] is None:
                problems.append(["parity closure", t, growth.status])
            last = len(growth.places) - 1
            if len(growth.places[last]) != len(growth.parents[last]):
                problems.append(["parity closing birth has a fresh distinction", t])
            break
        counts = Counter()
        for parents in growth.parents[first:]:
            ids = {part_ids[knot] for knot in parents}
            if len(ids) != 1:
                problems.append(["parents span roster parts", t, list(parents)])
            counts.update(ids)
        saved = record["births_by_part"][t - 1]
        if sorted(counts.values(), reverse=True)[:8] != saved:
            problems.append(["births by prior part", t])
        part_ids, sizes = member_parts(growth)
        if (len(growth.members), len(sizes), sizes[:8]) != (
            record["members_per_round"][t], record["parts_per_round"][t], record["part_sizes_per_round"][t]
        ):
            problems.append(["roster", t, len(sizes), record["parts_per_round"][t], len(growth.members),
                             record["members_per_round"][t]])
            break
        if knot_law == "nae" and growth.fillers and growth.barred:
            reports["rounds with barred fillers"] += 1
        if births and any(knot < first for knot in growth.members):
            reports["rounds retaining an old member"] += 1
    if knot_law == "nae" and done == record["rounds_done"]:
        reports["complete recorded runs"] += 1
        expected_status = record["ended"] or "running"
        if growth.status != expected_status:
            problems.append(["recorded termination", growth.status, expected_status])
        if growth.status == "running" and done < 100 and record["stop"] not in ("guard", "knots"):
            problems.append(["unknown external stop", record["stop"]])
    if knot_law == "nae" and done == record["rounds_done"] and not problems:
        n_start = len(stars)
        start_steps = counts_from(growth, range(n_start))
        min_s, classes = sample_classes(growth, record["start"], law, n_start, start_steps, knot_law)
        if classes != record["classes"] or min_s != record["s_min"]:
            problems.append(["sampled classes", min_s, record["s_min"],
                             {label: [classes[label], record["classes"][label]] for label in classes
                              if classes[label] != record["classes"][label]}])
        for knot in sorted(set().union(*classes.values())):
            steps = counts_from(growth, [knot])
            limit = max(steps.values()) if record["ended"] or min_s is None else min_s - start_steps[knot]
            holders = curve(steps, limit)
            if str(knot) not in record["H"]:
                continue
            reports["holder curves compared"] += 1
            if holders != record["H"][str(knot)]:
                problems.append(["holder curve", knot])
            parent = curve(counts_from(growth, [knot], parents=True), limit)
            reports["parent changes compared"] += 1
            if (parent != holders) != (knot in record["parent_steps_differ"]):
                problems.append(["parent-step change", knot])
            if parent != holders:
                verdict, _ = read_sequence(tuple(parent), 0, record["ended"] is not None)
                label = category(verdict)
                saved = record["parent_steps_reading"].get(str(knot), "").split()
                if not saved or (label != saved[0] and not (label.startswith("LINREC") and saved[0] == "LINREC")):
                    problems.append(["parent-step reading", knot, label, saved])
    return reports, problems


def select():
    census = json.loads((STARTS / "census_starts.json").read_text())
    order = json.loads((STARTS / "five_knot_order.json").read_text())["order"]
    fixed = {
        *[i for i, start in enumerate(census) if start["n"] == 3][:3],
        *[i for i, start in enumerate(census) if start["n"] == 4][:3],
        *order[:3],
    }
    candidates = {}
    all_fixed = {}
    turning = {}
    with gzip.open(ARTIFACTS / "run1.jsonl.gz", "rt") as stream:
        for row in map(json.loads, stream):
            law, i, item = row["law"], row["index"], row["item"]
            if i in fixed:
                all_fixed[item] = row
            if row["parity_closing_round"] is not None and parity_passes(census[i]["stars"]):
                key = (law, "eligible parity closure")
                if key not in candidates or row["parity_closing_round"] < candidates[key]["parity_closing_round"]:
                    candidates[key] = row
            if row["ended"] or row["stop"]:
                key = (law, row["ended"] or row["stop"])
                if key not in candidates or row["knots"] < candidates[key]["knots"]:
                    candidates[key] = row
            if law in ("L6", "L11") and row["births_reading"].get("j") in (2, 3):
                key = (law, f"first degree {row['births_reading']['j']}")
                if key not in candidates or item < candidates[key]["item"]:
                    candidates[key] = row
            if law in ("L6", "L9"):
                reading, _ = read_sequence(tuple(row["births"]), 1, row["ended"] is not None)
                kind = category(reading)
                if (law, kind) in (("L6", "POWER(1)"), ("L9", "POWER(0)")):
                    turning.setdefault(i, {})[law] = row
    first_change = min(i for i, rows in turning.items() if len(rows) == 2)
    for law, row in turning[first_change].items():
        candidates[law, "same start degree change"] = row
    for (law, reason), row in candidates.items():
        roles = all_fixed.setdefault(row["item"], row).setdefault("selection", [])
        roles.append(reason)
    rows = sorted(all_fixed.values(), key=lambda row: (
        not bool(row.get("selection")), LAWS.index(row["law"]), row["item"]
    ))
    return census, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--short-rounds", type=int, default=14)
    parser.add_argument("--full-knots", type=int, default=2200)
    parser.add_argument("--peak-knots", type=int, default=6500)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    census, cases = select()
    counts = {"nae": Counter(), "parity": Counter()}
    notes = []
    for row in cases[:args.limit]:
        stars = census[row["index"]]["stars"]
        for knot_law, tally in counts.items():
            if knot_law == "parity" and not parity_passes(stars):
                tally["starts failing K2 at round 0"] += 1
                continue
            tally["runs"] += 1
            report, problems = replay(
                row, stars, knot_law, short_rounds=args.short_rounds,
                full_knots=args.full_knots, peak_knots=args.peak_knots,
            )
            tally.update(report)
            notes.append({
                "census_start": row["start"],
                "initial_knots": len(stars),
                "law": row["law"],
                "knot_law": knot_law,
                "selection": row.get("selection", ["first three in its census stratum"]),
                "recorded_rounds": row["rounds_done"],
                "recorded_parity_close": row["parity_closing_round"],
                "rounds_checked": report["rounds compared"],
                "issues": problems,
            })
    result = json.dumps({
        "short_round_limit": args.short_rounds,
        "full_run_if_total_knots_at_most": args.full_knots,
        "stop_before_logged_knots_exceed": args.peak_knots,
        "aggregate": counts,
        "checks": notes,
    }, indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
