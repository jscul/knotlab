# Pre-registration: learning chooses which atom holds the leftover

Epic `ADDRESS-20261110-001` (backlog B81, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead. It also gives
`LEARN-RISE-20261110-001`'s post-hoc finding a frozen confirmation on fresh cases.

## The search (fixed in advance)

The targeted search of `research/LEARN-RISE-20261110-001/posthoc_targeted.py`, unchanged in its moves and bound: configurations are a law
and a state; a move is a state flip (A50) or a learning step at an A26 site; every configuration keeps W ≤ floor + 2. A target is chosen
first: a sign class in which the named atoms act as their lines and the others are transparent, and, by SAT, a floor state of that law
with one unit inside each named atom. Best-first search by Hamming distance to that target (law bits plus state bits); success is the
first floor configuration with a unit inside each named atom; at most 300,000 configurations.

## The cases (none used in `LEARN-RISE-20261110-001`)

- **F1, fresh two-atom starts.** K_3, line orbits 2 and 3 (that epic used only orbit 1 of K_3), atoms at l0 and at distance 1, 2 and 3:
  6 starts, target the unit inside atom 0.
- **F2, three atoms.** K_3, every line orbit, atoms at l0 and at distances 2 and 3 (genus 3, floor W = 2, two units), from the floor state
  the sight-4 learner of `GROW-STUCK-20261110-001` leaves; targets: each pair of atoms {0, 1}, {0, 2}, {1, 2} holding the two units.

## Expectations, frozen

- **F1.** The unit reaches atom 0 from all 6 fresh starts.
- **F2.** From every three-atom start, every pair of atoms is reachable as the holders of the two units: learning can place the leftovers
  in any chosen atoms, a learned address.
- **Roles.** At every success the named atoms act as their lines, or the result is one that `LAW-HOLDS-20261110-001`'s rule allows (an atom
  holding a unit acts as its line or is transparent); recorded either way.

## What would count against them

A fresh start or a named pair not reached within the cap (against F1 or F2).
