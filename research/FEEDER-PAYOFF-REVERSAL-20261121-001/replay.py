"""Regenerate the prospectively selected paired seed and optionally play it to death."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from intervene import (ARMS, BANK_PATH, CUE, HERE, LAWS, MIRRORS, VERSIONS, admitted,
                       clue_after, expected_action, learned_score, locked_weights, public_observation,
                       require, select_replay, take_step, witness_case)
from paired_game import ReversalGame
from reader import PayoffReader
from source_bank import sample_pair


LAW = {"parity": "parity", "nae": "not-all-equal"}
ARM_LABELS = {"original": "Resident word", "sham": "Sham", "transfer": "Other version’s word",
              "erase": "Neutral erase", "restore": "Restored word", "count": "Count-trained word",
              "shuffled": "Re-paired-credit word"}


def cue_label(clue):
    return "—" if clue is None else CUE[clue]


def growth_label(event):
    growth = event["growth"]
    if not growth:
        return "—"
    holders = [birth["holder"] for birth in growth["births"]]
    if not holders:
        return f"Growth {growth['status']}"
    ordered = sorted(holders)
    names = (f"K{ordered[0]}–K{ordered[-1]}" if len(ordered) > 2 and ordered == list(range(ordered[0], ordered[-1] + 1))
             else ", ".join(f"K{holder}" for holder in ordered))
    return f"Formation {growth['formation']} adds {names}"


def actual_action(event):
    h = event["holder_before"]
    if event["action"] == "move":
        action = f"PASS K{h} → K{event['holder_after']} via d{event['distinction']}"
    elif event["action"] == "refused":
        action = f"PASS refused at K{h}"
    elif event["denied"]:
        action = f"EAT denied at K{h}, stock retained"
    elif event["consumed"]:
        action = f"EAT at K{h}, ration consumed"
    else:
        action = f"EAT at K{h}, no ration in stock"
    energy = f"{event['energy_before']}→{event['energy_after']}"
    return f"{action}, energy {energy}" + (", died" if event["terminal"] else "")


def bit_action(read):
    bit = read["bit"]
    energy = read["actual"]
    return f"`{read['score']:+d}` · bit {bit} · {actual_action(energy)}"


def decision_section(rows):
    by = {(row["mirror"], row["version"]): row for row in rows}
    template = by[False, 0]
    yield f"### Ordinary cue {template['cue']} on tape {template['tape']}"
    yield ""
    yield "Both versions follow these physical passes. The mirrored code retains every move and exchanges the paired public slot names."
    yield ""
    yield "| Turn | Growth | Charged pass | Ordinary slot | Mirrored slot | Arrival clue in the ordinary code |"
    yield "|---:|---|---|---:|---:|---|"
    for left, right in zip(template["prefix"], by[True, 0]["prefix"], strict=True):
        event = left["game"]
        normal, mirror = (row["public"]["outgoing_slot"] for row in (left, right))
        clue = left["receipt"]["next_route_cue"] or "—"
        yield (f"| {left['turn']} | {growth_label(event)} | {actual_action(event)} | "
               f"{normal if normal is not None else '—'} | {mirror if mirror is not None else '—'} | {clue} |")
    yield ""
    for mirror in MIRRORS:
        v0, v1 = (by[mirror, version] for version in VERSIONS)
        obs, holder = v0["observation"], v0["frozen_game"]["holder"]
        before = v0["prepared"]["banks"]
        label = "Mirrored" if mirror else "Ordinary"
        yield f"**{label} code**"
        yield ""
        yield (f"Turn {v0['turn']} is at stocked K{holder}. Both readers see the feeder on, energy {obs['energy']}, "
               f"previous {obs['previous']} and anonymous ports {', '.join(map(str, obs['slots']))}. "
               f"The preceding real movement wrote clue {v0['cue']} into route word `{before['route']}`. "
               f"First receipt `{before['m']}` and prepared action `100` are fixed. "
               f"The spectator’s opening is {v0['accepted']} in version 0 and {v1['accepted']} in version 1.")
        yield ""
        yield "| Prepared arm | Version 0 learned score, bit and game result | Version 1 learned score, bit and game result |"
        yield "|---|---|---|"
        for arm in ARMS:
            yield f"| {ARM_LABELS[arm]} | {bit_action(v0['options'][arm])} | {bit_action(v1['options'][arm])} |"
        yield ""


def training_section(model, audit, laws):
    yield "## Actual acquisition receipts"
    yield ""
    if audit is not None:
        yield "| Law | Version | Charged A | A paid | Charged B | B paid |"
        yield "|---|---:|---:|---:|---:|---:|"
        for row in audit["training"]["streams"]:
            if row["law"] in laws and row["order"] == "primary" and row["arm"] == "outcome":
                yield (f"| {LAW[row['law']]} | {row['version']} | {row['A_visits']} | {row['A_paid']} | "
                       f"{row['B_visits']} | {row['B_paid']} |")
        yield ""
    yield "| Version | Credit condition | Signed score | 32 learned pairs, least significant first |"
    yield "|---|---|---:|---|"
    for version in VERSIONS:
        mounted = model["policies"][laws[0]][str(version)]
        require(all(model["policies"][law][str(version)] == mounted for law in laws), "This transcript needs separate trained-word rows")
        for arm in ("outcome", "count", "shuffled"):
            export = mounted[arm]
            yield f"| {version} | {arm} | {learned_score(export):+d} | `{export['word']}` |"
    yield ""
    if audit is None:
        return
    yield "The first matched pair was also rerun through the physical writer for each fitted arm. The two entries below are the actual charged bites in recorded order."
    yield ""
    yield "| Version | Credit condition | First actual bite and score update | Second actual bite and score update |"
    yield "|---|---|---|---|"
    for row in audit["training"]["physically_replayed_first_pairs"]:
        if row["law"] != laws[0]:
            continue
        fields = [(f"{probe['clue']} {'paid' if probe['paid'] else 'denied'} {probe['from_energy']}→{probe['to_energy']}, "
                   f"score {probe['score_before']:+d}→{probe['score_after']:+d}") for probe in row["actual"]]
        yield f"| {row['version']} | {row['arm']} | {fields[0]} | {fields[1]} |"
    yield ""


def whole_episode(world, tape, version, mirror, export):
    game = ReversalGame(world, tape=tape, version=version, mirror=mirror)
    board = PayoffReader.from_memory(world.law, export).begin_episode(training=False)
    cue = None
    events = []
    while not game.done:
        obs = game.observe()
        board.checkpoint(obs)
        bit = board.read_prepared()
        native = (board.word >> 6) & 1
        require(bit == native == expected_action(obs, cue, learned_score(export)), "Frozen learned role read the wrong action")
        action = board.action_word
        step = take_step(game, world, bit)
        receipt = step.receipt
        old_cue = cue
        cue = clue_after(obs, receipt.outgoing_slot, cue)
        local = board.after_turn(obs, bit, receipt.outgoing_slot, receipt.energy_after)
        require(board.export_memory() == export and admitted(board.word, world.law) and
                local["next_route_cue"] == (None if cue is None else CUE[cue]), "The whole episode changed the mounted word or receipt")
        events.append({"event": step.event, "public": public_observation(obs), "cue": cue_label(old_cue),
                       "action_mark": native, "action_word": action, "memory_after": local["memory_after"]})
    final = game.snapshot()
    require(final["turns"] == 6 + 4 * final["meals"] - final["wasted"], "Whole-episode energy does not balance")
    return events


def whole_section(world, tape, rep, mirror, model):
    sequences = [whole_episode(world, tape, version, mirror, model["policies"][world.law][str(version)]["outcome"])
                 for version in VERSIONS]
    yield f"### {LAW[world.law]}, tape {tape}, {'mirrored' if mirror else 'ordinary'} code"
    yield ""
    yield f"This separate uninterrupted game starts at reset on replicate {rep}. Each version reads its own sealed word until death."
    yield ""
    yield "| Turn | Version 0 from reset | Version 1 from reset |"
    yield "|---:|---|---|"
    for index in range(max(map(len, sequences))):
        cells = []
        for events in sequences:
            if index >= len(events):
                cells.append("—")
                continue
            row = events[index]
            event = row["event"]
            growth = growth_label(event)
            prefix = "" if growth == "—" else growth + ". "
            slot = "—" if event["slot"] is None else str(event["slot"])
            cue = row["cue"]
            cells.append(f"{prefix}{actual_action(event)} · slot {slot} · prior clue {cue} · "
                         f"actuator `{row['action_word']}` · first receipt `{row['memory_after']}`")
        yield f"| {index + 1} | {cells[0]} | {cells[1]} |"
    yield ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, default=HERE / "learned_words.json")
    parser.add_argument("--weights-sha", required=True)
    parser.add_argument("--bank", type=Path, default=BANK_PATH)
    parser.add_argument("--record", type=Path, default=HERE / "mechanism_results.json")
    parser.add_argument("--audit", type=Path, default=HERE / "audit_results.json")
    parser.add_argument("--seed", type=int, help="verify the named seed from the prospective selection")
    parser.add_argument("--law", choices=LAWS)
    parser.add_argument("--whole-life", action="store_true", help="also record uninterrupted games through death")
    parser.add_argument("--write", type=Path, help="write the verified transcript as Markdown")
    args = parser.parse_args()
    try:
        model, folds, bank = locked_weights(args.weights, args.weights_sha, args.bank)
        record = json.loads(args.record.read_bytes())
        require(record["weights_sha256"] == args.weights_sha and record["bank_sha256"] == bank, "Wrong release or bank")
        selected = select_replay(folds["mechanism"])
        require(record["selection"] == selected, "Saved replay selection differs from public-only prospectus")
        choices = [c for c in selected["cases"] if args.seed is None or c["seed"] == args.seed]
        require(choices, "No recorded seed matches the prospective selection")
        starts = {start.seed: start for start in folds["mechanism"]}
        laws = (args.law,) if args.law else LAWS
        audit = json.loads(args.audit.read_bytes()) if args.audit.exists() else None
        if audit is not None:
            require(audit["weights_sha256"] == args.weights_sha and
                    audit["mechanism"]["record_sha256"] == sha256(args.record.read_bytes()).hexdigest(), "Audit belongs to another sealed replay")
        lines = ["# Feeder payoff reversal seed replay", "", f"Released learned word hash `{args.weights_sha}`.", "",
                 *training_section(model, audit, laws), "## Frozen mechanism comparison", "",
                 "The prospectively first founder with both matched arrival clues was selected from public pass-only paths. "
                 "Each intervention was read on the same ready action mark before any fork advanced.", ""]
        for choice in choices:
            start = starts[choice["seed"]]
            worlds = sample_pair(start, "mechanism")
            lines.extend((f"Founder seed `{start.seed}`, replicate {choice['replicate']}, decision turn {choice['turn']}.", ""))
            displays = {}
            for law in laws:
                generated = witness_case(worlds[law], start, choice["tape"], choice["replicate"], choice["turn"], model)
                expected = [r for r in record["witnesses"] if (r["seed"], r["tape"], r["turn"], r["law"]) ==
                            (start.seed, choice["tape"], choice["turn"], law)]
                require(generated == expected, f"The actual detailed {law} replay disagrees with the sealed record")
                displays[law] = list(decision_section(generated))
            if len(displays) == 2 and displays[laws[0]] == displays[laws[1]]:
                lines.extend(("Parity and not-all-equal were replayed separately and give this same displayed trace.", "", *displays[laws[0]]))
            else:
                for law, display in displays.items():
                    lines.extend((f"**{LAW[law]}**", "", *display))
        if args.whole_life:
            lines.extend(("## Uninterrupted games", ""))
            for choice in choices:
                for law in laws:
                    world = sample_pair(starts[choice["seed"]], "mechanism")[law]
                    for mirror in MIRRORS:
                        lines.extend(whole_section(world, choice["tape"], choice["replicate"], mirror, model))
        result = "\n".join(lines).rstrip() + "\n"
        if args.write is None:
            print(result, end="")
        else:
            args.write.write_text(result, encoding="utf-8")
            print(args.write)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
