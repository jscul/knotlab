"""Regrow the post hoc probe and the four round-66 rosters.

Recorded outputs supply cases, stages, and the sample to compare. Growth,
one-step relations, and the counts from a member are computed afresh.
"""

import argparse
import gzip
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from time import monotonic

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from regrow_engine import Growth, connected_parts


HERE = Path(__file__).resolve().parent
CHECKS = HERE.parent / "checks"
TICKET = HERE.parent.with_name(HERE.parent.name + "A")
ARTIFACTS = HERE.parents[2] / "artifacts" / TICKET.name
FAMILIES = {
    "six": (19, 164, 172, 214, 1350, 2086, 2216, 2772, 3075),
    "twelve": (177, 218, 3195, 3288),
    "thirteen": (178, 179, 219, 1382, 2218, 2231, 2694, 3077),
    "twenty-two": (1964, 2236),
}
FAMILY_OF = {
    f"census:{index}": name for name, starts in FAMILIES.items() for index in starts
}
SIX_LAWS = {"L0", "L1", "L6", "L7", "L9", "L11"}
SURVIVES = {
    "six": SIX_LAWS,
    "twelve": {"L0", "L9", "L11"},
    "thirteen": {"L0", "L9"},
    "twenty-two": {"L0", "L9"},
}


def records(path):
    with gzip.open(path, "rt") as lines:
        yield from map(json.loads, lines)


def stars_of(census, start):
    return census[int(start.split(":")[1])]["stars"]


def reach_counts(neighbors, sources):
    labels = sorted(neighbors)
    index = {label: i for i, label in enumerate(labels)}
    cols = []
    indptr = [0]
    for v in labels:
        cols.extend(index[w] for w in sorted(neighbors[v]))
        indptr.append(len(cols))
    graph = csr_matrix((np.ones(len(cols)), cols, indptr), shape=(len(labels), len(labels)))
    for begin in range(0, len(sources), 128):
        batch = sources[begin:begin + 128]
        paths = dijkstra(graph, indices=[index[v] for v in batch], unweighted=True)
        for v, distances in zip(batch, paths, strict=True):
            finite = distances[np.isfinite(distances)].astype(np.intp)
            counts = np.bincount(finite).cumsum().tolist()
            yield v, counts


def greatest_counts(curves):
    best = [0] * max(map(len, curves))
    for curve in curves:
        for r, count in enumerate(curve):
            best[r] = max(best[r], count)
        for r in range(len(curve), len(best)):
            best[r] = max(best[r], curve[-1])
    return best


def polynomial_count(family, r):
    if family == "six":
        return 3 * r * r + 3 * r + 1
    if family == "twelve":
        return (2 * r + 1) * (5 * r * r + 5 * r + 3) // 3
    if family == "thirteen":
        return 12 * r * r + 2 if r else 1
    if r < 2:
        return (1, 23)[r]
    return 48 * r * r - 48 * r + 24


def roster_size(family, t):
    if family == "six":
        return t * (t + 1) // 2 + 3
    if family == "twelve":
        return math.comb(t + 2, 3) + 4
    if family == "thirteen":
        return 2 * t * t - 2 * t + 4
    return 8 * t * t - 24 * t + 27


def prefix_end(curve, expected, first=0):
    for r in range(first, len(curve)):
        if curve[r] != expected(r):
            return r - 1
    return len(curve) - 1


def difference_prefix(curve, degree):
    differences = curve
    for _ in range(degree):
        differences = [b - a for a, b in zip(differences, differences[1:])]
    if not differences or differences[0] <= 0:
        return None, None
    end = prefix_end(differences, lambda _: differences[0]) + degree
    return end, differences[0]


def check(got, expected, mismatches, field):
    if got != expected:
        mismatches[field] = {"got": got, "record": expected}


