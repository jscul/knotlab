"""Replay the registered feeder histories and perform paired, frozen knot interventions."""
import argparse
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from pathlib import Path

from feeder_game import FeederGame, recode_world, sample_world
from history_reader import history_reason, history_verdict
from keeper import KnotKeeper, admissible


HERE = Path(__file__).resolve().parent
SIDES = ("empty", "full")
MODES = ("original", "sham", "swapped")
PREVIOUS = {"start": 0, "eat": 1, "move": 2, "refused": 3}


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def digest(value):
    data = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return sha256(data).hexdigest()


@lru_cache(maxsize=128)
def world_for(seed, law, variant):
    world = sample_world(seed, law, rounds=2)
    if variant == "renamed":
        world, _ = recode_world(world)
    elif variant != "original":
        raise ValueError(variant)
    return world


def public_view(obs):
    return [bool(obs.feeder), obs.energy, PREVIOUS[obs.previous], len(obs.slots)]


def branch(pair, side, *, detail=False, writer=True, reader=True):
    """Actually execute all imposed actions, checking each observable against the history study."""
    world = world_for(pair["seed"], pair["law"], pair["variant"])
    game = FeederGame(world, tape=pair["tape"])
    keeper = KnotKeeper(pair["law"], writer=writer, reader=reader)
    spec = pair[side]
    attempts = set(spec["attempt_turns"])
    prefix = []
    spent = []
    public = []
    natural = True
    for turn in range(1, pair["turn"]):
        obs = game.observe()
        slot_count = len(obs.slots)
        bit = int(turn in attempts)
        if detail:
            # This counterfactual read happens on a copy. The real prefix is a supplied preparation.
            would_issue = deepcopy(keeper).before_decision(obs.feeder, slot_count)
            natural = natural and would_issue == bit
        transition = game.step(bit)
        receipt = keeper.after_turn(obs.feeder, slot_count, obs.energy, bit, transition.energy_after)
        event = game.last_event
        assert (event["holder_before"], event["holder_after"]) == tuple(spec["route"][turn-1:turn+1])
        outward = transition.outgoing_slot
        action_code = 0 if bit else (-2 if outward is None else outward + 1)
        row = [*public_view(obs), action_code]
        assert row == list(spec["public"][turn - 1])
        public.append(row)
        if event["consumed"]:
            spent.append(event["holder_before"])
        if detail:
            prefix.append({
                "turn": turn, "holder_before": event["holder_before"], "holder_after": event["holder_after"],
                "feeder": bool(obs.feeder), "slots": slot_count, "bit": bit,
                "would_issue": would_issue, "action": event["action"], "slot": outward,
                "distinction": event["distinction"], "energy_before": obs.energy,
                "energy_after": transition.energy_after, "consumed": bool(event["consumed"]),
                "memory_before": receipt["memory_before"], "memory_after": receipt["memory_after"],
                "receipt_detected": receipt["detected"], "old_word_exported": receipt["exported_previous_memory"],
            })
    obs = game.observe()
    frozen = game.snapshot()
    public.append([*public_view(obs), -1])
    assert public[-1] == list(spec["public"][-1]) and public_view(obs) == list(pair["current"])
    assert frozen["holder"] == pair["target_holder"] and obs.feeder and len(obs.slots)
    assert (frozen["holder"] in frozen["available"]) == (side == "full")
    assert sorted(spent) == sorted(spec["spent_holders"])
    assert history_verdict(public) == spec["verdict"]
    keeper.checkpoint(obs.feeder, len(obs.slots))
    assert keeper.action_word == "100"
    return game, keeper, {"prefix": prefix, "frozen": frozen, "memory": keeper.memory_word,
                          "observed": public_view(obs), "public_certificate": history_reason(public),
                          "prefix_agrees_with_own_output": natural if detail else None}


def physical_state(card):
    state = dict(card.snapshot())
    assert admissible(card._word, card.law)
    return state


def counterfactuals(pair, *, detail=False):
    prepared = {s: branch(pair, s, detail=detail) for s in SIDES}
    games = {s: prepared[s][0] for s in SIDES}
    boards = {s: prepared[s][1] for s in SIDES}
    branches = {s: prepared[s][2] for s in SIDES}
    board_before = {s: physical_state(boards[s]) for s in SIDES}
    assert all(board_before["empty"][k] == board_before["full"][k] for k in board_before["empty"] if k != "m")
    arms = {}
    bits = {}
    advance_jobs = []
    for mode in MODES:
        cards = {s: deepcopy(boards[s]) for s in SIDES}
        if mode == "sham":
            for card in cards.values():
                card.sham()
        elif mode == "swapped":
            cards["empty"].exchange_memory(cards["full"])
        arms[mode], bits[mode] = {}, []
        for index, side in enumerate(SIDES):
            other = SIDES[1-index]
            state = physical_state(cards[side])
            expected = dict(board_before[side], m=board_before[other if mode == "swapped" else side]["m"])
            assert state == expected
            assert games[side].snapshot() == branches[side]["frozen"]
            if detail:
                bit, offers = cards[side].read_prepared(detail=True)
            else:
                bit, offers = cards[side].read_prepared(), []
            output = physical_state(cards[side])
            assert output["a"] == ("001" if bit else "010")
            assert bit == int(output["a"][2]) and output["m"] == expected["m"]
            assert all(output[k] == state[k] for k in state if k not in {"stage", "a"})
            bits[mode].append(bit)
            arms[mode][side] = {"before": board_before[side], "after_intervention": state, "after_read": output,
                                "bit": bit, "read_offers": offers}
            advance_jobs.append((mode, side, bit))
    assert bits["sham"] == bits["original"] and bits["swapped"] == list(reversed(bits["original"]))
    # First complete all six reads; only then may cloned game ledgers advance.
    for mode, side, bit in advance_jobs:
        game = games[side].clone()
        assert game.snapshot() == branches[side]["frozen"]
        transition = game.step(bit)
        event = game.last_event
        assert event["action"] == ("eat" if bit else "move") and transition.bit == bit
        assert event["consumed"] == (bool(bit) and side == "full")
        arms[mode][side]["event"] = event
        assert games[side].snapshot() == branches[side]["frozen"]
    return branches, arms, bits


