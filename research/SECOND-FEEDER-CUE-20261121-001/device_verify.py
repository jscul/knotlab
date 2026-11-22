"""Independent mark and public-input replay of the B307 second-cue device."""

import argparse
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
from random import Random
import subprocess
import sys

import device as implementation


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = HERE.parent / "FEEDER-MEMORY-20261121-001"
OLD_RECORD = json.loads((PREVIOUS / "keeper_verified.json").read_bytes())
OLD_BILLS = {key: tuple(names) for key, names in OLD_RECORD["holdings"].items()}
OLD_BANKS = {key: tuple(names) for key, names in OLD_RECORD["named_banks"].items()}
LAWS = ("parity", "nae")
MEMORY = ("110", "101", "011")
ACTION = ("100", "010", "001")
SECOND = ("x_here", "x_departed", "x_paid_from", "x_paid_menu", "x_paid_slot")
ARRIVAL = ("arr_from", "arr_menu", "arr_slot")
SCORES = ("score_0", "score_1", "score_2", "score_3")
VOTES = ("vote_0", "vote_1", "vote_2", "vote_3")
SELECTED = (None, "x_here", "x_paid_from", "x_paid_menu", "x_paid_slot")
CUES = ("none", "strict_return", "approach_feeder", "approach_menu", "approach_slot")
BRIDGES = ("paid", "previous_on", "previous_menu", "cue", "menu", "energy_before")
NEW_WIDTHS = {
    "x_here": 2, "x_departed": 2, "x_paid_from": 3, "x_paid_menu": 4, "x_paid_slot": 3,
    "x_slack": 1, "arr_from": 3, "arr_menu": 4, "arr_slot": 3, "phase": 5, "real_slot": 3,
    "credit_energy": 11, "credit_paid": 2, "selector": 5, "selector_slack": 1,
    **dict.fromkeys(VOTES, 2), **dict.fromkeys(SCORES, 15),
    **{key + "_slack": 1 for key in SCORES},
}
BUFFERED = (*SECOND, *ARRIVAL, "phase", *SCORES, "selector")
for bank in BUFFERED:
    NEW_WIDTHS.update({"new_" + bank: NEW_WIDTHS[bank], "saved_" + bank: NEW_WIDTHS[bank]})
NEW_WIDTHS["j_slack"] = 1
BANKS = dict(OLD_BANKS)
next_name = 55
for bank, width in NEW_WIDTHS.items():
    BANKS[bank] = tuple(range(next_name, next_name + width))
    next_name += width
NAMES = tuple(range(next_name))
BRIDGE_NAMES = tuple(d for bank in BRIDGES for d in BANKS[bank])
BILLS = OLD_BILLS | {
    "X": tuple(d for bank in (*SECOND, "x_slack") for d in BANKS[bank]),
    "S": BANKS["selector"] + BANKS["selector_slack"],
    **{f"C{i}": BANKS[bank] + BANKS[bank + "_slack"] for i, bank in enumerate(SCORES)},
}
LEAF_SLACKS = ("x_slack", "selector_slack", *(key + "_slack" for key in SCORES))
BILLS["J"] = BRIDGE_NAMES + tuple(d for bank in NEW_WIDTHS if bank not in LEAF_SLACKS for d in BANKS[bank])
PIVOT = {holder: BANKS[bank][0] for holder, bank in zip(
    ("M", "K", "H", "X", "S", "C0", "C1", "C2", "C3", "J"),
    ("memory_slack", "action_slack", "coupler_slack", *LEAF_SLACKS, "j_slack"), strict=True)}
OWNERS = {d: frozenset(holder for holder, scope in BILLS.items() if d in scope) for d in NAMES}


def mask(names):
    return sum(1 << d for d in names)


BILL_MASKS = tuple(map(mask, BILLS.values()))
BANK_MASKS = {key: mask(names) for key, names in BANKS.items()}
OLD_MASK = (1 << 55) - 1


def bit(word, name):
    return (word >> name) & 1


def bits(word, scope):
    return "".join("1" if bit(word, d) else "0" for d in scope)


def marker(word, bank):
    part = word & BANK_MASKS[bank]
    assert part.bit_count() == 1, (bank, part)
    return BANKS[bank].index(part.bit_length() - 1)


def fill(word, bank, position):
    return (word & ~BANK_MASKS[bank]) | 1 << BANKS[bank][position]


def assign(word, scope, values):
    return (word & ~mask(scope)) | sum((v == "1") << d for v, d in zip(values, scope, strict=True))


def permits(part, support, law):
    used = part & support
    return used.bit_count() % 2 == 0 if law == "parity" else used not in (0, support)


def legal(word, law, masks=BILL_MASKS):
    return all(permits(word, scope, law) for scope in masks)


