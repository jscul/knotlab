# MARK-RATE-20261116-001: predictions

Frozen at the commit that adds this file (its time is the freeze time), after the advisor's review (`advisor_design_answer.md`) and
before `run_census.py` was run. Seen before freezing: the pilot on a held-out sample drawn with seed 1116 (`exploratory/pilot.json`;
cyclic rulers r = 1: 2 of 2 pass, r = 2: 3 of 5, r = 3: 0 of 1; 4 acyclic rulers with r = 1 pass; 4 half-rate fail; rerun unchanged
after the right part's cut was tightened to the step's image of the up-feasible values), and the gate (`gate_marks.json`: 360 real
signatures from random markings at depth 7 all lie in the computed families). The pilot's 16 descriptions are excluded from the counts
below.

- **P1 (the real prediction).** At least half of the small-orbit cyclic rulers with r ≥ 2 and r0 = 0 pass the no-skip check, so their
  reach grows by at least one member per level at every depth. The pilot sits on the threshold (3 of 6).
- **P2 (tightness).** Every small-orbit acyclic ruler with r ≥ 2 and r0 = 0 passes: their reach is s + 2 wherever a chain of knots
  steps down level by level (`RULER-LEVEL-20261114-001`), so a failure would show the families too coarse.

Consistency gates, not predictions (a violation means a bug, advisor): every description with r = 1 passes; no half-rate description
passes; every passing description has census L_9(3, s) ≥ s + 1 for every decided s.
