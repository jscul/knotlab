"""Watch a complete held-out episode on the renamed founder and original movement draws."""

import argparse
from pathlib import Path
import json
from bank import LAWS, select_starts
from learning_train import load_frozen_weights
from survival_eval import READERS, replay_survival

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=12030535759847423040)
    p.add_argument("--replicate", type=int, choices=range(8), default=0)
    p.add_argument("--law", choices=LAWS, default="parity")
    p.add_argument("--reader", choices=READERS, default="learned")
    args = p.parse_args()
    starts = {s.seed:s for s in select_starts("survival")}
    if args.seed not in starts:
        p.error("Use a held-out survival seed from bank.json.")
    digest = json.loads((HERE/"learning_training.json").read_bytes())["weights_sha256"]
    weights = load_frozen_weights(HERE/"learning_weights.json", digest)
    result = replay_survival(starts[args.seed], args.law, args.replicate, args.reader, weights)
    print(f"Seed {args.seed}, tape {result['tape']}, {args.law}, {args.reader}")
    for row in result["events"]:
        energy = f"{row['energy_before']} → {row['energy_after']}"
        if row["action"] == "eat":
            action = "ate one ration" if row["consumed"] else "attempted an empty eat"
        elif row["action"] == "move":
            action = f"passed to K{row['holder_after']} through slot {row['slot']}"
        else:
            action = "pass refused"
        obs = result["public_history"][row["turn"]-1]["observation"]
        print(f"{row['turn']:2}  K{row['holder_before']}  feeder={int(obs['feeder'])}  "
              f"exits={len(obs['slots'])}  {action}  energy {energy}")
    print(f"Death after {result['turns']} charged turns and {result['meals']} meals.")


if __name__ == "__main__":
    main()
