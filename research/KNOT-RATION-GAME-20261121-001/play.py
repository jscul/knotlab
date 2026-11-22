"""Play an entire seeded game, verify a saved episode, or render a spectator movie."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from game import episode
from policies import get_policy, load_model
from world import sample_world


HERE = Path(__file__).resolve().parent


def play(seed, law, bot, tape=0, model_path=None):
    model = None
    if bot == "learner":
        model_path = Path(model_path) if model_path else HERE / "model.json"
        model = load_model(model_path)
    world = sample_world(seed, law, rounds=2)
    result = episode(world, get_policy(bot, model), tape=tape, sensor=bot in ("sensing", "learner"), trace=True)
    result["policy"] = bot
    if bot == "learner":
        result["model_sha256"] = sha256(model_path.read_bytes()).hexdigest()
    return result


def transcript(result):
    law = "not-all-equal" if result["law"] == "nae" else "parity"
    yield (f"{law} | seed {result['seed']} | tape {result['tape']} | {result['policy']} bot | "
           f"{len(result['initial_holdings'])} founders | starts at K{result['start_holder']}")
    for e in result["events"]:
        g = e["growth"]
        if g is not None:
            if g["births"]:
                births = []
                for b in g["births"]:
                    parents = ", ".join(f"K{h} via d{d}" for h,d in b["payments"])
                    births.append(f"K{b['holder']} from {parents} (+1 ration)")
                yield f"  Formation {g['formation']} | " + " / ".join(births)
            else:
                yield f"  Growth {g['status']} | no births"
        food = {None: "blind", True: "yes", False: "no"}[e["food_sensor"]]
        if e["action"] == "eat":
            act = "ate one ration" if e["consumed"] else "tried eating; empty"
        else:
            act = f"slot {e['slot']} via d{e['distinction']} to K{e['holder_after']}"
        yield (f"{e['turn']:3} | K{e['holder_before']:<3} | food? {food:<5} | {act:<32} | "
               f"energy {e['energy_before']} → {e['energy_after']}" + (" | died" if e["terminal"] else ""))
    yield f"{result['turns']} turns played, {result['meals']} rations consumed."


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=208304)
    p.add_argument("--law", choices=("parity","nae","not-all-equal"), default="nae")
    p.add_argument("--bot", "--policy", choices=("blind","random","sensing","learner"), default="sensing")
    p.add_argument("--tape", type=int, default=0, help="Movement and decision randomness for the episode")
    p.add_argument("--model", type=Path, help="A saved Q model (default: the study's model.json)")
    p.add_argument("--out", type=Path, help="Save the complete replay JSON")
    p.add_argument("--render", type=Path, help="Render the replay as an animated GIF or MP4")
    p.add_argument("--verify", type=Path, help="Regenerate this JSON replay from its own seed, tape and policy")
    p.add_argument("--quiet", action="store_true", help="Print only the final score")
    args = p.parse_args()
    if args.verify:
        with args.verify.open() as f:
            saved = json.load(f)
        result = play(saved["seed"],saved["law"],saved["policy"],saved["tape"],args.model)
        if saved != result:
            p.exit(1, "Replay differs from the regenerated episode. Check its source, tape, bot and model.\n")
        print(f"Verified all {result['turns']} turns.")
    else:
        result = play(args.seed,"nae" if args.law=="not-all-equal" else args.law,args.bot,args.tape,args.model)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    if args.render:
        from spectator import render_replay
        render_replay(result,args.render)
    if args.quiet:
        print(f"{result['policy']} | {result['turns']} turns | {result['meals']} rations | {result['reason']}")
    else:
        print("\n".join(transcript(result)))


if __name__ == "__main__":
    main()
