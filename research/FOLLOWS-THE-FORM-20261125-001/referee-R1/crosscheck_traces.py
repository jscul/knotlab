"""Compare each literal birth in the two hand examples with the independent growth."""
from argparse import ArgumentParser
import json
from pathlib import Path

from growth_engine import grow

parser = ArgumentParser(description=__doc__)
parser.add_argument("--pilot", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parent
cases = [side for pair in json.loads((root / "trace_births.json").read_text()) for side in pair]
births = 0
for case in cases[:1] if args.pilot else cases:
    run = grow(case["start"], case["first_seed_size"], ration=case["ration"],
               treatment=case["treatment"], take=case["take"], max_rounds=2)
    for recorded, rebuilt in zip(case["rounds"], run.rounds, strict=True):
        for a, b in zip(recorded["births"], rebuilt.births, strict=True):
            desc = {1: "first", 2: "second", 3: "both"}[b.ancestry]
            assert [a[k] for k in ("knot", "parents", "given", "taken", "fresh", "demand", "descent")] == [
                b.knot, list(b.parents), list(b.given), list(b.takes), list(b.fresh), b.demand, desc]
            births += 1
print(f"{births} literal births agree")
