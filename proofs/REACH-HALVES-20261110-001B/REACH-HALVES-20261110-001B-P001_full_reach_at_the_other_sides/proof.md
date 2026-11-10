# Full reach at the sides that are not powers of two

Status: Partial (pre-registered 2026-11-10, before the proof attempt and before the census runs).

Ticket `REACH-HALVES-20261110-001B`, epic `REACH-HALVES-20261110-001`.

## What is registered

**Target B1.** Full reach (every contact reads some contact of every ring) at every side n ≥ 3 that is not a power of two from 8: a
proof for as large an infinite family of sides as can be reached, or the obstruction stated. Known: `FULL-REACH-PROOF-20261108-001A`
Proposition 6 proves it at 3, 5, 7 and 11 (a layer's polynomial is irreducible of full degree), and at no other side to 24 does that
argument apply.

**B2, the census one size past.** Every side from 3 to 130, the powers of two 4 to 128 run exactly over a whole period of the walk
(A^P = I for the P used), the other sides stopped as soon as every contact has met every ring. The census so far: sides 3 to 48,
then 49, 50 and 64 (`FULL-REACH-20261108-001A`, `FULL-REACH-PROOF-20261108-001`'s stress test).

**Predicted before the run.** Full reach at every side but 8, 16, 32, 64 and 128. At 128, exactly 124 contacts miss a ring, each the
three rings of one corner, and 404 = 3n + 20 contacts miss some contact.

## Criteria, frozen

- **B1 proved** for a family: a proof by hand, checked exactly at every side of the family to 64, refereed.
- **B2:** the prediction holds at every side, or the first side where it fails is recorded (a failure would be a correction of the
  published census pattern).

## Planned checks

- The census code checked against the published census at 8, 16, 32 and 64 (failing sets) and at small sides, then run in the
  background as a registered long-running check.
