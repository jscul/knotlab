"""Independent exact physical oracle for the B306 prepared keeper."""

import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from hashlib import sha256
import json
import os
from random import Random
import subprocess
import sys

import keeper as device


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAWS = ("parity", "nae")
MEMORY = ("110", "101", "011")
ACTION = ("100", "010", "001")
BANK_WIDTHS = (
    ("m", 3), ("memory_slack", 1), ("a", 3), ("action_slack", 1),
    ("t", 3), ("m_out", 3), ("a_scratch", 3), ("a_out", 3),
    ("paid", 2), ("previous_on", 2), ("previous_menu", 3),
    ("energy_before", 11), ("energy_after", 11), ("cue", 2), ("menu", 3), ("coupler_slack", 1),
)
PUBLIC = ("previous_on", "previous_menu", "energy_before", "energy_after", "cue", "menu")
ENERGIES = range(1, 11)
SLOTS = (0, 1, 2, 5)
CAPACITY = 10
RATION_GAIN = 4


def make_banks():
    names = {}
    first = 0
    for bank, width in BANK_WIDTHS:
        names[bank] = tuple(range(first, first + width))
        first += width
    return names


BANKS = make_banks()
M, A, T = BANKS["m"], BANKS["a"], BANKS["t"]
ALL = tuple(range(sum(width for _, width in BANK_WIDTHS)))
STARS = {
    "M": (*M, *BANKS["memory_slack"]),
    "K": (*A, *BANKS["action_slack"]),
    "H": tuple(d for d in ALL if d not in BANKS["memory_slack"] + BANKS["action_slack"]),
}
OWNERS = {d: frozenset(h for h in STARS if d in STARS[h]) for d in ALL}


def bit_mask(scope):
    return sum(1 << d for d in scope)


STAR_MASKS = tuple(map(bit_mask, STARS.values()))


def bit(word, name):
    return (word >> name) & 1


def read(word, names):
    return "".join(str(bit(word, d)) for d in names)


def assign(word, names, digits):
    return (word & ~bit_mask(names)) | sum((value == "1") << d for d, value in zip(names, digits, strict=True))


def canonical(digits, law):
    count = digits.count("1")
    return count % 2 == 0 if law == "parity" else 0 < count < len(digits)


def legal(word, law, supports=STAR_MASKS):
    if law == "parity":
        return all((word & scope).bit_count() % 2 == 0 for scope in supports)
    return all(word & scope not in (0, scope) for scope in supports)


def base(law, memory=MEMORY[0], action=ACTION[0]):
    prepared = {
        "m": memory, "memory_slack": "0", "a": action, "action_slack": "1",
        "t": MEMORY[0], "m_out": MEMORY[0], "a_scratch": ACTION[0], "a_out": ACTION[0],
        "paid": "10", **{reg: "1" + "0" * (len(BANKS[reg]) - 1) for reg in PUBLIC},
        "coupler_slack": "0",
    }
    word = sum(assign(0, BANKS[key], value) for key, value in prepared.items())
    if law == "parity" and not legal(word, law):
        word |= bit_mask(BANKS["coupler_slack"])
    assert legal(word, law)
    return word


def from_word(law, word=None, writer=True, reader=True):
    obj = device.KnotKeeper(law, writer=writer, reader=reader)
    assert obj._word == base(law)
    if word is not None:
        assert legal(word, law)
        obj._word = word
    return obj


def strings(width):
    return ("".join(p) for p in product("01", repeat=width))


def cli_check(scope, projected, law):
    names = [f"n{d}" for d in scope]
    forbidden = sorted(set(strings(len(scope))) - set(projected))
    cnf = "; ".join(" ".join((f"~{d}" if val == "1" else d) for d, val in zip(names, word, strict=True))
                    for word in forbidden)
    args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops",
            *names[:-1], "--contact", names[-1], "--json"]
    output = subprocess.run(args, check=True, text=True, capture_output=True, cwd=ROOT,
                            env=os.environ | {"PYTHONPATH": str(ROOT / "tools")})
    result = json.loads(output.stdout)
    assert result["is_knot"] and result["binding"] and result["coexistence"] and result["invisible_in_parts"]
    assert set(result["allowed"]) == set(projected), (scope, law)
    return {"named_distinctions": names, "allowed_words": result["allowed"],
            "binding": result["binding"], "coexistence": result["coexistence"],
            "invisible_in_parts": result["invisible_in_parts"],
            "one_name_omissions": [len({w[:i] + w[i+1:] for w in projected}) for i in range(len(scope))]}


