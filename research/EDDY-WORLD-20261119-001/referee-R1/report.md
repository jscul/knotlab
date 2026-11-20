# Referee report, group 2: the hub-guided sample and the world line (2026-11-19 studies)

**Partly checked.** Run lean at the owner's request.

**The base-growth parts were recomputed with the referee's own engine and stand.** The state-dynamics parts were read, not
recomputed. No Block, and no new correction to these studies. Their own logged corrections (the ring-transfer arity, the
two-parent transfer condition, the same-side start date and the sampler's starting supports) are in place.

## EDDY-WORLD: a self-feeding ring in a background. The growth stands.

- **All ten cases were regrown.** The referee's engine started from each age-0 support in the study's `stages.json`. Every
  per-round birth count agrees with the study's on every common round:
  - 32 rounds for the background and the single rings;
  - 5 to 29 rounds for the joined and paired starts, up to the study's caps.
- **The background** gives 17 + 2t births per round, and the bare five-ring gives exactly 5 per round.
- **The decorated rings' late ratios** (1.12 to 1.15 and about 1.26) match the stated factors 1.1347 and 1.2628.
- **Ring spacing.** Two rings four steps apart outgrow the pair eight apart: 520 against 435 births at round 5.
- **Not rechecked:** the bond-distance and recognition readings.
- **Scaffolds:** the built path background, the attached rings and the supplied loose distinctions. The growth itself is the
  program's rule.

## HUB-GUIDED-SAMPLE: start-03's round 9 is about 9×10²⁷ knots. Stands as a sampled estimate, not a count.

- **What it is.** The 9.08×10²⁷ estimate, its empirical 2.78-fold spread over 24 replicates, and a one-sided 99% lower bound
  (5.8×10²⁷) under its design. The study says a two-sided accuracy bound is open.
- **A reason for caution:** the study's own blind controls ran low. They gave means of 761 against 1,015 and 9,377 against 28,008,
  with spreads up to 31-fold. So the upper end deserves the caution the study gives it. Its lower bound leans on an approximation
  over 24 replicates.
- **Consistent with this referee's earlier count.** The exact round-8 figures it uses (28,065 knots, 28,008 large groups) are the
  same as the referee's earlier B2 check.
- **Not rerun:** the sampler itself.
- **Scaffold:** the sampling design.

## Read, not recomputed

These are the moving pattern, the motion rules, state feeding growth, the stored ring and old marks, the ring load to the end, the
same-side reading and the detection pace (MOTION-AT-EDDY, MOTION-LAW, STATE-FEEDS-GROWTH, OLD-MARK-GEOMETRY, RING-TO-END,
SAME-SIDE-READING and DETECTION-PACE).
- **What they are about.** Each concerns a **supplied law on states or a supplied lift**: a fixed reference state with four least
  responses, the feedback law (cold knots join; an active parent vetoes), or fresh-pair lifts. All run on built starts.
- **The scaffold rule applies.** Under the program's own rule, growth reads only the arrangement and loose distinctions, as
  STATE-FEEDS-GROWTH itself says. So every "a stored state changes growth" or "a pattern moves" result is about the named added
  law, not about the model. Most of these notes predate the scaffolds line, so they do not label these as scaffolds yet. They
  should, when next touched.
- **Not recomputed:** their exact numbers, for example the 31-ring's 124-change cycle and the 37 + 2p + 2q against 39 + 2p + 2q
  formula.

## How the work was split

- **The referee:** read the decision notes and controls, and wrote `job_g2.py` (own engine).
- **Where it ran.** Under `scripts/longrun.py`: `runs/referee-g2`, with the record in `referee_g2.json`.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
