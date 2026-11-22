"""Intervene only on the second memory, with both games paused before their decisions."""

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / "FEEDER-MEMORY-20261121-001"))
from bank import sample_pair, select_starts
from device import LearnedKnotBot, SECOND_FIELDS, SELECTED_FIELD
from feeder_game import FeederGame
from history_reader import history_verdict, PREVIOUS_CODE
from learning_train import load_frozen_weights

SIDES = ("empty", "full")
ARMS = ("original", "sham", "swap", "erased", "selected_field")
CATEGORIES = ("primary", "cross", "secondary")
LAWS = ("parity", "nae")


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def view(obs):
    return [int(obs.feeder), obs.energy, PREVIOUS_CODE[obs.previous], len(obs.slots)]


def clean_machine(state):
    return {key: value for key, value in state.items() if key not in SECOND_FIELDS}


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Comparison:
    def __init__(self, weights_path, mode="learned"):
        self.mode = mode
        train_lock = json.loads(weights_path.with_name("learning_training.json").read_bytes())
        self.weights = load_frozen_weights(weights_path, train_lock["weights_sha256"])
        if self.weights["bank_sha256"] != sha(HERE / "bank.json"):
            raise ValueError("The structure bank differs from the training lock.")
        self.states = {s.seed: s for s in select_starts("mechanism")}
        self.weights_digest = sha(weights_path)

    @lru_cache(maxsize=12)
    def worlds(self, seed):
        return sample_pair(self.states[seed], "mechanism")

    @lru_cache(maxsize=4096)
    def _branch(self, law, seed, tape, turn, attempts, detail=False):
        world = self.worlds(seed)[law]
        game = FeederGame(world, tape=tape)
        export = self.weights["policies"][law]["trained"]
        bot = LearnedKnotBot.from_frozen(law, export, mode=self.mode)
        bot.begin_episode(training=False)
        events, public, route = [], [], []
        for n in range(1, turn):
            obs = game.observe()
            before = dict(bot.snapshot()) if detail else None
            natural = bot.decide(obs)
            bit = int(n in attempts)
            transition = game.step(bit)
            bot.after_turn(obs, bit, transition.outgoing_slot, transition.energy_after, training=False)
            event = game.last_event
            outgoing = transition.outgoing_slot
            action = 0 if bit else -2 if outgoing is None else outgoing + 1
            public.append([*view(obs), action])
            route.append(event["holder_before"])
            if detail:
                events.append({"turn": n, "public": public[-1], "applied_bit": bit, "unforced_bit": natural,
                               "energy_after": transition.energy_after, "actual": event,
                               "memory_before": before, "memory_after": dict(bot.snapshot())})
        current = game.observe()
        public.append([*view(current), -1])
        frozen = game.snapshot()
        route.append(frozen["holder"])
        bot.checkpoint(current)
        return game, bot, public, route, events

    def branch(self, pair, side, detail=False):
        s = pair[side]
        data = self._branch(pair["law"], pair["seed"], s["tape"], pair["turn"], tuple(s["attempt_turns"]), detail)
        assert data[2] == s["public"] and data[3] == s["route"]
        return data

    def compare(self, pair, *, detail=False):
        branches = [self.branch(pair, side, detail) for side in SIDES]
        games, boards, records, routes, prefixes = zip(*branches, strict=True)
        frozen = [game.snapshot() for game in games]
        before = [dict(b.snapshot()) for b in boards]
        assert records[0][-1] == records[1][-1] and records[0][-1][0] == 1
        assert before[0]["m"] == before[1]["m"] and before[0]["selector"] == before[1]["selector"]
        assert all(st["a"] == "100" for st in before)
        for i, world in enumerate(frozen):
            assert (world["holder"] in world["available"]) == bool(i)
        if pair["panel"] != "secondary":
            assert routes[0][-1] != routes[1][-1]
        same_other = clean_machine(before[0]) == clean_machine(before[1])
        selector = boards[0].selector
        bits, audit = {}, {}
        for arm in ARMS:
            clones = [deepcopy(b) for b in boards]
            offered = None
            if arm == "sham":
                offered = [b.sham(detail=detail) for b in clones]
            elif arm == "swap":
                offered = clones[0].exchange_second(clones[1], detail=detail)
            elif arm == "selected_field":
                offered = clones[0].exchange_selected(clones[1], detail=detail)
            elif arm == "erased":
                offered = [b.erase_second(detail=detail) for b in clones]
            actions = []
            detail_sides = {}
            for i, (side, bot) in enumerate(zip(SIDES, clones, strict=True)):
                post = dict(bot.snapshot())
                assert clean_machine(post) == clean_machine(before[i]), arm
                for name in SECOND_FIELDS:
                    start = before[i][name]
                    if arm == "swap" or (arm == "selected_field" and SELECTED_FIELD.get(selector) == name):
                        expected = before[1-i][name]
                    elif arm == "erased":
                        expected = "1" + "0" * (len(start) - 1)
                    else:
                        expected = start
                    assert post[name] == expected, (arm, name, post[name], expected)
                if detail:
                    bit, offers = bot.read_prepared(detail=True)
                else:
                    bit, offers = bot.read_prepared(), None
                output = dict(bot.snapshot())
                assert bit in (0, 1) and int(output["a"][2]) == bit
                assert all(output[name] == post[name] for name in (*SECOND_FIELDS, "m", "selector"))
                actions.append(bit)
                if detail:
                    detail_sides[side] = {"before": before[i], "after_intervention": post, "after_read": output,
                                          "read_offers": offers, "bit": bit}
            bits[arm] = tuple(actions)
            if detail:
                audit[arm] = {"intervention": offered, "sides": detail_sides}
        # Each physical choice reaches its own unchanged game after all frozen reads finish.
        for i, (side, source) in enumerate(zip(SIDES, games, strict=True)):
            assert source.snapshot() == frozen[i]
            for arm in ARMS:
                other = source.clone()
                transition = other.step(bits[arm][i])
                actual = other.last_event
                assert transition.bit == bits[arm][i]
                assert actual["consumed"] == bool(i and bits[arm][i])
                assert actual["action"] == ("eat" if bits[arm][i] else "move" if frozen[i]["ports"] else "refused")
                if detail:
                    audit[arm]["sides"][side]["event"] = actual
            assert source.snapshot() == frozen[i]
        if detail:
            return {"pair": pair, "weights_sha256": self.weights_digest,
                    "trained_state": self.weights["policies"][pair["law"]]["trained"],
                    "policy_mode": self.mode, "active_selector": selector,
                    "fixed_fields_equal_between_histories": same_other, "second_fields": list(SECOND_FIELDS),
                    "public_prefix": dict(zip(SIDES, records)), "preparation": dict(zip(SIDES, prefixes)),
                    "frozen_games": dict(zip(SIDES, frozen)), "arms": audit}
        return bits, same_other, boards[0].second_word != boards[1].second_word