def lift(pins, on, law, bills=BILLS):
    """Fix all supplied values, then repair unsatisfied rows at their independent slack."""
    word = on
    assert word & ~pins == 0
    for holder, row in bills.items():
        scope = mask(row)
        if not permits(word, scope, law):
            place = 1 << PIVOT[holder]
            assert not pins & place and OWNERS[PIVOT[holder]] == {holder}
            word ^= place
        assert permits(word, scope, law)
    assert word & pins == on and legal(word, law, tuple(map(mask, bills.values())))
    return word


def four_places_cli(scope, law):
    names = tuple(f"n{d}" for d in scope)
    words = tuple("".join(v) for v in product("01", repeat=len(scope)))
    forbidden = [w for w in words if not permits(int(w, 2), (1 << len(scope)) - 1, law)]
    cnf = "; ".join(" ".join(f"~{d}" if v == "1" else d for d, v in zip(names, w, strict=True)) for w in forbidden)
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops", *names[:-1],
           "--contact", names[-1], "--json"]
    out = subprocess.run(cmd, cwd=ROOT, env=os.environ | {"PYTHONPATH": str(ROOT / "tools")},
                         text=True, capture_output=True, check=True)
    receipt = json.loads(out.stdout)
    assert (receipt["is_knot"], receipt["binding"], receipt["invisible_in_parts"], receipt["coexistence"]) == (True, True, True, True)
    assert set(receipt["allowed"]) == set(words) - set(forbidden)
    return {"physical_names": names, "complete_words": len(receipt["allowed"]), "K1_K2_K3": True}


def shape_audit():
    assert BANKS == implementation.NAMES and BILLS == implementation.STARS
    assert OWNERS == {n: frozenset(roles) for n, roles in implementation.OWNERS.items()}
    assert tuple(implementation.SECOND_FIELDS) == SECOND and tuple(implementation.SCORES) == SCORES
    assert tuple(implementation.CUES) == CUES
    old_changes = sorted(d for d in range(55) if OWNERS[d] != {h for h, row in OLD_BILLS.items() if d in row})
    assert old_changes == sorted(BRIDGE_NAMES)
    assert all(OWNERS[d] == {"H", "J"} for d in BRIDGE_NAMES)
    assert all(OWNERS[d] == {r} for r, d in PIVOT.items())
    assert max(map(len, OWNERS.values())) == 2
    assert tuple(map(len, (NAMES, BRIDGE_NAMES, BILLS["J"]))) == (368, 23, 330)
    assert sum(OWNERS[d] == {"J"} for d in BILLS["J"]) == 228
    return {"arity": {h: len(scope) for h, scope in BILLS.items()},
            "old_names_with_second_holder_J": BRIDGE_NAMES, "world_names": len(NAMES),
            "private_completion_pivots": PIVOT, "shared_and_private_names_at_J": [102, 228]}


def extent_certificate(law):
    rng = Random(202611213070)
    fixtures = {}
    for label, row in BILLS.items():
        local = mask(row)
        available = range(1 << len(row)) if len(row) <= 6 else (
            0, (1 << len(row)) - 1, *((1 << i) for i in range(len(row))),
            *((1 << len(row)) - 1 ^ (1 << i) for i in range(len(row))),
            *(rng.getrandbits(len(row)) for _ in range(48)))
        count = 0
        examples = []
        for word in available:
            if not permits(word, (1 << len(row)) - 1, law):
                continue
            pinned = sum(bit(word, i) << d for i, d in enumerate(row))
            extension = lift(local, pinned, law)
            assert implementation.lawful(extension, law)
            if count < 2:
                examples.append({"pinned_scope_word": pinned, "whole_extension": extension})
            count += 1
        fixtures[label] = {
            "arity": len(row), "complete_projection_cardinality": (1 << (len(row) - 1))
            if law == "parity" else (1 << len(row)) - 2, "one_name_omission_cardinality": 1 << (len(row) - 1),
            "K1_K2_K3": True, "constructive_extensions_checked": count, "examples": examples,
        }
        if len(row) <= 6:
            fixtures[label]["canonical_CLI"] = four_places_cli(row, law)

    old_words = []
    for old_shared in range(64):
        old_boundary = BANKS["m"] + BANKS["a"]
        candidates = (0, mask(BRIDGE_NAMES), rng.getrandbits(55) & mask(BRIDGE_NAMES))
        for selection in candidates:
            shared_values = sum(bit(old_shared, i) << d for i, d in enumerate(old_boundary))
            past = lift(mask(old_boundary + BRIDGE_NAMES), shared_values | selection, law, OLD_BILLS)
            grown = lift(OLD_MASK, past, law)
            assert grown & OLD_MASK == past and implementation.lawful(grown, law)
            old_words.append(past)
    # Both couplers have disjoint private names after fixing their common bridge.
    old_conditional = 196 * (1 << 24)
    new_conditional = (1 << 228)
    for holder in ("X", "S", "C0", "C1", "C2", "C3"):
        new_conditional *= (1 << len(BILLS[holder])) - 2
    count = (1 << (len(NAMES) - len(BILLS))) if law == "parity" else (
        ((1 << 23) - 2) * old_conditional * new_conditional
        + 2 * (old_conditional - 1) * (new_conditional - 1))
    return {"per_holder_full_projections": fixtures, "legal_whole_state_count": count,
            "legal_original_words_checked_jointly": len(old_words), "old_relation_identical": True,
            "proof": "Every row has an independent private slack. Fix a whole legal holder or the entire old 55-name relation, choose all other non-slack values, then complete each unconstrained row at its private slack. Any illegal pinned row remains illegal. Canonical parity and NAE each allow every proper projection by filling a forgotten name.",
            "old_words_distinct_checked": len(set(old_words))}


