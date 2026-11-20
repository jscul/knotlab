"""Check the two-parent condition directly on every source used for motion."""

from collections import Counter
from itertools import combinations
import json
from pathlib import Path

from motion_stage import growth_engine


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name


def read_source(spec):
    grown = growth_engine().grow_case(spec, 1, {"junctions": 2048, "distinctions": 8192})
    n = len(spec["sizes"])
    rows = [set(star) for star in grown["stages"]["1"]["stars"]]
    adjacent = [set() for _ in range(n)]
    for u, v in spec["meetings"]:
        adjacent[u].add(v)
        adjacent[v].add(u)
    wedges = Counter(tuple(sorted(pair)) for row in adjacent for pair in combinations(row, 2))
    children = [tuple(i for i, old in enumerate(rows[:n]) if old & child) for child in rows[n:]]
    assert grown["qualification"]["canonical"] and rows[n:]
    assert not any(len(parents) == 0 for parents in children)
    occurrences = Counter(bit for row in rows for bit in row)
    assert all(occurrences[bit] == 2 for row in rows[:n] for bit in row)
    assert all(any(occurrences[bit] == 1 for bit in row) for row in rows[n:])
    exact_pairs = Counter(parents for parents in children if len(parents) == 2) == wedges
    return dict(source_knots=n, canonical=True, old_loose_spent=True, each_child_has_loose=True,
                numbers_of_parents=dict(sorted(Counter(len(parents) for parents in children).items())),
                every_wedge_has_own_binary_child=exact_pairs and all(v == 1 for v in wedges.values()),
                larger_groups=[parents for parents in children if len(parents) > 2])


def main():
    specs = [spec for filename in ("inputs.json", "holdout.json")
             for spec in json.loads((HERE / filename).read_text())["cases"]]
    cases = {spec["id"]: read_source(spec) for spec in specs}
    assert len(cases) == 16
    assert all(c["every_wedge_has_own_binary_child"] and not c["larger_groups"] for c in cases.values())
    six = dict(id="six_cycle_first_layer_control", sizes=[4]*6,
               meetings=[[i, (i+1) % 6] for i in range(6)])
    control = read_source(six)
    assert set(control["larger_groups"]) == {(0, 2, 4), (1, 3, 5)}
    assert not control["every_wedge_has_own_binary_child"]
    result = dict(motion_sources=cases, local_first_layer_control=control)
    (DATA / "transfer_scope.json").write_text(json.dumps(result, indent=2) + "\n")
    print("All 16 motion sources meet the corrected condition. The six-cycle has two three-parent births.")


if __name__ == "__main__":
    main()
