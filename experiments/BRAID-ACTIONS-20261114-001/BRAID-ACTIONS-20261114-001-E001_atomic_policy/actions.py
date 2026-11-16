"""Finite structural induction of atomic Boolean programs on two ternary labels.

Inference evaluates six predicate ASTs on six raw one-hot equality bits. Only
the fitting accelerator uses their nine-row truth semantics. It never inserts
a crossing formula or constructs an inverse by reversing or inverting a map.
The supplied one-sided nondegenerate output grammar is an explicit prior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from itertools import permutations, product
from pathlib import Path

import numpy as np


LABELS = (0, 1, 2)
PAIRS = tuple(product(LABELS, repeat=2))
ALL_ROWS = (1 << 9) - 1
OPS = ("AND", "OR", "XOR")
TRAIN_TRIPLES = tuple(row for row in product(LABELS, repeat=3) if len(set(row)) < 3)
HELD_OUT_TRIPLES = tuple(row for row in product(LABELS, repeat=3) if len(set(row)) == 3)
# These arrays decode the generic ordered-pair encoding 3*x+y during fitting.
# They are not an action, a target operation, or an inference lookup.
PAIR_FIRST = np.asarray([row[0] for row in PAIRS], dtype=np.uint8)
PAIR_SECOND = np.asarray([row[1] for row in PAIRS], dtype=np.uint8)


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def eval_expr(expr, raw_bits):
    op = expr[0]
    if op == "input":
        return int(raw_bits[expr[1]])
    if op == "const":
        return int(expr[1])
    if op == "NOT":
        return 1 - eval_expr(expr[1], raw_bits)
    left, right = eval_expr(expr[1], raw_bits), eval_expr(expr[2], raw_bits)
    if op == "AND":
        return left & right
    if op == "OR":
        return left | right
    if op == "XOR":
        return left ^ right
    raise ValueError(f"Unknown atomic Boolean operation {op!r}")


def gate_count(expr):
    if expr[0] in ("input", "const"):
        return 0
    if expr[0] == "NOT":
        return 1 + gate_count(expr[1])
    return 1 + gate_count(expr[1]) + gate_count(expr[2])


def program_gate_count(program):
    return sum(gate_count(expr) for expr in program)


def one_hot(pair):
    if len(pair) != 2 or any(label not in LABELS for label in pair):
        raise ValueError("Two labels from {0,1,2} are required")
    return tuple(int(pair[coordinate] == label) for coordinate in (0, 1) for label in LABELS)


def eval_atomic(program, raw_bits):
    if (len(program) != 6 or len(raw_bits) != 6 or any(bit not in (0, 1) for bit in raw_bits)
            or sum(raw_bits[:3]) != 1 or sum(raw_bits[3:]) != 1):
        raise ValueError("Six output ASTs and two valid raw one-hot labels are required")
    outputs = tuple(eval_expr(expr, raw_bits) for expr in program)
    if sum(outputs[:3]) != 1 or sum(outputs[3:]) != 1:
        raise ValueError("The atomic program did not emit two one-hot labels")
    return outputs


def apply(program, pair):
    outputs = eval_atomic(program, one_hot(pair))
    return outputs[:3].index(1), outputs[3:].index(1)


def expression_mask(expr):
    return sum(eval_expr(expr, one_hot(pair)) << row for row, pair in enumerate(PAIRS))


@dataclass(frozen=True)
class Predicate:
    mask: int
    gates: int
    expr: tuple


def predicate_key(predicate):
    return predicate.gates, predicate.expr


def enumerate_predicates(max_gates=5):
    """Enumerate elementary formulas before joining any output registers."""
    best = {}
    for expr in (("const", 0), ("const", 1), *(("input", i) for i in range(6))):
        mask = expression_mask(expr)
        best[mask] = Predicate(mask, 0, expr)
    levels = [sorted(best.values(), key=predicate_key)]
    for cost in range(1, max_gates + 1):
        current = {}

        def offer(mask, expr):
            if mask in best:
                return
            if mask not in current or expr < current[mask].expr:
                current[mask] = Predicate(mask, cost, expr)

        for child in levels[cost - 1]:
            offer(ALL_ROWS ^ child.mask, ("NOT", child.expr))
        for left_cost in range(cost):
            right_cost = cost - left_cost - 1
            for left in levels[left_cost]:
                for right in levels[right_cost]:
                    if left.expr > right.expr:
                        continue
                    for op in OPS:
                        value = (left.mask & right.mask if op == "AND" else
                                 left.mask | right.mask if op == "OR" else left.mask ^ right.mask)
                        offer(value, (op, left.expr, right.expr))
        levels.append(sorted(current.values(), key=predicate_key))
        best.update(current)
    return best, {"maximum_gates_per_predicate": max_gates, "predicate_functions": len(best),
                  "by_minimum_gate_count": {str(cost): len(level) for cost, level in enumerate(levels)},
                  "cost": "Boolean formula tree gates, with no cross-output sharing",
                  "syntax_order": "recursive tuple order; commutative children canonically ordered"}


@dataclass(frozen=True)
class Register:
    predicates: tuple[Predicate, ...]
    labels: tuple[int, ...]

    @property
    def gates(self):
        return sum(predicate.gates for predicate in self.predicates)

    @property
    def syntax(self):
        return tuple(predicate.expr for predicate in self.predicates)


def register_catalogue(predicates, coordinate):
    """Join already enumerated predicate circuits under a supplied typing rule.

    Coordinate zero permutes y at each fixed x; coordinate one permutes x at
    each fixed y. Row/column permutation enumeration merely accelerates the
    join of three disjoint exhaustive predicate programs. No map is compiled.
    """
    catalogue = []
    choices = tuple(permutations(LABELS))
    for rows in product(choices, repeat=3):
        labels = tuple(rows[x][y] if coordinate == 0 else rows[y][x] for x, y in PAIRS)
        masks = tuple(sum(int(value == label) << row for row, value in enumerate(labels)) for label in LABELS)
        if any(mask not in predicates for mask in masks):
            continue
        parts = tuple(predicates[mask] for mask in masks)
        if (parts[0].mask & parts[1].mask or parts[0].mask & parts[2].mask
                or parts[1].mask & parts[2].mask or (parts[0].mask | parts[1].mask | parts[2].mask) != ALL_ROWS):
            raise ValueError("Output predicates were not a disjoint exhaustive register")
        catalogue.append(Register(parts, labels))
    return sorted(catalogue, key=lambda register: (register.gates, register.syntax))


def coordinate_joint_dependence(register):
    rows = np.asarray(register.labels).reshape(3, 3)
    depends_x = bool(np.any(rows != rows[:1, :]))
    depends_y = bool(np.any(rows != rows[:, :1]))
    return depends_x and depends_y


def training_pair_rows(first, second):
    left = np.asarray([register.labels for register in first], dtype=np.uint8)
    right = np.asarray([register.labels for register in second], dtype=np.uint8)
    # Nine-row semantic acceleration of actual enumerated AST programs only.
    return (3 * left[:, None, :] + right[None, :, :]).reshape(-1, 9)


def _cross_training_rows(rows, first, second):
    addresses = 3 * first + second
    values = np.take_along_axis(rows, addresses, axis=1)
    return PAIR_FIRST[values], PAIR_SECOND[values]


def _braid_matches(rows, triples):
    triples = np.asarray(triples, dtype=np.uint8)
    shape = (len(rows), len(triples))
    x, y, z = (np.broadcast_to(triples[:, coordinate], shape) for coordinate in (0, 1, 2))
    left_x, left_y = _cross_training_rows(rows, x, y)
    left_y, left_z = _cross_training_rows(rows, left_y, z)
    left_x, left_y = _cross_training_rows(rows, left_x, left_y)
    right_y, right_z = _cross_training_rows(rows, y, z)
    right_x, right_y = _cross_training_rows(rows, x, right_y)
    right_y, right_z = _cross_training_rows(rows, right_y, right_z)
    return ((left_x == right_x) & (left_y == right_y) & (left_z == right_z)).sum(axis=1)


def _point_metrics(rows, first, second):
    points = np.arange(9, dtype=np.uint8)
    bijective = np.all(np.sort(rows, axis=1) == points, axis=1)
    joint_first = np.asarray([coordinate_joint_dependence(register) for register in first])
    joint_second = np.asarray([coordinate_joint_dependence(register) for register in second])
    mixing = (joint_first[:, None] | joint_second[None, :]).reshape(-1)
    square = np.take_along_axis(rows, rows, axis=1)
    noninvolutive = np.any(square != points, axis=1)
    diagonal = (rows[:, (0, 4, 8)] == np.asarray((0, 4, 8))).sum(axis=1)
    gates = np.asarray([a.gates + b.gates for a in first for b in second], dtype=np.int64)
    return {"bijection": bijective, "mixing": mixing, "noninvolutive": noninvolutive,
            "diagonal_matches": diagonal, "gates": gates}


def _program(first, second, index):
    a, b = divmod(index, len(second))
    return first[a].syntax + second[b].syntax


def _score_record(metrics, index, braid=None):
    record = {name: int(values[index]) for name, values in metrics.items()}
    if braid is not None:
        record["training_braid_matches"] = int(braid[index])
        record["training_braid_total"] = len(TRAIN_TRIPLES)
    return record


def select_forward(first, second, metrics, braid=None):
    """Without braid argument the ablation cannot consult that feedback."""
    best, best_rank, trace = None, None, []
    for index in range(len(metrics["gates"])):
        rank = (-int(metrics["bijection"][index]), -int(metrics["mixing"][index]),
                -int(metrics["noninvolutive"][index]))
        if braid is not None:
            rank += (-int(braid[index]),)
        rank += (-int(metrics["diagonal_matches"][index]), int(metrics["gates"][index]),
                 _program(first, second, index))
        if best_rank is None or rank < best_rank:
            best, best_rank = index, rank
            trace.append({"candidate": index, "score": _score_record(metrics, index, braid)})
    return best, {"candidates_scored": len(metrics["gates"]), "initial_score": _score_record(metrics, 0, braid),
                  "final_score": _score_record(metrics, best, braid), "improvement_trace": trace,
                  "braid_feedback": braid is not None}


def select_inverse(first, second, rows, forward_rows):
    points = np.arange(9, dtype=np.uint8)
    # Both composition checks are training rewards on all nine primitive pairs.
    left = rows[:, forward_rows] == points
    right = forward_rows[rows] == points
    matches = left.sum(axis=1) + right.sum(axis=1)
    best, best_rank, trace = None, None, []
    for index, value in enumerate(matches):
        program = _program(first, second, index)
        rank = (-int(value), program_gate_count(program), program)
        if best_rank is None or rank < best_rank:
            best, best_rank = index, rank
            trace.append({"candidate": index, "round_trip_matches": int(value),
                          "gate_count": program_gate_count(program)})
    return best, {"candidates_scored": len(rows), "round_trip_training_pairs": list(PAIRS),
                  "round_trip_total": 18, "initial_round_trip_matches": int(matches[0]),
                  "final_round_trip_matches": int(matches[best]),
                  "left_round_trip_matches": int(left[best].sum()),
                  "right_round_trip_matches": int(right[best].sum()),
                  "improvement_trace": trace,
                  "selection": "both round trips on all nine pairs, then gates and syntax"}


def _braid_words(program, triple):
    left, right = list(triple), list(triple)
    for position in (0, 1, 0):
        left[position:position + 2] = apply(program, left[position:position + 2])
    for position in (1, 0, 1):
        right[position:position + 2] = apply(program, right[position:position + 2])
    return tuple(left), tuple(right)


def assess_program(program):
    """Post-freeze assessment through the actual primitive AST interpreter."""
    outputs = [apply(program, pair) for pair in PAIRS]
    dependent = []
    for coordinate in (0, 1):
        table = np.asarray([pair[coordinate] for pair in outputs]).reshape(3, 3)
        dependent.append({"x": bool(np.any(table != table[:1, :])),
                          "y": bool(np.any(table != table[:, :1]))})
    result = {"bijection": len(set(outputs)) == 9,
              "mixing": any(row["x"] and row["y"] for row in dependent),
              "coordinate_dependencies": dependent,
              "noninvolutive": any(apply(program, value) != pair for pair, value in zip(PAIRS, outputs, strict=True)),
              "diagonal_matches": sum(apply(program, (label, label)) == (label, label) for label in LABELS),
              "gate_count": program_gate_count(program)}
    for name, triples in (("train", TRAIN_TRIPLES), ("held_out", HELD_OUT_TRIPLES),
                          ("all", tuple(product(LABELS, repeat=3)))):
        rows = [{"input": triple, "left": left, "right": right, "equal": left == right}
                for triple in triples for left, right in (_braid_words(program, triple),)]
        result[f"braid_{name}"] = {"correct": sum(row["equal"] for row in rows),
                                   "total": len(rows), "rows": rows}
    return result


def trivial_programs():
    return {"identity": tuple(("input", i) for i in range(6)),
            "swap": tuple(("input", i) for i in (3, 4, 5, 0, 1, 2))}


def assess_fitted(fitted):
    """Assess frozen moves after the owner freezes its COMPLETE joint policy.

    This function does not alter the fitted object and is never called by
    fit(assess_after=False). It returns fresh diagnostic records only.
    """
    started = time.perf_counter()
    checkpoint = fitted["checkpoint"]
    checkpoint_sha = fitted["checkpoint_sha256"]
    ablation_program = fitted["ablation"]["forward"]
    ablation_sha = fitted["ablation"]["sha256"]
    if canonical_sha256(checkpoint) != checkpoint_sha or canonical_sha256(ablation_program) != ablation_sha:
        raise ValueError("A fitted atomic program changed before assessment")
    assessment = {"forward": assess_program(checkpoint["forward"]),
                  "inverse": assess_program(checkpoint["inverse"]),
                  "no_braid": assess_program(ablation_program)}
    round_trips = []
    for pair in PAIRS:
        inverse_after_forward = apply(checkpoint["inverse"], apply(checkpoint["forward"], pair))
        forward_after_inverse = apply(checkpoint["forward"], apply(checkpoint["inverse"], pair))
        round_trips.append({"input": pair, "inverse_after_forward": inverse_after_forward,
                            "forward_after_inverse": forward_after_inverse,
                            "left_equal": inverse_after_forward == pair,
                            "right_equal": forward_after_inverse == pair})
    assessment["round_trips"] = {"correct": sum(row["left_equal"] + row["right_equal"] for row in round_trips),
                                 "total": 18, "rows": round_trips}
    if (assessment["round_trips"]["correct"] != fitted["training"]["inverse_search"]["final_round_trip_matches"]
            or assessment["forward"]["braid_train"]["correct"]
            != fitted["training"]["forward_search"]["final_score"]["training_braid_matches"]):
        raise ValueError("Frozen primitive execution disagreed with accelerated training reward")
    controls = {}
    for name, program in trivial_programs().items():
        controls[name] = {"program": program, "assessment": assess_program(program),
                          "round_trip_matches": 2 * sum(apply(program, apply(program, pair)) == pair for pair in PAIRS),
                          "round_trip_total": 18}
    if canonical_sha256(checkpoint) != checkpoint_sha or canonical_sha256(ablation_program) != ablation_sha:
        raise ValueError("Post-freeze assessment altered a selected atomic program")
    return {"post_freeze": assessment, "trivial_controls": controls,
            "checkpoint_sha256_after_assessment": checkpoint_sha,
            "assessment_seconds": time.perf_counter() - started}


def fit(assess_after=True):
    started = time.perf_counter()
    predicates, enumeration = enumerate_predicates(5)
    for predicate in predicates.values():
        if expression_mask(predicate.expr) != predicate.mask or gate_count(predicate.expr) != predicate.gates:
            raise ValueError("An enumerated predicate disagreed with its primitive expression")
    first, second = register_catalogue(predicates, 0), register_catalogue(predicates, 1)
    if len(first) != 216 or len(second) != 216:
        raise ValueError("The declared predicate grammar did not form the full typed register catalogue")
    rows = training_pair_rows(first, second)
    metrics = _point_metrics(rows, first, second)
    # This selector receives no braid array. Freeze its choice before asking
    # the primary training scorer about any braid identity.
    ablation_index, ablation_search = select_forward(first, second, metrics)
    ablation_program = _program(first, second, ablation_index)
    ablation_program = json.loads(json.dumps(ablation_program))
    ablation_sha = canonical_sha256(ablation_program)
    braid = _braid_matches(rows, TRAIN_TRIPLES)
    forward_index, forward_search = select_forward(first, second, metrics, braid)
    inverse_index, inverse_search = select_inverse(first, second, rows, rows[forward_index])
    checkpoint = {"schema_version": 1, "encoding": "two ternary one-hot labels",
                  "input_bits": ["x_eq0", "x_eq1", "x_eq2", "y_eq0", "y_eq1", "y_eq2"],
                  "output_bits": ["first_eq0", "first_eq1", "first_eq2", "second_eq0", "second_eq1", "second_eq2"],
                  "forward": _program(first, second, forward_index),
                  "inverse": _program(first, second, inverse_index)}
    checkpoint = json.loads(json.dumps(checkpoint, sort_keys=True, separators=(",", ":")))
    checkpoint_sha = canonical_sha256(checkpoint)
    fit_seconds = time.perf_counter() - started
    result = {"schema_version": 1, "deterministic_fits": 1,
            "checkpoint": checkpoint, "checkpoint_sha256": checkpoint_sha,
            "ablation": {"forward": ablation_program, "sha256": ablation_sha,
                         "training_without_braid": ablation_search},
            "training": {"predicate_enumeration": enumeration,
                         "coordinate0_registers": len(first), "coordinate1_registers": len(second),
                         "joined_program_pairs": len(rows),
                         "supplied_prior": "one-hot labels; output0 permutes y per x and output1 permutes x per y",
                         "forward_selection": "bijection, mixing, non-involution, training braid, diagonal, gates, syntax",
                         "pair_points_used": list(PAIRS), "braid_triples": TRAIN_TRIPLES,
                         "held_out_unit": "six all-distinct triples; primitive pairs are familiar",
                         "forward_search": forward_search, "inverse_search": inverse_search,
                         "forward_training_truth_rows": rows[forward_index].tolist(),
                         "inverse_training_truth_rows": rows[inverse_index].tolist(),
                         "accelerated_braid_pair_applications": len(rows) * len(TRAIN_TRIPLES) * 6,
                         "inverse_round_trip_pair_applications": len(rows) * 9 * 4},
            "assessed_after_fit": bool(assess_after),
            "actions_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "numpy_version": np.__version__,
            "runtime_seconds": {"fit": fit_seconds,
                                "assessment": 0.0, "total": fit_seconds}}
    if assess_after:
        assessment = assess_fitted(result)
        result.update(assessment)
        result["runtime_seconds"]["assessment"] = assessment["assessment_seconds"]
    result["runtime_seconds"]["total"] = time.perf_counter() - started
    return result


train = fit


def smoke():
    # Synthetic primitive checks only: do not enumerate/select a crossing.
    predicates, enumeration = enumerate_predicates(1)
    checked = 0
    for predicate in predicates.values():
        if expression_mask(predicate.expr) != predicate.mask or gate_count(predicate.expr) != predicate.gates:
            raise ValueError("Primitive predicate mask or cost was invalid")
        checked += 9
    for name, program in trivial_programs().items():
        for pair in PAIRS:
            expected = pair if name == "identity" else pair[::-1]
            if apply(program, pair) != expected:
                raise ValueError("Raw one-hot primitive interpreter changed a zero-gate control")
    # Compare accelerated composition with actual ASTs on these fixed controls.
    programs = tuple(trivial_programs().values())
    rows = np.asarray([[3 * apply(program, pair)[0] + apply(program, pair)[1] for pair in PAIRS]
                       for program in programs], dtype=np.uint8)
    toy_triples = ((0, 0, 1), (0, 1, 0))
    matches = _braid_matches(rows, toy_triples)
    if matches.tolist() != [2, 2]:
        raise ValueError("Synthetic Boolean composition accelerator disagreed with primitive controls")
    return {"smoke_only_no_fit": True, "primitive_assignments_checked": checked,
            "predicate_enumeration": enumeration,
            "zero_gate_controls_executed": list(trivial_programs()),
            "synthetic_composition_matches": matches.tolist(),
            "actions_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "numpy_version": np.__version__}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", action="store_true", help="perform the declared structural fit")
    parser.add_argument("--smoke", action="store_true", help="only check synthetic primitives")
    args = parser.parse_args()
    if args.train and args.smoke:
        parser.error("Choose --train or --smoke")
    print(json.dumps(fit() if args.train else smoke(), sort_keys=True))


if __name__ == "__main__":
    main()