def initial(law):
    word = 0
    prepared = {"m": MEMORY[0], "t": MEMORY[0], "m_out": MEMORY[0], "a": ACTION[0],
                "a_scratch": ACTION[0], "a_out": ACTION[0], "paid": "10",
                "memory_slack": "0", "action_slack": "1"}
    for bank in ("previous_on", "previous_menu", "energy_before", "energy_after", "cue", "menu"):
        word = fill(word, bank, 0)
    for bank, val in prepared.items():
        word = assign(word, BANKS[bank], val)
    for bank in NEW_WIDTHS:
        if not bank.endswith("slack"):
            word = fill(word, bank, 7 if bank in SCORES else 0)
    # These are the only prepared slack bits not fixed to their prescribed old values.
    fixed = mask(d for d in NAMES if d not in {v for k, v in PIVOT.items() if k not in ("M", "K")})
    if law == "parity":
        word = lift(fixed, word, law)
    assert legal(word, law)
    return word


def board(law, props=None, memory=0, mode="learned", training=False):
    result = implementation.LearnedKnotBot(law, mode=mode)
    fresh = initial(law)
    expected = fill(fresh, "selector", CUES.index(mode)) if mode in CUES[1:] else fresh
    assert result._word == expected
    if props:
        for bank, position in props.items():
            expected = fill(expected, bank, position)
    result._word = assign(expected, BANKS["m"], MEMORY[memory])
    result.training = training
    assert legal(result._word, law)
    return result


def supports_offer(holder, operands, guard, owners=OWNERS):
    x, y = operands
    return (x != y and owners[x] == owners[y] and holder in owners[x]
            and len(set(n for n, _ in guard)) == len(guard)
            and all(n not in operands and holder in owners[n] and b in (0, 1) for n, b in guard))


def swap_value(word, holder, pair, guard, connected=True, owners=OWNERS):
    if not connected:
        return word, "disconnected"
    if not supports_offer(holder, pair, guard, owners):
        return word, "unsupported"
    if any(bit(word, n) != expect for n, expect in guard):
        return word, "guard refused"
    if bit(word, pair[0]) == bit(word, pair[1]):
        return word, "equal operands"
    return word ^ mask(pair), "changed"


def trace_word(path, start, law, tally, disconnected=()):
    word = start
    for event in path:
        if "fixed_local_table" in event:
            assert all(marker(word, b) == v for b, v in event["actual_inputs"].items())
            assert marker(word, "new_" + event["fixed_local_table"]) == event["prepared"]
            tally["fixed local table dispatch"] += 1
            continue
        assert event["before"] == word and legal(word, law)
        if "external_exchange" in event:
            bank = event["bank"]
            if "exported_index" in event:
                assert marker(word, bank) == event["exported_index"]
                word = fill(word, bank, event["incoming_index"])
            else:
                assert bits(word, BANKS[bank]) == event["exported"]
                word = assign(word, BANKS[bank], event["incoming"])
            result = "supplied export and refill"
        else:
            pair = tuple(event["operands"])
            guard = tuple(event["guard"])
            assert supports_offer(event["holder"], pair, guard)
            assert list(event["guard_actual"]) == [bit(word, n) for n, _ in guard]
            previous = word
            word, result = swap_value(word, event["holder"], pair, guard, event["offer"] not in disconnected)
            assert result == event["status"]
            assert event["toggled"] == [d for d in pair if bit(word, d) != bit(previous, d)]
        assert event["after"] == word and legal(word, law)
        tally[result] += 1
    return word


RULES = {
    "x_here": ("x_here", "x_departed", "real_slot", "previous_menu", "paid", "phase"),
    "x_departed": ("x_here", "x_departed", "real_slot", "phase"),
    **{x: (x, a, "paid") for x, a in zip(SECOND[2:], ARRIVAL, strict=True)},
    "arr_from": ("arr_from", "cue", "real_slot"),
    "arr_menu": ("arr_menu", "previous_menu", "real_slot"),
    "arr_slot": ("arr_slot", "real_slot"),
    "phase": ("phase",),
    **{key: (key, vote, "credit_paid", "previous_on") for key, vote in zip(SCORES, VOTES, strict=True)},
}


