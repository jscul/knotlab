"""Stage and history symmetries of the grown ring and the three-valued image."""

import argparse
from collections import Counter
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
import time

from sym_growth import EARLIER, RING, STUDY, check_maps, distinction_maps, extendible_maps, history


PAIRS = ((1, 5), (2, 3), (0, 4))


def all_pairings(places):
    if not places:
        yield ()
        return
    a = places[0]
    for j in range(1, len(places)):
        for rest in all_pairings(places[1:j] + places[j + 1:]):
            yield ((a, places[j]),) + rest


def allowed_states(supports):
    return [word for word in product((0, 1), repeat=7)
            if all(len({word[x] for x in support}) == 2 for support in supports)]


def triple(word, pairs, ref):
    return tuple(0 if word[a] != word[b] else 1 if word[a] == ref else 2 for a, b in pairs)


def pair_counts(image):
    return [len({(t[i], t[j]) for t in image}) for i, j in combinations(range(3), 2)]


def count_ternary(supports, pilot):
    group = list(distinction_maps(supports))
    all_allowed = allowed_states(supports)
    deletions = [allowed_states(supports[:i] + supports[i + 1:]) for i in range(len(supports))]
    def read(words, pairs, ref):
        return {triple(w, pairs, w[ref]) for w in words}
    image = read(all_allowed, PAIRS, 6)
    removed = [read(words, PAIRS, 6) for words in deletions]
    external = {triple(w, PAIRS, a) for w in all_allowed for a in (0, 1)}
    rows = []
    for ref in ([6] if pilot else range(7)):
        others = tuple(i for i in range(7) if i != ref)
        for pairs in all_pairings(others):
            current = read(all_allowed, pairs, ref)
            deleting = [len(read(words, pairs, ref)) for words in deletions]
            equivariant = all(g[ref] == ref and {tuple(sorted((g[a], g[b]))) for a, b in pairs}
                              == set(pairs) for g in group)
            rows.append({"reference": ref, "pairs": pairs, "size": len(current),
                         "pairs_free": pair_counts(current) == [9, 9, 9],
                         "each_law_essential": all(size > len(current) for size in deleting),
                         "pairing_and_reference_fixed": equivariant})
    binary = []
    for j in range(3):
        def coarsen(t):
            return tuple(int(t[i] == 1 if i == j else t[i] != 0) for i in range(3))
        binary_image = {coarsen(t) for t in image}
        binary.append({"pair_receiving_fresh": PAIRS[j],
                       "missing": sorted(set(product((0, 1), repeat=3)) - binary_image),
                       "deleted_image_sizes": [len({coarsen(t) for t in r}) for r in removed]})
    result = {
        "stage_states": len(all_allowed), "ternary_order": PAIRS,
        "ternary_labels": ["apart", "agree with reference", "agree against reference"],
        "image": sorted(image), "pairs": pair_counts(image), "deleted_image_sizes": [len(r) for r in removed],
        "new_triples_with_each_deletion": [sorted(r - image) for r in removed],
        "three_binary_bonds": binary,
        "unrefined_binary_pairs": len({tuple(ti != 0 for ti in t) for t in image}),
        "independent_free_reference_on_grown_stage": {"triples": len(external),
                                                     "same_as_birth_deletion": external == removed[-1],
                                                     "added_to_image": sorted(external - image)},
        "all_laws_removed": len(read(allowed_states(()), PAIRS, 6)),
        "all_source_renamings_preserve_ternary_image": all(
            {tuple(t[i] for i in p) for t in image} == image for p in permutations(range(3))),
        "pairings_tested": len(rows),
        "pairing_and_reference_fixed": [r for r in rows if r["pairing_and_reference_fixed"]],
        "pairings_with_ternary_k1_k2_k3": sum(r["pairs_free"] and 0 < r["size"] < 27 for r in rows),
        "pairings_with_ternary_k1_k2_k3_and_each_law_essential":
            sum(r["pairs_free"] and 0 < r["size"] < 27 and r["each_law_essential"] for r in rows),
        "coverage": "one reference and a perfect pairing of the remaining six identities",
    }
    raw = json.loads((STUDY / "out/symmetry.json").read_text())["P1.4 three-valued"]
    assert [list(t) for t in sorted(set(product(range(3), repeat=3)) - image)] == raw["missing"]
    assert result["pairs"] == raw["pairs (of 9)"]
    assert result["deleted_image_sizes"] == raw["with each law removed"]
    assert len(image) == raw["triples"] and result["all_source_renamings_preserve_ternary_image"]
    return result


