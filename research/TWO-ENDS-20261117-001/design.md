# TWO-ENDS-20261117-001: design

Epic `TWO-ENDS-20261117-001` takes direction #1 of `CARRIER-20261117-001` at the coordinator's go-ahead (2026-11-17 21:19 UTC). It
serves G17, with G1. Setting: the addressed not-all-equal patterns with orbits of at most four addresses of Theorems W, F, K and K\*
(`DIRECT-REACH-20261115-001`, `BLOCK-REACH-20261116-001`, `KEEP-REACH-20261117-001`, `CARRIER-20261117-001`), top level k = 3, and
L_N(k, s) the least bond of P_N meeting levels k and k + s, with r = N − k − s the remaining depth below the lower level.

The advisor checked the plan before the freeze (`advisor/plan_question.md`, `advisor/plan_answer.md`). Its repairs are adopted below,
marked (advisor).

## Prior work

`READ-RULE-20261114-001` proved a pumping dichotomy for nested families: per residue of s, bounded or a positive linear lower bound,
by pumping finite semigroup states along words. Pumping finite semigroup states is classical (regular languages, tree automata). New
here would be the transfer to addressed patterns of finite depth, where the depth tiers pin a third end, and the normal form with its
constants.

## Part A: theory

- **Lemma S (segments).** A step relation from a saturated orbit to one child depends only on the orbit's type and the child. The
  state of a downward path is its current type with the composite of its step relations; there are finitely many, M. The lengths of
  paths from one state to another form an eventually periodic set, with threshold T and period dividing Q = lcm(1..M).
  - (advisor) A replacement path starts at the same child of its special orbit, so two segments from one branch point never collide.
- **Theorem N (normal form, three ends).** For every c there is K(c), about c²(T + Q), such that a bond of at most c members meeting
  levels k and k + s can be moved, keeping its size and the two levels, until every member lies within K(c) blocks of:
  - the top region (levels at most k);
  - the lower member's orbit;
  - or an orbit of the bottom band (remaining depth below R = r₀ + 1).

  The proof works on the tree spanned by these anchors. Length moves only between segments of length at least T (advisor). A branch
  point that cannot move is already within O(c·T) of an anchor (advisor). Hanging subtrees with no anchor only shorten. The third end
  stays: bottom-band members cannot be moved without changing their tier, and the advisor sees no way to remove them.
- **Theorem D (dichotomy, per fixed r).** On each residue of s modulo Q, L_N(k, s) with N = k + s + r is eventually bounded, or at least
  s / (2(T + Q + 1)) − const. The proof pumps a level window (advisor): T + Q + 1 consecutive levels between k and k + s, at remaining
  depth at least R and holding no special orbit. Every segment crossing the window is lengthened by Q, which moves s and N up by Q and
  keeps r. Such a window exists unless the bond is large. Theorem N is not needed for D (advisor).
- **Lemma R (depth).** The same window below the lower level gives L(s, r + Q) ≤ L(s, r) once r exceeds a threshold depending on
  L(s, r).
- **Corollary.** "L ≤ c at every depth" is decidable in principle for each c, by a finite-state check over normal-form bonds with
  Lemma R for the tiers. No feasible bound on M, T or Q is claimed in general. For the 13 the real automaton is computed (Part B).
- **Growth test (advisor).** Suppose every composite of at least ℓ₀ steps that can cross a member-free window is a product, for every
  crossing. Then the allowed states factor across any member-free window of ℓ₀ levels, a bond cannot straddle it, and
  L ≥ s / ℓ₀ + 1. That is a finite computation.

## Part B: computation

- **B1.** The saturated composite automaton, by breadth-first search over (type, composite) along every child choice. It is run on the
  13 mutants of 8db5da810c00, their parent, the 12 patterns of CARRIER and a control sample of census patterns that forget. Read off:
  - M, the threshold T and the period Q;
  - whether every composite of at least ℓ₀ steps is a product, which would prove linear growth by the test above;
  - which non-product composites lie on cycles of the automaton.
- **B2.** CARRIER's pending certified runs are folded in: bound 7 at depth 12 for −79 (`CARRIER-A6`), and depth 13, bound 6 for −73
  (`CARRIER-A5`). Any bond of 7 found is located in the tree of orbits.
- **B3, the third end (advisor).** Exact L at fixed s for several r ≥ r₀, where readings exist: depth 11, 12 and 13. A difference
  would show the third end at work.

## Stop rule

Close when Part A is written and checked against the computations, and B1 to B3 are read. The epic does not need to settle the 13 if
B1's growth test fails. If it fails, the note records which composite on a cycle stands in the way.
