# Local steering rules and the force between the two halves: interpretation

Run of `RESIGN-STEER-20261107-001B-E001` (exploratory; `contract.json`), 935 seconds. Every decision in the contract came out
positive. Pilot runs before freezing had seen the rules up to K_8, the landscapes, the K_12 fit and the ascent up to K_6
(contract, feasibility disclosure); K_10 for the rules, K_16 for the fit and K_7–K_8 for the ascent were first run here.

## Rules

| Sphere | strict | sideways | no reversal | random | decoy |
| --- | --- | --- | --- | --- | --- |
| K_2 | 143 | 288 | 300 | 285 | 190 |
| K_3 | 110 | 272 | 300 | 253 | 125 |
| K_4 | 82 | 268 | 300 | 215 | 103 |
| K_5 | 67 | 269 | 300 | 168 | 59 |
| K_6 | 75 | 265 | 299 | 136 | 61 |
| K_7 | 52 | 249 | 300 | 118 | 42 |
| K_8 | 46 | 238 | 300 | 126 | 40 |
| K_10 | 45 | 241 | 300 | 97 | 18 |

Targets reached out of 300 within 40 m clean moves.
- **The local rule suffices.** The rule that sees only the lines at the carried even face, where each of them agrees, and the
  distance to the target, and never steps straight back, reached 2,399 of 2,400 targets, in about 2 to 2.7 moves per unit of
  start distance. Its one miss (K_6, start distance 4) reached the target in 18 moves with ten times the budget: slow, not stuck.
- **Each part of the rule matters.**
  - Strict descent stalls in most trials. The clean moves are fixed by the state, one per line at the even face, and none may lead
    nearer.
  - Allowing sideways moves recovers most trials. Forbidding the step straight back recovers the rest: the stalls were two-move
    oscillations.
- **The controls fail as they should.** The random walk, with no target signal, slows with size (285 of 300 on K_2, 97 on K_10, at
  13 to 27 moves per unit of distance). Steering toward a decoy face reaches the true target less often than the random walk on
  every sphere.
- **The moves are real sign changes.** Five no-reversal runs per sphere were replayed as sign changes on a consistent state; every
  step kept no violated line, no over-agreement and the expected two even faces.

## The count of consistent states

From a corner, an edge midpoint and an octant centre on K_4, K_6 and K_8, with every other face as the second even face:
- **Least when touching.** The least count from every source is at an adjacent face, where it equals N(T), as theorem 3 of
  `RESIGN-STEER-20261107-001A` proves for differently coloured faces. Between 91% and 98% of the other faces give more.
- **Growing with separation.** The mean of log(count / N) grows with graph distance from every source. From a corner of K_8 it is
  0.39 at distance 2, 0.82 at 4, 1.28 at 8 and 1.71 at 16.
- **Like two equal two-dimensional charges.** From an octant centre, among faces at least m/3 from every corner, the fitted slope of
  log(count / N) against log(distance) is 0.46 on K_12 (distances 2–6) and 0.49 on K_16 (distances 2–8). The stress test gives 0.51
  on K_20 (distances 2–10). Two unit holes in lozenge tilings correlate like distance^(1/2) (Ciucu's electrostatics), so the two
  halves repel like equal charges of that strength.
- **The corners attract.** The maximum from every source is at a corner, the antipodal one from a corner. At equal distance corners
  carry more states than other faces: from a corner of K_8, the four corners at distance 8 give 1.54 against a mean of 1.28 there.
- **The no-force comparator.** By theorem 3 the all-plus minor is the constant N for every pair of different colours. The excess
  of the count over it is the force.

## A learner that keeps the most states

From the split at a random line, each step moved one even face to the neighbouring face with the most consistent states, until no
move increased the count.
- **Both halves always end on corners.** All 144 runs on K_3–K_8 stopped with both even faces on corners. The chance that a random
  pair of faces is two corners is 2% on K_3 and below 0.05% on K_8.
- **Antipodal corners are the best pair.** On K_4–K_8 the largest count over corner pairs is at antipodal corners; 33 of the 144
  runs reached that pair. The rest stopped at two corners 90 degrees apart, a local maximum.
- **One size past.** The stress test adds four runs on K_9 and two on K_10, all ending on two corners.

## What this does and does not show

- **Shows.** On the octahedral spheres tested, a rule with one even face's local view and an outside target signal steers it
  anywhere. The number of consistent states acts as a potential in which the halves repel like equal two-dimensional charges and
  the corners attract them.
- **Does not show.** No theorem: the exponent and the attraction are fitted and sampled on finite spheres. The target signal is an
  observer's graph distance, not a native one (A26 of the register). Weighing laws by their number of states is a chosen measure
  (A27).
