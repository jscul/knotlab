"""Independent physical replay of the frozen three-private-distinction test."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONTRACT = ROOT / "research/NEW-SENDER-REFERENCE-20261122-001/design_candidate.md"
GROWTH = ROOT / "artifacts/HIDDEN-SENDER-MARKS-20261122-001A/HIDDEN-SENDER-MARKS-20261122-001A-E001_hidden_sends/growth.json.gz"
TERMINAL = ROOT / "artifacts/SUCCESSOR-RECEIPT-20261122-001A/SUCCESSOR-RECEIPT-20261122-001A-E001_successor_receipts/alternate.json.gz"
OPERATOR = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py"
HASHES = {
    CONTRACT: "dc0956dc1526a102daa09e49f7f9d7a53bf1412dae70a1d3d0e75b000046c19e",
    GROWTH: "f89de84f884b323e40f81a59dc7afa0e734bf4dc974e26eb5c7be9c5f775ce9a",
    TERMINAL: "e9fc4765288886313d46c596ee208e62d6f483d8ffdba842ec3833c3c5e9e0c2",
    OPERATOR: "cffce06049dee59029790d1668e34aa6efef0cd34cb34997379d0b9cbd4c3ece",
}
H, K, G = 631, 632, 1595
H_PAYMENT = 4381
BANK = (4383, 4384, 4385)
DESIGNATED = (0, 1)
TARGET = 1
PAIRS = tuple(combinations(range(3), 2))
PERMUTATIONS = tuple(permutations(range(3)))
CONTROLS = {
    "anonymous_refusal": "literal",
    "anonymous_equal_pair": "literal",
    "designated_pair": "literal",
    "designated_pair_refusal": "literal",
    "symmetric_unlike": "literal",
    "outsider_exchange": "literal",
    "addressed_writer": "desired_value",
    "outsider_writer": "desired_value",
    "late_role_read": "literal",
}


@dataclass(frozen=True)
class Birth:
    holder: int
    parents: tuple
    paid: tuple
    fresh: tuple
    demand: int

    @classmethod
    def recorded(cls, row):
        assert row["grant"] == len(row["fresh_names"])
        return cls(row["holder"], tuple(row["parents"]), tuple(row["consumed_names"]),
                   tuple(row["fresh_names"]), row["demand"])

    def renamed(self, convert):
        return Birth(self.holder, self.parents, tuple(map(convert, self.paid)),
                     tuple(map(convert, self.fresh)), self.demand)


def owners(stars):
    by_name = defaultdict(list)
    for holder, star in enumerate(stars):
        assert len(set(star)) == len(star) >= 3
        for name in star:
            by_name[name].append(holder)
    assert all(len(group) in (1, 2) for group in by_name.values())
    return by_name


def ordinary(stars, operator, law, cap, priority=None):
    before = owners(stars)
    plan = operator.step(operator.from_stars(stars), law, max_births=cap)
    assert plan.status == "extend" and not plan.shortages and not plan.implied
    private = defaultdict(list)
    for name in sorted(before, key=priority):
        if len(before[name]) == 1:
            private[before[name][0]].append(name)
    assert Counter(p for row in plan.parents for p in row) == {
        holder: len(names) for holder, names in private.items()}
    pools = {holder: iter(names) for holder, names in private.items()}
    next_name = max(before) + 1
    new = []
    for parents, grant, demand in zip(plan.parents, plan.fresh, plan.demand, strict=True):
        assert grant == max(demand, 1, 3 - len(parents))
        paid = tuple(next(pools[parent]) for parent in parents)
        fresh = tuple(range(next_name, next_name + grant))
        new.append(Birth(len(stars) + len(new), parents, paid, fresh, demand))
        next_name += grant
    grown = add(stars, new)
    after = owners(grown)
    for birth in new:
        assert all(after[name] == [payer, birth.holder]
                   for payer, name in zip(birth.parents, birth.paid, strict=True))
        assert all(after[name] == [birth.holder] for name in birth.fresh)
    return tuple(new)


def add(stars, births):
    return stars + tuple(row.paid + row.fresh for row in births)


def bitmask(names):
    return sum(1 << name for name in names)


def bits(word, names):
    return tuple(word >> name & 1 for name in names)


def word_of(names, values):
    return sum(value << name for name, value in zip(names, values, strict=True))


def label(values):
    return "".join(map(str, values))


def lawful(law, width, ones):
    return ones % 2 == 0 if law == "parity" else 0 < ones < width


def choices(law, paid, width):
    return tuple(fresh for fresh in product((0, 1), repeat=width)
                 if lawful(law, len(paid) + width, sum(paid) + sum(fresh)))


def check_word(law, word, stars):
    assert all(lawful(law, len(star), (word & bitmask(star)).bit_count()) for star in stars)


def extend(law, word, cut, fixed=None):
    if fixed is None:
        fixed = {}
    for row in cut:
        paid = (word & bitmask(row.paid)).bit_count()
        width = len(row.paid) + len(row.fresh)
        if any(name in fixed for name in row.fresh):
            held_ones = sum(fixed.get(name, 0) for name in row.fresh)
            free = tuple(name for name in row.fresh if name not in fixed)
            ones = next(count for count in range(len(free) + 1)
                        if lawful(law, width, paid + held_ones + count))
            word |= word_of(row.fresh, (fixed.get(name, 0) for name in row.fresh))
            word |= bitmask(free[:ones])
        elif not lawful(law, width, paid):
            assert lawful(law, width, paid + 1)
            word |= 1 << row.fresh[0]
    return word


def role_exchange(name):
    return {BANK[0]: BANK[1], BANK[1]: BANK[0]}.get(name, name)


def enrolled(growth, terminal, operator, law):
    stars = tuple(map(tuple, growth["original_stars"]))
    stages = [stars]
    old_layers = [cut["births"] for cut in growth["cases"]["intact"][law]["cuts"]]
    old_layers += [terminal["courses"][law]["intact"]["fourth"]["births"],
                   terminal["later_source_controls"][law]["fifth"]["births"]]
    cuts = []
    for saved, cap in zip(old_layers, (1024, 1024, 1024, 1024, 4096), strict=True):
        cut = ordinary(stages[-1], operator, law, cap)
        assert cut == tuple(map(Birth.recorded, saved))
        cuts.append(cut)
        stages.append(add(stages[-1], cut))
    assert tuple(map(len, cuts)) == (63, 131, 339, 964, 2782)
    records = {birth.holder: birth for cut in cuts for birth in cut}
    assert records[K].fresh == BANK and records[K].paid == (1749, 1761)
    assert records[H].parents == (292, 294) and records[G].parents == (H, K)
    assert records[G].paid == (H_PAYMENT, BANK[TARGET])
    assert records[G].fresh == (12953, 12954, 12955)
    assert not set(stages[4][G]) & (set(stages[3][K]) - {BANK[TARGET]})
    assert not {510, 563, 1754} & set(stages[4][G])
    launch = word_of(growth["original_name_order"], map(int, growth["common_original_words"][law]))
    assert bits(launch, (510, 563)) == (0, 1)
    check_word(law, launch, stars)
    return launch, stages, cuts, records


def changed_allocation(law, operator, stages, cuts):
    """Transport names with, and then without, the original priority."""
    renamed = tuple(tuple(map(role_exchange, star)) for star in stages[3])
    named_sham = ordinary(renamed, operator, law, 1024, priority=role_exchange)
    sham = tuple(row.renamed(role_exchange) for row in named_sham)
    assert sham == cuts[3]
    resorted = ordinary(renamed, operator, law, 1024)
    rerouted = tuple(row.renamed(role_exchange) for row in resorted)
    changed = {old.holder: [old.paid, new.paid]
               for old, new in zip(cuts[3], rerouted, strict=True) if old != new}
    assert set(changed) == {1211, G}
    for old, new in zip(cuts[3], rerouted, strict=True):
        assert (old.holder, old.parents, old.fresh, old.demand) == (
            new.holder, new.parents, new.fresh, new.demand)
        assert new.paid == tuple(map(role_exchange, old.paid))
    assert ordinary(add(stages[3], rerouted), operator, law, 4096) == cuts[4]
    assert tuple(row.renamed(role_exchange) for row in
                 ordinary(add(renamed, named_sham), operator, law, 4096)) == cuts[4]
    return renamed, named_sham, rerouted, changed


def projected_factor(law, launch, cuts, key_names):
    """Marginalize sibling banks once using the actual ancestor distinctions."""
    needed = set(key_names)
    chain = []
    for row in reversed([row for cut in cuts[:3] for row in cut]):
        used = tuple(i for i, name in enumerate(row.fresh) if name in needed)
        if used:
            chain.append((row, used))
            needed.update(row.paid)
    assert len(chain) == 9
    states = {launch: Fraction(1)}
    for row, used in reversed(chain):
        needed_fresh = tuple(row.fresh[i] for i in used)
        kernels = {}
        next_states = defaultdict(Fraction)
        for state, mass in states.items():
            paid = bits(state, row.paid)
            if paid not in kernels:
                legal_words = choices(law, paid, len(row.fresh))
                projected = Counter(word_of(needed_fresh, (fresh[i] for i in used))
                                    for fresh in legal_words)
                kernels[paid] = [(word, Fraction(count, len(legal_words)))
                                 for word, count in projected.items()]
            for word, chance in kernels[paid]:
                next_states[state | word] += mass * chance
        states = next_states
    weights = defaultdict(Fraction)
    witness = {}
    for state, mass in sorted(states.items()):
        key = bits(state, key_names)
        weights[key] += mass
        witness.setdefault(key, state)
    assert sum(weights.values()) == 1
    return weights, witness, needed, [row.holder for row, _ in reversed(chain)]


def permuted(bank, mapping):
    return tuple(bank[mapping.index(i)] for i in range(3))


def pair_map(pair, mapping):
    return tuple(sorted(mapping[i] for i in pair))


def protected_actions(bank):
    stabilizers = tuple(p for p in PERMUTATIONS if permuted(bank, p) == bank)
    fixed = tuple(pair for pair in PAIRS if all(pair_map(pair, p) == pair for p in stabilizers))
    assert all(bank[i] == bank[j] for i, j in fixed)
    return stabilizers, fixed


def offered(control, request, bank, target=TARGET, designated=DESIGNATED):
    """Each branch is (action, physical pair, reason, exact tie weight)."""
    def choice(action, pair=(), reason=""):
        return [(action, pair, reason, Fraction(1))]

    def ties(pairs):
        if not pairs:
            return choice("refuse", reason="homogeneous_bank")
        return [("exchange", pair, "", Fraction(1, len(pairs))) for pair in pairs]

    a, b = (bank[i] for i in designated)
    outside, = set(range(3)) - set(designated)
    if control == "addressed_writer":
        if bank[target] == request:
            return choice("hold", reason="already_requested_value")
        return ties([pair for pair in PAIRS if target in pair and bank[pair[0]] != bank[pair[1]]])
    if control == "outsider_writer":
        if a == b:
            return (choice("hold", reason="pair_already_requested_value") if a == request
                    else choice("refuse", reason="equal_pair_has_other_value"))
        if bank[outside] != request:
            return choice("refuse", reason="outsider_has_other_value")
    elif request == 0:
        return choice("hold")
    if control == "late_role_read":
        return choice("refuse", reason="all_three_are_paid")
    if control == "anonymous_refusal":
        return choice("refuse", reason="no_invariant_unlike_pair")
    if control == "anonymous_equal_pair":
        _, fixed = protected_actions(bank)
        return (choice("exchange", fixed[0], "unique_equal_pair") if fixed
                else choice("refuse", reason="no_invariant_pair"))
    if control in ("designated_pair", "designated_pair_refusal"):
        if control.endswith("refusal") and a == b:
            return choice("refuse", reason="designated_pair_equal")
        return choice("exchange", designated, "designated_pair")
    if control == "symmetric_unlike":
        return ties([pair for pair in PAIRS if bank[pair[0]] != bank[pair[1]]])
    assert control in ("outsider_exchange", "outsider_writer")
    if a == b:
        return choice("refuse", reason="designated_pair_equal")
    inside, = (i for i in designated if bank[i] != bank[outside])
    return choice("exchange", tuple(sorted((outside, inside))), "outsider_and_disagreeing_member")


def transpose(bank, pair):
    if not pair:
        return bank
    i, j = pair
    changed = list(bank)
    changed[i], changed[j] = bank[j], bank[i]
    return tuple(changed)


def public(law, h, q, width):
    return {label(fresh) for fresh in choices(law, (h, q), width)}


def account_observation(laws, request, h, fresh_words, weight):
    for fresh in fresh_words:
        laws[request, "fresh"][fresh] += weight / len(fresh_words)
        laws[request, "fresh+h"][f"{fresh}/{h}"] += weight / len(fresh_words)


def observation_summary(laws, denominator=Fraction(1)):
    summary = {"equiprobable_guess": {}, "observation_laws": {}}
    for read in ("fresh", "fresh+h"):
        left, right = (laws[request, read] for request in (0, 1))
        assert sum(left.values()) == sum(right.values()) == denominator
        values = sorted(left.keys() | right.keys())
        summary["equiprobable_guess"][read] = str(
            sum(max(left[w], right[w]) for w in values) / (2 * denominator))
        summary["observation_laws"][read] = {
            w: [str(left[w] / denominator), str(right[w] / denominator)] for w in values}
    return summary


def anonymous_prepay(bank, inherited, starred):
    # The past follows these same tracks throughout K's only prepayment record.
    return {"inherited_values_on_two_shared_tracks": label(inherited),
            "inherited_coholder_equalities": [0, 1],
            "private_values_up_to_track_renaming": label(sorted(bank)),
            "private_coholders": [None, None, None],
            "designated_pair_values_if_supplied": label(sorted(bank[i] for i in starred)),
            "outsider_value_if_supplied": next(bank[i] for i in range(3) if i not in starred)}


def replay_law(law, operator, growth, terminal):
    launch, stages, cuts, records = enrolled(growth, terminal, operator, law)
    renamed, named_sham, rerouted, changed = changed_allocation(law, operator, stages, cuts)
    by_third, by_fourth, by_fifth = (owners(stages[i]) for i in (3, 4, 5))
    assert all(by_third[name] == [K] for name in BANK)
    assert all(by_third[name] == by_fifth[name] == [payer, K]
               for payer, name in zip(records[K].parents, records[K].paid, strict=True))
    physical_payees = tuple(next(holder for holder in by_fourth[name] if holder != K) for name in BANK)
    assert physical_payees == (1211, G, 1597)
    assert all(by_fifth[name] == by_fourth[name] for name in BANK)
    assert all(by_fourth[name] == [G] for name in records[G].fresh)
    g_finish = [by_fifth[name][1] for name in records[G].fresh]
    assert g_finish == [3765, 4377, 4378]
    clock = [[None, None, None], [0, 1, 2]]
    recorded_clock = terminal["later_source_controls"][law]["G_own_finish"]["coholder_samples"]
    assert clock == recorded_clock
    key_names = (*records[K].paid, *BANK, H_PAYMENT)
    weights, witness, needed, contributing = projected_factor(law, launch, cuts, key_names)
    assert len(weights) == (32 if law == "parity" else 60)
    full_word_keys = {}
    full_words = []
    fifth_grants = bitmask(name for row in cuts[4] for name in row.fresh)
    fourth_grants = bitmask(name for row in cuts[3] for name in row.fresh)
    ancestor_masks = [bitmask(owners(stars)) for stars in stages[:3]]
    g_fresh = records[G].fresh

    def save(word):
        if word not in full_word_keys:
            full_word_keys[word] = len(full_words)
            full_words.append(format(word, "x"))
        return full_word_keys[word]

    def whole(prefix, fresh, routing="original"):
        key = (prefix, fresh, routing)
        if key in checked:
            return checked[key]
        if routing == "renamed":
            third, fourth = renamed, named_sham
        elif routing == "reallocated":
            third, fourth = stages[3], rerouted
        else:
            third, fourth = stages[3], cuts[3]
        check_word(law, prefix, third)
        stage4 = add(third, fourth)
        own = dict(zip(g_fresh, map(int, fresh), strict=True))
        word4 = extend(law, prefix, fourth, own)
        word5 = extend(law, word4, cuts[4])
        assert word4 & ~fourth_grants == prefix
        assert word5 & ~fifth_grants == word4
        assert bits(word4, g_fresh) == bits(word5, g_fresh) == tuple(map(int, fresh))
        check_word(law, word5, add(stage4, cuts[4]))
        checked[key] = [save(prefix), save(word4), save(word5)]
        return checked[key]

    checked = {}
    events = defaultdict(Counter)
    readings = {control: defaultdict(Counter) for control in CONTROLS}
    ready_laws, ready_launch_mass = defaultdict(Counter), Fraction(0)
    ready_cells = []
    rows = {}
    twin_candidates = {}
    transport_checks = 0
    counted_arms = 0
    for key, mass in sorted(weights.items()):
        inherited, bank, h = key[:2], key[2:5], key[-1]
        value = bank[TARGET]
        fixed = dict(zip(sorted(needed), bits(witness[key], sorted(needed)), strict=True))
        prefix = [launch]
        for stage, cut in zip(stages[1:4], cuts[:3], strict=True):
            prefix.append(extend(law, prefix[-1], cut, fixed))
            check_word(law, prefix[-1], stage)
        assert bits(prefix[-1], key_names) == key
        assert all(after & old == before for old, before, after in
                   zip(ancestor_masks, prefix[:3], prefix[1:], strict=True))
        common = prefix[-1]
        base_fresh = public(law, h, value, len(g_fresh))
        if value == 0 and bank[0] == 1:
            ready_cells.append(label(key))
            ready_launch_mass += mass
            for request in (0, 1):
                account_observation(ready_laws, request, h, public(law, h, request, len(g_fresh)), mass)
        stabilizer, pairs = protected_actions(bank)
        records_for_key = {}
        for control in CONTROLS:
            for request in (0, 1):
                options = offered(control, request, bank)
                assert sum(choice[-1] for choice in options) == 1
                for mapping in PERMUTATIONS:
                    transported = sorted((action, pair_map(pair, mapping), why, chance)
                                         for action, pair, why, chance in options)
                    assert transported == sorted(offered(
                        control, request, permuted(bank, mapping), mapping[TARGET],
                        pair_map(DESIGNATED, mapping)))
                    transport_checks += 1
                branches = []
                for action, pair, reason, chance in options:
                    after = transpose(bank, pair)
                    moved = after != bank
                    changes_q = after[TARGET] != value
                    outcome = "moved" if moved else "equal_noop" if pair else action
                    assert (changes_q <= moved) and all(by_third[BANK[i]] == [K] for i in pair)
                    after_word = common ^ word_of(BANK, (a ^ b for a, b in zip(bank, after, strict=True)))
                    assert ((common ^ after_word).bit_count(), transpose(after, pair)) == (
                        2 if moved else 0, bank)
                    assert (common ^ after_word) & ~bitmask(BANK) == 0
                    target_value = after[TARGET]
                    new_fresh = public(law, h, target_value, len(g_fresh))
                    overlap = base_fresh & new_fresh
                    if not changes_q:
                        assert overlap == base_fresh == new_fresh
                    elif law == "parity":
                        assert not overlap and len(base_fresh) == len(new_fresh) == 4
                    else:
                        assert len(overlap) == 7 and len(base_fresh ^ new_fresh) == 1
                    if control == "outsider_exchange" and moved:
                        assert after[0] == after[1] == bank[2]
                    if control in ("outsider_writer", "addressed_writer") and outcome != "refuse":
                        assert target_value == request
                        if control == "outsider_writer":
                            assert after[0] == after[1] == request
                    weight = mass * chance
                    events[control, request][outcome] += weight
                    if changes_q:
                        events[control, request]["changed_q"] += weight
                    if CONTROLS[control] == "desired_value" and target_value == request:
                        events[control, request]["actual_desired_payment"] += weight
                    if CONTROLS[control] == "desired_value" and outcome != "refuse":
                        events[control, request]["certified_desired_payment"] += weight
                    account_observation(readings[control], request, h, new_fresh, weight)
                    pick = min(overlap or base_fresh)
                    other = min(overlap or new_fresh)
                    held_trace = whole(common, pick)
                    acted_trace = whole(after_word, other)
                    if control == "late_role_read":
                        assert held_trace == acted_trace and all(len(by_fourth[d]) == 2 for d in BANK)
                    branches.append({
                        "outcome": outcome, "reason": reason, "pair": [BANK[i] for i in pair],
                        "request_after_cut": 4 if control == "late_role_read" else 3,
                        "tie_probability": str(chance), "K_after": label(after),
                        "q_after": target_value, "q_changed": changes_q,
                        "held_fresh_support": sorted(base_fresh), "acted_fresh_support": sorted(new_fresh),
                        "shared_fresh_support": sorted(overlap), "selected_fresh": [pick, other],
                        "held_whole_words": held_trace, "acted_whole_words": acted_trace,
                    })
                    counted_arms += 1
                records_for_key[f"{control}/{request}"] = branches
        row_label = label(key)
        rows[row_label] = {"prefix_from_launch": list(map(save, prefix)), "mass": str(mass),
                           "protected_permutations": stabilizer, "invariant_pairs": pairs,
                           "prepayment_view": anonymous_prepay(bank, inherited, DESIGNATED),
                           "same_prefix_controls": records_for_key}
        if bank[0] == 0 and bank[1] == 1:
            twin_candidates.setdefault(bank[2], (prefix, key))

    twins = []
    for outside, (prefix, key) in sorted(twin_candidates.items()):
        inherited, bank, h = key[:2], key[2:5], key[-1]
        same = prefix[-1]
        new_bank = transpose(bank, DESIGNATED)
        changed_at_birth = same ^ bitmask(BANK[:2])
        assert (same ^ changed_at_birth) & ancestor_masks[2] == 0
        assert bits(changed_at_birth, BANK) == new_bank and new_bank[TARGET] != bank[TARGET]
        assert anonymous_prepay(bank, inherited, DESIGNATED) == anonymous_prepay(
            new_bank, inherited, DESIGNATED)
        original_support = public(law, h, bank[TARGET], len(g_fresh))
        opposite_support = public(law, h, new_bank[TARGET], len(g_fresh))
        common_support = original_support & opposite_support
        original_trace = min(common_support or original_support)
        opposite_trace = min(common_support or opposite_support)
        renamed_word = changed_at_birth
        assert bits(renamed_word, tuple(map(role_exchange, BANK))) == bank
        original_full = whole(same, original_trace)
        sham_full = whole(renamed_word, original_trace, "renamed")
        assert [full_words[i] for i in original_full] == [
            format(int(full_words[i], 16) ^ bitmask(BANK[:2]), "x") for i in sham_full]
        assert bits(same, rerouted[G - len(stages[3])].paid) == (h, new_bank[TARGET])
        twins.append({
            "outsider_value": outside, "shared_ancestor_words": list(map(save, prefix[:3])),
            "same_allocation_K_birth_banks": [label(bank), label(new_bank)],
            "fixed_name_mapping_A_to_B": {BANK[0]: BANK[1], BANK[1]: BANK[0], BANK[2]: BANK[2]},
            "same_anonymous_prepayment": anonymous_prepay(bank, inherited, DESIGNATED),
            "H_payment": h, "opposite_actual_values_paid_at_fixed_G": [bank[TARGET], new_bank[TARGET]],
            "shared_fresh_support_at_fixed_h": sorted(common_support),
            "selected_fresh": [original_trace, opposite_trace],
            "original": original_full, "opposite_K_birth_assignment_same_allocation": whole(
                changed_at_birth, opposite_trace),
            "coherent_renaming_before_inverse_transport": sham_full,
            "physical_reallocation_same_prestate": whole(same, opposite_trace, "reallocated"),
        })
    assert len(twins) == 2

    rates = {}
    status_keys = ("hold", "refuse", "equal_noop", "moved")
    for control in CONTROLS:
        summary = {"input": CONTROLS[control], "requests": {}}
        for request in (0, 1):
            stat = events[control, request]
            assert sum(stat[key] for key in status_keys) == 1
            summary["requests"][request] = {key: str(stat[key]) for key in
                                            (*status_keys, "changed_q", *sorted(stat.keys() - {
                                                *status_keys, "changed_q"}))}
        summary.update(observation_summary(readings[control]))
        if control in ("anonymous_refusal", "anonymous_equal_pair", "designated_pair",
                       "designated_pair_refusal", "symmetric_unlike", "late_role_read"):
            assert all(left == right for table in summary["observation_laws"].values()
                       for left, right in table.values())
        rates[control] = summary
    both_desires = {
        control: str(sum(mass for key, mass in weights.items()
                         if all(offered(control, value, key[2:5])[0][0] != "refuse"
                                for value in (0, 1))))
        for control in ("addressed_writer", "outsider_writer")
    }
    assert both_desires["outsider_writer"] == "0"
    report = {
        "holders": {"H": H, "K": K, "G": G}, "births_by_cut": list(map(len, cuts)),
        "K_prepaid": {"paid_inputs": records[K].paid, "parents": records[K].parents, "own": BANK},
        "K_actual_payments": dict(zip(BANK, physical_payees, strict=True)),
        "H_payment": H_PAYMENT, "G_own": g_fresh,
        "G_new_coholders": dict(zip(g_fresh, g_finish, strict=True)), "G_private_to_shared_clock": clock,
        "post_payment_K_private_distinctions": [],
        "K_anonymous_new_coholders_at_payment": clock,
        "K_late_supplied_role_read": "paid identity is available at cut four, after all private moves end",
        "G_primary_observation_fields": ["own_fresh_values", "anonymous_coholder_equality_history"],
        "G_optional_read": "H payment value, source role only for this supplied read",
        "hidden": {"old_source": [510, 563], "all_K_distinctions": list(stages[3][K]),
                   "H_role": "hidden in primary read"},
        "coherent_allocations": "all receipts identical after inverse naming transport",
        "real_reallocation_changed_paid_identities": changed,
        "ancestor_births_marginalized_once": contributing, "exact_factor_cells": len(weights),
        "same_allocation_birth_twins": len(twins), "same_prefix_control_arms": counted_arms,
        "distinct_verified_whole_continuations": len(checked),
        "renaming_checks_all_six_permutations": transport_checks,
        "both_desires_can_be_guaranteed_on_same_prefix": both_desires,
        "prior_ready_01_uncalibrated_H": {
            "values_at_q_and_spare": {BANK[TARGET]: 0, BANK[0]: 1},
            "launch_mass": str(ready_launch_mass), "factor_cells": ready_cells,
            "q_change_given_ready_and_exchange": "1",
            **observation_summary(ready_laws, ready_launch_mass),
        },
        "policy_rates": rates,
    }
    return report, {"words_hex_little_bit_indexed_by_physical_distinction": full_words,
                    "factor_key_distinctions": key_names, "factor_cells": rows,
                    "opposite_future_roles": twins}


def main(check=False):
    for path, expected in HASHES.items():
        assert sha256(path.read_bytes()).hexdigest() == expected, path
    spec = spec_from_file_location("frozen_ordinary", OPERATOR)
    operator = module_from_spec(spec)
    sys.modules[spec.name] = operator
    spec.loader.exec_module(operator)
    growth, terminal = (json.loads(gzip.decompress(path.read_bytes())) for path in (GROWTH, TERMINAL))
    report = {"input_sha256": {str(path.relative_to(ROOT)): digest for path, digest in HASHES.items()},
              "independence": "terminal inputs and canonical ordinary operator only",
              "weighting": "fixed intact original hold and uniformly lawful fresh words conditional on actual paid inputs",
              "laws": {}}
    raw = {}
    for law in ("parity", "nae"):
        report["laws"][law], raw[law] = replay_law(law, operator, growth, terminal)
    pretty = lambda value: (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    artifacts = (
        (HERE / "audit.json", pretty(report)),
        (HERE / "witnesses.json.gz", gzip.compress(
            json.dumps(raw, separators=(",", ":"), sort_keys=True).encode(), mtime=0)),
    )
    for path, content in artifacts:
        if check:
            assert path.read_bytes() == content, path
        else:
            with path.open("xb") as output:
                output.write(content)
        print(sha256(content).hexdigest(), path.name)


if __name__ == "__main__":
    assert sys.argv[1:] in ([], ["--check"])
    main("--check" in sys.argv)
