# Pre-registration: twisted pins

Epic `TWIST-PIN-20261112-001` (`PIN-RULE-20261112-001` direction 1; G17 with G8; program mathematics, group arithmetic), written on
2026-11-12 before any census runs, at the coordinator's go-ahead under the owner's standing mandate; kept small around its one open
piece. Code frozen with this file in `proofs/TWIST-PIN-20261112-001A/TWIST-PIN-20261112-001A-P001_twisted_pins/` (`twist_lib.py`,
`check.py`). The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary: block, distinction substitution, block triples (here the block's knots in every order), between-copy
knots, spare distinction, part, tie class. New, plain: a **twist** gives member v of knot e of the pattern a symmetry g_(e,v) of the
block (a permutation of its distinctions keeping its knots), and the knot binds NAE((x, g_(e,x)(p')), (y, g_(e,y)(q')), (z, g_(e,z)(r')))
for every ordering (p', q', r') of a knot of the block (the literature's voltage or permutation-voltage assignment). The **holonomy**
of a closed walk of copies is the symmetry carried around it (the literature's word).

## What is settled by definition (by hand before the run; the advisor model's form)

- **T1 (transport).** Replacing each copy's state a by a ∘ g_(e,x) turns a twisted knot into an untwisted one, solution set and all. So
  by the pinning theorem, for every distinction p the block cannot spare, a(g_(e,x)(p)) = b(g_(e,y)(p)) = c(g_(e,z)(p)).
- **T2 (gauge).** Renaming a copy's distinctions by a symmetry, or composing one knot's three slots with one symmetry, changes nothing
  but names. Only the holonomy matters, up to simultaneous conjugation; a twist can be undone copy by copy exactly when every holonomy is
  trivial, so on a pattern with no closed chain of knots every twist undoes (the null outcome).
- **T3 (the quotient).** With H the holonomy group, the pinned values of a copy on a cycle are constant on the H-orbits of the
  distinctions the block cannot spare: **a twisted pin is ordinary pinning with the block folded by H** (the quotient block B/H). It
  can force new ties inside a copy, inequalities where a knot folds onto two orbits, or an end where a knot folds into one orbit or
  an odd chain of folded pairs closes.
- **Classes (frozen).** **Balanced:** H trivial. **N-balanced:** H moves no distinction the block cannot spare off its own tie class.
  **N-twisted:** some holonomy moves such a distinction to one not tied to it in the block.

So the varying pin the coordinator asked for exists by definition wherever an N-twisted holonomy exists: it is the quotient block's
pinning. The one piece not settled by definition is whether living depends on the length of the cycle: the advisor's exact condition
for one twisted cycle of n knots with holonomy h is that some state t of the block is within n steps of t ∘ h in the graph joining two
states when the places where they differ meet every knot at most once; this can depend on n only if some knot of the block holds two or
more spare distinctions.

## The census (frozen; small)

- The relation check: on all 87 blocks of `SUBST-NEST-20261112-001`'s census, three copies' states are allowed exactly when every knot
  of the block holds at most one place where they are not unanimous (the advisor's form of the binding).
- The 18 census blocks with a symmetry moving a distinction they cannot spare, every non-identity class of their symmetries (one twist
  on knot 0's second member), on: a chain of 4 knots (no cycle); one cycle of 2, 3 and 6 knots; two cycles of 3 knots through one
  distinction (pairs of classes, at most 6 per block); the one-shift ring of 6 and 7 distinctions with every knot's middle member
  twisted. None of these test patterns has ties of its own (checked in the run). Measured: lives, the holonomy group and its class, the
  root copy's ties inside and outside it, the quotient prediction, and for one cycle the advisor's distance.
- **Cap.** 30 minutes and 16 GB by its systemd unit.

## What counts (frozen)

- **A pin that varies:** on a test pattern with no ties of its own, an N-twisted holonomy under which the nested pattern lives with a
  tie inside a copy between two distinctions not tied in the block, or ends. (The referee's closed form already gives the block's own
  ties carried across copies; those do not count.)
- **Null:** balanced cells, and every cell on the chain of 4, identical to untwisted.

## Predictions (frozen; P2 to P6 the advisor's)

- **P1.** The relation check holds on all 87 blocks; the chain of 4 and every balanced cell match untwisted (theorems).
- **P2.** N-balanced cells: no new tie inside a copy.
- **P3.** N-twisted cells: pins that vary, as T3 says; measured ties contain the quotient's.
- **P4.** Living: the necessary condition (some state constant on the orbits of N) and the sufficient one (some state fixed by H) are
  never violated.
- **P5.** On one cycle, living agrees with the advisor's distance condition.
- **P6.** Cycles of 3 and 6 knots differ only for blocks with a knot holding two spare distinctions, and then only by living at 6 and
  not at 3.
- **P7.** Rings with the middle member twisted by an involution: removable at 6, not at 7 (the advisor's hand computation).

**Answer by rule.** P1 to P7; if P5 and P6 settle the length effect, close as a short null result and report.

## Known mathematics, checked before the freeze

Voltage and permutation-voltage graphs and derived covers (Gross, 1974; Gross and Tucker, 1977); balance and switching in signed and
gain graphs (Harary, 1953; Zaslavsky, 1982, 1989); graph bundles classified by voltages up to conjugacy (Pisanski and Vrabec; Kwak and
Lee, 1990); twisted gadgets whose twist class alone matters (Cai, Fürer and Immerman, 1992); Tseitin formulas, holonomy over Z₂; Unique
Games as permutation-voltage constraint graphs; cohomological obstructions in constraint problems and contextuality (Abramsky,
Brandenburger, Mansfield and Barbosa; Ó Conghaile, 2022); frustration and Wilson loops in physics (Toulouse).

**Referee.** The background referee thread (referee pending). Assumptions in force: A75 (Assumed). Nothing here bears on P versus NP.