def compare_profile(curves, stage, mismatches):
    sources = sorted(curves)
    n = len(sources)
    # The recorded even sample uses every ceil(n/2500)-th name.
    sample = sources[::math.ceil(n / 2500)]
    check(len(sample), stage["sources"], mismatches, "recorded source count")
    degree_counts = Counter(str(curves[v][1] - 1 if len(curves[v]) > 1 else 0) for v in sample)
    check(dict(degree_counts), stage["neighbours within one step, by count of members"],
          mismatches, "recorded source degree histogram")
    ecc = [len(curves[v]) - 1 for v in sample]
    check([min(ecc), max(ecc)], stage["greatest steps, least and greatest over sources"],
          mismatches, "recorded source greatest steps")
    best = greatest_counts([curves[v] for v in sample])
    expected = stage["greatest count at each r (first 30)"]
    check(best[:len(expected)], expected, mismatches, "recorded source greatest counts")
    for degree in (1, 2, 3):
        reading = stage.get(f"degree {degree}")
        if reading is None:
            continue
        prefixes = {v: difference_prefix(curves[v], degree) for v in sample}
        observed = [r for r, _ in prefixes.values() if r is not None]
        witness = reading["member"]
        if witness not in prefixes:
            mismatches[f"degree {degree} recorded source"] = witness
            continue
        expected_end = reading["longest exact prefix r"]
        check(max(observed, default=None), expected_end, mismatches, f"degree {degree} prefix")
        check(list(prefixes[witness]), [expected_end, reading["its top difference"]],
              mismatches, f"degree {degree} recorded source prefix")
        expected_curve = reading["its counts"]
        check(curves[witness][:len(expected_curve)], expected_curve,
              mismatches, f"degree {degree} recorded source counts")
        histogram = Counter(str(d) for r, d in prefixes.values() if r is not None and r >= degree + 4)
        check(dict(histogram), reading[f"sources with an exact prefix through r >= {degree + 4}, by top difference"],
              mismatches, f"degree {degree} prefix histogram")
    return best


def check_probe_stage(growth, recorded, family, law):
    roster = growth.roster()
    neighbors = roster.neighbors
    parts = sorted((sorted(p) for p in connected_parts(neighbors)), key=lambda p: (-len(p), p[0]))
    size = len(neighbors)
    t = growth.round
    mismatch = {}
    check(len(growth.places), recorded["knots"], mismatch, "knots")
    check(size, recorded["members"], mismatch, "members")
    check(len(parts), recorded["parts"], mismatch, "parts")
    check([len(p) for p in parts[:5]], recorded["part sizes (largest 5)"], mismatch, "largest parts")
    one_part_expected = law in SURVIVES[family]
    check(len(parts) == 1, one_part_expected, mismatch, "one part as reported")
    result = {"round": t, "knots": len(growth.places), "members": size}
    result["part_sizes"] = [len(p) for p in parts]
    if one_part_expected or "sources" in recorded:
        source_labels = parts[0]
        curves = dict(reach_counts(neighbors, source_labels))
        if "sources" in recorded:
            sampled_best = compare_profile(curves, recorded, mismatch)
            result["recorded_sources"] = recorded["sources"]
            result["recorded_sources_greatest_counts_differ"] = (
                sampled_best != greatest_counts(list(curves.values()))
            )
        else:
            sampled_best = None
    if one_part_expected:
        all_best = greatest_counts(list(curves.values()))
        t_size = roster_size(family, t)
        check(size, t_size, mismatch, "family roster size")
        max_degree = {"six": 6, "twelve": 12, "thirteen": 13, "twenty-two": 22}[family]
        check(all_best[1] - 1, max_degree, mismatch, "family maximum number of neighbors")
        start = {"thirteen": 1, "twenty-two": 2}.get(family, 0)
        end = prefix_end(all_best, lambda r: polynomial_count(family, r), start)
        result["exact_formula_from"] = start
        result["exact_formula_through"] = end
        result["greatest_counts_first_30"] = all_best[:30]
        result["strictly_below_formula_after"] = all(
            count < polynomial_count(family, r)
            for r, count in enumerate(all_best) if r > end
        )
        if sampled_best is not None:
            result["recorded_sources_exact_through"] = prefix_end(
                sampled_best, lambda r: polynomial_count(family, r), start
            )
        if family == "six":
            degrees = Counter(curve[1] - 1 for curve in curves.values())
            check(dict(degrees), {1: 3, 3: 3, 4: 3 * t - 6, 6: t_size - 3 * t},
                  mismatch, "six-neighbor family histogram")
        if family == "twelve":
            low = [curve for curve in curves.values() if curve[1] == 2]
            check(len(low), 4, mismatch, "four members with one neighbor")
            expected = [math.comb(r + 2, 3) + 1 for r in range(t + 1)]
            check(sum(curve[:t + 1] == expected for curve in low), len(low), mismatch,
                  "cubic count from members with one neighbor")
    if family == "twelve" and law in {"L1", "L6", "L7"}:
        count = 4 if law == "L6" else 5
        check(len(parts), count, mismatch, "parts with a cap of three")
        result["capped_part_counts"] = []
        for part in parts:
            part_neighbors = {v: neighbors[v] for v in part}
            best = greatest_counts([curve for _, curve in reach_counts(part_neighbors, part)])
            check(best, [min(2 * r + 1, len(part)) for r in range(len(best))],
                  mismatch, f"capped part count from {part[0]}")
            result["capped_part_counts"].append(best)
    if mismatch:
        result["mismatch"] = mismatch
    return result


