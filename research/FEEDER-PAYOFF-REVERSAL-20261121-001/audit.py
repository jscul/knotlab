"""Independently check the released exposure, mechanism and survival records."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from statistics import fmean, quantiles

from intervene import (ARMS, BANK_PATH, CUE, HERE, LAWS, MIRRORS, VERSIONS, clue_after,
                       expected_action, learned_score, locked_weights, require, take_step, walk)
from paired_game import Observation, ReversalGame
from reader import PayoffReader
from source_bank import derive_seed, movement_tape, sample_pair


TRAIN_ARMS = ("outcome", "count", "shuffled")
ORDERS = ("primary", "reversed")
READERS = (*TRAIN_ARMS, "current", "fixed_A", "fixed_B", "crossed")
CONTROLS = (*READERS[1:], "balanced_fixed")
GROUPS = {"pooled": ((0, 0), (0, 1), (1, 0), (1, 1)),
          "version_0": ((0, 0), (0, 1)), "version_1": ((1, 0), (1, 1)),
          "ordinary_0": ((0, 0),), "mirrored_0": ((0, 1),),
          "ordinary_1": ((1, 0),), "mirrored_1": ((1, 1),)}
EXPOSURE = ("seen", "eligible", "on", "on_open", "on_closed", "on_empty", "off_open", "off_closed", "off_empty")
CHANGES = ("outcome_on_other_off", "outcome_off_other_on", "outcome_correct_change", "outcome_incorrect_change")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def integers(row, names):
    return [int(row[name]) for name in names]


def trace_rows(row):
    return json.loads(row["public_trace"])


def check_training_route(row, start):
    trace = trace_rows(row)
    turn = int(row["turn"])
    route = json.loads(row["actual_route"])
    require(len(trace) == turn and len(route) == turn and route[-1] == int(row["target_holder"]),
            "Wrong number of training receipts or wrong target holder")
    require(int(row["seed"]) == start.seed and int(row["tape"]) == movement_tape("train", start.source_key, int(row["replicate"])),
            "Training receipt uses an unregistered founder or tape")
    cue = None
    before = 6
    eligible = []
    for index, (feeder, energy, previous, slots, bit, slot, after) in enumerate(trace, 1):
        require(energy == before and slots == list(range(len(slots))), "Invalid observed energy or public menu")
        require(bit == int(index == turn), "Probe action was chosen outside the declared last turn")
        if cue is not None and feeder and previous == "move" and len(slots) == 3:
            eligible.append((index, CUE[cue]))
        if bit:
            require(slot is None and after in (energy - 1, min(10, energy + 3)), "Invalid charged training bite")
        else:
            require((slot is None and not slots or slot in slots) and after == energy - 1,
                    "Pass was not the recorded charged public move or refusal")
        cue = clue_after(Observation(feeder, energy, previous, tuple(slots)), slot, cue)
        before = after
    require(eligible == [(turn, row["clue"])] and int(row["eligible_observations"]) == 1,
            "The training target is not the first actual eligible visit")
    final = trace[-1]
    actual = final[-1] >= final[1]
    before, after, bit, death = integers(row, ("query_energy_before", "query_energy_after", "actual_paid", "death"))
    require((before, after, bit, death) == (final[1], final[-1], int(actual), int(final[-1] == 0)),
            "Published payment differs from the public energy receipt")
    require(integers(row, ("turn_costs", "bite_cost")) == [turn, 1], "Wrong recorded charge in training")
    favored = int(row["version"]) ^ int(row["exception"])
    require(actual == (row["clue"] == CUE[favored]), "Matched bite did not have its declared opening")


def verify_first_physical_pair(rows, start_by_key, law):
    """Re-run the first two actual probes per fit, including the signed word updates."""
    bot = PayoffReader(law)
    sample = []
    for row in rows[:2]:
        start = start_by_key[row["source_key"]]
        world = sample_pair(start, "train")[law]
        version, tape, target, n = integers(row, ("version", "tape", "target_holder", "turn"))
        exception = bool(int(row["exception"]))
        game = ReversalGame(world, tape=tape, version=version, training_exception=(target, exception))
        bot.begin_episode(training=True)
        require(bot.score == int(row["score_before"]), "Training reset did not retain the learned word")
        trace = []
        for turn in range(1, n + 1):
            obs = game.observe()
            bit = bot.decide(obs, probe_bit=int(turn == n))
            checkpoint = game.snapshot()
            override = exception if checkpoint["holder"] == target else None
            observed = take_step(game, world, bit, exception=override)
            tr = observed.receipt
            trace.append([obs.feeder, obs.energy, obs.previous, list(obs.slots), bit, tr.outgoing_slot, tr.energy_after])
            credit = int(row["credit_paid"]) if bit and row["arm"] != "outcome" else None
            receipt = bot.after_turn(obs, bit, tr.outgoing_slot, tr.energy_after, credit_override=credit)
        require(trace == trace_rows(row) and checkpoint["holder"] == target,
                "An actual training prefix or charged bite differs from its saved public trace")
        require(receipt["eligible_bite"] and receipt["route_cue"] == row["clue"] and
                receipt["actual_paid"] == bool(int(row["actual_paid"])) and
                receipt["credit_paid"] == bool(int(row["credit_paid"])) and
                bot.score == int(row["score_after"]), "A sampled credit missed the physical learned word")
        sample.append({"seed": start.seed, "tape": tape, "turn": n, "clue": row["clue"],
                       "from_energy": obs.energy, "to_energy": tr.energy_after, "paid": receipt["actual_paid"],
                       "denied": observed.event["denied"], "stock_before": observed.event["food_before"],
                       "score_before": int(row["score_before"]), "score_after": bot.score, "physical_word": bot.export_memory()["word"]})
    return sample


def audit_training(directory, model, starts):
    path = directory / "training_receipts.csv"
    start_by_key = {start.source_key: start for start in starts}
    streams = defaultdict(list)
    for row in read_csv(path):
        require(row["law"] in LAWS and row["source_key"] in start_by_key and row["arm"] in TRAIN_ARMS and
                row["order"] in ORDERS and int(row["version"]) in VERSIONS, "Invalid role in training CSV")
        check_training_route(row, start_by_key[row["source_key"]])
        streams[row["law"], int(row["version"]), row["order"], row["arm"]].append(row)

    summary, first_pair, symmetry = [], [], []
    exposure = json.loads((directory / "exposure_results.json").read_bytes())
    for law in LAWS:
        selected = exposure["per_law"][law]["selected"]
        planned_routes = [(p["seed"], p[cue]["tape"]) for p in selected for cue in CUE]
        require(len(planned_routes) == len(set(planned_routes)) and len(selected) % 4 == 0 and len(selected) <= 64,
                "The admitted train pairs repeat a route or fail the complete-block budget")
        for block in range(0, len(selected), 4):
            schedule = selected[block:block + 4]
            require(sum(p["exception"] for p in schedule) == 1 and sum(p["A_first"] for p in schedule) == 2 and
                    sum(p["shuffled_payer"] == "A" for p in schedule) == 2, "Unmatched charge or order in training block")
        for order in ORDERS:
            for version in VERSIONS:
                factual = streams[law, version, order, "outcome"]
                for arm in TRAIN_ARMS:
                    rows = streams[law, version, order, arm]
                    require(len(rows) == 2 * len(selected), f"Omitted training pair under {law}")
                    score, counts = 0, Counter()
                    for index, row in enumerate(rows):
                        pair = selected[index // 2]
                        a_first = pair["A_first"] if order == "primary" else not pair["A_first"]
                        clue = ("A", "B")[index % 2 ^ int(not a_first)]
                        chooser = pair[clue]
                        other = rows[index ^ 1]
                        require(trace_rows(row)[-1][:4] == trace_rows(other)[-1][:4] and
                                row["actual_paid"] != other["actual_paid"],
                                "The two scheduled bites lack a common current view or complement")
                        require((row["public_trace"], row["actual_route"]) ==
                                (factual[index]["public_trace"], factual[index]["actual_route"]),
                                "A credit control changed the genuine game action or receipt")
                        require(row["clue"] == clue and integers(row, ("episode_index", "pair_index", "block_index", "position",
                            "seed", "target_holder", "replicate", "tape", "exception", "even_first")) ==
                            [index, pair["pair_index"], pair["block"], pair["position"], pair["seed"], pair["holder"],
                             chooser["replicate"], chooser["tape"], int(pair["exception"]), int(a_first)],
                            "The actual probe differs from the prospectively ordered pair")
                        paid, credited = integers(row, ("actual_paid", "credit_paid"))
                        expected = paid if arm == "outcome" else 1 if arm == "count" else int(clue == pair["shuffled_payer"])
                        require(credited == expected and int(row["score_before"]) == score,
                                "Training outcome or control supplied the wrong credit")
                        if arm == "shuffled":
                            donor = rows[index // 2 * 2 + (1 if row["donor_clue"] != rows[index // 2 * 2]["clue"] else 0)]
                            require(row["donor_clue"] == donor["clue"] and
                                    (row["donor_energy_before"], row["donor_energy_after"], credited) ==
                                    (donor["query_energy_before"], donor["query_energy_after"], int(donor["actual_paid"])),
                                    "The replacement receipt is not its matched actual donor")
                        score += (1 if clue == "A" else -1) * credited
                        require(int(row["score_after"]) == score, "Signed update differs from actual routed credit")
                        counts.update({f"{clue}_visits": 1, f"{clue}_paid": paid, f"{clue}_credited": credited})
                    family = "policies" if order == "primary" else "alternate_order"
                    require(learned_score(model[family][law][str(version)][arm]) == score, "Learned word fails ordered rescoring")
                    summary.append({"law": law, "version": version, "order": order, "arm": arm, "score": score, **counts})
                    if rows and order == "primary":
                        first_pair.append({"law": law, "version": version, "arm": arm,
                                           "actual": verify_first_physical_pair(rows, start_by_key, law)})

        for arm in TRAIN_ARMS:
            for order in ORDERS:
                a, b = (streams[law, v, order, arm] for v in VERSIONS)
                for left, right in zip(a, b, strict=True):
                    u, w = map(trace_rows, (left, right))
                    require((left["clue"], left["actual_route"], u[:-1], u[-1][:-1]) ==
                            (right["clue"], right["actual_route"], w[:-1], w[-1][:-1]),
                            "Version changed the actual pre-bite public route or cue sequence")
                    require(left["actual_paid"] != right["actual_paid"], "Versions failed to reverse the actual matched receipt")
                    if arm != "outcome":
                        require(left["credit_paid"] == right["credit_paid"], "Control received different routed credit across versions")
            for version in VERSIONS:
                a, b = streams[law, version, "primary", arm], streams[law, 1 - version, "reversed", arm]
                seq = lambda rows: [[[(step[1], step[-1]) for step in trace_rows(row)], row["actual_paid"]] for row in rows]
                require(seq(a) == seq(b), "Opposite versions in opposite pair order have different energy or payment chronology")
            symmetry.append({"law": law, "arm": arm, "full_prebite_clue_sequence_matched": True,
                             "crossed_version_and_order_all_turn_energy_matched": True})
    return {"receipts": sum(map(len, streams.values())), "receipt_csv_sha256": digest(path), "streams": summary,
            "order_checks": symmetry, "physically_replayed_first_pairs": first_pair}


def audit_opportunities(directory, starts, weights_sha, bank_sha):
    path = directory / "opportunity_results.json"
    report = json.loads(path.read_bytes())
    require(report["weights_sha256"] == weights_sha and report["bank_sha256"] == bank_sha,
            "Forced-opportunity ledger names different sealed inputs")
    by_seed = {start.seed: start for start in starts}
    counts = {law: [Counter(), Counter()] for law in LAWS}
    keys = set()
    for row in report["first_arrivals"]:
        law, seed, replicate = (row[name] for name in ("law", "founder", "replicate"))
        start = by_seed[seed]
        identity = law, seed, replicate
        require(identity not in keys and 0 <= replicate < 8 and row["tape"] == movement_tape("heldout", start.source_key, replicate),
                "Duplicate or unmatched fresh first-arrival probe")
        keys.add(identity)
        trials = row["versions_by_code"]
        fixed = {(b["turn"], b["holder"], b["energy_before"]) for pair in trials for b in pair}
        require(len(fixed) == 1, "A version or mirror changed the forced arrival state")
        for version, pair in enumerate(trials):
            require({p["clue"] for p in pair} == {0, 1} and sum(p["paid"] for p in pair) == 1,
                    "A genuine mirrored pair is missing a clue or has an unmatched payment")
            for code, point in enumerate(pair):
                other = trials[1 - version][code]
                require(point["clue"] == other["clue"] and point["paid"] != other["paid"], "Payment did not reverse across versions")
                before, after = point["energy_before"], point["energy_after"]
                require(after == min(10, before - 1 + 4 * point["paid"]), "A fresh forced bite has wrong energy accounting")
                cue = CUE[point["clue"]]
                counts[law][version][cue] += 1
                counts[law][version][f"{cue}_paid"] += point["paid"]
    for law in LAWS:
        count = sum(k[0] == law for k in keys)
        require(report["first_arrival_coverage"][law] == {"original_founder_tapes": len(starts) * 8,
                "matched": count, "no_focal_arrival": len(starts) * 8 - count}, "Fresh first-arrival coverage differs")
        for version in VERSIONS:
            require(counts[law][version] == report["real_bites"][law][str(version)], "Fresh payment rates disagree with raw bites")
    return {"records": len(keys), "per_law": {law: {str(v): counts[law][v] for v in VERSIONS} for law in LAWS}}


NATURAL_STATS = ("meals", "wasted", "stock_allocated", "stock_remaining", "empty_eats", "denied_eats",
                 "open_passes", "closed_stock_passes", "refusals")


@dataclass(frozen=True, slots=True)
class Episode:
    turns: int
    numeric: tuple[int, ...]
    natural_hash: str
    common_hash: str
    common_turns: int
    score: int | None
    funded: int
    stop: str
    natural: tuple[tuple[int, ...], ...]
    common: tuple[tuple[int, ...], ...]

    def triplet(self):
        return self.turns, self.numeric[0], self.numeric[1]


def mounted_score(model, law, version, arm):
    if arm == "current":
        return None, ""
    if arm in ("fixed_A", "fixed_B"):
        return 1 if arm == "fixed_A" else -1, ""
    origin = 1 - version if arm == "crossed" else version
    name = "outcome" if arm == "crossed" else arm
    return learned_score(model["policies"][law][str(origin)][name]), str(origin)


def load_episodes(path, model, starts):
    by_key = {start.source_key: start for start in starts}
    taps = {(key, x): movement_tape("heldout", key, x) for key in by_key for x in range(8)}
    blocks = defaultdict(dict)
    for row in read_csv(path):
        law, key, arm = row["law"], row["source_key"], row["arm"]
        version, code, replicate, seed, tape, candidate = integers(row, ("version", "mirror", "replicate", "seed", "tape", "candidate_index"))
        start = by_key[key]
        require(law in LAWS and (version, code) in GROUPS["pooled"] and arm in READERS and
                (seed, tape, candidate) == (start.seed, taps[key, replicate], start.candidate_index),
                "Episode does not follow registered pairing")
        block = blocks[law, key, replicate, version, code]
        require(arm not in block, "Duplicate natural episode")
        values = tuple(integers(row, NATURAL_STATS))
        turns, energy = integers(row, ("turns", "energy"))
        require(energy == 0 and row["reason"] == "death" and turns == 6 + 4 * values[0] - values[1] and
                values[2] == values[0] + values[3], "Terminal energy or stock does not balance")
        score, origin = mounted_score(model, law, version, arm)
        require(row["score"] == ("" if score is None else str(score)) and row["mounted_version"] == origin,
                "Mounted role violates the sealed word or version")
        data = []
        for name in ("natural", "common"):
            roles = []
            for role in CUE:
                fields = EXPOSURE if name == "natural" else (*EXPOSURE, *CHANGES)
                numbers = tuple(integers(row, (f"{name}_{role}_{x}" for x in fields)))
                seen, eligible, on = numbers[:3]
                require(0 <= eligible <= seen and on == sum(numbers[3:6]) and eligible == sum(numbers[3:9]),
                        "Public cue exposure cells are not mutually exhaustive")
                if name == "common":
                    require(sum(numbers[9:11]) == sum(numbers[11:]) <= eligible,
                            "Common-path comparison fails to account for all changed bits")
                roles.append(numbers)
            data.append(tuple(roles))
        block[arm] = Episode(turns, values, row["public_history_sha256"], row["common_public_history_sha256"],
                             int(row["common_turns"]), score, int(row["first_funded"]), row["growth_stop"], *data)
    require(len(blocks) == len(LAWS) * len(starts) * 8 * len(GROUPS["pooled"]), "Missing source/tape/version/code blocks")
    for block in blocks.values():
        require(set(block) == set(READERS), "A paired block is missing an arm")
        frozen = {(e.numeric[2], e.common_hash, e.common_turns, tuple(role[1] for role in e.common)) for e in block.values()}
        current = block["current"]
        require(len(frozen) == 1 and current.common_hash == current.natural_hash and current.common_turns == current.turns,
                "Common or initial stock condition differs across controls")
    return blocks


def founder_data(cluster, control):
    counts = []
    measurements = []
    aliases = ("fixed_A", "fixed_B") if control == "balanced_fixed" else (control,)
    for block in cluster:
        outcome = block["outcome"].triplet()
        baseline = list(zip(*(block[name].triplet() for name in aliases), strict=True))
        differential = tuple(x - fmean(ys) for x, ys in zip(outcome, baseline, strict=True))
        require(differential[0] == 4 * differential[1] - differential[2], "Paired energy differences disagree")
        measurements.append(differential)
        counts.append(differential[0])
    values = list(map(fmean, zip(*measurements, strict=True)))
    return {"pairs": len(counts), **dict(zip(("mean_delta_turns", "mean_delta_meals", "mean_delta_wasted"), values, strict=True)),
            "wins": sum(value > 0 for value in counts), "ties": counts.count(0), "losses": sum(value < 0 for value in counts)}


def bootstrap(values, seed, choices=None):
    rng = Random(seed)
    n = len(values)
    if choices is None:
        estimates = [fmean(rng.choices(values, k=n)) for _ in range(2000)]
    else:
        estimates = []
        for _ in range(2000):
            sample = rng.choices(choices, k=n)
            estimates.append(min(fmean(column) for column in zip(*sample, strict=True)))
    limits = quantiles(estimates, n=40, method="inclusive")
    return limits[0], limits[-1]


def audit_group(law, group, clusters, starts, published, founders):
    means = {arm: fmean(block[arm].turns for cluster in clusters for block in cluster) for arm in READERS}
    for arm in READERS:
        observed = [block[arm] for cluster in clusters for block in cluster]
        row = published["arms"][arm]
        require(row["episodes"] == len(observed) and row["mean_turns"] == means[arm], "Raw arm lifetimes do not match summary")
        for index, cue in enumerate(CUE):
            observed_natural = dict(zip(EXPOSURE, map(sum, zip(*(r.natural[index] for r in observed), strict=True)), strict=True))
            observed_common = dict(zip((*EXPOSURE, *CHANGES), map(sum, zip(*(r.common[index] for r in observed), strict=True)), strict=True))
            require(observed_natural == row["natural_exposure"][cue] and observed_common == row["common_exposure"][cue],
                    "Natural or common exposure totals do not replay")
    best = max(("fixed_A", "fixed_B"), key=means.__getitem__) if group == "pooled" else None
    require(published["best_pooled_constant"] == best, "Best fixed pooled arm is mislabeled")
    controls = (*CONTROLS, "best_constant") if best else CONTROLS
    matrix = {control: [founder_data(cluster, best if control == "best_constant" else control) for cluster in clusters]
              for control in controls}
    summary = {}
    for control, data in matrix.items():
        for start, cluster, observed in zip(starts, clusters, data, strict=True):
            row = founders.pop((law, group, control, start.source_key))
            marker = cluster[0]["outcome"]
            require((int(row["seed"]), int(row["first_funded"]), row["growth_stop"]) == (start.seed, marker.funded, marker.stop),
                    "Founder funding or growth annotation differs")
            require(all(float(row[k]) == v for k, v in observed.items()), "Independent founder deltas do not match CSV")
        values = [row["mean_delta_turns"] for row in data]
        seed = derive_seed("survival-bootstrap", law, group, control)
        options = None
        if control == "best_constant":
            options = list(zip(*([r["mean_delta_turns"] for r in matrix[arm]] for arm in ("fixed_A", "fixed_B")), strict=True))
        interval = list(bootstrap(values, seed, options))
        aggregate = {"paired_founders": len(data), "paired_games": sum(r["pairs"] for r in data),
                     "mean_delta_turns": fmean(values), "bootstrap_seed": seed, "founder_bootstrap_95_percent_interval": interval,
                     **{key: fmean(r[key] for r in data) for key in ("mean_delta_meals", "mean_delta_wasted")},
                     **{key: sum(r[key] for r in data) for key in ("wins", "ties", "losses")}}
        require(all(published["outcome_minus"][control][k] == v for k, v in aggregate.items()),
                f"Independent bootstrap or aggregate differs for {law} {group} {control}")
        summary[control] = aggregate
    return summary


def audit_survival(directory, model, starts, weights_sha, bank_sha):
    episodes_path = directory / "survival_episodes.csv"
    founders_path = directory / "survival_founders.csv"
    report = json.loads((directory / "survival_results.json").read_bytes())
    require(report["weights_sha256"] == weights_sha and report["bank_sha256"] == bank_sha and report["bootstrap_draws"] == 2000,
            "Lifetime report names a different lock or bootstrap")
    blocks = load_episodes(episodes_path, model, starts)
    founder_rows = {}
    for row in read_csv(founders_path):
        key = tuple(row[k] for k in ("law", "group", "control", "source_key"))
        require(key not in founder_rows, "Duplicate founder contrast")
        founder_rows[key] = row
    checked = {}
    for law in LAWS:
        checked[law] = {}
        for group, codes in GROUPS.items():
            clusters = [[blocks[law, start.source_key, r, v, m] for r in range(8) for v, m in codes] for start in starts]
            checked[law][group] = audit_group(law, group, clusters, starts, report["by_law"][law][group], founder_rows)
    require(not founder_rows and len(blocks) == report["paired_cases"] == report["common_episodes"] and
            len(blocks) * len(READERS) == report["natural_episodes"] and report["censored_episodes"] == 0,
            "Episode or founder denominators do not reconcile")
    return {"natural_episodes": len(blocks) * len(READERS), "common_episodes": len(blocks),
            "episodes_csv_sha256": digest(episodes_path), "founders_csv_sha256": digest(founders_path), "by_law": checked}


def audit_mechanism(path, model, starts, weights_sha, bank_sha):
    report = json.loads(path.read_bytes())
    require(report["schema"] == "feeder-payoff-mechanism-v1" and report["weights_sha256"] == weights_sha
            and report["bank_sha256"] == bank_sha and report["arm_order"] == list(ARMS),
            "The intervention ledger does not share the release")
    indexed = {start.seed: start for start in starts}
    rows = defaultdict(dict)
    for values in report["eligible_rows"]:
        data = dict(zip(report["eligible_fields"], values, strict=True))
        law, seed, replicate, turn, code, version = (data[k] for k in ("law", "seed", "replicate", "turn", "mirror", "version"))
        require(law in LAWS and seed in indexed and 0 <= replicate < 64 and 2 <= turn <= 6 and code in MIRRORS and version in VERSIONS,
                "Unregistered mechanism cell")
        group = rows[law, seed, replicate, turn, code]
        require(version not in group, "Duplicate reciprocal recipient")
        group[version] = data
    tally, counted = defaultdict(Counter), Counter()
    worlds_memo, visit_memo = {}, {}
    for (law, seed, replicate, turn, code), right_left in rows.items():
        start = indexed[seed]
        worlds = worlds_memo.setdefault(seed, sample_pair(start, "mechanism")) if seed not in worlds_memo else worlds_memo[seed]
        tape = movement_tape("mechanism", start.source_key, replicate)
        inputs = []
        for version, row in sorted(right_left.items()):
            key = (law, seed, tape, version, code)
            if key not in visit_memo:
                visit_memo[key] = walk(worlds[law], tape, version, code)[0]
            visit = visit_memo[key][turn]
            require(CUE[visit.approach] == row["cue"], "Recorded eligible cue disagrees with actual coded slot")
            words = model["policies"][law]
            resident = learned_score(words[str(version)]["outcome"])
            donor = learned_score(words[str(1 - version)]["outcome"])
            scores = (resident, resident, donor, 0, resident, learned_score(words[str(version)]["count"]),
                      learned_score(words[str(version)]["shuffled"]))
            predicted = [expected_action(visit.observation, visit.approach, score) for score in scores]
            require(row["expected_bits"] == predicted, "Decision predictions disagree with signed words")
            bites = [take_step(visit.game.clone(), worlds[law], bit).event for bit in (0, 1)]
            expect = [[bites[bit][k] for k in ("consumed", "denied", "energy_after")] for bit in row["issued_bits"]]
            require(row["consumed_denied_energy_after"] == expect and row["stock"] == bites[1]["food_before"]
                    and row["would_pay"] == bites[1]["consumed"] and row["accepted"] == CUE[bites[1]["accepted_approach"]],
                    "Actuator result, depletion and private payment are not jointly reproducible")
            inputs.append((row, visit.public_key()))
            counted[law, version, code] += 1

        cue = inputs[0][0]["cue"]
        counter = tally[law, code, cue]
        if len(inputs) != 2:
            counter["unmatched_recipient_turns"] += len(inputs)
            continue
        (first, a), (second, b) = inputs
        counter["both_eligible"] += 1
        if a != b or first["cue"] != second["cue"]:
            counter["not_exactly_matched"] += 1
            continue
        counter["exact_pairs"] += 1
        old = [first["issued_bits"][0], second["issued_bits"][0]]
        transferred = [first["issued_bits"][2], second["issued_bits"][2]]
        flip = old[0] != old[1] and old == transferred[::-1]
        correct = old == [first["would_pay"], second["would_pay"]]
        sham = old == [first["issued_bits"][1], second["issued_bits"][1]]
        restored = old == [first["issued_bits"][4], second["issued_bits"][4]]
        erased = [first["issued_bits"][3], second["issued_bits"][3]] == [1, 1]
        counter.update(swap_both_ways=int(flip), both_correct_reciprocal=int(correct and flip),
                       fully_controlled_correct_reciprocal=int(correct and flip and sham and restored and erased),
                       sham_unchanged_both=int(sham), restore_original_both=int(restored), neutral_both=int(erased))
    for row in report["paired"]:
        counts = tally[row["law"], row["mirror"], row["cue"]]
        require(all(row.get(key, 0) == value for key, value in counts.items()), "Raw reciprocal counts differ from publication")
    for row in report["margins"]:
        counts = ("nonfeeder", "feeder_other_menu", "three_exit_missing_cue", "three_exit_ordinary_pass", "eligible")
        require(row["games"] == len(starts) * 64 and row["reached"] == sum(row.get(key, 0) for key in counts) and
                row["games"] * 5 == row["reached"] + row.get("missing_after_death", 0) and
                row["eligible"] == counted[row["law"], row["version"], row["mirror"]],
                "Scheduled states, ineligible states and actual recipients do not reconcile")
    return {"eligible_recipients": sum(counted.values()), "record_sha256": digest(path),
            "pair_counts": [{"law": law, "mirror": code, "cue": cue, **counts}
                            for (law, code, cue), counts in sorted(tally.items())]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, default=HERE / "learned_words.json")
    parser.add_argument("--weights-sha", required=True)
    parser.add_argument("--bank", type=Path, default=BANK_PATH)
    parser.add_argument("--directory", type=Path, default=HERE, help="raw exposure, intervention and survival files")
    parser.add_argument("--output", type=Path, default=HERE / "audit_results.json")
    args = parser.parse_args()
    try:
        model, folds, bank_sha = locked_weights(args.weights, args.weights_sha, args.bank)
        result = {"schema": "feeder-payoff-reversal-audit-v1", "weights_sha256": args.weights_sha, "bank_sha256": bank_sha,
                  "training": audit_training(args.directory, model, folds["train"]),
                  "fresh_first_arrival": audit_opportunities(args.directory, folds["heldout"], args.weights_sha, bank_sha),
                  "mechanism": audit_mechanism(args.directory / "mechanism_results.json", model, folds["mechanism"], args.weights_sha, bank_sha),
                  "survival": audit_survival(args.directory, model, folds["heldout"], args.weights_sha, bank_sha)}
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"Checked {result['training']['receipts']} fitted receipts, {result['mechanism']['eligible_recipients']} rooted recipients, "
              f"and {result['survival']['natural_episodes']} complete lifetime episodes in {args.output}.")
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
