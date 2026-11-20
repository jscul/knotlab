"""Read exact ancestry and ordinary knot-step profiles from feedback stage exports."""

from argparse import ArgumentParser
from collections import Counter, deque
from hashlib import file_digest, sha256
import json
from pathlib import Path

from measure_growth import load_growth


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT = ROOT / "artifacts" / HERE.parent.name / HERE.name
STEP_CAP = 8


def ordinary_neighbors(stars):
    holders = {}
    for knot, support in enumerate(stars):
        for bit in support:
            holders.setdefault(bit, []).append(knot)
    neighbors = [set() for _ in stars]
    for knots in holders.values():
        assert 1 <= len(knots) <= 2
        if len(knots) == 2:
            p, q = knots
            neighbors[p].add(q)
            neighbors[q].add(p)
    return neighbors


def knot_steps(neighbors, roots):
    distance = dict.fromkeys(roots, 0)
    queue = deque(roots)
    while queue:
        parent = queue.popleft()
        for child in neighbors[parent]:
            if child not in distance:
                distance[child] = distance[parent] + 1
                queue.append(child)
    return distance


def bucket(distance):
    if distance is None:
        return STEP_CAP + 2
    return min(distance, STEP_CAP + 1)


def count_steps(distances):
    bins = [0] * (STEP_CAP + 3)
    for distance in distances:
        bins[bucket(distance)] += 1
    return bins


def region_label(ancestry, rings, exclusive):
    uses = [i for i, core in enumerate(exclusive) if ancestry & core]
    if not uses:
        return "background"
    if len(uses) > 1:
        return "both_rings"
    i = uses[0]
    if ancestry <= rings[i]:
        return f"pure_{i}"
    return f"mixed_{i}"


def roots_for(roles, rings):
    roots = {f"seam_{i}": (seam,) for i, seam in enumerate(roles.get("seams", []))}
    roots.update({f"ring_{i}": sorted(ring) for i, ring in enumerate(rings)})
    if roles.get("background"):
        roots["original_path"] = roles["background"]
    return roots


def ancestry_profile(stages, roles):
    """Rebuild ancestry from actual parents instead of trusting evaluator labels."""
    rings = list(map(set, roles.get("rings", [])))
    if roles.get("cut_appendage"):
        assert not rings
        rings = [set(roles["cut_appendage"])]
    background = set(roles.get("background", []))
    exclusive = [ring - background for ring in rings]
    regions = ["background", "both_rings"]
    regions += [f"{prefix}_{i}" for i in range(len(rings)) for prefix in ("pure", "mixed")]
    roots = roots_for(roles, rings)
    ancestry = {}
    previous = None
    previous_steps = None
    rows = {}
    for age, stage in sorted(((int(age), row) for age, row in stages.items())):
        stars = stage["stars"]
        occupied = set(stage["occupied"])
        born = stage["born"]
        parents = {int(k): row for k, row in stage["parent_sets"].items()}
        loose = {int(k): set(row) for k, row in stage["loose"].items()}
        count = Counter({region: 0 for region in regions})
        if age == 0:
            born = born or list(range(len(stars)))
            assert set(born) == set(range(len(stars))) and not parents
            assert set(born) == background.union(*rings)
            ancestry = {knot: {knot} for knot in born}
        else:
            assert previous is not None and age == previous["age"] + 1
            assert set(born) == set(parents)
            assert all(parent in ancestry for values in parents.values() for parent in values)
            for knot in born:
                ancestry[knot] = set.union(*(ancestry[parent] for parent in parents[knot]))
        assert len(ancestry) == len(stars)
        assert all(len(occupied.intersection(support)) % 2 == 0 for support in stars)
        for knot in born:
            count[region_label(ancestry[knot], rings, exclusive)] += 1
        assert sum(count.values()) == len(born)
        graph = ordinary_neighbors(stars)
        step_maps = {name: knot_steps(graph, seeds) for name, seeds in roots.items()}
        proximity = {}
        for name, steps in step_maps.items():
            old_steps = previous_steps[name] if previous_steps is not None else {}
            nearest_parent = [min((old_steps[p] for p in parents[knot] if p in old_steps), default=None)
                              for knot in born] if age else []
            distance_to_birth = [steps.get(knot) for knot in born]
            shells = count_steps(steps.get(knot) for knot in range(len(stars)))
            prefix = [sum(shells[:d+1]) for d in range(STEP_CAP + 1)]
            proximity[name] = {
                "all_knots_ball": prefix,
                "born_by_ordinary_knot_steps": count_steps(distance_to_birth),
                "born_by_previous_parent_steps": count_steps(nearest_parent) if age else None,
                "new_knots_touching_original_holders": nearest_parent.count(0) if age else None,
            }
        mark_rows = roles.get("ring_edges", [])
        active = {"total_ones": len(occupied),
                  "loose_ones": sum(len(occupied & bits) for bits in loose.values()),
                  "live_hot_knots": sum(bool(occupied.intersection(stars[knot])) for knot in loose),
                  "ring_mark_masks": [[int(bit in occupied) for bit in bits] for bits in mark_rows]}
        new_multi = sum(len(group) > 1 for group in parents.values())
        row = {"age": age, "births": len(born), "knots": len(stars),
               "distinctions": stage["distinction_count"],
               "fresh": (stage["distinction_count"] - previous["distinctions"]) if age else None,
               "fresh_per_birth": dict(Counter(map(len, stage["fresh"].values()))) if age else None,
               "new_multi": new_multi if age else None,
               "refused_multi": stage["vetoed_multi"] if age else None,
               "sizes": dict(Counter(map(len, (stars[knot] for knot in born)))),
               "ancestry": dict(count), "activity": active, "knot_steps": proximity}
        rows[age] = row
        previous, previous_steps = row, step_maps
    return rows


