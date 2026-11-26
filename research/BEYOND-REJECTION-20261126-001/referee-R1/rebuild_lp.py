"""Rebuild the whole-round record programs from the preparation and funding laws."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod, sqrt
from pathlib import Path
import json
import resource
from time import perf_counter
import warnings

import numpy as np
from scipy.optimize import OptimizeWarning, linprog


BITS = (0, 1)
ADDRESSES = tuple(product(BITS, repeat=2))
TRIPLES = tuple(product(BITS, repeat=3))
LAWS = ("parity", "not-all-equal")
REFERENCE_SIGNS = (1, 1, 1, -1)
CHSH_SIGNS = tuple(signs for signs in product((1, -1), repeat=4) if prod(signs) == -1)
SIGNED_THRESHOLDS = ("2", "2.001", "2.25", "2.5", "sqrt(8)", "3", "4")


def correspondence(preparation, reverse=False):
    u, v = preparation
    first = (1, 0, 2) if u else (0, 1, 2)
    second = (0, 2, 1) if v else (0, 1, 2)
    if reverse:
        first, second = second, first
    return tuple(second[first[second[first[i]]]] for i in range(3))


@dataclass(frozen=True)
class State:
    preparation: tuple
    terminals: tuple

    def record(self, settings, reader):
        return self.preparation[reader], self.terminals[reader], int(settings == self.preparation)

    def outcome(self, settings):
        if settings == self.preparation:
            return tuple(values[0] for values in self.terminals)
        return 0, 0


def states_for(law, reverse=False):
    states = []
    for preparation in ADDRESSES:
        order = correspondence(preparation, reverse)
        for left, right in product(TRIPLES, repeat=2):
            if law == "parity" and any(left[i] != right[order[i]] for i in range(3)):
                continue
            states.append(State(preparation, (left, right)))
    return tuple(states)


def knot_allows(law, values):
    ones = sum(values)
    return ones % 2 == 0 if law == "parity" else 0 < ones < len(values)


def one_correspondence(law):
    return tuple(tuple(sum(knot_allows(law, (left, *pair)) and knot_allows(law, (right, *pair))
                           for pair in ADDRESSES) for right in BITS) for left in BITS)


def endpoint_count(law, preparation, terminal):
    total = 0
    for bits in product(BITS, repeat=10):
        center = bits[:5]
        links = (center[:2], center[2:4])
        short_address = links[preparation] + bits[5:6]
        long_address = links[1 - preparation] + bits[6:8]
        detector = (center[4],) + terminal + bits[8:]
        total += all(knot_allows(law, values) for values in
                     (center, short_address, long_address, detector))
    return total


def earlier_weighting(law, states):
    single = one_correspondence(law)
    eight = np.linalg.matrix_power(np.asarray(single, dtype=np.int64), 8).tolist()
    endpoint = {(shortage, terminal): endpoint_count(law, shortage, terminal)
                for shortage, terminal in product(BITS, TRIPLES)}
    counts = {}
    for state in states:
        u, v = state.preparation
        left, right = state.terminals
        order = correspondence(state.preparation)
        counts[state] = endpoint[u, left] * endpoint[v, right] * prod(
            eight[left[i]][right[order[i]]] for i in range(3))
    assert min(counts.values()) > 0
    preparation_counts = Counter()
    for state, count in counts.items():
        preparation_counts[state.preparation] += count
    assert len(set(preparation_counts.values())) == 1
    denominator = sum(counts.values())
    return {state: Fraction(count, denominator) for state, count in counts.items()}, {
        "one_pair_completion_counts": single,
        "eight_pair_completion_counts": eight,
        "endpoint_completion_counts": [
            [shortage, terminal, count] for (shortage, terminal), count in endpoint.items()
        ],
        "old_assignments_per_preparation": list(preparation_counts.values()),
    }


def far_choices(receiver, own_setting):
    return ((own_setting, 0), (own_setting, 1)) if receiver == 0 else ((0, own_setting), (1, own_setting))


def visible_before_choice(state, sender, access):
    if access == "hidden":
        return state.terminals[sender]
    return state.preparation[sender], state.terminals[sender]


def contrast_rows(states, access):
    rows = []
    keys_compared = 0
    for receiver, own_setting in product(BITS, repeat=2):
        context0, context1 = far_choices(receiver, own_setting)
        record_contrasts = defaultdict(Counter)
        for column, state in enumerate(states):
            visible = None if access == "fixed" else visible_before_choice(state, 1 - receiver, access)
            record_contrasts[state.record(context0, receiver), visible][column] += 1
            record_contrasts[state.record(context1, receiver), visible][column] -= 1
        keys_compared += len(record_contrasts)
        for contrast in record_contrasts.values():
            nonzero = tuple(sorted((index, count) for index, count in contrast.items() if count))
            if nonzero:
                rows.append(nonzero)
    return tuple(rows), keys_compared


def matrix_from_rows(rows, width):
    matrix = np.zeros((len(rows), width))
    for line, row in enumerate(rows):
        for column, value in row:
            matrix[line, column] = value
    return matrix


def joint_record_rows(states):
    rows = []
    for settings in ADDRESSES:
        joint = defaultdict(list)
        for index, state in enumerate(states):
            joint[state.record(settings, 0), state.record(settings, 1)].append((index, 1))
        assert len(joint) == len(states)
        assert all(len(row) == 1 for row in joint.values())
        rows.extend(joint.values())
    return rows


def law_of_receiver(weights, receiver, own_setting, access, other_address):
    law = Counter()
    for state, weight in weights.items():
        label = visible_before_choice(state, 1 - receiver, access)
        settings = far_choices(receiver, own_setting)[other_address(label)]
        law[state.record(settings, receiver)] += weight
    return law


def check_weights(states, weights, access):
    assert set(weights) <= set(states)
    assert sum(weights.values()) == 1
    for settings in ADDRESSES:
        observable = Counter()
        for state, weight in weights.items():
            observable[state.record(settings, 0), state.record(settings, 1)] += weight
        assert all(probability >= 0 for probability in observable.values())
    for receiver, own_setting in product(BITS, repeat=2):
        base = law_of_receiver(weights, receiver, own_setting, access, lambda label: 0)
        assert base == law_of_receiver(weights, receiver, own_setting, access, lambda label: 1)
        if access != "fixed":
            labels = {visible_before_choice(state, 1 - receiver, access) for state in weights}
            for selected in labels:
                assert base == law_of_receiver(weights, receiver, own_setting, access,
                                              lambda label: int(label == selected))


def correlations(weights):
    totals = []
    for settings in ADDRESSES:
        difference = sum(weight for state, weight in weights.items()
                         if state.outcome(settings) in ((0, 1), (1, 0)))
        totals.append(1 - 2 * difference)
    return tuple(totals)


def score(values, signs=REFERENCE_SIGNS):
    return sum(sign * value for sign, value in zip(signs, values))


def weighting_receipt(weights, retain_witness=False):
    values = correlations(weights)
    receipt = {
        "correlations": [str(value) for value in values],
        "chsh": str(score(values)),
        "largest_chsh": str(max(score(values, signs) for signs in CHSH_SIGNS)),
        "supported_states": len(weights),
    }
    if retain_witness:
        receipt["weights"] = [[*state.preparation, *("".join(map(str, t)) for t in state.terminals), str(weight)]
                              for state, weight in weights.items()]
    return receipt


def uniform(states):
    return dict.fromkeys(states, Fraction(1, len(states)))


def exact_controls(law, states, row_families):
    indexed = {state: index for index, state in enumerate(states)}
    visible_rows = set(row_families["visible"][0])
    for index in indexed.values():
        assert ((index, 1),) in visible_rows or ((index, -1),) in visible_rows

    hidden_rows = set(row_families["hidden"][0])
    for terminals in product(TRIPLES, repeat=2):
        for axis, other in product(BITS, repeat=2):
            contrast = []
            for changed in BITS:
                preparation = (changed, other) if axis == 0 else (other, changed)
                index = indexed.get(State(preparation, terminals))
                if index is not None:
                    contrast.append((index, 1 - 2 * changed))
            if contrast:
                assert tuple(sorted(contrast)) in hidden_rows

    counts = Counter(state.terminals for state in states)
    surviving = {terminals for terminals, count in counts.items() if count == 4}
    for terminals in sorted(surviving):
        witness = uniform([state for state in states if state.terminals == terminals])
        check_weights(states, witness, "hidden")
    hidden = uniform([state for state in states if state.terminals in surviving])
    check_weights(states, hidden, "hidden")
    agree = uniform([state for state in states if state.terminals == ((0, 0, 0), (0, 0, 0))])
    check_weights(states, agree, "hidden")

    earlier, completion_counts = earlier_weighting(law, states)
    check_weights(states, earlier, "fixed")
    reduced_uniform = uniform(states)
    check_weights(states, reduced_uniform, "fixed")
    if law == "parity":
        fixed = uniform([state for state in states if sum(state.terminals[0]) == 1])
        assert earlier == reduced_uniform
        assert score(correlations(reduced_uniform)) == Fraction(9, 4)
        assert score(correlations(fixed)) == Fraction(7, 3)
        assert surviving == {((0, 0, 0), (0, 0, 0)), ((1, 1, 1), (1, 1, 1))}
        assert score(correlations(hidden)) == 2

        def relabel(values):
            return values[0], values[2], values[1]

        transported = {State(state.preparation, tuple(map(relabel, state.terminals))): weight
                       for state, weight in fixed.items()}
        reverse_states = states_for(law, reverse=True)
        assert {State(state.preparation, tuple(map(relabel, state.terminals))) for state in states} == set(reverse_states)
        check_weights(reverse_states, transported, "fixed")
        assert correlations(fixed) == correlations(transported)
        disjoint_hidden = None
    else:
        fixed = uniform([state for state in states
                         if all(sum(values) in (0, 3) for values in state.terminals)
                         and ((state.terminals[0] != state.terminals[1]) == (state.preparation == (1, 1)))])
        assert score(correlations(earlier)) == Fraction(21480051994324169922, 14320015907287890625)
        assert score(correlations(fixed)) == Fraction(5, 2)
        assert len(surviving) == 64
        assert score(correlations(hidden)) == Fraction(3, 2)
        disagree = uniform([state for state in states if state.terminals == ((0, 0, 0), (1, 1, 1))])
        check_weights(states, disagree, "hidden")
        assert score(correlations(disagree)) == 1
        disjoint_hidden = weighting_receipt(disagree, retain_witness=True)
        transported = None

    check_weights(states, fixed, "fixed")
    return {
        **completion_counts,
        "visible_policy_forces_each_weight_zero": True,
        "hidden_surviving_terminal_pairs": len(surviving),
        "hidden_surviving_states": len(hidden),
        "hidden_each_terminal_pair_individually_feasible": True,
        "record_uniform_weighting": weighting_receipt(reduced_uniform),
        "earlier_old_assignment_uniform_weighting": weighting_receipt(earlier),
        "fixed_independent_maximum_witness": weighting_receipt(fixed, retain_witness=True),
        "fixed_inverse_correspondence_witness": weighting_receipt(transported, True) if transported else None,
        "hidden_uniform_on_surviving_support": weighting_receipt(hidden),
        "hidden_independent_maximum_witness": weighting_receipt(agree, retain_witness=True),
        "hidden_disagreeing_witness": disjoint_hidden,
    }


@dataclass(frozen=True)
class Case:
    law: str
    access: str
    signed: bool
    signs: tuple = REFERENCE_SIGNS
    threshold: str | None = None

    def timing_group(self):
        return self.access, "threshold" if self.threshold else "signed" if self.signed else "ordinary"


def all_cases():
    for law, signed, access in product(LAWS, (False, True), ("fixed", "visible", "hidden")):
        signs_to_run = (REFERENCE_SIGNS,) if access == "visible" else CHSH_SIGNS
        for signs in signs_to_run:
            yield Case(law, access, signed, signs=signs)
    for law, access, threshold in product(LAWS, ("visible", "hidden"), SIGNED_THRESHOLDS):
        yield Case(law, access, True, threshold=threshold)


PILOT_CASES = {
    Case("parity", "fixed", False),
    *(Case("not-all-equal", access, signed)
      for signed, access in product((False, True), ("fixed", "visible", "hidden"))),
    Case("not-all-equal", "visible", True, threshold="2"),
    Case("not-all-equal", "hidden", True, threshold="2"),
    Case("not-all-equal", "hidden", True, threshold="2.001"),
}


def solve(case, states, rows, keys_compared, joint):
    begin = perf_counter()
    n_states = len(states)
    normalization = tuple((index, 1) for index in range(n_states))
    equalities = matrix_from_rows((normalization, *rows), n_states)
    right = np.zeros(equalities.shape[0])
    right[0] = 1
    score_terms = np.array([sum(sign * (-1 if state.outcome(settings) in ((0, 1), (1, 0)) else 1)
                                for sign, settings in zip(case.signs, ADDRESSES)) for state in states])
    objective = -score_terms
    inequalities = -joint if case.signed else None
    upper = np.zeros(joint.shape[0]) if case.signed else None
    bounds = (None, None) if case.signed else (0, None)
    threshold = None
    if case.threshold:
        threshold = sqrt(8) if case.threshold == "sqrt(8)" else float(case.threshold)
        equalities = np.hstack((equalities, -equalities))
        inequalities = np.vstack((inequalities, -score_terms))
        inequalities = np.hstack((inequalities, -inequalities))
        upper = np.append(upper, -threshold)
        objective = np.concatenate((np.zeros(n_states), np.ones(n_states)))
        bounds = (0, None)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Unrecognized options detected.*", category=OptimizeWarning)
        result = linprog(objective, A_ub=inequalities, b_ub=upper, A_eq=equalities, b_eq=right,
                         bounds=bounds, method="highs-ds", options={"threads": 1, "parallel": False})
    expected_feasible = case.access != "visible" and (threshold is None or threshold <= 2)
    assert result.status == (0 if expected_feasible else 2), result.message
    receipt = {
        "law": case.law,
        "sender_access": case.access,
        "signed": case.signed,
        "signs": case.signs,
        "threshold": case.threshold,
        "states": n_states,
        "variables": len(objective),
        "compared_record_keys": keys_compared,
        "equalities_including_normalization": equalities.shape[0],
        "nonnegative_joint_record_probabilities": joint.shape[0] if case.signed else 0,
        "inequalities_excluding_variable_bounds": 0 if inequalities is None else inequalities.shape[0],
        "status": "feasible" if result.success else "infeasible",
    }
    if result.success:
        rational = [Fraction(float(value)).limit_denominator(1_000_000) for value in result.x]
        atoms = rational[:n_states]
        if threshold is not None:
            negative = rational[n_states:]
            assert min(rational) >= 0
            atoms = [plus - minus for plus, minus in zip(atoms, negative)]
            assert sum(negative) == 0
            receipt["least_negative_mass"] = str(sum(negative))
        weights = {state: weight for state, weight in zip(states, atoms) if weight}
        check_weights(states, weights, case.access)
        exact_score = score(correlations(weights), case.signs)
        if threshold is None:
            assert abs(float(exact_score) + result.fun) < 1e-9
        else:
            assert exact_score >= Fraction(case.threshold)
        receipt["chsh_at_returned_weighting"] = str(exact_score)
        receipt["supported_states_at_returned_weighting"] = len(weights)
        receipt["returned_weighting_checked_exactly"] = True
    receipt["seconds"] = perf_counter() - begin
    return receipt


def run(pilot):
    begin = perf_counter()
    preparations = {}
    controls = {}
    for law in LAWS:
        states = states_for(law)
        families = {access: contrast_rows(states, access) for access in ("fixed", "visible", "hidden")}
        joint = matrix_from_rows(joint_record_rows(states), len(states))
        controls[law] = exact_controls(law, states, families)
        preparations[law] = states, families, joint
    preparation_seconds = perf_counter() - begin

    receipts = []
    timing_groups = defaultdict(list)
    full_counts = Counter()
    maxima = defaultdict(list)
    for case in all_cases():
        full_counts[case.timing_group()] += 1
        if pilot and case not in PILOT_CASES:
            continue
        states, families, joint = preparations[case.law]
        rows, compared_keys = families[case.access]
        result = solve(case, states, rows, compared_keys, joint)
        receipts.append(result)
        timing_groups[case.timing_group()].append(result["seconds"])
        if case.threshold is None and result["status"] == "feasible":
            maxima[case.law, case.access, case.signed].append(Fraction(result["chsh_at_returned_weighting"]))

    fixed_maximum = {"parity": Fraction(7, 3), "not-all-equal": Fraction(5, 2)}
    for (law, access, signed), values in maxima.items():
        assert max(values) == (fixed_maximum[law] if access == "fixed" else 2)
        if not pilot and access == "hidden":
            assert min(values) == (-2 if law == "parity" else -1)

    estimate = preparation_seconds + sum(full_counts[group] * max(times) for group, times in timing_groups.items())
    return {
        "run": "pilot" if pilot else "full",
        "state_order": "preparation (u,v), left terminals, right terminals",
        "terminal_correspondences": [correspondence(preparation) for preparation in ADDRESSES],
        "comparison_method": "receiver's record jointly with the sender's visible pre-edit record, from singleton switches",
        "signed_observable_positivity": "all joint records identify their state at each setting, so negative weights violate observable nonnegativity",
        "controls": controls,
        "cases": receipts,
        "case_count": len(receipts),
        "full_case_count": sum(full_counts.values()),
        "timing_by_group": [{"access": access, "program": program, "timed_cases": len(timing_groups[access, program]),
                             "slowest_case_seconds": max(timing_groups[access, program]),
                             "full_cases": full_counts[access, program]}
                            for access, program in sorted(timing_groups)],
        "preparation_seconds": preparation_seconds,
        "estimated_full_seconds_from_run": estimate,
        "wall_seconds": perf_counter() - begin,
        "peak_resident_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "address_space_limit_bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
        "solver_threads": 1,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", required=True, type=Path)
    arguments = parser.parse_args()
    arguments.out.write_text(json.dumps(run(arguments.pilot), indent=2) + "\n")
