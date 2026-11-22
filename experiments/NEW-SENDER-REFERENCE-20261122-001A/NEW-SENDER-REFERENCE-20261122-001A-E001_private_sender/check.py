"""Exact launch weighting and masked observations for the fixed B307 successor."""

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
from runpy import run_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "results.json"
DESIGN = ROOT / "research/NEW-SENDER-REFERENCE-20261122-001/design_candidate.md"
DESIGN_HASH = "dc0956dc1526a102daa09e49f7f9d7a53bf1412dae70a1d3d0e75b000046c19e"
PREDECESSOR = ROOT / "research/SUCCESSOR-RECEIPT-20261122-001B/independent/check.py"
REPLAY = run_path(str(PREDECESSOR))
K, H, G, R = 632, 631, 1595, 294
SLOTS = (0, 1, 2)
PAIRS = tuple(combinations(SLOTS, 2))
PERMUTATIONS = tuple(permutations(SLOTS))
BANKS = tuple(product((0, 1), repeat=3))


def word(values):
    return "".join(map(str, values))


def swap(bank, pair):
    changed = list(bank)
    if pair:
        i, j = pair
        changed[i], changed[j] = changed[j], changed[i]
    return tuple(changed)


def rename(bank, perm):
    return tuple(bank[perm.index(slot)] for slot in SLOTS)


def renamed_pair(pair, perm):
    return tuple(sorted(perm[i] for i in pair))


def invariant_pairs(bank):
    stabilizer = tuple(perm for perm in PERMUTATIONS if rename(bank, perm) == bank)
    eligible = tuple(pair for pair in PAIRS if all(renamed_pair(pair, p) == pair for p in stabilizer))
    return stabilizer, eligible


def move(policy, bank, request, pair, q):
    """An action, its exchanged private pair, and its exact tie probability."""
    hold = (("hold", (), Fraction(1)),)
    if policy == "addressed_desire":
        if bank[q] == request:
            return hold
        choices = tuple(p for p in PAIRS if q in p and bank[p[0]] != bank[p[1]])
        if not choices:
            return (("refuse_no_opposite_value", (), Fraction(1)),)
    elif policy == "outsider_desire":
        x, y = (bank[i] for i in pair)
        outsider, = set(SLOTS) - set(pair)
        if x == y == request:
            return hold
        if x == y or bank[outsider] != request:
            return (("refuse_pair_cannot_be_set_to_desire", (), Fraction(1)),)
        inside, = (i for i in pair if bank[i] != request)
        choices = (tuple(sorted((inside, outsider))),)
    elif not request:
        return hold
    elif policy == "deterministic_refusal":
        return (("refuse_no_unique_unlike_pair", (), Fraction(1)),)
    elif policy == "deterministic_equal_if_unique":
        _, choices = invariant_pairs(bank)
        if not choices:
            return (("refuse_no_unique_pair", (), Fraction(1)),)
    elif policy in ("fixed_pair_swap", "fixed_pair_refuse_equal"):
        if policy == "fixed_pair_refuse_equal" and bank[pair[0]] == bank[pair[1]]:
            return (("refuse_equal_pair", (), Fraction(1)),)
        choices = (pair,)
    elif policy == "random_unlike":
        choices = tuple(p for p in PAIRS if bank[p[0]] != bank[p[1]])
        if not choices:
            return (("refuse_no_unlike_pair", (), Fraction(1)),)
    elif policy == "outsider_equalize":
        x, y = (bank[i] for i in pair)
        if x == y:
            return (("refuse_equal_pair", (), Fraction(1)),)
        outsider, = set(SLOTS) - set(pair)
        inside, = (i for i in pair if bank[i] != bank[outsider])
        choices = (tuple(sorted((inside, outsider))),)
    else:
        raise ValueError(policy)
    return tuple(("exchange_equal" if bank[i] == bank[j] else "exchange_unlike", (i, j),
                  Fraction(1, len(choices))) for i, j in choices)


