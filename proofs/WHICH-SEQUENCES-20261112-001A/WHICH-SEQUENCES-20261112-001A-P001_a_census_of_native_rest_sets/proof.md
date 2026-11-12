# A census of native rest sets

Status: Proved (exact census). `census.py`, ticket A of `research/WHICH-SEQUENCES-20261112-001/preregistration.md`, frozen with the code in
commit `0954c916d` before the census ran (404 seconds).

## The test

On one copy of (2, 0, 4) (J1) and the first 12 undrawn bases of a frozen search (6 to 8 distinctions, 8 to 10 knots, 1 to 7 counting laws
each), every law with a satisfying state, whether it counts three at the base's interface, and its sums around every cyclic sequence of two
and of three knots. Sixteen rules by length (for each length: free, all 0, all 1, all equal); a rule passes on a base if a counting law is at
rest and the counting density at rest exceeds that among all laws. A null of 1,000 draws with random laws as targets. Symmetry orbits of the
sequences.

## Results (exact)

- **No rule passes on all 13 bases (R0).** The best, "all equal on sequences of two knots", passes on 2 (J1: 64 laws at rest, 4 counting,
  enrichment 8; the 6-distinction base U: 2 at rest, 1 counting); on the other 11 it leaves no counting law at rest. "All 0" on sequences of
  two knots passes on U only, "all 1" on J1 only (and leaves no law at all on 10 bases). Every rule constraining sequences of three knots
  passes on none.
- **The null:** in none of 1,000 draws did any rule pass on all 13 with random target laws (null rate 0), so the census had no chance
  pass to guard against.
- **Symmetry:** 10 of the 12 undrawn bases have no symmetry but the identity, so every law is constant on every orbit there and the test is
  empty. On the three bases with more: U (8 symmetries) and U(7, 10) seed 21 (2), the counting law's sums are constant on every orbit,
  which only 0.1% and 3.0% of all laws are; on J1 (64 symmetries, which move the interface), no counting law is, against 0.8% of all laws.

## What it says

No rule of the knots alone that fixes or equalizes the law's sums by sequence length keeps a counting law at rest across bases: what holds
the count on one base excludes it on the next. Where a base has symmetries that keep the interface's place, the counting law shares them,
and resting only at laws the symmetries fix would hold it far more densely than chance; on J1, whose symmetries move the interface, it
would exclude it.
