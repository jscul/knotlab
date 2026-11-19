"""Run the generic count kernel blind on archived fixed rosters."""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from control_checks import BATCHES, spread


FIRST_SEED = 202611193000
WIDTHS = (64,256)
POLICIES = ("hub","partner")


def measure(binary, stage_folder, row, position, width, policy):
    stage = stage_folder/f"{row['name']}-age{row['age']:02d}.txt"
    digest = sha256(stage.read_bytes()).hexdigest()
    assert digest == row["blocks_sha256"]
    first = FIRST_SEED + position*BATCHES
    assert first+BATCHES <= 202611197800
    # The launched process gets the roster and parameters, never any truth field.
    command = [str(binary), str(stage), str(BATCHES), str(first), str(width), policy,
               "coverage", "32", "6", "0", "160", "0"]
    run = subprocess.run(command, text=True, capture_output=True, check=True)
    meta, *observations = map(json.loads, run.stdout.splitlines())
    assert len(observations) == BATCHES
    assert [d["seed"] for d in observations] == list(range(first, first+BATCHES))
    raw = [Fraction(int(d["weight"])) for d in observations]
    truth = row["truth"]
    measured = truth["raw_maximal_cliques"]
    additive = truth["residual_pairs"] + truth["offshoots"] - truth["held_maximal_cliques"] - truth["isolated"]
    assert measured+additive == truth["births"]
    return {"name": row["name"], "age": row["age"], "blocks_sha256": digest, "settings": meta,
            "raw_maximal_cliques": spread(raw, measured),
            "births_with_known_corrections": spread([a+additive for a in raw], truth["births"]),
            "additive_control_correction": additive, "reported_theoretical_bias": 0,
            "runs_with_population_thinning": sum(d["merges"] > 0 for d in observations),
            "negative_birth_estimates": sum(a+additive < 0 for a in raw),
            "run_records": observations}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("binary", type=Path)
    cli.add_argument("roster_index", type=Path)
    cli.add_argument("stage_folder", type=Path)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    rosters = json.loads(args.roster_index.read_text())
    controls = [r for r in rosters if r["name"].startswith("start-") and "truth" in r]
    panel = [(r,w,p) for r in controls for w in WIDTHS for p in POLICIES]
    measured = [measure(args.binary,args.stage_folder,r,j,w,p) for j,(r,w,p) in enumerate(panel)]
    args.output.write_text(json.dumps({"first_seed": FIRST_SEED, "purpose": "pilot controls outside the held-out intervals",
                                      "kernel_sha256": sha256(args.binary.read_bytes()).hexdigest(),
                                      "rows": measured}, separators=(",", ":"))+"\n")
