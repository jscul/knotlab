"""Reconstruct frozen feeder decisions and test the learned-word interventions."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from hashlib import blake2s, sha256
import json
from pathlib import Path

from paired_game import Observation, ReversalGame, Transition
from feeder_game import CAPACITY, RATION_GAIN, action_rngs
from source_bank import BANK_PATH, LAWS, load_bank, movement_tape, sample_pair
from reader import ACTION_MARK, LEARNED_MASK, NAMES, OWNERS, STARS, PayoffReader


HERE = Path(__file__).resolve().parent
VERSIONS = (0, 1)
MIRRORS = (False, True)
FIRST_TURN, LAST_TURN = 2, 6
MECHANISM_TAPES = 64
ARMS = ("original", "sham", "transfer", "erase", "restore", "count", "shuffled")
CUE = ("A", "B")
NEUTRAL = {"schema": "feeder-payoff-difference-v1", "bits": 32, "word": "10" * 32, "score": 0}
SUPPORT = [(sum(1 << n for n in marks), len(marks)) for marks in STARS.values()]


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def public_observation(obs):
    if obs is None:
        return None
    return {"feeder": obs.feeder, "energy": obs.energy, "previous": obs.previous, "slots": list(obs.slots)}


def clue_after(obs, slot, previous):
    if slot is None:
        return previous
    return slot % 2 if (slot ^ 1) in obs.slots else None


def opening_at(before, *, exception=None):
    if exception is None:
        key = f"{before['seed']}|{before['tape']}|{before['holder']}".encode("ascii")
        tag = blake2s(key, digest_size=1, person=b"FDRGATE1").digest()[0]
        exception = tag % 4 == 0
    return before["version"] ^ int(exception)


def ordinary_bit(obs):
    return int(obs.feeder and obs.previous != "eat")


@dataclass(frozen=True, slots=True)
class Step:
    before: dict
    receipt: Transition
    event: dict

    def public(self):
        row = self.receipt
        return {"observation": public_observation(row.observation), "bit": row.bit,
                "outgoing_slot": row.outgoing_slot, "energy_after": row.energy_after,
                "next_observation": public_observation(row.next_observation)}


def take_step(game, world, bit, *, exception=None):
    """Recompute the cost, availability, opening and actual shared distinction."""
    obs = game.observe()
    before = game.snapshot()
    turn = before["turns"] + 1
    at = f"{before['law']} seed {before['seed']} tape {before['tape']} turn {turn}"
    source = before["holder"]
    stock = source in before["available"]
    clue = before["approach"]
    access_gate = obs.feeder and len(obs.slots) == 3 and clue is not None
    accepted = opening_at(before, exception=exception) if access_gate else None
    denied = bool(bit and stock and access_gate and clue != accepted)
    paid = bool(bit and stock and not denied)
    energy = min(CAPACITY, obs.energy - 1 + RATION_GAIN * paid)

    receipt = game.step(bit)
    event = game.last_event
    paid_fields = (stock, denied, paid, access_gate, accepted, clue, before["arrival_slot"])
    actual_fields = tuple(event[name] for name in ("food_before", "denied", "consumed", "eligible",
                                                   "accepted_approach", "approach", "arrival_slot"))
    require(paid_fields == actual_fields, f"Ration stock or opening differs at {at}")
    require(event["rations_remaining"] == len(before["available"]) - paid, f"Ration accounting differs at {at}")
    require(event["turn"] == turn and event["bit"] == receipt.bit == bit and event["holder_before"] == source,
            f"Applied action is not bound to the frozen game at {at}")
    require(obs == receipt.observation and receipt.energy_after == event["energy_after"] == energy and
            obs.energy == event["energy_before"] and event["terminal"] == (energy == 0) == game.done,
            f"Public receipt or physical energy differs at {at}")

    if bit == 0 and obs.slots:
        physical = action_rngs(before["tape"], turn)[1].choice(obs.slots)
        shown = physical ^ 1 if before["mirror"] and (physical ^ 1) in obs.slots else physical
        distinction, target = before["ports"][shown]
        require(event["physical_slot"] == physical and receipt.outgoing_slot == event["slot"] == shown,
                f"Actual control and displayed control disagree at {at}")
        require((event["action"], event["distinction"], event["holder_after"]) == ("move", distinction, target),
                f"Actuator did not move on its actual shared distinction at {at}")
        owners = {h for h, marks in enumerate(world.stages[before["formation"]].holdings) if distinction in marks}
        require(owners == {source, target} and source != target, f"Move has the wrong holders at {at}")
    else:
        require(event["action"] == ("eat" if bit else "refused") and event["holder_after"] == source and
                event["slot"] is None and event["physical_slot"] is None and event["distinction"] is None,
                f"Stationary action moved the cursor at {at}")
    post = game.snapshot()
    next_slot = receipt.outgoing_slot if receipt.outgoing_slot is not None else before["arrival_slot"]
    require(post["approach"] == clue_after(obs, receipt.outgoing_slot, clue) and post["arrival_slot"] == next_slot,
            f"Public arrival receipt disagrees with the game at {at}")
    return Step(before, receipt, event)


@dataclass(frozen=True, slots=True)
class Visit:
    observation: Observation
    game: ReversalGame
    prefix: tuple[Step, ...]
    approach: int

    def public_key(self):
        return public_observation(self.observation), [row.public() for row in self.prefix]


def walk(world, tape, version, mirror, *, stop=LAST_TURN):
    """Enumerate public-eligible decisions without making a fitted read or a bite."""
    game = ReversalGame(world, tape=tape, version=version, mirror=mirror)
    steps, visits, counts = [], {}, Counter(games=1)
    approach = None
    for turn in range(1, stop + 1):
        if game.done:
            counts["missing_after_death"] += int(turn >= FIRST_TURN)
            continue
        obs = game.observe()
        state = game.snapshot()
        if turn >= FIRST_TURN:
            counts["reached"] += 1
            counts["prior_refusal"] += int(obs.previous == "refused")
            if not obs.feeder:
                counts["nonfeeder"] += 1
            elif len(obs.slots) != 3:
                counts["feeder_other_menu"] += 1
            elif approach is None:
                counts["three_exit_missing_cue"] += 1
            elif not ordinary_bit(obs):
                counts["three_exit_ordinary_pass"] += 1
            else:
                require(approach == state["approach"], "Game and public route disagree on encounter eligibility")
                visits[turn] = Visit(obs, game.clone(), tuple(steps), approach)
                counts["eligible"] += 1
                counts[f"eligible_{CUE[approach]}"] += 1
                counts["eligible_stock_empty"] += int(state["holder"] not in state["available"])
        row = take_step(game, world, 0)
        steps.append(row)
        approach = clue_after(obs, row.receipt.outgoing_slot, approach)
        growth = row.event["growth"]
        if growth:
            counts[f"growth_{growth['status']}"] += 1
        counts["refused_actions"] += int(row.event["action"] == "refused")
    counts["died"] += int(game.done)
    counts["no_eligible_game"] += int(not visits)
    return visits, steps, counts


def learned_score(export):
    require(export["schema"] == NEUTRAL["schema"] and export["bits"] == 32, "Wrong learned memory type")
    word = export["word"]
    pairs = [word[i:i + 2] for i in range(0, len(word), 2)]
    require(len(word) == 64 and all(pair in ("10", "01") for pair in pairs), "Invalid two-mark score word")
    unsigned = sum(1 << i for i, pair in enumerate(pairs) if pair == "01")
    score = unsigned - (1 << 32) if unsigned >> 31 else unsigned
    require(score == export["score"], "Signed score differs from the transported pairs")
    return score


def expected_action(obs, approach, score):
    eligible = ordinary_bit(obs) and len(obs.slots) == 3 and approach is not None
    if eligible and score:
        return int(approach == int(score < 0))
    return ordinary_bit(obs)


def admitted(raw, law):
    counts = [(raw & mask).bit_count() for mask, _ in SUPPORT]
    if law == "parity":
        return all(count % 2 == 0 for count in counts)
    return all(0 < count < size for count, (_, size) in zip(counts, SUPPORT, strict=True))


def verify_offers(before, offers, after, law, *, only_memory=False):
    """Check literal co-held exchange, support, guard and output for recorded offers."""
    raw = before
    require(admitted(raw, law), "Starting word violates its declared law")
    for entry in offers:
        a, b = entry["operands"]
        holder = entry["holder"]
        mask = (1 << a) | (1 << b)
        require(entry["before"] == raw and a != b and holder in OWNERS[a] and OWNERS[a] == OWNERS[b],
                "Discontinuous or differently held operands")
        require(not only_memory or mask & ~LEARNED_MASK == 0, "An intervention touched a protected mark")
        guards = entry["guard"]
        require(all(n not in (a, b) and holder in OWNERS[n] and value in (0, 1) for n, value in guards),
                "An offer consulted a changing or differently held guard name")
        enabled = all(((raw >> n) & 1) == value for n, value in guards)
        unequal = ((raw >> a) ^ (raw >> b)) & 1
        expected = raw ^ mask if enabled and unequal else raw
        status = "guard refused" if not enabled else "changed" if unequal else "equal operands"
        require(entry["status"] == status and entry["after"] == expected and admitted(expected, law),
                "The logged offer differs from its physical rule")
        raw = expected
    require(raw == after, "The offer sequence ended at a different marking")


def prepare(visit, export, law, *, detail):
    """Establish only the actual public pass receipts before preparing to read."""
    board = PayoffReader.from_memory(law, export).begin_episode(training=False)
    require(board.export_memory() == export and ACTION_MARK == 6, "Wrong fitted word or action mark")
    route = None
    audit = []
    for row in visit.prefix:
        receipt = row.receipt
        obs = receipt.observation
        require(board.route_cue == (None if route is None else CUE[route]), "Wrong route before a public pass")
        raw = board.word
        emitted = board.decide(obs, probe_bit=0)
        require(emitted == receipt.bit == (board.word >> 6) & 1 == 0, "Supplied pass missed the native action mark")
        gain = board.after_turn(obs, emitted, receipt.outgoing_slot, receipt.energy_after)
        route = clue_after(obs, receipt.outgoing_slot, route)
        require(gain["next_route_cue"] == board.route_cue == (None if route is None else CUE[route]) and
                board.export_memory() == export and not gain["credited"], "A pass receipt changed the wrong state")
        if detail:
            audit.append({"turn": row.event["turn"], "public": row.public(), "game": row.event,
                          "physical_before": raw, "physical_after": board.word, "receipt": gain})
    board.checkpoint(visit.observation)
    require(route == visit.approach and board.action_word == "100" and not board.training and admitted(board.word, law),
            "The fixed checkpoint is missing its ready action or arrived cue")
    return board, audit


def intervention_copy(base, arm, recipient, donor, *, detail):
    board = deepcopy(base)
    expected = recipient["outcome"]
    offers = []
    counterpart = None
    match arm:
        case "original":
            pass
        case "sham":
            offers = board.sham(detail=detail)
        case "transfer":
            other = deepcopy(base)
            donor_start = other.word
            mounted = other.restore_learned(donor["outcome"], detail=detail)
            require(other.nonmemory_snapshot() == base.nonmemory_snapshot(), "Donor mounting changed recipient context")
            other_before = other.word
            both = board.swap_learned(other, detail=detail)
            expected = donor["outcome"]
            require(other.export_memory() == recipient["outcome"] and other.nonmemory_snapshot() == base.nonmemory_snapshot(),
                    "Reciprocal transfer changed the wrong donor state")
            if detail:
                offers, donor_offers = both
                verify_offers(donor_start, mounted, other_before, base.law, only_memory=True)
                verify_offers(other_before, donor_offers, other.word, base.law, only_memory=True)
                counterpart = {"before": other_before, "after": other.word, "offers": donor_offers,
                               "mount_from": donor_start, "mount_offers": mounted}
        case "erase" | "restore":
            raw = board.clear_learned(detail=detail)
            token, offers = raw if detail else (raw, None)
            require(token == recipient["outcome"] and board.export_memory() == NEUTRAL,
                    "Erasure failed to export the fitted word or set physical neutral")
            expected = NEUTRAL
            if arm == "restore":
                restored = board.restore_learned(token, detail=detail)
                expected = token
                if detail:
                    offers.extend(restored)
        case "count" | "shuffled":
            expected = recipient[arm]
            offers = board.restore_learned(expected, detail=detail)
        case _:
            raise ValueError(f"Unknown arm {arm}")

    require(board.nonmemory_snapshot() == base.nonmemory_snapshot() and board.action_word == "100" and
            board.export_memory() == expected and admitted(board.word, base.law),
            f"{arm} changed a protected field, unset the blank action, or mounted the wrong word")
    if detail:
        verify_offers(base.word, offers, board.word, base.law, only_memory=True)
    if arm in ("original", "sham", "restore"):
        require(board.word == base.word, f"{arm} did not restore the whole prepared physical word")
    return board, expected, offers, counterpart


def read_all(visit, law, recipient, donor, *, detail=False):
    base, preparation = prepare(visit, recipient["outcome"], law, detail=detail)
    options = {}
    for arm in ARMS:
        board, export, offers, counterpart = intervention_copy(base, arm, recipient, donor, detail=detail)
        held = board.word
        read = board.read_prepared(detail=detail)
        bit, trace = read if detail else (read, None)
        require(bit == (board.word >> 6) & 1 and board.action_word == ("001" if bit else "010") and
                board.export_memory() == export and admitted(board.word, law), "Wrong fixed physical readout")
        expected = expected_action(visit.observation, visit.approach, learned_score(export))
        options[arm] = {"bit": bit, "expected_bit": expected, "score": export["score"]}
        if detail:
            verify_offers(held, trace, board.word, law)
            options[arm].update(marking_before_read=held, marking_after_read=board.word, learned_word=export,
                                intervention_offers=offers, read_offers=trace, counterpart=counterpart)
    return {"options": options, "prepared_nonmemory": base.nonmemory_snapshot(),
            **({"prepared": base.snapshot(), "prefix": preparation} if detail else {})}


def apply_all(visit, readings, world, *, detail=False):
    """Score each armed clone only after all reads held at this decision finish."""
    frozen = visit.game.snapshot()
    proof = take_step(visit.game.clone(), world, 1)
    stock, can_pay = proof.event["food_before"], proof.event["consumed"]
    for arm, read in readings["options"].items():
        step = take_step(visit.game.clone(), world, read["bit"])
        read.update(consumed=step.event["consumed"], denied=step.event["denied"], energy_after=step.event["energy_after"])
        if detail:
            read["actual"] = step.event
    require(visit.game.snapshot() == frozen, "A read advanced or rewrote its frozen recipient game")
    readings.update(stock=stock, would_pay=can_pay, accepted=CUE[proof.event["accepted_approach"]],
                    **({"frozen_game": frozen, "would_be_bite": proof.event} if detail else {}))
    return readings


def pack(value):
    return json.loads(json.dumps(value))


def locked_weights(path, expected_sha, bank_path):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == expected_sha, "Physical words differ from the released hash")
    model = json.loads(raw)
    require(model["schema"] == "feeder-payoff-trained-words-v1", "Unknown released support for learned words")
    folds, bank_sha = load_bank(bank_path)
    for name, expected in model["input_sha256"].items():
        candidate = bank_path if name == bank_path.name else HERE / name
        require(candidate.is_file() and sha256(candidate.read_bytes()).hexdigest() == expected,
                f"A sealed training input differs for {name}")
    names = [start.source_key for starts in folds.values() for start in starts]
    require(len(names) == len(set(names)), "A founder structure leaks across folds")
    for law in LAWS:
        for version in VERSIONS:
            for policy in ("outcome", "count", "shuffled"):
                learned_score(model["policies"][law][str(version)][policy])
    return model, folds, bank_sha


def select_replay(starts):
    """Select by public pass eligibility before reading the learned words."""
    earliest = {}
    for start in starts:
        worlds = sample_pair(start, "mechanism")
        found = {}
        for replicate in range(MECHANISM_TAPES):
            tape = movement_tape("mechanism", start.source_key, replicate)
            groups = [walk(worlds[law], tape, version, False)[0] for law in LAWS for version in VERSIONS]
            turns = sorted(set.intersection(*(set(group) for group in groups)))
            for turn in turns:
                visits = [group[turn] for group in groups]
                first = visits[0]
                if all(v.approach == first.approach and v.public_key() == first.public_key() for v in visits[1:]):
                    cue = CUE[first.approach]
                    item = {"cue": cue, "seed": start.seed, "source_key": start.source_key,
                            "replicate": replicate, "tape": tape, "turn": turn}
                    found.setdefault(cue, item)
                    earliest.setdefault(cue, item)
            if len(found) == len(CUE):
                return {"shared_seed": True, "cases": [found[cue] for cue in CUE]}
    return {"shared_seed": False, "cases": [earliest[cue] for cue in CUE if cue in earliest]}


def physical_route(steps):
    return [(row.event["holder_before"], row.event["holder_after"], row.event["distinction"],
             row.event["physical_slot"], row.event["energy_after"]) for row in steps]


def update_recipient(counts, row):
    counts.update(recipients=1, stock=int(row["stock"]), would_pay=int(row["would_pay"]))
    for arm, action in row["options"].items():
        counts[f"{arm}_on"] += action["bit"]
        counts[f"{arm}_correct_for_payment"] += int(action["bit"] == row["would_pay"])
        counts[f"{arm}_consumed"] += action["consumed"]
        counts[f"{arm}_denied"] += action["denied"]
        counts[f"{arm}_empty_attempt"] += int(action["bit"] and not row["stock"])
        counts[f"{arm}_read_mismatch"] += int(action["bit"] != action["expected_bit"])
    original = row["options"]["original"]["bit"]
    counts["sham_unchanged"] += int(row["options"]["sham"]["bit"] == original)
    counts["restored_original"] += int(row["options"]["restore"]["bit"] == original)
    counts["erased_to_ordinary"] += int(row["options"]["erase"]["bit"] == 1)
    counts["transfer_changes_action"] += int(row["options"]["transfer"]["bit"] != original)


def bits_at(rows, arm):
    return tuple(row["options"][arm]["bit"] for row in rows)


def update_pair(counts, states, rows):
    if len(rows) != 2:
        counts["unmatched_recipient_turns"] += len(rows)
        return
    left, right = states
    counts["both_eligible"] += 1
    public = left.approach == right.approach and left.public_key() == right.public_key()
    same_board = rows[0]["prepared_nonmemory"] == rows[1]["prepared_nonmemory"]
    counts["same_complete_public"] += int(public)
    counts["same_prepared_nonmemory"] += int(same_board)
    if not public or not same_board:
        counts["not_exactly_matched"] += 1
        return
    counts["exact_pairs"] += 1
    first, crossed = bits_at(rows, "original"), bits_at(rows, "transfer")
    both_flipped = first[0] != first[1] and crossed == first[::-1]
    correct = first == tuple(int(r["would_pay"]) for r in rows)
    sham = bits_at(rows, "sham") == first
    restored = bits_at(rows, "restore") == first
    erased = bits_at(rows, "erase") == (1, 1)
    counts.update(original_opposite=int(first[0] != first[1]), original_correct_both=int(correct),
                  swap_both_ways=int(both_flipped), both_correct_reciprocal=int(correct and both_flipped),
                  sham_unchanged_both=int(sham), restore_original_both=int(restored), neutral_both=int(erased),
                  fully_controlled_correct_reciprocal=int(correct and both_flipped and sham and restored and erased))
    key = f"original_{first[0]}{first[1]}_transfer_{crossed[0]}{crossed[1]}"
    counts[key] += 1


def update_mirror(counts, base_visit, mirror_visit, base, mirrored):
    counts["with_counterpart"] += 1
    counts["cue_complemented"] += int(base_visit.approach == 1 - mirror_visit.approach)
    counts["opening_complemented"] += int(base["accepted"] != mirrored["accepted"])
    counts["same_possible_payment"] += int(base["would_pay"] == mirrored["would_pay"])
    first = base["options"]["original"]
    other = mirrored["options"]["original"]
    counts["same_fitted_action"] += int(first["bit"] == other["bit"])
    counts["same_actual_consequences"] += int((first["consumed"], first["denied"], first["energy_after"]) ==
                                              (other["consumed"], other["denied"], other["energy_after"]))


def witness_case(world, start, tape, replicate, turn, model):
    result = []
    pending = []
    for mirror in MIRRORS:
        for version in VERSIONS:
            visits, _, _ = walk(world, tape, version, mirror, stop=turn)
            require(turn in visits, "Prospectively selected arrival is no longer eligible")
            state = visits[turn]
            words = model["policies"][world.law]
            reads = read_all(state, world.law, words[str(version)], words[str(1 - version)], detail=True)
            pending.append((mirror, version, state, reads))
    for mirror, version, state, reads in pending:
        result.append({"law": world.law, "seed": start.seed, "source_key": start.source_key, "tape": tape,
                       "replicate": replicate, "turn": turn, "version": version, "mirror": mirror,
                       "cue": CUE[state.approach], "observation": public_observation(state.observation),
                       **apply_all(state, reads, world, detail=True)})
    return pack(result)


def run(model, starts, *, weights_sha, bank_sha):
    choice = select_replay(starts)
    start_by_seed = {start.seed: start for start in starts}
    witnesses = []
    margin, recipients, paired, mirrored = (defaultdict(Counter) for _ in range(4))
    rows = []
    for spec in choice["cases"]:
        start = start_by_seed[spec["seed"]]
        worlds = sample_pair(start, "mechanism")
        witnesses.extend(case for law in LAWS for case in
                         witness_case(worlds[law], start, spec["tape"], spec["replicate"], spec["turn"], model))

    for start in starts:
        worlds = sample_pair(start, "mechanism")
        for replicate in range(MECHANISM_TAPES):
            tape = movement_tape("mechanism", start.source_key, replicate)
            for law, world in worlds.items():
                words = model["policies"][law]
                walks = {(version, mirror): walk(world, tape, version, mirror) for version in VERSIONS for mirror in MIRRORS}
                for (version, mirror), (_, steps, counts) in walks.items():
                    margin[law, version, mirror].update(counts)
                    require(physical_route(steps) == physical_route(walks[0, False][1]),
                            "Version or mirror changed the physical pass-only path")
                arrivals = {turn for visits, _, _ in walks.values() for turn in visits}
                for turn in sorted(arrivals):
                    current = {}
                    for (version, mirror), (visits, _, _) in walks.items():
                        if turn in visits:
                            state = visits[turn]
                            current[version, mirror] = (state, read_all(state, law, words[str(version)], words[str(1 - version)]))
                    for (version, mirror), (state, reads) in current.items():
                        outcome = apply_all(state, reads, world)
                        cue = CUE[state.approach]
                        update_recipient(recipients[law, version, mirror, cue], outcome)
                        rows.append([law, start.seed, replicate, turn, version, mirror, cue, outcome["stock"],
                                     outcome["accepted"], outcome["would_pay"],
                                     [outcome["options"][arm]["bit"] for arm in ARMS],
                                     [outcome["options"][arm]["expected_bit"] for arm in ARMS],
                                     [[outcome["options"][arm][k] for k in ("consumed", "denied", "energy_after")]
                                      for arm in ARMS]])
                    for mirror in MIRRORS:
                        got = [current[v, mirror] for v in VERSIONS if (v, mirror) in current]
                        if got:
                            states, results = zip(*got, strict=True)
                            cue = CUE[states[0].approach]
                            update_pair(paired[law, mirror, cue], states, results)
                    for version in VERSIONS:
                        base, other = current.get((version, False)), current.get((1 - version, True))
                        if base and other:
                            update_mirror(mirrored[law, version, CUE[base[0].approach]], base[0], other[0], base[1], other[1])
                        elif base:
                            mirrored[law, version, CUE[base[0].approach]]["without_counterpart"] += 1

    def table(mapping, fields):
        return [{**dict(zip(fields, key, strict=True)), **value} for key, value in sorted(mapping.items())]

    return {"schema": "feeder-payoff-mechanism-v1", "weights_sha256": weights_sha, "bank_sha256": bank_sha,
            "founders": len(starts), "tapes_per_founder": MECHANISM_TAPES, "turns": [FIRST_TURN, LAST_TURN],
            "arm_order": list(ARMS), "selection": choice, "witnesses": witnesses,
            "margins": table(margin, ("law", "version", "mirror")),
            "recipients": table(recipients, ("law", "version", "mirror", "cue")),
            "paired": table(paired, ("law", "mirror", "cue")), "mirrored_and_crossed": table(mirrored, ("law", "version", "cue")),
            "eligible_fields": ["law", "seed", "replicate", "turn", "version", "mirror", "cue", "stock", "accepted",
                                "would_pay", "issued_bits", "expected_bits", "consumed_denied_energy_after"],
            "eligible_rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, default=HERE / "learned_words.json")
    parser.add_argument("--weights-sha", required=True)
    parser.add_argument("--bank", type=Path, default=BANK_PATH)
    parser.add_argument("--output", type=Path, default=HERE / "mechanism_results.json")
    args = parser.parse_args()
    try:
        model, folds, bank_sha = locked_weights(args.weights, args.weights_sha, args.bank)
        results = run(model, folds["mechanism"], weights_sha=args.weights_sha, bank_sha=bank_sha)
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(results, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
        print(f"{len(results['eligible_rows'])} eligible recipients, {len(results['witnesses'])} detailed archives in {args.output}")
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
