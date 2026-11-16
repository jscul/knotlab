"""One finite empirical fit, followed by execution from raw named records.

The encoder has no gathered-pair input. It evaluates width from the public
menu first, then compares each original record with each inlet and applies
the same Boolean update at both lanes. Only the packet and eventual mask
enter the shared decoder. --smoke checks synthetic primitives without fitting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OPS = ("AND", "OR", "XOR", "NAND")
FUNCTION_UNIVERSE = (1 << 16) - 1
TRAIN_WORLDS = tuple(world for world in range(256) if world.bit_count() % 2 == 0)
TRAIN_MASK = sum(1 << world for world in TRAIN_WORLDS)
TRAIN_PAIRS = ((0, 1), (2, 3), (0, 2), (1, 3))
TRAIN_WIRINGS = tuple(order for pair in TRAIN_PAIRS for order in (pair, pair[::-1]))
TRAIN_MENUS = ((1, 1), (2, 2), (3, 3), (1, 2), (2, 1), (1, 3), (3, 1))
ALL_MENUS = tuple(product((1, 2, 3), repeat=2))
INPUT_ORDER = {
    "T": ("old", "value", "match_inlet0", "match_inlet1"),
    "F": ("state_h0", "state_h1", "first_mask_h0", "first_mask_h1"),
    "W": ("first_mask_h0", "first_mask_h1", "second_mask_h0", "second_mask_h1"),
}


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def apply_operation(op, left, right, universe):
    if op == "AND":
        return left & right
    if op == "OR":
        return left | right
    if op == "XOR":
        return left ^ right
    if op == "NAND":
        return universe ^ (left & right)
    raise ValueError(f"Unknown Boolean operation {op!r}")


def evaluate_expr(expr, inputs):
    kind = expr[0]
    if kind == "const":
        return int(expr[1])
    if kind == "input":
        return int(inputs[expr[1]])
    left = evaluate_expr(expr[1], inputs)
    # The admitted identical-value reuse evaluates the child only once.
    right = left if expr[1] == expr[2] else evaluate_expr(expr[2], inputs)
    return apply_operation(kind, left, right, 1)


def expression_gates(expr):
    if expr[0] in ("const", "input"):
        return 0
    return 1 + expression_gates(expr[1]) + (0 if expr[1] == expr[2] else expression_gates(expr[2]))


def expression_mask(expr):
    return sum(evaluate_expr(expr, tuple((address >> bit) & 1 for bit in range(4))) << address
               for address in range(16))


@dataclass(frozen=True)
class Function:
    truth_mask: int
    gate_count: int
    expr: tuple


def function_key(function):
    return function.gate_count, function.expr


def enumerate_functions(max_gates=4):
    """Minimum formula cost per function; identical NAND children reuse a value."""
    best = {}
    for expr in (("const", 0), ("const", 1), *(("input", index) for index in range(4))):
        mask = expression_mask(expr)
        node = Function(mask, 0, expr)
        if mask not in best or node.expr < best[mask].expr:
            best[mask] = node
    levels = [sorted(best.values(), key=function_key)]
    for cost in range(1, max_gates + 1):
        level = {}

        def offer(mask, expr):
            if mask in best:
                return
            old = level.get(mask)
            if old is None or expr < old.expr:
                level[mask] = Function(mask, cost, expr)

        for left_cost in range(cost):
            right_cost = cost - left_cost - 1
            for left in levels[left_cost]:
                for right in levels[right_cost]:
                    if left.expr > right.expr:
                        continue
                    for op in OPS:
                        mask = apply_operation(op, left.truth_mask, right.truth_mask, FUNCTION_UNIVERSE)
                        offer(mask, (op, left.expr, right.expr))
        # Reusing an already computed value supplies unary inversion in one gate.
        for child in levels[cost - 1]:
            offer(FUNCTION_UNIVERSE ^ child.truth_mask, ("NAND", child.expr, child.expr))
        levels.append(sorted(level.values(), key=function_key))
        best.update(level)
    return sorted(best.values(), key=function_key), {
        "maximum_gates": max_gates, "functions": len(best),
        "functions_by_minimum_gate_count": {str(cost): len(level) for cost, level in enumerate(levels)},
        "cost": "sum of child formula costs plus one; identical NAND operands reuse one child",
        "syntax_order": "recursive Python tuple order after canonical commutative operand order",
    }


def node_record(function):
    return {"truth_mask": function.truth_mask, "gate_count": function.gate_count, "expr": function.expr}


def width_from_menu(policy, menu):
    first, second = map(int, menu)
    if first not in (1, 2, 3) or second not in (1, 2, 3):
        raise ValueError("Reader masks must be 1, 2 or 3")
    return 1 + evaluate_expr(policy["W"]["expr"], (first & 1, first >> 1, second & 1, second >> 1))


def encode_packet(policy, raw_records, inlet_names, menu):
    # Crucial ordering: width is committed before accessing any membership bit.
    width = width_from_menu(policy, menu)
    if len(raw_records) != 4 or len(inlet_names) != 2:
        raise ValueError("Four raw records and two distinct inlets are required")
    states = [int(policy["initial_bit"])] * 2
    matches_seen = [0, 0]
    for record in raw_records:
        match0 = int(record["endpoint"] == inlet_names[0])
        match1 = int(record["endpoint"] == inlet_names[1])
        matches_seen[0] += match0
        matches_seen[1] += match1
        if match0 and match1:
            raise ValueError("The two inlets must name distinct endpoints")
        for lane in (0, 1):
            value = int(record["values"][lane])
            if value not in (0, 1):
                raise ValueError("Membership values must be bits")
            states[lane] = evaluate_expr(policy["T"]["expr"], (states[lane], value, match0, match1))
    if matches_seen != [1, 1]:
        raise ValueError("Each inlet must match exactly one original source")
    if width == 2:
        payload = tuple(states)
    else:
        first = int(menu[0])
        payload = (evaluate_expr(policy["F"]["expr"], (*states, first & 1, first >> 1)),)
    scan_gates = 8 * policy["T"]["gate_count"]
    emission_gates = policy["F"]["gate_count"] if width == 1 else 0
    actions = {"endpoint_comparisons": 8, "scan_updates": 8,
               "scan_boolean_gates": scan_gates,
               "width_boolean_gates": policy["W"]["gate_count"],
               "emission_boolean_gates": emission_gates,
               "boolean_gates": scan_gates + policy["W"]["gate_count"] + emission_gates,
               "payload_bits": len(payload)}
    return {"packet": payload, "actions": actions}


def packet(policy, raw_records, inlet_names, menu):
    return encode_packet(policy, raw_records, inlet_names, menu)["packet"]


def decode(policy, payload, actual_mask):
    if len(payload) not in (1, 2) or actual_mask not in (1, 2, 3):
        raise ValueError("An actual packet and one eventual query mask are required")
    code = sum(int(bit) << index for index, bit in enumerate(payload))
    return int(policy["decoders"]["one" if len(payload) == 1 else "two"][str(actual_mask)][code])


def predict(policy, raw_records, inlet_names, menu, actual_port):
    encoded = encode_packet(policy, raw_records, inlet_names, menu)
    # The actual port enters only the receiver after the packet is committed.
    return encoded | {"width": len(encoded["packet"]),
                      "answer": decode(policy, encoded["packet"], int(menu[actual_port]))}


def make_training_data():
    values = tuple(sum(((world >> bit) & 1) << world for world in TRAIN_WORLDS) for bit in range(8))
    labels = []
    for first, second in TRAIN_WIRINGS:
        row = {1: 0, 2: 0, 3: 0}
        # Only training-world oracle labels are constructed during fitting.
        for world in TRAIN_WORLDS:
            allowed = [((world >> (2 * first + h)) & 1)
                       & ((world >> (2 * second + h)) & 1) for h in (0, 1)]
            for mask in (1, 2, 3):
                row[mask] |= int(any(allowed[h] for h in (0, 1) if mask & (1 << h))) << world
        labels.append(row)
    frequencies = Counter(mask for menu in TRAIN_MENUS for mask in menu)
    return values, labels, frequencies


def two_input_function(mask, old, value):
    """Four-entry Shannon table, with complement confined to training worlds."""
    if mask == 0:
        return 0
    if mask == 1:
        return TRAIN_MASK ^ (old | value)
    if mask == 2:
        return old & (TRAIN_MASK ^ value)
    if mask == 3:
        return TRAIN_MASK ^ value
    if mask == 4:
        return (TRAIN_MASK ^ old) & value
    if mask == 5:
        return TRAIN_MASK ^ old
    if mask == 6:
        return old ^ value
    if mask == 7:
        return TRAIN_MASK ^ (old & value)
    if mask == 8:
        return old & value
    if mask == 9:
        return TRAIN_MASK ^ (old ^ value)
    if mask == 10:
        return old
    if mask == 11:
        return old | (TRAIN_MASK ^ value)
    if mask == 12:
        return value
    if mask == 13:
        return (TRAIN_MASK ^ old) | value
    if mask == 14:
        return old | value
    return TRAIN_MASK


def scan_training(truth_mask, initial_bit, values):
    outputs = []
    for first, second in TRAIN_WIRINGS:
        states = [TRAIN_MASK if initial_bit else 0] * 2
        for source_index in range(4):
            match0, match1 = int(source_index == first), int(source_index == second)
            local = (truth_mask >> (4 * match0 + 8 * match1)) & 15
            for lane in (0, 1):
                states[lane] = two_input_function(local, states[lane], values[2 * source_index + lane])
        outputs.append(tuple(states))
    return outputs


def state_groups(states):
    first, second = states
    return ((TRAIN_MASK ^ first) & (TRAIN_MASK ^ second),
            first & (TRAIN_MASK ^ second), (TRAIN_MASK ^ first) & second, first & second)


def fit_two_decoder(outputs, labels, frequencies):
    counts = [[[0, 0] for _ in range(4)] for _ in range(3)]
    for states, wanted in zip(outputs, labels, strict=True):
        for code, group in enumerate(state_groups(states)):
            total = group.bit_count()
            for query in (1, 2, 3):
                ones = (group & wanted[query]).bit_count()
                counts[query - 1][code][0] += total - ones
                counts[query - 1][code][1] += ones
    decoder = {str(query): [int(ones > zeros) for zeros, ones in counts[query - 1]]
               for query in (1, 2, 3)}
    correct = sum(frequencies[query] * max(zeros, ones)
                  for query in (1, 2, 3) for zeros, ones in counts[query - 1])
    return correct, decoder, counts


def fit_scan(functions, values, labels, frequencies):
    # The declared input type never presents both distinct inlet matches at a
    # single record. Grouping their unvisited truth entries consumes no label.
    representatives = {}
    for function in functions:
        representatives.setdefault(function.truth_mask & 0x0FFF, function)
    candidates = sorted(representatives.values(), key=function_key)
    best, best_rank = None, None
    trace = {}
    for function in candidates:
        for initial_bit in (0, 1):
            outputs = scan_training(function.truth_mask, initial_bit, values)
            correct, decoder, counts = fit_two_decoder(outputs, labels, frequencies)
            rank = (-correct, function.gate_count, function.expr, initial_bit)
            if best_rank is None or rank < best_rank:
                best_rank = rank
                best = (function, initial_bit, outputs, decoder, counts, correct)
            row = trace.setdefault(str(function.gate_count), {"candidates": 0, "best_training_correct": 0})
            row["candidates"] += 1
            row["best_training_correct"] = max(row["best_training_correct"], correct)
    return best, {"raw_functions": len(functions), "distinct_admitted_local_behaviors": len(candidates),
                  "initial_bits_per_function": 2, "candidates_evaluated": 2 * len(candidates),
                  "trace_by_gate_count": trace,
                  "selection": "training errors, T gate count, canonical T syntax, initial bit"}


def training_histogram(outputs, labels):
    # H[menu, eventual-mask-1, state-code, answer] contains training events only.
    histogram = np.zeros((len(TRAIN_MENUS), 3, 4, 2), dtype=np.int64)
    for states, wanted in zip(outputs, labels, strict=True):
        for code, group in enumerate(state_groups(states)):
            total = group.bit_count()
            for menu_index, menu in enumerate(TRAIN_MENUS):
                for query in menu:
                    ones = (group & wanted[query]).bit_count()
                    histogram[menu_index, query - 1, code, 0] += total - ones
                    histogram[menu_index, query - 1, code, 1] += ones
    return histogram


def fit_packet(functions, histogram, two_decoder):
    reachable = []
    for menu_index, menu in enumerate(TRAIN_MENUS):
        offset = 4 * (menu[0] & 1) + 8 * (menu[0] >> 1)
        reachable += [offset + code for code in range(4) if histogram[menu_index, :, code, :].sum()]
    reachable = sorted(set(reachable))
    f_representatives, w_representatives = {}, {}
    menu_addresses = [first + 4 * second for first, second in TRAIN_MENUS]
    for function in functions:
        f_pattern = sum(((function.truth_mask >> address) & 1) << bit
                        for bit, address in enumerate(reachable))
        f_representatives.setdefault(f_pattern, function)
        if function.gate_count <= 3:
            w_pattern = sum(((function.truth_mask >> address) & 1) << bit
                            for bit, address in enumerate(menu_addresses))
            w_representatives.setdefault(w_pattern, function)
    emitters = sorted(f_representatives.values(), key=function_key)
    # C[F,menu,eventual-mask-1,emitted-bit,answer] is sufficient for every W.
    one_counts = np.zeros((len(emitters), len(TRAIN_MENUS), 3, 2, 2), dtype=np.int64)
    for menu_index, menu in enumerate(TRAIN_MENUS):
        offset = 4 * (menu[0] & 1) + 8 * (menu[0] >> 1)
        selectors = np.asarray([[(function.truth_mask >> (offset + code)) & 1 for code in range(4)]
                                for function in emitters], dtype=np.int64)
        selected = (selectors @ histogram[menu_index].transpose(1, 0, 2).reshape(4, 6)).reshape(-1, 3, 2)
        one_counts[:, menu_index, :, 1, :] = selected
        one_counts[:, menu_index, :, 0, :] = histogram[menu_index].sum(axis=1) - selected
    two_correct = np.asarray([
        sum(int(histogram[m, query - 1, code, two_decoder[str(query)][code]])
            for query in (1, 2, 3) for code in range(4))
        for m in range(len(TRAIN_MENUS))], dtype=np.int64)
    samples = len(TRAIN_WORLDS) * len(TRAIN_WIRINGS)
    best, best_rank, trace = None, None, []
    for pattern, width_function in sorted(w_representatives.items(), key=lambda item: function_key(item[1])):
        one_menus = [m for m in range(len(TRAIN_MENUS)) if not (pattern >> m) & 1]
        two_menus = [m for m in range(len(TRAIN_MENUS)) if (pattern >> m) & 1]
        counts = one_counts[:, one_menus].sum(axis=1)
        correct = counts.max(axis=-1).sum(axis=(1, 2)) + two_correct[two_menus].sum()
        maximum = int(correct.max())
        # emitters already follow the declared gate-count/syntax tie order.
        selected = int(np.flatnonzero(correct == maximum)[0])
        emitter = emitters[selected]
        bits = 2 * samples * (len(TRAIN_MENUS) + len(two_menus))
        rank = (-maximum, bits, width_function.gate_count + emitter.gate_count,
                width_function.expr, emitter.expr)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            chosen_counts = counts[selected].copy()
            decoder = {str(query): [int(chosen_counts[query - 1, bit, 1]
                                        > chosen_counts[query - 1, bit, 0]) for bit in (0, 1)]
                       for query in (1, 2, 3)}
            best = (emitter, width_function, decoder, chosen_counts, maximum, bits, pattern)
        trace.append({"training_width_pattern": pattern, "W_truth_mask": width_function.truth_mask,
                      "best_training_correct": maximum, "transmitted_bits": bits,
                      "best_F_truth_mask": emitter.truth_mask,
                      "F_plus_W_gate_count": emitter.gate_count + width_function.gate_count})
    return best, {"reachable_F_addresses": reachable, "distinct_F_training_behaviors": len(emitters),
                  "distinct_W_training_patterns": len(w_representatives),
                  "F_W_behavior_pairs_scored": len(emitters) * len(w_representatives),
                  "histogram_shape": list(histogram.shape), "training_histogram": histogram.tolist(),
                  "trace": trace,
                  "selection": "training errors, transmitted bits, F+W gates, W syntax, F syntax",
                  "transmission_unit": "one packet per eventual-port episode; both ports are scored"}


def raw_world(world, names=("A", "B", "C", "D")):
    return [{"endpoint": name, "values": [(world >> (2 * index + h)) & 1 for h in (0, 1)]}
            for index, name in enumerate(names)]


def assess(policy):
    before = canonical_sha256(policy)
    strata, menus, failures = {}, {}, []
    action_totals = Counter()
    names = ("A", "B", "C", "D")
    for world in range(256):
        records = raw_world(world, names)
        for pair in combinations(range(4), 2):
            for order in (pair, pair[::-1]):
                inlets = tuple(names[index] for index in order)
                for menu in ALL_MENUS:
                    encoded = encode_packet(policy, records, inlets, menu)
                    payload = encoded["packet"]
                    key = ("train" if world in TRAIN_WORLDS else "held_out",
                           "train" if pair in TRAIN_PAIRS else "held_out",
                           "train" if menu in TRAIN_MENUS else "held_out")
                    label = "|".join(key)
                    row = strata.setdefault(label, {"correct": 0, "total": 0, "transmitted_bits": 0})
                    menu_key = f"{menu[0]},{menu[1]}"
                    widths = menus.setdefault(menu_key, {"width": len(payload), "packets": 0})
                    if widths["width"] != len(payload):
                        raise ValueError("Payload width depended on world or wiring")
                    widths["packets"] += 1
                    for query in menu:
                        wanted = int(any(((world >> (2 * pair[0] + h)) & 1)
                                         & ((world >> (2 * pair[1] + h)) & 1)
                                         for h in (0, 1) if query & (1 << h)))
                        answer = decode(policy, payload, query)
                        row["correct"] += int(answer == wanted)
                        row["total"] += 1
                        row["transmitted_bits"] += len(payload)
                        action_totals.update(encoded["actions"])
                        if answer != wanted and len(failures) < 16:
                            failures.append({"world": world, "inlet_indices": order, "menu": menu,
                                             "actual_mask": query, "packet": payload,
                                             "predicted": answer, "wanted": wanted})
    after = canonical_sha256(policy)
    if before != after:
        raise ValueError("Assessment modified the checkpoint")
    correct = sum(row["correct"] for row in strata.values())
    total = sum(row["total"] for row in strata.values())
    return {"correct": correct, "total": total, "accuracy": correct / total,
            "strata_order": ["world", "pair", "menu"], "strata": strata,
            "menus": menus, "action_totals_per_eventual_port_episode": dict(action_totals),
            "first_failures": failures, "checkpoint_sha256_after": after}


def fit():
    started = time.perf_counter()
    functions, enumeration = enumerate_functions(4)
    enumeration_seconds = time.perf_counter() - started
    values, labels, frequencies = make_training_data()
    stage1_started = time.perf_counter()
    first, scan_search = fit_scan(functions, values, labels, frequencies)
    update, initial, outputs, two_decoder, two_counts, stage1_correct = first
    stage1_seconds = time.perf_counter() - stage1_started
    stage2_started = time.perf_counter()
    histogram = training_histogram(outputs, labels)
    second, packet_search = fit_packet(functions, histogram, two_decoder)
    emitter, width, one_decoder, one_counts, correct, bits, width_pattern = second
    stage2_seconds = time.perf_counter() - stage2_started
    checkpoint = {"schema_version": 1, "initial_bit": initial,
                  "T": node_record(update), "F": node_record(emitter), "W": node_record(width),
                  "input_bit_order": INPUT_ORDER, "decoders": {"one": one_decoder, "two": two_decoder}}
    # Canonical JSON is also the sole serialization passed to the receiver and
    # independent interpreters. Freeze before constructing any held-out labels.
    checkpoint = json.loads(json.dumps(checkpoint, sort_keys=True, separators=(",", ":")))
    frozen = canonical_sha256(checkpoint)
    training_total = len(TRAIN_WORLDS) * len(TRAIN_WIRINGS) * len(TRAIN_MENUS) * 2
    fit_seconds = time.perf_counter() - started
    assessment_started = time.perf_counter()
    assessment = assess(checkpoint)
    trained = assessment["strata"]["train|train|train"]
    if trained["correct"] != correct or trained["total"] != training_total or trained["transmitted_bits"] != bits:
        raise ValueError("Raw-record execution disagrees with the training histogram selection")
    files = (Path(__file__), HERE / "contract.json", ROOT / "research/WIRED-FOLD-20261114-001/preregistration.md")
    return {
        "schema_version": 1, "seed_label": 17, "deterministic_fits": 1,
        "checkpoint": checkpoint, "checkpoint_sha256": frozen,
        "training": {"worlds": TRAIN_WORLDS, "pairs": TRAIN_PAIRS, "wirings": TRAIN_WIRINGS,
                     "menus": TRAIN_MENUS, "eventual_port_episodes": training_total,
                     "stage1_correct": stage1_correct, "stage2_correct": correct,
                     "transmitted_bits": bits, "distinct_packet_transmitted_bits": bits // 2,
                     "training_width_pattern": width_pattern,
                     "two_decoder_counts_per_world_wiring": two_counts,
                     "one_decoder_counts_per_eventual_port_episode": one_counts.tolist(),
                     "query_frequencies_per_menu_roster": dict(frequencies)},
        "enumeration": enumeration, "scan_search": scan_search, "packet_search": packet_search,
        "assessment": assessment,
        "runtime_seconds": {"enumeration": enumeration_seconds, "fit_scan": stage1_seconds,
                            "fit_packet": stage2_seconds, "fit_total": fit_seconds,
                            "assessment": time.perf_counter() - assessment_started,
                            "total": time.perf_counter() - started},
        "numpy_version": np.__version__,
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in files},
    }


def smoke():
    functions, enumeration = enumerate_functions(1)
    checked = 0
    for function in functions:
        if expression_mask(function.expr) != function.truth_mask or expression_gates(function.expr) != function.gate_count:
            raise ValueError("Primitive formula semantics or gate cost disagreed")
        checked += 16
    toy_t = ("XOR", ("input", 0), ("AND", ("input", 1), ("input", 2)))
    toy_f, toy_w = ("input", 0), ("input", 0)
    policy = {"schema_version": 1, "initial_bit": 0,
              **{name: {"expr": expr, "truth_mask": expression_mask(expr),
                        "gate_count": expression_gates(expr)} for name, expr in (("T", toy_t), ("F", toy_f), ("W", toy_w))},
              "input_bit_order": INPUT_ORDER,
              "decoders": {"one": {str(query): [0, 1] for query in (1, 2, 3)},
                           "two": {str(query): [0, 1, 0, 1] for query in (1, 2, 3)}}}
    records = raw_world(57)
    encoded = encode_packet(policy, records, ("B", "D"), (1, 2))
    renamed = [{"endpoint": f"fresh:{record['endpoint']}", "values": record["values"]} for record in records]
    if encoded != encode_packet(policy, renamed, ("fresh:B", "fresh:D"), (1, 2)):
        raise ValueError("Synthetic raw-name renaming changed the interpreter")
    for world in (0, 57, 255):
        if len(packet(policy, raw_world(world), ("B", "D"), (1, 2))) != 2:
            raise ValueError("Synthetic width depended on record values")
    # A tiny synthetic histogram independently verifies F's bit-selection
    # contraction, without constructing or scoring the research training set.
    h = np.arange(24, dtype=np.int64).reshape(3, 4, 2)
    selector = np.asarray([[0, 1, 0, 1], [1, 0, 1, 0]], dtype=np.int64)
    contracted = (selector @ h.transpose(1, 0, 2).reshape(4, 6)).reshape(2, 3, 2)
    for f in range(2):
        for q in range(3):
            for y in range(2):
                if contracted[f, q, y] != sum(selector[f, code] * h[q, code, y] for code in range(4)):
                    raise ValueError("Synthetic histogram contraction disagreed")
    return {"smoke_only_no_fit": True, "primitive_assignments_checked": checked,
            "enumeration": enumeration, "synthetic_packet": encoded,
            "synthetic_histogram_contraction": True,
            "job_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "numpy_version": np.__version__}


def setup(params):
    if params:
        raise ValueError("This frozen one-fit experiment accepts no runner parameters")


def cases():
    yield "fit-17", {"seed_label": 17}


def run(case_id, payload):
    if payload != {"seed_label": 17}:
        raise ValueError("Exactly one deterministic official fit is declared")
    return fit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    print(json.dumps(smoke() if args.smoke else fit(), sort_keys=True))


if __name__ == "__main__":
    main()