def evaluate_cell(target, row):
    if target == "x_here":
        here, depart, moved, menu, paid, phase = row
        if moved:
            return int(depart == 1 and menu == 1 and phase >= 4)
        return max(here, paid)
    if target == "x_departed":
        here, depart, moved, phase = row
        return int(here == 1 and phase >= 4) if moved else depart
    if target in SECOND[2:]:
        remember, arrival, actual_payment = row
        return arrival if actual_payment else remember
    if target in ("arr_from", "arr_menu"):
        old_value, origin, moves = row
        return origin + 1 if moves else old_value
    if target == "arr_slot":
        previous, now = row
        return now or previous
    if target == "phase":
        return min(row[0] + 1, 4)
    pos, voted, paid, action = row
    score = pos - 7
    change = 0 if not (action and voted) else -4 if paid else 1
    return min(7, max(-7, score + change)) + 7


def check_offer(obj):
    assert supports_offer(obj.holder, obj.operands, obj.guard)
    assert obj.supported and obj.guard_mask == mask(n for n, _ in obj.guard)
    assert obj.guard_word == sum(v << d for d, v in obj.guard)
    assert obj.change_mask == mask(obj.operands)
    assert all(sum(d in physical for d in obj.operands) in (0, 2) for physical in BILLS.values())


def tables_and_offers():
    old = implementation.old
    original = (*old.DETECT, *old.ADDRESS, *old.COMMIT, *old.READ, *old.CLEAR_ACTION,
                *old.EXPORT["memory"], *old.EXPORT["action"], old.SHAM)
    attached = (*implementation.MATCH, *(row for group in implementation.DETECTORS for row in group),
                *implementation.VETO, *implementation.OUTPUT, *implementation.CREDIT_DETECT,
                implementation.TRUE_CREDIT, *implementation.WINNER)
    for obj in original + attached:
        check_offer(obj)
    old_preparations = 0
    for b in old.PUBLIC:
        for x, y in product(BANKS[b], repeat=2):
            if x != y:
                assert supports_offer("H", (x, y), ())
                old_preparations += 1
    cases = {}
    clipped = Counter()
    for t in (*implementation.DYNAMICS, *implementation.CREDITS):
        inputs = RULES[t.target]
        assert t.inputs == inputs
        rows = tuple(product(*(range(len(BANKS[b])) for b in inputs)))
        assert set(t.rows) == set(rows)
        for row in rows:
            expected = evaluate_cell(t.target, row)
            issued = t.rows[row]
            if expected:
                assert issued.operands == (BANKS["new_" + t.target][0], BANKS["new_" + t.target][expected])
                assert issued.guard == tuple((BANKS[b][i], 1) for b, i in zip(inputs, row, strict=True))
                check_offer(issued)
            else:
                assert issued is None
            if t.target in SCORES and row[1] and row[3]:
                unbounded = row[0] + (-4 if row[2] else 1)
                clipped["upper" if unbounded > 14 else "lower" if unbounded < 0 else "unchanged_by_clip"] += 1
        cases[t.target] = len(rows)
    return {"literal_inherited_fixed_offers": len(original), "old_public_prepare_transpositions": old_preparations,
            "new_fixed_offers": len(attached), "guarded_truth_table_cases": cases,
            "score_updates_by_clip": dict(clipped), "all_operand_owner_lists_equal": True,
            "guards_unchanged_and_held_by_the_offering_holder": True}


def winner(scores):
    best = max(scores)
    return 0 if best <= 0 else scores.index(best) + 1


def scores_on(word):
    return tuple(marker(word, name) - 7 for name in SCORES)


def score_selector(law):
    neutral = initial(law)
    choices = Counter()
    ties = 0
    for scores in product(range(-7, 8), repeat=4):
        w = neutral
        for b, v in zip(SCORES, scores, strict=True):
            w = fill(w, b, v + 7)
        before = w
        expected = winner(scores)
        matches = [o for o in implementation.WINNER if all(bit(w, d) == val for d, val in o.guard)]
        assert len(matches) == int(expected > 0)
        for o in implementation.WINNER:
            w, _ = implementation.old.local_exchange(w, o)
        assert marker(w, "new_selector") == expected and w == fill(before, "new_selector", expected)
        choices[expected] += 1
        ties += bool(expected and scores.count(max(scores)) > 1)
    exact_transfers = 0
    statuses = Counter()
    for old, requested in product(range(5), repeat=2):
        b = board(law, {"selector": old, "new_selector": requested})
        start = b._word
        trace = []
        b._commit("selector", trace)
        assert trace_word(trace, start, law, statuses) == b._word
        assert b._word == fill(fill(start, "selector", requested), "new_selector", 0)
        assert trace[-1]["exported_index"] == old
        exact_transfers += 1
    return {"every_score_bank_word": sum(choices.values()), "highest_selector_counts": dict(choices),
            "positive_ties": ties, "verified_selector_deposit_cases": exact_transfers,
            "score_bound": [-7, 7], "zero_winner_if_all_scores_nonpositive": True}


@dataclass(frozen=True)
class Query:
    feeder: bool
    energy: int
    previous: str
    slots: tuple


def observation(feeder, slots, previous=False, energy=6):
    return Query(feeder, energy, "eat" if previous else "move", tuple(range(slots)))


