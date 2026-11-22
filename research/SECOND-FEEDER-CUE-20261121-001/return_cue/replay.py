"""Verify the return-cue repair with the unchanged first-study replay checks."""

from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
from statistics import fmean
import sys

from panel import load_file


HERE = Path(__file__).resolve().parent
FIRST = HERE.parent
if str(FIRST) not in sys.path:
    sys.path.append(str(FIRST))

from replay_game import require  # noqa: E402
from replay_state import MENU_MEMORY, current_choice, empty_votes, expected_bit, offered_menu  # noqa: E402


def return_votes(observation, words):
    votes = empty_votes(observation, words)
    votes["strict_return"] = bool(current_choice(observation) and words["x_here"] == "01")
    return votes


def return_bit(observation, words, selector):
    return current_choice(observation) * (not return_votes(observation, words).get(selector, False))


def audit_helpers():
    """Bind the first-study checks in private modules, leaving the originals intact."""
    bank = load_file("return_cue_replay_bank", HERE / "bank.py")
    device = load_file("return_cue_replay_device", HERE / "device.py")
    training = load_file("return_cue_training_audit", FIRST / "replay_training.py")
    replay = load_file("return_cue_decision_audit", FIRST / "replay.py")

    old, = device.first.DETECTORS[0]
    new, = device.DETECTORS[0]
    removed = (device.NAMES["paid"][1], 1)
    require((old.holder, old.operands) == (new.holder, new.operands) and removed in old.guard and
            new.guard == tuple(test for test in old.guard if test != removed) and
            tuple(device.DETECTORS[1:]) == tuple(device.first.DETECTORS[1:]),
            "The repair changed more than the strict menu guard")

    replay.sample_pair = bank.sample_pair
    replay.movement_tape = bank.movement_tape
    replay.LearnedKnotBot = device.LearnedKnotBot
    replay.NAMES, replay.OWNERS, replay.STARS = device.NAMES, device.OWNERS, device.STARS
    replay.empty_votes = return_votes
    replay.expected_bit = return_bit

    training.sample_pair = bank.sample_pair
    training.movement_tape = bank.movement_tape
    training.derive_seed = bank.derive_seed
    training.LearnedKnotBot = device.LearnedKnotBot
    training.device = device
    training.empty_votes = return_votes
    return bank, replay, training


