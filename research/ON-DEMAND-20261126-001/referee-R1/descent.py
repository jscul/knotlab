"""Recount recorded birth shares and replay readings that retain parent names.

The replay uses the independent roster and sample reconstruction in this
folder. It matches names of start knots across regions and counts repeated
recursive parent names with multiplicity. A second reading retains the fresh
count at each birth in the recursive name. Neither name identifies an occurrence
or a shared distinction. The two original kind readings are implied by their
joint reading, which contains both the birth kind and the immediate parents'
kinds.
"""

import argparse
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
import json
from pathlib import Path
import resource
from statistics import median
from time import perf_counter


STUDY = Path(__file__).resolve().parent.parent
POPULATIONS = ("tree40", "treeplus25", "census6")
PROVISIONAL = "births of the region not in the full growth, of all the region's births, at round t"
NEEDED = "births needed, of all births, through round t"
H1 = "H1 within t + 1 steps agrees"
H1_SHORT = "within t steps agrees"
CAP = 3_000


def records(population):
    with (STUDY / f"results_{population}.jsonl").open() as source:
        return {row["index"]: row for row in map(json.loads, source)}


def shares(counts):
    fractions = sorted(Fraction(n, d) for n, d in counts if d)
    total = [sum(values) for values in zip(*counts, strict=True)]
    return {
        "readers": len(fractions),
        "count_numerator_and_denominator": total,
        "upper_median_per_reader": float(fractions[len(fractions) // 2]),
        "median_per_reader": float(median(fractions)),
        "least_per_reader": float(fractions[0]),
        "pooled_share": float(Fraction(*total)),
        "readers_with_all_births_counted": fractions.count(Fraction(1)),
    }


def archive():
    summary = {}
    for population in POPULATIONS:
        summary[population] = {}
        panel = records(population)
        for law in ("nae", "parity"):
            readers = []
            provisional = []
            starts_with_excess = []
            proper_last_regions = 0
            for index, record in panel.items():
                row = record.get("laws", {}).get(law, {})
                if not row.get(NEEDED):
                    continue
                last = max(row[NEEDED], key=int)
                readers.append(row[NEEDED][last])
                proper_last_regions += (record["live in the reader piece"] < record["live"]
                                        or record["eccentricity"] > int(last) + 1)
                counts = row[PROVISIONAL]
                provisional.extend(counts.values())
                if any(a for a, _ in counts.values()):
                    starts_with_excess.append(index)
            summary[population][law] = {
                "last_round_ancestry_counts": shares(readers),
                "proper_regions_at_last_compared_round": proper_last_regions,
                "last_round_provisional_counts_per_comparison_pooled": [
                    sum(values) for values in zip(*provisional, strict=True)
                ],
                "comparisons_with_named_excess": sum(a != 0 for a, _ in provisional),
                "starts_with_named_excess": starts_with_excess,
            }
    return summary


@dataclass(slots=True)
class Reading:
    names: Counter = field(default_factory=Counter)
    fresh_names: Counter = field(default_factory=Counter)
    reader_names: Counter = field(default_factory=Counter)
    reader_fresh_names: Counter = field(default_factory=Counter)
    kinds: Counter = field(default_factory=Counter)
    reader_kinds: Counter = field(default_factory=Counter)
    size: int = 0
    reader_size: int = 0


def readings(growth, reader, names, fresh_names, collision=None):
    """Intern parent-name tuples to compare them without unrolling repeats."""
    old_names = [-k - 1 for k in growth.start]
    old_fresh = old_names
    results = []
    for number, row in enumerate(growth.rows, 1):
        r = Reading(size=len(row))
        new_names = []
        new_fresh = []
        for b in row:
            name = tuple(sorted(old_names[parent] for parent in b.parents))
            name = names.setdefault(name, len(names))
            fresh = (b.fresh, tuple(sorted(old_fresh[parent] for parent in b.parents)))
            fresh = fresh_names.setdefault(fresh, len(fresh_names))
            new_names.append(name)
            new_fresh.append(fresh)
            r.names[name] += 1
            r.fresh_names[fresh] += 1
            r.kinds[b.with_parents] += 1
            if (b.ancestry >> reader) & 1:
                r.reader_names[name] += 1
                r.reader_fresh_names[fresh] += 1
                r.reader_kinds[b.with_parents] += 1
                r.reader_size += 1
        if collision is not None and not collision:
            duplicate = next((key for key, count in r.reader_fresh_names.items() if count > 1), None)
            if duplicate is not None:
                positions = [i for i, key in enumerate(new_fresh) if key == duplicate]
                collision.update({"round": number, "birth_positions": positions,
                                  "parent_positions": [row[i].parents for i in positions],
                                  "fresh_counts": [row[i].fresh for i in positions]})
        old_names = new_names
        old_fresh = new_fresh
        results.append(r)
    return results


def closure_sizes(growth, reader, horizon):
    rows = growth.rows[:horizon]
    direct, covered, total = 0, 0, 0
    later = set()
    for row in reversed(rows):
        descendants = {i for i, birth in enumerate(row) if (birth.ancestry >> reader) & 1}
        selected = descendants | later
        direct += len(descendants)
        covered += len(selected)
        total += len(row)
        later = {parent for i in selected for parent in row[i].parents}
    return direct, covered, total


def reading_at(rows, index):
    return rows[index] if index < len(rows) else Reading()


def compare(full, region, horizon):
    """Compare through the requested round, allowing an empty tail after closure."""
    fields = ("reader_size", "reader_kinds", "reader_names", "reader_fresh_names", "size", "kinds", "names", "fresh_names")
    pairs = [(reading_at(full, i), reading_at(region, i)) for i in range(horizon)]
    return {
        field: all(getattr(a, field) == getattr(b, field) for a, b in pairs)
        for field in fields
    }


def tally_comparison(counts, compared, context):
    counts[f"{context} comparisons"] += 1
    for key, equal in compared.items():
        counts[f"{context} equal through horizon by {key}"] += equal
    counts[f"{context} equal reader kinds but unequal reader parent names"] += (
        compared["reader_kinds"] and not compared["reader_names"]
    )
    counts[f"{context} equal reader parent names but unequal reader fresh names"] += (
        compared["reader_names"] and not compared["reader_fresh_names"]
    )
    counts[f"{context} equal reader totals but unequal reader kinds"] += (
        compared["reader_size"] and not compared["reader_kinds"]
    )


def tally_excess(counts, full, region, horizon):
    """Names cannot mix readers and nonreaders, since their leaves fix ancestry."""
    f, r = reading_at(full, horizon - 1), reading_at(region, horizon - 1)
    for label in ("names", "fresh_names", "reader_names", "reader_fresh_names", "kinds", "reader_kinds"):
        excess = sum((getattr(r, label) - getattr(f, label)).values())
        counts[f"H1 last round excess by {label}"] += excess
        counts[f"H1 horizons with last round excess by {label}"] += excess != 0
    counts["H1 last round region births"] += r.size
    counts["H1 last round region reader births"] += r.reader_size
    counts["H1 last round region births with repeated name beyond its first occurrence"] += r.size - len(r.names)
    counts["H1 last round region reader births with repeated name beyond its first occurrence"] += r.reader_size - len(r.reader_names)
    return sum((r.names - f.names).values()), r.size


def tally_admission(counts, full, before, halfway, horizon):
    """Track unmatched multiplicities while the compared horizon stays fixed."""
    counts["strict halfway admissions"] += 1
    per_round = []
    for field in ("names", "fresh_names", "reader_names", "reader_fresh_names"):
        has_extra_before = False
        changed = False
        for i in range(horizon):
            a, b, f = (getattr(reading_at(rows, i), field) for rows in (before, halfway, full))
            first, middle = a - f, b - f
            kept = sum((first & middle).values())
            removed = sum(first.values()) - kept
            emerged = sum(middle.values()) - kept
            if field == "names":
                per_round.append((kept + removed, kept, removed, emerged))
            counts[f"admission {field} excess before"] += kept + removed
            counts[f"admission {field} excess retained at halfway"] += kept
            counts[f"admission {field} excess removed by halfway"] += removed
            counts[f"admission {field} excess gained at halfway"] += emerged
            has_extra_before |= bool(first)
            changed |= bool(removed or emerged)
        counts[f"admissions with {field} excess before"] += has_extra_before
        counts[f"admissions changing {field} excess at halfway"] += changed
    return per_round


def replay_case(case, roster, archived, law, counts, examples):
    from growth import grow

    expected = archived["laws"][law]
    full = grow(roster, case.horizon, law, CAP)
    if expected["end"] != full.end:
        raise ValueError(f"full end differs, index {case.index}, {law}")
    if full.end == "stall":
        counts["stalled"] += 1
        return None
    n = len(full.rows) if full.end == "cap" else case.horizon
    if expected["rounds read"] != n:
        raise ValueError(f"full horizon differs, index {case.index}, {law}")
    counts["starts checked"] += 1

    names, fresh_names = {}, {}
    collision = {} if "repeated descendant name including fresh counts" not in examples else None
    full_read = readings(full, case.reader, names, fresh_names, collision)
    if collision:
        examples["repeated descendant name including fresh counts"] = {
            "index": case.index, "start_holdings": case.stars, "reader": case.reader, **collision,
        }

    region_cap = CAP if archived["population"] == "treeplus25" else None
    cache = {}

    def inside(region, t):
        if region == case.live:
            return full_read[:t]
        key = (region, t)
        if key not in cache:
            growth = grow(roster.restrict(region), t, law, region_cap)
            read = None if growth.end == "cap" else readings(growth, case.reader, names, fresh_names)
            cache[key] = read
        return cache[key]

    def check(region, t, context):
        local = inside(region, t)
        if local is None:
            counts[f"{context} unread at cap"] += 1
            return None, None
        compared = compare(full_read, local, t)
        tally_comparison(counts, compared, context)
        distinctions = {
            "differs by all birth totals": not compared["size"],
            "differs by reader parent names": not compared["reader_names"],
            "differs by reader fresh names": not compared["reader_fresh_names"],
            "preserves reader kind counts but differs by reader names": (
                compared["reader_kinds"] and not compared["reader_names"]
            ),
            "preserves reader names but differs when they record fresh counts": (
                compared["reader_names"] and not compared["reader_fresh_names"]
            ),
            "preserves reader totals but differs by reader kind": (
                compared["reader_size"] and not compared["reader_kinds"]
            ),
        }
        for reason, differs in distinctions.items():
            label = f"{context} {reason}"
            if differs and label not in examples:
                fields = ("reader_names", "reader_fresh_names", "reader_kinds")
                first_mismatches = {
                    field: next((i + 1 for i in range(t)
                                 if getattr(reading_at(full_read, i), field) != getattr(reading_at(local, i), field)), None)
                    for field in fields
                }
                examples[label] = {
                    "index": case.index, "start_holdings": case.stars, "reader": case.reader,
                    "round": t, "region": sorted(region), "agreements": compared,
                    "first_mismatches": first_mismatches,
                    "full_birth_counts": [reading_at(full_read, i).size for i in range(t)],
                    "region_birth_counts": [reading_at(local, i).size for i in range(t)],
                    "full_reader_birth_counts": [reading_at(full_read, i).reader_size for i in range(t)],
                    "region_reader_birth_counts": [reading_at(local, i).reader_size for i in range(t)],
                }
        return local, compared

    for t in range(1, n + 1):
        local, compared = check(case.reach(t + 1), t, "H1")
        _, compared_short = check(case.reach(t), t, "t steps")
        for outcome, archive_key in ((compared, H1), (compared_short, H1_SHORT)):
            actual = outcome["reader_kinds"] if outcome is not None else None
            if actual != expected[archive_key].get(str(t)):
                raise ValueError(f"kind comparison differs from archive, index {case.index}, {law}, {t}, {archive_key}")
        if local is not None:
            provisional = tally_excess(counts, full_read, local, t)
            if list(provisional) != expected[PROVISIONAL][str(t)]:
                raise ValueError(f"provisional count differs from archive, index {case.index}, {law}, {t}")
            direct, covered, total = closure_sizes(full, case.reader, t)
            if [covered, total] != expected[NEEDED][str(t)]:
                raise ValueError(f"ancestry count differs from archive, index {case.index}, {law}, {t}")
            counts["archive provisional and ancestry rows matched"] += 1

    h2 = []
    for t, extra in case.h2_draws:
        if t <= n:
            _, compared = check(case.reach(t + 1) | extra, t, "H2 random superset")
            if compared is not None:
                h2.append([t, len(extra), compared["reader_kinds"]])
    t = case.h2_draws[0][0]
    if t <= n:
        initial = case.reach(t + 1)
        halfway = initial | frozenset(case.admission_order[:len(case.admission_order) // 2])
        before, a = check(initial, t, "H2 admission snapshot")
        middle, b = check(halfway, t, "H2 admission snapshot")
        _, c = check(case.live, t, "H2 admission snapshot")
        h2.append([t, "admitted in three steps", [x["reader_kinds"] for x in (a, b, c) if x is not None]])
        if before is not None and middle is not None and halfway != initial:
            excess = tally_admission(counts, full_read, before, middle, t)
            if any(gained for _, _, _, gained in excess) and "admission adds unmatched parent names" not in examples:
                examples["admission adds unmatched parent names"] = {
                    "index": case.index, "start_holdings": case.stars, "reader": case.reader,
                    "horizon": t, "initial_region": sorted(initial), "halfway_region": sorted(halfway),
                    "each_round_excess_before_then_count_retained_removed_gained_at_halfway": excess,
                }
    if h2 != expected["H2"]:
        raise ValueError(f"H2 comparison differs from archive, index {case.index}, {law}")

    direct, covered, total = closure_sizes(full, case.reader, n)
    counts["last horizon direct reader births"] += direct
    counts["last horizon births including parent ancestry"] += covered
    counts["last horizon all full births"] += total
    return (case.index, direct, covered, total)


def replay(populations, selections, laws):
    from growth import Roster
    from sampling import draws

    output = {}
    for population in populations:
        if selections and population not in selections:
            continue
        panel = records(population)
        output[population] = {law: {"counts": Counter(), "examples": {}, "last_horizon_rows": []} for law in laws}
        pending = set(selections[population]) if selections else set(panel)
        for case in draws(population):
            if case.index not in pending:
                continue
            pending.remove(case.index)
            row = panel[case.index]
            if row["reader"] != case.reader:
                raise ValueError(f"reader differs from archive, {population}, index {case.index}")
            if "not read" not in row:
                roster = Roster.from_holdings(case.stars)
                if roster.loose.keys() != case.live or roster.steps_from(case.reader) != case.steps:
                    raise ValueError(f"two maps disagree, {population}, index {case.index}")
                for law in laws:
                    result = output[population][law]
                    sizes = replay_case(case, roster, row, law, result["counts"], result["examples"])
                    if sizes is not None:
                        result["last_horizon_rows"].append(sizes)
            if not pending:
                break
        if pending:
            raise ValueError(f"sample reconstruction omits {population} indices {sorted(pending)}")
        for law in laws:
            result = output[population][law]
            rows = result["last_horizon_rows"]
            if rows:
                result["direct_reader_shares"] = shares([(direct, total) for _, direct, _, total in rows])
                result["reader_and_ancestor_shares"] = shares([(covered, total) for _, _, covered, total in rows])
        print(population, flush=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--archive", action="store_true")
    parser.add_argument("--select", action="append", default=[], metavar="POPULATION:INDEX")
    parser.add_argument("--populations", nargs="+", choices=POPULATIONS, default=POPULATIONS)
    parser.add_argument("--laws", nargs="+", choices=("nae", "parity"), default=("nae", "parity"))
    args = parser.parse_args()
    selected = {}
    for item in args.select:
        population, index = item.split(":")
        selected.setdefault(population, []).append(int(index))
    started = perf_counter()
    evidence = archive() if args.archive else replay(args.populations, selected, args.laws)
    result = {
        "scope": "recorded archive only" if args.archive else "independent replay against recorded archive",
        "selected_indices": selected,
        "populations_requested": args.populations,
        "laws_requested": args.laws,
        "evidence": evidence,
        "elapsed_seconds": round(perf_counter() - started, 3),
        "maximum_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
