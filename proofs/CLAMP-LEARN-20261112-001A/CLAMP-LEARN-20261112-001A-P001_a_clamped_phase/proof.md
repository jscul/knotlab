# A clamped phase against honest baselines

Status: Proved (baselines exact; walk and runs computed, frozen). Referee pending. `check.py`, ticket A of
`research/CLAMP-LEARN-20261112-001/preregistration.md`, frozen with the code in commit `498f903cc` before any frozen run. All parts ran to
completion in one unit (baselines, the walk's 80 walks, 600 runs in `runs.jsonl`, the summary).

## The walk's bias (B169's cheap part)

The unchanged learner taught an impossible map, the map of its law read at 60 probes in each of 20 walks:

| Setting and start | Share of probes at the count's law (uniform chance) | Share at g's law (uniform chance) |
| --- | --- | --- |
| F, fixed start | 3.4% (12.5%) | 15.3% (6.25%) |
| F, random starts | 4.3% (12.5%) | 13.2% (6.25%) |
| GE, fixed start | 0.17% (3.1%) | 0.33% (1.6%) |
| GE, random starts | 0.17% (3.1%) | 0.5% (1.6%) |

From random starts the walk is as biased as from the fixed start: the bias belongs to the dynamics, not to where the runs start.

## Runs (GE, random starts, 100 seeds each)

| Rule / target | Found | Median all steps | Restricted blind median (steps) | Uniform blind median (steps) | Within the restricted median | Passes |
| --- | --- | --- | --- | --- | --- | --- |
| B / the count | 48 | not found in half | 0.97 million | 3.55 million | 4% | — |
| B / g | 73 | 14.9 million | 1.89 million | 12.1 million | 5% | — |
| C / the count | 13 | not found in half | 0.97 million | 3.55 million | 0% | no |
| C / g | 36 | not found in half | 1.89 million | 12.1 million | 3% | no |
| CA / the count | 12 | not found in half | 0.97 million | 3.55 million | 0% | no |
| CA / g | 55 | 36.9 million | 1.89 million | 12.1 million | 2% | no |

No steering shown: the clamped phase and contrastive acceptance found the count less often than the unchanged learner (13 and 12 of 100
against 48), and nothing beat even the uniform blind median in steps.

## What it says

Feeling each example's clamp during the walk does not steer this learner; it finds the count less often than without the clamp. The walk's
preference among the laws it can rest at is a property of its dynamics, the same from random starts as from the fixed one.
