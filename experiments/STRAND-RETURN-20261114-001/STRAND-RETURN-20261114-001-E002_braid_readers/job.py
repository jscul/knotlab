"""Exhaust reversible crossings and the messages required by their later readers."""

import argparse
import json
from collections import Counter, defaultdict
from itertools import permutations, product


def binary_forward(x, y):
    return y, 1 - x


def binary_inverse(u, v):
    return 1 - v, u


def ternary_forward(x, y):
    return y, (2 * y - x) % 3


def ternary_inverse(u, v):
    return (2 * u - v) % 3, u


def trace(move, triple, positions):
    state = tuple(triple)
    states = [state]
    for i in positions:
        state = state[:i] + move(*state[i:i + 2]) + state[i + 2:]
        states.append(state)
    return states


def coordinate_dependencies(move, n):
    full = range(n)
    support = []
    for output in (0, 1):
        varies_with_x = any(len({move(x, y)[output] for x in full}) > 1 for y in full)
        varies_with_y = any(len({move(x, y)[output] for y in full}) > 1 for x in full)
        support.append([axis for axis, varies in zip(("x", "y"), (varies_with_x, varies_with_y)) if varies])
    return support


def binary_census():
    pairs = list(product(range(2), repeat=2))
    triples = list(product(range(2), repeat=3))
    candidates = []
    for image in permutations(pairs):
        table = dict(zip(pairs, image))

        def move(x, y):
            return table[x, y]

        disagreements = []
        for triple in triples:
            left = trace(move, triple, (0, 1, 0))[-1]
            right = trace(move, triple, (1, 0, 1))[-1]
            if left != right:
                disagreements.append({"input": triple, "left": left, "right": right})
        signs = next(((a, b) for a, b in pairs
                      if all(move(x, y) == (y ^ a, x ^ b) for x, y in pairs)), None)
        candidates.append({
            "image_in_pair_order": image,
            "agreeing_triples": len(triples) - len(disagreements),
            "first_disagreement": next(iter(disagreements), None),
            "identity": tuple(pairs) == image,
            "signed_swap_offsets": signs,
            "output_dependencies": coordinate_dependencies(move, 2),
        })
    passing = [item for item in candidates if item["agreeing_triples"] == len(triples)]
    return {
        "pair_order": pairs,
        "permutations": len(candidates),
        "triple_comparisons": len(candidates) * len(triples),
        "passing": len(passing),
        "passing_identities": sum(item["identity"] for item in passing),
        "passing_signed_swaps": sum(item["signed_swap_offsets"] is not None for item in passing),
        "passing_with_a_jointly_dependent_output": sum(
            any(len(axes) == 2 for axes in item["output_dependencies"]) for item in passing),
        "candidates": candidates,
    }


def signature_panel(signatures):
    """For a fixed one-bit decoder, each encoder row can choose either output profile."""
    counts = Counter(signatures)
    queries = len(signatures[0])
    profiles = list(product((0, 1), repeat=queries))
    best_answers = best_complete = -1
    for decoder in product(profiles, repeat=2):
        complete = sum(count for target, count in counts.items() if target in decoder)
        answers = 0
        for target, count in counts.items():
            matches = [sum(a == b for a, b in zip(target, prediction)) for prediction in decoder]
            answers += count * max(matches)
        if complete > best_complete:
            best_complete, complete_decoder = complete, decoder
        if answers > best_answers:
            best_answers, answer_decoder = answers, decoder
    return {
        "points": len(signatures),
        "individual_answers": len(signatures) * queries,
        "signature_counts": [{"answers": value, "points": count} for value, count in sorted(counts.items())],
        "distinct_signatures": len(counts),
        "minimum_fixed_payload_bits_for_exactness": (len(counts) - 1).bit_length(),
        "one_bit_decoders_enumerated": len(profiles) ** 2,
        "best_one_bit_complete_points": best_complete,
        "decoder_attaining_complete_points": complete_decoder,
        "best_one_bit_individual_answers": best_answers,
        "decoder_attaining_individual_answers": answer_decoder,
    }


def label_mask(values):
    return sum(1 << value for value in set(values))


