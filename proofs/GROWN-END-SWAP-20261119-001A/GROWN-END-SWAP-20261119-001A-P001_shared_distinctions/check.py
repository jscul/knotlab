"""Replay the published six-start example with the complete-round law and measure its bonds."""
from collections import Counter
from itertools import combinations, permutations
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
LAW = ROOT / "experiments/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend"
CASE = ROOT / "artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json"
sys.path.insert(0, str(LAW))
import extend as law


def replay(rows):
    system = law.C.S.from_junctions([list(s) for s in rows["start"]])
    stages = []
    new_rows = []
    for name in ("start", "current", "next"):
        if name != "start":
            before = len(system.bits_of)
            change = system.step(law.C.S.gf2(law.C.F.fewest), None)
            assert change is not None and change["new"] > 0
            new_rows.append([sorted(s) for s in system.bits_of[before:]])
        actual = [frozenset(s) for s in system.bits_of]
        assert actual == [frozenset(s) for s in rows[name]], name
        stages.append(actual)
    return stages, new_rows


def shortest(bonds, labels):
    mark = set(labels)
    return min((len(b) for b in bonds if mark.issubset(b)), default=None)


def satisfies(rows, ones):
    return all(len(ones.intersection(row)) % 2 == 0 for row in rows)


def main():
    data = json.loads(CASE.read_text())
    (start, current, following), new_rows = replay(data["a"])
    phi = dict(data["permutation"])
    now, names = law.L.table(current)
    after, next_names = law.L.table(following)
    assert sorted(phi) == sorted(phi.values()) == names
    assert {i for i in names if phi[i] != i} == {0, 2}

    def image(pair):
        return tuple(sorted(phi.get(i, i) for i in pair))

    assert all(now[pair] == now[image(pair)] for pair in combinations(names, 2))
    reading = law.reading(current)
    site_map = law.keeps_reading(phi, current, current, reading, reading)
    assert site_map == {i: i for i in (6, 7, 8, 9)}
    assert all(all(phi[x] == x for x in current[j]) for j in site_map)
    assert {x for x, owners in law.L.owners(current).items() if len(owners) == 1} == set(range(15, 21))
    assert (now[(0, 1)], now[(1, 2)]) == (3, 3)
    assert (after[(0, 1)], after[(1, 2)]) == (2, 3)
    differences = [list(pair) for pair in combinations(next_names, 2) if after[pair] != after[image(pair)]]
    assert differences == [[0, 1], [0, 3], [1, 2], [2, 3]]

    middle = (0, 1, 2, 3)
    partition = {frozenset((0, 1)), frozenset((2, 3))}
    extending = 0
    for ordering in permutations(middle):
        rename = dict(zip(middle, ordering))
        def transported(pair):
            return tuple(sorted(rename.get(x, x) for x in pair))
        assert all(value == now[transported(pair)] for pair, value in now.items())
        keeps_partition = {frozenset(rename[x] for x in part) for part in partition} == partition
        after_on_middle = all(after[pair] == after[transported(pair)] for pair in combinations(middle, 2))
        after_on_all = all(value == after[transported(pair)] for pair, value in after.items())
        assert keeps_partition == after_on_middle == after_on_all
        extending += after_on_all
    assert extending == 8

    current_bonds = [frozenset(cut) for cut in law.L.bonds(current)]
    next_bonds = [frozenset(cut) for cut in law.L.bonds(following)]
    assert frozenset((0, 1, 15, 16)) in current_bonds
    assert frozenset((0, 1, 21)) in next_bonds
    triple_sizes = [shortest(current_bonds, t) for t in ((0, 1, 15), (2, 1, 15))]
    assert triple_sizes == [4, None]
    assert satisfies(current, {0, 1}) and not satisfies(current, {1, 2})
    for rows, bonds in ((start, law.L.bonds(start)), (current, current_bonds), (following, next_bonds)):
        assert set(rows) <= {frozenset(b) for b in bonds}
        assert all(n in (1, 2) for n in Counter(x for row in rows for x in row).values())
    return {
        "sizes_in_junctions_and_distinctions": [
            [len(rows), len(law.L.owners(rows))] for rows in (start, current, following)
        ],
        "new_supports_by_round": new_rows,
        "current_pairs_verified": len(now),
        "current_live_sites_fixed_pointwise": sorted(site_map),
        "successor_pairs_verified": len(after),
        "old_pair_and_its_image": [[0, 1], [1, 2]],
        "current_distances": [3, 3],
        "successor_distances": [2, 3],
        "mismatches_under_the_same_swap_with_all_fresh_fixed": differences,
        "current_permutations_of_four_interior_names": 24,
        "extending_permutations_of_four_interior_names": extending,
        "current_least_bond_sizes_for_0_1_15_and_2_1_15": triple_sizes,
        "permutation_preserves_equations": False,
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