def check_probe_run(row, census):
    start_time = monotonic()
    start, law, knot_law = row["start"], row["law"], row["knot law"]
    stars = stars_of(census, start)
    growth = Growth(stars, law, knot_law)
    schedule = {stage["round"]: stage for stage in row["stages"]}
    sums = [len(growth.members)]
    result = {"start": start, "stars": stars, "law": law, "knot_law": knot_law}
    stages = []
    births = []
    closures = []
    while growth.round < row["rounds done"]:
        n = growth.step()
        if not n:
            break
        births.append(n)
        sums.append(len(growth.members))
        if any(len(p) == len(q) for p, q in zip(growth.places[-n:], growth.parents[-n:], strict=True)):
            closures.append(growth.round)
        if growth.round in schedule:
            stages.append(check_probe_stage(growth, schedule[growth.round], FAMILY_OF[start], law))
    mismatch = {}
    check(growth.round, row["rounds done"], mismatch, "rounds done")
    check(len(growth.places), row["knots"], mismatch, "knots final")
    check(sums, row["members per round"], mismatch, "members per round")
    check([x["round"] for x in stages], sorted(schedule), mismatch, "reached recorded stages")
    if row["stop"] == "knots":
        check(len(growth.places) - births[-1] <= 50_000 < len(growth.places), True, mismatch, "knot cap")
    result["rounds_done"] = growth.round
    result["stages"] = stages
    result["members_per_round"] = sums
    result["births_per_round"] = births
    result["births_with_no_fresh_distinction"] = closures
    if mismatch:
        result["mismatch"] = mismatch
    result["wall_seconds"] = round(monotonic() - start_time, 3)
    return result


def quadratic_bounds(curve, span, factor):
    # The growth gate used a common range for H. Here these are solely
    # robustness readings of one P curve. Check the roster's final segment
    # separately from an arbitrary segment.
    ratios = {r: Fraction(curve[r], r * r) for r in range(4, len(curve))}
    longest = None
    final = []
    for a in ratios:
        low = high = ratios[a]
        for z in range(a, len(curve)):
            low = min(low, ratios[z])
            high = max(high, ratios[z])
            if high > factor * low:
                break
            if z >= span * a:
                row = [a, z]
                if longest is None or (z - a) > (longest[1] - longest[0]):
                    longest = row
                if z == len(curve) - 1:
                    final.append(row)
    return {"longest_range": longest, "final_segment": final[0] if final else None}


