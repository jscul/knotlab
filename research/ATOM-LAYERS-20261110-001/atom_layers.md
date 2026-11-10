# Layers through atoms

Epic `ATOM-LAYERS-20261110-001` (sub-goal B54; G15 with G16; program learning), 2026-11-10, at the coordinator's go-ahead; the owner flagged
the direction. Pre-registered in [preregistration.md](preregistration.md). Proof family:
`proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/`.

## The question

A Fano atom spliced in for a line acts from outside exactly as that line. Read the sphere as the upper level and each atom as a lower level
standing for one upper line. With several atoms, where does the forced dissonance sit, and does learning carry it between levels and
between atoms?

## The answer

- **Down, yes.** Growing an atom at the dissonance moves it into the atom at once, and learning resolves it there (3 sign changes). Grown
  away from the dissonance, the resolution still passes through the atom (proved, `GROW-HANDLE-20261110-001`), but it is longer than a
  learner seeing 4 steps ahead can find: that learner stays stuck at the upper level.
- **Back up or across, no (proved, then computed).** At genus 2 the remaining unit at the floor is a single over-agreeing face, with no
  violated line or even face, so no learning step exists there: it is frozen. A learner that only lowers dissonance never unfreezes it.
- **Each extra atom carries its own unit.** With an atom at the dissonance and a second one elsewhere, the learner resolves the first
  atom's pair and is left with one over-agreeing face inside the second atom, which was there from the moment the second atom was grown
  (14 of 15, the 15th at its junction).
- **Where it can rest.** The floor unit can sit inside an atom on every genus-2 space tried, but at the upper level on only half of them.

For the owner's picture: in a two-level network of this kind the point flows down into the named pattern and settles there. To move it
back up or into another pattern, something must first raise the tension: either the state moves (which A26 forbids here), or learning
accepts a temporary rise in dissonance (which this learner never does).

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| At genus 2 the floor unit is one over-agreeing face that no learning step can move | proved by hand; checked on 15 floor states |
| Growth at the dissonance puts it inside the atom; learning resolves it there | computed (and `GROW-HANDLE-20261110-001`) |
| Away from the dissonance a sight-4 learner is stuck at the upper level | computed |
| A second atom holds one unit from its birth, where the learner leaves it | computed |
| Upper faces can hold the floor unit on half the spaces, atoms on all | computed (matching census) |

## Against the pre-registration

B1 held. B2 failed: upper faces can hold the unit on only 10 of 20 spaces. B3 held at l0 and failed away from it, because sight 4 is
shorter than the resolution. B4 held where an atom sits at l0 (floor reached, unit inside an atom) and failed with both atoms away (stuck).
One construction test before the frozen run printed one space's starting dissonance and host census.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — layers through atoms (B54) | **Status:** Partially successful | dissonance flows down into atoms, never back up |
| Local direction — learning with the state fixed | Continue, with a challenge | A26 is what freezes the unit |
| Broader exploration — learning program | Known alternatives | moving state, temporary rises |
| Long-term goal — G15 Learning: a point in a learned knot space | Obstruction learned | a fixed-state, lowering learner cannot move a point between patterns |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Let the state move while learning acts (B71, challenges A26) | 2/3 — Substantial | 3/3 — Ready | state flips that keep W, between learning steps, on the two-atom spaces → the unit moves between atoms, or stays | Selected · awaiting go-ahead |
| 2 | A learner that accepts a temporary rise (B72) | 2/3 — Substantial | 3/3 — Ready | allow W to rise by one for at most k steps → the unit crosses to another atom or level, or not | Alternative · deferred |
| 3 | Learning on an overgrown surface (B70) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** is the owner's own picture most closely: a point that moves (the state) through a network that learning orients. It is also the
  first challenge of A26, which every learning epic so far has relied on.
- **#2** keeps the state fixed and asks only whether a bounded rise lets the unit travel.

**Corrections:** none. **Goals:** G15 checkpoint (obstruction learned); sub-goal B54 taken; B71 and B72 added. **Assumptions:** A26 put
under challenge if #1 is taken.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (01:08 UTC).

**B54 (layers through atoms) done: the dissonance flows down into the named patterns and settles there, but never comes back up or moves across.** I replaced one or two lines of K_2 and K_3 by Fano atoms, each acting as the line it replaced. Growing an atom at the dissonance moves it down into the atom, where learning resolves it. A second atom holds one unit of dissonance from the moment it's grown, and that's where the leftover ends. Once there it's frozen (proved): at genus 2 the leftover is a single over-agreeing face, and a learner that holds the state still has no move there. So moving the point between patterns needs something to raise the tension first.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: layers through atoms (B54) | **Status:** Partially successful | flows down, never back up or across |
| Local direction: learning with the state fixed | Continue, with a challenge | holding the state still is what freezes it |
| Broader exploration: learning program | Known alternatives | moving state, temporary rises |
| Long-term goal: G15 | Obstruction learned | a fixed-state learner can't move a point between patterns |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Let the state move while learning acts (B71) | 2/3 — Substantial | 3/3 — Ready | state flips between learning steps → unit moves between atoms, or stays | Selected · awaiting go-ahead |
| 2 | Accept a temporary rise (B72) | 2/3 — Substantial | 3/3 — Ready | allow W +1 for ≤ k steps → unit crosses, or not | Alternative · deferred |
| 3 | Overgrown surfaces (B70) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

#1 is your original picture most directly: a point that moves, through a network that learning orients. It would be the first challenge of the "state holds still" assumption every learning epic has used.

**Corrections:** none. **Goals:** G15 checkpoint; B54 taken (atom reading); B71, B72 added. **Assumptions:** A26 history line.
