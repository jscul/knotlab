"""Exact stabilizer and extension comparisons on the four archived witnesses."""

from functools import reduce
from hashlib import sha256
from itertools import combinations
import json
from operator import xor
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
MEET_ONCE_RUN = Path("GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds")
sys.path.insert(0, str(ROOT / "experiments" / MEET_ONCE_RUN))
from readings import ARCHIVED_CASE, all_mappings, bond_readings, extension_checks  # noqa: E402
from verify import connected, cut_certificate, exact_table, indices, lineage, reading  # noqa: E402


def check_bonds(stage, span_bonds):
    _, neighbors, _ = stage.holder_graph()
    universe = (1 << len(neighbors)) - 1
    half = 1 << (len(neighbors) - 1)
    connected_bonds = {reduce(xor, (stage.masks[j] for j in indices(shore)), 0)
                       for shore in range(1, half)
                       if connected(shore, neighbors) and connected(universe ^ shore, neighbors)}
    assert set(span_bonds) == connected_bonds
    assert set(stage.masks) <= connected_bonds, "one of the named current junctions fails the parity-support gate"
    return {"shores_checked": half - 1, "bonds": len(connected_bonds),
            "ordinary_junctions": len(stage.stars), "distinctions": len(stage.labels)}


def changed(table, phi):
    for names, source in table.items():
        image = tuple(sorted(phi[x] for x in names))
        if source != (target := table[image]):
            yield {"names": names, "image": image, "value": source, "image_value": target}


def flip_table(a, bonds):
    # Flipping exactly x and y preserves every allowed state iff each row has both or neither.
    columns = {x: sum(1 << j for j, row in enumerate(a.masks) if row & a.label_bits[x]) for x in a.labels}
    bond_columns = {x: sum(1 << j for j, row in enumerate(bonds) if row & a.label_bits[x]) for x in a.labels}
    flips = {(x, y): columns[x] == columns[y] for x, y in combinations(a.labels, 2)}
    assert flips == {(x, y): bond_columns[x] == bond_columns[y] for x, y in flips}
    return flips


def classify(maps, stage, successor, records, next_pairs, flips, triples, span):
    projected = {pair: value for pair, value in next_pairs.items() if all(x in stage.owners for x in pair)}
    result = []
    for phi in maps:
        assert reading(stage, stage, phi)[1]["keeps_reading"]
        flip_mismatch = list(changed(flips, phi))
        triple_mismatch = list(changed(triples, phi))
        successor_mismatch = list(changed(projected, phi))
        can_extend, can_repair, round_match = extension_checks(stage, successor, records, next_pairs, phi)
        named_extension = {x: phi.get(x, x) for x in successor.labels}
        fixes_fresh_and_extends = next(changed(next_pairs, named_extension), None) is None
        carries_equations = all(sum(stage.label_bits[phi[x]] for x in support) in span for support in stage.stars)
        assert not successor_mismatch or not can_extend
        assert not carries_equations or can_extend
        result.append({"images": [phi[x] for x in stage.labels], "preserves_flip": not flip_mismatch,
                       "preserves_triples": not triple_mismatch, "extends_next_pair_table": can_extend,
                       "extends_with_loose_repair": can_repair, "extends_matching_new_junctions": round_match,
                       "extends_by_fixing_fresh_names": fixes_fresh_and_extends,
                       "preserves_equations": carries_equations,
                       "flip_mismatches": len(flip_mismatch), "triple_mismatches": len(triple_mismatch),
                       "old_pair_mismatches_at_successor": len(successor_mismatch),
                       "first_flip_mismatch": next(iter(flip_mismatch), None),
                       "first_triple_mismatch": next(iter(triple_mismatch), None),
                       "first_triple_existence_mismatch": next((item for item in triple_mismatch
                                                                if None in (item["value"], item["image_value"])), None),
                       "first_successor_old_pair_mismatch": next(iter(successor_mismatch), None)})
    return result


def summarize(maps):
    conditions = {"pair_stabilizer": (), "also_flip": ("preserves_flip",), "also_triples": ("preserves_triples",),
                  "also_both": ("preserves_flip", "preserves_triples")}
    outcome = {}
    for name, gates in conditions.items():
        admitted = [m for m in maps if all(m[gate] for gate in gates)]
        strict = sum(m["extends_next_pair_table"] for m in admitted)
        repair = sum(m["extends_with_loose_repair"] for m in admitted)
        equation = sum(m["preserves_equations"] for m in admitted)
        outcome[name] = {"size": len(admitted), "extends": strict, "fails": len(admitted) - strict,
                         "extends_with_loose_repair": repair, "extends_matching_new_junctions":
                             sum(m["extends_matching_new_junctions"] for m in admitted),
                         "preserves_equations": equation, "extends_without_preserving_equations": strict - equation}
    return outcome


def cut_evidence(stage, record, shores):
    def certificate(names, value):
        return (cut_certificate(stage, names, value, shores[names]) if value is not None else
                {"pair": names, "distance": None})

    return {"source": certificate(record["names"], record["value"]),
            "image": certificate(record["image"], record["image_value"])}