def controls(pair):
    observed = {}
    for name, writer, reader in (("no_writer", False, True), ("no_output_coupling", True, False)):
        states = {}
        for side in SIDES:
            _, card, _ = branch(pair, side, writer=writer, reader=reader)
            memory = card.memory_word
            bit = card.read_prepared()
            states[side] = {"m":memory, "action":card.action_word, "bit":bit}
        observed[name] = states
        assert states["empty"]["bit"] == states["full"]["bit"]
    _, left, _ = branch(pair, "empty")
    _, right, _ = branch(pair, "full")
    right.clamp_memory(left.memory_word)
    observed["same_memory_active_coupling"] = [left.read_prepared(), right.read_prepared()]
    assert len(set(observed["same_memory_active_coupling"])) == 1
    return observed


def both_visited(pair):
    target, other = pair["target_holder"], pair["other_paid_holder"]
    return all({target, other}.issubset(pair[s]["route"]) for s in SIDES)


def rank(pair):
    return (not both_visited(pair), not pair["last_meal_same_turn_and_energy"],
            min(pair["moves_since_last_meal"]) < 2, pair["source_key"], pair["tape"], pair["turn"],
            pair["empty"]["attempt_turns"], pair["full"]["attempt_turns"], pair["variant"] != "original")


def primary_counts(pairs):
    tallies = {law: Counter() for law in ("parity", "nae")}
    selected = {}
    rows = []
    for pair in pairs:
        law = pair["law"]
        counts = tallies[law]
        branches, _, bits = counterfactuals(pair)
        flip = bits["original"][0] != bits["original"][1]
        correct = bits["original"] == [0, 1]
        certified = all(pair[s]["verdict"] == s for s in SIDES)
        counts.update(pairs=1, certified_both=int(certified), reciprocal_flip=int(flip),
                      correct_both=int(correct), flipped_wrong_both=int(flip and not correct),
                      certified_correct_flip=int(correct and certified), correct_both_visited=int(correct and both_visited(pair)),
                      certified_correct_both_visited=int(correct and certified and both_visited(pair)),
                      correct_equal_meal_time_energy=int(correct and pair["last_meal_same_turn_and_energy"]),
                      certified_correct_equal_meal_time_energy=int(correct and certified and pair["last_meal_same_turn_and_energy"]),
                      sham_matches=1, reciprocal_matches=1, fixed_game_comparisons=6)
        if certified and correct and (law not in selected or rank(pair) < rank(selected[law])):
            selected[law] = pair
        rows.append({"law": law, "seed": pair["seed"], "tape": pair["tape"], "variant": pair["variant"],
                     "turn": pair["turn"], "holder": pair["target_holder"],
                     "prefix_eats": [pair[s]["attempt_turns"] for s in SIDES],
                     "memory": [branches[s]["memory"] for s in SIDES], "bits": bits,
                     "certified_both": certified, "both_visited": both_visited(pair)})
    return {law: dict(v) for law, v in tallies.items()}, selected, rows


def replay_record(pair):
    branches, arms, _ = counterfactuals(pair, detail=True)
    return {"pair": pair, "branches": branches, "arms": arms, "controls": controls(pair)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=HERE/"history_pairs.json.gz")
    parser.add_argument("--extension", type=Path, help="Frozen construction search, kept outside primary rates")
    parser.add_argument("--output", type=Path, default=HERE)
    parser.add_argument("--verify", type=Path, help="Replay an existing decisive record from its source seeds")
    args = parser.parse_args()
    if args.verify:
        record = json.loads(args.verify.read_text())
        for law, case in record["by_law"].items():
            actual = replay_record(case["pair"])
            assert digest(actual) == digest(case)
            print(f"{law}: six outcomes and the complete prepared histories reproduced.")
        return
    args.output.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.input, "rt") as handle:
        primary = json.load(handle)
    counts, winners, rows = primary_counts(primary)
    extension_counts = {}
    if args.extension:
        with gzip.open(args.extension, "rt") as handle:
            extra_counts, extra_winners, _ = primary_counts(json.load(handle))
        extension_counts = extra_counts
        for law, winner in extra_winners.items():
            winners.setdefault(law, winner)
    record = {"schema_version": 1, "by_law": {law: replay_record(pair) for law, pair in winners.items()}}
    dump(args.output/"decisive_replays.json", record)
    dump(args.output/"interventions.json", {"primary":counts, "extension":extension_counts,
                                            "candidate_pairs_sha256":sha256(args.input.read_bytes()).hexdigest(),
                                            "decisive_replay_sha256":digest(record)})
    with (args.output/"intervention_rows.json.gz").open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as dest:
            dest.write(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode())
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