def stages_and_trials(stages, births, pilot):
    source_group = list(distinction_maps(stages[0]))
    fixed = []
    earlier = json.loads((EARLIER / "carrier_birth.json").read_text())
    archived = [earlier["source"]["supports"]] + [r["supports"] for r in earlier["with_birth_reading"]]
    assert archived == [[list(s) for s in stage] for stage in stages[:len(archived)]]
    for n, stage in enumerate(stages):
        family = {frozenset(s) for s in stage}
        index = {frozenset(s): k for k, s in enumerate(stage)}
        holds = 0
        records_preserved = 0
        for g in source_group:
            moved = [frozenset(g.get(x, x) for x in s) for s in stage]
            if set(moved) != family:
                continue
            holds += 1
            knot_names = [index[s] for s in moved]
            step = {b.knot: b for b in births[n - 1]} if n else {}
            if all(knot_names[k] in step
                   and set(step[knot_names[k]].parents) == {knot_names[x] for x in b.parents}
                   and set(step[knot_names[k]].inputs) == {g.get(x, x) for x in b.inputs}
                   and set(step[knot_names[k]].fresh) == {g.get(x, x) for x in b.fresh}
                   and step[knot_names[k]].demand == b.demand for k, b in step.items()):
                records_preserved += 1
        fixed.append({"round": n, "knots": len(stage), "distinctions": len(set().union(*map(set, stage))),
                      "start_maps_fix_stage": holds,
                      "start_maps_preserve_round_birth_records": records_preserved,
                      "births_using_a_source_distinction": sum(
                          any(x < 6 for x in b.inputs) for b in births[n-1]) if n else 0})
    assert len(source_group) == 6
    assert all(r["start_maps_fix_stage"] == r["start_maps_preserve_round_birth_records"] == 6 for r in fixed)
    relabelled = []
    rng = random.Random(20261127)
    for _ in range(1 if pilot else 3):
        names = list(range(6))
        rng.shuffle(names)
        rename = dict(enumerate(x + 10 for x in names))
        order = list(range(3))
        rng.shuffle(order)
        supports, steps = check_maps(RING, order, rename, len(births))
        assert all(supports) and all(steps)
        relabelled.append({"start_renaming": rename, "knot_order": order,
                           "supports_at_every_round": supports, "parent_input_fresh_and_demand_at_every_birth": steps})
    return {"stages": fixed, "relabellings": relabelled, "checked_earlier_supports_through_round": len(archived) - 1}


def transform(carriers, words, mapping):
    reordered = sorted((tuple(sorted(mapping.get(x, x) for x in carrier)), i)
                       for i, carrier in enumerate(carriers))
    transformed = tuple(c for c, _ in reordered)
    transformed_words = tuple(sorted("".join(word[i] for _, i in reordered) for word in words))
    return transformed, transformed_words


def orbits(bonds, group):
    seen = set()
    sizes = Counter()
    fixed = []
    for carriers, words in bonds.items():
        if carriers in seen:
            continue
        orbit = set()
        for g in group:
            mapped, image = transform(carriers, words, g)
            assert bonds.get(mapped) == image
            orbit.add(mapped)
        assert not (seen & orbit)
        sizes[len(orbit)] += 1
        if len(orbit) == 1:
            fixed.append(carriers)
        seen.update(orbit)
    assert len(seen) == len(bonds)
    return {"size_to_number_of_orbits": dict(sorted(sizes.items())), "fixed_count": len(fixed),
            "fixed": sorted(fixed)}


