"""Check the published incremental ring reader on new serial parity presentations."""

from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from random import Random
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_module(name, path):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


local = load_module("boundary_histories", HERE / "search.py")
ringfile, = (ROOT / "experiments/RING-READ-20261118-001B").glob("*/reader3.py")
ring = load_module("ring_incremental_comparison", ringfile)
measurefile, = (ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001H").glob("*/check_reader.py")
measure = load_module("clipped_source_bonds", measurefile)


def read_and_undo(table, permutation, top):
    """Give the reader the renamed table and translate its answer to the original names."""
    renamed = {tuple(sorted((permutation[a], permutation[b]))): d for (a, b), d in table.items()}
    inverse = {value: i for i, value in enumerate(permutation)}
    return {frozenset(inverse[x] for x in support) for support in ring.r3(renamed, top)}


def check(history):
    rows = tuple(tuple(row) for _, row in history)
    measure.oracle.replay_history(rows, tuple(range(len(rows))))
    width = 1 + max(max(row) for row in rows)
    minima, _, _ = measure.measured_short_bonds(rows, width, 6)
    assert all(3 <= x <= 6 for x in minima.values())
    seen = set()
    arm_pairs = 0
    for row in rows:
        inputs = [i for i in row if i in seen]
        outputs = [i for i in row if i not in seen]
        for a in inputs:
            for b in outputs:
                assert minima[tuple(sorted((a, b)))] == len(row)
                arm_pairs += 1
        seen.update(row)

    rng = Random(87541 + width)
    permutations = [list(range(width)), list(reversed(range(width)))]
    for _ in range(8):
        order = list(range(width))
        rng.shuffle(order)
        permutations.append(order)
    actual = {frozenset(row) for row in rows}
    comparisons = {}
    for horizon in (2, 3, 4, 5):
        table = {pair: min(minima.get(pair, 7) - 1, horizon + 1)
                 for pair in combinations(range(width), 2)}
        counts = []
        for perm in permutations:
            found = read_and_undo(table, perm, horizon + 1)
            counts.append((len(actual - found), len(found - actual)))
        comparisons[horizon] = {"missing_and_extra_junctions_by_relabeling": counts,
                                "exact_relabelings": counts.count((0, 0))}
    return {"width": width, "sites": len(rows), "largest_ordinary_arity": max(map(len, rows)),
            "exact_cross_arm_pairs": arm_pairs, "comparisons": comparisons}


def second_shrink_tie(history):
    """Identify a single transposition and check it on every full, exact entry."""
    minima, _, _ = local.measure(history, independent=True)
    full = {pair: k - 1 for pair, k in minima.items()}
    original = list(range(27))
    swapped = original.copy()
    swapped[0], swapped[24] = 24, 0
    actual = {frozenset(row) for _, row in history}
    exterior = frozenset(i for i in original if sum(i in row for row in actual) == 1)
    assert exterior == {21, 22, 24, 25, 26}
    caps = {frozenset({10, 16, 19, 21, 22}), frozenset({14, 18, 23, 25, 26})}
    stages = {}
    for horizon in (4, 5, max(full.values())):
        table = {pair: min(d, horizon + 1) for pair, d in full.items()}
        answers = [read_and_undo(table, permutation, horizon + 1)
                   for permutation in (original, swapped)]
        assert answers[0] == actual or horizon > 5
        assert exterior in answers[1] and not caps & answers[1]
        stages[horizon] = [{"missing": sorted(sorted(x) for x in actual - found),
                            "extra": sorted(sorted(x) for x in found - actual)} for found in answers]
    return {"transposition": [0, 24], "exact_entries": len(full), "maximum_D": max(full.values()),
            "exterior_bond": sorted(exterior), "five_place_caps": sorted(sorted(x) for x in caps),
            "changes_under_identity_and_transposition": stages}


def all_fixtures():
    for name, parents, outputs in local.PLANS:
        history = local.grow(local.SEED, parents, outputs)
        yield name + "_before", history[:-1]
        yield name + "_after", history
    history = local.grow(local.SEED, local.PLANS[0][1], local.PLANS[0][2])
    yield "connected_live_extension", local.grow(history, *local.CONNECTED)
    source = json.loads((HERE / "frontier.json").read_bytes())
    for label, rows in (("second_shrink", source["closure"]["first_histories_by_shrinking_joins"]["2"]),
                        ("sharp_D4", source["sharp_distance_four"]["junction_supports"])):
        yield label, tuple((str(i), tuple(row)) for i, row in enumerate(rows))


if __name__ == "__main__":
    fixtures = dict(all_fixtures())
    result = {"reader_file_sha256": hashlib.sha256(ringfile.read_bytes()).hexdigest(),
              "fixtures": {name: check(rows) for name, rows in fixtures.items()},
              "single_swap": second_shrink_tie(fixtures["second_shrink"])}
    print(json.dumps(result, indent=2))
