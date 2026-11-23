"""Exact all-policy optimization by a signed test of the receiver's record."""

from fractions import Fraction
from itertools import product
from math import gcd

import numpy as np


VIEWS = {"blind": 1, "bit": 2, "detector": 8, "guard": 8, "guard_and_bit": 16, "type": 2}
READINGS = ("gain", "published_bit", "old_bit_and_gain", "view_and_gain")
ADDRESSES = (0, 1)


def ratio(numerator, denominator):
    q = Fraction(int(numerator), int(denominator))
    return [q.numerator, q.denominator]


def projection(state, receiver, record, readout):
    bit = state.first_bit(receiver)
    if readout == "published_bit":
        return 0 if bit else None
    if readout == "gain":
        return 0
    if readout == "old_bit_and_gain":
        return bit
    return state.observes(receiver, record)


def matrix(states, sender, sender_view, receiver_view, record, readout, menu):
    receiver = 1 - sender
    s, r = VIEWS[sender_view], VIEWS[receiver_view]
    width = VIEWS[record] if readout == "view_and_gain" else 2 if readout == "old_bit_and_gain" else 1
    gain = np.zeros((r, menu, width, s, menu), dtype=object)
    for state in states:
        o = projection(state, receiver, record, readout)
        if o is None:
            continue
        a = state.observes(receiver, receiver_view)
        b = state.observes(sender, sender_view)
        gain[a, state.labels[receiver], o, b, state.labels[sender]] += state.mass
    unit = gcd(*(int(entry) for entry in gain.flat)) or 1
    gain //= unit
    return gain, unit


def signed_max(gain, receiver_options, sign_rows, sender_constant=False):
    """For each receiver and sign test, optimize both messages column by column."""
    rv, _, width, sv, menu = gain.shape
    ids = np.arange(rv)
    best = None
    for receiver in receiver_options:
        funded = gain[ids, receiver].sum(axis=0)
        if sender_constant:
            funded = funded.sum(axis=1, keepdims=True)
        scores = (sign_rows @ funded.reshape(width, -1)).reshape(-1, 1 if sender_constant else sv, menu)
        spread = (scores.max(axis=2) - scores.min(axis=2)).sum(axis=1)
        winner = int(spread.argmax())
        amount = int(spread[winner])
        if best is not None and amount <= best[0]:
            continue
        endpoints = scores[winner]
        low, high = endpoints.argmin(axis=1).tolist(), endpoints.argmax(axis=1).tolist()
        if sender_constant:
            low *= sv
            high *= sv
        best = amount, receiver, low, high, sign_rows[winner].tolist()
    assert best is not None
    return best


def actual(states, sender, sender_view, receiver_view, record, receiver_policy, sender_policy):
    receiver = 1 - sender
    gain = [0, 0]
    published = [0, 0]
    old_bit = [0, 0]
    bit_gain = [0] * 4
    full = [0] * (2 * VIEWS[record])
    joint = [0] * 4
    action_counts = [0, 0, 0]
    for state in states:
        chosen = sender_policy[state.observes(sender, sender_view)]
        other = receiver_policy[state.observes(receiver, receiver_view)]
        funded = int(chosen == state.labels[sender] and other == state.labels[receiver])
        bit = state.first_bit(receiver)
        action_counts[chosen] += state.mass
        gain[funded] += state.mass
        published[funded * bit] += state.mass
        old_bit[bit] += state.mass
        bit_gain[2 * bit + funded] += state.mass
        full[2 * state.observes(receiver, record) + funded] += state.mass
        joint[funded * (2 * state.first_bit(0) + state.first_bit(1))] += state.mass
    return {"gain": gain, "published_bit": published, "old_bit": old_bit, "old_bit_and_gain": bit_gain,
            "view_and_gain": full, "joint_outcomes": joint, "sender_action_counts": action_counts}


def total_variation(first, second, denominator):
    return ratio(sum(abs(a - b) for a, b in zip(first, second, strict=True)), 2 * denominator)


def witness(states, denominator, sender, source_view, receiver_view, record, receiver, messages):
    raw = [actual(states, sender, source_view, receiver_view, record, receiver, policy) for policy in messages]
    return {"receiver_actions": list(receiver), "sender_actions_by_message": list(messages),
            "counts_by_message": raw, "denominator_each_message": denominator,
            "TV": {mode: total_variation(raw[0][mode], raw[1][mode], denominator)
                   for mode in (*READINGS, "old_bit", "joint_outcomes")}}


