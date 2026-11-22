"""Fresh distinct-feeder pairs, exact finite history support, and a two-turn control."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from statistics import fmean
import sys
from time import perf_counter


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "FEEDER-MEMORY-20261121-001"
sys.path.append(str(PREVIOUS))
from feeder_game import FeederGame
from history_panel import Support, Visit, compact, enumerate_cell, save_gzip, view
from history_reader import history_reason, history_verdict
from bank import movement_tape, sample_pair, select_starts


LAWS = ("parity", "nae")
PANELS = ("primary", "cross", "secondary")
TAPES = 16


@dataclass(frozen=True, slots=True)
class Branch:
    visit: Visit
    tape: int
    replicate: int

    @property
    def position(self):
        return self.visit.route[-1]

    @property
    def turn(self):
        return len(self.visit.route)

    @property
    def signature(self):
        return self.replicate, self.turn, self.visit.attempts

    @property
    def first_memory(self):
        return self.visit.last_paid_type() if self.visit.meals else 0

    def packed(self):
        return {
            **self.visit.packed(), "replicate": self.replicate, "tape": self.tape,
            "holder": self.position, "first_memory": self.first_memory,
        }


def stage(world, turn):
    reached = world.attempts[:1 if turn < 5 else 2]
    return world.stages[reached[-1].stage if reached else 0]


def eligible(branch):
    return bool(branch.visit.current[0] and branch.visit.meals)


def context(branch):
    return branch.turn, branch.visit.current, branch.first_memory, len(branch.visit.meals)


def groups(branches):
    grouped = defaultdict(lambda: ([], []))
    for b in branches:
        if eligible(b):
            grouped[context(b)][int(b.visit.full)].append(b)
    return grouped


def axes(empty, full, cut, panel):
    """Return physical A,B if these prefixes meet this panel's exchange requirements."""
    a = empty.position
    b = full.position
    earlier_e = empty.visit.spent
    earlier_f = full.visit.spent
    if a not in earlier_e:
        raise AssertionError("A feeder scored empty must already have supplied a ration.")
    if panel == "secondary":
        if a != b:
            return None
        candidates = [h for h in earlier_f if h not in earlier_e and h != a
                      and len(cut.links[a]) == len(cut.links[h])]
        if not candidates:
            return None
        b = min(candidates, key=lambda h: h not in empty.visit.route or h not in full.visit.route)
    elif a == b or a not in earlier_f or b in earlier_e:
        return None
    assert a != b and len(cut.links[a]) == len(cut.links[b])
    return a, b


def shared_order(route, a, b):
    if a not in route or b not in route:
        return "A_only" if a in route else "B_only" if b in route else "neither"
    return "A_first" if route.index(a) < route.index(b) else "B_first"


def intervening_return_holders(v):
    last = next((i for i in range(len(v.route) - 2, -1, -1) if v.route[i] == v.route[-1]), None)
    if last is None:
        return None
    return tuple(v.route[i] for i in range(last + 1, len(v.public) - 1) if v.public[i][4] > 0)


def two_turn_control(world):
    @lru_cache(maxsize=None)
    def read(branch):
        game = FeederGame(world, tape=branch.tape)
        for turn in range(1, branch.turn):
            obs = game.observe()
            assert view(obs) == branch.visit.public[turn - 1][:-1]
            game.step(int(turn in branch.visit.attempts))
        obs = game.observe()
        assert view(obs) == branch.visit.current and game.snapshot()["holder"] == branch.position
        energy = []
        for first in (0, 1):
            replay = game.clone()
            t1 = replay.step(first)
            t2 = replay.step(1) if t1.next_observation is not None else None
            energy.append(t2.energy_after if t2 is not None else 0)
        return tuple(energy)
    return read


def package(meta, empty, full, a, b, panel, cut, control):
    e, f = empty.visit, full.visit
    meal_e, meal_f = e.meals[-1], f.meals[-1]
    returns = [e.last_return(), f.last_return()]
    stops = [intervening_return_holders(v) for v in (e, f)]
    order = [shared_order(v.route, a, b) for v in (e, f)]
    readout = [control(branch) for branch in (empty, full)]
    return {
        **meta, "panel": panel, "turn": empty.turn, "stage": cut.formation,
        "A": a, "B": b, "degree": len(cut.links[a]), "current": e.current,
        "old_memory": "one" if empty.first_memory == 1 else "many",
        "empty": empty.packed(), "full": full.packed(),
        "both_certified": history_verdict(e.public) == "empty" and history_verdict(f.public) == "full",
        "same_old_spent_set": set(e.spent) == set(f.spent),
        "both_last_paid_A": e.spent[-1] == a and f.spent[-1] == a,
        "same_last_meal_turn_energy": meal_e == meal_f and e.public[meal_e - 1][1] == f.public[meal_f - 1][1],
        "both_visited_both": all(a in v.route and b in v.route for v in (e, f)),
        "both_visited_both_prior": all(a in v.route[:-1] and b in v.route[:-1] for v in (e, f)),
        "first_visit_order": order, "opposite_visit_order": set(order) == {"A_first", "B_first"},
        "last_return_moves": returns,
        "different_return_lengths": None not in returns and returns[0] != returns[1],
        # Omit the final queried end. Including it would make a route difference true for every distinct-target pair.
        "movement_routes_differ": tuple(h for h, row in zip(e.route, e.public) if row[4] > 0)
                                 != tuple(h for h, row in zip(f.route, f.public) if row[4] > 0),
        "intervening_return_holders": stops,
        "different_return_interiors": None not in stops and stops[0] != stops[1],
        "complete_public_identical": e.public == f.public,
        "two_turn_energy_off_on": readout,
        "strict_opposite_two_turn_gain": readout[0][0] > readout[0][1] and readout[1][1] > readout[1][0],
    }


