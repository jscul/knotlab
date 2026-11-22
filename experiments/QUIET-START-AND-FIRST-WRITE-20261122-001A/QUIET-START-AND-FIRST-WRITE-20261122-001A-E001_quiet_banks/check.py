"""Exhaust the frozen quiet founder's three local filling policies."""

from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import product
from math import prod
import json
from pathlib import Path
from runpy import run_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research/QUIET-START-AND-FIRST-WRITE-20261122-001/design_candidate.md"
DESIGN_HASH = "b3418bfde5b86c84564929d8d9a7f7a73b74cc21fb6b13f0bd1c8f1b90c41ff0"
PREDECESSOR, = (ROOT / "experiments/WRITTEN-BIT-AND-JOIN-VETO-20261122-001A").glob("*/check.py")
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "results.json"
OLD = run_path(str(PREDECESSOR))
State = OLD["State"]
bits = OLD["bits"]
OUTCOMES = ("missing", "join", "veto_with_H_payment_deviation", "veto_without_H_payment_deviation")
EARLIEST = ("cut_1", "cut_2", "cut_3", "none")
POLICIES = ("M", "F", "A")


def all_fresh(policy, cut):
    return policy == "A" or (policy == "F" and cut == 1)


@cache
def local_bank(law, transport, paid_reference, paid_actual, width, allow_all):
    is_legal = OLD["lawful"]
    candidates = tuple(product((0, 1), repeat=width))
    legal_reference = tuple(w for w in candidates if is_legal(law, paid_reference + w))
    assert legal_reference
    ref = legal_reference[0]
    if transport == "opposite" and len(set(paid_reference)) == 1:
        ref = (1 - paid_reference[0],) * width
    assert ref in legal_reference
    words = tuple(w for w in candidates if is_legal(law, paid_actual + w))
    assert words
    if allow_all:
        return ref, words
    changes = {w: sum(a != b for a, b in zip(w, ref, strict=True)) for w in words}
    return ref, tuple(w for w in words if changes[w] == min(changes.values()))


def bank_factors(law, transport, state, rows, allow_all):
    return tuple(local_bank(law, transport, tuple(state.reference[i] for i in b.paid),
                            tuple(state.actual[i] for i in b.paid), len(b.fresh), allow_all) for b in rows)


def extensions(law, transport, state, rows, allow_all):
    fs = bank_factors(law, transport, state, rows, allow_all)
    if not allow_all:
        assert fs == OLD["factors"](law, transport, state, rows)
    reference = tuple(r for r, _ in fs)
    denominator = prod(len(choices) for _, choices in fs)
    for actual in product(*(choices for _, choices in fs)):
        yield OLD["materialize"](law, state, rows, reference, actual), actual, denominator


class StructuralPlans:
    """The ordinary roster and the veto depend on holdings and hot parents only."""

    def __init__(self, law):
        self.law = law
        self.by_hot_set = {}
        self.rows = {}

    def read(self, state, feedback):
        if state.holdings not in self.rows:
            self.rows[state.holdings] = OLD["loose_names"](state.holdings)
        live = self.rows[state.holdings]
        hot = tuple(v for v in live if any(state.actual[i] != state.reference[i] for i in state.holdings[v])) if feedback else ()
        key = (state.holdings, feedback, hot)
        if key not in self.by_hot_set:
            plan = OLD["plan"](self.law, state, feedback)
            births = OLD["bind"](state, plan) if plan["status"] == "extend" else ()
            self.by_hot_set[key] = plan, births
        return self.by_hot_set[key]


def h_birth(first_rows):
    h, = (b for b in first_rows if b.paid == (0,))
    return h