def projections(law):
    assert len(ALL) == 55 and tuple(map(len, STARS.values())) == (4, 4, 53)
    assert [d for d in ALL if len(OWNERS[d]) == 2] == list(M + A)
    private_h = tuple(d for d in STARS["H"] if OWNERS[d] == {"H"})
    assert len(private_h) == 47
    boundary = []
    for word in strings(6):
        mem, action = word[:3], word[3:]
        m_choices = tuple(b for b in "01" if canonical(mem + b, law))
        k_choices = tuple(b for b in "01" if canonical(action + b, law))
        h_total = 1 << 46 if law == "parity" else (1 << 47) - int(word in ("000000", "111111"))
        # Verify that the three independent private completions really join
        # with the exact six shared names held by the implemented board.
        h_one = next(bits for bits in ("0" * 47, "1" + "0" * 46)
                     if canonical(word + bits, law))
        for m_bit, a_bit in product(m_choices, k_choices):
            sample = 0
            for names, digits in ((M + A, word), (private_h, h_one), (BANKS["memory_slack"], m_bit),
                                  (BANKS["action_slack"], a_bit)):
                sample = assign(sample, names, digits)
            assert legal(sample, law) and device.admissible(sample, law)
        boundary.append({"shared_word_m_then_a": word, "M_private_completions": m_choices,
                         "K_private_completions": k_choices, "H_private_completion_count": h_total,
                         "H_one_private_completion": h_one})
    worlds = sum(len(row["M_private_completions"]) * len(row["K_private_completions"]) *
                 row["H_private_completion_count"] for row in boundary)
    h_rows = sum(row["H_private_completion_count"] for row in boundary)
    assert h_rows == ((1 << 52) if law == "parity" else (1 << 53) - 2)
    assert worlds == ((1 << 52) if law == "parity" else 196 * (1 << 47) - 2)
    records = {}
    for tag, s in (("M", slice(None, 3)), ("K", slice(3, None))):
        words = tuple(sorted({r["shared_word_m_then_a"][s] + b for r in boundary
                              for b in r[f"{tag}_private_completions"]}))
        assert words == tuple(w for w in strings(4) if canonical(w, law))
        records[tag] = cli_check(STARS[tag], words, law)
    return {
        "complete_unrestricted_word_count": worlds, "boundary_certificate": boundary, **records,
        "H": {"arity": 53, "private_names": private_h, "true_shared_names": M + A,
              "full_projection": law, "allowed_word_count": h_rows,
              "each_proper_omission_free": True, "one_name_omission_word_count": 1 << 52,
              "K1_K2_K3": True,
              "extension": "Complete M and K independently at their separate private names for each fixed shared word. Every admissible H word at that boundary therefore extends. For H every one-name deletion has a completion at the forgotten name."},
    }


def guard_support(holder, operands, guard, holdings=STARS, owners=OWNERS):
    x, y = operands
    held = holdings[holder]
    return (x != y and x in held and y in held and owners[x] == owners[y]
            and all(name in held and name not in (x, y) and value in (0, 1) for name, value in guard))


def exchange_oracle(word, holder, operands, guard=(), connected=True, *, holdings=STARS, owners=OWNERS):
    if not connected:
        return word, "disconnected"
    if not guard_support(holder, operands, guard, holdings, owners):
        return word, "unsupported"
    if any(bit(word, d) != val for d, val in guard):
        return word, "guard refused"
    x, y = operands
    if bit(word, x) == bit(word, y):
        return word, "equal operands"
    return word ^ bit_mask(operands), "changed"


def check_offer(word, action, law, enabled=True):
    assert legal(word, law)
    assert action.supported == guard_support(action.holder, action.operands, action.guard)
    assert action.guard_mask == bit_mask(d for d, _ in action.guard)
    assert action.guard_word == sum(v << d for d, v in action.guard)
    oracle = exchange_oracle(word, action.holder, action.operands, action.guard, enabled)
    assert device.local_exchange(word, action, enabled) == oracle
    assert legal(oracle[0], law)
    if action.supported:
        # Holder sums, including every holder beyond the acting knot, are
        # unchanged for each possible value of the guard.
        assert all(sum(d in row for d in action.operands) in (0, 2) for row in STARS.values())
    return oracle


