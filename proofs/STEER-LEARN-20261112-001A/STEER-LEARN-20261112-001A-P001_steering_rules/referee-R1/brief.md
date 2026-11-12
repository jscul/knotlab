# Referee job STEER-LEARN-R1: the brief

The coordinator relayed this job from the learning thread on 2026-11-12 at 09:19 UTC. It covers `STEER-LEARN-20261112-001` (B165),
committed with its referee pending in e62df5a31. The owner's next step, B168, does not depend on the verdict.

## The claims

1. **Blind medians and swap targets (exact).**

   | Setting | Laws at rest | Count: p, blind median | Swap target g | g: p, blind median |
   | --- | --- | --- | --- | --- |
   | F | 4 | 1/8, 6 | 0uu01uu1 | 1/16, 11 |
   | GE | 64 | 1/32, 22 | 00001111 | 1/64, 45 |

   g was chosen by the frozen closest-chance rule.
2. **No steering (computed, frozen).** None of B, P, M or A passes on the count under the frozen bar in either setting.
3. **A bias of the walk (computed).** Every rule finds g in F in about 5.5 to 6 world probes, and B passes on g. The owner reads this
   as a bias of the walk.

## What the owner asked to have checked

- That candidate checks are charged as frozen.
- The computation of the blind p.
- The median and within-blind tallies from `runs.jsonl`.
- Whether the walk-bias reading is supported, or only one explanation among several.
- Whether any result is settled by its own definition.