POLICIES = {
    "deterministic_refusal": "unmarked",
    "deterministic_equal_if_unique": "unmarked",
    "random_unlike": "unmarked",
    "fixed_pair_swap": "subset",
    "fixed_pair_refuse_equal": "subset",
    "outsider_equalize": "subset",
    "outsider_desire": "subset",
    "addressed_desire": "target_address",
}


def candidates(visibility, pair, q):
    return {"unmarked": SLOTS, "subset": pair, "target_address": (q,)}[visibility]


def verify_orbits(pair, q):
    records = {}
    for bank in BANKS:
        stabilizer, allowed = invariant_pairs(bank)
        assert len(allowed) == (0 if len(set(bank)) == 1 else 1)
        assert all(bank[i] == bank[j] for i, j in allowed)
        orbits = sorted({tuple(sorted({p[i] for p in stabilizer})) for i in SLOTS})
        records[word(bank)] = {"observable_track_orbits": orbits, "stabilizer_size": len(stabilizer),
                               "deterministic_pairs": allowed,
                               "target_values_across_unmarked_allocations": sorted(set(bank)),
                               "target_values_across_subset_allocations": sorted({bank[i] for i in pair})}
        for policy, request, perm in product(POLICIES, (0, 1), PERMUTATIONS):
            motions = move(policy, bank, request, pair, q)
            assert sum(prob for _, _, prob in motions) == 1
            transported = {(status, renamed_pair(p, perm), prob) for status, p, prob in motions}
            assert transported == set(move(policy, rename(bank, perm), request, renamed_pair(pair, perm), perm[q]))
    return records


def physical_rows(growth, recorded, law):
    original = growth["original_stars"]
    third = growth["cases"]["intact"][law]["cuts"]
    fourth = recorded["courses"][law]["intact"]["fourth"]
    fifth = recorded["later_source_controls"][law]["fifth"]
    assert fourth["status"] == fifth["status"] == "extend"
    assert len(fourth["births"]) == 964 <= 1024 and len(fifth["births"]) == 2782 <= 4096
    births = REPLAY["recover_births"](original, [*third, fourth, fifth])
    g_payments = REPLAY["pairs"](births[G])
    assert g_payments == {H: 4381, K: 4384}
    k_bank = births[K]["fresh_names"]
    assert k_bank == [4383, 4384, 4385]
    k_paid = {REPLAY["pairs"](b)[K]: b["holder"] for b in fourth["births"] if K in b["parents"]}
    g_paid = {REPLAY["pairs"](b)[G]: b["holder"] for b in fifth["births"] if G in b["parents"]}
    assert set(k_paid) == set(k_bank) and len(set(k_paid.values())) == 3
    assert set(g_paid) == set(births[G]["fresh_names"]) and len(set(g_paid.values())) == 3
    physical = {"K_inherited": births[K]["consumed_names"], "K_bank": k_bank,
                "K_payments": k_paid, "G_payments": g_paid, "H_companion_payment": g_payments[H],
                "G_fresh": births[G]["fresh_names"], "cut_sizes": [len(fourth["births"]), len(fifth["births"])],
                "after_cut_four_K_private_marks": [],
                "G_coholder_pattern": [[None] * 3, [0, 1, 2]]}
    return births, physical


def allocation_checks(physical, pair, q):
    """Keep the actual proposed groups while varying which private identity pays each."""
    marks = physical["K_bank"]
    receivers = tuple(physical["K_payments"][mark] for mark in marks)
    all_routes = tuple(tuple(marks[i] for i in ordering) for ordering in PERMUTATIONS)
    pair_routes = tuple(route for route in all_routes if route[q] in {marks[i] for i in pair})
    assert len(all_routes) == 6 and len(pair_routes) == 4
    assert all(len(set(route)) == len(receivers) for route in all_routes)
    old_order = sorted(marks)
    assert old_order == marks
    spare, = set(pair) - {q}
    relabel = {mark: mark + 100_000 for mark in marks}
    relabel[marks[q]], relabel[marks[spare]] = relabel[marks[spare]], relabel[marks[q]]
    renamed_history = tuple(relabel[mark] for mark in marks)
    resorted = tuple(sorted(renamed_history))
    assert renamed_history[q] != resorted[q]
    return {"fixed_receivers": receivers, "actual_payment_order": marks,
            "all_routes_same_groups": all_routes, "routes_with_designated_pair_at_G": pair_routes,
            "coherently_relabelled_payment_order": renamed_history,
            "new_allocation_if_relabelled_ids_are_resorted": resorted}


