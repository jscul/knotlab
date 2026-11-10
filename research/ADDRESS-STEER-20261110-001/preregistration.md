# Pre-registration: does the stored address steer later learning?

Epic `ADDRESS-STEER-20261110-001` (backlog B86, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead, as a fuller epic:
three tickets, a larger sample, the four-atom case, and failure stated in advance for each.

## Background and a fact used below

A knot sphere with g Fano atoms is a surface of genus g, and its laws have no even face. Then every state with no violated line is at the
floor: each line has one agreeing corner, so Σ agree = n, and E = (n − V)/2 = g − 1. The floor holds g − 1 units. `READ-ADDRESS-20261110-001`
found the holders were exactly the atoms acting as their lines in 23 of 24 written cases; the exception had one acting atom for two units.

## Ticket A: the rule behind the exception (exact, SAT over every state)

On three-atom spaces (K_3 and K_4, every line orbit; atoms at l0 and at distances 2 and 3) over all 64 classes, and four-atom spaces (K_3,
every line orbit; atoms at l0 and at distances 2, 3 and 4) over all 256 classes:

- **R-a.** If every atom acts as its line, no state satisfies every line.
- **R-b.** Otherwise, in every state that satisfies every line, every acting atom holds a unit: some face inside it or at its junctions has
  three agreeing corners.
- **R-c.** When fewer atoms act than there are units (a < g − 1), some such state has a unit outside every acting atom's region.

Expected: all three hold, so the rule is "each acting atom holds a unit; units beyond the acting atoms are free", and the exception is the
case a < g − 1. **Failure:** any class breaking R-a or R-b: then "the acting atoms are the address" is a tendency, not a rule.

## Ticket B: writing with four atoms (computed, the frozen targeted search)

`ADDRESS-20261110-001`'s targeted search, unchanged, on the four-atom spaces of K_3 (every line orbit), toward every triple of atoms as the
holders of the three units (4 triples each). Expected: every triple written. **Failure:** a triple not reached within 300,000
configurations.

## Ticket C: does the address steer later learning? (computed)

On every written three-atom configuration of `READ-ADDRESS-20261110-001` (K_3 and K_4, every orbit, each of the three addresses): flip k
random upper-level points (k = 1, 2, 3), then run the learner M1: each round take a uniformly random move among those that lower W if any
(state flips and learning steps at A26 sites), else among those that keep W; at most 200 rounds; 10 runs per configuration and k
(random.Random(86)). At the floor, read the address as the set of atoms holding units.

- **Expected.** The address survives: at k = 1 the final address equals the written one in at least 80% of runs on every space, falling
  as k grows. Then what was learned before decides how a new tension resolves.
- **Failure.** At k = 1 the final address equals the written one in at most a third of runs (chance among three addresses): the stored
  address does not steer later learning.
