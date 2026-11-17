"""Referee R1 for KEEP-REACH-20261117-001: are the third-class read-outs' finite cut-offs enough?

  .venv/bin/python -B referee_cutoffs.py > referee_cutoffs.json

(b) analyze_third.py reads actual-value forgetting on the orbit states (type, Up) of levels jmin..16, at stable remaining depth. Every
level's set of orbit states is a function of the previous level's, so the sequence of sets is eventually periodic; levels <= 16
cover every level exactly when the sequence has entered its cycle by then. For each of the 39 third-class patterns this reports r0
(the depth from which feasibility is constant: r0 = 0 means every remaining depth is stable) and the level from which the orbit
state sets repeat, with their period.
(c) The "hidden" verdict reads the top pair states at s = 13..16 only. The pair-state sequence from level 3 is eventually periodic
(two_orbit.every_depth_cross gives its start and period); s = 13..16 covers its cycle when start <= 13 and period <= 4. Reported for
the 12 hidden and the 13 product patterns, with a re-read of non-product / hidden over one full cycle where it is longer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "exploratory"))
sys.path.insert(0, str(HERE.parents[2] / "research/DIRECT-REACH-20261115-001/exploratory"))
from two_orbit import every_depth_cross  # noqa: E402
from window_tree import WindowTree, level_states  # noqa: E402


def level_cycle(tree, upto=60):
    F = tree.feasible(20)
    r0 = next(r for r in range(19) if F[r] == F[r + 1])
    Fc = F[r0]
    st = level_states(tree, upto, [Fc] * (upto + 2))
    seen = {}
    for j in range(upto + 1):
        key = frozenset(st[j])
        if key in seen:
            return r0, seen[key], j - seen[key], max(len(st[i]) for i in range(j + 1))
        seen[key] = j
    return r0, None, None, None


def main():
    third = json.load(open(HERE.parent / "third_class.json"))["third"]
    out = {}
    for idx, v in third.items():
        tree = WindowTree(v["key"])
        r0, start, period, width = level_cycle(tree)
        row = {"kind": v["kind"], "r0": r0, "orbit_states_cycle_start": start, "orbit_states_period": period,
               "levels_to_16_cover_all": start is not None and start + period - 1 <= 16, "max_orbit_states": width}
        if v["kind"] != "forgets on actual values":
            e = every_depth_cross(tree, 3)
            row.update(pair_start=e["start"], pair_period=e["period"],
                       s13_16_cover_cycle=e["start"] <= 13 and e["period"] <= 4)
        out[idx] = row
        print(idx, row, flush=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