def run_offers(word, schedule, law, connected=True):
    statuses = Counter()
    for action in schedule:
        word, reason = check_offer(word, action, law, connected)
        statuses[reason] += 1
    return word, statuses


def trit_permutation(left, right, codes):
    """Independent three-symbol form of each elementary controlled permutation."""
    pair = [codes.index(left), codes.index(right)]
    moves = 0
    for low, high in combinations(range(3), 2):
        replacement = {low: high, high: low}
        for side in (0, 1, 0):
            current = pair[side]
            if pair[1 - side] == high and current in replacement:
                pair[side] = replacement[current]
                moves += 1
    assert tuple(pair) == (codes.index(right), codes.index(left))
    return moves


def transfer_checks(law):
    status = Counter()
    m_cases = a_cases = 0
    sample = {}
    for left, right, paid, menu, connected in product(MEMORY, MEMORY, (0, 1), (0, 1, 2), (False, True)):
        initial = assign(base(law, memory=left), T, right)
        initial = assign(initial, BANKS["paid"], "01" if paid else "10")
        initial = assign(initial, BANKS["previous_menu"], "0" * menu + "1" + "0" * (2 - menu))
        actual, counts = run_offers(initial, device.COMMIT, law, connected)
        active = connected and paid and menu != 0
        expected = assign(assign(initial, M, right), T, left) if active else initial
        assert actual == expected
        status.update(counts)
        m_cases += 1
        assert counts["changed"] == (trit_permutation(left, right, MEMORY) if active else 0)
        if active and left != right:
            sample.setdefault(str(menu), {"before": initial, "after": actual, "memory_before": left,
                                           "receipt_before": right, "changed_offers": counts["changed"]})

    for left, right, connected in product(ACTION, ACTION, (False, True)):
        initial = assign(base(law, action=left), BANKS["a_scratch"], right)
        actual, counts = run_offers(initial, device.CLEAR_ACTION, law, connected)
        expected = assign(assign(initial, A, right), BANKS["a_scratch"], left) if connected else initial
        assert actual == expected
        assert counts["changed"] == (trit_permutation(left, right, ACTION) if connected else 0)
        status.update(counts)
        a_cases += 1
    return {"all_memory_receipt_product_cases": m_cases, "all_action_scratch_product_cases": a_cases,
            "offer_status_counts": dict(status), "nonidentity_transfer_examples": sample,
            "local_changes_for_each_enabled_trit_exchange": [
                [left, right, trit_permutation(left, right, MEMORY)] for left, right in product(MEMORY, repeat=2)]}


def independent_trace(trace, initial, law, counts):
    word = initial
    for event in trace:
        assert event["before"] == word and legal(word, law)
        if "external_exchange" in event:
            bank = event["bank"]
            assert bank in ("m_out", "a_out")
            ready = MEMORY[0] if bank == "m_out" else ACTION[0]
            assert event["exported"] == read(word, BANKS[bank]) and event["incoming"] == ready
            after = assign(word, BANKS[bank], ready)
            reason = "supplied export and refill"
        else:
            operands, guard = tuple(event["operands"]), tuple(event["guard"])
            after, reason = exchange_oracle(word, event["holder"], operands, guard,
                                             connected=event["status"] != "disconnected")
            assert event["status"] == reason
            assert event["guard_actual"] == [bit(word, d) for d, _ in guard]
            assert event["toggled"] == [d for d in operands if bit(after, d) != bit(word, d)]
        assert event["after"] == after and legal(after, law)
        counts[reason] += 1
        word = after
    return word


def select_menu(slots):
    return 0 if slots == 0 else 1 if slots == 1 else 2


def decision_oracle(memory, cue, slots, enabled):
    same_recent_type = slots > 0 and memory == select_menu(slots)
    on = cue and not same_recent_type
    return (int(on), ACTION[2 if on else 1]) if enabled else (0, ACTION[0])


def energy_oracle(cue, on, energy):
    allowed = {energy - 1: False}
    if on and cue:
        allowed[min(CAPACITY, energy - 1 + RATION_GAIN)] = True
    return allowed


def one_hot(word, register, index):
    return assign(word, BANKS[register], "".join("1" if k == index else "0" for k in range(len(BANKS[register]))))