def launch_distribution(law, births, physical, growth, old):
    h = physical["H_companion_payment"]
    h_background = (set(births[H]["fresh_names"]) - {h}) | {REPLAY["pairs"](births[H])[292]}
    w = births[R]["fresh_names"]
    k_bank = physical["K_bank"]
    old_k = physical["K_inherited"]
    query = set(w + [h] + k_bank + old_k) | h_background
    names, states, contributing, peak = REPLAY["propagate"](
        law, births, old, set(growth["original_name_order"]), query)
    ls = Counter()
    for state, mass in states.items():
        bits = dict(zip(names, state, strict=True))
        bank = tuple(bits[i] for i in k_bank)
        inherited = tuple(bits[i] for i in old_k)
        assert REPLAY["lawful"](law, inherited + bank)
        ls[word(bits[i] for i in w), inherited, bank, bits[h], not any(bits[i] for i in h_background)] += mass
    assert ls.total() == 1
    return ls, {"births": [b["holder"] for b in contributing], "peak_states": peak}


def observation_summary(table):
    supports = defaultdict(Counter)
    for (request, observed), mass in table.items():
        supports[observed][request] += mass
    certificates = {observed: next(iter(choices)) for observed, choices in sorted(supports.items()) if len(choices) == 1}
    odds = sum(max(choices.values()) for choices in supports.values()) / 2
    certainty = sum((supports[o].total() for o in certificates), Fraction(0)) / 2
    return {"best_guess": odds, "total_variation": 2 * odds - 1,
            "certifying_records": certificates, "certainty_mass": certainty,
            "support": sorted(supports),
            "arm_laws": {str(i): {o: table[i, o] for o in sorted(supports) if table[i, o]} for i in (0, 1)}}