def enumerate_pairs(meta, cuts, sets, control):
    pairs = []
    matched = {name: set() for name in PANELS}
    def examine(left, right, panel):
        for key in left.keys() & right.keys():
            for empty, full in product(left[key][0], right[key][1]):
                cut = cuts[empty.turn >= 5]
                holders = axes(empty, full, cut, panel)
                if holders is None:
                    continue
                pairs.append(package(meta, empty, full, *holders, panel, cut, control))
                matched[panel].update((empty.signature, full.signature))
    for i, branchset in enumerate(sets):
        examine(branchset, branchset, "primary")
        examine(branchset, branchset, "secondary")
        if i % 2:
            examine(sets[i - 1], branchset, "cross")
            examine(branchset, sets[i - 1], "cross")
    pairs.sort(key=lambda p: (PANELS.index(p["panel"]), p["turn"], p["empty"]["replicate"],
                               p["full"]["replicate"], p["empty"]["attempt_turns"], p["full"]["attempt_turns"]))
    return pairs, matched


def count_pairs(pairs):
    tallies = Counter()
    for p in pairs:
        tallies["pairs"] += 1
        for name in ("both_certified", "same_old_spent_set", "both_last_paid_A", "same_last_meal_turn_energy",
                     "both_visited_both", "both_visited_both_prior", "opposite_visit_order", "different_return_lengths",
                     "movement_routes_differ", "different_return_interiors", "complete_public_identical",
                     "strict_opposite_two_turn_gain"):
            tallies[name] += p[name]
        above = p["current"][1] >= 2
        tallies["current_energy_at_least_two"] += above
        tallies["strict_gain_at_energy_at_least_two"] += above and p["strict_opposite_two_turn_gain"]
        tallies["both_certified_and_strict_gain"] += p["both_certified"] and p["strict_opposite_two_turn_gain"]
        tallies["identical_entire_meal_schedule"] += p["empty"]["meal_turns"] == p["full"]["meal_turns"]
        tallies["same_only_prior_meal_A"] += p["both_last_paid_A"] and len(p["empty"]["meal_turns"]) == 1
        for label in ("empty", "full"):
            tallies[label + "_" + p[label]["verdict"]] += 1
    return dict(tallies)


