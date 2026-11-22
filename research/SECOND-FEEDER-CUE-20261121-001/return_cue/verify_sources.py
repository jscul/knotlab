"""Run the same exact holder-projection checker on the new, disjoint founder bank."""

import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parents[1] / "FEEDER-MEMORY-20261121-001"))
from bank import select_starts, sample_pair


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=HERE/"source_checks.json")
    args = p.parse_args()
    spec = importlib.util.spec_from_file_location("first_feeder_projection", HERE.parent/"verify_sources.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.select_starts, module.sample_pair = select_starts, sample_pair
    result = module.check()
    prior = json.loads((HERE.parent/"bank.json").read_bytes())
    old = {s["source_key"] for rows in prior["folds"].values() for s in rows}
    fresh = {s.source_key for fold in ("train","mechanism","survival") for s in select_starts(fold)}
    assert not fresh.intersection(old)
    result["previous_founder_keys_excluded"] = len(old)
    args.out.write_text(json.dumps(result,indent=2)+"\n")


if __name__ == "__main__":
    main()