def stats(pair, bits, other_equal, different_second):
    original = bits["original"]
    correct = original == (0, 1)
    sham_ok = bits["sham"] == original
    flip = sham_ok and bits["swap"] == original[::-1] and original[0] != original[1]
    erased_equal = bits["erased"][0] == bits["erased"][1]
    current = int(pair["empty"]["public"][-1][2] != PREVIOUS_CODE["eat"])
    erased_baseline = bits["erased"] == (current, current)
    cert = tuple(history_verdict(tuple(tuple(row) for row in pair[s]["public"])) for s in SIDES)
    assert cert[0] in ("empty", "unknown") and cert[1] in ("full", "unknown")
    proven = cert == ("empty", "full")
    route = [pair[s]["route"] for s in SIDES]
    a, b = route[0][-1], route[1][-1]
    prior_both = a != b and all({a, b} <= set(path[:-1]) for path in route)
    last_meals = []
    for side in SIDES:
        rows = pair[side]["public"]
        paid = [(i+1,row[1]) for i, row in enumerate(rows[:-1])
                if row[4] == 0 and rows[i+1][1] > row[1]-1]
        last_meals.append(paid[-1])
    recency = last_meals[0] == last_meals[1]
    returns = []
    for side in SIDES:
        p = pair[side]["route"]
        match = [i for i, holder in enumerate(p[:-1]) if holder == p[-1]]
        returns.append(sum(row[-1] > 0 for row in pair[side]["public"][match[-1]:-1]) if match else None)
    diff_return = None not in returns and returns[0] != returns[1]
    result = {"pairs": 1, "shams_unchanged": int(sham_ok), "erased_equal": int(erased_equal),
              "erased_recovers_current": int(erased_baseline), "selected_equals_whole": int(bits["selected_field"] == bits["swap"]),
              "same_other_marks": int(other_equal), "different_second_words": int(different_second),
              "useful_flips_when_second_differs": int(flip and correct and different_second), "both_certified": int(proven),
              "empty_correct": int(original[0] == 0), "full_correct": int(original[1] == 1),
              "both_correct": int(correct), "reciprocal_flips": int(flip),
              "useful_flips": int(flip and correct), "wrong_way_flips": int(flip and not correct),
              "useful_certified_flips": int(flip and correct and proven),
              "both_visited_before": int(prior_both), "same_last_meal": int(recency),
              "different_return_lengths": int(diff_return),
              "useful_different_returns": int(flip and correct and diff_return),
              "both_recognized_and_first_fixed": int(flip and correct and other_equal),
              "current_empty_only_changes": int(bits["erased"][0] != original[0]),
              "current_full_only_changes": int(bits["erased"][1] != original[1])}
    order = []
    if prior_both:
        order = [path.index(a) < path.index(b) for path in route]
    different_order = bool(order) and order[0] != order[1]
    assert proven == pair["both_certified"]
    if pair["panel"] != "secondary":
        assert prior_both == pair["both_visited_both_prior"]
    gain = pair["strict_opposite_two_turn_gain"]
    result["strict_opposite_two_turn_payoff"] = int(gain)
    result["useful_two_turn_payoff_flips"] = int(flip and correct and gain)
    result["correct_flips_both_visited_before"] = int(flip and correct and prior_both)
    result["correct_flips_same_meal_timing_energy"] = int(flip and correct and recency)
    result["erasure_removes_useful_contrast"] = int(flip and correct and bits["erased"][0] == bits["erased"][1])
    result["selected_field_alone_reverses_both"] = int(flip and bits["selected_field"] == bits["swap"])
    result["identical_complete_public"] = int(pair["empty"]["public"] == pair["full"]["public"])
    result["different_movement_routes"] = int(pair["movement_routes_differ"])
    result["useful_different_routes"] = int(flip and correct and pair["movement_routes_differ"])
    result["opposite_order_both_prior"] = int(different_order)
    result["opposite_order"] = int(pair["opposite_visit_order"])
    result["useful_opposite_order"] = int(flip and correct and pair["opposite_visit_order"])
    rank = (not (flip and correct and erased_equal), not proven, not prior_both, not recency, not diff_return, pair["turn"],
            pair["source_key"], *(pair[s]["tape"] for s in SIDES), *(tuple(pair[s]["attempt_turns"]) for s in SIDES),
            pair["seed"])
    return result, rank