def orbit_results(stages, pilot):
    from ring_recount import find_bonds
    from sym_selection import consumed
    from sym_growth import advance

    raw = json.loads((STUDY / "out/symmetry.json").read_text())
    post = json.loads((STUDY / "post/chain_and_orbits.json").read_text())
    source_group = list(distinction_maps(stages[0]))
    results = []
    for t in ((1,) if pilot else (1, 2, 3)):
        bonds = find_bonds(stages[t])
        full_group = list(distinction_maps(stages[t]))
        start = orbits(bonds, source_group)
        whole = orbits(bonds, full_group)
        key = lambda histogram: {int(k): v for k, v in histogram.items()}
        assert start["size_to_number_of_orbits"] == key(raw["rounds"][t]["orbit sizes"])
        assert whole["size_to_number_of_orbits"] == key(post[f"round {t}"]["orbit sizes"])
        assert len(full_group) == post[f"round {t}"]["symmetries"]
        future = []
        candidates = full_group
        for u in range(t, len(stages)):
            candidates = extendible_maps(stages[:u+1], candidates)
            assert candidates
            future.append({"through_round": u, "extendible_stage_symmetries": len(candidates),
                           "orbits": orbits(bonds, candidates)})
        later = advance(stages[t])
        lost, read_at = consumed(stages[t], later, bonds)
        affected = []
        seen_lost = set()
        for carriers in sorted(lost):
            if carriers in seen_lost:
                continue
            orbit = {transform(carriers, bonds[carriers], g)[0] for g in full_group}
            lost_portion = orbit & lost
            seen_lost.update(lost_portion)
            affected.append({"orbit_size": len(orbit), "lost": len(lost_portion),
                             "lost_example": min(lost_portion), "kept_example": min(orbit-lost, default=None)})
        results.append({"round": t, "bonds": len(bonds), "start_symmetries": start,
                        "start_fixed_on_born_part": sum(
                            all(x >= 6 for carrier in bond for x in carrier) for bond in start["fixed"]),
                        "stage_symmetry_order": len(full_group), "stage_symmetries": whole,
                        "with_more_growth": future, "lost_at_next_round": len(lost),
                        "old_bond_carriers_becoming_readable":
                            [{"carrier": c, "births": knots, "stage_equivalents":
                              sorted({tuple(sorted(g[x] for x in c)) for g in full_group})}
                             for c, knots in sorted(read_at.items())],
                        "stage_orbits_with_some_loss": affected})
    return results


def orbit_cost(stages):
    from ring_recount import Stage, scan

    started = time.monotonic()
    group = list(distinction_maps(stages[3]))
    cohort, _ = scan(Stage(stages[3]), prefix=24)
    after_scan = time.monotonic()
    kept = extendible_maps(stages, group[::8])
    return {"round_three_first_readings": 24, "bonds_in_prefix": len(cohort),
            "scan_seconds": after_scan - started, "maps_tried_through_round_six": len(group[::8]),
            "maps_extended": len(kept), "extension_seconds": time.monotonic() - after_scan}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", choices=("ternary", "growth", "orbits", "orbit-cost"), required=True)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    stages, births = history(RING, 6)
    if args.part == "ternary":
        data = count_ternary(stages[1], args.pilot)
    elif args.part == "growth":
        data = stages_and_trials(stages, births, args.pilot)
    elif args.part == "orbits":
        data = orbit_results(stages, args.pilot)
    else:
        data = orbit_cost(stages)
    result = {"part": args.part, "results": data, "seconds": round(time.monotonic() - started, 5)}
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{args.part} finished in {result['seconds']} seconds")


if __name__ == "__main__":
    main()
