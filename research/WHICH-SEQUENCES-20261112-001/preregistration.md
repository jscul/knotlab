# Pre-registration: which cyclic sequences to fix

Epic `WHICH-SEQUENCES-20261112-001` (backlog B161, G15 with G16; program learning), written on 2026-11-12 before the census runs, at the
coordinator's go-ahead. Frozen with the code in
`proofs/WHICH-SEQUENCES-20261112-001A/WHICH-SEQUENCES-20261112-001A-P001_a_census_of_native_rest_sets/` (`census_lib.py`, `census.py`).
Nothing is tuned after a result is read. The design follows the advisor model's view, asked cold before freezing (recorded below).

## The question

`SEARCH-AUDIT-20261112-001` found that the learner finds a target no faster than blind draws among the laws it may rest at, so the cost
of finding is the number of laws at rest per target law. A rest set chosen by the knots alone, without knowing the target, would cut that
cost only if it holds the target's laws more densely than all laws do. `NATIVE-GRADE-20261112-001` found that fixing the law's sums on the
shortest cyclic sequences of knots and distinctions leaves no counting law at rest on two of three undrawn bases. Is there any rule of
this kind, the same on every base, that raises the density of counting laws beyond chance?

## What the advisor model said before freezing (a colleague's view, checked)

- The laws modulo flipping a distinction and complementing a knot are fully described by their sums around cyclic sequences, so every
  rule of "fix these sums" kind gives an affine set of laws, or an empty one; "all equal" gives a union of two. Checked: each base's law
  count is 2^(places − distinctions − knots + 1).
- A proper rest set containing even one target law has enrichment about 2^codimension / (target laws), so "enrichment above 1" mostly
  means "contains a counting law". With many rules and few target laws, some rule can pass by chance: hence a null with random laws as
  targets, the family frozen in advance, and many bases.
- The finest rules the knots alone can state are by symmetry orbits of sequences: if a counting law's sums are not constant on an orbit,
  no rule fixing or equalizing that orbit can hold it. That is an impossibility test.
- These points are folded in below. The advisor's call used the CLI's default model, because the model name given to it was not
  recognized; noted for the record.

## The bases (frozen)

One copy of (2, 0, 4) (J1, interface 0, 1, 4, read 5) and the first 12 hits of a frozen search: sizes (distinctions, knots) in the order
(6, 7), (6, 8), (7, 8), (7, 9), (8, 9), (8, 10), (7, 10), (8, 11), (9, 11), (9, 12), seeds 0 to 199 in each, a hit being
`UNDRAWN-LEARN-20261111-001`'s rule: a random pattern of distinct three-place knots, connected, whose plain law has a satisfying state and
does not count at the interface, where some law counts three (the interface is the first such set). The search is structure only; it
reads nothing about any rule.

## The census (frozen; exact)

For each base: every law with a satisfying state; whether it counts three at the interface (with either constant); its sums around every
cyclic sequence of two knots and of three knots.

1. **Rules by length**, the same on every base: for sequences of two knots, and separately for sequences of three, one of free, all sums
   0, all sums 1, all sums equal: 16 rules, 15 besides "free / free". For each rule and base: laws at rest, counting laws among them,
   expected blind draws (laws at rest per counting law), enrichment (counting density at rest over counting density among all satisfiable
   laws).
2. **A rule passes on a base** when at least one counting law is at rest and the enrichment is above 1. **It passes** when it passes on all
   13 bases.
3. **The null:** 1,000 times (seed 0), each base's counting laws are replaced by as many satisfiable laws drawn at random, and the 15 rules
   are applied; the null rate is the share of draws in which some rule passes on all 13.
4. **Symmetry orbits:** each base's symmetries (permutations of its distinctions carrying its knots to knots) and their orbits on the
   sequences; the share of counting laws whose sums are constant on every orbit, against the share among all satisfiable laws.

## Readings (frozen)

- **R1, a native rule:** some rule passes on all 13 bases and the null rate is below 0.05: the knots choose a rest set that holds counting
  laws more densely than chance.
- **R0, none in this family:** no rule passes on all 13 bases.
- **Chance:** some rule passes but the null rate is 0.05 or more.
- **Orbits:** if counting laws are no more often constant on every orbit than all laws are, the base's symmetry gives no native handle on
  the count; if they are, symmetry is a candidate for a native rest set (reported, not a mark).

Not settled by definition: whether a target-independent rule holds counting laws is what the census decides; the null calibrates chance.

## Prediction

R0: no rule by length passes on all 13 bases (on two of three undrawn bases already none fixing the shortest sums holds a counting law).
Counting laws no more orbit-uniform than all laws.

## Caps

Exact and expected well under ten minutes; one run, 30-minute cap, written at the end (a single file).

## Stop

R1, R0 or chance settled; then report, with B165 (a learner whose examples steer) ready as the next step.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58.
