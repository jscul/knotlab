"""Replay the three explicit starts with the archived complete-round law and exact bonds."""

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
PREVIOUS = "EXTEND-ROUND-20261119-001A"
sys.path.insert(0, str(ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_extend")))
import extend as law


# The same four central distinctions occur in each fixture. The sites are M, A, B,
# followed by the remaining left sites and (in the eleven-site start) right sites.
STARTS = {
    6: [
        [0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 13, 14],
        [4, 6, 9, 10], [5, 6, 7, 8, 11], [7, 8, 12],
    ],
    7: [
        [0, 1, 2, 3], [0, 1, 4, 5, 6], [2, 3, 14, 15],
        [4, 7, 10, 11], [5, 6, 12], [8, 9, 13], [7, 8, 9],
    ],
    11: [
        [0, 1, 2, 3], [0, 1, 4, 5, 6], [2, 3, 10, 11, 12],
        [4, 7, 16, 17], [5, 6, 18], [8, 9, 19], [7, 8, 9],
        [10, 13, 20, 21], [11, 12, 22], [14, 15, 23], [13, 14, 15],
    ],
}


def swap(x):
    return {0: 2, 2: 0}.get(x, x)


def compare(stars):
    # No clipping, isometry cap, optimization cutoff, or tree approximation.
    table, labels = law.L.table(stars)
    mismatch = []
    for pair, distance in table.items():
        image = tuple(sorted(swap(x) for x in pair))
        if table[image] != distance:
            mismatch.append({"pair": list(pair), "image": list(image),
                             "distance": distance, "image_distance": table[image]})
    return {
        "junctions": len(stars),
        "distinctions": len(labels),
        "compared_pairs": len(table),
        "mismatches": mismatch,
        "distance_0_1": table[0, 1],
        "distance_1_2": table[1, 2],
    }


def trace_round(previous, following):
    owners = law.L.owners(previous)
    additions = []
    for star in following[len(previous):]:
        taken = sorted(star & owners.keys())
        assert all(len(owners[x]) == 1 for x in taken)
        additions.append({
            "parents": sorted(owners[x][0] for x in taken),
            "taken": taken,
            "fresh": sorted(star - owners.keys()),
        })
    return additions


def replay(size):
    start = [frozenset(star) for star in STARTS[size]]
    start_bonds = {frozenset(s) for s in law.L.bonds(start)}
    assert all(len(star) >= 3 and star in start_bonds for star in start)
    assert all(len(bond) > 1 for bond in start_bonds)
    current = law.grow1(start)
    successor = law.grow1(current)
    owners = law.L.owners(current)
    assert all(len(owners[x]) == 2 for x in (0, 1, 2, 3))
    phi = {x: swap(x) for x in sorted(owners)}
    reading = law.reading(current)
    live, loose, maximal = reading
    site_map = law.keeps_reading(phi, current, current, reading, reading)
    assert site_map == {j: j for j in live}
    assert all(all(swap(x) == x for x in current[j]) for j in live)
    initial_reading = law.reading(start)
    initial_phi = {x: swap(x) for x in law.L.owners(start)}
    initial_map = law.keeps_reading(initial_phi, start, start, initial_reading, initial_reading)
    assert (initial_map is not None) == (size == 11)

    # The A-star is physical. Its image contains exactly one of the two
    # parallel M--A distinctions, which is impossible in any cut.
    old_equations = [sum(1 << x for x in star) for star in current]
    transported = sum(1 << swap(x) for x in current[1])
    rank = law.L.rank(old_equations)
    assert law.L.rank(old_equations + [transported]) == rank + 1

    stages = {"start": start, "current": current, "next": successor}
    comparisons = {name: compare(stars) for name, stars in stages.items()}
    assert not comparisons["current"]["mismatches"]
    assert {tuple(row["pair"]) for row in comparisons["next"]["mismatches"]} == {
        (0, 1), (0, 3), (1, 2), (2, 3),
    }
    assert comparisons["next"]["distance_0_1"] == 2
    assert comparisons["next"]["distance_1_2"] == 3
    certificate = {
        "a": {key: [sorted(star) for star in stars] for key, stars in stages.items()},
        "permutation": [[x, y] for x, y in phi.items()],
    }
    summary = {
        "certificate": f"construct_{size}.json",
        "tables": comparisons,
        "rounds": [trace_round(start, current), trace_round(current, successor)],
        "start_growing_end_preserved": initial_map is not None,
        "current_reading": {
            "live": live,
            "loose": {str(j): sorted(loose[j]) for j in live},
            "maximal_common_neighbor_sets_of_size_at_least_two": sorted(
                sorted(group) for group in maximal
            ),
            "all_live_supports_fixed_pointwise": True,
        },
        "support_1_image_in_current_equation_space": False,
    }
    return certificate, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with saved files without writing")
    args = parser.parse_args()
    files, results = {}, {}
    for size in STARTS:
        certificate, results[str(size)] = replay(size)
        files[f"construct_{size}.json"] = certificate
    files["construct_results.json"] = results
    for name, payload in files.items():
        path = OUTPUT / name
        content = json.dumps(payload, indent=2) + "\n"
        if args.check:
            if path.read_text() != content:
                raise SystemExit(f"Saved result differs: {path}")
        else:
            path.write_text(content)
    print("All three lineages passed the complete old and successor table comparisons.")


if __name__ == "__main__":
    main()
