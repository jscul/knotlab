# Swapping the pieces' roles by learning at a rise

Status: Computed. The pre-registered breadth-first search (`check.py`, run `learn-rise-a1`, 5 minutes) stopped at its cap of 300,000
configurations on all 9 starts without reaching the target, so it is inconclusive. A post-hoc targeted search
(`research/LEARN-RISE-20261110-001/posthoc_targeted.py`, not pre-registered) answered the question.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

## Setting

Genus-2 patterns (K_2: both knot orbits; K_3: its first orbit; two Fano pieces, piece 0 at l0 and piece 1 at distance 1, 2 or 3), from the floor
state where the leftover sits in piece 1, which acts as its knot while piece 0 is transparent (`LAW-HOLDS-20261110-001`). Moves: a state flip
(A50) or a learning step at an A26 site; every configuration at most one unit above the floor (W ≤ 3).

## Results

- **Frozen search (pre-registered): inconclusive.** Breadth first reaches only about four moves deep within the cap, and no path that short
  exists.
- **Post-hoc targeted search: the leftover moves.** With a target chosen first (a class in which piece 0 acts as its knot and piece 1 is
  transparent, and, by SAT, a floor state of that law with the unit inside piece 0), a best-first search over the same moves, guided by the
  Hamming distance to the target, reached a floor configuration with the unit inside piece 0 from all 9 starts, expanding 225 to 812
  configurations. The paths take 16 to 43 moves, 4 to 16 of them learning steps and the rest state flips. At the end piece 0 acts as its
  knot and piece 1 is transparent in 7 cases; in 2 both pieces are transparent, where `LAW-HOLDS-20261110-001` allows the unit in either.

So learning at a rise, with the state moving, carries the leftover from one pattern to the other: the learned roles change, and the
tension follows them.

## Against the pre-registration

R1 is not settled by the frozen test (capped); the post-hoc search finds it true on all 9 starts. R2 held in kind (every path has both
learning steps and flips) and failed in length: only 2 of the 6 K_2 paths take at most 20 moves, and the paths found are not shortest.

## Scope

K_2 and K_3 (first orbit), two Fano pieces (A48), moves of A50 and A26 at most one unit above the floor (A49).