def price(law, launches, policy, pair, q, g_width):
    denom = launches.total()
    exposure = candidates(POLICIES[policy], pair, q)
    arm_events = {str(i): Counter() for i in (0, 1)}
    tables = {"fresh_only": Counter(), "fresh_plus_h": Counter()}
    paid_joint = {str(i): Counter() for i in (0, 1)}
    inherited_k_mass = Counter()
    sent_ones_by_inherited_k = {str(i): Counter() for i in (0, 1)}
    both_desires = Fraction(0)
    input_mass = Counter()
    is_desire = policy.endswith("_desire")
    for (_w, inherited, bank, h, _cal), launch in launches.items():
        mass = launch / denom
        input_mass[word(bank)] += mass
        inherited_k_mass[word(inherited)] += mass
        certain_by_arm = []
        for request in (0, 1):
            events = arm_events[str(request)]
            arm_certain = True
            for status, exchanged, tie_mass in move(policy, bank, request, pair, q):
                p = mass * tie_mass
                permuted = swap(bank, exchanged)
                assert REPLAY["lawful"](law, inherited + permuted)
                if policy == "outsider_equalize" and request:
                    assert all(permuted[i] == int(sum(bank) > 1) for i in pair)
                val = permuted[q]
                paid_joint[str(request)][f"{h}{val}"] += p
                sent_ones_by_inherited_k[str(request)][word(inherited)] += p * val
                events[status] += p
                events["changed_g_payment"] += p * (val != bank[q])
                events["paid_one"] += p * val
                events["prepaid_one"] += p * bank[q]
                events["certified_target_reversal"] += p * all(permuted[i] != bank[i] for i in exposure)
                events["actual_value_transposition"] += p * (permuted != bank)
                if is_desire:
                    certainly_desire = not status.startswith("refuse") and all(permuted[i] == request for i in exposure)
                    arm_certain &= certainly_desire
                    events["certified_desired_payment"] += p * certainly_desire
                    events["actual_desired_payment"] += p * (val == request)
                    events["refused_but_actual_payment_equals_desire"] += p * (status.startswith("refuse") and val == request)
                fresh_options = REPLAY["fresh_words"](law, (h, val), g_width)
                for fresh in fresh_options:
                    tables["fresh_only"][request, word(fresh)] += p / len(fresh_options)
                    tables["fresh_plus_h"][request, f"{word(fresh)}|{h}"] += p / len(fresh_options)
            certain_by_arm.append(arm_certain)
        if is_desire and all(certain_by_arm):
            both_desires += mass
    for table in tables.values():
        assert all(sum(m for (r, _o), m in table.items() if r == i) == 1 for i in (0, 1))
    for request, joint in paid_joint.items():
        assert joint.total() == 1
        for fresh in product((0, 1), repeat=g_width):
            fresh_label = word(fresh)
            expected_fresh = Fraction(0)
            for h in (0, 1):
                expected = Fraction(0)
                for val in (0, 1):
                    row_mass = joint.get(f"{h}{val}", Fraction(0))
                    if law == "parity":
                        count = 1 << (g_width - 1)
                        allowed = (h + val + sum(fresh)) % 2 == 0
                    else:
                        count = (1 << g_width) - int(h == val)
                        allowed = 0 < h + val + sum(fresh) < g_width + 2
                    if allowed:
                        expected += row_mass / count
                assert tables["fresh_plus_h"][int(request), f"{fresh_label}|{h}"] == expected
                expected_fresh += expected
            assert tables["fresh_only"][int(request), fresh_label] == expected_fresh
    report = {"launch_mass": denom, "bank_prior": input_mass,
              "request_interpretation": "desired payment value" if is_desire else "0 holds; 1 requests exchange",
              "audit_only_h_then_K_paid_bit": paid_joint,
              "audit_only_paid_one_given_K_inherited": {
                  request: {bits: sent_ones_by_inherited_k[request][bits] / m for bits, m in inherited_k_mass.items()}
                  for request in ("0", "1")},
              "arm_events": {}, "masked_decoding": {name: observation_summary(table) for name, table in tables.items()}}
    if is_desire:
        report["both_desires_certified_on_same_prestate"] = both_desires
        report["both_desires_certified_on_same_prestate_per_launch"] = both_desires * denom
    for request, events in arm_events.items():
        assert sum(m for label, m in events.items() if label.startswith(("hold", "exchange", "refuse_"))) == 1
        events["locally_refused"] = sum((m for label, m in events.items() if label.startswith("refuse_")), Fraction(0))
        report["arm_events"][request] = {"conditional_on_cohort": events,
                                         "per_launch_given_request": {k: p * denom for k, p in events.items()}}
    for read in report["masked_decoding"].values():
        read["certifying_mass_per_launch_at_equal_odds"] = read["certainty_mass"] * denom
    return report


def subcohort(launches, predicate):
    return Counter({state: mass for state, mass in launches.items() if predicate(state)})


