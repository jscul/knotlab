"""Compare three current observations on the complete meet-once starting census."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ANCESTOR = Path("GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds")
ARCHIVED = ROOT / "artifacts" / ANCESTOR / "census_results.json"
ARMS = ("pair_flip", "triple_minimum", "both")


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def minimum_tables(arrangement, connected, indices, arities):
    """Measure pair bond distances and triple bond cardinalities."""
    _, adjacent, _ = arrangement.holder_graph()
    universe = (1 << len(adjacent)) - 1
    shore_count = universe >> 1
    shore = mask = 0
    bonds = []
    for step in range(1, shore_count + 1):
        changed = step & -step
        shore ^= changed
        mask ^= arrangement.masks[changed.bit_length() - 1]
        if connected(shore, adjacent) and connected(universe ^ shore, adjacent):
            bonds.append(mask)
    bonds.sort(key=int.bit_count)
    assert len(bonds) == len(set(bonds))
    width = len(arrangement.labels)
    occurrences = [bytearray((len(bonds) + 7) // 8) for _ in range(width)]
    for index, mask in enumerate(bonds):
        for position in indices(mask):
            occurrences[position][index >> 3] |= 1 << (index & 7)
    columns = [int.from_bytes(raw, "little") for raw in occurrences]
    sizes = [mask.bit_count() for mask in bonds]
    tables = {}
    for arity in arities:
        table = {}
        for positions in combinations(range(width), arity):
            common = columns[positions[0]]
            for position in positions[1:]:
                common &= columns[position]
            labels = tuple(arrangement.labels[position] for position in positions)
            reading = None
            if common:
                first = (common & -common).bit_length() - 1
                reading = sizes[first] - (arity == 2)
            table[labels] = reading
        tables[arity] = table
    return tables, bonds, shore_count


def pair_flips(arrangement):
    return {(a, b): arrangement.owners[a] == arrangement.owners[b]
            for a, b in combinations(arrangement.labels, 2)}


def difference(table, image):
    for names, value in table.items():
        mapped = tuple(sorted(image[x] for x in names))
        if table[mapped] != value:
            return {"distinctions": names, "image": mapped, "readings": [value, table[mapped]]}
    return None


def exact_lifts(pairs, image, fresh_names):
    old_pairs = {key: value for key, value in pairs.items() if key[-1] < len(image)}
    failed = difference(old_pairs, image)
    if failed is not None:
        return [], failed
    return [image + fresh for fresh in permutations(fresh_names) if difference(pairs, image + fresh) is None], None


def carries_equations(arrangement, basis, image, reduce_word):
    return all(reduce_word(sum(arrangement.label_bits[image[b]] for b in support), basis) == 0
               for support in arrangement.stars)


def histogram(values):
    counts = Counter(values)
    return sorted(counts.items(), key=lambda row: -1 if row[0] is None else row[0])


def replay_controls(readings, verify):
    """Verify the two readouts from literal allowed states and minimal dual words."""
    arrangement = verify.Arrangement.parse([[0, 1, 2], [0, 1, 3]])
    tables, cuts, _ = minimum_tables(arrangement, verify.connected, verify.indices, (2, 3))
    alternate, bonds, _ = readings.bond_readings(arrangement)
    assert set(cuts) == set(bonds) and tables[2] == alternate[1]
    assert tables[3] == {triple: None if size is None else size + 1 for triple, size in alternate[2].items()}
    states = {row for row in range(1 << len(arrangement.labels))
              if all((row & support).bit_count() % 2 == 0 for support in arrangement.masks)}
    literal_flip = {(a, b): any(row ^ ((1 << a) | (1 << b)) in states for row in states)
                    for a, b in combinations(arrangement.labels, 2)}
    assert literal_flip == pair_flips(arrangement)
    assert literal_flip[0, 1] and not literal_flip[2, 3]
    assert tables[3][0, 1, 2] == 3 and tables[3][0, 2, 3] is None
    return {"supports": [[0, 1, 2], [0, 1, 3]], "allowed_states": sorted(states),
            "flippable_pairs": sorted(pair for pair, possible in literal_flip.items() if possible),
            "triple_minimum_examples": [{"distinctions": [0, 1, 2], "reading": 3},
                                        {"distinctions": [0, 2, 3], "reading": None}]}


def measure_exception(row, prior, readings, verify, law, binary):
    witness = row["witness"]
    ancestry = prior.replay_witness(law, binary, witness, row["key"][4])
    here, following = (verify.Arrangement.parse(witness[key]) for key in ("current", "next"))
    readers = (verify.connected, verify.indices)
    now, now_bonds, now_shores = minimum_tables(here, *readers, (2, 3))
    then, then_bonds, then_shores = minimum_tables(following, *readers, (2, 3))
    for tables, stage in ((now, here), (then, following)):
        native = prior.literal_table(binary, stage.stars)
        assert tables[2] == {pair: None if size == -1 else size - 1 for pair, size in native.items()}

    live_labels = set().union(*(here.stars[site] for site in here.live))
    fresh = tuple(x for x in following.labels if x not in here.owners)
    assert here.labels == tuple(range(len(here.labels))) and following.labels == here.labels + fresh
    flips = pair_flips(here)
    next_flips = pair_flips(following)
    present = {triple: value is not None for triple, value in now[3].items()}
    assert all(set(pair) <= live_labels for pair, ok in flips.items() if ok)
    basis = verify.linear_basis(here.masks)
    next_basis = verify.linear_basis(following.masks)

    exact_group = sorted(tuple(phi[x] for x in here.labels)
                         for phi in readings.all_mappings(here.labels, now[2], live_labels))
    assert len(exact_group) == len(set(exact_group))
    maps = []
    for image in exact_group:
        assert difference(now[2], image) is None and all(image[x] == x for x in live_labels)
        rejected_flip = difference(flips, image)
        rejected_triple = difference(now[3], image)
        assert rejected_flip is None
        lifts, old_pair_failure = exact_lifts(then[2], image, fresh)
        lifted_flip = [lift for lift in lifts if difference(next_flips, lift) is None]
        lifted_triple = [lift for lift in lifts if difference(then[3], lift) is None]
        same_equations = carries_equations(here, basis, image, verify.reduce_word)
        if same_equations:
            assert image + fresh in lifted_flip and image + fresh in lifted_triple
            assert carries_equations(following, next_basis, image + fresh, verify.reduce_word)
        maps.append({"images": image, "preserves": {"pair_flip": rejected_flip is None,
                                                    "triple_minimum": rejected_triple is None,
                                                    "both": rejected_flip is None and rejected_triple is None},
                     "carries_current_equations": same_equations,
                     "next_pair_lifts": [lift[len(image):] for lift in lifts],
                     "current_triple_mismatch": rejected_triple,
                     "current_triple_existence_mismatch": difference(present, image),
                     "successor_old_pair_mismatch": old_pair_failure,
                     "lifts_also_preserving_next_refinement": {
                         "pair_flip": len(lifted_flip), "triple_minimum": len(lifted_triple),
                         "both": sum(lift in lifted_triple for lift in lifted_flip),
                         "equations": sum(carries_equations(following, next_basis, lift, verify.reduce_word)
                                          for lift in lifts)}})
    assert ancestry["complete_old_map"] in [list(row["images"]) for row in maps if not row["next_pair_lifts"]]

    groups = {}
    for arm in ("pair_table", *ARMS):
        eligible = [i for i, item in enumerate(maps) if arm == "pair_table" or item["preserves"][arm]]
        extend = [i for i in eligible if maps[i]["next_pair_lifts"]]
        assert eligible and extend and len(eligible) % len(extend) == 0
        for group in (eligible, extend):
            images = {maps[i]["images"] for i in group}
            assert tuple(here.labels) in images
            assert all(tuple(b[i] for i in a) in images for a in images for b in images)
        groups[arm] = {"order": len(eligible), "extension_subgroup_order": len(extend),
                       "nonextending_maps": len(eligible) - len(extend),
                       "equation_preserving_current_maps": sum(maps[i]["carries_current_equations"] for i in eligible),
                       "eligible_map_indices": eligible, "extending_map_indices": extend}

    return {"stage_key": row["key"], "literal_witness": witness, "law_replay": ancestry["junctions_and_width_by_age"],
            "live_support_distinctions": sorted(live_labels), "successor_fresh_distinctions": fresh,
            "current_shores_checked": now_shores, "successor_shores_checked": then_shores,
            "current_bonds": len(now_bonds), "successor_bonds": len(then_bonds),
            "pair_table_entries": [len(now[2]), len(then[2])],
            "triple_minimum_counts": histogram(now[3].values()),
            "successor_triple_minimum_counts": histogram(then[3].values()),
            "current_true_pair_flips": sorted(pair for pair, ok in flips.items() if ok),
            "full_stabilizers": groups, "all_current_pair_maps": maps}


def analyse(ledger_path, binary):
    archive = ARCHIVED.read_bytes()
    replay = ledger_path.read_bytes()
    assert replay == archive, "the complete starting census did not reproduce its archived ledger"
    ledger = json.loads(replay)
    prior = load(ROOT / "experiments" / ANCESTOR / "census.py", "previous_census")
    readings = load(ROOT / "experiments" / ANCESTOR / "readings.py", "previous_readings")
    import verify  # The committed verify.py imported by previous_readings.
    control = replay_controls(readings, verify)
    totals = ledger["summary"]["admissible"]
    assert totals["starts"] == 33_430 and totals["total"]["stages"] == 30_189
    failed = [row for row in ledger["stages"] if row["key"][3] and row["counts"].get("failure")]
    assert len(failed) == totals["total"]["failure"] == 2
    assert all(row["counts"]["failure"] == 1 for row in failed)
    law = prior.production_law()
    exceptions = [measure_exception(row, prior, readings, verify, law, binary) for row in failed]
    stages = totals["total"]["stages"]
    summaries = {}
    for arm in ("pair_table", *ARMS):
        failures = sum(bool(item["full_stabilizers"][arm]["nonextending_maps"]) for item in exceptions)
        summaries[arm] = {"tested_stages": stages, "passing_stages": stages - failures,
                          "failing_stages": failures, "unresolved_stages": 0,
                          "inherited_positive_stages": stages - len(exceptions), "directly_retested_stages": len(exceptions)}
    return {"freeze": "324a407ca", "starting_width_bound": 15, "current_junction_bound": 16,
            "admissible_starts": totals["starts"],
            "units": {"pairs": "minimum common bond cardinality minus one", "triples": "minimum common bond cardinality",
                      "undefined": None},
            "positive_ages": sorted(map(int, totals["stages_by_age"])),
            "archived_and_replayed_ledger_sha256": sha256(archive).hexdigest(),
            "summaries": summaries, "exact_exceptions": exceptions, "literal_observation_control": control}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("replayed_baseline", type=Path)
    parser.add_argument("baseline_binary", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyse(args.replayed_baseline, args.baseline_binary), indent=2))


if __name__ == "__main__":
    main()
