"""Independent finite verification for WIRED-FOLD-20261114-001.

The oracle enumerates h in the raw records.  The policy interpreter accepts
only four Boolean inputs per expression, and independently checks every AST,
truth-mask entry and gate count.  No producer is imported and no decoder is
fitted here.  ``send`` returns only the physical tuple; ``decode`` receives
only that tuple and the eventual mask.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


NAMES = ("A", "B", "C", "D")
WORLDS = tuple(range(256))
PAIRS = tuple(combinations(range(4), 2))
ORDERS = tuple(permutations(range(4)))
MENUS = tuple(product((1, 2, 3), repeat=2))
TRAIN_PAIRS = frozenset(((0, 1), (2, 3), (0, 2), (1, 3)))
TRAIN_MENUS = frozenset(((1, 1), (2, 2), (3, 3), (1, 2), (2, 1), (1, 3), (3, 1)))
INPUT_ORDER = {
    "T": ("old", "value", "match_inlet0", "match_inlet1"),
    "F": ("state_h0", "state_h1", "first_mask_h0", "first_mask_h1"),
    "W": ("first_mask_h0", "first_mask_h1", "second_mask_h0", "second_mask_h1"),
}


def _bit(value: Any) -> int:
    if type(value) not in (int, bool) or value not in (0, 1):
        raise ValueError("expected a Boolean bit")
    return int(value)


def _mask(value: Any) -> int:
    if type(value) is not int or value not in (1, 2, 3):
        raise ValueError("a query mask must be 1, 2 or 3")
    return value


def _world(value: Any) -> int:
    if type(value) is not int or not 0 <= value < 256:
        raise ValueError("world must be an eight-bit integer")
    return value


def _expression(node: Any) -> tuple:
    if not isinstance(node, (tuple, list)) or not node:
        raise ValueError("expression must be a JSON AST")
    operation = node[0]
    if operation == "const" and len(node) == 2:
        return ("const", _bit(node[1]))
    if operation == "input" and len(node) == 2:
        if type(node[1]) is not int or not 0 <= node[1] < 4:
            raise ValueError("an expression may read only its four declared inputs")
        return ("input", node[1])
    if operation not in ("AND", "OR", "XOR", "NAND") or len(node) != 3:
        raise ValueError("unknown or malformed Boolean instruction")
    return operation, _expression(node[1]), _expression(node[2])


def _evaluate(expression: tuple, inputs: tuple[int, ...]) -> int:
    operation = expression[0]
    if operation == "const":
        return expression[1]
    if operation == "input":
        return inputs[expression[1]]
    left, right = _evaluate(expression[1], inputs), _evaluate(expression[2], inputs)
    if operation == "AND":
        return left & right
    if operation == "OR":
        return left | right
    if operation == "XOR":
        return left ^ right
    return 1 - (left & right)


def _cost(expression: tuple) -> int:
    if expression[0] in ("input", "const"):
        return 0
    # Only an identical pair of operands shares its immediate computation.
    left, right = expression[1:]
    return 1 + _cost(left) + (0 if left == right else _cost(right))


@dataclass(frozen=True)
class Policy:
    initial_bit: int
    T: tuple[int, ...]
    F: tuple[int, ...]
    W: tuple[int, ...]
    decoders: tuple[dict[int, tuple[int, ...]], dict[int, tuple[int, ...]]]
    gate_counts: tuple[int, int, int]
    digest: str


def compile_policy(checkpoint: Mapping | Policy) -> Policy:
    if isinstance(checkpoint, Policy):
        return checkpoint
    if not isinstance(checkpoint, Mapping) or checkpoint.get("schema_version") != 1:
        raise ValueError("expected checkpoint schema_version 1")
    initial = _bit(checkpoint["initial_bit"])
    if "input_bit_order" in checkpoint:
        for component, expected in INPUT_ORDER.items():
            if tuple(checkpoint["input_bit_order"].get(component, ())) != expected:
                raise ValueError(f"wrong {component} input order")
    tables, counts = [], []
    for component, limit in (("T", 4), ("F", 4), ("W", 3)):
        data = checkpoint[component]
        expression = _expression(data["expr"])
        count = _cost(expression)
        if type(data["gate_count"]) is not int or count != data["gate_count"] or count > limit:
            raise ValueError(f"incorrect or out-of-budget {component} gate count")
        table = tuple(_evaluate(expression, tuple((address >> index) & 1 for index in range(4)))
                      for address in range(16))
        truth_mask = sum(value << address for address, value in enumerate(table))
        if type(data["truth_mask"]) is not int or data["truth_mask"] != truth_mask:
            raise ValueError(f"{component} truth_mask does not match its atomic program")
        tables.append(table)
        counts.append(count)
    decoded = []
    for name, width in (("one", 1), ("two", 2)):
        rows = checkpoint["decoders"][name]
        if set(rows) != {"1", "2", "3"}:
            raise ValueError("decoder may contain only actual-mask keys 1,2,3")
        part = {}
        for mask in (1, 2, 3):
            row = rows[str(mask)]
            if not isinstance(row, (list, tuple)) or len(row) != 1 << width:
                raise ValueError("wrong number of physical packet codes in decoder")
            part[mask] = tuple(_bit(value) for value in row)
        decoded.append(part)
    digest = hashlib.sha256(json.dumps(checkpoint, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return Policy(initial, *tables, tuple(decoded), tuple(counts), digest)


def _address(values: Sequence[int]) -> int:
    return sum(value << index for index, value in enumerate(values))


def _menu(menu: Sequence[int]) -> tuple[int, int]:
    if len(menu) != 2:
        raise ValueError("the public menu has exactly two masks")
    return _mask(menu[0]), _mask(menu[1])


def _records(records: Sequence[Mapping], inlets: Sequence[Any]) -> tuple[tuple[Any, tuple[int, int]], ...]:
    if len(records) != 4 or len(inlets) != 2 or inlets[0] == inlets[1]:
        raise ValueError("four original records and two distinct inlets are required")
    result = []
    for record in records:
        if set(record) != {"endpoint", "values"} or len(record["values"]) != 2:
            raise ValueError("a raw record contains only endpoint and two values")
        endpoint = record["endpoint"]
        if type(endpoint) not in (str, int):
            raise ValueError("use opaque string or integer endpoint names")
        result.append((endpoint, tuple(_bit(value) for value in record["values"])))
    names = tuple(endpoint for endpoint, _ in result)
    if len(set(names)) != 4 or any(inlet not in names for inlet in inlets):
        raise ValueError("source names must be distinct and both inlet identities present")
    return tuple(result)


def records_for_world(world: int, *, order: Sequence[int] = (0, 1, 2, 3),
                      names: Sequence[Any] = NAMES) -> list[dict]:
    world = _world(world)
    if tuple(sorted(order)) != (0, 1, 2, 3) or len(names) != 4 or len(set(names)) != 4:
        raise ValueError("invalid source order or endpoint renaming")
    return [{"endpoint": names[index], "values": [(world >> (2 * index + h)) & 1 for h in (0, 1)]}
            for index in order]


def oracle_records(records: Sequence[Mapping], inlets: Sequence[Any], actual_mask: int) -> int:
    records = _records(records, inlets)
    actual_mask = _mask(actual_mask)
    for h in (0, 1):
        if not actual_mask & (1 << h):
            continue
        allowed = True
        for endpoint, values in records:
            if endpoint == inlets[0] or endpoint == inlets[1]:
                allowed = allowed and bool(values[h])
        if allowed:
            return 1
    return 0


def oracle(world: int, inlets: Sequence[int], actual_mask: int) -> int:
    """Enumerate h directly from the eight raw bits, without a folded column."""
    world = _world(world)
    if len(inlets) != 2 or inlets[0] == inlets[1] or any(type(index) is not int or index not in range(4) for index in inlets):
        raise ValueError("oracle inlet indices must be two different values in 0..3")
    actual_mask = _mask(actual_mask)
    for h in (0, 1):
        if actual_mask & (1 << h):
            if ((world >> (2 * inlets[0] + h)) & 1) and ((world >> (2 * inlets[1] + h)) & 1):
                return 1
    return 0


def _scan(policy: Policy, records: tuple, inlets: Sequence[Any], hide_wiring: bool = False) -> tuple[int, int]:
    states = [policy.initial_bit, policy.initial_bit]
    for endpoint, values in records:
        # These are the only uses of source and inlet identities in execution.
        match0 = 0 if hide_wiring else int(endpoint == inlets[0])
        match1 = 0 if hide_wiring else int(endpoint == inlets[1])
        for h in (0, 1):
            address = states[h] | (values[h] << 1) | (match0 << 2) | (match1 << 3)
            states[h] = policy.T[address]
    return tuple(states)


def width(policy: Mapping | Policy, menu: Sequence[int]) -> int:
    policy = compile_policy(policy)
    first, second = _menu(menu)
    return 1 + policy.W[(first & 1) | ((first >> 1) << 1) | ((second & 1) << 2) | ((second >> 1) << 3)]


def _packet(policy: Policy, states: tuple[int, int], menu: tuple[int, int], forced: int | None = None) -> tuple[int, ...]:
    size = width(policy, menu) if forced is None else forced
    if size not in (1, 2):
        raise ValueError("forced payload width must be one or two")
    if size == 2:
        return states
    first = menu[0]
    address = states[0] | (states[1] << 1) | ((first & 1) << 2) | ((first >> 1) << 3)
    return (policy.F[address],)


def send(checkpoint: Mapping | Policy, records: Sequence[Mapping], inlets: Sequence[Any],
         menu: Sequence[int], *, force_width: int | None = None, hide_wiring: bool = False) -> tuple[int, ...]:
    """Choose physical width from the menu, then scan all original records."""
    policy = compile_policy(checkpoint)
    menu = _menu(menu)
    declared_width = width(policy, menu)  # Evaluated before reading records.
    records = _records(records, inlets)
    states = _scan(policy, records, inlets, hide_wiring)
    packet = _packet(policy, states, menu, force_width)
    if force_width is None and len(packet) != declared_width:
        raise AssertionError("physical tuple length differs from pre-world choice")
    return packet


def decode(checkpoint: Mapping | Policy, packet: Sequence[int], actual_mask: int) -> int:
    """No names, source values, menu, program state, or actual-port index enter."""
    policy = compile_policy(checkpoint)
    if not isinstance(packet, (tuple, list)) or len(packet) not in (1, 2):
        raise ValueError("a packet is physically one or two bits")
    packet = tuple(_bit(bit) for bit in packet)
    return policy.decoders[len(packet) - 1][_mask(actual_mask)][_address(packet)]


def predict(checkpoint: Mapping | Policy, records: Sequence[Mapping], inlets: Sequence[Any],
            menu: Sequence[int], actual_port: int) -> int:
    if type(actual_port) is not int or actual_port not in (0, 1):
        raise ValueError("actual_port must be zero or one")
    packet = send(checkpoint, records, inlets, menu)
    return decode(checkpoint, packet, menu[actual_port])


def exact_widths_and_bounds() -> dict:
    """Exact finite information bounds, allowing unrestricted encoders.

    A chosen pair's branch column has multiplicities 144,48,48,16 among the
    256 raw worlds.  Decoder vectors give predictions at masks1,2,3.  For any
    fixed decoder, each individual world/menu may choose its best code; this
    includes encoders using irrelevant records or splitting answer classes.
    No such splitting improves on that independent maximum.  Searching all
    decoder-vector pairs is consequently an exact one-bit upper bound.
    """
    multiplicities = {column: 0 for column in range(4)}
    for world in WORLDS:
        column = sum(oracle(world, (0, 1), 1 << h) << h for h in (0, 1))
        multiplicities[column] += 1

    def bound(menus):
        best = -1
        selected = None
        for vectors in combinations(range(8), 2):
            score = 0
            for menu in menus:
                for column, count in multiplicities.items():
                    score += count * max(sum(((vector >> (mask - 1)) & 1) == int(bool(column & mask))
                                             for mask in menu) for vector in vectors)
            if score > best:
                best, selected = score, vectors
        total = 256 * len(menus) * 2
        fraction = Fraction(best, total)
        return {"correct": best, "total": total, "fraction": (fraction.numerator, fraction.denominator),
                "accuracy": float(fraction), "decoder_vectors": selected}

    rows = []
    for menu in MENUS:
        signatures = {tuple(int(bool(column & mask)) for mask in menu) for column in range(4)}
        minimum = (len(signatures) - 1).bit_length()
        rows.append({"menu": menu, "answer_classes": len(signatures), "minimum_fixed_bits": minimum,
                     "one_bit_unrestricted": bound((menu,))})
    mean = Fraction(sum(row["minimum_fixed_bits"] for row in rows), len(rows))
    return {"branch_column_counts": multiplicities, "menus": rows,
            "minimum_mean_payload": (mean.numerator, mean.denominator), "always_two_mean_payload": 2,
            "shared_one_bit_decoder_bound": bound(MENUS),
            "scope": "uniform raw worlds and public menus; delayed actual mask; one shared decoder"}


def hidden_wiring_bound() -> dict:
    """Even unlimited world encoding cannot identify an undisclosed inlet pair."""
    correct = total = 0
    witnesses = []
    by_mask = []
    for mask in (1, 2, 3):
        subtotal = 0
        for world in WORLDS:
            labels = [oracle(world, pair, mask) for pair in PAIRS]
            subtotal += max(labels.count(0), labels.count(1))
            if len(witnesses) < 3 and len(set(labels)) > 1:
                left = next(index for index, label in enumerate(labels) if label == 0)
                right = next(index for index, label in enumerate(labels) if label == 1)
                witnesses.append({"world": world, "mask": mask, "pairs": (PAIRS[left], PAIRS[right]), "answers": (0, 1)})
        denominator = 256 * len(PAIRS)
        fraction = Fraction(subtotal, denominator)
        by_mask.append({"mask": mask, "fraction": (fraction.numerator, fraction.denominator)})
        correct += subtotal
        total += denominator
    fraction = Fraction(correct, total)
    return {"correct": correct, "total": total, "fraction": (fraction.numerator, fraction.denominator),
            "by_mask": by_mask, "incompatible_cases": witnesses,
            "scope": "pair hidden from encoder and decoder; all raw values and eventual mask otherwise available"}


def _empty_score() -> dict:
    return {"correct": 0, "answers": 0, "payload_bits": 0, "packets": 0}


def _add_score(score: dict, packet: tuple, actual: tuple, expected: tuple) -> None:
    score["correct"] += sum(left == right for left, right in zip(actual, expected))
    score["answers"] += 2
    score["payload_bits"] += len(packet)
    score["packets"] += 1


def _finish(score: dict) -> dict:
    return {**score, "accuracy": score["correct"] / score["answers"] if score["answers"] else None,
            "exact": score["correct"] == score["answers"],
            "mean_payload_bits": score["payload_bits"] / score["packets"] if score["packets"] else None}


def _swapped_mask(mask: int) -> int:
    return ((mask & 1) << 1) | ((mask >> 1) & 1)


def remap_world(world: int, rule_permutation: Sequence[int], swap_h: bool = False) -> int:
    if tuple(sorted(rule_permutation)) != (0, 1, 2, 3):
        raise ValueError("rule remapping must be a permutation")
    out = 0
    for rule in range(4):
        for h in (0, 1):
            out |= ((world >> (2 * rule + h)) & 1) << (2 * rule_permutation[rule] + (h ^ int(swap_h)))
    return out


def verify(checkpoint: Mapping | Policy) -> dict:
    """Exhaust every original-world stratum, then independent counterfactuals."""
    policy = compile_policy(checkpoint)
    ordered_pairs = tuple(pair for unordered in PAIRS for pair in (unordered, unordered[::-1]))
    states = {}
    hidden_states = {}
    packets, predictions, targets = {}, {}, {}
    modes = ("frozen", "forced_one", "forced_two", "hidden_wiring", "static_AB")
    scores = {mode: _empty_score() for mode in modes}
    strata = {f"world_{w}_pair_{p}_menu_{m}": _empty_score()
              for w, p, m in product(("train", "held"), repeat=3)}
    menu_scores = {menu: _empty_score() for menu in MENUS}
    first_error = None
    lengths = {menu: set() for menu in MENUS}
    for world in WORLDS:
        raw = records_for_world(world)
        checked = _records(raw, ("A", "B"))
        for pair in ordered_pairs:
            inlet_names = tuple(NAMES[index] for index in pair)
            states[world, pair] = _scan(policy, checked, inlet_names)
            hidden_states[world, pair] = _scan(policy, checked, inlet_names, True)
    for world in WORLDS:
        for pair in ordered_pairs:
            for menu in MENUS:
                key = (world, pair, menu)
                expected = tuple(oracle(world, pair, mask) for mask in menu)
                targets[key] = expected
                packet = _packet(policy, states[world, pair], menu)
                actual = tuple(decode(policy, packet, mask) for mask in menu)
                packets[key], predictions[key] = packet, actual
                lengths[menu].add(len(packet))
                _add_score(scores["frozen"], packet, actual, expected)
                _add_score(menu_scores[menu], packet, actual, expected)
                flags = ("train" if world.bit_count() % 2 == 0 else "held",
                         "train" if tuple(sorted(pair)) in TRAIN_PAIRS else "held",
                         "train" if menu in TRAIN_MENUS else "held")
                _add_score(strata[f"world_{flags[0]}_pair_{flags[1]}_menu_{flags[2]}"], packet, actual, expected)
                if actual != expected and first_error is None:
                    first_error = {"world": world, "inlets": pair, "menu": menu, "packet": packet,
                                   "expected": expected, "actual": actual}
                for mode, source, forced in (("forced_one", states[world, pair], 1),
                                             ("forced_two", states[world, pair], 2),
                                             ("hidden_wiring", hidden_states[world, pair], None),
                                             ("static_AB", states[world, (0, 1)], None)):
                    other_packet = _packet(policy, source, menu, forced)
                    other_actual = tuple(decode(policy, other_packet, mask) for mask in menu)
                    _add_score(scores[mode], other_packet, other_actual, expected)

    # All 24 visit orders.  The menu/decoder is evaluated on the resulting two
    # states, never rerun or refitted from a reordered target table.
    perm_score = _empty_score()
    perm_code_changes = 0
    for order in ORDERS:
        for world in WORLDS:
            raw = tuple((record["endpoint"], tuple(record["values"]))
                        for record in records_for_world(world, order=order))
            for pair in ordered_pairs:
                changed_states = _scan(policy, raw, tuple(NAMES[index] for index in pair))
                for menu in MENUS:
                    packet = _packet(policy, changed_states, menu)
                    actual = tuple(decode(policy, packet, mask) for mask in menu)
                    key = (world, pair, menu)
                    _add_score(perm_score, packet, actual, targets[key])
                    perm_code_changes += packet != packets[key]

    # Simultaneously move record values and their endpoint identities.  A
    # common swap of h also moves mask bits, preserving the requested truth.
    remap_cases = remap_failures = remap_code_changes = 0
    for permutation in ORDERS:
        for swap_h in (False, True):
            for world in WORLDS:
                changed_world = remap_world(world, permutation, swap_h)
                for pair in ordered_pairs:
                    changed_pair = tuple(permutation[index] for index in pair)
                    for menu in MENUS:
                        changed_menu = tuple(_swapped_mask(mask) for mask in menu) if swap_h else menu
                        before, after = (world, pair, menu), (changed_world, changed_pair, changed_menu)
                        assert targets[before] == targets[after]
                        remap_cases += 2
                        remap_failures += sum(left != right for left, right in zip(predictions[before], predictions[after]))
                        if not swap_h:
                            remap_code_changes += packets[before] != packets[after]

    # Fresh names preserve every match trace for all orders and inlet orders.
    # Since no other name data enter any program or decoder, this factors all
    # 256 value worlds without claiming to have rerun them under every name.
    renamed_trace_cases = renamed_packet_cases = 0
    for names in (("record::p7", "record::q2", "record::r9", "record::s4"), (101, -23, 5041, 88)):
        for order in ORDERS:
            for pair in ordered_pairs:
                old_trace = tuple((int(index == pair[0]), int(index == pair[1])) for index in order)
                new_trace = tuple((int(names[index] == names[pair[0]]), int(names[index] == names[pair[1]])) for index in order)
                assert old_trace == new_trace
                renamed_trace_cases += 1
                for menu in MENUS:
                    old = send(policy, records_for_world(173, order=order), tuple(NAMES[index] for index in pair), menu)
                    new = send(policy, records_for_world(173, order=order, names=names), tuple(names[index] for index in pair), menu)
                    assert old == new
                    renamed_packet_cases += 1

    # Same eight values and menu, change only downstream inlet identities.
    rewiring = {"changed_cells": 0, "unchanged_cells": 0,
                "correct_new_on_changed": 0, "stale_correct_on_changed": 0,
                "prediction_changed_on_changed": 0, "prediction_changed_on_unchanged": 0}
    rewiring_witness = None
    for world in WORLDS:
        for old_pair, new_pair in combinations(PAIRS, 2):
            for menu in MENUS:
                old, new = (world, old_pair, menu), (world, new_pair, menu)
                for port in (0, 1):
                    changed = targets[old][port] != targets[new][port]
                    moved = predictions[old][port] != predictions[new][port]
                    if changed:
                        rewiring["changed_cells"] += 1
                        rewiring["correct_new_on_changed"] += predictions[new][port] == targets[new][port]
                        rewiring["stale_correct_on_changed"] += predictions[old][port] == targets[new][port]
                        rewiring["prediction_changed_on_changed"] += moved
                        if rewiring_witness is None:
                            rewiring_witness = {"world": world, "old_pair": old_pair, "new_pair": new_pair,
                                               "mask": menu[port], "answers": (targets[old][port], targets[new][port]),
                                               "predictions": (predictions[old][port], predictions[new][port])}
                    else:
                        rewiring["unchanged_cells"] += 1
                        rewiring["prediction_changed_on_unchanged"] += moved

    support_rows = []
    collisions = []
    excess = []
    for pair in PAIRS:
        for menu in MENUS:
            truth_groups, code_groups = {}, {}
            for world in WORLDS:
                key = (world, pair, menu)
                truth_groups.setdefault(targets[key], []).append(world)
                code_groups.setdefault(packets[key], []).append(world)
            for code, worlds in code_groups.items():
                left = worlds[0]
                right = next((world for world in worlds if targets[world, pair, menu] != targets[left, pair, menu]), None)
                if right is not None:
                    collisions.append({"pair": pair, "menu": menu, "packet": code, "worlds": (left, right),
                                       "answers": (targets[left, pair, menu], targets[right, pair, menu])})
            for answer, worlds in truth_groups.items():
                codes = {packets[world, pair, menu] for world in worlds}
                if len(codes) > 1:
                    excess.append({"pair": pair, "menu": menu, "answers": answer, "packet_classes": len(codes)})
            for index in range(8):
                code_changes = answer_changes = truth_changes = 0
                for world in WORLDS:
                    if world & (1 << index):
                        continue
                    other = world ^ (1 << index)
                    left, right = (world, pair, menu), (other, pair, menu)
                    code_changes += packets[left] != packets[right]
                    answer_changes += predictions[left] != predictions[right]
                    truth_changes += targets[left] != targets[right]
                support_rows.append({"pair": pair, "menu": menu, "input": f"{NAMES[index // 2]}{index % 2}",
                                     "bit_flip_pairs": 128, "code_changes": code_changes,
                                     "answer_changes": answer_changes, "truth_changes": truth_changes})

    port_order_cases = port_order_failures = 0
    for world in WORLDS:
        for pair in ordered_pairs:
            for menu in MENUS:
                left = predictions[world, pair, menu]
                right = predictions[world, pair, menu[::-1]][::-1]
                port_order_cases += 2
                port_order_failures += sum(a != b for a, b in zip(left, right))

    information_bounds = exact_widths_and_bounds()
    minimum_widths = all(width(policy, row["menu"]) == row["minimum_fixed_bits"]
                         for row in information_bounds["menus"])
    complete_gate = (scores["frozen"]["correct"] == scores["frozen"]["answers"] and minimum_widths
                     and perm_score["correct"] == perm_score["answers"]
                     and remap_failures == 0 and port_order_failures == 0)
    return {"policy_digest": policy.digest, "gate_counts_T_F_W": policy.gate_counts,
            "minimum_fixed_width_every_menu": minimum_widths,
            "complete_finite_gate": complete_gate,
            "scores": {mode: _finish(score) for mode, score in scores.items()},
            "strata": {key: _finish(score) for key, score in strata.items()},
            "menus": [{"menu": menu, "width": width(policy, menu),
                       "physical_lengths": sorted(lengths[menu]), **_finish(menu_scores[menu])} for menu in MENUS],
            "physical_width_world_independent": all(len(sizes) == 1 for sizes in lengths.values()),
            "first_error": first_error,
            "source_permutations": {**_finish(perm_score), "orders": 24, "changed_packets": perm_code_changes},
            "simultaneous_remaps": {"answer_comparisons": remap_cases, "answer_changes": remap_failures,
                                     "rule_only_packet_changes": remap_code_changes,
                                     "includes_h_value_swap_and_matching_query_swap": True},
            "fresh_renamings": {"trace_cases": renamed_trace_cases, "executed_packet_pairs": renamed_packet_cases,
                                "all_equal": True, "all_worlds_factored_by_identical_match_traces": True},
            "port_order": {"answer_comparisons": port_order_cases, "answer_changes": port_order_failures},
            "rewiring": {**rewiring, "first_changed_case": rewiring_witness},
            "support": support_rows, "collisions": collisions, "excess_detail": excess,
            "information_bounds": information_bounds, "hidden_wiring_upper_bound": hidden_wiring_bound(),
            "decoder_interface": "literal packet tuple and eventual actual mask only; no fitting during verification"}


def verify_raw(checkpoint: Mapping | Policy, rows: Sequence[Mapping]) -> dict:
    """Check recorded physical packets and predictions, without trusting summaries.

    Each row needs world, inlet_indices, menu, packet.  It may additionally
    contain original records, names, source order, predictions (two ports), or
    actual_port plus prediction.  A claimed width is checked against tuple
    length.  Any provided raw record must match its named world's source bits.
    """
    policy = compile_policy(checkpoint)
    if not rows:
        raise ValueError("raw verification requires nonempty case rows")
    failures = []
    lengths = {}
    for index, row in enumerate(rows):
        try:
            world, pair, menu = _world(row["world"]), tuple(row["inlet_indices"]), _menu(row["menu"])
            names = tuple(row.get("names", NAMES))
            order = tuple(row.get("order", (0, 1, 2, 3)))
            canonical = records_for_world(world, order=order, names=names)
            records = row.get("records", canonical)
            if records != canonical:
                raise ValueError("raw records disagree with named source values or visit order")
            packet = tuple(_bit(value) for value in row["packet"])
            actual = send(policy, records, tuple(names[item] for item in pair), menu)
            if packet != actual:
                raise ValueError("recorded physical packet differs from independent execution")
            for field in ("width", "payload_bits"):
                if field in row and row[field] != len(packet):
                    raise ValueError("claimed payload count differs from actual tuple length")
            lengths.setdefault(menu, set()).add(len(packet))
            expected = tuple(oracle(world, pair, mask) for mask in menu)
            predicted = tuple(decode(policy, packet, mask) for mask in menu)
            if "predictions" in row and tuple(row["predictions"]) != predicted:
                raise ValueError("recorded predictions differ from isolated decoding")
            if "actual_port" in row:
                port = row["actual_port"]
                if type(port) is not int or port not in (0, 1):
                    raise ValueError("wrong actual port")
                if row.get("prediction", predicted[port]) != predicted[port]:
                    raise ValueError("recorded final answer differs from isolated decoding")
            if "oracle" in row and tuple(row["oracle"]) != expected:
                raise ValueError("recorded truth differs from enumerated raw rules")
        except (KeyError, TypeError, ValueError, IndexError) as error:
            failures.append({"row": index, "reason": str(error)})
    return {"rows": len(rows), "pass": not failures, "failures": failures,
            "physical_width_world_independent": all(len(values) == 1 for values in lengths.values())}


def hand_checkpoint() -> dict:
    """Attainable supplied reference, never a fitted policy."""
    inp = lambda index: ["input", index]
    selected = ["OR", inp(2), inp(3)]
    T = ["AND", inp(0), ["OR", ["NAND", selected, selected], inp(1)]]
    F = ["OR", ["AND", inp(0), inp(2)], ["AND", inp(1), inp(3)]]
    W = ["OR", ["XOR", inp(0), inp(2)], ["XOR", inp(1), inp(3)]]
    data = {"schema_version": 1, "initial_bit": 1,
            "input_bit_order": {key: list(value) for key, value in INPUT_ORDER.items()}}
    for name, ast in (("T", T), ("F", F), ("W", W)):
        expression = _expression(ast)
        data[name] = {"expr": ast, "gate_count": _cost(expression),
                      "truth_mask": sum(_evaluate(expression, tuple((word >> bit) & 1 for bit in range(4))) << word
                                        for word in range(16))}
    data["decoders"] = {"one": {str(mask): [0, 1] for mask in (1, 2, 3)},
                        "two": {str(mask): [int(bool(code & mask)) for code in range(4)] for mask in (1, 2, 3)}}
    return data


def self_test() -> dict:
    hand = hand_checkpoint()
    policy = compile_policy(hand)
    bounds = exact_widths_and_bounds()
    assert bounds["branch_column_counts"] == {0: 144, 1: 48, 2: 48, 3: 16}
    assert bounds["shared_one_bit_decoder_bound"]["fraction"] == (11, 12)
    for row in bounds["menus"]:
        menu = row["menu"]
        assert width(policy, menu) == row["minimum_fixed_bits"] == (1 if menu[0] == menu[1] else 2)
        assert row["answer_classes"] == (2 if menu[0] == menu[1] else 4 if set(menu) == {1, 2} else 3)
    for world in WORLDS:
        records = records_for_world(world)
        for pair in PAIRS:
            inlets = tuple(NAMES[index] for index in pair)
            for menu in MENUS:
                packet = send(policy, records, inlets, menu)
                for mask in menu:
                    assert decode(policy, packet, mask) == oracle(world, pair, mask) == oracle_records(records, inlets, mask)
    malformed = json.loads(json.dumps(hand))
    malformed["T"]["truth_mask"] ^= 1
    try:
        compile_policy(malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("corrupt truth-mask metadata accepted")
    wrong = json.loads(json.dumps(hand))
    wrong["T"]["expr"][0] = "OR"
    expression = _expression(wrong["T"]["expr"])
    wrong["T"]["truth_mask"] = sum(_evaluate(expression, tuple((address >> bit) & 1 for bit in range(4))) << address
                                      for address in range(16))
    wrong["T"]["gate_count"] = _cost(expression)
    assert predict(wrong, records_for_world(0), ("A", "B"), (1, 1), 0) != oracle(0, (0, 1), 1)
    wrong_decoder = json.loads(json.dumps(hand))
    wrong_decoder["decoders"]["one"]["1"][0] ^= 1
    assert predict(wrong_decoder, records_for_world(0), ("A", "B"), (1, 1), 0) != oracle(0, (0, 1), 1)
    sample = {"world": 255, "inlet_indices": [0, 1], "menu": [1, 1], "packet": [1], "width": 1}
    assert verify_raw(policy, [sample])["pass"]
    truncated = {**sample, "packet": []}
    assert not verify_raw(policy, [truncated])["pass"]
    mutated = {**sample, "records": records_for_world(255)}
    mutated["records"][0]["values"][0] = 0
    assert not verify_raw(policy, [mutated])["pass"]
    assert not verify_raw(policy, [{**sample, "records": records_for_world(255)[:3]}])["pass"]
    try:
        decode(policy, {"world": 255, "packet": (1,)}, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("decoder accepted a world-bearing record")
    return {"pass": True, "worlds": 256, "pairs": 6, "menus": 9,
            "hand_all_original_cases_exact": True, "corrupted_program_rejected": True,
            "truncated_and_mutated_records_rejected": True, "bounds": bounds,
            "hidden_wiring_upper_bound": hidden_wiring_bound()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--raw", type=Path, help="JSON case-row list or object containing rows")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--full-hand-test", action="store_true", help="also exhaust remappings of the hand reference")
    args = parser.parse_args()
    if not args.checkpoint and not args.self_test and not args.full_hand_test:
        parser.error("provide --checkpoint, --self-test or --full-hand-test")
    result = {}
    if args.self_test:
        result["self_test"] = self_test()
    if args.full_hand_test:
        result["hand_verification"] = verify(hand_checkpoint())
    if args.checkpoint:
        raw_bytes = args.checkpoint.read_bytes()
        checkpoint = json.loads(raw_bytes)
        if "checkpoint" in checkpoint:
            checkpoint = checkpoint["checkpoint"]
        result["checkpoint_file_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
        result["verification"] = verify(checkpoint)
        if args.raw:
            content = json.loads(args.raw.read_text())
            rows = content["rows"] if isinstance(content, dict) else content
            result["raw_verification"] = verify_raw(checkpoint, rows)
    elif args.raw:
        parser.error("--raw needs --checkpoint")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
