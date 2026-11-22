"""Run the sealed feeder-policy comparison on paired held-out founders."""

import argparse
from collections import Counter, defaultdict
from copy import copy
import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from statistics import fmean, quantiles
from time import perf_counter

from paired_game import ReversalGame, current_only, derive_clue
from reader import ACTION_MARK, PayoffReader
from source_bank import BANK_PATH, HERE, LAWS, derive_seed, load_bank, movement_tape, sample_pair


READERS = ("outcome", "count", "shuffled", "current", "fixed_A", "fixed_B", "crossed")
CONTROLS = (*READERS[1:], "balanced_fixed")
TAPES = 8
BOOTSTRAP_DRAWS = 2000
ROLES = ("A", "B")
GROUPS = {
    "pooled": ((0, False), (0, True), (1, False), (1, True)),
    "version_0": ((0, False), (0, True)), "version_1": ((1, False), (1, True)),
    "ordinary_0": ((0, False),), "mirrored_0": ((0, True),),
    "ordinary_1": ((1, False),), "mirrored_1": ((1, True),),
}
EXPOSURE = ("seen", "eligible", "on", "on_open", "on_closed", "on_empty", "off_open", "off_closed", "off_empty")
CHANGES = ("outcome_on_other_off", "outcome_off_other_on", "outcome_correct_change", "outcome_incorrect_change")
NATURAL_FIELDS = tuple(f"natural_{role}_{key}" for role in ROLES for key in EXPOSURE)
COMMON_FIELDS = tuple(f"common_{role}_{key}" for role in ROLES for key in (*EXPOSURE, *CHANGES))
IDENTITY = ("law", "version", "mirror", "source_key", "seed", "candidate_index", "replicate", "tape")
EPISODE_FIELDS = (*IDENTITY, "arm", "mounted_version", "score", "first_funded", "growth_stop",
                  "turns", "meals", "wasted", "energy", "reason", "stock_allocated", "stock_remaining",
                  "denied_eats", "empty_eats", "open_passes", "closed_stock_passes", "refusals",
                  "public_history_sha256", "common_turns", "common_public_history_sha256", *NATURAL_FIELDS, *COMMON_FIELDS)
FOUNDER_FIELDS = ("law", "group", "control", "source_key", "seed", "first_funded", "growth_stop", "pairs",
                  "mean_delta_turns", "mean_delta_meals", "mean_delta_wasted", "wins", "ties", "losses")


def _physical_bit(board, obs, probe=None):
    emitted = board.decide(obs) if probe is None else board.decide(obs, probe_bit=probe)
    actual = (board.word >> ACTION_MARK) & 1
    if emitted != actual or (probe is not None and actual != probe):
        raise RuntimeError("The issued bit differs from the prepared physical action mark.")
    return actual


class Seat:
    """One fixed reader with an independently audited physical action read."""

    def __init__(self, arm, law, version, weights):
        self.mounted_version = None
        if arm == "current":
            self.board = None
        elif arm in ("fixed_A", "fixed_B"):
            self.board = PayoffReader.calibrated(law, arm[-1])
        else:
            self.mounted_version = version ^ 1 if arm == "crossed" else version
            condition = "outcome" if arm == "crossed" else arm
            word = weights["policies"][law][str(self.mounted_version)][condition]
            self.board = PayoffReader.from_memory(law, word)
        if self.board is not None:
            self.board.begin_episode(training=False)
        self.initial = None if self.board is None else self.board.export_memory()

    @property
    def score(self):
        return None if self.board is None else self.board.score

    def read(self, obs, probe=None):
        return current_only(obs) if self.board is None else _physical_bit(self.board, obs, probe)

    def proposed(self, obs):
        if self.board is None:
            return current_only(obs)
        return _physical_bit(copy(self.board), obs)

    def advance(self, transition):
        if self.board is not None:
            self.board.after_turn(transition.observation, transition.bit, transition.outgoing_slot, transition.energy_after)

    def check(self):
        if self.board is not None and self.board.export_memory() != self.initial:
            raise RuntimeError("Held-out play changed a locked physical memory word.")


def _view(obs):
    return None if obs is None else {**asdict(obs), "slots": list(obs.slots)}


def _public(transition, role):
    return {"observation": _view(transition.observation), "arrival_cue": role, "bit": transition.bit,
            "outgoing_slot": transition.outgoing_slot, "energy_after": transition.energy_after,
            "next_observation": _view(transition.next_observation)}