def opportunities(ledger, checked):
    results = {}
    for law, summary in checked.items():
        strict = [row for packet in ledger["packets_by_law"][law] for row in packet["ordered_evidence"] if row["votes"][0]]
        positions = [[row[name] for name in ("seed", "tape", "turn")] for row in strict]
        paid = sum(row["energy_after"] > row["energy_before"] - 1 for row in strict)
        score = min(7, len(strict))
        if not paid:
            require(summary["trained_scores"][0] == score, f"Strict score differs from the opportunity count under {law}")
        representation = json.dumps(positions, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        results[law] = {"count": len(strict), "founders": len({row[0] for row in positions}), "paid": paid,
                        "score_from_count": score, "position_digest": sha256(representation).hexdigest(),
                        "selector_from_count": "strict_return" if len(strict) >= 7 else "none", "positions": positions}
    return results


def verify_count_record(record, ledger, counts, digest):
    require(record["schema"] == "return-cue-count-controls-v1" and record["weights_sha256"] == digest,
            "The opportunity count names a different release")
    require(record["position_fields"] == ["seed", "tape", "turn"], "The opportunity position schema changed")
    for law, recomputed in counts.items():
        entry = record["by_law"][law]
        require(entry["ordered_positions"] == recomputed["positions"] and
                entry["ordered_position_sha256"] == recomputed["position_digest"] and
                entry["opportunities"] == recomputed["count"] and entry["count_credit"] == recomputed["score_from_count"],
                f"Opportunity ledger differs under {law}")
        expected_first = "strict" if recomputed["count"] else "zero"
        expected_seven = "strict" if recomputed["count"] >= 7 else "zero"
        require(entry["aliases"]["first_opportunity"] == expected_first and
                entry["aliases"]["seven_opportunities"] == expected_seven, f"Count-only control is mislabeled under {law}")
        seen = 0
        for packet, held in zip(ledger["packets_by_law"][law], entry["packets"], strict=True):
            seen += sum(row["votes"][0] for row in packet["ordered_evidence"])
            actual = packet["trained"]
            scored = [min(7, seen), *actual["scores"][1:]]
            maximum = max(scored)
            winner = scored.index(maximum) + 1 if maximum > 0 else 0
            require((held["replicate"], held["opportunities"], held["reconstructed_scores"], held["reconstructed_selector"]) ==
                    (packet["replicate"], seen, scored, winner), f"Count-credit packet differs under {law}")


def check_source_lock(weights, args, bank, digest, bank_digest):
    path = args.weights.with_name("learning_source_lock.json")
    lock = json.loads(path.read_bytes())
    require(lock["weights_sha256"] == digest and lock["bank_sha256"] == bank_digest and
            lock["original_sha256"] == bank.ORIGINAL_SHA256, "Return-cue source lock differs")
    for name, expected in lock["repair_sha256"].items():
        require(sha256((HERE / name).read_bytes()).hexdigest() == expected, f"Frozen repair source {name} changed")
    require(lock["repair_sha256"]["device.py"] == weights["device_sha256"],
            "The frozen weights name a different repair source")


def check_count_behavior(directory, counts, starts, bank, digest):
    """Compare saved full-history hashes and each common-path output to the count-only arm."""
    path = directory / "survival_count_only.json"
    if not path.exists():
        return None
    results = json.loads(path.read_bytes())
    require(results["schema"] == "return-cue-count-survival-v1" and results["weights_sha256"] == digest,
            "The count-only behavior ledger names different weights")
    expected = {(s.source_key, r): (s.seed, bank.movement_tape("survival", s.source_key, r))
                for s in starts for r in range(bank.TAPES)}
    lives, common = {}, {law: [] for law in counts}
    with (directory / "survival_episodes.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["reader"] not in ("learned", "strict", "zero"):
                continue
            law, key, replicate = row["law"], row["source_key"], int(row["replicate"])
            require((int(row["seed"]), int(row["tape"])) == expected[key, replicate], "Wrong natural-play seed or tape")
            slot = law, key, replicate, row["reader"]
            require(slot not in lives, "Duplicate natural-play episode")
            lives[slot] = int(row["turns"]), row["public_history_sha256"]
    seen = set()
    with (directory / "survival_common_path.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            law, key, replicate = row["law"], row["source_key"], int(row["replicate"])
            require((int(row["seed"]), int(row["tape"])) == expected[key, replicate], "Wrong common-path seed or tape")
            slot = law, key, replicate, int(row["turn"])
            require(slot not in seen and {row[k] for k in ("learned", "strict", "zero")} <= {"0", "1"},
                    "Duplicate or non-Boolean common-path decision")
            seen.add(slot)
            common[law].append(row)
    checked = {}
    for law, count in counts.items():
        aliases = {"first_opportunity": "strict" if count["count"] else "zero",
                   "seven_opportunities": "strict" if count["count"] >= 7 else "zero"}
        for name, alias in aliases.items():
            pairs = [(lives[law, key, replicate, "learned"], lives[law, key, replicate, alias])
                     for key, replicate in expected]
            deltas = [left[0] - right[0] for left, right in pairs]
            row = {"reader_alias": alias, "paired_episodes": len(pairs),
                   "matching_full_public_histories": sum(a[1] == b[1] for a, b in pairs),
                   "mean_turn_difference_learned_minus_alias": fmean(deltas),
                   "wins": sum(d > 0 for d in deltas), "ties": deltas.count(0), "losses": sum(d < 0 for d in deltas),
                   "common_feeder_decisions": len(common[law]),
                   "matching_common_decisions": sum(r["learned"] == r[alias] for r in common[law])}
            require(all(results["by_law"][law][name][key] == value for key, value in row.items()),
                    f"The saved {name} behavior summary differs under {law}")
            if name == "seven_opportunities":
                checked[law] = row
    return checked


def score_chapter(replay, checked, counts, digest, behavior):
    yield "# Certified return replay"
    yield ""
    yield ("The repaired device removes the old menu-match guard from the strict-return offer. "
           "The other three detectors keep their guards. The prepared action still uses mark 6.")
    yield ""
    yield f"Frozen weights SHA-256 `{digest}`."
    yield ""
    yield "| Law | Strict training receipts | Paid | Score from count | Final fitted scores | Fitted cue | Count-only cue |"
    yield "|---|---:|---:|---:|---|---|---|"
    for law, summary in checked.items():
        count = counts[law]
        yield (f"| {replay.LAW_LABEL[law]} | {count['count']} | {count['paid']} | {count['score_from_count']} | "
               f"`{summary['trained_scores']}` | `{summary['trained_selector']}` | `{count['selector_from_count']}` |")
    yield ""
    yield "A certified return has already paid its ration. Seven charged strict vetoes saturate the strict score at 7, and its first tie priority forces selection there."
    if all(row["count"] >= 7 and row["paid"] == 0 for row in counts.values()):
        yield ("For these training receipts the supplied count threshold reproduces the deployed selector. "
               "Actual feedback updates the score words. The certified-opportunity count suffices to select the deployed rule.")
    yield ""
    if behavior is not None:
        yield "| Law | Count-only matches of full histories | Lifetime ties | Count-only matches of common-path decisions |"
        yield "|---|---:|---:|---:|"
        for law, row in behavior.items():
            yield (f"| {replay.LAW_LABEL[law]} | {row['matching_full_public_histories']}/{row['paired_episodes']} | "
                   f"{row['ties']}/{row['paired_episodes']} | {row['matching_common_decisions']}/{row['common_feeder_decisions']} |")
        yield ""


def mismatch_lines(audit, export, old_type):
    obs = audit["prefixes"]["empty"].observation
    for side, words in audit["before"].items():
        current_menu = MENU_MEMORY[offered_menu(obs)]
        if words["m"] != current_menu and words["x_here"] == "01" and current_choice(obs):
            bot = old_type.from_frozen(audit["pair"]["law"], export, mode=audit["mode"]).begin_episode(training=False)
            for row in audit["prefixes"][side].rows:
                receipt = row.receipt
                bot.decide(receipt.observation)
                bot.after_turn(receipt.observation, receipt.bit, receipt.outgoing_slot,
                               receipt.energy_after, training=False)
            bot.checkpoint(obs)
            require(dict(bot.snapshot()) == words, "The old and repaired guards received different prepared words")
            old = bot.read_prepared()
            require(old == expected_bit(obs, words, audit["selector"]), "The actual old read disagrees with its guard")
            revised = audit["answers"]["original"][side]
            yield (f"The {side} history keeps M=`{words['m']}` while the current menu would match `{current_menu}`. "
                   f"Its certified return has `x_here=01`. Reading the same prepared words gives bit {old} "
                   f"under the old guard and bit {revised} under the repaired guard.")
            yield ""


def paired_chapters(record, weights, starts, digest, args, replay, old_type):
    count = 0
    displayed = None
    for family, label in (("by_law", "Frozen fitted reader"), ("control_by_law", "Preset strict-return control"),
                          ("menu_mismatch_by_law", "Old-menu-mismatch decision")):
        reports = []
        for law in (args.law,) if args.law else replay.LAWS:
            case = record.get(family, {}).get(law)
            if case is None or args.seed is not None and args.seed != case["pair"]["seed"]:
                continue
            pair = case["pair"]
            seed = pair["seed"]
            require(pair["law"] == law and seed in starts and starts[seed].source_key == pair["source_key"],
                    f"The recorded seed or source is outside the {law} mechanism fold")
            require(case["weights_sha256"] == digest, f"The {law} witness names different fitted weights")
            export = weights["policies"][law]["trained"]
            audit = replay.audit_case(case, starts[seed], export)
            mismatch = list(mismatch_lines(audit, export, old_type))
            if family == "menu_mismatch_by_law":
                require(mismatch, f"The saved old-menu-mismatch replay has no certified mismatch under {law}")
            lines = [*replay.transcript(audit), *mismatch]
            reports.append((law, lines))
            count += 1
        if reports:
            if reports == displayed:
                yield f"The independently verified {label.lower()} has the same displayed trace."
                yield ""
            else:
                yield from replay.case_chapters(label, reports)
            if displayed is None:
                displayed = reports
    require(count > 0, "No recorded pairing matches the requested seed and law")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=HERE / "causal_replay.json")
    parser.add_argument("--weights", type=Path, default=HERE / "learning_weights.json")
    parser.add_argument("--training", type=Path, default=HERE / "learning_training.json")
    parser.add_argument("--bank", type=Path, default=HERE / "bank.json")
    parser.add_argument("--menu-record", type=Path, help="additional saved old-menu-mismatch comparison")
    parser.add_argument("--law", choices=("parity", "nae"))
    parser.add_argument("--seed", type=int, help="verify the recorded seed without searching for a replacement")
    parser.add_argument("--write", type=Path, help="write the verified Markdown replay")
    args = parser.parse_args()
    try:
        raw = args.weights.read_bytes()
        weights, ledger = json.loads(raw), json.loads(args.training.read_bytes())
        digest = sha256(raw).hexdigest()
        require(ledger["weights_sha256"] == digest, "The released policy differs from its training lock")
        bank, replay, training = audit_helpers()
        folds, bank_digest = bank.load_bank(args.bank)
        require(bank_digest == ledger["bank_sha256"] == weights["bank_sha256"], "Frozen bank digest differs")
        check_source_lock(weights, args, bank, digest, bank_digest)
        first = json.loads((FIRST / "bank.json").read_bytes())
        first_keys = {row["source_key"] for rows in first["folds"].values() for row in rows}
        keys = [start.source_key for starts in folds.values() for start in starts]
        require(len(keys) == len(set(keys)) and not first_keys.intersection(keys),
                "A source structure overlaps the original round or a second-round fold")
        record = json.loads(args.record.read_bytes())
        require(record["weights_sha256"] == digest and record["schema_version"] == 1,
                "The paired replay does not attest the released policy")
        menu_record = args.menu_record or HERE / "menu_mismatch_replay.json"
        if args.menu_record is not None or menu_record.exists():
            mismatch = json.loads(menu_record.read_bytes())
            require(mismatch["weights_sha256"] == digest, "The additional trace uses different fitted weights")
            record["menu_mismatch_by_law"] = mismatch["by_law"]
        checked = training.audit_training(weights, ledger, folds["train"])
        counts = opportunities(ledger, checked)
        count_record = json.loads(args.weights.with_name("learning_count_only.json").read_bytes())
        verify_count_record(count_record, ledger, counts, digest)
        behavior = check_count_behavior(args.record.parent, counts, folds["survival"], bank, digest)
        starts = {start.seed: start for start in folds["mechanism"]}
        lines = [*score_chapter(replay, checked, counts, digest, behavior),
                 *paired_chapters(record, weights, starts, digest, args, replay, training.device.first.LearnedKnotBot)]
        text = "\n".join(lines).rstrip() + "\n"
        if args.write is None:
            print(text, end="")
        else:
            args.write.write_text(text, encoding="utf-8")
            print(args.write)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