def checkpoints(law):
    records = {}
    statuses = Counter()
    total = 0
    for m, a, cue, slots, reader, tuple_slots in product(range(3), range(3), (False, True), SLOTS,
                                                         (False, True), (False, True)):
        prior = base(law, MEMORY[m], ACTION[a])
        # The previous public banks may carry different values and must clear.
        prior = one_hot(one_hot(prior, "cue", int(not cue)), "menu", (select_menu(slots) + 1) % 3)
        obj = from_word(law, prior, reader=reader)
        menu = tuple(f"anonymous {j}" for j in reversed(range(slots))) if tuple_slots else slots
        prep = obj.checkpoint(cue, menu, detail=True)
        expected = one_hot(one_hot(base(law, MEMORY[m]), "cue", int(cue)), "menu", select_menu(slots))
        assert independent_trace(prep, prior, law, statuses) == expected == obj._word
        assert [e["exported"] for e in prep if e.get("bank") == "a_out"] == [ACTION[a]]
        got, events = obj.read_prepared(detail=True)
        answer, word = decision_oracle(m, cue, slots, reader)
        assert (got, obj.action_word) == (answer, word)
        assert independent_trace(events, expected, law, statuses) == assign(expected, A, word) == obj._word
        assert got == bit(obj._word, A[2])
        total += 1
        if a == 0 and not tuple_slots:
            records[f"{MEMORY[m]}/{int(cue)}/{slots}/{int(reader)}"] = [got, word]
    return {"cases": total, "offer_status_counts": dict(statuses), "outputs": records}


def public_writes(law):
    counts, statuses = Counter(), Counter()
    samples = {}
    for m, a, cue, slots, on, e, writer in product(range(3), range(3), (False, True), SLOTS, (0, 1), ENERGIES,
                                                   (False, True)):
        legal_transitions = energy_oracle(cue, on, e)
        for after, received in legal_transitions.items():
            prior = base(law, MEMORY[m], ACTION[a])
            obj = from_word(law, prior, writer=writer)
            out = obj.after_turn(cue, slots, e, on, after, detail=True)
            detected = received and writer
            t = select_menu(slots) if detected else 0
            old_export = MEMORY[m] if t else MEMORY[0]
            expected_word = assign(prior, M, MEMORY[t]) if t else prior
            assert (out["memory_before"], out["memory_after"], out["detected"], out["addressed_receipt_word"],
                    out["exported_previous_memory"]) == (MEMORY[m], MEMORY[t] if t else MEMORY[m], detected,
                                                        MEMORY[t], old_export)
            assert independent_trace(out["offers"], prior, law, statuses) == expected_word == obj._word
            assert obj.action_word == ACTION[a]
            receipt_events = [r for r in out["offers"] if r.get("offer", "").startswith(
                ("issued ON", "write observed", "exchange physical"))]
            assert all((r["status"] == "disconnected") == (not writer) for r in receipt_events)
            receipt_kind = ("writer disconnected" if not writer else "no received meal" if not received
                            else "unaddressed zero-menu" if not t else "repeat same type" if t == m else "write new type")
            counts[receipt_kind] += 1
            if received and after == e:
                counts["cap with unchanged energy"] += 1
            if received and after == CAPACITY:
                counts["meal reaching capacity"] += 1
            samples.setdefault(receipt_kind, {"public": [cue, slots, e, on, after],
                                               "start": prior, "end": obj._word, "after": out["memory_after"],
                                               "actual_exported_old_word": out["exported_previous_memory"]})
    valid_cases = sum(v for k, v in counts.items() if k not in ("cap with unchanged energy", "meal reaching capacity"))
    assert valid_cases == 3600

    rejected = 0
    obj = from_word(law)
    baseline_word = obj._word
    initial = obj.snapshot()
    for cue, slots, on, e, after in product((False, True), SLOTS, (0, 1), range(0, 12), range(-1, 12)):
        if e in ENERGIES and after in energy_oracle(cue, on, e):
            continue
        try:
            obj.after_turn(cue, slots, e, on, after, detail=True)
        except ValueError:
            assert obj.snapshot() == initial and obj._word == baseline_word
        else:
            raise AssertionError((cue, slots, on, e, after))
        rejected += 1

    sequential = from_word(law)
    executions = []
    for cue, slots, e, on, after in ((True, 1, 7, 1, 10), (False, 2, 10, 0, 9),
                                     (True, 2, 9, 1, 8), (True, 1, 8, 1, 10),
                                     (True, 0, 10, 1, 10), (True, 2, 10, 1, 10)):
        before = sequential._word
        receipt = sequential.after_turn(cue, slots, e, on, after, detail=True)
        assert independent_trace(receipt.pop("offers"), before, law, statuses) == sequential._word
        executions.append(receipt)
    assert [r["memory_after"] for r in executions] == [MEMORY[1]] * 5 + [MEMORY[2]]
    assert [r["exported_previous_memory"] for r in executions] == [MEMORY[0], MEMORY[0], MEMORY[0],
                                                                  MEMORY[1], MEMORY[0], MEMORY[1]]
    return {"cases": valid_cases, "rejected_public_inputs_unchanged": rejected,
            "transition_counts": dict(counts), "selected_examples": samples,
            "sequential_device_calibration": executions, "offer_status_counts": dict(statuses)}