def _hash_step(hasher, public):
    hasher.update(json.dumps(public, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii"))
    hasher.update(b"\n")


def _access(event):
    if not event["food_before"]:
        return "empty"
    if event["eligible"] and event["approach"] != event["accepted_approach"]:
        return "closed"
    return "open"


def _tally(tally, prefix, role, obs, action, access):
    if role is None or not obs.feeder or len(obs.slots) != 3:
        return
    stem = f"{prefix}_{role}_"
    tally[stem + "seen"] += 1
    if current_only(obs):
        tally[stem + "eligible"] += 1
        tally[stem + "on"] += action
        tally[stem + ("on_" if action else "off_") + access] += 1


def _advance_cue(transition, role):
    if transition.outgoing_slot is None:
        return role
    cue = derive_clue(transition.observation, transition.outgoing_slot)
    return None if cue is None else ROLES[cue]


def _check_route(board, role, private):
    expected = None if private["approach"] is None else ROLES[private["approach"]]
    if role != expected or (board is not None and board.route_cue != role):
        raise RuntimeError("The public approach reconstruction disagrees with the game or reader.")


def play_episode(world, *, tape, version, mirror, arm, weights, capture=False):
    game = ReversalGame(world, tape=tape, version=version, mirror=mirror)
    seat = Seat(arm, world.law, version, weights)
    initial = game.snapshot()
    tally = Counter()
    role = None
    public_hash = sha256()
    trace = []
    while not game.done:
        obs = game.observe()
        bit = seat.read(obs)
        if (role is None or not obs.feeder or len(obs.slots) != 3) and bit != current_only(obs):
            raise RuntimeError("The fixed reader changed an outside-cue action.")
        action_word = None if seat.board is None else seat.board.action_word
        transition = game.step(bit)
        private = game.last_event
        _check_route(seat.board, role, private)
        access = _access(private)
        if bool(private["consumed"]) != bool(bit and access == "open") or private["denied"] != bool(bit and access == "closed"):
            raise RuntimeError("The real action and available ration disagree with the receipt ledger.")
        _tally(tally, "natural", role, obs, bit, access)
        tally["empty_eats"] += bool(bit and access == "empty")
        tally["denied_eats"] += private["denied"]
        tally["open_passes"] += bool(not bit and access == "open")
        tally["closed_stock_passes"] += bool(not bit and access == "closed")
        tally["refusals"] += private["action"] == "refused"
        public = _public(transition, role)
        _hash_step(public_hash, public)
        if capture:
            trace.append({"public": public, "physical_action_word": action_word, "spectator": private})
        seat.advance(transition)
        role = _advance_cue(transition, role)
    final = game.snapshot()
    seat.check()
    turns, meals, wasted = final["turns"], final["meals"], final["wasted"]
    stock = (game.turn_bound - initial["energy"]) // 4
    if (turns != initial["energy"] + 4 * meals - wasted or final["energy"] != 0
            or stock != meals + len(final["available"])):
        raise RuntimeError("The terminal energy or ration ledger does not balance.")
    record = {
        "arm": arm, "mounted_version": seat.mounted_version, "score": seat.score,
        "turns": turns, "meals": meals, "wasted": wasted, "energy": final["energy"], "reason": "death",
        "stock_allocated": stock, "stock_remaining": len(final["available"]),
        "public_history_sha256": public_hash.hexdigest(),
        **{field: tally[field] for field in ("empty_eats", "denied_eats", "open_passes", "closed_stock_passes", "refusals", *NATURAL_FIELDS)},
    }
    if capture:
        record.update(start=initial, end=final, decisions=trace,
                      initial_holdings=[list(row) for row in world.stages[0].holdings], mounted_word=seat.initial)
    return record


def play_common_path(world, *, tape, version, mirror, weights, capture=False):
    """Run one current-only game and read every policy on that same public path."""
    game = ReversalGame(world, tape=tape, version=version, mirror=mirror)
    seats = {arm: Seat(arm, world.law, version, weights) for arm in READERS}
    tallies = {arm: Counter() for arm in READERS}
    role = None
    digest = sha256()
    trace = []
    while not game.done:
        obs = game.observe()
        bits = {arm: seat.proposed(obs) for arm, seat in seats.items()}
        actual = bits["current"]
        for arm, seat in seats.items():
            if seat.read(obs, probe=None if bits[arm] == actual else actual) != actual:
                raise RuntimeError("A common-path shadow did not issue the actual action.")
        transition = game.step(actual)
        private = game.last_event
        _check_route(None, role, private)
        access = _access(private)
        for arm, seat in seats.items():
            bit = bits[arm]
            if seat.board is not None and seat.board.route_cue != role:
                raise RuntimeError("A common-path reader lost its issued route receipt.")
            tally = tallies[arm]
            _tally(tally, "common", role, obs, bit, access)
            if role is not None and obs.feeder and len(obs.slots) == 3 and current_only(obs) and bit != bits["outcome"]:
                stem = f"common_{role}_"
                outcome = bits["outcome"]
                tally[stem + ("outcome_on_other_off" if outcome else "outcome_off_other_on")] += 1
                correct = outcome == (access == "open")
                tally[stem + ("outcome_correct_change" if correct else "outcome_incorrect_change")] += 1
            seat.advance(transition)
        public = _public(transition, role)
        _hash_step(digest, public)
        if capture:
            trace.append({"public": public, "proposed_bits": bits, "spectator": private})
        role = _advance_cue(transition, role)
    final = game.snapshot()
    for seat in seats.values():
        seat.check()
    if final["energy"] or final["turns"] != 6 + 4 * final["meals"] - final["wasted"]:
        raise RuntimeError("Common-path death disagrees with its energy ledger.")
    result = {
        "common_turns": final["turns"], "common_public_history_sha256": digest.hexdigest(),
        "by_arm": {arm: {field: tallies[arm][field] for field in COMMON_FIELDS} for arm in READERS},
    }
    if capture:
        result.update(decisions=trace, end=final)
    return result


def _case(start, world, version, mirror, replicate, weights):
    tape = movement_tape("heldout", start.source_key, replicate)
    identity = {**asdict(start), "law": world.law, "version": version, "mirror": int(mirror),
                "replicate": replicate, "tape": tape, "growth_stop": world.stop,
                "first_funded": int(bool(world.attempts[0].births))}
    common = play_common_path(world, tape=tape, version=version, mirror=mirror, weights=weights)
    rows = {}
    for arm in READERS:
        result = play_episode(world, tape=tape, version=version, mirror=mirror, arm=arm, weights=weights)
        rows[arm] = {**identity, **result, **common["by_arm"][arm],
                     "common_turns": common["common_turns"],
                     "common_public_history_sha256": common["common_public_history_sha256"]}
    if (rows["current"]["turns"] != common["common_turns"]
            or rows["current"]["public_history_sha256"] != common["common_public_history_sha256"]
            or len({row["stock_allocated"] for row in rows.values()}) != 1):
        raise RuntimeError("The paired current path or initial stock cannot be reconstructed.")
    return rows


def _outcome_delta(block, control):
    comparators = ("fixed_A", "fixed_B") if control == "balanced_fixed" else (control,)
    delta = tuple(block["outcome"][key] - fmean(block[arm][key] for arm in comparators)
                  for key in ("turns", "meals", "wasted"))
    if delta[0] != 4 * delta[1] - delta[2]:
        raise RuntimeError("A paired lifetime effect disagrees with the energy accounts.")
    return delta


def _founder_rows(grouped, law, group, control, alias=None):
    rows = []
    for blocks in grouped:
        first = blocks[0]["outcome"]
        turns, meals, wasted = zip(*(_outcome_delta(block, control if alias is None else alias) for block in blocks))
        rows.append({
            "law": law, "group": group, "control": control, "source_key": first["source_key"],
            "seed": first["seed"], "first_funded": first["first_funded"], "growth_stop": first["growth_stop"],
            "pairs": len(turns), "mean_delta_turns": fmean(turns), "mean_delta_meals": fmean(meals),
            "mean_delta_wasted": fmean(wasted), "wins": sum(t > 0 for t in turns),
            "ties": turns.count(0), "losses": sum(t < 0 for t in turns),
        })
    return rows


def _stratum(rows):
    values = [row["mean_delta_turns"] for row in rows]
    return {
        "founders": len(rows), "mean_delta_turns": fmean(values) if values else None,
        "founders_positive": sum(value > 0 for value in values),
        "founders_tied": values.count(0), "founders_negative": sum(value < 0 for value in values),
    }


def _paired(rows, seed, best_choices=None):
    scores = [row["mean_delta_turns"] for row in rows]
    rng = Random(seed)
    if best_choices is None:
        estimates = [fmean(rng.choices(scores, k=len(scores))) for _ in range(BOOTSTRAP_DRAWS)]
    else:
        # The better fixed policy has the smaller outcome-minus-fixed gap.
        choices = list(zip(*(tuple(r["mean_delta_turns"] for r in option) for option in best_choices), strict=True))
        estimates = [min(map(fmean, zip(*rng.choices(choices, k=len(choices))))) for _ in range(BOOTSTRAP_DRAWS)]
    cuts = quantiles(estimates, n=40, method="inclusive")
    return {
        "paired_founders": len(rows), "paired_games": sum(row["pairs"] for row in rows),
        "mean_delta_turns": fmean(scores), "mean_delta_meals": fmean(row["mean_delta_meals"] for row in rows),
        "mean_delta_wasted": fmean(row["mean_delta_wasted"] for row in rows),
        "founder_bootstrap_95_percent_interval": [cuts[0], cuts[-1]], "bootstrap_seed": seed,
        **{key: sum(row[key] for row in rows) for key in ("wins", "ties", "losses")},
        "funding": {"first_funded": _stratum([r for r in rows if r["first_funded"]]),
                    "no_first_birth": _stratum([r for r in rows if not r["first_funded"]])},
        "founder_effects": _stratum(rows),
    }


def _arm_scores(blocks, arm):
    rows = [block[arm] for block in blocks]
    totals = {key: sum(row[key] for row in rows) for key in (*NATURAL_FIELDS, *COMMON_FIELDS)}
    return {
        "episodes": len(rows), "mean_turns": fmean(row["turns"] for row in rows),
        "score_words_decoded": sorted({row["score"] for row in rows}, key=lambda x: -100 if x is None else x),
        "energy_stock_and_action_means": {key: fmean(row[key] for row in rows) for key in (
            "meals", "wasted", "stock_allocated", "stock_remaining", "empty_eats", "denied_eats",
            "open_passes", "closed_stock_passes", "refusals")},
        "identical_natural_history_to_outcome": sum(row["public_history_sha256"] == block["outcome"]["public_history_sha256"]
                                                    for row, block in zip(rows, blocks, strict=True)),
        "natural_exposure": {role: {key: totals[f"natural_{role}_{key}"] for key in EXPOSURE} for role in ROLES},
        "common_exposure": {role: {key: totals[f"common_{role}_{key}"] for key in (*EXPOSURE, *CHANGES)} for role in ROLES},
    }


def _summarize_group(grouped, law, group):
    blocks = [block for founder in grouped for block in founder]
    arms = {arm: _arm_scores(blocks, arm) for arm in READERS}
    for role in ROLES:
        if len({data["common_exposure"][role]["eligible"] for data in arms.values()}) != 1:
            raise RuntimeError("Common-path policies received different observation opportunities.")
    rows = {control: _founder_rows(grouped, law, group, control) for control in CONTROLS}
    stats = {control: _paired(data, derive_seed("survival-bootstrap", law, group, control))
             for control, data in rows.items()}
    best = None
    if group == "pooled":
        fixed = ("fixed_A", "fixed_B")
        best = max(fixed, key=lambda arm: arms[arm]["mean_turns"])
        rows["best_constant"] = _founder_rows(grouped, law, group, "best_constant", alias=best)
        stats["best_constant"] = _paired(rows["best_constant"], derive_seed("survival-bootstrap", law, group, "best_constant"),
                                         best_choices=tuple(rows[arm] for arm in fixed))
    swaps = arms["crossed"]["common_exposure"]
    inverted = {role: data["outcome_on_other_off"] + data["outcome_off_other_on"] for role, data in swaps.items()}
    return {"arms": arms, "outcome_minus": stats, "best_pooled_constant": best,
            "crossed_inversions": inverted,
            "crossed_inverts_all_observed_eligible": all(0 < inverted[role] == swaps[role]["eligible"] for role in ROLES)}, [
                r for data in rows.values() for r in data
            ]


def _write_csv(path, fields, rows):
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(bank_path, weights_path, pinned, output_dir):
    from training import load_words

    start_time = perf_counter()
    weights, digest = load_words(weights_path, pinned)
    partitions, bank_digest = load_bank(bank_path)
    if digest != pinned or weights["input_sha256"]["source_bank.json"] != bank_digest:
        raise ValueError("The held-out source bank and fitted words must share the exact training lock.")
    starts = partitions["heldout"]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    artifacts = {name: output / f"survival_{name}.{extension}" for name, extension in (
        ("episodes", "csv"), ("founders", "csv"), ("results", "json"))}
    if any(path.exists() for path in artifacts.values()):
        raise FileExistsError(f"Held-out survival files already exist in {output}.")

    records = {}
    growth = {law: Counter(starts=0, first_funded=0, stalled=0, closed=0, rations=0) for law in LAWS}
    paired_growth = 0
    for index, start in enumerate(starts, 1):
        worlds = sample_pair(start, "heldout")
        p, n = (worlds[law] for law in LAWS)
        paired_growth += (p.stages, p.attempts, p.births, p.stop) == (n.stages, n.attempts, n.births, n.stop)
        for law, world in worlds.items():
            growth[law].update(starts=1, first_funded=bool(world.attempts[0].births),
                               stalled=world.stop == "stall", closed=world.stop == "closed", rations=len(world.births))
            for replicate in range(TAPES):
                stock = set()
                for version, mirror in GROUPS["pooled"]:
                    block = _case(start, world, version, mirror, replicate, weights)
                    stock.add(block["current"]["stock_allocated"])
                    records[law, start.source_key, replicate, version, mirror] = block
                if len(stock) != 1:
                    raise RuntimeError("Paired versions and anonymous codes received different stock budgets.")
        if index % 8 == 0 or index == len(starts):
            print(f"Played every natural and common-path case for {index}/{len(starts)} held-out founders.", flush=True)

    expected = len(starts) * len(LAWS) * TAPES * len(GROUPS["pooled"])
    if len(records) != expected or any(len(block) != len(READERS) for block in records.values()):
        raise RuntimeError("Missing or duplicate paired cases in the held-out ledger.")
    per_law, all_founder_rows = {}, []
    for law in LAWS:
        summaries = {}
        for group, cells in GROUPS.items():
            grouped = [[records[law, start.source_key, replicate, version, mirror]
                        for replicate in range(TAPES) for version, mirror in cells] for start in starts]
            summaries[group], rows = _summarize_group(grouped, law, group)
            all_founder_rows.extend(rows)
        per_law[law] = summaries
    law_agreement = {arm: sum(records["parity", s.source_key, rep, v, m][arm]["public_history_sha256"]
                              == records["nae", s.source_key, rep, v, m][arm]["public_history_sha256"]
                              for s in starts for rep in range(TAPES) for v, m in GROUPS["pooled"]) for arm in READERS}
    gates = {}
    for law, summaries in per_law.items():
        def positive(group, control):
            return summaries[group]["outcome_minus"][control]["founder_bootstrap_95_percent_interval"][0] > 0

        gates[law] = {"pooled_gain_over_count": positive("pooled", "count"),
                      "pooled_gain_over_current": positive("pooled", "current"),
                      "gain_over_count_in_each_version": all(positive(f"version_{v}", "count") for v in (0, 1)),
                      "crossed_actions_invert": summaries["pooled"]["crossed_inverts_all_observed_eligible"]}
    if sha256(Path(weights_path).read_bytes()).hexdigest() != digest:
        raise RuntimeError("The fitted words changed during the held-out run.")
    _write_csv(artifacts["episodes"], EPISODE_FIELDS, (row for block in records.values() for row in block.values()))
    _write_csv(artifacts["founders"], FOUNDER_FIELDS, all_founder_rows)
    results = {
        "schema": "feeder-payoff-reversal-survival-v1", "weights_sha256": digest, "bank_sha256": bank_digest,
        "heldout_founders": len(starts), "tapes_per_founder": TAPES, "bootstrap_draws": BOOTSTRAP_DRAWS,
        "paired_cases": len(records), "natural_episodes": len(records) * len(READERS),
        "common_episodes": len(records), "censored_episodes": 0, "frozen_memories_verified": True,
        "growth_by_law": {law: dict(c) for law, c in growth.items()}, "identical_paired_growth": paired_growth,
        "between_laws_identical_public_histories": law_agreement, "by_law": per_law, "gates": gates,
        "public_hash": "SHA-256 of the ordered compact sorted ASCII JSON transition lines, including final newlines",
        "elapsed_seconds": perf_counter() - start_time,
    }
    with artifacts["results"].open("x", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(f"Saved {results['natural_episodes']} deaths, {len(records)} common paths and {len(all_founder_rows)} founder effects.",
          flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", default=BANK_PATH, type=Path)
    parser.add_argument("--weights", default=HERE / "learned_words.json", type=Path)
    parser.add_argument("--weights-sha256", required=True)
    parser.add_argument("--output-dir", default=HERE, type=Path)
    args = parser.parse_args()
    run(args.bank, args.weights, args.weights_sha256, args.output_dir)


if __name__ == "__main__":
    main()
