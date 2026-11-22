"""Play a feeder game to death or reproduce a saved public decision replay."""

import argparse
import json
from pathlib import Path

from feeder_game import episode, recode_world, sample_world
from survival_eval import LAWS, READERS, make_reader


VARIANTS = ("original", "renamed", "transported")


def play(seed, law, reader, tape=0, *, prefix=(), variant="original"):
    if variant not in VARIANTS:
        raise ValueError(f"Unknown naming variant {variant!r}")
    world = sample_world(seed, law, rounds=2)
    transport = None
    if variant != "original":
        world, original_labels = recode_world(world)
        if variant == "transported":
            transport = original_labels
    result = episode(world, make_reader(reader, law), tape=tape, prefix=prefix,
                     trace=True, original_labels=transport)
    return {**result, "reader": reader, "policy": reader, "variant": variant}


def _prefix(word):
    if any(bit not in "01" for bit in word):
        raise argparse.ArgumentTypeError("Use 0 for OFF and 1 for ON in a preparation prefix.")
    return tuple(map(int, word))


def _transcript(result):
    yield (f"{result['reader']} | {result['law']} | seed {result['seed']} | tape {result['tape']} | "
           f"{result['variant']} names")
    for turn, (local, spectator, keeper) in enumerate(zip(result["public_history"], result["events"],
                                                          result["apparatus"], strict=True), 1):
        obs = local["observation"]
        bit = "ON" if local["bit"] else "OFF"
        note = " supplied" if local["supplied"] else ""
        if spectator["action"] == "eat":
            action = "ate one ration" if spectator["consumed"] else "tried an empty eat"
        elif spectator["action"] == "move":
            action = f"moved through anonymous slot {local['outgoing_slot']}"
        else:
            action = "move refused"
        memory = ""
        if keeper is not None:
            memory = f" | keeper {keeper['memory_before']} → {keeper['receipt']['memory_after']}"
        yield (f"{turn:3} | feeder {'yes' if obs['feeder'] else 'no'} | {obs['previous']} | "
               f"{len(obs['slots'])} slots | {bit}{note}, {action} | "
               f"energy {obs['energy']} → {local['energy_after']}{memory}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=208304)
    parser.add_argument("--law", choices=LAWS, default="nae")
    parser.add_argument("--reader", choices=READERS, default="current")
    parser.add_argument("--tape", type=int, default=0)
    parser.add_argument("--prefix", type=_prefix, default=(), help="Supplied opening bits followed by the reader's own decisions")
    parser.add_argument("--variant", choices=VARIANTS, default="original")
    parser.add_argument("--out", type=Path, help="Save the public and spectator records")
    parser.add_argument("--verify", type=Path, help="Replay the seed, tape and preparation in a saved record")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if args.verify:
        expected = json.loads(args.verify.read_bytes())
        result = play(expected["seed"], expected["law"], expected["reader"], expected["tape"],
                      prefix=expected["prefix"], variant=expected["variant"])
        if expected != result:
            parser.exit(1, "The saved replay differs from the regenerated record.\n")
        print(f"Verified all {result['turns']} decisions.")
    else:
        result = play(args.seed, args.law, args.reader, args.tape, prefix=args.prefix, variant=args.variant)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if not args.quiet:
        print("\n".join(_transcript(result)))
    print(f"{result['turns']} turns | {result['meals']} rations | {result['reason']}")


if __name__ == "__main__":
    main()
