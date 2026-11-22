"""Enumerate the frozen Boolean action schedules and group public feeder histories."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
from hashlib import sha256
from itertools import islice
import json
from math import comb
from pathlib import Path
from time import perf_counter

from feeder_game import FeederGame, recode_world, sample_world
from history_reader import history_reason, history_verdict
from survival_sources import candidate_starts, derive_seed


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "KNOT-RATION-GAME-20261121-001"
LAWS = ("parity", "nae")
VARIANTS = ("original", "renamed")
PREVIOUS = {"start": 0, "eat": 1, "move": 2, "refused": 3}
ATTEMPT_END = 10
MAX_ATTEMPTS = 2
LAST_TURN = 14


def compact(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def save_gzip(path, value):
    # mtime=0 permits exact regeneration of the compressed scientific ledger.
    with path.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as stream:
        stream.write(compact(value).encode("ascii"))


def view(obs):
    return bool(obs.feeder), obs.energy, PREVIOUS[obs.previous], len(obs.slots)


def action_code(transition):
    if transition.bit:
        return 0
    if transition.outgoing_slot is None:
        return -2
    return transition.outgoing_slot + 1


def choose_count(turn, n_attempts):
    remaining = max(0, ATTEMPT_END - turn + 1)
    return sum(comb(remaining, n) for n in range(min(MAX_ATTEMPTS - n_attempts, remaining) + 1))


@dataclass(frozen=True, slots=True)
class Visit:
    public: tuple
    route: tuple
    attempts: tuple
    meals: tuple
    full: bool

    @property
    def current(self):
        return self.public[-1][:-1]

    @property
    def spent(self):
        return tuple(self.route[t - 1] for t in self.meals)

    def packed(self, *, reason=True):
        row = {
            "attempt_turns": self.attempts, "meal_turns": self.meals,
            "spent_holders": sorted(self.spent), "paid_in_order": self.spent,
            "route": self.route, "public": self.public, "verdict": history_verdict(self.public),
        }
        if reason:
            row["certificate"] = history_reason(self.public)
        return row

    def last_paid_type(self):
        count = self.public[self.meals[-1] - 1][3]
        return 0 if not count else 1 if count == 1 else 2

    def last_return(self):
        earlier = [t for t, p in enumerate(self.route[:-1]) if p == self.route[-1]]
        return None if not earlier else sum(row[4] > 0 for row in self.public[earlier[-1]:-1])


class Support:
    """Exact multiplicities over reached action prefixes of this finite experiment."""

    def __init__(self):
        self.current = defaultdict(lambda: [0, 0])
        self.full = defaultdict(lambda: [0, 0])
        self.verdicts = Counter()
        self.cert_by_public = {}
        self.counts = Counter()

    def add(self, visit):
        self.counts["all_visits"] += 1
        if not visit.current[0]:
            self.counts["founder_visits"] += 1
            return
        self.counts["feeder_visits"] += 1
        label = int(visit.full)
        self.current[visit.current][label] += 1
        self.full[visit.public][label] += 1
        verdict = self.cert_by_public.get(visit.public)
        if verdict is None:
            verdict = history_verdict(visit.public)
            self.cert_by_public[visit.public] = verdict
        if verdict in ("full", "empty") and (verdict == "full") != visit.full:
            raise AssertionError(("invalid public certificate", verdict, visit))
        self.verdicts[verdict] += 1
        self.counts["full" if visit.full else "empty"] += 1
        self.counts["current_policy_correct"] += (visit.current[2] != PREVIOUS["eat"]) == visit.full
        self.counts["history_policy_correct"] += (verdict in ("full", "unknown")) == visit.full
        if visit.current[2] == PREVIOUS["move"] and visit.meals:
            self.counts["with_prior_meal_and_arrival"] += 1

    @staticmethod
    def class_summary(classes):
        totals = Counter()
        for empty, full in classes.values():
            n = empty + full
            totals["classes"] += 1
            totals["visits"] += n
            totals["best_uniform_prefix_correct"] += max(empty, full)
            totals["best_uniform_prefix_errors"] += min(empty, full)
            kind = "mixed" if empty and full else "pure"
            totals[kind + "_classes"] += 1
            totals[kind + "_visits"] += n
            if n == 1:
                totals["singleton_classes"] += 1
        return dict(totals)

    def summary(self):
        remaining = 0
        mixed = 0
        for public, (empty, full) in self.full.items():
            if self.cert_by_public[public] == "unknown":
                if empty and full:
                    mixed += empty + full
                else:
                    remaining += empty + full
        assert mixed + remaining == self.verdicts["unknown"]
        return {
            "counts": dict(self.counts), "current_only_finite": self.class_summary(self.current),
            "complete_history_finite": self.class_summary(self.full),
            "public_certificates": dict(self.verdicts),
            "unknown_with_opposite_history_witness": mixed, "other_unknown": remaining,
        }


def frame(law, start, tape, repeat, variant):
    return {"law": law, "seed": start.seed, "source_key": start.source_key, "variant": variant,
            "tape": tape, "replicate": repeat}


def visit_word_order(visit, target, other):
    first = [i for i, holder in enumerate(visit.route) if holder in (target, other)]
    seen = {h for h in visit.route if h in (target, other)}
    if len(seen) == 2:
        return "target_first" if visit.route[first[0]] == target else "other_first"
    return "target_only" if target in seen else "other_only"


def make_pair(meta, empty, full):
    target = empty.route[-1]
    others = [h for h in full.spent if h not in empty.spent]
    def visited_both(h, *, before_query):
        return all({target, h} <= set(v.route[:-1] if before_query else v.route) for v in (empty, full))
    other = min(others, key=lambda h: (not visited_both(h, before_query=False),
                                      not visited_both(h, before_query=True), full.spent.index(h)))
    last_e = empty.meals[-1] - 1
    last_f = full.meals[-1] - 1
    target_type = 1 if empty.current[3] == 1 else 2 if empty.current[3] > 1 else 0
    last_types = (empty.last_paid_type(), full.last_paid_type())
    keeper_on = [typ != target_type for typ in last_types]
    lag = tuple(sum(row[4] > 0 for row in visit.public[prior + 1:-1])
                for visit, prior in ((empty, last_e), (full, last_f)))
    return {
        **meta, "turn": len(empty.public), "target_holder": target, "current": empty.current,
        "empty": empty.packed(), "full": full.packed(), "other_paid_holder": other,
        "both_feeders_visited": visited_both(other, before_query=False),
        "both_feeders_visited_before_probe": visited_both(other, before_query=True),
        "last_meal_same_turn_and_energy": last_e == last_f and
            empty.public[last_e][1] == full.public[last_f][1],
        "moves_since_last_meal": lag, "last_paid_types": last_types,
        "keeper_expected_on": keeper_on, "return_lengths": [empty.last_return(), full.last_return()],
        "visit_orders": [visit_word_order(v, target, other) for v in (empty, full)],
    }


def strong_pairs(meta, visits):
    by_context = defaultdict(lambda: [[], []])
    for v in visits:
        if v.current[0] and v.current[2] == PREVIOUS["move"] and v.meals:
            by_context[(len(v.public), v.route[-1], v.current, len(v.meals))][v.full].append(v)
    matched = set()
    pairs = []
    for empty_group, full_group in by_context.values():
        for empty in empty_group:
            for full in full_group:
                if set(empty.spent) == set(full.spent):
                    raise AssertionError("The same current feeder and spent set cannot change its stock.")
                pairs.append(make_pair(meta, empty, full))
                matched.update((empty.public, full.public))
    return pairs, len(matched)


def enumerate_cell(world, tape, *, original_labels=None):
    visits = []
    episodes = []

    def walk(game, past, route, attempts, meals):
        obs = game.observe()
        before = game.snapshot()
        local = view(obs)
        turn = len(past) + 1
        assert turn <= LAST_TURN and before["turns"] + 1 == turn
        holder = before["holder"]
        route = (*route, holder)
        full = holder in before["available"]
        visits.append(Visit((*past, (*local, -1)), route, attempts, meals, full))
        choices = (0, 1) if turn <= ATTEMPT_END and len(attempts) < MAX_ATTEMPTS else (0,)
        for bit in choices:
            child = game.clone()
            tr = child.step(bit)
            assert view(tr.observation) == local
            code = action_code(tr)
            paid = bool(bit and tr.energy_after > obs.energy - 1)
            assert paid == (bool(bit) and full)
            new_past = (*past, (*local, code))
            new_attempts = (*attempts, turn) if bit else attempts
            new_meals = (*meals, turn) if paid else meals
            if tr.next_observation is not None:
                walk(child, new_past, route, new_attempts, new_meals)
                continue
            assert tr.energy_after == 0
            episodes.append({
                "attempt_turns": new_attempts, "meal_turns": new_meals, "route": route,
                "public": new_past, "end_energy": 0, "turns": turn,
                "schedules_represented": choose_count(turn + 1, len(new_attempts)),
            })

    walk(FeederGame(world, tape=tape, original_labels=original_labels), (), (), (), ())
    assert sum(x["schedules_represented"] for x in episodes) == 56
    return visits, episodes


def archived_decisions():
    path = PRIOR / "replays/208304-nae-sensing.json"
    old = json.loads(path.read_text())
    born = set()
    completed = []
    regraded = {}
    for e in old["events"]:
        if e["growth"]:
            born.update(b["holder"] for b in e["growth"]["births"])
        local = (e["holder_before"] in born, e["energy_before"], PREVIOUS[e["previous"]], e["available_slots"])
        public = (*completed, (*local, -1))
        if e["turn"] in (15, 21):
            regraded[str(e["turn"])] = {
                "current": local, "public": public, "verdict": history_verdict(public),
                "certificate": history_reason(public), "scored_full": e["food_before"],
                "spectator_holder": e["holder_before"], "recorded_action": e["action"],
            }
        action = e["slot"] + 1 if e["action"] == "move" else 0
        completed.append((*local, action))
    assert regraded["15"]["current"] == regraded["21"]["current"]
    return regraded


def witness_rank(pair):
    return (
        not pair["both_feeders_visited"], not pair["last_meal_same_turn_and_energy"],
        min(pair["moves_since_last_meal"]) < 2,
        pair["source_key"], pair["tape"], pair["turn"], pair["empty"]["attempt_turns"],
        pair["full"]["attempt_turns"], VARIANTS.index(pair["variant"]),
    )


def pair_summary(pairs, support=None):
    counts = Counter()
    lengths = Counter()
    orders = Counter()
    paths = set()
    selected = None
    shortest = None
    feeders_in_opposite_orders = None
    different_returns = None
    for p in pairs:
        e, f = p["empty"], p["full"]
        cert = (e["verdict"], f["verdict"]) == ("empty", "full")
        correct = p["keeper_expected_on"] == [False, True]
        flip = p["keeper_expected_on"][0] != p["keeper_expected_on"][1]
        counts["pairs"] += 1
        counts["two_certificates"] += cert
        counts["same_last_type"] += p["last_paid_types"][0] == p["last_paid_types"][1]
        counts["different_last_type"] += p["last_paid_types"][0] != p["last_paid_types"][1]
        counts["expected_keeper_opposite"] += flip
        counts["expected_keeper_correct_both"] += correct
        counts["certified_and_expected_keeper_correct_both"] += cert and correct
        counts["same_last_meal_turn_and_energy"] += p["last_meal_same_turn_and_energy"]
        counts["both_previously_visited_target"] += None not in p["return_lengths"]
        counts["both_feeders_visited"] += p["both_feeders_visited"]
        counts["both_feeders_visited_before_probe"] += p["both_feeders_visited_before_probe"]
        counts["certified_correct_both_feeders_visited"] += cert and correct and p["both_feeders_visited"]
        counts["matched_prior_two_meals"] += len(e["meal_turns"]) == 2
        counts["at_least_two_moves_since_last_meals"] += min(p["moves_since_last_meal"]) >= 2
        counts["history_policy_correct_both"] += e["verdict"] == "empty" and f["verdict"] != "empty"
        if support is not None:
            mixed = [all(support.full[branch["public"]]) for branch in (e, f)]
            counts["opposite_public_history_witness_on_either_branch"] += any(mixed)
            counts["opposite_public_history_witness_on_both_branches"] += all(mixed)
        lengths[compact(p["return_lengths"])] += 1
        orders[compact(p["visit_orders"])] += 1
        for branch in (e, f):
            # Compare patterns of holder revisits with all private names erased.
            seen = {}
            paths.add(tuple(seen.setdefault(h, len(seen)) for h in branch["route"]))
        if cert and correct and (selected is None or witness_rank(p) < witness_rank(selected)):
            selected = p
        if cert and correct and (shortest is None or (p["turn"], witness_rank(p)) <
                                 (shortest["turn"], witness_rank(shortest))):
            shortest = p
        if (p["both_feeders_visited"] and len(set(p["visit_orders"])) == 2
                and (feeders_in_opposite_orders is None or witness_rank(p) < witness_rank(feeders_in_opposite_orders))):
            feeders_in_opposite_orders = p
        if (None not in p["return_lengths"] and len(set(p["return_lengths"])) == 2
                and (different_returns is None or witness_rank(p) < witness_rank(different_returns))):
            different_returns = p
    return {
        "counts": dict(counts), "ordered_return_lengths": dict(lengths), "visit_order": dict(orders),
        "distinct_name_erased_walks": len(paths), "selected": selected, "shortest_strong": shortest,
        "opposite_visit_orders": feeders_in_opposite_orders, "different_return_lengths": different_returns,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extension", action="store_true", help="run the preregistered witness-only extension")
    args = parser.parse_args()
    t_start = perf_counter()
    if args.extension:
        primary = json.loads((HERE / "history_results.json").read_text())
        need_causal = {law for law in LAWS if primary["per_law"][law]["pairs"]["selected"] is None}
        need_twin = {law for law in LAWS if primary["per_law"][law]["opposite_history_example"] is None}
        if not (need_causal or need_twin):
            raise SystemExit("The declared primary study already has both witness kinds under each law.")
    else:
        need_causal = set(LAWS)
        need_twin = set(LAWS)
    starts = list(islice(candidate_starts("mechanism"), 16 if not args.extension else 48))
    if args.extension:
        starts = starts[16:]
    banks = {law: {v: Support() for v in (*VARIANTS, "paired_mixture")} for law in LAWS}
    all_pairs = {law: [] for law in LAWS}
    opposite = {law: None for law in LAWS}
    representatives = {law: {} for law in LAWS}
    stats = {law: Counter() for law in LAWS}
    law_traces = {law: sha256() for law in LAWS}
    run_blocks = []
    processed = []
    recodings = []
    suffix = "_extension" if args.extension else ""
    num_tapes = 32 if args.extension else 16

    for start in starts:
        processed.append({"seed": start.seed, "source_key": start.source_key, "index": start.candidate_index})
        for law in LAWS:
            world = sample_world(start.seed, law, rounds=2)
            renamed, labels = recode_world(world)
            stats[law]["starts"] += 1
            stats[law]["first_funded_starts"] += bool(world.attempts and world.attempts[0].births)
            for repeat in range(num_tapes):
                tape = derive_seed("tape", start.source_key, repeat)
                original_episodes = None
                for variant, shown in zip(VARIANTS, (world, renamed), strict=True):
                    meta = frame(law, start, tape, repeat, variant)
                    visits, episodes = enumerate_cell(shown, tape)
                    if variant == "original":
                        original_episodes = episodes
                    for v in visits:
                        banks[law][variant].add(v)
                        banks[law]["paired_mixture"].add(v)
                        if not v.current[0]:
                            continue
                        previous = representatives[law].get(v.public)
                        if previous is None:
                            representatives[law][v.public] = (meta, v)
                        elif previous[1].full != v.full:
                            old_meta, old = previous
                            # A cross-tape collision on the very same physical target is preferred.
                            same_target = old_meta["seed"] == meta["seed"] and old.route[-1] == v.route[-1]
                            same_which = same_target and set(old.spent) != set(v.spent)
                            rank = (not same_which, not same_target, not bool(v.meals), len(v.public))
                            candidate = opposite[law]
                            if candidate is None or rank < candidate["rank"]:
                                v0, v1 = ((old_meta, old), (meta, v)) if v.full else ((meta, v), (old_meta, old))
                                opposite[law] = {
                                    "rank": rank, "same_physical_target": same_target,
                                    "different_spent_sets_same_target": same_which,
                                    "empty": {**v0[0], **v0[1].packed()}, "full": {**v1[0], **v1[1].packed()},
                                }
                    matched, n_matched = strong_pairs(meta, visits)
                    all_pairs[law].extend(matched)
                    banks[law][variant].counts["matched_unique_visits"] += n_matched
                    banks[law]["paired_mixture"].counts["matched_unique_visits"] += n_matched
                    stats[law]["cells"] += 1
                    stats[law]["fixed_schedules"] += 56
                    stats[law]["distinct_stopped_prefixes"] += len(episodes)
                    stats[law]["turns_counting_all_schedules"] += sum(
                        ep["turns"] * ep["schedules_represented"] for ep in episodes)
                    for ep in episodes:
                        s = ep["schedules_represented"]
                        stats[law]["charged_empty_eats_counting_schedules"] += s * (
                            len(ep["attempt_turns"]) - len(ep["meal_turns"]))
                    run_blocks.append({**meta, "terminal_prefixes": episodes})
                    law_traces[law].update(compact(episodes).encode("ascii"))
                # A full parity/NAE split across founders keeps these recodings paired.
                if repeat == 0:
                    _, restored = enumerate_cell(renamed, tape, original_labels=labels)
                    if original_episodes != restored:
                        raise AssertionError("Reversing distinction names and transporting local ranks changed a trajectory.")
                    recodings.append({"law": law, "seed": start.seed, "tape": tape,
                                      "schedules": 56, "distinct_stopped_prefixes": len(restored)})
        if args.extension:
            attained_causal = all(pair_summary(all_pairs[l])["selected"] is not None for l in need_causal)
            attained_twin = all(opposite[l] is not None for l in need_twin)
            if attained_causal and attained_twin:
                break

    pairs = [p for law in LAWS for p in all_pairs[law]]
    results = {"schema": "feeder-history-v1", "extension": args.extension, "starts": processed,
               "tapes_per_start": num_tapes, "schedules_per_cell": 56,
               "archive": archived_decisions(), "transported_port_controls": recodings, "per_law": {}}
    for law in LAWS:
        summaries = {variant: bank.summary() for variant, bank in banks[law].items()}
        for summary in summaries.values():
            counts = summary["counts"]
            counts["unmatched_after_meal_arrivals"] = (
                counts.get("with_prior_meal_and_arrival", 0) - counts.get("matched_unique_visits", 0))
            counts["all_other_feeder_visits"] = counts.get("feeder_visits", 0) - counts.get("matched_unique_visits", 0)
            assert counts["unmatched_after_meal_arrivals"] >= 0
        results["per_law"][law] = {
            "runs": dict(stats[law]), "support": summaries,
            "pairs": pair_summary(all_pairs[law], banks[law]["paired_mixture"]),
            "pairs_by_variant": {
                variant: pair_summary([p for p in all_pairs[law] if p["variant"] == variant],
                                      banks[law][variant])
                for variant in VARIANTS
            },
            "opposite_history_example": opposite[law], "episode_sha256": law_traces[law].hexdigest(),
        }
    results["law_episodes_identical"] = law_traces["parity"].digest() == law_traces["nae"].digest()
    save_gzip(HERE / f"history_runs{suffix}.json.gz", run_blocks)
    save_gzip(HERE / f"history_pairs{suffix}.json.gz", pairs)
    results["elapsed_seconds"] = round(perf_counter() - t_start, 3)
    (HERE / f"history_results{suffix}.json").write_text(json.dumps(results, indent=2) + "\n")
    print(compact({law: {"runs": results["per_law"][law]["runs"],
                          "pairs": results["per_law"][law]["pairs"]["counts"],
                          "ambiguity_witness": opposite[law] is not None} for law in LAWS}), flush=True)


if __name__ == "__main__":
    main()
