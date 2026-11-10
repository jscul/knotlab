# Where a dissonance sits among atoms

Status: Proved by hand (theorem 1); the rest is computed (`check.py` checks 2 to 4). Pre-registered in
`research/ATOM-LAYERS-20261110-001/preregistration.md`. Before the frozen run, one construction test built one genus-2 space of K_2 (atoms at
l0 and at distance 2) and printed its starting dissonance and its host census; nothing else was read.

## Setting

Fano atoms (`stuck_lib.grow_any`) at one or two lines of K_2 and K_3; the sphere's flat state at l0 extended to the atoms and held fixed;
levels as in the pre-registration (sphere upper, atoms lower, mixed faces junctions); the W-lowering learner with sight 4 (A49, A26).

**Theorem 1 (the floor unit is frozen; proved).** On a genus-2 space a state at the floor W = 1 has no violated line and no even face, and
exactly one face whose agreeing corners number three, every other face one. It offers no learning step, so a learner that keeps the state
fixed cannot move it.

*Proof.* The count gives violated − E + |D|/2 = −1 and W = violated + E + |D|/2 = 1, so violated + |D|/2 = 0 and E = 1. No face is even, so
every agreement count is odd, and the one unit of E is a face with three. A learning step needs a violated line or an even face. ∎

## Computations (20 genus-2 spaces and 10 genus-1 spaces, every line orbit of K_2 and K_3)

- **Theorem 1 checked** on all 15 floor states reached.
- **Host census.** The floor unit can sit inside an atom on all 20 genus-2 spaces, at a junction on all 20, and at an upper face on only 10
  (atoms at l0 and at distance 2 or 3): with the atoms adjacent, or both away from l0, no upper face can hold it.
- **One atom.** Grown at l0, the violated line starts inside the atom and the learner resolves it in 3 sign changes (5 of 5). Grown away
  (distance 2), the violated line stays at the upper level and the learner is stuck at W = 2 without a single step (0 of 5): the
  resolution exists and passes through the atom (`GROW-HANDLE-20261110-001` theorem 4), but it is longer than sight 4 (8 sign changes on
  K_2 at distance 2).
- **Two atoms.** With an atom at l0 the learner reaches the floor (15 of 15) in 3 sign changes, all inside that atom; the remaining unit
  is an over-agreeing face inside the other atom (14) or at its junction (1), present there since the second atom was grown. With both atoms
  away the learner is stuck at W = 3 (0 of 5).

So the dissonance moves down a level, by growth at the dissonance at once, or by learning along a walk through the atom when the learner
sees far enough; it does not move back up or across to another atom, because at the floor it is frozen and a W-lowering learner never
raises it. Each atom beyond the first holds its own unit from the moment it is grown.

## Against the pre-registration

B1 held. B2 did not: upper faces can hold the unit on only half the spaces. B3 held at l0 and failed away from it (sight 4 is shorter than
the resolution). B4: the floor was reached only with an atom at l0 (15 of 20), and there the unit ended inside an atom, as expected.

## Scope

K_2 and K_3, at most two atoms of A48's kind, the learner of A26 with A49's weight and sight 4.