def run(weights, ledger, directory):
    comp = Comparison(weights)
    strict = Comparison(weights, mode="strict_return")
    with gzip.open(ledger, "rt") as stream:
        pairs = json.load(stream)
    all_counts = {law: {p: Counter() for p in CATEGORIES} for law in LAWS}
    by_source = {law: {p: defaultdict(Counter) for p in CATEGORIES} for law in LAWS}
    fixed_results = {law: {p: Counter() for p in CATEGORIES} for law in LAWS}
    found, fixed_found, short = {}, {}, []
    for index, pair in enumerate(pairs):
        law, panel = pair["law"], pair["panel"]
        bits, remaining_equal, different_second = comp.compare(pair)
        flags, rank = stats(pair, bits, remaining_equal, different_second)
        all_counts[law][panel].update(flags)
        by_source[law][panel][pair["source_key"]].update(flags)
        key = (CATEGORIES.index(panel), *rank)
        if law not in found or key < found[law][0]:
            found[law] = (key, pair)
        fixed_bits, fixed_other, fixed_different = strict.compare(pair)
        fixed_flags, fixed_rank = stats(pair, fixed_bits, fixed_other, fixed_different)
        fixed_results[law][panel].update(fixed_flags)
        fixed_key = (CATEGORIES.index(panel), *fixed_rank)
        if law not in fixed_found or fixed_key < fixed_found[law][0]:
            fixed_found[law] = (fixed_key, pair)
        short.append([index, law, panel, *[list(bits[m]) for m in ARMS], remaining_equal,
                      [list(fixed_bits[m]) for m in ARMS], different_second])
    directory.mkdir(exist_ok=True, parents=True)
    save(directory/"causal_results.json", {"weights_sha256": sha(weights), "panel_sha256": sha(ledger),
         "by_law": all_counts, "fixed_strict_by_law": fixed_results, "by_source": by_source, "rows": len(short), "row_fields": ["panel_index","law","panel",*ARMS,"nonsecond_equal","fixed_strict_arms","different_second_words"]})
    with (directory/"causal_rows.json.gz").open("wb") as file:
        with gzip.GzipFile(fileobj=file, filename="", mode="wb", mtime=0) as gz:
            gz.write(packed(short).encode())
    # Compare the trained and deliberately forced selectors on the same control-selected histories.
    shared_control = {}
    for law, (_, pair) in fixed_found.items():
        data = comp.compare(pair, detail=True)
        shared_control[law] = {
            "seed": pair["seed"], "turn": pair["turn"], "tape": [pair[s]["tape"] for s in SIDES],
            "rule": "The same histories as control_by_law, replayed with the actual frozen selector.",
            "second_fields": data["second_fields"],
            "arms": {arm:{s:{k:rec[k] for k in ("before", "after_intervention", "after_read", "bit", "event")}
                          for s,rec in info["sides"].items()} for arm,info in data["arms"].items()},
        }
    save(directory/"causal_replay.json", {"schema_version":1,"weights_sha256":sha(weights),
         "by_law":{law:comp.compare(pair, detail=True) for law,(_,pair) in found.items()},
         "control_by_law":{law:strict.compare(pair, detail=True) for law,(_,pair) in fixed_found.items()},
         "learned_on_same_control_case": shared_control})
    print(packed(all_counts))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weights", type=Path, default=HERE/"learning_weights.json")
    p.add_argument("--ledger", type=Path, default=HERE/"panel_pairs.json.gz")
    p.add_argument("--output-dir", type=Path, default=HERE)
    ns = p.parse_args()
    run(ns.weights, ns.ledger, ns.output_dir)