def inspect_target(state, h, second_rows, actual_plan, ordinary_plan):
    recipients = {b.paid[0]: b for b in second_rows if b.parents == (h.holder,)}
    if not all(i in recipients for i in h.fresh[:2]):
        return {"outcome": "missing", "reason": "one or both H payments have no separate unary recipient"}
    pair = tuple(sorted(recipients[i].holder for i in h.fresh[:2]))
    ordinary_candidates = {g["parents"] for g in ordinary_plan["guard_table"]}
    if pair not in ordinary_candidates or ordinary_plan["status"] != "extend":
        return {"outcome": "missing", "reason": "target does not have an ordinary funded proposal", "parents": pair}
    union = tuple(sorted(set().union(*(set(state.holdings[parent]) for parent in pair))))
    assert len(union) == 6 and set(h.fresh) <= set(union) and not set(union).intersection((0, 1, 2))
    differences = OLD["differences"](state, union)
    carriers = tuple(i for i in differences if i in h.fresh)
    remaining = tuple(i for i in differences if i not in h.fresh)
    matched, = (g for g in actual_plan["guard_table"] if g["parents"] == pair)
    if matched["action"] == "keep":
        outcome = "join"
    else:
        assert differences
        outcome = "veto_with_H_payment_deviation" if carriers else "veto_without_H_payment_deviation"
    return {"outcome": outcome, "parents": pair, "six_place_union": union, "differences": differences,
            "actual_on_union": bits(state.actual[i] for i in union), "reference_on_union": bits(state.reference[i] for i in union),
            "H_fresh_marks_in_difference": carriers, "differences_after_auditor_masks_H_marks": remaining,
            "audit_mask_still_vetoes": bool(remaining), "sole_H_mark": carriers[0] if len(differences) == 1 and carriers else None}


def first_factoring(law, transport, start, first_rows):
    complete = bank_factors(law, transport, start, first_rows, True)
    minimum = bank_factors(law, transport, start, first_rows, False)
    h = h_birth(first_rows)
    assert first_rows[0] == h and tuple(b.paid for b in first_rows) == ((0,), (1,), (2,))
    assert all(words == (ref,) for ref, words in minimum)
    return {"first_cut_births": [OLD["serialize_birth"](b) for b in first_rows],
            "all_legal_banks_in_H_U_J_order": [list(map(bits, choices)) for _, choices in complete],
            "reference_banks_in_H_U_J_order": [bits(ref) for ref, _ in complete],
            "minimum_banks_in_H_U_J_order": [list(map(bits, choices)) for _, choices in minimum],
            "all_lawful_first_triples": [tuple(map(bits, w)) for w in product(*(choices for _, choices in complete))],
            "H_deviation_allowed_under_all_lawful": len(complete[0][1]) > 1,
            "H_deviation_forced_under_all_lawful": complete[0][0] not in complete[0][1]}


class Counts:
    def __init__(self):
        self.first = self.predecision = self.terminal = 0
        self.first_probability = Fraction(0)
        self.outcomes = Counter()
        self.outcome_terminal = Counter()
        self.masses = defaultdict(Fraction)
        self.earliest = Counter()
        self.earliest_probability = defaultdict(Fraction)
        self.audit = Counter()
        self.audit_probability = defaultdict(Fraction)
        self.missing = Counter()
        self.funding_status = Counter()

    def add_first(self, weight):
        self.first += 1
        self.first_probability += weight

    def record(self, detail, weight, terminal_fills, earliest, status):
        outcome = detail["outcome"]
        self.predecision += 1
        self.terminal += terminal_fills
        self.outcomes[outcome] += 1
        self.outcome_terminal[outcome] += terminal_fills
        self.masses[outcome] += weight
        self.funding_status[status] += 1
        if "reason" in detail:
            self.missing[detail["reason"]] += 1
        if earliest is not None:
            self.earliest[earliest] += terminal_fills
            self.earliest_probability[earliest] += weight
        elif terminal_fills:
            # On a quiet incoming state exactly one permitted fill is the lawful reference.
            self.earliest["none"] += 1
            self.earliest["cut_3"] += terminal_fills - 1
            self.earliest_probability["none"] += weight / terminal_fills
            self.earliest_probability["cut_3"] += weight * (terminal_fills - 1) / terminal_fills
        if outcome.startswith("veto"):
            labels = ["audit_mask_keeps_veto" if detail["audit_mask_still_vetoes"] else "audit_mask_clears_veto"]
            carriers = detail["H_fresh_marks_in_difference"]
            labels.append(f"H_carriers_{len(carriers)}")
            if detail["sole_H_mark"] is not None:
                labels.append(f"sole_H_mark_{detail['sole_H_mark']}")
            for label in labels:
                self.audit[label] += 1
                self.audit_probability[label] += weight

    def summary(self):
        assert sum(self.outcomes.values()) == self.predecision
        assert sum(self.masses.values()) == self.first_probability
        assert sum(self.earliest.values()) == self.terminal
        assert sum(self.earliest_probability.values()) == self.first_probability
        return {"first_bank_assignments": self.first, "initial_mass": self.first_probability,
                "predecision_histories": self.predecision, "terminal_histories": self.terminal,
                "predecision_count_by_outcome": {k: self.outcomes[k] for k in OUTCOMES},
                "terminal_count_by_outcome": {k: self.outcome_terminal[k] for k in OUTCOMES},
                "initial_mass_by_outcome": {k: self.masses[k] for k in OUTCOMES},
                "conditional_mass_by_outcome": {k: self.masses[k] / self.first_probability for k in OUTCOMES},
                "terminal_count_by_first_deviation": {k: self.earliest[k] for k in EARLIEST},
                "initial_mass_by_first_deviation": {k: self.earliest_probability[k] for k in EARLIEST},
                "veto_diagnostics_predecision_counts": self.audit,
                "veto_diagnostics_initial_mass": self.audit_probability,
                "funding_status_predecision_counts": self.funding_status, "missing_reasons_predecision_counts": self.missing}