def relation_panel(forward, inverse, n):
    pairs = list(product(range(n), repeat=2))
    rows = []
    classes = defaultdict(Counter)
    full_exact = rectangular_exact = 0
    for crossed_mask in range(1 << len(pairs)):
        crossed = {pair for i, pair in enumerate(pairs) if crossed_mask & (1 << i)}
        # Independent oracle: check forward images of all possible original points.
        original = {p for p in pairs if forward(*p) in crossed}
        oracle_x = label_mask(x for x, _ in original)
        recovered = {inverse(*p) for p in crossed}
        recovered_x = label_mask(x for x, _ in recovered)
        u_values = {u for u, _ in crossed}
        v_values = {v for _, v in crossed}
        rectangular_x = label_mask(inverse(u, v)[0] for u in u_values for v in v_values)
        u_mask, v_mask = label_mask(u_values), label_mask(v_values)
        classes[u_mask, v_mask][oracle_x] += 1
        full_exact += recovered == original
        rectangular_exact += rectangular_x == oracle_x
        rows.append([crossed_mask, u_mask, v_mask, oracle_x, recovered_x, rectangular_x])

    held_examples = []
    for x in (0, 1):
        crossed = sorted(forward(x, y) for y in range(n))
        u_values = sorted({u for u, _ in crossed})
        v_values = sorted({v for _, v in crossed})
        held_examples.append({
            "initial_x": x, "initial_y": list(range(n)), "crossed_pairs": crossed,
            "u_values": u_values, "v_values": v_values,
            "joint_then_undo_x": sorted({inverse(*p)[0] for p in crossed}),
            "marginals_then_undo_x": sorted({inverse(u, v)[0] for u in u_values for v in v_values}),
        })
    left, right = held_examples
    return {
        "crossed_pair_order_for_mask_bits": pairs,
        "subsets": len(rows),
        "full_joint_then_inverse_exact_entire_relation": full_exact,
        "full_joint_then_inverse_exact_old_x": sum(row[3] == row[4] for row in rows),
        "product_of_marginals_then_inverse_exact_old_x": rectangular_exact,
        "distinct_marginal_pairs": len(classes),
        "marginal_pairs_that_uniquely_determine_old_x": sum(len(values) == 1 for values in classes.values()),
        "subsets_where_marginals_uniquely_determine_old_x": sum(
            sum(values.values()) for values in classes.values() if len(values) == 1),
        "best_possible_exact_old_x_count_from_marginals_uniform_subsets": sum(
            max(values.values()) for values in classes.values()),
        "held_x_examples": held_examples,
        "held_x_examples_have_identical_marginals": (
            left["u_values"] == right["u_values"] and left["v_values"] == right["v_values"]),
        "subset_columns": ["crossed_pair_mask", "u_mask", "v_mask", "oracle_old_x_mask",
                           "joint_then_inverse_old_x_mask", "marginals_then_inverse_old_x_mask"],
        "subset_rows": rows,
    }


def named_move(forward, inverse, n):
    pairs = list(product(range(n), repeat=2))
    point_rows = []
    schedules = []
    for p in pairs:
        crossed = forward(*p)
        point_rows.append({
            "input": p, "forward": crossed, "inverse": inverse(*p), "two_forwards": forward(*crossed),
            "forward_then_inverse": inverse(*crossed), "inverse_then_forward": forward(*inverse(*p)),
        })
    for p in product(range(n), repeat=3):
        left = trace(forward, p, (0, 1, 0))
        right = trace(forward, p, (1, 0, 1))
        schedules.append({"input": p, "left": left, "right": right})
    # The two questions refer to the first strand after stopping or undoing.
    # Every possible crossed point has the same weight, as does each question.
    signatures = [(int(u == 0), int(inverse(u, v)[0] == 0)) for u, v in pairs]
    return {
        "alphabet_size": n, "output_dependencies": coordinate_dependencies(forward, n),
        "points": len(pairs),
        "forward_then_inverse_restores": sum(row["input"] == row["forward_then_inverse"] for row in point_rows),
        "inverse_then_forward_restores": sum(row["input"] == row["inverse_then_forward"] for row in point_rows),
        "two_forwards_restore": sum(row["input"] == row["two_forwards"] for row in point_rows),
        "point_rows": point_rows,
        "triple_count": len(schedules),
        "three_move_schedules_agree": sum(row["left"][-1] == row["right"][-1] for row in schedules),
        "two_move_prefixes_disagree": sum(row["left"][2] != row["right"][2] for row in schedules),
        "schedule_positions": {"left": [0, 1, 0], "right": [1, 0, 1]},
        "schedule_rows": schedules,
        "allowed_relations": relation_panel(forward, inverse, n),
        "point_reader": {
            "query_order": ["stop_first_zero", "undo_first_zero"],
            "crossed_point_order": pairs, "answers_in_point_order": signatures,
            "stop_known_before_encoding": signature_panel([(s,) for s, _ in signatures]),
            "undo_known_before_encoding": signature_panel([(u,) for _, u in signatures]),
            "choice_announced_after_encoding": signature_panel(signatures),
        },
    }


def cases():
    yield "binary-census", {}
    yield "binary-signed-swap", {}
    yield "ternary-mixing", {}


def run(case_id, payload):
    if case_id == "binary-census":
        return binary_census()
    if case_id == "binary-signed-swap":
        return named_move(binary_forward, binary_inverse, 2)
    if case_id == "ternary-mixing":
        return named_move(ternary_forward, ternary_inverse, 3)
    raise ValueError(f"Unknown case {case_id}")


if __name__ == "__main__":
    available = dict(cases())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=available)
    args = parser.parse_args()
    selected = [args.case] if args.case else available
    print(json.dumps({key: run(key, available[key]) for key in selected}, sort_keys=True))