def predict(word, obs, training=False):
    menu = min(2, len(obs.slots))
    current = obs.feeder and obs.previous != "eat"
    previous = MEMORY.index(bits(word, BANKS["m"]))
    eligible = current and menu != 0 and previous == menu
    features = [marker(word, "x_here") == 1]
    for old, new in zip(SECOND[2:], ARRIVAL, strict=True):
        recorded = marker(word, old)
        features.append(recorded != 0 and recorded == marker(word, new))
    votes = tuple(int(eligible and v) for v in features)
    selected = marker(word, "selector")
    blocked = bool(selected and votes[selected - 1] and not training)
    return int(current and not blocked), votes


def query_check(law, mode="learned"):
    results = Counter()
    statuses = Counter()
    selected_values = range(5) if mode == "learned" else (2,)
    pairs = ((0, 0), (1, 2), (1, 1))
    for m, menu, cue, previous, chosen, here, relations in product(
            range(3), (0, 1, 2), (False, True), (False, True), selected_values, (0, 1),
            product(pairs, repeat=3)):
        obs = observation(cue, menu, previous)
        fields = {"selector": chosen, "x_here": here}
        for name, a, (old, current) in zip(SECOND[2:], ARRIVAL, relations, strict=True):
            fields[name], fields[a] = old, current
        b = board(law, fields, m, mode)
        start = b._word
        step = b.checkpoint(obs, detail=True)
        assert trace_word(step, start, law, statuses) == b._word
        before = b._word
        answer, votes = predict(before, obs)
        emitted, trace = b.read_prepared(detail=True)
        assert trace_word(trace, before, law, statuses) == b._word
        assert emitted == answer == bit(b._word, 6)
        assert tuple(b.candidate_votes()) == votes
        assert bits(b._word, BANKS["a"]) == ACTION[2 if emitted else 1]
        assert b._word & ~mask((*BANKS["a"], *(d for role in VOTES for d in BANKS[role]))) == (
            before & ~mask((*BANKS["a"], *(d for role in VOTES for d in BANKS[role]))))
        noisy_current = int(cue and not previous)
        tag = "same-current" if noisy_current == emitted else "learned-suppression"
        results[tag] += 1
    return {"cases": sum(results.values()), "interventions_by_action": dict(results),
            "physical_offer_counts": dict(statuses)}


def step_oracle(word, obs, action, slot, new_energy, training=False, supplied=None):
    scores = scores_on(word)
    if training:
        votes = tuple(marker(word, v) for v in VOTES)
        real_credit = new_energy >= obs.energy
        selected_credit = real_credit if supplied is None else supplied >= obs.energy
        gain = 0 if not action else -4 if selected_credit else 1
        scores = tuple(min(7, max(-7, value + voted * gain)) for value, voted in zip(scores, votes, strict=True))
    paid = bool(action and new_energy >= obs.energy)
    before_x = tuple(marker(word, b) for b in SECOND)
    old_arrival = tuple(marker(word, b) for b in ARRIVAL)
    phase = marker(word, "phase")
    menu = min(2, len(obs.slots))
    if slot is None:
        second = (int(before_x[0] or paid), before_x[1], *(old_arrival if paid else before_x[2:]))
        arrived = old_arrival
    else:
        assert not action
        second = (int(phase == 4 and menu == 1 and before_x[1] == 1), int(phase == 4 and before_x[0] == 1),
                  *before_x[2:])
        arrived = (1 + int(obs.feeder), 1 + menu, 1 + slot % 2)
    expected = word
    for key, v in zip((*SECOND, *ARRIVAL, "phase"), (*second, *arrived, min(phase + 1, 4)), strict=True):
        expected = fill(expected, key, v)
    for key, v in zip(SCORES, scores, strict=True):
        expected = fill(expected, key, v + 7)
    if training:
        expected = fill(expected, "selector", winner(scores))
    memory = MEMORY[menu] if paid and menu else bits(word, BANKS["m"])
    expected = assign(expected, BANKS["m"], memory)
    for role in (*VOTES, "cue", "menu", "previous_on", "previous_menu", "energy_before", "energy_after",
                 "real_slot", "credit_energy", "credit_paid"):
        expected = fill(expected, role, 0)
    return expected, paid


def checked_transition(bot, obs, action, slot, energy, counters, credit=None):
    before = bot._word
    expected, actual = step_oracle(before, obs, action, slot, energy, bot.training, credit)
    result = bot.after_turn(obs, action, slot, energy, credit_energy_after=credit, detail=True)
    assert trace_word(result["offers"], before, bot.law, counters) == expected == bot._word
    assert result["detected"] == actual
    wanted_credit = int((energy if credit is None else credit) >= obs.energy and action) if bot.training else None
    assert result["credit_paid"] == wanted_credit
    return result