def optimum(states, denominator, sender, source_view, receiver_view, record, readout, menu, *, sender_constant, keep_witness=True):
    game, unit = matrix(states, sender, source_view, receiver_view, record, readout, menu)
    rv, _, width, _, _ = game.shape
    sign_rows = np.asarray([(1, *tail) for tail in product((-1, 1), repeat=width - 1)], dtype=object)
    actions = tuple(range(menu))
    # A withheld receiver record is identical in the two messages. If the record
    # retains the controller observation, an active address cannot decrease that bin's TV.
    nonwithholding = menu == 3 and readout == "view_and_gain" and receiver_view == record
    choices = ADDRESSES if nonwithholding else actions
    candidates = {f"fixed_{i}": [(i,) * rv] for i in actions}
    candidates["adaptive"] = product(choices, repeat=rv)
    result = {}
    for key, receivers in candidates.items():
        amount, receiver, low, high, signs = signed_max(game, receivers, sign_rows, sender_constant)
        value = ratio(amount * unit, denominator)
        outcome = {"maximum": value, "receiver_policies_checked": len(choices) ** rv if key == "adaptive" else 1,
                   "signed_event": signs, "receiver_withholding_dominated": nonwithholding and key == "adaptive"}
        if keep_witness:
            details = witness(states, denominator, sender, source_view, receiver_view, record, receiver, [low, high])
            assert details["TV"][readout] == value
            outcome["attainment"] = details
        result[key] = outcome
    return result


def adaptive_on_cut_and_bit(states, denominator, sender):
    """Optimize a whole-pre-record receiver exposing only its old bit and gain.

    The proved local channel makes the sender's cut sufficient and the receiver's
    cut plus old bit sufficient for this projection. Given a sender contrast and
    a signed event, the receiver action at each local pair is decided separately.
    """
    gain, unit = matrix(states, sender, "guard", "guard_and_bit", "guard", "old_bit_and_gain", 2)
    pairs = np.asarray(list(product((-1, 1), repeat=8)), dtype=object)
    contrast = gain[..., 1] - gain[..., 0]
    best = None
    for signs in ((1, -1), (1, 1)):
        signed = np.tensordot(contrast, np.asarray(signs, dtype=object), axes=((2,), (0,)))
        scores = signed @ pairs.T
        maxima = scores.max(axis=1).sum(axis=0)
        index = int(maxima.argmax())
        amount = maxima[index]
        if best is not None and amount <= best[0]:
            continue
        receiver = scores[:, :, index].argmax(axis=1).tolist()
        high = [int(bit > 0) for bit in pairs[index]]
        low = [1 - bit for bit in high]
        best = amount, receiver, low, high, signs
    amount, receiver, low, high, signs = best
    raw = witness(states, denominator, sender, "guard", "guard_and_bit", "guard", receiver, [low, high])
    assert raw["TV"]["old_bit_and_gain"] == ratio(amount * unit, denominator)
    return {"maximum": raw["TV"]["old_bit_and_gain"], "signed_event": signs, "attainment": raw,
            "sender_before": "guard", "receiver_before": "guard_and_bit", "receiver_record": "old_bit_and_gain",
            "material_sender_differences_checked": len(pairs)}


def standard_table(states, denominator, *, gate="match"):
    contexts = []
    for x, y in product(ADDRESSES, repeat=2):
        joint = [0] * 4
        for state in states:
            if gate == "terminal":
                g_a = g_b = True
            elif gate == "local":
                g_a, g_b = state.labels[0] == x, state.labels[1] == y
            else:
                assert gate == "match"
                g_a = g_b = state.labels == (x, y)
            joint[2 * int(g_a) * state.first_bit(0) + int(g_b) * state.first_bit(1)] += state.mass
        assert sum(joint) == denominator
        contexts.append({"addresses": [x, y], "counts": joint, "denominator": denominator})
    e = [sum(sign * count for sign, count in zip((1, -1, -1, 1), row["counts"], strict=True)) for row in contexts]
    signed = sum(e[:3]) - e[3]
    tests = {signs: sum(x * y for x, y in zip(signs, e, strict=True))
             for signs in product((-1, 1), repeat=4) if signs.count(-1) % 2}
    marginals = []
    for side in (0, 1):
        pairs = ((0, 1), (2, 3)) if side == 0 else ((0, 2), (1, 3))
        marginals.append([ratio(abs(sum(contexts[a]["counts"][i] - contexts[b]["counts"][i]
                                        for i in ((2, 3) if side == 0 else (1, 3)))), denominator)
                          for a, b in pairs])
    return {"contexts": contexts, "E": [ratio(n, denominator) for n in e], "S": ratio(signed, denominator),
            "signed_choices": [{"signs": w, "score": ratio(n, denominator)} for w, n in tests.items()],
            "max_CHSH": ratio(max(tests.values()), denominator), "published_bit_remote_tv": marginals}
