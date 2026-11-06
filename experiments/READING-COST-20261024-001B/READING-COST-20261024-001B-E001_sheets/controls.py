#!/usr/bin/env python3
"""Controls of READING-COST-20261024-001B-E001, run before the producer; writes controls.json next to the rows.

(i)   The three certified witnesses of WALLS-WITH-CHOICES-20261024-001D-P001 (placement 159, 3 x 4, twist 11) come out misjudged:
      walls.c (the frozen engine) reports their class as contradicting, and the truth procedure finds 3, 3 and 5 sheets.
(ii)  The sampling engine is the frozen engine: on 200 sampled configurations (placements 159 and 155, tori 4 x 4 and 4 x 5),
      walls_sample and walls.c report the same pattern.
(iii) A class that simple cycles serve has an assignment: for 200 such (configuration, class) pairs the truth procedure finds one.
"""

from __future__ import annotations

import json
import random
import subprocess
from pathlib import Path

import run

FROZEN = run.ROOT / "experiments/WALLS-WITH-CHOICES-20261024-001B/WALLS-WITH-CHOICES-20261024-001B-E001_simple_cycles/walls.c"
WALLS = run.OUT / "walls_frozen"


def frozen_pattern(R, L, M, q, x):
    out = subprocess.run([str(WALLS), str(R), str(L), str(M), str(q[0]), str(q[1]), str(x), str(x + 1), "0"]
                         + [str(v) for c in run.CLASSES for v in c], capture_output=True, text=True, check=True).stdout.split("\n")
    return int(out[1].split()[0])


def sampled(R, L, M, q, n, seed):
    out = subprocess.run([str(run.ENGINE), str(R), str(L), str(M), str(q[0]), str(q[1]), str(n), str(seed), "0"]
                         + [str(v) for c in run.CLASSES for v in c], capture_output=True, text=True, check=True).stdout.split("\n")
    return {int(a): int(b) for a, b in (line.split() for line in out[1:] if line)}


def main() -> int:
    run.OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run(["gcc", "-O2", "-std=c99", "-o", str(WALLS), str(FROZEN)], check=True)
    subprocess.run(["gcc", "-O2", "-std=c99", "-o", str(run.ENGINE), str(run.HERE / "walls_sample.c")], check=True)
    controls = {}
    # (i)
    ok = True
    for x, c, m in ((7860857, (2, 1), 3), (7985754, (0, 1), 3), (6433130, (1, 2), 5)):
        k = run.CLASSES.index(c)
        ok &= bool(frozen_pattern(159, 3, 4, (1, 1), x) >> k & 1)
        ok &= run.truth(159, 3, 4, (1, 1), x, c) == ("assignment", m)
    controls["the three witnesses come out misjudged with 3, 3 and 5 sheets"] = ok
    # (ii) and (iii)
    rng = random.Random(20261024)
    same, served_ok, served = True, True, 0
    for R in (159, 155):
        for L, M in ((4, 4), (4, 5)):
            q = (1, 1)
            mask = (1 << (2 * L * M)) - 1
            seed = rng.randrange(1 << 60)
            pats = sampled(R, L, M, q, 50, seed)
            # replay the same draws: splitmix64 from the seed
            state = seed
            xs = []
            for _ in range(50):
                state = (state + 0x9E3779B97F4A7C15) & ((1 << 64) - 1)
                z = state
                z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
                z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & ((1 << 64) - 1)
                xs.append((z ^ (z >> 31)) & mask)
            for x in xs:
                p = frozen_pattern(R, L, M, q, x)
                same &= p == pats.get(x, 0)
                odd = [k for k, c in enumerate(run.CLASSES) if (q[0] * c[0] + q[1] * c[1]) % 2 == 1]
                for k in odd:
                    if not (p >> k & 1) and served < 200 and rng.random() < 0.6:
                        served += 1
                        served_ok &= run.truth(R, L, M, q, x, run.CLASSES[k])[0] == "assignment"
    controls["the sampling engine reports the frozen engine's patterns"] = same
    controls["classes served by simple cycles have assignments"] = served_ok and served > 0
    (run.OUT / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
    print(json.dumps(controls, indent=1), "served pairs checked:", served)
    return 0 if all(controls.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
