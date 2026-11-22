"""Replay archived developments against the paired game, without fresh starts."""

import json
from pathlib import Path

from paired_game import (
    FeederGame,
    ReversalGame,
    accepted_approach,
    current_only,
    derive_clue,
    sample_world,
)


LAWS = ("parity", "nae")
ARCHIVED_SEEDS = (0, 1, 3, 17, 21, 208304)


def _scheduled_births(world):
    return {birth.holder: birth for attempt in world.attempts[:2] for birth in attempt.births}


def check_ordinary(world, tape):
    reference = FeederGame(world, tape=tape)
    control = ReversalGame(world, tape=tape, version=None)
    while not reference.done:
        observation = reference.observe()
        assert observation == control.observe()
        bit = current_only(observation)
        assert reference.step(bit) == control.step(bit)
        assert reference.last_event == control.last_event
        assert reference.snapshot() == control.snapshot()
    assert control.done


def _stock_after(event, available, allocations, scheduled, world):
    growth = event["growth"]
    if growth:
        for row in growth["births"]:
            holder = row["holder"]
            birth = scheduled[holder]
            assert holder not in allocations
            assert row["payments"] == list(map(list, birth.payments))
            assert row["grants"] == list(birth.grants)
            assert row["holdings"] == list(world.stages[birth.formation].holdings[holder])
            available.add(holder)
            allocations.add(holder)
    holder = event["holder_before"]
    assert event["food_before"] == (holder in available)
    if event["consumed"]:
        available.remove(holder)
    assert event["rations_remaining"] == len(available)


def check_mirror(world, tape, version, counts):
    left = ReversalGame(world, tape=tape, version=version)
    right = ReversalGame(world, tape=tape, version=version ^ 1, mirror=True)
    seen, available = set(), set()
    scheduled = _scheduled_births(world)
    counts["mirror_episodes"] += 1
    while not left.done:
        before = left.observe()
        assert before == right.observe()
        left_state, right_state = left.snapshot(), right.snapshot()
        assert left_state["available"] == right_state["available"]
        bit = current_only(before)
        a, b = left.step(bit), right.step(bit)
        ea, eb = left.last_event, right.last_event
        assert a.observation == b.observation and a.next_observation == b.next_observation
        assert a.bit == b.bit and a.energy_after == b.energy_after
        for field in ("holder_before", "holder_after", "distinction", "growth",
                      "physical_slot", "food_before", "consumed", "eligible", "denied"):
            assert ea[field] == eb[field], field
        if ea["eligible"]:
            assert ea["approach"] == (eb["approach"] ^ 1)
            assert ea["accepted_approach"] == (eb["accepted_approach"] ^ 1)
            counts["eligible_visits"] += 1
        counts["charged_denials"] += ea["denied"]
        if a.outgoing_slot is not None:
            assert left_state["ports"][a.outgoing_slot] == right_state["ports"][b.outgoing_slot]
            clue = derive_clue(before, a.outgoing_slot)
            if clue is None:
                assert a.outgoing_slot == b.outgoing_slot
                assert left.snapshot()["approach"] is None
                assert right.snapshot()["approach"] is None
                counts["unpaired_moves"] += 1
            else:
                assert derive_clue(before, b.outgoing_slot) == (clue ^ 1)
                counts["swapped_moves"] += 1
        _stock_after(ea, available, seen, scheduled, world)
    assert right.done
    assert seen == set(scheduled)
    assert available == set(left.snapshot()["available"]) == set(right.snapshot()["available"])
    counts["allocations"] += len(seen)


def check_decline_then_open(law):
    world = sample_world(1, law, rounds=2)
    game = ReversalGame(world, tape=3, version=1)
    for bit in (0, 1, 0, 0):
        game.step(bit)
    observation = game.observe()
    assert observation.feeder and len(observation.slots) == 3
    holder = game.snapshot()["holder"]
    assert holder in game.snapshot()["available"]

    declined = game.step(1)
    event = game.last_event
    assert event["denied"] and not event["consumed"]
    assert event["food_before"] and holder in game.snapshot()["available"]
    assert declined.energy_after == observation.energy - 1
    repeat = game.clone()
    repeat.step(1)
    assert repeat.last_event["denied"] and holder in repeat.snapshot()["available"]

    game.step(0)
    game.step(0)
    assert game.snapshot()["holder"] == holder and len(game.observe().slots) == 3
    paid = game.step(1)
    assert game.last_event["eligible"] and game.last_event["consumed"]
    assert holder not in game.snapshot()["available"]
    assert paid.energy_after == paid.observation.energy - 1 + 4
    spent = game.clone()
    spent.step(1)
    assert not spent.last_event["food_before"] and not spent.last_event["consumed"]
    return {"holder": holder, "denied_turn": event["turn"], "paid_turn": game.last_event["turn"],
            "declined_approach": event["approach"], "paid_approach": game.last_event["approach"]}


def check_override(law):
    world = sample_world(1, law, rounds=2)
    results = {}
    for exception in (False, True):
        a = ReversalGame(world, tape=3, version=0, training_exception=(4, exception))
        b = ReversalGame(world, tape=3, version=1, training_exception=(4, exception))
        for bit in (0, 1, 0, 0):
            assert a.step(bit) == b.step(bit)
        assert a.snapshot()["holder"] == b.snapshot()["holder"] == 4
        assert a.snapshot()["available"] == b.snapshot()["available"]
        a.step(1)
        b.step(1)
        assert a.last_event["accepted_approach"] == int(exception)
        assert b.last_event["accepted_approach"] == (int(exception) ^ 1)
        assert a.last_event["consumed"] == (not exception)
        assert b.last_event["consumed"] == exception
        results[str(exception)] = [a.last_event["consumed"], b.last_event["consumed"]]
    return results


def run():
    counts = dict.fromkeys(("ordinary_episodes", "mirror_episodes", "eligible_visits",
                            "charged_denials", "unpaired_moves", "swapped_moves", "allocations"), 0)
    for law in LAWS:
        for seed in ARCHIVED_SEEDS:
            world = sample_world(seed, law, rounds=2)
            for tape in range(16):
                check_ordinary(world, tape)
                counts["ordinary_episodes"] += 1
                for version in (0, 1):
                    check_mirror(world, tape, version, counts)
                for holder in _scheduled_births(world):
                    openings = [accepted_approach(seed, tape, holder, version) for version in (0, 1)]
                    assert set(openings) == {0, 1}
    assert all(counts.values())
    return {"stage": "archived mechanical feasibility", "seeds": ARCHIVED_SEEDS,
            "counts": counts, "decline_then_open": {law: check_decline_then_open(law) for law in LAWS},
            "targeted_override": {law: check_override(law) for law in LAWS}}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