def reciprocal(law):
    totals = Counter()
    statuses = Counter()
    example = {}
    for m0, m1, a0, a1, cue, slots, reader in product(range(3), range(3), range(3), range(3),
                                                       (False, True), SLOTS, (False, True)):
        def prepared(mem, act):
            prior = base(law, MEMORY[mem], ACTION[act])
            board = from_word(law, prior, reader=reader)
            path = board.checkpoint(cue, slots, detail=True)
            assert independent_trace(path, prior, law, statuses) == board._word
            return board

        baselines = (prepared(m0, a0), prepared(m1, a1))
        exchange = (prepared(m0, a0), prepared(m1, a1))
        shams = (prepared(m0, a0), prepared(m1, a1))
        copied = tuple(obj._word for obj in baselines)
        assert tuple(obj._word for obj in shams) == tuple(obj._word for obj in exchange) == copied
        phase = tuple(obj.snapshot()[:4] for obj in exchange)
        paths = exchange[0].exchange_memory(exchange[1], detail=True)
        crossed = tuple(obj._word for obj in exchange)
        for i, (before, after, path) in enumerate(zip(copied, crossed, paths, strict=True)):
            expected_word = assign(before, M, MEMORY[(m1, m0)[i]])
            assert independent_trace(path, before, law, statuses) == after == expected_word
            assert (before ^ after).bit_count() == (0 if m0 == m1 else 2)
            assert (before ^ after) & ~bit_mask(M) == 0
        assert tuple(obj.snapshot()[:4] for obj in exchange) == phase
        for obj, before in zip(shams, copied, strict=True):
            trace = obj.sham(detail=True)
            assert independent_trace(trace, before, law, statuses) == obj._word == before
            assert len(trace) == 2
        bits = {}
        for key, arms, mems in (("base", baselines, (m0, m1)), ("cross", exchange, (m1, m0)), ("sham", shams, (m0, m1))):
            got = []
            for obj, m in zip(arms, mems, strict=True):
                before = obj._word
                act, trace = obj.read_prepared(detail=True)
                expect = decision_oracle(m, cue, slots, reader)
                assert independent_trace(trace, before, law, statuses) == obj._word
                assert (act, obj.action_word) == expect
                got.append(act)
            bits[key] = got
        assert bits["cross"] == bits["base"][::-1] and bits["sham"] == bits["base"]
        disposition = "equal-memory" if m0 == m1 else "ready-and-filled" if 0 in (m0, m1) else "one-and-many"
        effect = "reciprocal-flip" if bits["base"][0] != bits["base"][1] else "same-bit"
        combinations = f"{disposition}/{effect}/{int(reader)}"
        totals[combinations] += 1
        example.setdefault(combinations, {"memory_start": [MEMORY[m0], MEMORY[m1]], "old_action": [ACTION[a0], ACTION[a1]],
                                          "public_query": [cue, slots], "before": copied, "after": crossed,
                                          "read_bits": bits})
    return {"cases": sum(totals.values()), "by_intervention_and_effect": dict(totals),
            "offer_status_counts": dict(statuses), "examples": example}