def scalars(row):
    numbers = {key: row[key] for key in ("births", "knots", "distinctions", "fresh", "new_multi", "refused_multi")
               if row[key] is not None}
    numbers.update(row["ancestry"])
    for name, profile in row["knot_steps"].items():
        if profile["new_knots_touching_original_holders"] is not None:
            numbers[f"{name}_touch"] = profile["new_knots_touching_original_holders"]
    return numbers


def geometry_delta(current, base):
    difference = {}
    for root, values in current.items():
        assert root in base
        difference[root] = {}
        for key, readings in values.items():
            if isinstance(readings, list):
                difference[root][key] = [a-b for a, b in zip(readings, base[root][key], strict=True)]
    return difference


def compare(current, base):
    matched = sorted(current.keys() & base.keys())
    result = {}
    for age in matched:
        now, before = current[age], base[age]
        old_counts = scalars(before)
        result[age] = {"difference": {key: value-old_counts[key] for key, value in scalars(now).items()},
                       "knot_steps": geometry_delta(now["knot_steps"], before["knot_steps"])}
    return {"matched_ages": matched, "only_treatment": sorted(current.keys() - base.keys()),
            "only_comparator": sorted(base.keys() - current.keys()), "results": result}


def receiver_factorial(cells):
    labels = ("00", "10", "01", "11")
    common = set.intersection(*(set(cells[k]) for k in labels))
    out = {}
    for age in sorted(common):
        x00, x10, x01, x11 = (scalars(cells[k][age]) for k in labels)
        out[age] = {}
        for key in x00:
            out[age][key] = {
                "ring_0_load_given_ring_1_quiet": x10[key]-x00[key],
                "ring_0_load_given_ring_1_loaded": x11[key]-x01[key],
                "ring_1_load_given_ring_0_quiet": x01[key]-x00[key],
                "ring_1_load_given_ring_0_loaded": x11[key]-x10[key],
                "interaction": x11[key]-x10[key]-x01[key]+x00[key],
            }
    conditional = {"donor_0_receiver_1_quiet": compare(cells["10"], cells["00"]),
                   "donor_0_receiver_1_loaded": compare(cells["11"], cells["01"]),
                   "donor_1_receiver_0_quiet": compare(cells["01"], cells["00"]),
                   "donor_1_receiver_0_loaded": compare(cells["11"], cells["10"])}
    return {"all_four_common_ages": sorted(common), "factorial": out, "conditional": conditional}


def successive_counts(rows):
    ratios = {}
    for age, row in rows.items():
        if age-1 not in rows:
            continue
        earlier = rows[age-1]
        now = {"whole": row["births"], **row["ancestry"]}
        prior = {"whole": earlier["births"], **earlier["ancestry"]}
        ratios[age] = {key: [value, prior[key]] if prior[key] else None for key, value in now.items()}
    return ratios


