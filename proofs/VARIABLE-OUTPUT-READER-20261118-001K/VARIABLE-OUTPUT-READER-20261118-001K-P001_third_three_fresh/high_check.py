"""Compare the full tables at two lawful six-place births in the same prefix."""

from collections import Counter
from functools import reduce
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from operator import xor
from pathlib import Path


PROOFS = Path(__file__).resolve().parents[2]
OLD = "VARIABLE-OUTPUT-READER-20261118-001C"
SOURCE = "VARIABLE-OUTPUT-READER-20261118-001J"
path = PROOFS / OLD / f"{OLD}-P001_triple_inverse" / "check_gluing.py"
spec = spec_from_file_location("literal_parity", path)
literal = module_from_spec(spec)
spec.loader.exec_module(literal)


def mask(bits):
    return sum(1 << bit for bit in bits)


def connected(adjacent, vertices):
    unseen = set(vertices)
    todo = [unseen.pop()]
    while todo:
        new = adjacent[todo.pop()] & unseen
        unseen.difference_update(new)
        todo.extend(new)
    return not unseen


def wired_table(rows):
    """Enumerate all shores and test both sides for graph connectivity."""
    holders, adjacent = literal.incidence(rows)
    outside = len(rows)
    adjacent.append(set())
    for sites in holders.values():
        if len(sites) == 1:
            site, = sites
            adjacent[outside].add(site)
            adjacent[site].add(outside)
    vertices = set(range(outside + 1))
    table = {}
    equations = set()
    for length in range(1, outside + 1):
        for shore in combinations(range(outside), length):
            support = reduce(xor, (mask(rows[i]) for i in shore))
            equations.add(support)
            if connected(adjacent, shore) and connected(adjacent, vertices.difference(shore)):
                size = support.bit_count()
                for pair in combinations(literal.bit_indices(support), 2):
                    table[pair] = min(size, table.get(pair, size))
    assert len(equations) == 2 ** outside - 1
    return table, equations


def compare(old, parents, fresh, other):
    rows = [*old, [*parents, *fresh]]
    events = literal.replay(rows)
    values, equations = wired_table(rows)
    holders, adjacent = literal.incidence(rows)
    dual_values = literal.scalar_table(literal.minimal_dual(rows), len(holders))
    assert values == {pair: size_minus_one + 1 for pair, size_minus_one in dual_values.items()}
    frontier = sorted(bit for bit, sites in holders.items() if len(sites) == 1)
    menu = [bits for bits in combinations(frontier, 3)
            if literal.legal_parents([holders[bit][0] for bit in bits], adjacent)]
    assert mask([*parents, *fresh]) in equations and mask([*other, *fresh]) not in equations
    cross = [values[tuple(sorted(pair))] for pair in product(parents, fresh)]
    assert cross == [6] * 9
    reading = sorted(bit for bit in range(min(fresh)) if values[bit, fresh[0]] <= 6)
    return values, {"cap_inputs": parents, "cap_outputs": fresh, "cap_input_holders": events[-1]["parents"],
                    "fresh_to_old_K_at_most_six": reading, "cross_K": cross, "eligible_triples": menu,
                    "own_cap_is_equation": True, "other_cap_is_equation": False}


def run():
    record = json.loads((PROOFS / SOURCE / f"{SOURCE}-P001_seven_to_six" / "frontier.json").read_text())
    old = record["sharp_distance_four"]["junction_supports"]
    first, second, fresh = [12, 20, 21], [12, 20, 22], [25, 26, 27]
    left, left_record = compare(old, first, fresh, second)
    right, right_record = compare(old, second, fresh, first)
    assert left == right and len(left) == 378
    assert not left_record["eligible_triples"] and not right_record["eligible_triples"]
    for selected, rival, support in ((first, second, [11, 12, 14, 21]), (second, first, [11, 12, 14, 22])):
        assert all((mask(support) & mask(row)).bit_count() % 2 == 0 for row in [*old, [*selected, *fresh]])
        assert (mask(support) & mask([*rival, *fresh])).bit_count() % 2 == 1

    # With no earlier shrink the fresh row through K=6 recovers precisely the input set.
    initial = record["closure"]["first_histories_by_shrinking_joins"]["1"]
    cap_inputs = list(initial[-1][:3])
    before = initial[:-1]
    cap_outputs = [19, 20, 21]
    positive = [*before, [*cap_inputs, *cap_outputs]]
    literal.replay(positive)
    table, _ = wired_table(positive)
    assert [i for i in range(19) if table[i, 19] <= 6] == cap_inputs
    upper = [[left[i, j] for j in range(i + 1, 28)] for i in range(27)]
    return {"prefix_junctions": old, "transition": [left_record, right_record],
            "width": 28, "sites": 12, "full_pair_readings": len(left), "differing_full_entries": 0,
            "K_upper_triangle": upper, "K_histogram": dict(sorted(Counter(left.values()).items())),
            "one_state_per_side_given_by_its_one_bits": [[11, 12, 14, 21], [11, 12, 14, 22]],
            "before_any_shrink_control": {"width": 22, "cap_inputs": cap_inputs, "fresh_bits": cap_outputs,
                                         "old_bits_with_fresh_row_K_at_most_six": cap_inputs}}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