def negative_controls(law):
    malformed = [
        ("memory-to-receipt", "H", (M[0], T[0]), ()),
        ("action-to-scratch", "H", (A[0], BANKS["a_scratch"][0]), ()),
        ("memory-to-action", "H", (M[0], A[0]), ()),
        ("receipt-guard-at-M", "M", M[:2], ((T[0], 1),)),
        ("private-M-guard-at-H", "H", M[:2], ((BANKS["memory_slack"][0], 0),)),
        ("guard-reads-operand", "H", M[:2], ((M[0], 1),)),
        ("operand-absent-on-K", "K", M[:2], ()),
        ("same-name-twice", "H", (M[0], M[0]), ()),
    ]
    invalid = []
    initial = base(law, MEMORY[1], ACTION[2])
    for label, holder, pair, guard in malformed:
        offered = device.swap(label, pair, guard, holder)
        assert check_offer(initial, offered, law) == (initial, "unsupported")
        invalid.append({"offer": label, "holder": holder, "pair": pair, "guard": guard,
                        "status": "unsupported", "held": [sorted(OWNERS[d]) for d in pair]})
    try:
        device.swap("duplicated named guard", M[:2], ((T[0], 1), (T[0], 1)), "H")
    except ValueError:
        repeated = True
    else:
        raise AssertionError("Duplicate guard admitted")

    board = from_word(law, initial)
    checkpoint = board.snapshot()
    for action in (board.read_prepared, board.sham, lambda: board.exchange_memory(from_word(law))):
        try:
            action()
        except ValueError:
            assert board.snapshot() == checkpoint
        else:
            raise AssertionError("Unprepared intervention reached a move")
    board.checkpoint(True, 1)
    other = from_word("nae" if law == "parity" else "parity")
    other.checkpoint(True, 1)
    old_words = (board._word, other._word)
    try:
        board.exchange_memory(other)
    except ValueError:
        assert (board._word, other._word) == old_words
    else:
        raise AssertionError("Mixed-law exchange reached a move")

    tamper = Counter()
    named = Counter()
    for mem, act, d in product(MEMORY, ACTION, ALL):
        w = base(law, mem, act)
        u = w ^ (1 << d)
        assert legal(u, law) == device.admissible(u, law)
        result = "lawful" if legal(u, law) else "unlawful"
        tamper[result] += 1
        named[str(tuple(sorted(OWNERS[d]))), result] += 1
    assert tamper == {"unlawful" if law == "parity" else "lawful": 495}

    special = []
    if law == "nae":
        # Lawful unrestricted words close to a forbidden constant row.
        w_m = assign(base(law), BANKS["memory_slack"], "1")
        w_k = assign(base(law), BANKS["action_slack"], "0")
        h_bit = BANKS["coupler_slack"][0]
        w_h = bit_mask((*BANKS["memory_slack"], *BANKS["action_slack"], h_bit))
        for holder, w, d in (("M", w_m, M[2]), ("K", w_k, A[0]), ("H", w_h, h_bit)):
            u = w ^ (1 << d)
            assert legal(w, law) and not legal(u, law) and device.admissible(w, law) and not device.admissible(u, law)
            failures = [name for name, star in STARS.items() if not canonical(read(u, star), law)]
            assert failures == [holder]
            special.append({"holder": holder, "changed_name": d, "old_scope": read(w, STARS[holder]),
                            "new_scope": read(u, STARS[holder])})
    return {"unsupported_offers": invalid, "duplicate_guard_refused": repeated,
            "unprepared_and_mixed_law_calls_refused": True, "single_bit_tampers_on_prepared_words": dict(tamper),
            "single_bit_tampers_by_owner_class": [[*key, val] for key, val in sorted(named.items())],
            "near_constant_NAE_tampers": special}


def recode_word(word, renaming):
    return sum(bit(word, d) << renamed for d, renamed in renaming.items())


