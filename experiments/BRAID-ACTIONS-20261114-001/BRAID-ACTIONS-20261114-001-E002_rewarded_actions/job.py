"""Run the fixed-seed guided and neutral primitive-action comparisons."""

import json
from pathlib import Path
import runpy


def cases():
    yield "guided-and-neutral-27183", {}


def run(case_id, payload):
    root = Path(__file__).resolve().parents[3]
    agent = runpy.run_path(str(root / "research/BRAID-ACTIONS-20261114-001/unguided.py"))
    checkpoint = agent["fit"]()
    return {"fit": checkpoint, "assessment": agent["assess"](checkpoint)}


if __name__ == "__main__":
    print(json.dumps(run("guided-and-neutral-27183", {}), sort_keys=True))