def least_support(stage, bonds, names):
    marked = sum(stage.label_bits[x] for x in names)
    available = [mask for mask in bonds if mask & marked == marked]
    if not available:
        return None
    smallest = min(available, key=lambda mask: (mask.bit_count(), mask))
    return [stage.labels[i] for i in indices(smallest)]


def analyse(case, source_permutation):
    current, successor, records, history = lineage(case)
    assert history["rounds"] and history["start"]["census_open_legal"]
    (_, pairs, triples), current_bonds, span = bond_readings(current)
    (_, next_pairs, _), next_bonds, _ = bond_readings(successor)
    stage_counts = {"current": check_bonds(current, current_bonds), "next": check_bonds(successor, next_bonds)}
    assert exact_table(current, 100_000)[0] == pairs
    exact_next, shores, _ = exact_table(successor, 100_000)
    assert exact_next == next_pairs
    fixed = set().union(*(current.stars[j] for j in current.live))
    maps = sorted(all_mappings(current.labels, pairs, fixed), key=lambda m: [m[x] for x in current.labels])
    assert len({tuple(m[x] for x in current.labels) for m in maps}) == len(maps)
    flips = flip_table(current, current_bonds)
    triple_sizes = {names: None if value is None else value + 1 for names, value in triples.items()}
    rows = classify(maps, current, successor, records, next_pairs, flips, triple_sizes, span)
    archived = next(m for m in rows if m["images"] == source_permutation)
    assert not archived["extends_next_pair_table"]
    identity = next(m for m in rows if m["images"] == list(current.labels))
    assert identity["preserves_flip"] and identity["preserves_triples"] and identity["extends_next_pair_table"]

    def bad_transpositions():
        for x, y in combinations(sorted(set(current.labels) - fixed), 2):
            swap = {x: y, y: x}
            phi = {z: swap.get(z, z) for z in current.labels}
            if mismatch := next(changed(pairs, phi), None):
                yield {"exchanged": (x, y), "first_pair_mismatch": mismatch}

    false_input = next(bad_transpositions())
    discrepancy = archived["first_triple_existence_mismatch"]
    query = discrepancy["names"]
    archived["minimum_bonds_for_triple_existence_mismatch"] = {
        "source": least_support(current, current_bonds, query),
        "image": least_support(current, current_bonds, discrepancy["image"])}
    query_exists = triple_sizes[query] is not None
    rejects = [i for i, m in enumerate(maps)
               if (triple_sizes[tuple(sorted(m[x] for x in query))] is not None) != query_exists]
    failed = [i for i, m in enumerate(rows) if not m["extends_next_pair_table"]]
    for row in rows:
        if mismatch := row["first_successor_old_pair_mismatch"]:
            row["decisive_next_bonds"] = cut_evidence(successor, mismatch, shores)
    return {"round_history": history, "next_round": records, "stage_counts": stage_counts,
            "fixed_live_distinctions": sorted(fixed), "current_labels": current.labels,
            "pairs_checked": len(pairs), "triples_checked": len(triples), "next_pairs_checked": len(next_pairs),
            "groups": summarize(rows), "all_maps": rows, "archived_failure": archived,
            "controls": {"identity": identity, "false_pair_table_isometry": false_input},
            "pair_flip_true_entries": [names for names, value in flips.items() if value],
            "single_triple_existence_query": {"names": query, "exists": query_exists, "rejected_map_indices": rejects,
                                              "rejects_exactly_the_failures": rejects == failed}}


def named_cases():
    source = ROOT / "artifacts" / MEET_ONCE_RUN / "reach_bound_threshold.json"
    audit = json.loads(source.read_text())["joint_minimum_audit"]
    allocations = {row["allocation_index"]: row for row in audit["failing_allocations"]}
    classes = audit["distinct_failing_presentations"]
    assert len(classes) == 3
    for classification in classes:
        index = classification["allocation_indices"][0]
        allocation = allocations[index]
        case = {age: allocation[age] for age in ("start", "current", "next")}
        assert len(case["current"]) == 12 and len(set().union(*map(set, case["current"]))) == 23
        partial = allocation["old_movable_permutation"]
        images = partial + list(range(len(partial), 23))
        yield f"meet_once_threshold_{index}", source, case, images
    source = ROOT / "artifacts" / ARCHIVED_CASE / "construct_6.json"
    archived = json.loads(source.read_text())
    yield "meet_twice_six_start", source, archived["a"], [y for _, y in sorted(archived["permutation"])]


def main():
    output = {}
    for name, source, case, images in named_cases():
        output[name] = {"source": str(source.relative_to(ROOT)), "source_sha256": sha256(source.read_bytes()).hexdigest(),
                        "explicit_stages": case, **analyse(case, images)}
    print(json.dumps({"measurement_units": {"pair": "minimum bond size minus one", "triple": "minimum bond size",
                                           "no_common_bond": None}, "cases": output}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
