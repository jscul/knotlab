"""Does the next ordinary growth round distinguish agreement bonds on asymmetric starts?"""

import argparse
from collections import Counter
import json
from pathlib import Path
import random
import time

from sym_growth import RESEARCH, STUDY, advance, history_graph, owner_classes, supports_of, symmetry_orders


def census_rows():
    archive = json.loads((RESEARCH / "FORBID-EDITS-20261126-001/starts.json").read_text())
    excluded = set(random.Random(1).sample(range(len(archive)), 10))
    sample = sorted(random.Random(20261127).sample([i for i in range(len(archive)) if i not in excluded], 1000))
    published = {}
    for path in sorted((STUDY / "out").glob("census_nae_[0-9].jsonl")):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            index = int(row["start"].split()[1])
            assert index not in published
            published[index] = row
    assert sample == sorted(published)
    return archive, sample, published


def survey(archive, sample, published):
    counts = Counter()
    rigid = []
    for index in sample:
        supports = supports_of(archive[index])
        knot_group, full_group = symmetry_orders(supports)
        result = advance(supports)
        row = published[index]
        assert (len(supports), len({x for support in supports for x in support})) == (
            row["round 0"]["knots"], row["round 0"]["distinctions"])
        funded = result.status == "funded"
        assert funded == isinstance(row["round 1"], dict)
        if funded:
            assert (len(result.supports), len({x for support in result.supports for x in support})) == (
                row["round 1"]["knots"], row["round 1"]["distinctions"])
        for group_name, order in (("knot_permutations", knot_group), ("full_incidence", full_group)):
            if order == 1:
                counts[group_name] += 1
                counts[group_name + "_funded"] += funded
                counts[group_name + "_funded_with_published_source_bonds"] += int(
                    funded and row["round 0"]["bonds"] > 0)
        if full_group == 1:
            rigid.append({
                "source_ordinal": index, "source": supports, "growth_status": result.status,
                "published_local_bonds_at_source": row["round 0"]["bonds"],
                "published_local_bonds_after_growth": row["round 1"]["bonds"] if funded else None,
                "birth_inputs": [b.inputs for b in result.births],
            })
    return {"starts_counted": len(sample), "counts": dict(counts), "rigid_starts": rigid}


def rigid_in_archive(archive, indices):
    from networkx.algorithms.isomorphism import GraphMatcher

    selected = []
    for i in indices:
        supports = supports_of(archive[i])
        if symmetry_orders(supports)[1] == 1:
            graph = history_graph([supports])
            check = GraphMatcher(graph, graph, node_match=lambda a, b: a["colour"] == b["colour"])
            assert sum(1 for _ in check.isomorphisms_iter()) == 1
            step = advance(supports)
            selected.append({"source_ordinal": i, "source": supports, "growth_status": step.status,
                             "birth_inputs": [b.inputs for b in step.births]})
    return {"starts_counted": len(indices), "full_incidence_asymmetric": len(selected),
            "statuses": dict(Counter(row["growth_status"] for row in selected)), "rigid_starts": selected}


def consumed(supports, step, bonds):
    """An old reading becomes readable iff it is a function of one birth's old inputs.

    Every admissible source state on those inputs permits the same nonempty
    choices of fresh values at that birth. All other births extend independently.
    """
    from ring_recount import Stage

    stage = Stage(supports)
    rows = stage.allowed_values
    input_codes = [(b, stage.group_codes(b.inputs)) for b in step.births if len(b.inputs) > 1]
    readable_at = {}
    for carrier in sorted({c for bond in bonds for c in bond}):
        mask = stage.mask(carrier)
        restricted = rows & mask
        yes = (restricted == 0) | (restricted == mask)
        read = tuple(b.knot for b, codes in input_codes if set(codes[yes]).isdisjoint(codes[~yes]))
        if read:
            readable_at[carrier] = read
    lost = {bond for bond in bonds if any(carrier in readable_at for carrier in bond)}
    return lost, readable_at


def source_orbits(supports, bonds):
    """These starts fix every knot. Pair exchanges within equal holder classes generate all renamings."""
    assert symmetry_orders(supports)[0] == 1
    exchanges = [(group[i], group[i + 1]) for group in owner_classes(supports).values()
                 for i in range(len(group) - 1)]
    seen = set()
    for bond in bonds:
        if bond in seen:
            continue
        reached = {bond}
        stack = [bond]
        while stack:
            current = stack.pop()
            for a, b in exchanges:
                rename = {a: b, b: a}
                image = tuple(sorted(tuple(sorted(rename.get(x, x) for x in c)) for c in current))
                assert image in bonds
                if image not in reached:
                    reached.add(image)
                    stack.append(image)
        seen.update(reached)
        yield reached


def select_one(index, supports, stage_bonds):
    from ring_recount import find_bonds

    step = advance(supports)
    assert step.status == "funded"
    bonds = find_bonds(supports)
    lost, readable = consumed(supports, step, bonds)
    orbit_counts = Counter()
    for orbit in source_orbits(supports, bonds):
        lost_in_orbit = orbit & lost
        if len(lost_in_orbit) == len(orbit):
            kind = "entirely_lost"
        elif not lost_in_orbit:
            kind = "entirely_kept"
        else:
            kind = "depends_on_loose_input_assignment"
        orbit_counts[kind + "_orbits"] += 1
        orbit_counts[kind + "_bonds"] += len(orbit)
        if len(orbit) == 1:
            orbit_counts[kind + "_source_fixed_bonds"] += 1
    def example(bond):
        return {
            "carriers": bond, "missing": bonds[bond],
            "read_by_new_knots": [[carrier, readable[carrier]] for carrier in bond if carrier in readable],
        }
    return {
        "source_ordinal": index, "source": supports, "symmetry_orders_knot_and_full": symmetry_orders(supports),
        "births": [{"parents": b.parents, "inputs": b.inputs, "fresh": b.fresh} for b in step.births],
        "published_local_source_bonds": stage_bonds, "full_source_bonds": len(bonds),
        "lost": len(lost), "kept": len(bonds) - len(lost), "source_orbits": dict(orbit_counts),
        "first_lost": example(min(lost)) if lost else None,
        "first_kept": example(min(set(bonds) - lost)) if len(lost) < len(bonds) else None,
    }