def mask_name(mask, ring_count):
    return "".join(str(mask >> i & 1) for i in range(ring_count)) or "0"


def index_runs(document):
    runs = document["cases"]
    source = {}
    for run_id, run in runs.items():
        if run["family"] != "source":
            continue
        case = run["base_case"]
        count = len(run["input"]["roles"].get("rings", []))
        key = (case, "".join(run["table"]), mask_name(run["load_mask"], count))
        assert key not in source
        source[key] = run_id
    return runs, source


def quiet_key(case, table, roles):
    return case, table, "0" * (len(roles.get("rings", [])) or 1)


def termination_summary(termination):
    summary = {key: value for key, value in termination.items()
               if key in {"status", "last_age", "next_age", "retained_multi", "vetoed_multi", "implied_arity"}
               or key.startswith("planned_")}
    if "shortages" in termination:
        summary["shortage_parents"] = len(termination["shortages"])
        summary["missing_loose_distinctions"] = sum(termination["shortages"].values())
    return summary


def geometric_budget(quiet, treatment, roles, parent_stage, treatment_stages, age):
    """Account for every changed parent-distance birth in an otherwise-fresh veto round."""
    stage = treatment_stages[str(age)]
    refused = [row["parents"] for row in stage["candidate_groups"] if row["action"] == "V"]
    assert len(refused) == stage["vetoed_multi"]
    predicted = sum(len(group)-1 for group in refused)
    assert treatment[age]["births"]-quiet[age]["births"] == predicted
    graph = ordinary_neighbors(parent_stage["stars"])
    rings = [set(row) for row in roles.get("rings", [])]
    if roles.get("cut_appendage"):
        rings = [set(roles["cut_appendage"])]
    result = {"additional_births": predicted, "refused_group_sizes": dict(Counter(map(len, refused))), "by_root": {}}
    for name, seeds in roots_for(roles, rings).items():
        seen = knot_steps(graph, seeds)
        bins = [0] * (STEP_CAP + 3)
        for group in refused:
            individual = [seen.get(parent) for parent in group]
            for distance in individual:
                bins[bucket(distance)] += 1
            nearest = min((d for d in individual if d is not None), default=None)
            bins[bucket(nearest)] -= 1
        field = "born_by_previous_parent_steps"
        observed = [after-before for after, before in zip(treatment[age]["knot_steps"][name][field],
                                                           quiet[age]["knot_steps"][name][field], strict=True)]
        assert bins == observed, (name, bins, observed)
        result["by_root"][name] = bins
    return result


