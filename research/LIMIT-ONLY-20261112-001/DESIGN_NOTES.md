# Patterns alive only in the limit: design notes (paused, not frozen, not run)

Draft for `SHORT-DESC-20261112-001#2`, written 2026-11-12 at the coordinator's go-ahead; paused at the owner's request before any
ticket node, freeze or registered run. Nothing here is a result. No outcome was looked at: a plumbing run (1/200 of class E and
3,000 sampled tries, seed 99, scratch output) checked only counts and timing.

## Question

Nested families (SHORT-DESC's language) that die at a finite depth, with the holding knot at the bottom, while the bottomless
limit (SELF never reaching a bottom; greatest fixed point from "nothing") allows a state: the owner's "dying feels like limits".

## Settled before measuring (say so up front)

- Alive at every finite depth implies a living limit (knot inside "nothing", monotonicity); compactness and Knaster–Tarski give
  the limit as the greatest fixed point. Ours is only the other cell: finite truncations add bottom knots the limit never has.
- L1, a one-line monotonicity (Park coinduction) corollary: a limit-only family has a self-holding definition whose limit relation
  allows its three ports all equal, the one state the holding knot forbids. A code gate, not a result.
- The orbit of the knot is eventually periodic; the 0.63% and 58% of SHORT-DESC are properties of the code's weighting.

## What the advisor changed (advisor_review_answer.md)

- **L2 ("lives at every depth iff a post-fixed relation inside the knot exists") is false in general**: the orbit can leave the
  relations inside the knot (example: D = [a = b = c] ∧ SELF on three own distinctions gives NAE → all-equal → all-equal). The
  exact criterion is cycle detection on the orbit, which `dlang.fate` already does.
- **Measure instead:** how often the knot is comparable with its image Φ(knot) (where L2 holds: Φ(knot) ⊆ knot descends to the
  largest post-fixed point P below the knot; knot ⊆ Φ(knot) settles life); among incomparable cases, L2's failure rate split into
  "fixed point outside the knot" and "period above 1"; whether class E can express a failure at all. Compute P by iterating
  X ↦ knot ∧ Φ(X) (removes the 4,096-tuple cap); drop the "not all empty" clause.
- **Prior work:** Knaster–Tarski; Park (coinduction); Cousot and Cousot 1979 (iteration from seeds); Kozen's mu-calculus (least
  against greatest fixed points); Lengauer and Wanke; Courcelle and Habel–Kreowski–Vogler (HR grammars); Schaefer and co-clones.

## Code status

`census.py` (draft, beside this file): class E (every one-definition family with three ports, 0 to 3 own distinctions, 1 to 3
distinct calls, about 517,000 bodies, about 2 minutes on 8 workers) and class W (families by the description code); reads fate,
limit, L1 and the L2 tuple test. To resume: replace the tuple test with P's iteration and the comparability split above, write the
pre-registration with these as frozen measurements (L1 as a gate), create the epic, freeze, run.