def transports(law):
    obj = from_word(law)
    initial = obj._word
    first = obj.after_turn(True, 1, 8, 1, 10, detail=True)
    second = obj.after_turn(True, 4, 10, 1, 10, detail=True)
    prep = obj.checkpoint(True, 1, detail=True)
    bit_out, issued = obj.read_prepared(detail=True)
    assert bit_out == 1
    full_path = first["offers"] + second["offers"] + prep + issued
    all_records = []
    for seed in (202611213060, 202611213061):
        rng = Random(seed)
        encoded = dict(zip(ALL, rng.sample(range(70, 300), len(ALL)), strict=True))
        old_roles = list(STARS)
        new_roles = old_roles[:]
        rng.shuffle(new_roles)
        roles = dict(zip(old_roles, new_roles, strict=True))
        held = {roles[n]: tuple(encoded[d] for d in row) for n, row in STARS.items()}
        owners = {encoded[d]: frozenset(roles[n] for n in OWNERS[d]) for d in ALL}
        checks = tuple(map(bit_mask, held.values()))
        word = recode_word(initial, encoded)
        status = Counter()
        for r in full_path:
            assert word == recode_word(r["before"], encoded) and legal(word, law, checks)
            if "external_exchange" in r:
                scope = tuple(encoded[d] for d in BANKS[r["bank"]])
                assert read(word, scope) == r["exported"]
                word = assign(word, scope, r["incoming"])
                status["supplied export and refill"] += 1
            else:
                operands = tuple(encoded[d] for d in r["operands"])
                guard = tuple((encoded[d], v) for d, v in r["guard"])
                word, why = exchange_oracle(word, roles[r["holder"]], operands, guard, holdings=held, owners=owners)
                assert why == r["status"]
                status[why] += 1
            assert word == recode_word(r["after"], encoded) and legal(word, law, checks)
        assert bit(word, encoded[A[2]]) == bit_out
        assert read(word, tuple(encoded[d] for d in M)) == MEMORY[2]
        all_records.append({"seed": seed, "holder_transport": roles, "name_transport": encoded,
                            "actual_action_name": encoded[A[2]], "action_bit": bit_out,
                            "saved_memory": MEMORY[2], "status_counts": dict(status)})
    return all_records


def source_receipt():
    assert BANKS == device.NAMES and STARS == device.STARS
    assert PUBLIC == device.PUBLIC and tuple(device.MEMORY_CODES) == MEMORY and tuple(device.ACTION_CODES) == ACTION
    assert dict(OWNERS) == {d: frozenset(names) for d, names in device.OWNERS.items()}
    approvals = json.loads((HERE / "advisor.json").read_bytes())
    assert sha256((HERE / "preregistration.md").read_bytes()).hexdigest() == approvals["approved"]
    assert sha256((HERE / "keeper_design.md").read_bytes()).hexdigest() == approvals["keeper"]
    sources = (Path(__file__).resolve(), HERE / "keeper.py", HERE / "preregistration.md", HERE / "keeper_design.md",
               HERE / "advisor.json", ROOT / "research/KNOT-RATION-GAME-20261121-001/game.py",
               *(ROOT / "tools/knotlab" / label for label in ("cli.py", "knots.py", "relations.py")))
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources}


def static_offers():
    schedules = {"meal_detector": device.DETECT, "address": device.ADDRESS, "memory_exchange": device.COMMIT,
                 "decision_read": device.READ, "action_clear": device.CLEAR_ACTION,
                 "memory_export": device.EXPORT["memory"], "action_export": device.EXPORT["action"],
                 "sham": (device.SHAM,)}
    for rows in schedules.values():
        for r in rows:
            assert r.supported and guard_support(r.holder, r.operands, r.guard)
            assert len({d for d, _ in r.guard}) == len(r.guard)
    # Dynamic loads are unguarded moves within one fully H-private bank.
    public_preparations = 0
    for reg in PUBLIC:
        for x, y in product(BANKS[reg], repeat=2):
            if x != y:
                assert guard_support("H", (x, y), ())
                public_preparations += 1
    return {"fixed_schedule_offer_counts": {k: len(v) for k, v in schedules.items()},
            "supported_distinct_ordered_public_preparations": public_preparations,
            "every_offer_preserves_all_holder_bit_counts": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE / "keeper_verified.json")
    args = parser.parse_args()
    hashes = source_receipt()
    record = {"schema": "B306-independent-keeper-physical-1", "holdings": STARS, "named_banks": BANKS,
              "single_actuator_name": A[2], "sources_sha256": hashes, "static_offers": static_offers(),
              "scope": "A separately prepared physical keeper. All inputs in these cases are synthetic public values; real feeder histories and causal comparison denominators are measured separately.",
              "laws": {}}
    for law in LAWS:
        record["laws"][law] = {"unrestricted_projections": projections(law), "register_exchanges": transfer_checks(law),
                               "action_reads": checkpoints(law), "public_write_receipts": public_writes(law),
                               "reciprocal_and_sham": reciprocal(law), "negative_controls": negative_controls(law),
                               "physical_recodings": transports(law)}
    data = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode()
    if args.verify:
        assert args.output.read_bytes() == data
    else:
        staging = args.output.with_suffix(".tmp")
        staging.write_bytes(data)
        staging.replace(args.output)
    print(sha256(data).hexdigest())


if __name__ == "__main__":
    main()
