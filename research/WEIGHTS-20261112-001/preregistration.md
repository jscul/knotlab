# Two unlengthened shifts beyond one box: pre-registration

Epic `WEIGHTS-20261112-001` (`SHIFT-COUNT-20261112-001` direction 2; G17 with G1, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead. Committed before the registered run. The canonical K1–K3 test is unchanged. The advisor
model was consulted on the design before freezing; what it changed is listed below.

## The question

Under COMMON-FOLD's weighting (uniform r-sets of the 171 knot kinds in [0, 2] × [−2, 2]) 146 of 169 travelling bases have two
certified unlengthened shifts. Is that the rule for random samples under other declared weightings, or a feature of one box?

## The weightings (fixed before any look)

- **Kinds.** The 738 sets of three offsets up to translation in [0, 3] × [−3, 3]; 171 of them are the old box's. D(k), the
  L∞ diameter of a kind, runs from 1 to 6; the old box's kinds have D up to 4.
- **W2(r, β).** A sample draws kinds one at a time without replacement, each with probability proportional to exp(−β D(k)) among
  those left; its bases are the first r = 3, 4, 5 kinds (nested prefixes). β = 0 is the uniform weighting over the larger box; β = 1
  and β = 2 prefer short knots. This one-parameter family is the natural "short knots preferred" family, chosen because the kinds'
  diameter is the one size the box sets; it is reported across β, not tuned. Kind mix by diameter in a pilot of 20 unregistered
  samples at r = 5 (seeds 70500 to 70519, a design quantity): β = 0 mostly D 3 to 6; β = 1 mostly D 2 to 3; β = 2 mostly D 1 to 3.
  The three are correlated (shared kinds and seeding scheme), not three independent confirmations.
- **Seeds and stopping.** random.Random(70000 + 1000 w + i) for weighting w and sample i; per weighting, samples until at least 40
  travelling bases with a kind outside the old box are classified, or 300 samples.

## What is settled by definition

- Under β = 0, the bases whose kinds all lie in the old box are distributed exactly as COMMON-FOLD's W(r): that **old-box stratum**
  replicates the old census and is reported separately; the primary endpoint is the **new-kinds stratum** (a kind outside the old box).
- The certificates are sound and certified counts are lower bounds within the search family; "no second direction found" is relative
  to it.

## The pipeline (frozen in `experiments/WEIGHTS-20261112-001A/`)

COMMON-FOLD's classification unchanged (its read_base); for travelling bases SHIFT-COUNT's certified second-direction search (main
arm); where the main arm finds no certified second direction, an enlarged arm (sets of 2 to 4 cells in [0, 3]², primitive shifts with
entries up to 8). Calibration: the enlarged arm on COMMON-FOLD's 23 travelling bases with one certified direction. Reported, never
ranked against each other: certified second direction (main or enlarged), forced but uncertified, and none found; the travelling rate
per weighting (the denominator); both strata.

## Predictions and failure criteria

- **W1 (primary, per weighting, new-kinds stratum).** Among travelling bases, the share with two certified directions: **pass** if
  its Wilson 95% lower bound is at least 50% and its point estimate at least 70%; **fail** if the Wilson upper bound is below 70%;
  else inconclusive. Prediction: pass under all three weightings. "The rule holds beyond one box" fails if any weighting fails.
- **W2.** The old-box stratum under β = 0 gives a share within the old census's Wilson interval at r = 3 to 5 (a replication check;
  small denominators are reported as such).
- **W3 (calibration).** The enlarged arm adds a certified second direction to at most 5 of the old census's 23 one-direction bases (if
  more, the old search was the limit, and the old 86% is a lower bound by more than that).
- **Validity.** At least 40 travelling new-kind bases per weighting, else that weighting is inconclusive by size; at most 20% dropped.

## Changed by the advisor's critique

The new-kinds stratum as the primary endpoint (the old-box stratum replicates the old census); an enlarged search arm on the misses
and its calibration on the old census; the travelling rate reported as a finding; β widened to 1 and 2 after tabulating the kind
mix; three-way outcome per weighting instead of overlap with 86%; a minimum denominator by a stopping rule; the weightings not
counted as independent.

## Runtime

Hours on 6 workers; each sample saved as it finishes, capped at 3,600 s; registered in `docs/LONG_RUNNING.md`.

## Workspace assumptions

- **Relied on.** A64, A67, A71 (each random process is one weighting of many), A76.
