"""Apply comparison A's pinned observability experiment to comparison B's founder bank."""

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
FIRST = HERE.parent
FIRST_PANEL = "556397b444006af255f3fcbec6f246cf8a143d9527344d4fef3bf8e2fb064008"
FIRST_DESIGN = "b2c980a20d5a843088f1034ad478bd47de4da957dc22e19e4974152cbbdd929c"
FIRST_BANK = "777e6f04863a7d7e1a20b638714db875cf9da141e61bc029df55e6e9c3ed2a9a"


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def frozen_input(path, expected):
    blob = path.read_bytes()
    if sha256(blob).hexdigest() != expected:
        raise ValueError(f"The expansion of comparison A must use the recorded {path.name}.")
    return blob


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True, help="weights frozen before fresh play")
    parser.add_argument("--policy-sha", required=True)
    args = parser.parse_args()
    if sha256(args.policy.read_bytes()).hexdigest() != args.policy_sha:
        parser.error("the supplied policy differs from its release hash")
    frozen_input(FIRST / "panel.py", FIRST_PANEL)
    frozen_input(FIRST / "panel_design.md", FIRST_DESIGN)
    a = json.loads(frozen_input(FIRST / "bank.json", FIRST_BANK))
    b = json.loads((HERE / "bank.json").read_bytes())
    previous_keys = {row["source_key"] for rows in a["folds"].values() for row in rows}
    new_keys = {row["source_key"] for rows in b["folds"].values() for row in rows}
    if len(previous_keys) != 128 or previous_keys & new_keys:
        raise ValueError("Comparison B requires a new founder bank disjoint from all 128 earlier founders.")
    required_exclusions = set(a["excluded_keys"]) | previous_keys
    if not required_exclusions <= set(b["excluded_keys"]):
        raise ValueError("The new bank omitted an archived structural exclusion.")

    bank = load_file("equal_exit_return_cue_bank", HERE / "bank.py")
    for fold in ("train", "mechanism", "survival"):
        if [s.source_key for s in bank.select_starts(fold)] != [row["source_key"] for row in b["folds"][fold]]:
            raise ValueError(f"The published {fold} fold differs from the executable founder selection.")
    inherited = load_file("equal_exit_original_panel", FIRST / "panel.py")
    inherited.HERE = HERE
    inherited.select_starts = bank.select_starts
    inherited.sample_pair = bank.sample_pair
    inherited.movement_tape = bank.movement_tape
    inherited.main()

    path = HERE / "panel_results.json"
    result = json.loads(path.read_text())
    result.update(comparison="B", comparison_A_panel_sha256=FIRST_PANEL,
                  comparison_A_design_sha256=FIRST_DESIGN, excluded_A_founder_count=len(previous_keys))
    path.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