def train_and_turns(law):
    population = Counter()
    statuses = Counter()
    crossed = {}
    for phase, chosen, active, previous_x, energies, law_receipt in product(
            (0, 3, 4), (0, 1, 4), (False, True), (0, 1), (1, 6, 10), ("plain", "retained", "counterfactual")):
        args = {"selector": chosen, "x_here": previous_x, "phase": phase, "x_departed": 1 - previous_x,
                "score_0": 1, "score_1": 14, "score_2": 7, "score_3": 13}
        for a, n, i in zip(ARRIVAL, SECOND[2:], (1, 2, 1), strict=True):
            args[a] = args[n] = i
        e = energies
        motion = observation(False, 1, energy=e)
        feeding = observation(True, 1, energy=e)
        for case in ("paid", "empty", "move", "refused_move"):
            obs = feeding if case in ("paid", "empty") else motion if case == "move" else observation(False, 0, energy=e)
            bot = board(law, args, memory=1, training=active)
            begin = bot._word
            prep = bot.checkpoint(obs, detail=True)
            assert trace_word(prep, begin, law, statuses) == bot._word
            initial_query = bot._word
            bit_value, read = bot.read_prepared(detail=True)
            assert trace_word(read, initial_query, law, statuses,
                              ("selected physical veto to original coupler",) if active else ()) == bot._word
            assert bit_value == predict(initial_query, obs, active)[0]
            action = int(case in ("paid", "empty"))
            if active:
                assert bit_value == action
            slot = 0 if case == "move" else None
            plain_energy = e - 1
            paid_energy = min(10, e + 3)
            after = paid_energy if case == "paid" else plain_energy
            supplied = None
            if active and law_receipt != "plain":
                supplied = after if law_receipt == "retained" else paid_energy if after == plain_energy else plain_energy
            b = checked_transition(bot, obs, action, slot, after, statuses, supplied)
            population[case, active, law_receipt] += 1
            if active and law_receipt == "counterfactual" and action and phase == 4 and e == 10:
                crossed.setdefault(case, {"genuine_payment": b["detected"], "credit_payment": b["credit_paid"],
                                          "votes": b["votes"], "before_scores": b["before"]["scores"],
                                          "after_scores": b["after"]["scores"],
                                          "actual_memory": b["memory_after"], "actual_second_word": b["second_after"]})
            if active:
                policy = bot.export()
                start_policy = scores_on(bot._word), marker(bot._word, "selector")
                bot.begin_episode(training=False)
                assert all(marker(bot._word, n) == 0 for n in (*SECOND, *ARRIVAL, "phase"))
                assert (scores_on(bot._word), marker(bot._word, "selector")) == start_policy
                assert bot.export() == policy
    return {"cases": sum(population.values()), "physical_offer_counts": dict(statuses),
            "public_cases": [[*key, count] for key, count in sorted(population.items())],
            "counterfactual_credit_examples": crossed}


