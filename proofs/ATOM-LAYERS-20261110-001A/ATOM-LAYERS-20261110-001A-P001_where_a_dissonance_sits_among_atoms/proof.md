# Where a dissonance sits among pieces

Status: Proved by hand (theorem 1); the rest is computed (`check.py` checks 2 to 4). Pre-registered in
`research/ATOM-LAYERS-20261110-001/preregistration.md`. Before the frozen run, one construction test built one genus-2 pattern of K_2 (pieces at
l0 and at distance 2) and printed its starting dissonance and its host census; nothing else was read.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

## Setting

Fano pieces (`stuck_lib.grow_any`) at one or two knots of K_2 and K_3; the sphere's flat state at l0 extended to the pieces and held fixed;
levels as in the pre-registration (sphere upper, pieces lower, mixed faces junctions); the W-lowering learner with sight 4 (A49, A26).

**Theorem 1 (the floor unit is frozen; proved).** On a genus-2 pattern a state at the floor W = 1 has no violated knot and no even face, and
exactly one face whose agreeing corners number three, every other face one. It offers no learning step, so a learner that keeps the state
fixed cannot move it.

*Proof.* The count gives violated − E + |D|/2 = −1 and W = violated + E + |D|/2 = 1, so violated + |D|/2 = 0 and E = 1. No face is even, so
every agreement count is odd, and the one unit of E is a face with three. A learning step needs a violated knot or an even face. ∎

## Computations (20 genus-2 patterns and 10 genus-1 patterns, every knot orbit of K_2 and K_3)

- **Theorem 1 checked** on all 15 floor states reached.
- **Host census.** The floor unit can sit inside a piece on all 20 genus-2 patterns, at a junction on all 20, and at an upper face on only 10
  (pieces at l0 and at distance 2 or 3): with the pieces adjacent, or both away from l0, no upper face can hold it.
- **One piece.** Grown at l0, the violated knot starts inside the piece and the learner resolves it in 3 sign changes (5 of 5). Grown away
  (distance 2), the violated knot stays at the upper level and the learner is stuck at W = 2 without a single step (0 of 5): the
  resolution exists and passes through the piece (`GROW-HANDLE-20261110-001` theorem 4), but it is longer than sight 4 (8 sign changes on
  K_2 at distance 2).
- **Two pieces.** With a piece at l0 the learner reaches the floor (15 of 15) in 3 sign changes, all inside that piece; the remaining unit
  is an over-agreeing face inside the other piece (14) or at its junction (1), present there since the second piece was grown. With both pieces
  away the learner is stuck at W = 3 (0 of 5).

So the dissonance moves down a level, by growth at the dissonance at once, or by learning along a walk through the piece when the learner
sees far enough; it does not move back up or across to another piece, because at the floor it is frozen and a W-lowering learner never
raises it. Each piece beyond the first holds its own unit from the moment it is grown.

## Against the pre-registration

B1 held. B2 did not: upper faces can hold the unit on only half the patterns. B3 held at l0 and failed away from it (sight 4 is shorter than
the resolution). B4: the floor was reached only with a piece at l0 (15 of 20), and there the unit ended inside a piece, as expected.

## Scope

K_2 and K_3, at most two pieces of A48's kind, the learner of A26 with A49's weight and sight 4.
