"""Compare the ordinary birth's implication flag with explicit old words."""
import argparse
import sys
from itertools import product
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
for directory in ("NAE-GROWTH-20261119-001B", "FORBIDDING-JOIN-20261120-001B"):
    experiment, = (ROOT / "experiments" / directory).glob("*-E001_*")
    sys.path.insert(0, str(experiment))

import naelib
import rival_growth


def allows(row, word, law):
    values = [word[d] for d in row]
    if law == "parity":
        return sum(values) % 2 == 0
    return min(values) != max(values)


def check(law, rounds):
    stage = ((0, 1, 2),)
    for t in range(1, rounds + 1):
        start = perf_counter()
        new, info = rival_growth.grow(stage, law, "ordinary", naelib)
        assert info["status"] == "funded"
        n = max(d for row in stage for d in row) + 1
        allowed = [w for w in product((0, 1), repeat=n) if all(allows(row, w, law) for row in stage)]
        implied_count = 0
        for birth in info["births"]:
            implied = all(allows(birth["inputs"], w, law) for w in allowed)
            assert implied == birth["old_inputs_already_imply_law"]
            demand = birth["D"]
            expected = demand if implied else max(1, 3 - len(birth["inputs"]), demand)
            assert birth["f"] == expected
            implied_count += implied
        print(law, t, "old words", len(allowed), "births", len(info["births"]),
              "implied", implied_count, f"{perf_counter() - start:.6f} s")
        stage = new


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    for law in ("parity", "nae"):
        check(law, 1 if args.pilot else 3)