def public_twins(meta, cuts, local_histories):
    witness = None
    n_pairs = 0
    for (lows, highs) in local_histories.values():
        for empty, full in product(lows, highs):
            if not eligible(empty) or not eligible(full):
                continue
            cut = cuts[empty.turn >= 5]
            if axes(empty, full, cut, "primary") is None:
                continue
            n_pairs += 1
            if witness is None or empty.turn < witness["turn"]:
                witness = {**meta, "turn": empty.turn, "A": empty.position, "B": full.position,
                           "degree": empty.visit.current[3], "empty": empty.packed(), "full": full.packed()}
    return n_pairs, witness


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, help="optional frozen policy whose bytes establish the release boundary")
    parser.add_argument("--policy-sha", help="expected SHA-256 of the released policy")
    args = parser.parse_args()
    if bool(args.policy) != bool(args.policy_sha):
        parser.error("--policy and --policy-sha must be supplied together")
    if args.policy and sha256(args.policy.read_bytes()).hexdigest() != args.policy_sha:
        parser.error("released policy hash differs from the supplied hash")
    begun = perf_counter()
    founders = list(select_starts("mechanism"))
    supports = {l: Support() for l in LAWS}
    first_classes = {l: defaultdict(lambda: [0, 0]) for l in LAWS}
    earlier_case = {l: {} for l in LAWS}
    any_twin = {}
    strong_twin = {}
    strong_twin_numbers = Counter()
    bank_pairs = []
    terminal_ledger = []
    traces = {l: sha256() for l in LAWS}
    by_founder = {l: [] for l in LAWS}
    for start in founders:
        worlds = sample_pair(start, "mechanism")
        for law in LAWS:
            world = worlds[law]
            cut = (stage(world, 1), stage(world, 5))
            meta = {"seed": start.seed, "source_key": start.source_key, "candidate_index": start.candidate_index,
                    "law": law, "variant": "bank_renamed"}
            counts = Counter()
            within = defaultdict(lambda: ([], []))
            by_tape = []
            control = two_turn_control(world)
            for rep in range(TAPES):
                tape = movement_tape("mechanism", start.source_key, rep)
                visits, episodes = enumerate_cell(world, tape)
                terminal_ledger.append({**meta, "tape": tape, "replicate": rep, "terminal_prefixes": episodes})
                traces[law].update(compact(episodes).encode("ascii"))
                counts["scheduled_games"] += 56
                counts["completed_prefixes"] += len(episodes)
                counts["schedule_decisions"] += sum(x["turns"] * x["schedules_represented"] for x in episodes)
                branches = []
                for visit in visits:
                    b = Branch(visit, tape, rep)
                    supports[law].add(visit)
                    counts["distinct_visits"] += 1
                    if not visit.current[0]:
                        continue
                    counts["feeder_visits"] += 1
                    counts["after_paid_feeder_visits"] += eligible(b)
                    first_classes[law][visit.current, b.first_memory][visit.full] += 1
                    within[visit.public][visit.full].append(b)
                    branches.append(b)
                    old = earlier_case[law].get(visit.public)
                    if old is None:
                        earlier_case[law][visit.public] = (meta, b)
                    elif old[1].visit.full != visit.full:
                        opposite = any_twin.get(law)
                        if opposite is None or b.turn < opposite["turn"]:
                            sides = ((old[0], old[1]), (meta, b)) if visit.full else ((meta, b), (old[0], old[1]))
                            any_twin[law] = {"turn": b.turn, "empty": {**sides[0][0], **sides[0][1].packed()},
                                             "full": {**sides[1][0], **sides[1][1].packed()}}
                by_tape.append(groups(branches))
            pairs, matched = enumerate_pairs(meta, cut, by_tape, control)
            bank_pairs.extend(pairs)
            n_twins, twin = public_twins(meta, cut, within)
            strong_twin_numbers[law] += n_twins
            if twin is not None and (law not in strong_twin or twin["turn"] < strong_twin[law]["turn"]):
                strong_twin[law] = twin
            cells = {}
            for kind in PANELS:
                cells[kind] = count_pairs([p for p in pairs if p["panel"] == kind])
                cells[kind]["distinct_paired_visits"] = len(matched[kind])
                cells[kind]["unmatched_after_paid_feeder_visits"] = counts["after_paid_feeder_visits"] - len(matched[kind])
            by_founder[law].append({**meta, "counts": dict(counts), "panels": cells,
                                   "first_funded": bool(world.attempts and world.attempts[0].births),
                                   "exact_distinct_target_twins_all_tapes": n_twins})

    results = {"schema": "second-feeder-panel-v1", "founders_requested": 32, "tapes_per_source": TAPES,
               "released_policy_sha256": args.policy_sha, "per_law": {},
               "paired_law_traces_identical": traces["parity"].digest() == traces["nae"].digest()}
    for law in LAWS:
        stats = {}
        starts = by_founder[law]
        for kind in PANELS:
            rows = [p for p in bank_pairs if p["law"] == law and p["panel"] == kind]
            s = count_pairs(rows)
            src = [v["panels"][kind] for v in starts]
            n = [v for v in src if v.get("pairs", 0)]
            s.update({"founders_with_pairs": len(n), "founders_without_pairs": len(src) - len(n),
                      "distinct_paired_visits": sum(v["distinct_paired_visits"] for v in src),
                      "unmatched_after_paid_feeder_visits": sum(v["unmatched_after_paid_feeder_visits"] for v in src),
                      "equal_founder_mean_proportion_both_certified":
                          fmean(v.get("both_certified", 0) / v["pairs"] for v in n) if n else None})
            stats[kind] = s
        mixed = supports[law].full
        for p in bank_pairs:
            if p["law"] == law:
                p["public_twin_witnessed"] = [all(mixed[p[side]["public"]]) for side in ("empty", "full")]
                s = stats[p["panel"]]
                s["at_least_one_opposite_full_history_witness"] = s.get("at_least_one_opposite_full_history_witness", 0) + int(any(p["public_twin_witnessed"]))
        support = supports[law].summary()
        support["old_memory_and_current_finite"] = Support.class_summary(first_classes[law])
        results["per_law"][law] = {
            "all": dict(sum((Counter(v["counts"]) for v in starts), Counter())),
            "number_funded": sum(v["first_funded"] for v in starts), "panels": stats,
            "founder_rows": starts, "support": support, "episode_sha256": traces[law].hexdigest(),
            "any_exact_opposite_public_example": any_twin.get(law), "exact_distinct_targets_all_tapes": strong_twin_numbers[law],
            "strong_exact_public_example": strong_twin.get(law),
        }
    save_gzip(HERE / "panel_pairs.json.gz", bank_pairs)
    save_gzip(HERE / "panel_runs.json.gz", terminal_ledger)
    inputs = [HERE / "panel.py", HERE / "bank.py", HERE / "bank.json", HERE / "preregistration.md",
              HERE / "panel_design.md", PREVIOUS / "history_reader.py", PREVIOUS / "history_panel.py"]
    results["input_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in inputs if p.is_file()}
    results["elapsed_seconds"] = round(perf_counter() - begun, 3)
    (HERE / "panel_results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(compact({law: {k: v.get("pairs", 0) for k, v in d["panels"].items()}
                   for law, d in results["per_law"].items()}))


if __name__ == "__main__":
    main()