def report_law(law, growth, words, physical_archive, predecessor):
    births, physical = physical_rows(growth, physical_archive, law)
    old = int(words["old_words"][f"{law}-00"]["common_before"], 16)
    assert word((old >> i) & 1 for i in growth["original_name_order"]) == growth["common_original_words"][law]
    launches, resources = launch_distribution(law, births, physical, growth, old)
    k_bank = physical["K_bank"]
    q, spare = k_bank.index(4384), k_bank.index(4383)
    pair = tuple(sorted((q, spare)))
    policy_scores = {p: price(law, launches, p, pair, q, len(physical["G_fresh"])) for p in POLICIES}

    ready = subcohort(launches, lambda s: (s[2][q], s[2][spare]) == (0, 1))
    ready_calibrated = subcohort(ready, lambda s: s[4])
    mixed_full_bank = subcohort(launches, lambda s: len(set(s[2])) > 1)
    cohorts = {"previous_ready_01": (ready, "fixed_pair_swap"),
               "previous_ready_01_and_H_zero_background": (ready_calibrated, "fixed_pair_swap"),
               "addressed_on_mixed_full_bank": (mixed_full_bank, "addressed_desire")}
    independently_anchored = predecessor["laws"][law]
    assert ready.total() == Fraction(independently_anchored["cohorts"]["ready"]["probability_per_launch"])
    assert ready_calibrated.total() == Fraction(independently_anchored["cohorts"]["ready_and_calibrated"]["probability_per_launch"])
    cohort_scores = {name: price(law, entries, p, pair, q, len(physical["G_fresh"]))
                     for name, (entries, p) in cohorts.items()}
    w_prior = {w: sum(m for state, m in launches.items() if state[0] == w) for w in independently_anchored["W_before_preparation"]}
    assert w_prior == {w: Fraction(m) for w, m in independently_anchored["W_before_preparation"].items()}
    for p in ("deterministic_refusal", "deterministic_equal_if_unique", "fixed_pair_swap", "fixed_pair_refuse_equal",
              "random_unlike", "outsider_equalize"):
        assert all(r["arm_laws"]["0"] == r["arm_laws"]["1"] for r in policy_scores[p]["masked_decoding"].values())
        audit = policy_scores[p]["audit_only_h_then_K_paid_bit"]
        assert audit["0"] == audit["1"]
    paid_by_k = policy_scores["outsider_equalize"]["audit_only_paid_one_given_K_inherited"]
    if law == "parity":
        assert all(paid_by_k["0"][bits] == Fraction(1, 2) for bits in paid_by_k["0"])
        assert all(paid_by_k["1"][bits] == (Fraction(3, 4) if bits[0] == bits[1] else Fraction(1, 4))
                   for bits in paid_by_k["1"])
    else:
        assert paid_by_k["0"] == paid_by_k["1"]
    assert policy_scores["outsider_desire"]["both_desires_certified_on_same_prestate"] == 0
    assert policy_scores["addressed_desire"]["both_desires_certified_on_same_prestate"] == mixed_full_bank.total()

    inherited_bank_mass = Counter()
    for (_w, inputs, bank, _h, _cal), mass in launches.items():
        inherited_bank_mass[f"{word(inputs)}|{word(bank)}"] += mass
    pair_marginal = {word(values): sum(m for s, m in launches.items() if tuple(s[2][i] for i in (q, spare)) == values)
                     for values in product((0, 1), repeat=2)}
    assert pair_marginal["01"] == pair_marginal["10"]
    mixed = pair_marginal["01"] + pair_marginal["10"]
    assert mixed == 2 * ready.total()
    return {"physical": physical, "resources": resources, "allocation_controls": allocation_checks(physical, pair, q),
            "orbit_records_by_complete_private_word": verify_orbits(pair, q),
            "launch_joint_K_inherited_and_bank": inherited_bank_mass, "launch_W_prior": w_prior,
            "pair_prior_in_target_then_companion_order_for_audit": pair_marginal,
            "pair_mixed_launch_mass": mixed, "full_bank_mixed_launch_mass": mixed_full_bank.total(),
            "orientation_given_mixed_pair": {"target_zero": pair_marginal["01"] / mixed,
                                             "target_one": pair_marginal["10"] / mixed},
            "policy_scores": policy_scores, "conditional_controls": cohort_scores}


def main():
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_HASH
    load = REPLAY["load"]
    growth_path, words_path, physical_path = (REPLAY[k] for k in ("GROWTH", "OLD_WORDS", "FOURTH"))
    predecessor_path = PREDECESSOR.with_name("verification.json")
    growth, words, physical, predecessor = map(load, (growth_path, words_path, physical_path, predecessor_path))
    output = {"schema": "private-sender-fixed-b307-20261122-v1",
              "input_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                              for p in (DESIGN, PREDECESSOR, growth_path, words_path, physical_path, predecessor_path)},
              "laws": {law: report_law(law, growth, words, physical, predecessor) for law in ("parity", "nae")}}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, default=str, sort_keys=True, indent=2) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