def memory_interventions(law):
    issues = Counter()
    statuses = Counter()
    samples = {}
    query = observation(True, 1)
    shapes = [range(len(BANKS[key])) for key in SECOND]

    def prepared(x, selected):
        fields = dict(zip(SECOND, x, strict=True)) | dict(zip(ARRIVAL, (1, 2, 1), strict=True))
        fields["selector"] = selected
        result = board(law, fields, memory=1)
        prior = result._word
        offers = result.checkpoint(query, detail=True)
        assert trace_word(offers, prior, law, statuses) == result._word
        return result

    def read_action(q):
        before = q._word
        output, offers = q.read_prepared(detail=True)
        assert trace_word(offers, before, law, statuses) == q._word
        assert (output, q.candidate_votes()) == predict(before, query)
        return output

    def changed_expected(word, fields, values):
        for field, v in zip(fields, values, strict=True):
            word = fill(word, field, v)
        return word

    for x, selected, equal in product(product(*shapes), range(5), (False, True)):
        y = x if equal else tuple(len(shape) - i - 1 for shape, i in zip(shapes, x, strict=True))
        first = tuple(prepared(word, selected) for word in (x, y))
        base_words = tuple(q._word for q in first)
        original = tuple(map(read_action, first))
        outcomes = {"original": original}
        for arm in ("sham", "whole_X", "selected_field", "erasure"):
            controllers = tuple(prepared(word, selected) for word in (x, y))
            assert tuple(q._word for q in controllers) == base_words
            if arm == "sham":
                paths = [q.sham(detail=True) for q in controllers]
                expected = base_words
            elif arm == "erasure":
                paths = [q.erase_second(detail=True) for q in controllers]
                expected = tuple(changed_expected(w, SECOND, (0,) * len(SECOND)) for w in base_words)
            else:
                fields = SECOND if arm == "whole_X" else ((SELECTED[selected],) if selected else ())
                transfer = controllers[0].exchange_second if arm == "whole_X" else controllers[0].exchange_selected
                paths = transfer(controllers[1], detail=True)
                expected = tuple(changed_expected(w, fields, (v[SECOND.index(f)] for f in fields))
                                 for w, v in zip(base_words, (y, x), strict=True))
            for q, w, want, trace in zip(controllers, base_words, expected, paths, strict=True):
                assert trace_word(trace, w, law, statuses) == q._word == want
            outcomes[arm] = tuple(map(read_action, controllers))
        assert outcomes["sham"] == original and outcomes["erasure"] == (1, 1)
        assert outcomes["whole_X"] == outcomes["selected_field"]
        if equal or not selected:
            assert original == outcomes["whole_X"]
        swapped = outcomes["whole_X"]
        assert swapped == original[::-1]
        key = (str(selected), "equal" if equal else "complement", "flips" if swapped != original else "unchanged")
        issues[key] += 1
        samples.setdefault("/".join(key), {"original_X_positions": [x, y], "marks_before": base_words,
                                           "action_bits_by_arm": outcomes})

    blocked = board(law, {"x_here": 0, "selector": 1})
    unprepared = board(law, {"x_here": 1, "selector": 1})
    blocked.checkpoint(query)
    first_state, second_state = blocked.snapshot(), unprepared.snapshot()
    try:
        blocked.exchange_second(unprepared, detail=True)
    except ValueError:
        assert (blocked.snapshot(), unprepared.snapshot()) == (first_state, second_state)
    else:
        raise AssertionError("Accepted unprepared second participant")
    unprepared.checkpoint(query)
    conflict = board(law, {"x_here": 1, "selector": 2})
    conflict.checkpoint(query)
    try:
        blocked.exchange_selected(conflict, detail=True)
    except ValueError:
        assert blocked.snapshot() == first_state
    else:
        raise AssertionError("Accepted different selectors")

    erasing = board(law, {"x_here": 1, "x_departed": 1, "selector": 1, "score_0": 10}, 1, "erased")
    prior = erasing._word
    recorded = erasing.checkpoint(query, detail=True)
    assert trace_word(recorded, prior, law, statuses) == erasing._word
    assert {n for n in (*SECOND, "selector", "score_0") if marker(erasing._word, n)} == {"selector", "score_0"}
    assert len([r for r in recorded if r.get("holder") == "X"]) == 2
    assert read_action(erasing) == 1
    return {"cases": sum(issues.values()), "exact_outputs": [[*k, v] for k, v in sorted(issues.items())],
            "offer_status_counts": dict(statuses), "selected_examples": samples,
            "reject_mismatched_or_unprepared_reciprocal_without_change": True,
            "erased_checkpoint_includes_actual_X_transpositions": True}


def historical_return_scope(law):
    """Expose a synthetic consistent receipt where the certified site is an older paid site."""
    d = board(law, {"phase": 4})
    status = Counter()
    marked = []
    for site, e, menu, taking, landing, after in (
            ("A", 6, 2, 1, None, 9), ("A", 9, 2, 0, 0, 8),
            ("B", 8, 1, 1, None, 10), ("B", 10, 1, 0, 0, 9)):
        obs = observation(True, menu, energy=e)
        start = d._word
        prep = d.checkpoint(obs, detail=True)
        assert trace_word(prep, start, law, status) == d._word
        ready = d._word
        _, p = d.read_prepared(detail=True)
        assert trace_word(p, ready, law, status) == d._word
        result = checked_transition(d, obs, taking, landing, after, status)
        marked.append({"synthetic_site_label": site, "actual_payment": result["detected"],
                       "x_here": marker(d._word, "x_here"), "left_paid_anchor": marker(d._word, "x_departed")})
    assert marker(d._word, "x_here") == 1
    assert [item["synthetic_site_label"] for item in marked if item["actual_payment"]] == ["A", "B"]
    return {"site_after_last_move": "A", "latest_paid_site": "B", "earlier_paid_site_is_certified": True,
            "synthetic_public_receipts": marked, "meaning": "The stable return target was paid earlier. The flag does not identify only the latest paid site."}


