"""Check on the shortcut used in census_p2.py: the not-all-equal history of a recorded source equals its parity history.

The engine's two laws differ only in the clause `implied = (law == parity and exactly one birth in the step)`.  census_p2.py
therefore shares the parity history with the not-all-equal law when the parity history has no step with exactly one birth.
Here the not-all-equal law is actually run, for the first five parent steps of every P2 source (all stages up to 2,100 knots),
and compared stage by stage with the parity run (knots, and every birth's number of parents and fresh distinctions).

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

STEPS = 5


def main():
    started = time.time()
    out = {}
    for name, stars in lib.recorded_sources().items():
        a = lib.grow(stars, "parity", STEPS, 20000, time_limit=100)
        b = lib.grow(stars, "nae", STEPS, 20000, time_limit=100)
        same = (a["n_at"] == b["n_at"] and a["births"] == b["births"] and a["stars"] == b["stars"]
                and a["outcome"] == b["outcome"])
        out[name] = {"steps_compared": min(len(a["births"]), len(b["births"])), "n_at": a["n_at"],
                     "identical_stars_births_outcome": same, "outcomes": [a["outcome"], b["outcome"]]}
    out["all_identical"] = all(v["identical_stars_births_outcome"] for k, v in out.items() if k != "all_identical")
    out["seconds"] = round(time.time() - started, 1)
    (lib.OUT / "p2_law_check.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