def compare_first_look(census, records, first_look):
    for entry in records:
        start, law = entry["start"], entry["law"]
        began = monotonic()
        growth = Growth(stars_of(census, start), law)
        births = []
        while growth.round < 66:
            b = growth.step()
            if not b:
                break
            births.append(b)
        roster = growth.roster()
        all_curves = dict(reach_counts(roster.neighbors, sorted(roster.neighbors)))
        best = greatest_counts(list(all_curves.values()))
        mismatch = {}
        check(growth.round, 66, mismatch, "round")
        check(births, entry["births"], mismatch, "births per round")
        check(len(growth.places), entry["knots_final"], mismatch, "count of all knots")
        check(len(growth.members), 2214, mismatch, "roster size")
        check(len(list(connected_parts(roster.neighbors))), 1, mismatch, "one part")
        samples = entry["P_66" if law == "L1" else "at_T"]
        samples = samples["counted_from"] if law == "L1" else samples["P"]["counted_from"]
        sample_readings = []
        missing = []
        for sample in samples:
            v = sample["member"]
            if v not in all_curves:
                missing.append(v)
                continue
            counts = all_curves[v]
            check(counts, sample["P"], mismatch, f"count from {v}")
            exact = prefix_end(counts, lambda r: polynomial_count("six", r))
            bounds = quadratic_bounds(counts, 8, 2)
            sample_readings.append({
                "member": v, "exact_through": exact, "recorded_label": sample["label"],
                "greatest_steps": len(counts) - 1, "quadratic_bounds_factor_8_and_2": bounds,
                "quadratic_bounds_factor_4_and_3": quadratic_bounds(counts, 4, 3),
            })
        if missing:
            mismatch["missing recorded samples"] = missing
        selected = [row for row in sample_readings if row["exact_through"] >= 5]
        if law != "L1":
            reported = first_look["runs"][f"{law} | {start} | round 66"]
            check(
                [(row["member"], row["exact through r"]) for row in reported["members"]],
                [(row["member"], row["exact_through"]) for row in selected],
                mismatch, "first-look prefix counts",
            )
        yield {
            "start": start, "starts_holding": stars_of(census, start), "law": law,
            "round": growth.round, "knots": len(growth.places), "members": len(growth.members),
            "sampled_matching_through_at_least_5": len(selected),
            "sampled_longest_exact_prefix": max(x["exact_through"] for x in sample_readings),
            "all_member_longest_exact_prefix": prefix_end(best, lambda r: polynomial_count("six", r)),
            "all_member_greatest_counts": best,
            "number_of_members_matching_through_at_least_5": sum(
                prefix_end(curve, lambda r: polynomial_count("six", r)) >= 5
                for curve in all_curves.values()
            ),
            "sampled_readings": sample_readings,
            "mismatch": mismatch, "wall_seconds": round(monotonic() - began, 3),
        }


def summarize_probe(rows):
    totals = Counter()
    families = defaultdict(dict)
    for row in rows:
        family = FAMILY_OF[row["start"]]
        label = f'{row["law"]} {row["knot_law"]}'
        totals["runs"] += 1
        totals["runs_with_mismatches"] += bool(row.get("mismatch"))
        for stage in row["stages"]:
            totals["stages"] += 1
            totals["stages_with_mismatches"] += bool(stage.get("mismatch"))
            if "recorded_sources" in stage:
                totals["profile_stages"] += 1
                totals["profile_stages_with_even_sample"] += stage["recorded_sources"] < stage["part_sizes"][0]
                totals["all_member_maxima_different_from_sample"] += stage[
                    "recorded_sources_greatest_counts_differ"
                ]
            if "exact_formula_through" in stage:
                key = f'{label}, round {stage["round"]}'
                families[family].setdefault(key, set()).add(stage["exact_formula_through"])
                totals["profile_stages_below_formula_after_match"] += stage["strictly_below_formula_after"]
            if "capped_part_counts" in stage:
                totals["stages_with_capped_part_counts"] += 1
                totals["capped_parts"] += len(stage["capped_part_counts"])
    by_family = {k: {q: sorted(v) for q, v in d.items()} for k, d in families.items()}
    return {"totals": dict(totals), "all_member_exact_through": by_family}


