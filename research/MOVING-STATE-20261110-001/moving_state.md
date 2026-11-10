# Let the state move while learning acts

Epic `MOVING-STATE-20261110-001` (backlog B71, G15; the challenge of A26; program learning), 2026-11-10, at the coordinator's go-ahead.
Pre-registered in [preregistration.md](preregistration.md); frozen contract and run in
`experiments/MOVING-STATE-20261110-001A/MOVING-STATE-20261110-001A-E001_a_moving_state_with_learning/`; results in
`artifacts/MOVING-STATE-20261110-001A/.../run/` (run `moving-state-a1`, 11 minutes, long-running row MOVING-STATE-A1).

## The question

Every learning epic held the state still (A26). In `ATOM-LAYERS-20261110-001` that left a learner stuck when the atoms were away from the
dissonance, and froze the leftover unit inside an atom. Let the state flip one point between learning steps, never raising the
dissonance: does the point then travel?

## The answer (computed, exploratory)

- **A moving point frees learning.** With one atom away, the fixed-state learner made no step; with the state moving, 23 of 50 runs
  resolved within 150 rounds. With two atoms away, 28 of 50 reached the floor, against none. The point walks to where learning can act.
- **But a settled unit stays in its pattern.** At the genus-2 floor, every state reachable by flips that keep the dissonance at the
  floor holds the unit inside the atom it settled in or at that atom's junction faces: never in the other atom, never at the upper
  level (exhaustive on K_2, 270 states each; on K_3 to a cap of 20,000 states).

So the two-level network has a trap: dissonance flows down into a named pattern, and at constant tension it moves around inside that
pattern without leaving. Crossing to another pattern needs the tension to rise first (B72).

## A26

By the frozen rule A26 is **Overturned as a limit on what learning reaches**: a moving state changed an outcome. Its fixed-state results
stand as statements about a learner that holds the state still; every published claim resting on it was rechecked and each names the
fixed state, so none needs a correction. The moving-state reading is added as A50.

## Against the pre-registration

S1 and S2 failed as stated (every run): about half resolve or reach the floor within the budget. S3 failed: the unit never reached the
first atom or the upper level. The A26 verdict follows the frozen rule.

## Corrections

None (rechecked: the claims that rest on A26, in `GROW-STUCK-20261110-001` and `ATOM-LAYERS-20261110-001`, are stated for a learner that
holds the state still).

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — let the state move (B71, challenge of A26) | **Status:** Partially successful | frees learning; a settled unit stays in its atom |
| Local direction — learning with a moving state | Continue | the point now travels to where learning acts |
| Broader exploration — learning program | Known alternatives | temporary rises, larger networks |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | a moving point plus learning, as in the owner's picture |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learner that accepts a temporary rise (B72) | 2/3 — Substantial | 3/3 — Ready | let W rise by one for at most k steps, state moving or not → the unit crosses to the other atom or level, or no k ≤ 6 does it | Selected · started |
| 2 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | the junction faces' agreement under floor flips → a local reason the unit cannot pass, or a path | Alternative · deferred |
| 3 | Learning on an overgrown surface (B70) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** is next by the coordinator's order, and the trap makes it the natural test: does a bounded rise let the point cross?
- **#2** asks for the mechanism of the trap.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B71 taken; B78 added. **Assumptions:** A26 Overturned (as a limit on
what learning reaches); A50 added (the state moves without raising the dissonance while learning acts).
