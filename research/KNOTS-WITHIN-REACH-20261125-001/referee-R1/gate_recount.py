"""Recount the paired history gates and the roster labels from individual curves."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import islice, pairwise
import json
from math import isclose
from pathlib import Path
from random import Random
import re
import resource
from time import monotonic

from gate_readings import gate, history_readings, limits, power, roster_reading


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name + "A"
ARTIFACTS = ROOT / "artifacts" / TICKET / (TICKET + "-E001_knots_within_reach")
REGISTERED = {"named", "census", "bare ring"}
STAGES = ("at_T", "at_2T")
CAPS = {"L6", "L7"}
HIGH_POWER = {"POWER(2)", "POWER(3)"}
P9_LITERAL = {"POWER(1)", "ALL WITHIN r"}
GATES = {
    "registered": ("H", "gate", 8, 2, Fraction(9, 5)),
    "threshold swap": ("H", "gate_swap_thresholds", 4, 3, Fraction(3, 2)),
    "parent steps": ("H_parent_steps", "gate_parent_steps", 8, 2, Fraction(9, 5)),
    "retired stops": ("H_retired_not_stepped", "gate_retired_not_stepped", 8, 2, Fraction(9, 5)),
}


def run_key(record):
    return f"{record['kind']} | {record['start']} | {record['law']} | {record['T']}"


def registered_items():
    folder = ROOT / "research" / TICKET
    named = json.loads((folder / "named_starts.json").read_text())["named_starts"]
    five = json.loads((folder / "five_knot_order.json").read_text())["order"][:50]
    small = json.loads((folder / "run2_small_starts.json").read_text())
    census = [f"census:{i}" for i in five + small["degree_2"] + small["degree_3_or_more"]]
    cases = {
        "named": (named, ("L0", "L6", "L7"), 66),
        "census": (census, ("L0", "L6", "L7"), 66),
        "bare ring": ([s for s in named if s.endswith(",2)")], ("L0",), 264),
        "swap HOLD": (named, ("L3", "L6"), 66),
        "swap bounds": (named, ("L0", "L6", "L7"), 60),
        "P only": ([*named, *census], ("L1",), 66),
    }
    return {f"{kind} | {start} | {law} | {t}" for kind, (starts, laws, t) in cases.items()
            for start in starts for law in laws}


def narrow_fit(curve, a, z, j, ratio):
    if z < a or z >= len(curve):
        return False
    lo, hi = limits(curve, a, z, j)
    return hi <= ratio * lo


def compare_gate(new, old):
    mismatches = {}
    fields = {"K": new["K"], "least_l": new["least_l"], "holds": new["state"] == "holds"}
    if fields["holds"]:
        fields.update(j=new["j"], range=new["range"], k=new["K"])
        if "earlier" in old:
            old_earlier = [{"j": g["j"], "range": g["range"]} for g in old["earlier"]]
            if old_earlier != new["earlier"]:
                mismatches["earlier"] = [old_earlier, new["earlier"]]
        for label, check in new["spread"].items():
            stored = old.get("spread", {}).get(label, {})
            if check["n"] != stored.get("n") or check["band"] != stored.get("band") or not isclose(
                    check["spread"], stored.get("spread", 0), rel_tol=1e-12):
                mismatches[f"spread {label}"] = [stored, check]
    if new["state"] == "no gate":
        support = new["widest_support"]
        fields["k"] = max(support.values())
        fields["j_best"] = min(j for j, count in support.items() if count == fields["k"])
        fields["k_by_j_on_widest"] = {str(j): count for j, count in support.items()}
        fields["widest"] = new["reported partial support range"]
    mismatches.update({field: [old.get(field), value] for field, value in fields.items() if old.get(field) != value})
    return mismatches


def paired(first, second, scaling):
    if first["state"] in {"short", "not reached"}:
        return "undecided"
    if first["state"] == "no gate":
        return "no gate"
    if second["state"] in {"short", "not reached"}:
        return "undecided"
    if second["state"] == "holds" and second["j"] == first["j"] and second["range"][1] >= scaling * first["range"][1]:
        return f"both j={first['j']}"
    return "gate only"


def any_common_power(first, second, scaling):
    left = first.get("each_degree", {})
    right = second.get("each_degree", {})
    return sorted(j for j in left.keys() & right.keys() if right[j][1] >= scaling * left[j][1])


def expected_samples(record, stage):
    """Recreate candidate names and the frozen samples when steps equal birth round."""
    if record["kind"] not in REGISTERED:
        return []
    classes = stage["classes"]
    num_start = len(classes["a"])
    name_ranges = [num_start]
    for count in record["births"][:stage["round"]]:
        name_ranges.append(name_ranges[-1] + count)
    failures = []
    s_min = stage["s_min"]
    if s_min is None:
        return failures
    intervals = {"b": (1, s_min // 4), "c": (s_min // 2 - 2, s_min // 2),
                 "d": (3 * s_min // 4 - 2, 3 * s_min // 4)}
    for group, (lo, hi) in intervals.items():
        lo, hi = max(1, lo), min(hi, stage["round"])
        candidates = range(name_ranges[lo - 1], name_ranges[hi]) if hi >= lo else range(0)
        seed = f"KWR|{record['start']}|{record['law']}|nae|{group}".encode()
        sampled = Random(int.from_bytes(sha256(seed).digest(), "big")).sample(candidates, min(len(candidates), 64))
        if len(candidates) != stage["candidates"][group] or set(sampled) != set(classes[group]):
            failures.append({"class": group, "stored_candidates": stage["candidates"][group],
                             "recount_candidates": len(candidates), "sampled_names_agree": set(sampled) == set(classes[group])})
    if not stage["ended_here"]:
        for u in classes["a"] + classes["b"] + classes["c"] + classes["d"]:
            r = next(i for i, end in enumerate(name_ranges) if u < end)
            if stage["ell"][str(u)] != s_min - r:
                failures.append({"knot": u, "birth_round": r, "stored_l": stage["ell"][str(u)], "recount_l": s_min - r})
    return failures


def recount_roster(roster, identity, mismatches):
    observations = Counter()
    widest = Counter()
    examples = []
    if "counted_from" not in roster:
        return observations, widest, examples
    assert roster["members"] == sum(roster["part_sizes"])
    assert roster["parts"] == len(roster["part_sizes"])
    assert len(roster["counted_from"]) == min(roster["members"], 8)
    assert len({record["member"] for record in roster["counted_from"]}) == len(roster["counted_from"])
    for row in roster["counted_from"]:
        counts = row["P"]
        assert counts[0] == 1 and all(left < right for left, right in pairwise(counts))
        assert len(counts) - 1 == row["greatest_ws"] and counts[-1] in roster["part_sizes"]
        label, interval = roster_reading(counts)
        observations[label] += 1
        widest["enough for any exact power"] += len(counts) >= 8
        widest["enough for a quadratic exact power"] += len(counts) >= 10
        stored_interval = row.get("reading", {}).get("segment")
        if label != row["label"] or interval is not None and interval != stored_interval:
            mismatches.append([identity, row["member"], row["label"], stored_interval, label, interval])
        if label not in P9_LITERAL:
            examples.append({"knot": row["member"], "label": label, "greatest_ws": len(counts) - 1})
    return observations, widest, examples


def p6(record, reports):
    if record["law"] != "L0" or not re.fullmatch(r"Ring\(\d+,2\)", record["start"]):
        return None
    n = int(record["start"].split("(")[1].split(",")[0])
    summary = {"n": n, "T": record["T"], "constant_births": set(record["births"]) == {n}, "stages": {}}
    for stage_key in STAGES:
        stage = record[stage_key]
        profiles = {}
        for name, knot_ids in (("start", stage["classes"]["a"]), ("made", stage["classes"]["b"] + stage["classes"]["c"])):
            curves = {str(knot): stage["H"][str(knot)] for knot in knot_ids}
            eligible = sum(n <= len(curve) and n > 4 for curve in curves.values())
            fits = sum(narrow_fit(curve, 4, n - 1, 2, 2) for curve in curves.values())
            d, h = 0, 0
            if name == "made":
                for knot, curve in curves.items():
                    t = int(knot) // n
                    if t < n or len(curve) <= n:
                        continue
                    d += 1
                    # On the kept range there is no cut above the knot counted from.
                    correct = [2*r*r + 2*r + 1 if r < n else n*(min(r, t) + r + 1) for r in range(len(curve))]
                    assert curve == correct, (record["start"], knot, stage_key)
                    h += len(curve) - 1 > t
            profiles[name] = {"fits [4,n-1] at factor 2": fits, "eligible": eligible, "all": len(curves),
                              "corrected formula compared": d, "extend past birth round": h}
        summary["stages"][stage_key] = {"n-1 reaches factor 8": n - 1 >= 32,
                                       "same range counts": profiles, "gate": reports[stage_key]["registered"],
                                       "all made pass full gate on [4,n-1]": n - 1 >= 32 and
                                       profiles["made"]["all"] == profiles["made"]["fits [4,n-1] at factor 2"]}
    return summary


def check_history(curve, stage, knot, identity, discrepancies):
    reading, bound, doubling = history_readings(tuple(curve), stage["ended_here"])
    label, degree, interval = reading
    old = stage["reading"][knot]
    if label != old["verdict"] or degree != old.get("j", old.get("k")) or (
            interval is not None and interval != old.get("segment")):
        discrepancies["individual H final readings"].append([identity, [old["verdict"], old.get("j", old.get("k")),
                                                                      old.get("segment")], reading])
    old_bound = stage["bound"][knot]
    if bound is not None and old_bound is not None:
        j, a, low, high = bound
        if j != old_bound["j"] or [a, len(curve) - 1] != old_bound["segment"] or not all(
                isclose(float(value), old_bound[field], rel_tol=1e-12)
                for field, value in (("c", low), ("C", high), ("C_over_c", high / low))):
            discrepancies["individual BOUND swap"].append([identity, old_bound, [j, a, str(low), str(high)]])
    elif (bound is None) != (old_bound is None):
        discrepancies["individual BOUND swap"].append([identity, old_bound, str(bound)])
    old_doubling = stage["doubling"][knot]
    if old_doubling != doubling:
        discrepancies["individual doubling swap"].append([identity, old_doubling, doubling])
    return (f"{label}({degree})" if degree is not None else label), bound is not None, bool(doubling)


def inspect(records):
    rows = {}
    pair_totals = defaultdict(Counter)
    stage_totals = defaultdict(Counter)
    eligibility = defaultdict(Counter)
    roster_totals = defaultdict(Counter)
    roster_eligibility = defaultdict(Counter)
    roster_stages = defaultdict(Counter)
    p9_cases = defaultdict(list)
    individual_stage_gates = defaultdict(Counter)
    overlap = defaultdict(Counter)
    robust_totals = defaultdict(Counter)
    mismatches = defaultdict(list)
    p6_reports = []
    long_j2 = Counter()
    capped_j2_roster = Counter()
    both_births = Counter()
    preserved_prefix = Counter()
    candidate_checks = Counter()
    strict_pairs = Counter()
    endpoint_bounds = defaultdict(list)
    square_curves = Counter()
    f_checks = Counter()
    history_totals = defaultdict(Counter)
    coverage = Counter()
    for record in records:
        key = run_key(record)
        kind, law = record["kind"], record["law"]
        dataset = "registered" if kind in REGISTERED else kind
        coverage[f"{dataset} | {law}"] += 1
        assert key not in rows
        row = rows[key] = {"item": record["item"], "stop": record["stop"], "ended": record["ended"],
                          "rounds_done": record["rounds_done"], "gates": {}, "roster labels": {}}
        if kind == "P only":
            rosters = [(str(t), record.get(f"P_{t}", {}), record.get(f"P_{t}_round")) for t in (66, 132)]
        else:
            rosters = [(label, record[label].get("P", {}), record[label].get("round")) for label in STAGES]
        for phase, roster, round_done in rosters:
            total_key = f"{dataset} | {law}"
            roster_stages[total_key][f"{phase}: {('read' if 'counted_from' in roster else 'empty or absent')}"] += 1
            counts, widths, examples = recount_roster(roster, [key, phase], mismatches["roster labels or segments"])
            roster_totals[total_key].update(counts)
            roster_eligibility[total_key].update(widths)
            row["roster labels"][phase] = counts
            if examples and (kind == "P only" or dataset == "registered" and law in CAPS):
                p9_cases[total_key].append({"run": key, "phase": phase, "actual_round": round_done, "cases": examples})
            if kind == "census" and phase == "at_T" and record["start"] in {
                    "census:19", "census:164", "census:172", "census:214"}:
                for source in roster["counted_from"]:
                    curve = source["P"]
                    z = len(curve) - 1
                    match = next((r - 1 for r, F in enumerate(curve) if F != 3 * r * r + 3 * r + 1), z)
                    square_curves["recorded curves"] += 1
                    square_curves["quadratic prefix at least through step 5"] += match >= 5
                    square_curves["quadratic prefix at least through step 9"] += match >= 9
                    square_curves["at least 32 witnessed steps available"] += z >= 32
                    square_curves["hypothetical final segment BOUND(2)"] += z >= 32 and narrow_fit(curve, z // 8, z, 2, 2)
                    square_curves[roster_reading(curve)[0]] += 1
        if kind == "P only":
            continue
        for phase in STAGES:
            stage = record[phase]
            stage_reports = row["gates"][phase] = {}
            phase_key = f"{dataset} | {law} | {phase}"
            if stage.get("not_reached"):
                for mode in GATES:
                    stage_reports[mode] = {"state": "not reached"}
                eligibility[phase_key]["round not reached"] += 1
                if dataset == "registered":
                    endpoint_bounds[f"{phase} missing | {record['stop']}"].append(key)
                continue
            if dataset == "registered":
                if stage["knots"] > record["knot_bound"]:
                    endpoint_bounds[f"{phase} read above knot bound"].append(
                        {"run": key, "knots": stage["knots"], "round": stage["round"]})
                future = stage["check_F"]
                f_checks["reported stage checks"] += 1
                f_checks["reported knot checks"] += future.get("checked", 0)
                f_checks["stage checks with no knots compared"] += future.get("checked", 0) == 0
                f_checks["reported disagreements"] += future.get("n_bad", 0)
                f_checks["reported knot checks at ten more rounds"] += (
                    future.get("checked", 0) if future.get("t2") == stage["round"] + 10 else 0)
            candidates = expected_samples(record, stage)
            if candidates:
                mismatches["frozen candidate counts, samples or kept range"].append([key, phase, candidates])
            if kind in REGISTERED:
                candidate_checks["stages with recorded curves"] += 1
                candidate_checks["stage has s_min"] += stage["s_min"] is not None
                candidate_checks["eligible class c has sampled knots"] += bool(stage["classes"]["c"])
            paths = stage["H"]
            classes = stage["classes"]
            assert set(paths) == {str(knot) for group in classes.values() for knot in group}
            for knot, path in paths.items():
                assert path[0] == 1 and all(a <= z for a, z in pairwise(path)), (key, phase, knot)
                assert len(path) == stage["ell"][knot] + 1, (key, phase, knot)
                result, has_bound, has_doubling = check_history(path, stage, knot, [key, phase, knot], mismatches)
                bucket = history_totals[phase_key]
                bucket["H count curves"] += 1
                bucket[result] += 1
                bucket["individual BOUND defined"] += has_bound
                bucket["individual doubling defined"] += has_doubling
            core = {str(knot): paths[str(knot)] for label in "abc" for knot in classes[label]}
            assert len(core) == sum(len(classes[label]) for label in "abc")
            for mode, (path_field, gate_field, span, tolerance, _) in GATES.items():
                if gate_field not in stage:
                    continue
                paths_for_mode = core | stage.get(path_field, {}) if path_field != "H" else core
                assert set(paths_for_mode) == set(core), (key, phase, mode)
                stage_gate = gate(paths_for_mode, span, tolerance, map(str, classes["a"]))
                stage_reports[mode] = stage_gate
                mismatch = compare_gate(stage_gate, stage[gate_field])
                if mismatch:
                    mismatches[f"gate: {mode}"].append([key, phase, mismatch])
                outcome = f"holds j={stage_gate['j']}" if stage_gate["state"] == "holds" else stage_gate["state"]
                stage_totals[f"{phase_key} | {mode}"][outcome] += 1
                if dataset == "registered":
                    individual_stage_gates[f"{mode} | {phase}"][outcome] += 1
                    if len(stage_gate.get("at_canonical_end", [])) > 1:
                        overlap[mode][phase] += 1
                    if stage_gate["state"] == "no gate":
                        max_peak = max(d["k"] for d in stage_gate["peak_support"].values())
                        overlap[mode][f"{phase} reported widest support below best on an allowed range"] += (
                            max_peak > max(stage_gate["widest_support"].values()))
            main = stage_reports["registered"]
            eligibility[phase_key]["range shorter than 32" if main["state"] == "short" else "range at least 32"] += 1
            if dataset == "registered":
                swapped = stage.get("P_live_swap", {})
                counts, _, _ = recount_roster(swapped, [key, phase, "live swap"], mismatches["roster labels or segments"])
                roster_totals[f"live swap | {law}"].update(counts)
        coverage[f"{dataset} | {law} | windows past the knot bound"] += sum(
            record[phase].get("not_reached", False) and record["stop"] == "knots" for phase in STAGES)
        first_curves = record["at_T"].get("H", {})
        second_curves = record["at_2T"].get("H", {})
        if dataset == "registered" and not record["at_T"].get("ended_here"):
            for u in first_curves.keys() & second_curves.keys():
                first, second = first_curves[u], second_curves[u]
                common = min(len(first), len(second))
                preserved_prefix["compared overlapping recorded knots"] += 1
                preserved_prefix["disagreeing common prefixes"] += first[:common] != second[:common]
        first, second = (row["gates"][phase] for phase in STAGES)
        row["paired"] = {}
        for mode, (_, _, _, _, scaling) in GATES.items():
            if mode not in first or mode not in second:
                continue
            answer = paired(first[mode], second[mode], scaling)
            row["paired"][mode] = answer
            pair_totals[f"{dataset} | {mode}"][answer] += 1
            pair_totals[f"{dataset} | {mode} | {law}"][answer] += 1
            if dataset == "registered":
                left, right = first[mode], second[mode]
                left_label = f"holds j={left['j']}" if left["state"] == "holds" else left["state"]
                right_label = f"holds j={right['j']}" if right["state"] == "holds" else right["state"]
                eligibility[f"{mode} | paired reasons"][f"{left_label} | {right_label}"] += 1
                other = any_common_power(left, right, scaling)
                if other:
                    for j in other:
                        robust_totals[mode][f"any common degree j={j}"] += 1
                if mode == "registered" and record["verdict"]["answer"] != answer.split(" j=")[0]:
                    mismatches["registered paired verdict"].append([key, record["verdict"]["answer"], answer])
                if mode == "registered":
                    missing_2T = right["state"] == "not reached"
                    strict_pairs["undecided" if missing_2T else answer] += 1
                    if missing_2T and answer == "no gate":
                        endpoint_bounds[f"regular 'no gate' despite missing 2T | {record['stop']}"].append(key)
        if dataset == "registered" and row["paired"]["registered"].startswith("both"):
            births = record["births"]
            degree = power(births)
            both_births["constant every recorded round" if len(set(births)) == 1 else "varies before terminal segment"] += 1
            both_births[f"terminal degree {degree[0] if degree else None}"] += 1
        if dataset == "registered" and second["registered"].get("j") == 2:
            long_j2[law] += 1
            roster = record["at_2T"]["P"]
            if law in CAPS:
                degree = power(record["births"])
                capped_j2_roster[f"births terminal degree {degree[0] if degree else None}"] += 1
                capped_j2_roster[f"parts at 2T: {roster['parts']}"] += 1
                capped_j2_roster["part size multiset changes between T and 2T"] += (
                    sorted(record["at_T"]["P"]["part_sizes"]) != sorted(roster["part_sizes"]))
                capped_j2_roster["number of parts changes between T and 2T"] += (
                    record["at_T"]["P"]["parts"] != roster["parts"])
                capped_j2_roster.update(row["roster labels"]["at_2T"])
        if dataset == "registered":
            family = p6(record, row["gates"])
            if family:
                p6_reports.append(family)
    return {"recounts": {
        "coverage": coverage, "paired verdicts": pair_totals, "stage verdicts by law": stage_totals,
        "registered stage verdicts": individual_stage_gates, "eligibility": eligibility,
        "power ambiguity and partial support": overlap, "common power even if canonical gates differ": robust_totals,
        "roster labels": roster_totals, "roster stages": roster_stages, "roster eligibility": roster_eligibility,
        "P9 cases outside the literal outcomes": p9_cases, "P6": p6_reports,
        "long j2 by law": long_j2, "capped long j2 roster and births": capped_j2_roster,
        "births for both": both_births, "same-knot H prefixes": preserved_prefix, "sample and range audit": candidate_checks,
        "reported check F metadata": f_checks, "all missing longer lengths called undecided": strict_pairs,
        "round and knot bound cases": endpoint_bounds, "early square curves": square_curves,
        "individual H final readings and swaps": history_totals,
        "stored-output discrepancies": mismatches,
    }, "runs": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=int, metavar="ITEMS")
    args = parser.parse_args()
    start = monotonic()
    with gzip.open(ARTIFACTS / "run2.jsonl.gz", "rt") as data:
        rows = map(json.loads, data)
        result = inspect(islice(rows, args.pilot) if args.pilot is not None else rows)
    result["execution"] = {"items": len(result["runs"]), "seconds": round(monotonic() - start, 3),
                           "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if args.pilot is None:
        assert result["execution"]["items"] == 396
        expected = registered_items()
        assert expected == set(result["runs"]), expected.symmetric_difference(result["runs"])
        result["execution"]["frozen and disclosed cases matched"] = len(expected)
        (HERE / "gate_recount.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["execution"])
    print({key: len(value) for key, value in result["recounts"]["stored-output discrepancies"].items()})


if __name__ == "__main__":
    main()