def summarize_first_look(rows):
    summary = {}
    for restriction, group in (
        ("first look", [row for row in rows if row["law"] != "L1"]),
        ("cap of three with waiting", [row for row in rows if row["law"] == "L1"]),
    ):
        if not group:
            continue
        samples = [sample for row in group for sample in row["sampled_readings"]]
        summary[restriction] = {
            "runs": len(group),
            "sampled_members": len(samples),
            "sampled_matching_through_at_least_5": sum(x["exact_through"] >= 5 for x in samples),
            "sampled_longest_exact_prefix": max(x["exact_through"] for x in samples),
            "all_member_longest_exact_prefixes": sorted({
                row["all_member_longest_exact_prefix"] for row in group
            }),
            "sampled_roster_labels": dict(Counter(x["recorded_label"] for x in samples)),
            "any_quadratic_range_with_bounds_8_and_2": sum(
                x["quadratic_bounds_factor_8_and_2"]["longest_range"] is not None for x in samples
            ),
            "final_quadratic_segment_with_bounds_8_and_2": sum(
                x["quadratic_bounds_factor_8_and_2"]["final_segment"] is not None for x in samples
            ),
            "any_quadratic_range_with_bounds_4_and_3": sum(
                x["quadratic_bounds_factor_4_and_3"]["longest_range"] is not None for x in samples
            ),
            "final_quadratic_segment_with_bounds_4_and_3": sum(
                x["quadratic_bounds_factor_4_and_3"]["final_segment"] is not None for x in samples
            ),
        }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-index", action="append", type=int)
    parser.add_argument("--probe-law", action="append")
    parser.add_argument("--skip-probe", action="store_true")
    parser.add_argument("--first-look-limit", type=int)
    parser.add_argument("--first-look-law", action="append")
    parser.add_argument("--skip-first-look", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE / "regrow_rosters.json")
    args = parser.parse_args()
    census = json.loads((TICKET / "census_starts.json").read_text())
    start = monotonic()
    probe = []
    if not args.skip_probe:
        for i, row in enumerate(records(CHECKS / "roster_probe" / "probe_runs.jsonl.gz")):
            if args.probe_index is not None and i not in args.probe_index:
                continue
            if args.probe_law is not None and row["law"] not in args.probe_law:
                continue
            out = check_probe_run(row, census)
            probe.append(out)
            print(i, out["start"], out["law"], out["knot_law"], out["wall_seconds"], flush=True)
    first = []
    if not args.skip_first_look:
        gate_path = next(ARTIFACTS.glob("*/run2.jsonl.gz"))
        first_look = json.loads((CHECKS / "square_law.json").read_text())
        inputs = [
            row for row in records(gate_path)
            if row["start"] in {f"census:{i}" for i in FAMILIES["six"][:4]}
            and row["kind"] in {"census", "P only"}
            and row["law"] in {"L0", "L1", "L6", "L7"}
            and (args.first_look_law is None or row["law"] in args.first_look_law)
        ][:args.first_look_limit]
        for row in compare_first_look(census, inputs, first_look):
            first.append(row)
            print("first look", row["start"], row["law"], row["wall_seconds"], flush=True)
    result = {
        "probe_summary": summarize_probe(probe),
        "first_look_summary": summarize_first_look(first),
        "probe": probe,
        "first_look": first,
        "wall_seconds": round(monotonic() - start, 3),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
