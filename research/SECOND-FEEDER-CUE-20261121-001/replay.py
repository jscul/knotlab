"""Regenerate a sealed paired decision from its seed, tapes, and public prefixes."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from replay_game import Observation, play_prefix, public_view, require, take_turn
from replay_state import (
    DETECTORS,
    SECOND_FIELDS,
    SELECTED_FIELD,
    PublicMemory,
    empty_votes,
    expected_bit,
    neutral_words,
    one_hot,
    selected_from_score,
)
from replay_training import audit_training

from bank import load_bank, movement_tape, sample_pair
from device import NAMES, OWNERS, STARS, LearnedKnotBot
from history_reader import history_verdict


HERE = Path(__file__).resolve().parent
SIDES = ("empty", "full")
ARMS = ("original", "sham", "swap", "erased", "selected_field")
LAWS = ("parity", "nae")
LAW_LABEL = {"parity": "parity", "nae": "not-all-equal"}
CUE_ORDER = ("none", *DETECTORS)
ACTION = {0: "PASS", 1: "EAT"}
WORD_MEANING = {
    "x_here": {"10": "certificate absent", "01": "paid-site certificate present"},
    "x_paid_menu": {"1000": "origin unavailable", "0100": "zero ports", "0010": "one port", "0001": "multiple ports"},
    "arr_menu": {"1000": "origin unavailable", "0100": "zero ports", "0010": "one port", "0001": "multiple ports"},
    "arr_from": {"100": "origin unavailable", "010": "nonfeeder origin", "001": "feeder origin"},
}


def normalized(value):
    return json.loads(json.dumps(value))


def raw_state(snapshot):
    raw = 0
    for name, marks in NAMES.items():
        bits = snapshot[name]
        require(len(bits) == len(marks) and set(bits) <= {"0", "1"}, f"Invalid raw word for {name}")
        raw |= sum(1 << index for index, bit in zip(marks, bits, strict=True) if bit == "1")
    return raw


def allowed(raw, law):
    for support in STARS.values():
        count = sum((raw >> mark) & 1 for mark in support)
        if law == "parity" and count % 2 or law == "nae" and not 0 < count < len(support):
            return False
    return True


def verify_offers(before, offers, after, law, only=None):
    raw = raw_state(before)
    require(allowed(raw, law), f"Unlawful starting word under {law}")
    for offer in offers:
        a, b = offer["operands"]
        target = offer["after"]
        require(offer["before"] == raw, f"Discontinuous physical offers under {law}")
        require(OWNERS[a] == OWNERS[b] and offer["holder"] in OWNERS[a],
                f"Operands do not have the same admitted holders under {law}")
        require(all(name in STARS[offer["holder"]] and name not in (a, b) for name, _ in offer["guard"]),
                f"Offer guard does not use unchanged co-held marks under {law}")
        if only is not None:
            require(a in only and b in only, f"Intervention reached a name outside its field under {law}")
        enabled = all((raw >> name) & 1 == value for name, value in offer["guard"])
        mask = (1 << a) | (1 << b)
        expected = raw ^ mask if enabled and ((raw >> a) ^ (raw >> b)) & 1 else raw
        require(expected == target and allowed(target, law), f"Incorrect physical offer under {law}")
        raw = target
    require(raw == raw_state(after), f"Physical offer trace ended at the wrong state under {law}")


def frozen_selector(export):
    values = export["scores"]
    require(len(values) == len(DETECTORS) and all(type(x) is int and -7 <= x <= 7 for x in values),
            "Invalid credit scores")
    selector = selected_from_score(dict(zip(DETECTORS, values, strict=True)))
    require(export["selector"] == CUE_ORDER.index(selector), "Selector differs from the frozen score and tie rule")
    require(export["selector_word"] == one_hot(CUE_ORDER.index(selector), len(CUE_ORDER)),
            "Selector index differs from the physical word")
    require(export["score_words"] == [one_hot(value + 7, 15) for value in values],
            "Fitted scores differ from the physical words")
    return selector


def word_subset(state, expected, label):
    bad = [name for name, word in expected.items() if state[name] != word]
    require(not bad, f"Wrong words in {label} for {', '.join(bad)}")


def check_preparation(bot, prefix, events, selector, export, side):
    memory = PublicMemory()
    if events is not None:
        require(len(events) == len(prefix.rows), f"The saved preparation length differs for {side}")
    for index, row in enumerate(prefix.rows):
        saved = events[index] if events is not None else None
        receipt = row.receipt
        public = receipt.observation
        label = f"{side} prefix on turn {row.event['turn']}"
        state = dict(bot.snapshot())
        word_subset(state, memory.words(), label)
        if saved is not None:
            require(state == saved["memory_before"] and row.event == saved["actual"], f"Saved {label} differs")
            require(saved["public"] == row.public_row() and saved["applied_bit"] == receipt.bit,
                    f"Supplied action differs from {label}")
        natural = bot.decide(public)
        require(natural == expected_bit(public, memory.words(), selector), f"Unforced action differs from {label}")
        if saved is not None:
            require(natural == saved["unforced_bit"], f"Saved unforced action differs from {label}")
        require(tuple(map(int, empty_votes(public, memory.words()).values())) == bot.candidate_votes(),
                f"Pre-action physical detector votes differ from {label}")
        bot.after_turn(public, receipt.bit, receipt.outgoing_slot, receipt.energy_after, training=False)
        memory = memory.advance(receipt)
        state = dict(bot.snapshot())
        word_subset(state, memory.words(), label)
        require(bot.export() == export, f"Read-only fitted state changed during {label}")
        if saved is not None:
            require(state == saved["memory_after"], f"Saved receipt differs at {label}")
    bot.checkpoint(prefix.observation)
    checkpoint = dict(bot.snapshot())
    word_subset(checkpoint, memory.words(), f"{side} decision")
    require(checkpoint["a"] == "100" and bot.export() == export, f"Incorrect prepared actuator on {side}")
    require(not any(bot.candidate_votes()), f"A detector vote was already present at the {side} checkpoint")
    return checkpoint


def apply_arm(arm, bots):
    if arm == "sham":
        return [bots[side].sham(detail=True) for side in SIDES]
    if arm == "swap":
        return bots["empty"].exchange_second(bots["full"], detail=True)
    if arm == "selected_field":
        return bots["empty"].exchange_selected(bots["full"], detail=True)
    if arm == "erased":
        return [bots[side].erase_second(detail=True) for side in SIDES]
    return None


def expected_intervention(arm, state, other, selector):
    if arm == "swap":
        return {**state, **{field: other[field] for field in SECOND_FIELDS}}
    if arm == "selected_field" and selector != "none":
        field = SELECTED_FIELD[selector]
        return {**state, field: other[field]}
    if arm == "erased":
        return {**state, **neutral_words()}
    return state


def audit_arm(arm, saved, bots, before, observation, law, selector, export):
    working = {side: deepcopy(bot) for side, bot in bots.items()}
    offered = apply_arm(arm, working)
    if "intervention" in saved:
        require(normalized(offered) == saved["intervention"], f"{arm} physical intervention trace differs under {law}")
    fields = SECOND_FIELDS
    if arm == "selected_field":
        fields = () if selector == "none" else (SELECTED_FIELD[selector],)
    names = {name for field in fields for name in NAMES[field]}

    bits = {}
    for i, side in enumerate(SIDES):
        label = f"{law} {arm} {side}"
        bot = working[side]
        logged = saved.get("sides", saved)[side]
        post = dict(bot.snapshot())
        expected = expected_intervention(arm, before[side], before[SIDES[1 - i]], selector)
        require(before[side] == logged["before"] and post == logged["after_intervention"] == expected,
                f"The named intervention changed the wrong words in {label}")
        if offered is not None:
            verify_offers(before[side], offered[i], post, law, only=names)
        bit, trace = bot.read_prepared(detail=True)
        read = dict(bot.snapshot())
        if "read_offers" in logged:
            require(normalized(trace) == logged["read_offers"], f"Read offers differ in {label}")
        require(read == logged["after_read"], f"Final words differ in {label}")
        verify_offers(post, trace, read, law)
        require(bit == logged["bit"] == int(read["a"][2]) == expected_bit(observation, post, selector),
                f"Fixed physical action differs from the public cue in {label}")
        require(read["a"] == ("001" if bit else "010") and bot.export() == export,
                f"Actuator or frozen credit words differ in {label}")
        require(tuple(map(int, empty_votes(observation, post).values())) == bot.candidate_votes(),
                f"Candidate veto marks differ in {label}")
        bits[side] = bit
    return bits


def audit_pair_metadata(pair, prefixes, world):
    a, b = pair["A"], pair["B"]
    require(a != b, "The two scorer-side feeder identities must be distinct")
    states = {side: prefixes[side].game.snapshot() for side in SIDES}
    stage = states["empty"]["formation"]
    require(stage == states["full"]["formation"] == pair["stage"], "The decision formations differ")
    require(len(world.stages[stage].links[a]) == len(world.stages[stage].links[b]) == pair["degree"],
            "Exact-degree matching failed at the decision")
    require(states["empty"]["holder"] == a, "The empty branch does not query A")
    payments = {side: prefixes[side].paid_holders() for side in SIDES}
    require(0 < len(payments["empty"]) == len(payments["full"]), "Prior paid meal counts differ")
    if pair["panel"] == "secondary":
        require(states["full"]["holder"] == a and a in payments["empty"] and b in payments["full"],
                "The same-target comparison does not replay")
    else:
        require(states["full"]["holder"] == b and all(a in paid and b not in paid for paid in payments.values()),
                "The distinct equal-degree comparison does not replay")
    for side in SIDES:
        state = states[side]
        require((state["holder"] in state["available"]) == (side == "full"), f"Wrong frozen stock on {side}")

    certificates = {side: history_verdict(prefixes[side].public_history()) for side in SIDES}
    require((certificates == {"empty": "empty", "full": "full"}) == pair["both_certified"],
            "Public history verdicts differ from the saved match")
    control = []
    for side in SIDES:
        energies = []
        source = prefixes[side].game
        for bit in (0, 1):
            copy = source.clone()
            row = take_turn(copy, world, bit)
            if not copy.done:
                row = take_turn(copy, world, 1)
            energies.append(row.receipt.energy_after)
        control.append(energies)
    require(control == pair["two_turn_energy_off_on"], "Two-turn energy control differs")
    return certificates


def check_barrier(prefixes, bots, law):
    """Perturb only the spectator-side stock, knot and tape before a fixed read."""
    for index, side in enumerate(SIDES):
        clean = prefixes[side].observation
        require(set(clean.__slots__) == {"feeder", "energy", "previous", "slots"}, "Public input gained fields")
        copy = prefixes[side].game.clone()
        hidden = copy._game
        old_holder = hidden.holder
        old_stock = old_holder in hidden.available
        other = prefixes[SIDES[1 - index]].game.snapshot()
        hidden.holder = other["holder"]
        if old_stock:
            hidden.available.discard(hidden.holder)
        else:
            hidden.available.add(hidden.holder)
        # Keep the entire ration ledger distinct even if the counterpart already had the opposite stock.
        if hidden.holder != old_holder:
            hidden.available.symmetric_difference_update({old_holder})
        hidden.tape ^= 1
        challenge = copy.observe()
        state = prefixes[side].game.snapshot()
        changed = copy.snapshot()
        require(challenge == clean and state["available"] != changed["available"] and state["tape"] != changed["tape"]
                and ((changed["holder"] in changed["available"]) != old_stock),
                f"Spectator perturbation did not preserve the public observation under {law}")
        isolated = Observation(challenge.feeder, challenge.energy, challenge.previous, challenge.slots)
        require(deepcopy(bots[side]).decide(isolated) == deepcopy(bots[side]).decide(clean),
                f"Private perturbation changed the read under {law}")


def audit_case(case, start, export):
    pair = case["pair"]
    law = pair["law"]
    world = sample_pair(start, "mechanism")[law]
    fitted = frozen_selector(export)
    require(export == case["trained_state"], f"Saved {law} case did not use the fitted words in this file")
    mode = case["policy_mode"]
    require(mode in ("learned", "strict_return"), f"Unknown recorded policy {mode!r}")
    selector = fitted if mode == "learned" else mode
    index = CUE_ORDER.index(selector)
    require(case["active_selector"] == index, f"The active {law} selector differs from its transport")
    active = {**export, "selector": index, "selector_word": one_hot(index, len(CUE_ORDER))}
    require(NAMES["a"][2] == 6 and tuple(case["second_fields"]) == SECOND_FIELDS,
            "Fixed action or second-memory names differ from the declared interface")
    prefixes, bots, before = {}, {}, {}
    for side in SIDES:
        branch = pair[side]
        tape = movement_tape("mechanism", start.source_key, branch["replicate"])
        require(tape == branch["tape"], f"Wrong seeded {side} tape under {law}")
        prefix = play_prefix(world, tape, branch["attempt_turns"], pair["turn"])
        require(prefix.public_history() == branch["public"] == case["public_prefix"][side],
                f"Regenerated public history differs on {side} under {law}")
        require(prefix.route() == branch["route"] and prefix.game.snapshot() == case["frozen_games"][side],
                f"Regenerated game checkpoint differs on {side} under {law}")
        bot = LearnedKnotBot.from_frozen(law, export, mode=mode)
        bot.begin_episode(training=False)
        before[side] = check_preparation(bot, prefix, case["preparation"][side], selector, active, side)
        prefixes[side], bots[side] = prefix, bot

    observation = prefixes["empty"].observation
    require(observation == prefixes["full"].observation and public_view(observation) == pair["current"],
            "The full decision-time public observations differ")
    require(before["empty"]["m"] == before["full"]["m"] and before["empty"]["selector"] == before["full"]["selector"],
            "The original keeper or frozen cue selector differs between histories")
    certificates = audit_pair_metadata(pair, prefixes, world)
    check_barrier(prefixes, bots, law)

    differing = [name for name in before["empty"] if before["empty"][name] != before["full"][name]]
    require((set(differing) <= set(SECOND_FIELDS)) == case["fixed_fields_equal_between_histories"],
            "The between-history register contrast was misclassified")
    answers = {arm: audit_arm(arm, case["arms"][arm], bots, before, observation, law, selector, active)
               for arm in ARMS}
    events = {}
    for arm, bits in answers.items():
        events[arm] = {}
        for side, bit in bits.items():
            source = prefixes[side].game
            require(source.snapshot() == case["frozen_games"][side], f"Device read advanced {side} before game action")
            step = take_turn(source.clone(), world, bit)
            require(step.event == case["arms"][arm]["sides"][side]["event"], f"Actual game event differs for {arm} {side}")
            events[arm][side] = step.event
    return {"pair": pair, "prefixes": prefixes, "before": before, "certificates": certificates,
            "differing": differing, "selector": selector, "answers": answers, "events": events,
            "world": world, "mode": mode, "preparation": case["preparation"]}


def audit_inactive_with_different_x(control, saved, export):
    pair, prefixes = control["pair"], control["prefixes"]
    law = pair["law"]
    require(saved["seed"] == pair["seed"] and saved["turn"] == pair["turn"] and
            saved["tape"] == [pair[side]["tape"] for side in SIDES], "Different case supplied for the fitted control replay")
    selector = frozen_selector(export)
    bots, before = {}, {}
    for side in SIDES:
        bots[side] = LearnedKnotBot.from_frozen(law, export).begin_episode(training=False)
        before[side] = check_preparation(bots[side], prefixes[side], None, selector, export, side)
        word_subset(before[side], {name: control["before"][side][name] for name in SECOND_FIELDS},
                    f"same prefix on {side} with the fitted selector")
    differing_x = [name for name in SECOND_FIELDS if before["empty"][name] != before["full"][name]]
    require(differing_x, "The strict-control histories have equal second-memory words")
    answers = {arm: audit_arm(arm, details, bots, before, prefixes["empty"].observation, law, selector, export)
               for arm, details in saved["arms"].items()}
    for arm, bits in answers.items():
        for side, bit in bits.items():
            actual = take_turn(prefixes[side].game.clone(), control["world"], bit).event
            require(actual == saved["arms"][arm][side]["event"], "Same-prefix fitted game action differs")
    return selector, differing_x, answers


def format_event(event):
    start, end = event["holder_before"], event["holder_after"]
    if event["action"] == "move":
        movement = f"PASS K{start} → K{end} via d{event['distinction']} (port {event['slot']})"
    else:
        result = "ration consumed" if event["consumed"] else "no ration" if event["bit"] else "refused"
        movement = f"{ACTION[event['bit']]} at K{start}, {result}"
    energy = f"{event['energy_before']}→{event['energy_after']}"
    life = ", died" if event["terminal"] else ""
    return f"{movement}, energy {energy}{life}"


def transcript(audit):
    pair, prefixes = audit["pair"], audit["prefixes"]
    tapes = ", ".join(str(pair[side]["tape"]) for side in SIDES)
    yield f"Seed `{pair['seed']}`, tapes `{tapes}`, {pair['panel']} comparison. Prefix actions were supplied."
    yield ""
    yield "| Turn | History ending at the empty feeder | History ending at the full feeder |"
    yield "|---:|---|---|"
    for left, right in zip(prefixes["empty"].rows, prefixes["full"].rows, strict=True):
        yield f"| {left.event['turn']} | {format_event(left.event)} | {format_event(right.event)} |"
    yield ""
    observation = prefixes["empty"].observation
    left, right = (prefixes[side].game.snapshot()["holder"] for side in SIDES)
    yield (f"On turn {pair['turn']}, the bot sees feeder on, energy {observation.energy}, previous action "
           f"{observation.previous} and ports {', '.join(map(str, observation.slots))} in both histories. "
           f"Spectators see K{left} empty and K{right} full.")
    yield ""
    first = audit["before"]["empty"]["m"]
    meaning = {"110": "ready", "101": "one port at the last paid meal", "011": "multiple ports at the last paid meal"}
    yield (f"Both preparations hold first memory `{first}` ({meaning[first]}), active cue "
           f"`{audit['selector']}`, and ready action `100`.")
    for side in SIDES:
        saved = [step for step in audit["preparation"][side] if step["actual"]["consumed"]][-1]
        start, end = saved["memory_before"], saved["memory_after"]
        yield (f"The {side} side’s last paid EAT was at K{saved['actual']['holder_before']} on turn {saved['turn']}. "
               f"The receipt stored the pre-action arrival menu `{end['x_paid_menu']}` in `x_paid_menu`, "
               f"which had held `{start['x_paid_menu']}`.")
    yield ""
    yield "| Differing word | Empty history | Full history |"
    yield "|---|---|---|"
    for name in audit["differing"]:
        e, f = (audit["before"][side][name] for side in SIDES)
        values = WORD_MEANING.get(name, {})
        shown = [f"`{word}` ({values[word]})" if word in values else f"`{word}`" for word in (e, f)]
        yield f"| `{name}` | {shown[0]} | {shown[1]} |"
    if not audit["differing"]:
        yield "| No differing words | — | — |"
    yield ""
    differing_x = [name for name in audit["differing"] if name in SECOND_FIELDS]
    if differing_x:
        yield f"The X differences are {', '.join(f'`{name}`' for name in differing_x)}."
    else:
        yield "The two X words agree before the interventions."
    yield "The physical action mark was read for both histories in every arm before any forked game advanced."
    yield ""
    yield "| Arm | Recorded empty-side bit and game result | Recorded full-side bit and game result |"
    yield "|---|---|---|"
    for arm in ARMS:
        cells = [f"{audit['answers'][arm][side]} · {format_event(audit['events'][arm][side])}" for side in SIDES]
        yield f"| {arm.replace('_', ' ')} | {cells[0]} | {cells[1]} |"
    yield ""
    verdicts = audit["certificates"]
    yield f"Public-history verdicts were `{verdicts['empty']}` and `{verdicts['full']}`."
    e, f = pair["two_turn_energy_off_on"]
    yield (f"In the separate two-charged-turn control, PASS first versus EAT first leaves {e[0]} versus {e[1]} energy "
           f"on the empty side and {f[0]} versus {f[1]} on the full side.")
    yield ""


def case_chapters(label, reports):
    if len(reports) == 2 and reports[0][1] == reports[1][1]:
        yield f"## {label} under both laws"
        yield ""
        yield "The parity and not-all-equal seed replays were checked separately and have the same displayed trace."
        yield ""
        yield from reports[0][1]
        return
    for law, lines in reports:
        yield f"## {label} under {LAW_LABEL[law]}"
        yield ""
        yield from lines


def cue_bits(answers, arm):
    return "/".join(str(answers[arm][side]) for side in SIDES)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=HERE / "causal_replay.json")
    parser.add_argument("--weights", type=Path, default=HERE / "learning_weights.json")
    parser.add_argument("--bank", type=Path, default=HERE / "bank.json")
    parser.add_argument("--training", type=Path, default=HERE / "learning_training.json")
    parser.add_argument("--law", choices=LAWS)
    parser.add_argument("--seed", type=int, help="verify the named seed without searching for a replacement")
    parser.add_argument("--write", type=Path, help="write the verified Markdown replay")
    args = parser.parse_args()
    try:
        packed = args.weights.read_bytes()
        weights = json.loads(packed)
        record = json.loads(args.record.read_bytes())
        receipts = json.loads(args.training.read_bytes())
        folds, bank_digest = load_bank(args.bank)
        all_keys = [s.source_key for starts in folds.values() for s in starts]
        require(len(set(all_keys)) == len(all_keys), "Founder structures cross the frozen folds")
        require(weights["bank_sha256"] == receipts["bank_sha256"] == bank_digest,
                "Fitted weights came from a different bank")
        digest = sha256(packed).hexdigest()
        require(record["schema_version"] == 1 and record["weights_sha256"] == receipts["weights_sha256"] == digest,
                "The replay does not attest the supplied frozen weights")
        starts = {start.seed: start for start in folds["mechanism"]}
        chapters = ["# Second feeder cue replay", ""]
        checked = audit_training(weights, receipts, folds["train"])
        chapters.extend((
            "## Frozen training check", "",
            f"Pinned weights SHA-256 `{digest}`.", "",
            "| Law | Charged veto opportunities | Receipts that changed scores | Final scores | Active cue |",
            "|---|---:|---:|---|---|",
        ))
        for law, result in checked.items():
            chapters.append(f"| {LAW_LABEL[law]} | {result['opportunities']} | {result['score_changes']} | "
                            f"`{result['trained_scores']}` | `{result['trained_selector']}` |")
        chapters.extend(("", "The scores are in the fixed order strict return, approach feeder, approach menu and approach slot. "
                         "Ordered public receipts reproduced every packet and final word, with one eligible episode per law also replayed physically. "
                         "A final selector of `none` leaves the current-only action in force.", ""))
        chapters.extend((
            f"Permuted feedback ended at `{checked['parity']['permuted_scores']}` under parity and "
            f"`{checked['nae']['permuted_scores']}` under not-all-equal, with selector `none` under both.", ""))
        chapters.extend(("The replay uses the archived game and the frozen device with separate checks for public receipts, "
                         "physical offers and credit arithmetic. On game copies, changing private stock, cursor and tape "
                         "while preserving the public observation preserved the prepared read.", ""))
        count = 0
        for family, label in (("by_law", "Frozen fitted reader"), ("control_by_law", "Preset strict-return control")):
            reports = []
            for law in (args.law,) if args.law else LAWS:
                case = record.get(family, {}).get(law)
                if case is None or args.seed is not None and args.seed != case["pair"]["seed"]:
                    continue
                pair = case["pair"]
                seed = pair["seed"]
                require(pair["law"] == law, "Requested law differs from the saved case")
                require(seed in starts and starts[seed].source_key == pair["source_key"], "Seed is outside the mechanism fold")
                require(case["weights_sha256"] == digest, f"Saved {law} case has a different fitted policy digest")
                export = weights["policies"][law]["trained"]
                audit = audit_case(case, starts[seed], export)
                lines = list(transcript(audit))
                if family == "control_by_law" and law in record.get("learned_on_same_control_case", {}):
                    saved = record["learned_on_same_control_case"][law]
                    selector, differences, answers = audit_inactive_with_different_x(audit, saved, export)
                    lines.extend((f"With these same prepared histories, the fitted reader retains differences in "
                                  f"{', '.join(f'`{name}`' for name in differences)} and has selector `{selector}`. "
                                  f"Its original bits are `{cue_bits(answers, 'original')}`, and exchanging X gives "
                                  f"`{cue_bits(answers, 'swap')}`. Neutralizing X gives `{cue_bits(answers, 'erased')}`.", ""))
                reports.append((law, lines))
                count += 1
            if reports:
                chapters.extend(case_chapters(label, reports))
        require(count > 0, "No recorded pairing matches the requested seed and law")
        result = "\n".join(chapters).rstrip() + "\n"
        if args.write is None:
            print(result, end="")
        else:
            args.write.write_text(result, encoding="utf-8")
            print(args.write)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
