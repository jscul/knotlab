"""Exhaust the frozen three-cut payment relay, including every tied minimum."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from itertools import permutations, product
from math import prod
import json
from pathlib import Path
from runpy import run_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research/WRITTEN-BIT-AND-JOIN-VETO-20261122-001/design_candidate.md"
DESIGN_HASH = "1f5c941c41cd1a1c31b0d9a12f834b5124f9ff73b422c0359e14fd698c585d32"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "results.json"
OPERATOR, = (ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A").glob("*/end_operator.py")
GUARD, = (ROOT / "experiments/STATE-FEEDS-GROWTH-20261119-001").glob("*/growth.py")
END = run_path(str(OPERATOR))
ARCHIVED = run_path(str(GUARD))
FOUNDER = ((0, 1, 2),)
DEVIATIONS = {"signal": (1, 0, 1), "diversion": (0, 1, 1), "quiet": (0, 0, 0)}
SETTINGS = {"parity_zero": ("parity", (0, 0, 0), "zero"),
            "nae_lexicographic": ("nae", (1, 1, 0), "lexicographic"),
            "nae_opposite_on_homogeneous_reference": ("nae", (1, 1, 0), "opposite")}


@dataclass(frozen=True)
class State:
    holdings: tuple
    actual: tuple
    reference: tuple


@dataclass(frozen=True)
class Birth:
    holder: int
    parents: tuple
    paid: tuple
    fresh: tuple
    demand: int


def bits(word):
    return "".join(map(str, word))


def lawful(law, word):
    ones = sum(word)
    return ones % 2 == 0 if law == "parity" else 0 < ones < len(word)


def check_state(law, state):
    assert len(state.actual) == len(state.reference)
    assert set().union(*map(set, state.holdings)) == set(range(len(state.actual)))
    assert all(len(set(row)) == len(row) >= 3 for row in state.holdings)
    for word in (state.actual, state.reference):
        assert all(lawful(law, tuple(word[i] for i in row)) for row in state.holdings)


def loose_names(holdings):
    sizes = Counter(i for held in holdings for i in held)
    assert all(n in (1, 2) for n in sizes.values())
    return {v: tuple(sorted(i for i in held if sizes[i] == 1)) for v, held in enumerate(holdings)
            if any(sizes[i] == 1 for i in held)}


def differences(state, names):
    return tuple(sorted(i for i in set(names) if state.actual[i] != state.reference[i]))


@cache
def plan(law, state, guard):
    check_state(law, state)
    end = END["from_stars"](state.holdings)
    ordinary = END["step"](end, law, max_births=128)
    candidates = END["proposals"](end)
    decisions = []
    for group in candidates:
        active = differences(state, (i for parent in group for i in state.holdings[parent]))
        decisions.append({"parents": group, "deviating_marks": active,
                          "action": "veto" if guard and active else "keep"})
    kept = tuple(row["parents"] for row in decisions if row["action"] == "keep")
    demand_by_parent = Counter(parent for group in kept for parent in group)
    shortage = {v: demand_by_parent[v] - n for v, n in end.opens.items() if demand_by_parent[v] > n}
    if shortage:
        return {"status": "stall", "shortage": shortage, "guard_table": decisions}
    if not end.opens:
        return {"status": "closed", "guard_table": decisions}
    parents = kept + tuple((v,) for v, count in end.opens.items() for _ in range(count - demand_by_parent[v]))
    needs, _ = END["_demands"](parents)
    closes = law == "parity" and len(parents) == 1
    if closes and len(parents[0]) < 3:
        return {"status": "arity_stop", "guard_table": decisions}
    grants = tuple(0 if closes else max(n, 3 - len(p), 1) for p, n in zip(parents, needs, strict=True))
    if not guard:
        assert ordinary.status == "extend" and (parents, needs, grants) == (ordinary.parents, ordinary.demand, ordinary.fresh)
    if law == "parity":
        occupied = tuple(i for i, x in enumerate(state.actual) if x != state.reference[i])
        archived = ARCHIVED["plan_round"](state.holdings, occupied, ("P", "V" if guard else "P"))
    else:
        # Only the structural part is borrowed. The archive validates relative parity,
        # so replay the actual decisions on its quiet reference instead of passing NAE words.
        actions = {row["parents"]: "V" if row["action"] == "veto" else "P" for row in decisions}
        actions.update({(v,): "P" for v in end.opens})
        archived = ARCHIVED["plan_round"](state.holdings, (), recorded_actions=actions)
    assert archived.status == "extend"
    old_grants = Counter((b.parents, b.demand, b.fresh) for b in archived.births)
    if law == "nae" and len(parents) == 1:
        # The archive closes this parity-only case. Use ordinary NAE's positive floor.
        assert len(archived.births) == 1 and archived.births[0].parents == parents[0]
        assert ordinary.parents == parents and ordinary.fresh == grants
    else:
        assert old_grants == Counter(zip(parents, needs, grants, strict=True))
    return {"status": "extend", "guard_table": decisions, "parent_roster": parents,
            "fresh_grants": grants, "next_demands": needs, "implied_parity_closure": closes}


def binding_options(state):
    loose = loose_names(state.holdings)
    return tuple(dict(zip(loose, assignment, strict=True))
                 for assignment in product(*(permutations(loose[v]) for v in loose)))


def bind(state, planned, binding=None):
    assert planned["status"] == "extend"
    loose = loose_names(state.holdings)
    binding = loose if binding is None else binding
    assert set(binding) == set(loose) and all(sorted(binding[v]) == list(loose[v]) for v in loose)
    available = {v: iter(order) for v, order in binding.items()}
    next_distinction = len(state.actual)
    births = []
    for parents, grant, demand in zip(planned["parent_roster"], planned["fresh_grants"], planned["next_demands"], strict=True):
        paid = tuple(next(available[v]) for v in parents)
        fresh = tuple(range(next_distinction, next_distinction + grant))
        births.append(Birth(len(state.holdings) + len(births), parents, paid, fresh, demand))
        next_distinction += grant
    assert all(next(cursor, None) is None for cursor in available.values())
    return tuple(births)


def factors(law, transport, before, births):
    result = []
    for row in births:
        ref_paid = tuple(before.reference[i] for i in row.paid)
        actual_paid = tuple(before.actual[i] for i in row.paid)
        bank_words = tuple(product((0, 1), repeat=len(row.fresh)))
        ref_allowed = tuple(w for w in bank_words if lawful(law, ref_paid + w))
        assert ref_allowed
        reference = ref_allowed[0]
        if transport == "opposite" and len(set(ref_paid)) == 1:
            reference = (1 - ref_paid[0],) * len(row.fresh)
        actual_allowed = tuple(w for w in bank_words if lawful(law, actual_paid + w))
        assert actual_allowed and reference in ref_allowed
        distances = {w: sum(a != b for a, b in zip(w, reference, strict=True)) for w in actual_allowed}
        minimum = min(distances.values())
        result.append((reference, tuple(w for w in actual_allowed if distances[w] == minimum)))
    return tuple(result)


def materialize(law, before, births, reference_banks, actual_banks):
    holdings = before.holdings + tuple(b.paid + b.fresh for b in births)
    actual, reference = list(before.actual), list(before.reference)
    for row, r, a in zip(births, reference_banks, actual_banks, strict=True):
        assert row.fresh == tuple(range(len(actual), len(actual) + len(a)))
        actual.extend(a)
        reference.extend(r)
    state = State(holdings, tuple(actual), tuple(reference))
    check_state(law, state)
    assert state.actual[:len(before.actual)] == before.actual and state.reference[:len(before.reference)] == before.reference
    return state


def successors(law, transport, state, rows):
    local = factors(law, transport, state, rows)
    for outcome in product(*(places for _, places in local)):
        yield materialize(law, state, rows, tuple(ref for ref, _ in local), outcome)


def serialize_birth(row):
    return {"holder": row.holder, "parents": row.parents, "paid": row.paid, "fresh": row.fresh, "demand": row.demand}


def target(first, second, source_names=(0, 1, 2)):
    by_mark = {b.paid[0]: b for b in first if len(b.parents) == 1}
    assert set(by_mark) == set(source_names)
    h = by_mark[source_names[0]]
    assert len(h.fresh) >= 2
    children = {b.paid[0]: b for b in second if b.parents == (h.holder,)}
    if not all(i in children for i in h.fresh[:2]):
        return None
    return tuple(sorted(children[i].holder for i in h.fresh[:2]))


def transport_names(law, transport, state, guard, first, second, pair):
    length = len(state.actual)
    trans = lambda marks: tuple(length - 1 - i for i in marks)
    translated = State(tuple(tuple(length - 1 - i for i in row) for row in state.holdings),
                       state.actual[::-1], state.reference[::-1])
    def rename_births(rows):
        return tuple(Birth(b.holder, b.parents, trans(b.paid), trans(b.fresh), b.demand) for b in rows)

    assert target(rename_births(first), rename_births(second), trans((0, 1, 2))) == pair
    original_plan, new_plan = plan(law, state, guard), plan(law, translated, guard)
    assert original_plan["status"] == new_plan["status"] == "extend"
    for older, new in zip(original_plan["guard_table"], new_plan["guard_table"], strict=True):
        assert older["parents"] == new["parents"] and older["action"] == new["action"]
        assert sorted(length - 1 - i for i in older["deviating_marks"]) == list(new["deviating_marks"])
    transported_order = {v: tuple(length - 1 - i for i in bank) for v, bank in loose_names(state.holdings).items()}
    canonical = bind(state, original_plan)
    renamed = bind(translated, new_plan, transported_order)
    assert [(r.holder, r.parents, tuple(length - 1 - i for i in r.paid), r.fresh) for r in canonical] == [
        (r.holder, r.parents, r.paid, r.fresh) for r in renamed]
    assert factors(law, transport, state, canonical) == factors(law, transport, translated, renamed)
    report = {"existing_name_transport": f"new={length - 1}-old", "future_fresh_identity_preserved": True,
              "enrollment_candidate_funding_and_filling_invariant": True}
    if pair is not None:
        union = set().union(*(set(state.holdings[p]) for p in pair))
        report["transported_guard_distinctions"] = sorted(length - 1 - i for i in union)
    return report


def final_receipt(law, transport, state, planned, pair):
    if planned["status"] != "extend":
        return {**planned, "number_of_final_fills": 0}
    births = bind(state, planned)
    local = factors(law, transport, state, births)
    reference = tuple(ref for ref, _ in local)
    representative = materialize(law, state, births, reference, tuple(allowed[0] for _, allowed in local))
    filled = prod(len(allowed) for _, allowed in local)
    report = {**planned, "actual_births": [serialize_birth(row) for row in births], "number_of_final_fills": filled,
              "local_factors_birth_order": [{"reference_fresh": bits(ref), "all_minimum_fresh": list(map(bits, allowed))}
                                            for ref, allowed in local],
              "representative_complete_actual": bits(representative.actual),
              "complete_reference": bits(representative.reference)}
    if pair is not None:
        involved = [row for row in births if set(row.parents) & set(pair)]
        report["actual_target_parent_payments"] = [serialize_birth(row) for row in involved]
        report["target_join_born"] = any(row.parents == pair for row in involved)
        action, = (r["action"] for r in planned["guard_table"] if r["parents"] == pair)
        assert report["target_join_born"] == (action == "keep")
        if action == "veto":
            assert all(len(row.parents) == 1 for row in involved)
    return report


def guard_read(state, first, second, pair, third_plan):
    source = {birth.paid[0]: birth for birth in first}
    h = source[0]
    assert state.holdings[h.holder] == h.paid + h.fresh
    target_rows = [row for row in second if pair is not None and row.holder in pair]
    union = sorted({mark for row in target_rows for mark in state.holdings[row.holder]})
    changed = differences(state, union)
    carriers = tuple(i for i in changed if i in h.fresh)
    competing = tuple(i for i in changed if i not in h.fresh)
    assert set(union).isdisjoint((0, 1, 2))
    candidate = next((row for row in third_plan["guard_table"] if row["parents"] == pair), None)
    real_payments = {name: serialize_birth(row) for row in second for name in row.paid if name in h.fresh}
    assert set(real_payments) == set(h.fresh)
    if pair is not None:
        assert candidate is not None and changed == candidate["deviating_marks"]
    return {"H_U_J": [serialize_birth(source[i]) for i in (0, 1, 2)],
            "target_parents": pair, "target_parent_births": [serialize_birth(row) for row in target_rows],
            "H_real_second_cut_payments_by_distinction": real_payments,
            "target_guard_union": union, "actual_on_union": bits(state.actual[i] for i in union),
            "reference_on_union": bits(state.reference[i] for i in union),
            "all_differences": changed, "paid_H_carriers": carriers, "competing_recipient_fresh_differences": competing,
            "source_mark_reaches_target_union_directly": False,
            "same_eligible_target_action": candidate["action"] if candidate else None}


def physical_histories(law, transport, founder, guarded):
    first_plan = plan(law, founder, guarded)
    first = bind(founder, first_plan)
    histories, total = [], 0
    for at_two in successors(law, transport, founder, first):
        second_plan = plan(law, at_two, guarded)
        second = bind(at_two, second_plan)
        pair = target(first, second)
        for at_three in successors(law, transport, at_two, second):
            deciding = plan(law, at_three, guarded)
            local = guard_read(at_three, first, second, pair, deciding)
            final = final_receipt(law, transport, at_three, deciding, pair)
            same_stage_control = final_receipt(law, transport, at_three, plan(law, at_three, False), pair) if guarded else None
            if pair is not None and same_stage_control:
                assert same_stage_control["target_join_born"]
            histories.append({"actual_through_first_cut": bits(at_two.actual), "reference_through_first_cut": bits(at_two.reference),
                              "second_cut": {**second_plan, "births": [serialize_birth(row) for row in second]},
                              "actual_through_second_cut": bits(at_three.actual),
                              "reference_through_second_cut": bits(at_three.reference),
                              "target": local, "deciding_cut": final,
                              "ordinary_on_same_reached_predecision_stage": same_stage_control,
                              "coherent_name_transport": transport_names(law, transport, at_three, guarded, first, second, pair)})
            total += final["number_of_final_fills"]
    return {"first_cut": {**first_plan, "births": [serialize_birth(row) for row in first]},
            "preguard_histories": histories, "preguard_history_count": len(histories), "terminal_history_count": total}


def matched_signal_and_diversion(signal, diversion):
    def signature(h):
        target_read = h["target"]
        return (target_read["target_parents"], tuple(target_read["target_guard_union"]),
                target_read["reference_on_union"], h["reference_through_second_cut"],
                tuple(tuple(x["paid"]) for x in h["second_cut"]["births"]))

    diversion_records = {signature(h) for h in diversion["preguard_histories"]}
    assert {signature(h) for h in signal["preguard_histories"]} == diversion_records
    assert all(h["target"]["same_eligible_target_action"] == "keep" and not h["target"]["all_differences"]
               for h in diversion["preguard_histories"])
    tally = Counter()
    for history in signal["preguard_histories"]:
        row = history["target"]
        assert row["same_eligible_target_action"] == "veto" and len(row["paid_H_carriers"]) == 1
        assert not history["deciding_cut"]["target_join_born"]
        assert history["ordinary_on_same_reached_predecision_stage"]["target_join_born"]
        carrier, = row["paid_H_carriers"]
        sole = row["all_differences"] == (carrier,)
        tally[f"physical_mark_{carrier}_sole" if sole else f"physical_mark_{carrier}_with_companion"] += 1
    return {"same_fixed_physical_target_and_reference_records": len(diversion_records),
            "signal_guard_difference_histogram": tally,
            "structural_comparison": "signal vetoes; diversion keeps; complete funding in all reached cases"}


def upstream_binding_controls(law, transport, initial):
    """Follow actual recipient identities for every legal binder before the guard."""
    first_plan = plan(law, initial, True)
    controls = Counter()
    matched_physical_signatures = []
    for first_bind in binding_options(initial):
        first = bind(initial, first_plan, first_bind)
        h, = (row for row in first if row.paid == (0,))
        at_twos = tuple(successors(law, transport, initial, first))
        for second_bind in binding_options(at_twos[0]):
            reads = Counter()
            signatures = set()
            for at_two in at_twos:
                second_plan = plan(law, at_two, True)
                second = bind(at_two, second_plan, second_bind)
                pair = target(first, second)
                assert pair is not None
                for at_three in successors(law, transport, at_two, second):
                    decided = plan(law, at_three, True)
                    record = guard_read(at_three, first, second, pair, decided)
                    signatures.add((pair, tuple(b.paid for b in second), at_three.reference))
                    carrier_positions = tuple(h.fresh.index(m) for m in record["paid_H_carriers"])
                    key = (record["same_eligible_target_action"], carrier_positions,
                           len(record["competing_recipient_fresh_differences"]))
                    reads[key] += 1
            controls[tuple(sorted(reads.items()))] += 1
            assert len(signatures) == 1
            matched_physical_signatures.extend(signatures)
    assert sum(controls.values()) == 48 and len(controls) == 1
    signature_hash = sha256(json.dumps(matched_physical_signatures, separators=(",", ":")).encode()).hexdigest()
    cases = [{"number_of_paired_first_and_second_cut_binders": n, "preguard_history_histogram": [
        {"action": k[0], "H_fresh_positions_of_carriers": k[1], "additional_differences": k[2], "histories": count}
        for k, count in record]} for record, n in controls.items()]
    return {"target_payments_and_full_reference_signature_sha256": signature_hash, "cases": cases}


def third_binding_control(law, transport, guarded):
    """Rebind the already chosen rosters. The guard precedes these allocations."""
    histogram = Counter()
    for row in guarded["preguard_histories"]:
        stages = guarded["first_cut"]["births"] + row["second_cut"]["births"]
        holds = FOUNDER + tuple(tuple(b["paid"] + b["fresh"]) for b in stages)
        state = State(holds, tuple(map(int, row["actual_through_second_cut"])), tuple(map(int, row["reference_through_second_cut"])))
        planned = plan(law, state, True)
        assert planned["status"] == "extend"
        for binding in binding_options(state):
            births = bind(state, planned, binding)
            local = factors(law, transport, state, births)
            materialize(law, state, births, tuple(r for r, _ in local), tuple(w[0] for _, w in local))
            assert tuple(b.parents for b in births) == planned["parent_roster"]
            histogram[prod(len(w) for _, w in local)] += 1
    return {"legal_third_cut_binding_cases": histogram.total(), "local_minimum_fill_product_histogram": histogram}


def run_setting(law, reference, transport):
    starts = {name: State(FOUNDER, tuple(a ^ b for a, b in zip(reference, deviation, strict=True)), reference)
              for name, deviation in DEVIATIONS.items()}
    assert starts["signal"].actual == (starts["diversion"].actual[1], starts["diversion"].actual[0], starts["diversion"].actual[2])
    feedback = {name: physical_histories(law, transport, s, True) for name, s in starts.items()}
    ordinary = {name: physical_histories(law, transport, s, False) for name, s in starts.items()}
    for name, run in ordinary.items():
        assert not any(h["target"]["target_parents"] is not None for h in run["preguard_histories"])
        if name == "quiet":
            assert all(r["deciding_cut"]["representative_complete_actual"] == r["deciding_cut"]["complete_reference"]
                       for r in run["preguard_histories"])
    quiet = feedback["quiet"]
    assert len(quiet["preguard_histories"]) == quiet["terminal_history_count"] == 1
    q, = quiet["preguard_histories"]
    assert q["target"]["target_parents"] is None and q["actual_through_second_cut"] == q["reference_through_second_cut"]
    assert q["deciding_cut"]["representative_complete_actual"] == q["deciding_cut"]["complete_reference"]
    matches = matched_signal_and_diversion(feedback["signal"], feedback["diversion"])
    upstream_controls = {name: upstream_binding_controls(law, transport, starts[name]) for name in ("signal", "diversion")}
    assert upstream_controls["signal"]["target_payments_and_full_reference_signature_sha256"] == (
        upstream_controls["diversion"]["target_payments_and_full_reference_signature_sha256"])
    downstream_controls = {name: third_binding_control(law, transport, run) for name, run in feedback.items()}
    return {"law": law, "transport": transport, "founder_reference": bits(reference),
            "founding_preparations": {n: {"absolute": bits(s.actual), "deviations": bits(DEVIATIONS[n])} for n, s in starts.items()},
            "feedback": feedback, "ordinary_continuous_from_same_founder": ordinary, "matched_signal_and_diversion": matches,
            "all_first_and_second_cut_binders": upstream_controls, "all_third_cut_binders_on_displayed_histories": downstream_controls}


def main():
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_HASH
    studies = {name: run_setting(*args) for name, args in SETTINGS.items()}
    out = {"schema": "written-bit-join-veto-v1", "physical_source_names": {"p": 0, "u": 1, "j": 2}, "study": studies,
           "source_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                             for path in (DESIGN, OPERATOR, GUARD)}}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
