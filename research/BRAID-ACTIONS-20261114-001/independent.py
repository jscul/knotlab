"""Independent finite algebra, public-wiring and memory checks.

No producer is imported, no program is fitted, and no oriented braid formula
is a target.  Six raw one-hot Boolean ASTs define each proposed move.  Reader
plans depend only on those frozen moves and the public descriptors; the
receiver sees the physical packet, public wiring and eventual port only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PAIRS = tuple(product(range(3), repeat=2))
RELATIONS = tuple(range(512))
TRIPLES = tuple(product(range(3), repeat=3))


def _bit(value: Any) -> int:
    if type(value) not in (int, bool) or value not in (0, 1):
        raise ValueError("expected an actual Boolean bit")
    return int(value)


def _ast(node: Any, arity: int) -> tuple:
    if not isinstance(node, (list, tuple)) or not node:
        raise ValueError("expected an atomic Boolean expression")
    operation = node[0]
    if operation == "const" and len(node) == 2:
        return operation, _bit(node[1])
    if operation == "input" and len(node) == 2:
        if type(node[1]) is not int or not 0 <= node[1] < arity:
            raise ValueError("expression reads an undeclared input")
        return operation, node[1]
    if operation == "NOT" and len(node) == 2:
        return operation, _ast(node[1], arity)
    if operation in ("AND", "OR", "XOR") and len(node) == 3:
        return operation, _ast(node[1], arity), _ast(node[2], arity)
    raise ValueError("unknown or malformed atomic instruction")


def _eval(expression: tuple, inputs: Sequence[int]) -> int:
    operation = expression[0]
    if operation == "const":
        return expression[1]
    if operation == "input":
        return inputs[expression[1]]
    left = _eval(expression[1], inputs)
    if operation == "NOT":
        return 1 - left
    right = _eval(expression[2], inputs)
    if operation == "AND":
        return left & right
    if operation == "OR":
        return left | right
    return left ^ right


def gate_count(expression: tuple) -> int:
    """Tree cost: repeated operands and separate outputs are charged again."""
    if expression[0] in ("const", "input"):
        return 0
    return 1 + sum(gate_count(child) for child in expression[1:])


def _one_hot(pair: tuple[int, int]) -> tuple[int, ...]:
    return tuple(int(pair[0] == label) for label in range(3)) + tuple(int(pair[1] == label) for label in range(3))


def _program(expressions: Sequence) -> tuple[tuple, ...]:
    if len(expressions) != 6:
        raise ValueError("a move must have six output predicates")
    parsed = tuple(_ast(expression, 6) for expression in expressions)
    if any(gate_count(expression) > 5 for expression in parsed):
        raise ValueError("a move predicate exceeds the five-gate budget")
    return parsed


def _map_from_program(expressions: tuple[tuple, ...]) -> tuple[tuple[int, int], ...]:
    result = []
    for pair in PAIRS:
        bits = tuple(_eval(expression, _one_hot(pair)) for expression in expressions)
        if sum(bits[:3]) != 1 or sum(bits[3:]) != 1:
            raise ValueError("move output is not two valid one-hot labels")
        result.append((bits[:3].index(1), bits[3:].index(1)))
    return tuple(result)


def compile_moves(data: Mapping) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...], dict]:
    if data.get("schema_version") != 1:
        raise ValueError("expected moves schema_version 1")
    forward, inverse = _program(data["forward"]), _program(data["inverse"])
    return _map_from_program(forward), _map_from_program(inverse), {
        "forward_predicate_gates": tuple(gate_count(expression) for expression in forward),
        "inverse_predicate_gates": tuple(gate_count(expression) for expression in inverse),
        "execution": "raw six-input one-hot ASTs; no inferred output predicates"}


def _apply(mapping: tuple, pair: tuple[int, int]) -> tuple[int, int]:
    return mapping[3 * pair[0] + pair[1]]


def _on_triple(mapping: tuple, triple: tuple[int, int, int], place: int) -> tuple[int, int, int]:
    values = list(triple)
    values[place:place + 2] = _apply(mapping, tuple(values[place:place + 2]))
    return tuple(values)


def _algebra_maps(forward: tuple, inverse: tuple) -> dict:
    bijective = len(set(forward)) == 9
    left_nondegenerate = all(len({forward[3 * x + y][0] for y in range(3)}) == 3 for x in range(3))
    right_nondegenerate = all(len({forward[3 * x + y][1] for x in range(3)}) == 3 for y in range(3))
    dependence = []
    for coordinate in (0, 1):
        depends_x = any(forward[3 * x + y][coordinate] != forward[3 * other + y][coordinate]
                        for y, x, other in product(range(3), repeat=3))
        depends_y = any(forward[3 * x + y][coordinate] != forward[3 * x + other][coordinate]
                        for x, y, other in product(range(3), repeat=3))
        dependence.append((depends_x, depends_y))
    square_changed = [pair for pair in PAIRS if _apply(forward, _apply(forward, pair)) != pair]
    inverse_left = [pair for pair in PAIRS if _apply(inverse, _apply(forward, pair)) != pair]
    inverse_right = [pair for pair in PAIRS if _apply(forward, _apply(inverse, pair)) != pair]
    braid_rows = []
    for triple in TRIPLES:
        left = right = triple
        for place in (0, 1, 0):
            left = _on_triple(forward, left, place)
        for place in (1, 0, 1):
            right = _on_triple(forward, right, place)
        braid_rows.append({"input": triple, "left": left, "right": right,
                           "split": "heldout" if len(set(triple)) == 3 else "train",
                           "pass": left == right})
    training = [row for row in braid_rows if row["split"] == "train"]
    heldout = [row for row in braid_rows if row["split"] == "heldout"]
    mixed = any(x and y for x, y in dependence)
    structural = bijective and left_nondegenerate and right_nondegenerate and mixed and bool(square_changed)
    return {"bijective": bijective, "left_nondegenerate": left_nondegenerate,
            "right_nondegenerate": right_nondegenerate, "coordinate_dependence_xy": dependence,
            "at_least_one_mixed_output": mixed, "square_is_identity": not square_changed,
            "square_changed_pairs": square_changed,
            "inverse_after_forward_failures": inverse_left, "forward_after_inverse_failures": inverse_right,
            "inverse_both_orders": not inverse_left and not inverse_right,
            "braid_train": {"correct": sum(row["pass"] for row in training), "total": len(training)},
            "braid_heldout": {"correct": sum(row["pass"] for row in heldout), "total": len(heldout)},
            "braid_all": all(row["pass"] for row in braid_rows), "braid_rows": braid_rows,
            "structural_goal": structural,
            "complete_algebra_gate": structural and not inverse_left and not inverse_right and all(row["pass"] for row in braid_rows)}


def algebra(moves: Mapping) -> dict:
    forward, inverse, costs = compile_moves(moves)
    return {**_algebra_maps(forward, inverse), **costs, "forward_map": forward, "inverse_map": inverse}


@dataclass(frozen=True)
class Policy:
    forward: tuple
    inverse: tuple
    aggregate_initial: int
    aggregate: tuple[int, ...]
    reuse_initial: int
    reuse: tuple[int, ...]
    digest: str
    aggregate_gates: int
    reuse_gates: int


def compile_checkpoint(data: Mapping | Policy) -> Policy:
    if isinstance(data, Policy):
        return data
    if "checkpoint" in data:
        data = data["checkpoint"]
    if data.get("schema_version") != 1:
        raise ValueError("expected combined schema_version 1")
    forward, inverse, _ = compile_moves(data["moves"])
    components = []
    for name in ("aggregate", "reuse"):
        record = data["reader"][name]
        expression = _ast(record["expr"], 3)
        table = tuple(_eval(expression, tuple((address >> index) & 1 for index in range(3)))
                      for address in range(8))
        truth = sum(value << index for index, value in enumerate(table))
        if type(record["truth_mask"]) is not int or truth != record["truth_mask"]:
            raise ValueError(f"{name} truth mask differs from the atomic expression")
        components.extend((_bit(record["initial"]), table, gate_count(expression)))
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return Policy(forward, inverse, components[0], components[1], components[3], components[4], digest,
                  components[2], components[5])


def _descriptor(descriptor: Sequence[int]) -> tuple[int, int, int]:
    if len(descriptor) != 3:
        raise ValueError("a public descriptor is (phase,first,second)")
    phase, first, second = descriptor
    if (type(phase) is not int or phase not in (0, 1) or type(first) is not int or first not in range(3)
            or type(second) is not int or second not in (-1, 0, 1, 2)):
        raise ValueError("invalid public coordinate predicate")
    return phase, first, second


def _menu(menu: Sequence[Sequence[int]]) -> tuple[tuple[int, int, int], ...]:
    if len(menu) != 9:
        raise ValueError("a menu contains exactly nine reader ports")
    return tuple(_descriptor(descriptor) for descriptor in menu)


def _relation(relation: Any) -> int:
    if type(relation) is not int or not 0 <= relation < 512:
        raise ValueError("a relation is exactly nine membership bits")
    return relation


def image(relation: int, mapping: tuple) -> int:
    relation = _relation(relation)
    result = 0
    for index, pair in enumerate(PAIRS):
        if relation & (1 << index):
            target = _apply(mapping, pair)
            result |= 1 << (3 * target[0] + target[1])
    return result


@lru_cache(maxsize=None)
def _reach(policy: Policy, descriptor: tuple[int, int, int]) -> tuple[int, ...]:
    phase, first, second = descriptor
    result = []
    for crossed in PAIRS:
        pair = _apply(policy.inverse, crossed) if phase else crossed
        result.append(int(pair[0] == first and (second == -1 or pair[1] == second)))
    return tuple(result)


def oracle(checkpoint: Mapping | Policy, relation: int, descriptor: Sequence[int]) -> int:
    """Enumerate original allowed pairs; phase1's intended undo reads them directly.

    Current reads use the proposed forward map, for which no oriented formula
    is prescribed.  Undo is checked against the original relation rather than
    trusting the proposed inverse to define its own correct answer.
    """
    policy = compile_checkpoint(checkpoint)
    relation = _relation(relation)
    phase, first, second = _descriptor(descriptor)
    for index, pair in enumerate(PAIRS):
        if relation & (1 << index):
            observed = pair if phase else _apply(policy.forward, pair)
            if observed[0] == first and (second == -1 or observed[1] == second):
                return 1
    return 0


@lru_cache(maxsize=None)
def _plan(policy: Policy, menu: tuple) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    """Cache only public wiring; no relation value appears in this key."""
    bindings, representatives = [], []
    for descriptor in menu:
        reach = _reach(policy, descriptor)
        chosen = None
        for index, earlier in enumerate(representatives):
            state = policy.reuse_initial
            for old_bit, new_bit in zip(earlier, reach):
                state = policy.reuse[state | (old_bit << 1) | (new_bit << 2)]
            if state:
                chosen = index
                break
        if chosen is None:
            chosen = len(representatives)
            representatives.append(reach)
        bindings.append(chosen)
    return tuple(bindings), tuple(representatives)


def public_plan(checkpoint: Mapping | Policy, menu: Sequence[Sequence[int]]) -> dict:
    policy = compile_checkpoint(checkpoint)
    menu = _menu(menu)
    bindings, representatives = _plan(policy, menu)
    return {"bindings": bindings, "representative_reaches": representatives, "physical_bits": len(representatives)}


def packet(checkpoint: Mapping | Policy, relation: int, menu: Sequence[Sequence[int]]) -> tuple[int, ...]:
    policy = compile_checkpoint(checkpoint)
    menu = _menu(menu)
    _, representatives = _plan(policy, menu)  # Chosen before source values enter.
    crossed = image(relation, policy.forward)
    result = []
    for reach in representatives:
        state = policy.aggregate_initial
        for cell in range(9):
            state = policy.aggregate[state | (((crossed >> cell) & 1) << 1) | (reach[cell] << 2)]
        result.append(state)
    return tuple(result)


def decode(checkpoint: Mapping | Policy, physical_packet: Sequence[int],
           menu: Sequence[Sequence[int]], eventual_port: int) -> int:
    """Only the physical bits, public wiring and eventual port are available."""
    policy = compile_checkpoint(checkpoint)
    menu = _menu(menu)
    bindings, representatives = _plan(policy, menu)
    if (not isinstance(physical_packet, (tuple, list))
            or len(physical_packet) != len(representatives)):
        raise ValueError("physical packet length disagrees with public wiring")
    values = tuple(_bit(value) for value in physical_packet)
    if type(eventual_port) is not int or not 0 <= eventual_port < 9:
        raise ValueError("the eventual port is in 0..8")
    return values[bindings[eventual_port]]


def _padded(descriptors: Sequence[tuple[int, int, int]]) -> tuple:
    return tuple(descriptors[index % len(descriptors)] for index in range(9))


TRAIN_PORTS = tuple(product((0, 1), (0, 1), (-1, 0, 1)))
TRAIN_WIRINGS = frozenset(
    {_padded((port,)) for port in TRAIN_PORTS}
    | {_padded((left, right)) for left, right in product(TRAIN_PORTS, repeat=2) if left != right}
    | {_padded((TRAIN_PORTS[index], TRAIN_PORTS[(index + 1) % 12], TRAIN_PORTS[(index + 5) % 12]))
       for index in range(12)}
)


def default_menus(checkpoint: Mapping | Policy) -> dict[str, tuple]:
    policy = compile_checkpoint(checkpoint)
    moved_zero = _apply(policy.forward, (0, 0))
    return {
        "one_current_cell": ((0, 0, 0),) * 9,
        "one_undo_cell": ((1, 1, 1),) * 9,
        "one_current_row": ((0, 0, -1),) * 9,
        "one_undo_row": ((1, 1, -1),) * 9,
        "two_current_cells": _padded(((0, 0, 0), (0, 0, 1))),
        "mixed_three": _padded(((0, 0, 0), (1, 0, 0), (1, 1, -1))),
        "fresh_label_two": ((0, 2, 2),) * 9,
        "all_current_cells": tuple((0, first, second) for first, second in PAIRS),
        "all_undo_cells": tuple((1, first, second) for first, second in PAIRS),
        "three_current_rows": _padded(tuple((0, first, -1) for first in range(3))),
        "three_undo_rows": _padded(tuple((1, first, -1) for first in range(3))),
        "duplicate_current_undo": _padded(((0, *moved_zero), (1, 0, 0))),
        "redundant_row": _padded(((0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, -1))),
    }


def _training_menu(menu: tuple) -> bool:
    """Exact membership in the 156 evaluated training wirings."""
    return menu in TRAIN_WIRINGS


def menu_information(checkpoint: Mapping | Policy, menu: Sequence[Sequence[int]]) -> dict:
    policy = compile_checkpoint(checkpoint)
    menu = _menu(menu)
    classes = {}
    for relation in RELATIONS:
        answers = tuple(oracle(policy, relation, descriptor) for descriptor in menu)
        classes.setdefault(answers, []).append(relation)
    required = (len(classes) - 1).bit_length()
    return {"answer_classes": len(classes), "minimum_fixed_bits": required,
            "class_sizes": sorted(len(relations) for relations in classes.values()),
            "public_read_functions": len({_reach(policy, descriptor) for descriptor in menu})}


def _score_rows(policy: Policy, menu: tuple) -> dict:
    correct = total = 0
    split = {"train_even": {"correct": 0, "total": 0}, "heldout_odd": {"correct": 0, "total": 0}}
    widths = set()
    codes, signatures = {}, {}
    first_failure = None
    for relation in RELATIONS:
        physical = packet(policy, relation, menu)
        widths.add(len(physical))
        actual = tuple(decode(policy, physical, menu, port) for port in range(9))
        expected = tuple(oracle(policy, relation, descriptor) for descriptor in menu)
        row_correct = sum(left == right for left, right in zip(actual, expected))
        correct += row_correct
        total += 9
        category = "train_even" if relation.bit_count() % 2 == 0 else "heldout_odd"
        split[category]["correct"] += row_correct
        split[category]["total"] += 9
        if actual != expected and first_failure is None:
            first_failure = {"relation": relation, "packet": physical, "expected": expected, "actual": actual}
        codes.setdefault(physical, []).append(relation)
        signatures[relation] = expected
    collisions = []
    for physical, relations in codes.items():
        left = relations[0]
        right = next((relation for relation in relations if signatures[relation] != signatures[left]), None)
        if right is not None:
            collisions.append({"packet": physical, "relations": (left, right),
                               "answers": (signatures[left], signatures[right])})
    information = menu_information(policy, menu)
    return {"correct": correct, "total": total, "exact": correct == total,
            "accuracy": correct / total, "split": split, "training_menu": _training_menu(menu),
            "physical_lengths": sorted(widths), "width_chosen_before_values": len(widths) == 1,
            "packet_classes": len(codes), "collisions": collisions, "first_failure": first_failure,
            **information,
            "minimum_width": len(widths) == 1 and next(iter(widths)) == information["minimum_fixed_bits"]}


def table_recovery(checkpoint: Mapping | Policy) -> dict:
    """Identify all512 original joint tables from one frozen physical packet."""
    policy = compile_checkpoint(checkpoint)
    menu = tuple((0, first, second) for first, second in PAIRS)
    exact = prefix_exact = truncated_rejects = 0
    per_cell = 0
    widths = set()
    for relation in RELATIONS:
        physical = packet(policy, relation, menu)
        widths.add(len(physical))
        decoded_crossed = sum(decode(policy, physical, menu, cell) << cell for cell in range(9))
        reconstructed = sum(((decoded_crossed >> (3 * moved[0] + moved[1])) & 1) << index
                            for index, moved in enumerate(policy.forward))
        exact += reconstructed == relation
        try:
            decode(policy, physical[:4], menu, 0)
        except ValueError:
            truncated_rejects += 1
        # A separate physically four-bit, explicitly lossy baseline.  Its
        # receiver fills the other five crossed cells with zero.
        crossed = image(relation, policy.forward)
        four_bits = tuple((crossed >> index) & 1 for index in range(4))
        filled = sum(bit << index for index, bit in enumerate(four_bits))
        restored = sum(((filled >> (3 * moved[0] + moved[1])) & 1) << index
                       for index, moved in enumerate(policy.forward))
        prefix_exact += restored == relation
        per_cell += 9 - (restored ^ relation).bit_count()
    return {"tables": 512, "exact_identifications": exact, "physical_lengths": sorted(widths),
            "full_unknown_table_classes": 512, "minimum_fixed_bits": (512 - 1).bit_length(),
            "truncated_four_bit_packets_rejected": truncated_rejects,
            "four_bit_baseline": {"physical_bits": 4, "exact_tables": prefix_exact, "tables": 512,
                                  "correct_cells": per_cell, "cell_queries": 512 * 9},
            "unrestricted_four_bit_exact_identification_bound": (16, 512),
            "scope": "one precommitted packet; all nine delayed cell reads; public wiring supplied"}


def same_marginals(checkpoint: Mapping | Policy) -> dict:
    policy = compile_checkpoint(checkpoint)
    left, right = (1 << 0) | (1 << 4), (1 << 1) | (1 << 3)

    def counts(relation):
        rows = tuple(sum((relation >> (3 * first + second)) & 1 for second in range(3)) for first in range(3))
        columns = tuple(sum((relation >> (3 * first + second)) & 1 for first in range(3)) for second in range(3))
        return rows, columns

    descriptor = (1, 0, 0)
    menu = (descriptor,) * 9
    left_packet, right_packet = packet(policy, left, menu), packet(policy, right, menu)
    return {"relations": (left, right), "marginals": (counts(left), counts(right)),
            "equal_marginals": counts(left) == counts(right), "query": descriptor,
            "true_answers": (oracle(policy, left, descriptor), oracle(policy, right, descriptor)),
            "packets": (left_packet, right_packet),
            "decoded": (decode(policy, left_packet, menu, 0), decode(policy, right_packet, menu, 0))}


def rewiring_check(checkpoint: Mapping | Policy) -> dict:
    """Hold every relation fixed and transpose only two public cell wires."""
    policy = compile_checkpoint(checkpoint)
    original = tuple((0, first, second) for first, second in PAIRS)
    changed = unchanged = new_correct = stale_correct = stale_rejects = 0
    first = None
    for first_port, second_port in combinations(range(9), 2):
        menu = list(original)
        menu[first_port], menu[second_port] = menu[second_port], menu[first_port]
        menu = tuple(menu)
        for relation in RELATIONS:
            old_packet = packet(policy, relation, original)
            new_packet = packet(policy, relation, menu)
            for port in range(9):
                old_truth, new_truth = oracle(policy, relation, original[port]), oracle(policy, relation, menu[port])
                if old_truth == new_truth:
                    unchanged += 1
                    continue
                changed += 1
                current = decode(policy, new_packet, menu, port)
                new_correct += current == new_truth
                try:
                    stale = decode(policy, old_packet, menu, port)
                    stale_correct += stale == new_truth
                except ValueError:
                    stale = None
                    stale_rejects += 1
                if first is None:
                    first = {"relation": relation, "swapped_ports": (first_port, second_port),
                             "port": port, "truth": (old_truth, new_truth),
                             "fresh_prediction": current, "stale_prediction": stale}
    return {"wire_transpositions": 36, "changed_query_cells": changed, "unchanged_query_cells": unchanged,
            "correct_after_rewiring_on_changed": new_correct, "stale_correct_on_changed": stale_correct,
            "stale_invalid_packets_on_changed": stale_rejects, "first_changed_case": first}


def verify(checkpoint: Mapping | Policy, menus: Mapping[str, Sequence] | None = None) -> dict:
    policy = compile_checkpoint(checkpoint)
    menu_map = default_menus(policy) if menus is None else {name: _menu(menu) for name, menu in menus.items()}
    move_report = _algebra_maps(policy.forward, policy.inverse)
    identity = tuple(PAIRS)
    swap = tuple((second, first) for first, second in PAIRS)
    identity_report, swap_report = _algebra_maps(identity, identity), _algebra_maps(swap, swap)
    roundtrips = sum(image(image(relation, policy.forward), policy.inverse) == relation for relation in RELATIONS)
    return {"checkpoint_digest": policy.digest, "algebra": move_report,
            "reader_gate_counts": {"aggregate": policy.aggregate_gates, "reuse": policy.reuse_gates},
            "menus": {name: {"descriptors": menu, **_score_rows(policy, menu)} for name, menu in menu_map.items()},
            "full_table_recovery": table_recovery(policy), "same_marginal_control": same_marginals(policy),
            "rewiring": rewiring_check(policy),
            "stop_and_undo": {"undo_after_move_relation_roundtrips": roundtrips, "relations": 512,
                              "identity_actor_structural_goal": identity_report["structural_goal"],
                              "swap_actor_structural_goal": swap_report["structural_goal"],
                              "stop_alone_is_not_a_noninvolutive_mixed_braid": not identity_report["structural_goal"]},
            "receiver_interface": "physical bits, same public descriptors, frozen policy, eventual port only",
            "public_cache_scope": "binding/reach cache keys contain no relation values"}


def _component(expression, initial):
    parsed = _ast(expression, 3)
    return {"initial": initial, "expr": expression,
            "truth_mask": sum(_eval(parsed, tuple((word >> bit) & 1 for bit in range(3))) << word for word in range(8))}


def _hand_moves() -> dict:
    """A supplied test fixture, not an oriented target or a learned result.

    It is built from a finite map into ordinary one-hot minterms.  Three
    two-input minterms and two ORs cost five gates per output predicate, so
    the fixture passes the same parser and budget as a fitted checkpoint.
    """
    forward = tuple((second, (2 * second - first) % 3) for first, second in PAIRS)
    inverse = tuple(((2 * first - second) % 3, first) for first, second in PAIRS)

    def predicates(mapping):
        result = []
        for coordinate in (0, 1):
            for label in range(3):
                terms = [["AND", ["input", pair[0]], ["input", 3 + pair[1]]]
                         for pair, moved in zip(PAIRS, mapping) if moved[coordinate] == label]
                assert len(terms) == 3
                result.append(["OR", terms[0], ["OR", terms[1], terms[2]]])
        return result

    return {"schema_version": 1, "encoding": "two ternary one-hot labels",
            "forward": predicates(forward), "inverse": predicates(inverse)}


def self_test() -> dict:
    assert len(TRAIN_WIRINGS) == 156
    assert all(_training_menu(_padded((port,))) for port in TRAIN_PORTS)
    assert not _training_menu(_padded(TRAIN_PORTS[:3]))
    fixture = _hand_moves()
    aggregate = ["OR", ["input", 0], ["AND", ["input", 1], ["input", 2]]]
    reuse = ["AND", ["input", 0], ["NOT", ["XOR", ["input", 1], ["input", 2]]]]
    aggregate_data, reuse_data = _component(aggregate, 0), _component(reuse, 1)
    checkpoint = {"schema_version": 1, "moves": fixture,
                  "reader": {"aggregate": aggregate_data, "reuse": reuse_data}}
    policy = compile_checkpoint(checkpoint)
    result = verify(policy)
    assert not result["menus"]["mixed_three"]["training_menu"]
    assert result["algebra"]["complete_algebra_gate"]
    assert result["algebra"]["braid_train"] == {"correct": 21, "total": 21}
    assert result["algebra"]["braid_heldout"] == {"correct": 6, "total": 6}
    assert all(row["exact"] for row in result["menus"].values())
    assert result["full_table_recovery"]["exact_identifications"] == 512
    assert result["full_table_recovery"]["four_bit_baseline"]["exact_tables"] == 16
    redundant = result["menus"]["redundant_row"]
    assert redundant["answer_classes"] == 8 and redundant["minimum_fixed_bits"] == 3
    assert redundant["physical_lengths"] == [4] and not redundant["minimum_width"]
    assert result["menus"]["duplicate_current_undo"]["physical_lengths"] == [1]
    assert result["same_marginal_control"]["equal_marginals"]
    assert result["same_marginal_control"]["true_answers"] == result["same_marginal_control"]["decoded"] == (1, 0)
    assert result["rewiring"]["correct_after_rewiring_on_changed"] == result["rewiring"]["changed_query_cells"]
    assert result["rewiring"]["stale_correct_on_changed"] == 0
    # A genuine semantic corruption with valid Boolean values, not metadata.
    wrong_data = json.loads(json.dumps(checkpoint))
    wrong_data["reader"]["aggregate"] = _component(["const", 0], 0)
    wrong = compile_checkpoint(wrong_data)
    assert not _score_rows(wrong, default_menus(wrong)["all_current_cells"])["exact"]
    physical = packet(policy, 511, default_menus(policy)["all_current_cells"])
    for malformed in (physical[:4], (511,) * 9):
        try:
            decode(policy, malformed, default_menus(policy)["all_current_cells"], 0)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid physical packet accepted")
    return {"pass": True, "fixture_is_not_a_fit_or_target": True,
            "algebra_pairs": 9, "braid_train_triples": 21, "braid_heldout_triples": 6,
            "relation_tables": 512, "menu_count": len(result["menus"]),
            "full_table_recovery": result["full_table_recovery"],
            "redundant_row": {key: redundant[key] for key in ("answer_classes", "minimum_fixed_bits", "physical_lengths")},
            "rewiring": result["rewiring"], "corrupt_reader_rejected": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--moves", type=Path, help="independently check a moves-only checkpoint")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.checkpoint and not args.moves and not args.self_test:
        parser.error("provide --checkpoint, --moves, or --self-test")
    result = {}
    if args.self_test:
        result["self_test"] = self_test()
    if args.moves:
        data = json.loads(args.moves.read_text())
        data = data.get("checkpoint", data)
        result["moves"] = algebra(data.get("moves", data))
    if args.checkpoint:
        raw = args.checkpoint.read_bytes()
        data = json.loads(raw)
        result["checkpoint_file_sha256"] = hashlib.sha256(raw).hexdigest()
        result["verification"] = verify(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