def census(law, transport, start, policy, feedback, planner):
    first_plan, first_rows = planner.read(start, feedback)
    assert first_plan["status"] == "extend"
    h = h_birth(first_rows)
    overall, by_first, by_others = Counts(), {}, defaultdict(Counts)
    for at_two, realized, first_denominator in extensions(law, transport, start, first_rows, all_fresh(policy, 1)):
        label = "|".join(map(bits, realized))
        background = "|".join(map(bits, realized[1:]))
        assert label not in by_first
        by_first[label] = Counts()
        ledgers = (overall, by_first[label], by_others[background])
        first_mass = Fraction(1, first_denominator)
        for ledger in ledgers:
            ledger.add_first(first_mass)
        second_plan, second_rows = planner.read(at_two, feedback)
        assert second_plan["status"] == "extend"
        first_quiet = at_two.actual == at_two.reference
        for at_three, _, second_denominator in extensions(law, transport, at_two, second_rows, all_fresh(policy, 2)):
            cut, third_rows = planner.read(at_three, feedback)
            ordinary_cut, _ = planner.read(at_three, False)
            detail = inspect_target(at_three, h, second_rows, cut, ordinary_cut)
            assert cut["status"] == "extend"
            if detail["outcome"] != "missing":
                target = detail["parents"]
                assert target in ordinary_cut["parent_roster"]
                assert (target in cut["parent_roster"]) == (detail["outcome"] == "join")
            last = bank_factors(law, transport, at_three, third_rows, all_fresh(policy, 3))
            count = prod(len(words) for _, words in last)
            weight = first_mass / second_denominator
            earlier = "cut_1" if not first_quiet else "cut_2" if at_three.actual != at_three.reference else None
            if earlier is None:
                assert all(ref in choices for ref, choices in last)
            for ledger in ledgers:
                ledger.record(detail, weight, count, earlier, cut["status"])
    assert overall.first_probability == 1
    assert sum(c.first_probability for c in by_others.values()) == 1
    value_ref = [r for r, _ in bank_factors(law, transport, start, first_rows, False)]
    reference_background = "|".join(map(bits, value_ref[1:]))
    return {"all_launches": overall.summary(), "by_first_H_U_J_words": {k: s.summary() for k, s in by_first.items()},
            "by_fixed_U_J_background": {k: s.summary() for k, s in by_others.items()},
            "quiet_U_J_background": reference_background,
            "H_comparison_with_both_siblings_quiet": {k: s.summary() for k, s in by_first.items()
                                                      if k.split("|", 1)[1] == reference_background}}


def trace_cut(law, transport, state, policy, cut, feedback, at_birth=None):
    decision = OLD["plan"](law, state, feedback)
    births = OLD["bind"](state, decision)
    permitted = bank_factors(law, transport, state, births, all_fresh(policy, cut))
    # Draw no outcome here: this read chooses a single permitted minimum only for display.
    minimum = bank_factors(law, transport, state, births, False)
    current = tuple(w[0] for _, w in minimum) if at_birth is None else at_birth
    assert all(word in allowed for word, (_, allowed) in zip(current, permitted, strict=True))
    actual = OLD["materialize"](law, state, births, tuple(ref for ref, _ in permitted), current)
    report = {**decision, "births": [OLD["serialize_birth"](b) for b in births],
              "reference": bits(actual.reference), "complete_actual": bits(actual.actual),
              "permitted_fresh_banks_in_birth_order": [list(map(bits, words)) for _, words in permitted],
              "displayed_fresh_word_in_birth_order": list(map(bits, current)),
              "number_of_permitted_current_cut_fills": prod(len(words) for _, words in permitted)}
    return actual, births, report


