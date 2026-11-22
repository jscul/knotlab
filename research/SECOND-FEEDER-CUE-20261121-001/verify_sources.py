"""Check local projections in every reached stage and the three structural partitions."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
B306 = HERE.parent / "FEEDER-MEMORY-20261121-001"
SOURCE = HERE.parent.parent / "experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators"
sys.path.insert(0, str(B306))
sys.path.insert(0, str(SOURCE))
from bank import select_starts, sample_pair
from fixtures import certify_source


def check():
    checked = {}
    earlier = set()
    for fold in ("train", "mechanism", "survival"):
        starts = select_starts(fold)
        keys = {start.source_key for start in starts}
        assert len(keys) == len(starts) and not keys.intersection(earlier)
        earlier.update(keys)
        totals = {law: Counter() for law in ("parity", "nae")}
        for start in starts:
            worlds = sample_pair(start, fold)
            for law in totals:
                world = worlds[law]
                assert world.source_key == start.source_key and world.law == law
                totals[law]["founders"] += 1
                totals[law]["no_first_birth"] += int(len(world.stages) == 1)
                for stage in world.stages:
                    certify_source(stage.holdings, law)
                    totals[law]["stages"] += 1
                    totals[law]["projected_holders"] += len(stage.holdings)
        checked[fold] = totals
    return {"independent_checker": "Canonical relation projected on every holder in the full reached system.",
            "unique_structures": len(earlier), "folds": checked}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "source_checks.json")
    args = parser.parse_args()
    result = check()
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
