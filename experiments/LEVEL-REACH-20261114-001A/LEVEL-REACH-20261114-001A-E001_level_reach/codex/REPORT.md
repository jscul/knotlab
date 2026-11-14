# LEVEL-REACH-20261114-001A — stage 1

Implementation and validation are in progress. Scope is stage 1 only: code,
gates, and the shared runner's 20-case smoke. No pilot or registered run is
authorized in this stage. All task writes are confined to this directory.

## Ambiguities

Both first-handoff ambiguities are resolved by the 2026-11-14 addendum.

1. E_R uses `r = min(1 + gamma(list_rng)[0], 9)`, from each list's own
   `random.Random(f"20261123-{s}-{a}-{j}")`. All 2,320 lists have been built
   and independently replayed. P remains unchanged at 998 distinct keys;
   complete R has 4,399 distinct keys. No registered scientific case ran.
2. The process ceiling counts runner workers, excluding the parent and
   each worker's one solver/checker subprocess at a time. G-mono resumes
   its saved 31/50 cases with two workers; the required smoke will use
   three workers after G-mono finishes.

Final gate accounting, smoke timings, estimates and launch commands will
replace this progress draft after execution finishes.
