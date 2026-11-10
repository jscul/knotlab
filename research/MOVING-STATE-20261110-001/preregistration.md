# Pre-registration: let the state move while learning acts (a challenge of A26)

Epic `MOVING-STATE-20261110-001` (backlog B71, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead. It is the challenge
epic of assumption A26 ("a learner acts only at dissonance while the state holds still"), which every learning epic has relied on.

## The alternative and the discriminator

- **A26 (held).** The state is fixed; only the law changes, at the dissonance.
- **The alternative.** The point moves: between learning steps the state may flip one point, provided the flip does not raise the
  dissonance weight W (A49). Learning still acts only at the dissonance.
- **Where it can tell.** The spaces of `ATOM-LAYERS-20261110-001` on which the fixed-state learner was stuck or frozen: one Fano atom at
  distance 2 from the dissonance (genus 1, stuck at W = 2), two atoms away (genus 2, stuck at W = 3), and the genus-2 floor states reached
  with an atom at the dissonance (the unit frozen in the second atom). K_2 and K_3, every line orbit.

## The dynamics

- **M (moving state with learning).** Each round, the learner of `GROW-STUCK-20261110-001` (sight r = 3, W-lowering, A26 sites) takes a
  step if one lowers W; otherwise the state takes a uniformly random flip among those that do not raise W; otherwise the run stops. At
  most 150 rounds, 10 seeded runs per space (random.Random(71)). The dissonance's levels are recorded each round.
- **F (the floor component).** On each genus-2 floor state, every state reachable by single flips that keep W at the floor, by breadth-first
  search with the law fixed (at most 20,000 states): which faces then hold the unit, by level and atom.

## Expectations, frozen

- **S1 (the stuck learner is freed).** On genus 1 with the atom away, every run of M resolves (W = 0): the moving state carries the
  dissonance to where learning can resolve it.
- **S2 (two atoms away).** Every run of M reaches the floor W = 1.
- **S3 (the unit moves).** F from each frozen floor state reaches faces inside both atoms; where the census of `ATOM-LAYERS-20261110-001`
  found upper hosts, it reaches the upper level too.

## How A26 is judged (frozen)

- **Confirmed** (kept for stated reasons) if a moving state changes no outcome: no stuck run is freed and no frozen unit leaves its atom.
- **Overturned as a limit on what learning reaches** if it changes one: a stuck learner resolves, or a frozen unit reaches another atom or
  level. Then the conclusions that rested on the fixed state (the stuck learner and the frozen unit of `ATOM-LAYERS-20261110-001`) hold
  only with the state still, the moving-state reading is added to the register as its own entry, and every published claim resting on
  A26 is rechecked for a correction.