def selection(archive, sample, published, pilot):
    eligible = []
    for i in sample:
        row = published[i]
        supports = supports_of(archive[i])
        if isinstance(row["round 1"], dict) and symmetry_orders(supports)[0] == 1:
            eligible.append(i)
    if pilot:
        indices = eligible[::max(1, len(eligible) // 4)]
    else:
        indices = eligible
    rows = []
    for index in indices:
        row = select_one(index, supports_of(archive[index]), published[index]["round 0"]["bonds"])
        if not row["lost"]:
            for key in ("source", "births", "first_lost", "first_kept"):
                del row[key]
        rows.append(row)
    split = [r for r in rows if r["lost"] > 0 and r["kept"] > 0]
    return {
        "eligible": len(eligible), "starts_counted": len(rows),
        "sources_with_some_full_bond": sum(r["full_source_bonds"] > 0 for r in rows),
        "sources_with_published_local_source_bonds": sum(r["published_local_source_bonds"] > 0 for r in rows),
        "full_source_bonds": sum(r["full_source_bonds"] for r in rows),
        "lost": sum(r["lost"] for r in rows), "kept": sum(r["kept"] for r in rows),
        "starts_with_both_outcomes": len(split),
        "starts_with_one_loss_and_some_kept": [r["source_ordinal"] for r in split if r["lost"] == 1],
        "starts_with_one_kept_and_some_lost": [r["source_ordinal"] for r in split if r["kept"] == 1],
        "starts_with_source_orbit_split": sum(
            bool(r["source_orbits"].get("depends_on_loose_input_assignment_orbits")) for r in rows),
        "all_source_orbits": dict(sum((Counter(r["source_orbits"]) for r in rows), Counter())),
        "selection_rows": rows,
    }


def direct_controls(archive, sample, pilot):
    from ring_recount import Reading, Stage, find_bonds, scan

    # All four loss cases among the 500 funded starts fixing every knot,
    # followed by the only fully asymmetric source in the full census to grow.
    ranks = [1596, 2046, 2186, 5500, 5091]
    results = []
    for i in ranks:
        supports = supports_of(archive[i])
        step = advance(supports)
        old = find_bonds(supports)
        cases = dict(list(old.items())[:2]) if pilot else old
        after = Stage(step.supports)
        old_carriers = {carrier for bond in cases for carrier in bond}
        readers = {c: Reading(c, c, (0,) * len(c), "=") for c in old_carriers}
        detectable = {c: after.determined_at(r) for c, r in readers.items()}
        expected_lost, _ = consumed(supports, step, cases)
        found_lost = set()
        for bond, words in cases.items():
            assert after.missing([readers[c] for c in bond]) == words
            if any(detectable[c] for c in bond):
                found_lost.add(bond)
        assert found_lost == expected_lost
        record = {"source_ordinal": i, "in_frozen_sample": i in sample, "source": supports,
                  "source_orders": symmetry_orders(supports), "after_orders": symmetry_orders(step.supports),
                  "first_round_inputs": [b.inputs for b in step.births],
                  "old_bonds_checked_on_entire_grown_stage": len(cases),
                  "same_image": len(cases), "lost_by_readability": len(found_lost),
                  "old_distinction_carriers_becoming_readable": [
                      {"carrier": c, "read_at_knots": knots} for c, knots in detectable.items() if knots],
                  "first_lost": min(found_lost, default=None),
                  "first_kept": min(set(cases) - found_lost, default=None)}
        if i == 5091:
            # For the single fully asymmetric growing census start, also count the new bonds.
            new, _ = scan(after, prefix=10 if pilot else None)
            record["bonds_after_birth"] = len(new)
            record["new_bonds_needing_birth_law"] = sum(len(supports) in b.essential for b in new)
            record["new_bonds_needing_every_law"] = sum(len(b.essential) == len(step.supports) for b in new)
            record["part_of_scan"] = "first 10 readings" if pilot else "whole stage"
        results.append(record)
    return {"direct_controls": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--part", choices=("survey", "universe", "selection", "controls"), default="survey")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    archive, sample, published = census_rows()
    if args.part == "survey":
        selected = sample[::25] if args.pilot else sample
        result = survey(archive, selected, published)
    elif args.part == "universe":
        # Include the rigid held-out source to time the independent map check as well.
        indices = sorted(set(range(0, len(archive), 25)) | {5078}) if args.pilot else range(len(archive))
        result = rigid_in_archive(archive, indices)
    elif args.part == "selection":
        result = selection(archive, sample, published, args.pilot)
    else:
        result = direct_controls(archive, sample, args.pilot)
    result["seconds"] = round(time.monotonic() - started, 4)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("rigid_starts", "selection_rows")}))


if __name__ == "__main__":
    main()
