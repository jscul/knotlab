# A temporary rise

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `RISE-ESCAPE-20261110-001` (backlog B72, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md). Proof family: `proofs/RISE-ESCAPE-20261110-001A/RISE-ESCAPE-20261110-001A-P001_excursions_out_of_an_atom/`
(long-running row RISE-ESCAPE-A1, run `rise-escape-a1b`).

## The question

A unit settled at the genus-2 floor inside a Fano piece wanders only inside that atom (`MOVING-STATE-20261110-001`). Can it leave if the
dissonance may rise for a few steps?

## The answer

No, not by moving the state. With the state fixed there is no learning step at the floor (proved). With the law fixed and the state
flipping one point at a time, allowed one unit of dissonance above the floor for as long as it likes, the unit never reaches the other
atom or the upper level: exhaustively on five of K_2's six components (up to 195,264 states each), and to a cap of 200,000 states on the
rest. The trap is a wall at this height, not a barrier.

A reading, not checked: with the law fixed the unit never changes atom, which suggests that the law's class decides which atom holds it.
After learning, the first atom is transparent and the second still acts as its line, and the floor unit sits in the second. If so, only a
change of law can move the unit, which means learning at a rise, where violated lines appear and learning has somewhere to act (B79).

For the owner's picture: where a pattern's leftover tension lives may be decided by what has been learned, not by where the point is; a
moving point cannot carry it out, even with room to rise.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| A fixed-state learner has no step at the genus-2 floor | proved |
| With the law fixed, flips allowed one unit above the floor never move the unit out of its atom | computed; exhaustive on five K_2 components, capped elsewhere |
| The law's class decides which atom holds the unit | a reading, unchecked (B79) |

## Against the pre-registration

E1 held. E2 and E3 failed: no escape at any excursion length. One K_3 row's "reached" came from a target that included the unit's own atom
(its unit started at a junction); read post hoc it is not an escape.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a temporary rise (B72) | **Status:** Failed | no escape at a one-unit rise, with the law fixed |
| Local direction — moving the point to move the unit | Retire | the trap holds against state moves, even with a rise |
| Broader exploration — learning program | Known alternatives | the law as the trap, learning at a rise |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Obstruction learned | a pattern's leftover tension is not carried by the point |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does the law decide which atom holds the unit (B79) | 2/3 — Substantial | 3/3 — Ready | every floor state of the fixed law, by matching census in its class → none in the other atom (the law decides), or some | Selected · awaiting go-ahead |
| 2 | Learning at a rise (B80) | 2/3 — Substantial | 2/3 — Testable | state flips and learning steps together, one unit above the floor → the unit changes atom, or not | Alternative · deferred |
| 3 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** is the cheapest discriminator for the reading above: if no floor state of the fixed law has the unit in the other atom, the trap is
  the law's, and moving it is learning's job.
- **#2** follows if #1 says so.

**Corrections:** none. **Goals:** G15 checkpoint (obstruction learned); B72 taken; B79 and B80 added. **Assumptions:** none new; A50 and A49
used.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (02:01 UTC).

**B72 done, with a negative result: a temporary rise doesn't let a settled unit escape its atom.** With the law fixed, I let the state go one unit of dissonance above the floor for as long as it liked. The leftover never reached the other atom or the sphere: I checked every reachable state on five K_2 cases (up to 195,264 states each), and found the same within a 200,000-state cap elsewhere. With the state fixed there's no learning step at the floor at all (proved). My guess is that which atom holds the leftover is set by what was learned (the law's class), not by where the point is. If so, only learning could move it. That's the cheap next check.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: temporary rise (B72) | **Status:** Failed | no escape at a one-unit rise, law fixed |
| Local direction: moving the point to move the unit | Retire | the trap holds against state moves |
| Broader exploration: learning program | Known alternatives | the law as the trap; learning at a rise |
| Long-term goal: G15 | Obstruction learned | a pattern's leftover isn't carried by the point |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does the law decide which atom holds it (B79) | 2/3 — Substantial | 3/3 — Ready | every floor state the fixed law allows → none in the other atom, or some | Selected · awaiting go-ahead |
| 2 | Learning at a rise (B80) | 2/3 — Substantial | 2/3 — Testable | state and learning steps together, one unit up → unit changes atom, or not | Alternative · deferred |
| 3 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

**Corrections:** none. **Goals:** G15 checkpoint; B72 taken; B79, B80 added. **Assumptions:** none new.
