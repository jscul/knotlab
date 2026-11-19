"""Find exclusive nonmeetings across two actual parent blocks; verify the literal names."""

import argparse
import hashlib
import json
import random
from pathlib import Path

from precision_lift import indices, read_blocks, verify


def rectangles(parent_sets, blocks, seed, trials, pilot=False):
    rng = random.Random(seed)
    feasible = [i for i, row in enumerate(blocks) if len(row) >= 36]
    record = {"k": 0}
    for trial in range(trials):
        p, q = rng.sample(feasible, 2)
        pp, qq = set(blocks[p]), set(blocks[q])
        left, right = sorted(pp - qq), sorted(qq - pp)
        if min(len(left), len(right)) < 24:
            continue
        if len(right) > 1300:
            right = sorted(rng.sample(right, 1300))
        if len(left) > 3100:
            left = sorted(rng.sample(left, 3100))
        by = {}
        for j, v in enumerate(right):
            bit = 1 << j
            for h in parent_sets[v]:
                by[h] = by.get(h, 0) | bit
        full = (1 << len(right)) - 1
        reps = {}
        for x in left:
            seen = 0
            for h in parent_sets[x]:
                seen |= by.get(h, 0)
            missing = full ^ seen
            if missing and missing != full:
                reps.setdefault(missing, x)
        choices = sorted(reps, key=int.bit_count)
        for repeat in range(3):
            available = full
            private = []
            used = []
            order = sorted(choices, key=lambda a: a.bit_count() * (0.5 + rng.random())**(1 + repeat))
            for missing in order:
                share = missing & available
                if share and all(old & ~missing for old in private):
                    private = [old & ~missing for old in private]
                    private.append(share)
                    used.append(missing)
                    available &= ~missing
            if len(used) > record["k"]:
                witness = [[reps[a], right[(b & -b).bit_length() - 1]] for a, b in zip(used, private)]
                record = dict(k=len(used), trial=trial, repeat=repeat, source_blocks=[p, q],
                              source_block_sizes=[len(pp),len(qq)], arcs_examined=[len(left),len(right)],
                              distinct_missing_patterns=len(reps), pairs=witness)
                if pilot:
                    print("best", len(used), "trial", trial, flush=True)
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--trials", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20261119094)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--pilot", action="store_true")
    a = parser.parse_args()
    n, blocks = read_blocks(a.folder / "age8.txt")
    parents = json.loads((a.folder / "parents8.json").read_text())
    data = rectangles(parents, blocks, a.seed, a.trials, a.pilot)
    verify(n, blocks, data["pairs"])
    data.update(seed=a.seed, trials=a.trials,
                stage_sha256=hashlib.sha256((a.folder / "age8.txt").read_bytes()).hexdigest())
    # The exact held count is produced by the ticket's separately checked block accounting.
    output = Path(__file__).resolve().parent
    parts = output.parents[2] / "artifacts" / output.parent.name / output.name / "parts8.json"
    held = json.loads(parts.read_text())["held_maximal_blocks"]
    data["deterministic_unheld_lower"] = 2 ** data["k"] - held
    if a.out:
        a.out.write_text(json.dumps(data, indent=2) + "\n")
    print({k:v for k,v in data.items() if k != "pairs"})
