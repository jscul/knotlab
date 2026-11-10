# Pre-registration: a temporary rise

Epic `RISE-ESCAPE-20261110-001` (backlog B72, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## The question

In `MOVING-STATE-20261110-001` a unit settled at the genus-2 floor wandered under state flips that keep the floor, but only inside its own
atom. Can it leave if the dissonance may rise for a few steps?

## Two readings

- **As recorded (state fixed, learning only).** At the genus-2 floor there is no violated line and no even face (`ATOM-LAYERS-20261110-001`
  theorem 1), so no learning step exists, whatever rise is allowed. Expected proved: the answer is no.
- **With the moving state (A50).** Between steps the state flips one point; a flip may raise W to the next value for at most k consecutive
  steps, then W must be back at the floor. On genus 2, W = 2E − 1 is odd, so the next value is the floor plus 2 (one more over-agreeing
  unit).

## The test

On the 15 genus-2 floor states of `ATOM-LAYERS-20261110-001` (atoms at l0 and at distance 1, 2 or 3; K_2 and K_3), with the law fixed:
breadth-first search over states reached by single flips, each state allowed W ≤ floor + 2, with at most k consecutive steps above the
floor, k = 2, 4, 6 and unbounded; at most 200,000 states each. Read which faces hold the unit in the floor states reached, by level and
atom, and the least k at which a unit inside the other atom or at the upper level is reached.

## Expectations, frozen

- **E1 (proved).** State fixed: no learning step at the floor, so no escape.
- **E2 (computed).** With the moving state and a rise of one unit, the unit reaches the other atom from every floor state: the trap is a
  barrier of one unit, not a wall. The least k is small (at most 6) on K_2.
- **E3 (computed).** Where the census of `ATOM-LAYERS-20261110-001` found upper hosts, the unit also reaches the upper level.

## What would count against them

A floor state from which no k up to unbounded reaches the other atom within the cap (against E2: the trap would be a wall at this rise),
or upper hosts never reached (against E3).
