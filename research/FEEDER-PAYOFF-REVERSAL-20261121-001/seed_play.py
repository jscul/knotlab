"""Play or independently replay a sealed held-out feeder episode."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from source_bank import BANK_PATH, HERE, LAWS, load_bank, movement_tape, sample_pair
from survival import READERS, TAPES, play_common_path, play_episode
from training import load_words


def replay(start, law, version, mirror, replicate, arm, weights, digest, *, common=False):
    world = sample_pair(start, "heldout")[law]
    tape = movement_tape("heldout", start.source_key, replicate)
    if common:
        result = play_common_path(world, tape=tape, version=version, mirror=mirror, weights=weights, capture=True)
    else:
        result = play_episode(world, tape=tape, version=version, mirror=mirror, arm=arm, weights=weights, capture=True)
    return {"schema": "feeder-payoff-seed-replay-v1", **asdict(start), "law": law,
            "version": version, "mirror": mirror, "replicate": replicate, "tape": tape,
            "arm": None if common else arm, "common": common, "weights_sha256": digest, **result}


def _transcript(result):
    code = "mirrored" if result["mirror"] else "ordinary"
    tag = "shared current-only path" if result["common"] else result["arm"]
    if not result["common"] and result["mounted_version"] is not None:
        tag += f" fitted in version {result['mounted_version']}"
    yield f"{tag} | {result['law']} | access version {result['version']} | {code} labels | seed {result['seed']} | tape {result['tape']}"
    for index, decision in enumerate(result["decisions"], 1):
        public, private = decision["public"], decision["spectator"]
        obs = public["observation"]
        role = public["arrival_cue"] or "unknown"
        labels = ",".join(str(slot) for slot in obs["slots"]) or "none"
        issued = "ON" if public["bit"] else "OFF"
        if private["consumed"]:
            action = "ate one ration"
        elif private["denied"]:
            action = "charged closed attempt"
        elif private["action"] == "eat":
            action = "charged empty attempt"
        elif private["action"] == "refused":
            action = "move refused"
        else:
            action = f"moved through anonymous slot {public['outgoing_slot']}"
        offers = ""
        if result["common"]:
            offers = " | proposed " + " ".join(f"{arm}={bit}" for arm, bit in decision["proposed_bits"].items())
        elif decision["physical_action_word"] is not None:
            offers = f" | action word {decision['physical_action_word']}"
        yield (f"{index:3} | feeder {int(obs['feeder'])} | arrival {role} | previous {obs['previous']} | "
               f"controls {labels} | issued {issued}, {action} | energy {obs['energy']} → {public['energy_after']}{offers}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", default=BANK_PATH, type=Path)
    parser.add_argument("--weights", default=HERE / "learned_words.json", type=Path)
    parser.add_argument("--weights-sha256")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--law", choices=LAWS, default="nae")
    parser.add_argument("--version", "--world-version", type=int, choices=(0, 1), default=0)
    parser.add_argument("--training-version", type=int, choices=(0, 1),
                        help="Choose which fitted outcome word to mount before the world starts")
    parser.add_argument("--mirror", action="store_true")
    parser.add_argument("--replicate", type=int, choices=range(TAPES), default=0)
    parser.add_argument("--arm", choices=READERS, default="outcome")
    parser.add_argument("--common", action="store_true", help="Use one current-only path to query all mounted readers")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    saved = json.loads(args.verify.read_bytes()) if args.verify else None
    pinned = args.weights_sha256 or (saved["weights_sha256"] if saved is not None else None)
    if pinned is None:
        parser.error("Supply the sealed --weights-sha256 or a saved replay record.")
    words, digest = load_words(args.weights, pinned)
    folds, bank_digest = load_bank(args.bank)
    if words["input_sha256"]["source_bank.json"] != bank_digest:
        parser.error("The supplied bank differs from the fitted source lock.")
    starts = {start.seed: start for start in folds["heldout"]}
    if saved is not None:
        result = replay(starts[saved["seed"]], saved["law"], saved["version"], saved["mirror"],
                        saved["replicate"], saved["arm"], words, digest, common=saved["common"])
        if result != saved:
            parser.exit(1, "The replay differs from the saved full decision history.\n")
        print(f"Verified {len(result['decisions'])} complete decision records.")
    else:
        seed = args.seed if args.seed is not None else folds["heldout"][0].seed
        if seed not in starts:
            parser.error("The source seed is outside the sealed held-out bank.")
        arm = args.arm
        if args.training_version is not None:
            if args.common or arm not in ("outcome", "crossed"):
                parser.error("A training version selects an outcome word for a natural game.")
            arm = "outcome" if args.training_version == args.version else "crossed"
        result = replay(starts[seed], args.law, args.version, args.mirror, args.replicate, arm, words, digest,
                        common=args.common)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if not args.quiet:
        print("\n".join(_transcript(result)))
    turns = result["common_turns"] if result["common"] else result["turns"]
    meals = result["end"]["meals"] if result["common"] else result["meals"]
    print(f"{turns} turns | {meals} rations | death")


if __name__ == "__main__":
    main()