def analyze(document):
    runs, source = index_runs(document)
    assert {case for case, _, _ in source} == {"B", "R0", "R1", "R2", "J0", "J1", "J2", "C1", "T4", "T8"}
    assert len(source) == 16 * 22
    profiles = {}
    raw_rows = {}
    for run_id, run in runs.items():
        stages = run["stages"]
        profiles[run_id] = ancestry_profile(stages, run["input"]["roles"])
        raw_rows[run_id] = {"base_case": run["base_case"], "table": run["table"], "arm": run["arm"],
                           "load_mask": run.get("load_mask"), "termination": termination_summary(run["termination"]),
                           "injection_age": run["injection_age"], "injected_distinctions": run["injected_distinctions"],
                           "preparation": run["preparation"],
                           "rows": profiles[run_id], "successive_birth_count_ratios": successive_counts(profiles[run_id])}
    feedback = {}
    passive = {}
    budgets = {}
    for case, table, mask in sorted(source):
        run_id = source[(case, table, mask)]
        roles = runs[run_id]["input"]["roles"]
        if table != "PP":
            reference = source[(case, "PP", mask)]
            passive[run_id] = {"comparator": reference, **compare(profiles[run_id], profiles[reference])}
        if any(c == "1" for c in mask):
            base = source[quiet_key(case, table, roles)]
            feedback[run_id] = {"comparator": base, **compare(profiles[run_id], profiles[base])}
            if table == "PV" and 1 in profiles[run_id] and 1 in profiles[base]:
                stages = runs[run_id]["stages"]
                budgets[run_id] = geometric_budget(profiles[base], profiles[run_id], roles, stages["0"], stages, 1)
    paired = {}
    receiver_replay = Counter()
    for case in ("T4", "T8"):
        paired[case] = {}
        for table in sorted({table for here, table, _ in source if here == case}):
            names = {mask: source[(case, table, mask)] for mask in ("00", "10", "01", "11")}
            paired[case][table] = {"runs": names, **receiver_factorial({mask: profiles[key] for mask, key in names.items()})}
            for condition, contrast in paired[case][table]["conditional"].items():
                receiver = int(condition.split("_")[3])
                receiver_replay["cases"] += 1
                unmatched = len(contrast["only_treatment"]) + len(contrast["only_comparator"])
                receiver_replay["unmatched_ages"] += unmatched
                receiver_replay["directional_cases_with_unmatched_ages"] += bool(unmatched)
                for age, result in contrast["results"].items():
                    receiver_replay["matched_cells"] += 1
                    if age:
                        receiver_replay["positive_age_cells"] += 1
                    if result["difference"][f"pure_{receiver}"]:
                        receiver_replay["changed_pure_birth_counts"] += 1
    late = {}
    for run_id, run in runs.items():
        paired_run = run["matched_quiet"]
        if run["family"] == "source" or paired_run == run_id:
            continue
        late[run_id] = {"comparator": paired_run, **compare(profiles[run_id], profiles[paired_run])}
        if run["family"].startswith("late"):
            control = runs[paired_run]["stages"]
            common = run["stages"].keys() & control.keys()
            late[run_id]["literal_same_geometry_ages"] = sorted(int(age) for age in common
                                                               if run["stages"][age]["stars"] == control[age]["stars"])
        if run["family"] == "pulse" and tuple(run["table"]) == ("P", "V") and 2 in profiles[run_id] and 2 in profiles[paired_run]:
            stages = run["stages"]
            control = runs[paired_run]["stages"]
            if stages["1"]["stars"] == control["1"]["stars"]:
                budgets[run_id] = geometric_budget(profiles[paired_run], profiles[run_id], run["input"]["roles"],
                                                   stages["1"], stages, 2)
        if run["family"] == "pulse_plus_raw_ring":
            pulse = paired_run.rsplit("/", 1)[0] + "/1"
            control = runs[pulse]["stages"]
            common = run["stages"].keys() & control.keys()
            late[run_id]["increment_from_adding_the_late_ring_to_the_pulse"] = {
                "comparator": pulse, **compare(profiles[run_id], profiles[pulse]),
                "literal_same_geometry_ages": sorted(int(age) for age in common
                                                     if run["stages"][age]["stars"] == control[age]["stars"])}
    return {"units": {"ratios": "integer sequence [later births, earlier births]; null if earlier births is zero",
                        "ball_index": "ordinary knot steps 0 through 8",
                        "birth_histogram_index": [*range(STEP_CAP + 1), "beyond_8", "unreachable"],
                        "ancestry": "grading from actual parents; each new knot votes once in one source region"},
              "run_profiles": raw_rows, "loaded_minus_quiet": feedback, "versus_passive": passive, "two_eddy": paired,
              "late_minus_quiet": late, "first_veto_birth_budgets_by_step": budgets,
              "receiver_count_summary": {"changed_pure_birth_counts": 0, **receiver_replay}, "subtracting_caps": False}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--growth", type=Path, default=ARTIFACT / "growth.json")
    parser.add_argument("--output", type=Path, default=ARTIFACT / "interaction.json")
    args = parser.parse_args()
    document = load_growth(args.growth)
    record = analyze(document)
    record["source_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    with args.growth.open("rb") as file:
        record["growth_sha256"] = file_digest(file, "sha256").hexdigest()
    record["maximum_requested_age"] = document["age_limit"]
    args.output.write_text(json.dumps(record, separators=(",", ":")) + "\n")
    histories = record["run_profiles"]
    print(f"Measured {len(histories)} histories with {sum(len(row['rows']) for row in histories.values())} scored stages; "
          f"{len(record['loaded_minus_quiet'])} source contrasts and {len(record['late_minus_quiet'])} delayed contrasts.")


if __name__ == "__main__":
    main()