def representative(law, transport, start, policy, first_realized):
    at_two, first, trace1 = trace_cut(law, transport, start, policy, 1, True, first_realized)
    at_three, second, trace2 = trace_cut(law, transport, at_two, policy, 2, True)
    at_four, third, trace3 = trace_cut(law, transport, at_three, policy, 3, True)
    _, bypass, guard_off = trace_cut(law, transport, at_three, policy, 3, False)
    h = h_birth(first)
    detail = inspect_target(at_three, h, second, trace3, guard_off)
    target = detail.get("parents")
    if target is not None:
        trace3["actual_target_parent_payments"] = [OLD["serialize_birth"](b) for b in third if set(b.parents) & set(target)]
        guard_off["actual_target_join"] = next(OLD["serialize_birth"](b) for b in bypass if b.parents == target)
    assert at_four.actual[:len(at_three.actual)] == at_three.actual
    renaming = OLD["transport_names"](law, transport, at_three, True, first, second, target)
    writers = [name for name, row in zip(("H", "U", "J"), first, strict=True)
               if any(at_two.actual[i] != at_two.reference[i] for i in row.fresh)]
    return {"first_H_U_J_fresh_words": list(map(bits, first_realized)), "display_later_fills": "first minimizer only for display",
            "first_cut_writers_by_audit_role": writers,
            "first_cut": trace1, "second_cut": trace2, "target_read": detail,
            "third_cut": trace3, "guard_off_at_same_reached_stage": guard_off,
            "transported_enrollment_and_guard": renaming}


def matched_examples(law, transport, start, first_rows):
    allowed = bank_factors(law, transport, start, first_rows, True)
    ref = tuple(q for q, _ in allowed)
    h_alternatives = tuple(word for word in allowed[0][1] if word != ref[0])
    nonref_others = tuple(next(word for word in choices if word != q) for q, choices in allowed[1:])
    select_mass = Fraction(1, prod(len(choices) for _, choices in allowed[1:]))
    expected = {}
    for policy in ("F", "A"):
        chosen = [representative(law, transport, start, policy, (h, *nonref_others)) for h in (ref[0], *h_alternatives)]
        quiet_siblings = [representative(law, transport, start, policy, (h, *ref[1:])) for h in (ref[0], *h_alternatives)]
        first_quiet, *others = chosen
        comparisons = []
        for word in others:
            original, modified = first_quiet["second_cut"], word["second_cut"]
            assert original["births"] == modified["births"] and original["reference"] == modified["reference"]
            targets = (first_quiet["target_read"], word["target_read"])
            assert targets[0]["parents"] == targets[1]["parents"] and targets[0]["outcome"] == "join"
            assert targets[1]["outcome"] == "veto_with_H_payment_deviation"
            changed = [i for i, (a, b) in enumerate(zip(original["complete_actual"], modified["complete_actual"], strict=True)) if a != b]
            h = h_birth(first_rows)
            recipients = [b for b in original["births"] if b["parents"] == (h.holder,)]
            assert set(changed) <= {*h.fresh, *(i for b in recipients for i in b["fresh"])}
            unaffected = []
            left, right = first_quiet["third_cut"], word["third_cut"]
            def by_old_payment(cut):
                return {(b["parents"], b["paid"]): b for b in cut["births"]
                        if not set(b["parents"]).intersection(targets[0]["parents"])}

            old_left, old_right = by_old_payment(left), by_old_payment(right)
            assert old_left.keys() == old_right.keys()
            for key, a in old_left.items():
                b = old_right[key]
                matched_words = {name: bits(left[name][i] for i in a["fresh"])
                                 for name in ("complete_actual", "reference")}
                assert a["demand"] == b["demand"] and len(a["fresh"]) == len(b["fresh"])
                assert all(value == bits(right[name][i] for i in b["fresh"]) for name, value in matched_words.items())
                unaffected.append({"matched_holder_ids": [a["holder"], b["holder"]], "parents": a["parents"],
                                   "paid": a["paid"], "fresh_words_under_slot_transport": matched_words})
            comparisons.append({"H_nonreference_word": word["first_H_U_J_fresh_words"][0],
                                "all_changes_at_same_funded_predecision_roster": changed,
                                "first_writer_is_H_alone": False,
                                "unaffected_third_cut_births_matched": unaffected,
                                "other_first_birth_values_matched": True})
        assert quiet_siblings[0]["target_read"]["outcome"] == "missing"
        assert all(w["target_read"]["outcome"] == "veto_with_H_payment_deviation" for w in quiet_siblings[1:])
        expected[policy] = {"predesignated_U_J_nonreference_words": list(map(bits, nonref_others)),
                            "mass_of_fixed_U_J_background": select_mass,
                            "all_reference_U_J_background_has_same_mass": select_mass,
                            "controlled_traces_varying_all_H_words": chosen,
                            "paired_reached_stage_comparisons": comparisons,
                            "H_alone_with_U_J_reference_words": quiet_siblings}
    return expected


