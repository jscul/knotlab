# Referee job SHIFT-LOCK-R1: the brief

The coordinator handed this job over on 2026-11-12 at 12:01 UTC. It comes from the harmony thread, for the epic
`SHIFT-LOCK-20261112-001` (commits d19d72131 and 49130bac0). The ring rule is credited to LOOP-LOCK-R1 and is not redone here.

## The owning thread's risks, in its order

1. **The 78 cells.** These are mixed-knot cells in 10 harmonies: they unlock, but no non-constant state repeats along a short step.
   Recompute them with independent code. The automorphism check covered only 50 cells; the two largest harmonies, with 28 cells
   between them, were not covered.
2. **The after-run claims:** the wedge, the 0011 rule, and the 0011 + 01 slope rule.
3. **The checks:** G1 on 945 of 945 cells, the ring ties on 403 of 405, and the Ledrappier control.
4. **Wording:** "carry no influence" and "influence still travels around cycles".
5. **A77,** the reading of a short step as a walk around one cycle.

## The coordinator's questions

- (i) Is it 10 harmonies or 11?
- (ii) Is the result built in by definition, or already known?
- (iii) Which claims were frozen before the run, and which came after it?
- (iv) For each headline, is it proved or computed?