def transport_and_readonly(law):
    source = board(law, {"score_0": 8, "score_1": 11, "score_2": 13, "score_3": 7,
                         "selector": 3, "x_here": 1, "x_paid_menu": 2, "arr_menu": 2, "phase": 4}, memory=1)
    prepared = source.export()
    readonly = {}
    for mode in ("learned", "current", "zero", "erased", "permuted", *CUES[1:]):
        d = implementation.LearnedKnotBot.from_frozen(law, prepared, mode=mode)
        chosen = CUES.index(mode) if mode in CUES[1:] else 0 if mode in ("current", "zero") else 4 if mode == "permuted" else 3
        assert marker(d._word, "selector") == chosen
        assert scores_on(d._word) == ((0, 0, 0, 0) if mode == "zero" else (1, 4, 6, 0))
        d.begin_episode(training=False)
        prof = observation(True, 1, energy=10)
        original = d.export()
        expected, _ = predict(d._word, prof)
        decision = d.decide(prof)
        assert decision == expected == 1
        st = Counter()
        assert checked_transition(d, prof, 1, None, 10, st)["detected"]
        assert d.export() == original
        readonly[mode] = original

    broken = dict(prepared) | {"selector_word": "10000"}
    try:
        implementation.LearnedKnotBot.from_frozen(law, broken)
    except ValueError:
        pass
    else:
        raise AssertionError("Accepted incorrect transported word")

    for holder, pair, guard in (
            ("J", (BANKS[SECOND[0]][0], BANKS["new_x_here"][1]), ()),
            ("H", (BANKS["m"][0], BANKS["m"][1]), ((BANKS[SECOND[0]][0], 1),)),
            ("X", tuple(BANKS[SECOND[0]]), ((BANKS[SECOND[0]][0], 0),)),
            ("J", (BANKS["credit_energy"][0], BANKS["energy_before"][1]), ()),
    ):
        assert not supports_offer(holder, pair, guard)
        try:
            implementation.offer("negative physical mark", holder, pair, guard)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsupported motion compiled")

    src = board(law, {"selector": 1, "x_here": 1, "x_departed": 1, "phase": 4}, 1)
    obs = observation(True, 1, energy=10)
    initial_word = src._word
    groups = src.checkpoint(obs, detail=True)
    bit_out, offers = src.read_prepared(detail=True)
    groups += offers
    assert bit_out == 0
    after = src.after_turn(obs, 0, 0, 9, detail=True)
    groups += after["offers"]
    transports = []
    for seed in (2026112130701, 2026112130702):
        rng = Random(seed)
        renames = dict(zip(NAMES, rng.sample(range(500, 4 * len(NAMES) + 500), len(NAMES)), strict=True))
        labels = list(BILLS)
        renamed = labels[:]
        rng.shuffle(renamed)
        role = dict(zip(labels, renamed, strict=True))
        owners = {renames[n]: frozenset(role[h] for h in OWNERS[n]) for n in NAMES}
        mapped_masks = tuple(mask(renames[n] for n in row) for row in BILLS.values())

        def recode(w):
            return sum(bit(w, n) << k for n, k in renames.items())

        w = recode(initial_word)
        checked = 0
        for step in groups:
            if "fixed_local_table" in step:
                continue
            assert w == recode(step["before"]) and legal(w, law, mapped_masks)
            if "external_exchange" in step:
                bank = step["bank"]
                translated = tuple(renames[d] for d in BANKS[bank])
                if "exported_index" in step:
                    incoming = "0" * step["incoming_index"] + "1" + "0" * (len(translated) - step["incoming_index"] - 1)
                else:
                    incoming = step["incoming"]
                w = assign(w, translated, incoming)
            else:
                pair = tuple(renames[n] for n in step["operands"])
                guard = tuple((renames[n], v) for n, v in step["guard"])
                w, status = swap_value(w, role[step["holder"]], pair, guard, owners=owners)
                assert status == step["status"]
            assert w == recode(step["after"]) and legal(w, law, mapped_masks)
            checked += 1
        assert bit(w, renames[6]) == bit_out
        transports.append({"seed": seed, "role_transport": role, "mark_transport": renames,
                           "actual_output_name": renames[6], "unchanged_action": bit_out, "mark_level_steps": checked})
    return {"all_supplied_modes_evaluation_readonly": readonly, "mismatched_selector_transport_refused": True,
            "cross_holder_and_changed_guard_alternatives_refused": 4, "transported_role_and_name_replays": transports}


def provenance():
    binding = json.loads((HERE / "advisor.json").read_bytes())
    design = (HERE / "preregistration.md").read_text()
    assert sha256((HERE / "device_design.md").read_bytes()).hexdigest() in design
    assert sha256((HERE / "preregistration.md").read_bytes()).hexdigest() in json.dumps(binding)
    dependencies = (Path(__file__).resolve(), HERE / "device.py", HERE / "advisor.json", HERE / "preregistration.md",
                    HERE / "device_design.md", PREVIOUS / "keeper.py", PREVIOUS / "keeper_verified.json",
                    ROOT / "tools/knotlab/cli.py", ROOT / "tools/knotlab/knots.py", ROOT / "tools/knotlab/relations.py")
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in dependencies}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "device_verified.json")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    receipt = {"schema": "b307-independent-device-v1", "physical_shape": shape_audit(),
               "named_banks": BANKS, "checked_offers": tables_and_offers(), "source_hashes": provenance(), "laws": {},
               "scope": "Exact synthetic full-word, allowed-relation and supplied public-interface cases. No fresh game or training-fold history is run."}
    for law in LAWS:
        receipt["laws"][law] = {
            "unrestricted_projections": extent_certificate(law),
            "all_score_selector_words": score_selector(law),
            "guarded_queries": query_check(law),
            "public_energy_and_credit": train_and_turns(law),
            "memory_interventions": memory_interventions(law),
            "actual_return_scope": historical_return_scope(law),
            "physical_transports_and_readonly": transport_and_readonly(law),
        }
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    if args.verify:
        assert raw == args.output.read_bytes()
    else:
        temp = args.output.with_suffix(".tmp")
        temp.write_bytes(raw)
        temp.replace(args.output)
    print(sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