def ordinary_continuous_witness(law, transport, start, first_words):
    state, histories = start, []
    for cut in (1, 2, 3):
        state, _, stage = trace_cut(law, transport, state, "F", cut, False, first_words if cut == 1 else None)
        histories.append(stage)
    h = next(row for row in histories[0]["births"] if row["paid"] == (0,))
    targets = [row for row in histories[1]["births"] if set(row["paid"]) & set(h["fresh"])]
    assert len(targets) == 2 and all(len(row["parents"]) == 2 for row in targets)
    return {"first_H_U_J_fresh_words": list(map(bits, first_words)), "cuts": histories,
            "H_actual_second_cut_payees": targets, "enrolled_unary_target_missing": True}


def run_setting(law, reference, transport):
    start = State(OLD["FOUNDER"], reference, reference)
    OLD["check_state"](law, start)
    planner = StructuralPlans(law)
    _, first = planner.read(start, True)
    first_summary = first_factoring(law, transport, start, first)
    feedback, ordinary = {}, {}
    for policy in POLICIES:
        feedback[policy] = census(law, transport, start, policy, True, planner)
        ordinary[policy] = census(law, transport, start, policy, False, planner)
        assert ordinary[policy]["all_launches"]["initial_mass_by_outcome"]["missing"] == 1
    for law_mode in (feedback, ordinary):
        assert law_mode["M"]["all_launches"]["initial_mass_by_first_deviation"]["none"] == 1
    assert feedback["F"]["all_launches"]["initial_mass_by_outcome"]["veto_without_H_payment_deviation"] == 0
    quiet_trace = representative(law, transport, start, "M", tuple(tuple(map(int, b)) for b in first_summary["reference_banks_in_H_U_J_order"]))
    assert all(quiet_trace[t]["complete_actual"] == quiet_trace[t]["reference"] for t in ("first_cut", "second_cut", "third_cut"))
    examples = matched_examples(law, transport, start, first)
    first_words = [tuple(tuple(map(int, word)) for word in a["first_H_U_J_fresh_words"])
                   for a in examples["F"]["controlled_traces_varying_all_H_words"]]
    return {"law": law, "reference_transport": transport, "initial_actual_and_reference": bits(reference),
            "first_cut_exact_bank_support": first_summary, "feedback_by_policy": feedback,
            "ordinary_continuous_from_source_by_policy": ordinary, "completely_quiet_M_physical_trace": quiet_trace,
            "controlled_examples_by_policy": examples, "ordinary_continuous_physical_controls": [
                ordinary_continuous_witness(law, transport, start, words) for words in first_words]}


def main():
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_HASH
    answers = {name: run_setting(*params) for name, params in OLD["SETTINGS"].items()}
    out = {"schema": "quiet-founder-first-write-v1", "replay": answers,
           "weighting": "Uniform among allowed fresh words independently at each actual birth, conditional on its reached older word and roster. Product factors count terminal histories without weighting them equally across different branches.",
           "local_classification_from_quiet_paid_word": {
               "zero_fresh_slots": "One empty bank when the inherited word is already lawful.",
               "even_parity_h_positive": "2^(h-1) lawful banks. With a lawful reference, the reference is admissible and deviations are possible exactly when h >= 2.",
               "nae_mixed_paid_h_positive": "2^h lawful banks. A deviation from a lawful reference is possible for any h >= 1.",
               "nae_homogeneous_paid_h_positive": "2^h-1 lawful banks. A deviation from a lawful reference is possible exactly when h >= 2.",
               "zero_deviation_is_never_forbidden": True},
           "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                             for p in (DESIGN, PREDECESSOR, OLD["OPERATOR"], OLD["GUARD"])}}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, default=str, sort_keys=True, separators=(",", ":")) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
