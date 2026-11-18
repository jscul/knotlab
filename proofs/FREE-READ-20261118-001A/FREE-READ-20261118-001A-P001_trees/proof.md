# Bond distance on knot trees: what is proved

Ticket `FREE-READ-20261118-001A`, 18 November 2026. Checked by ticket B's gates and frozen run
(`experiments/FREE-READ-20261118-001B/FREE-READ-20261118-001B-E001_bonds/`). Referee pending. The proofs are the thread's; the advisor
(claude-fable-5-2) checked them before the freeze, made three lemmas explicit (L1, L2 and the meaning of "third branch") and gave
the clause counterexample (C).

## Terms

A base is a set of knots, each a relation on three distinctions; its allowed states are the joint values every knot allows. A set S
of distinctions is **free** when the allowed states, every other distinction forgotten, take all 2^|S| joint values on S, and
**constrained** otherwise. Subsets of free sets are free. S is a **bond** when it is constrained (K1) and every set of |S| − 1 of its
distinctions is free (K2); K3 holds whenever the base allows some state. **Bond distance** b(x, y) is the size of the least bond
holding x and y, minus one, and is undefined when no bond holds them. It is read from the allowed states alone. It is unchanged by
renaming distinctions and by switching (renaming the two values of any distinction), since both map allowed states one to one and
keep every projection's size.

A **knot tree** is a base whose incidence of distinctions and knots has no cycle and is connected. For x ≠ y, the path between them
is x = v₀, K₁, v₁, …, K_k, v_k = y, and **steps apart** s(x, y) = k is the number of knots on it. The **third branch** T_j of K_j is
the set of distinctions reached from K_j's third distinction p_j without passing through K_j (p_j and the whole subtree hanging
there). Removing K_j splits the distinctions into three parts: L_j holding v_{j−1} (and x), R_j holding v_j (and y), and T_j.

The laws: parity (an even or odd sum), not-all-equal (forbids 000 and 111) and betweenness (forbids 010 and 101 in some order; a
switch of not-all-equal).

## L0. Pairs are free inside a knot

A three-place knot passing K2 allows every joint value of any two of its distinctions: forgetting the third leaves them free. So
given values on two of its distinctions some value of the third is allowed, and given a value on one, every value of a second has an
allowed third. All three laws pass K2. ∎

## L1. Hanging subtrees extend (advisor)

In a knot tree whose knots pass K2, let a sub-base be given by a connected set of its knots, with a state allowed by them. The
state extends to an allowed state of the whole base: add the remaining knots one at a time, each meeting the knots already added in
exactly one distinction (no cycle), and choose its two new distinctions by L0. In particular every value of one distinction extends,
so a knot tree allows some state (K3). ∎

## L2. The path chain is the base on the path (advisor)

Let P = {v₀, …, v_k, p₁, …, p_k}. The allowed states restricted to P are exactly the joint values on P allowed by K₁, …, K_k: one
inclusion is clear, and the other is L1 applied to the chain's knots. ∎

## U. Upper bound: b(x, y) ≤ s(x, y) + 1 under the three laws

Let S = {x, y, p₁, …, p_k}, of size k + 2.

*S is constrained.* Fix x and choose p₁, …, p_k in turn. Once v_{j−1} is forced, a not-all-equal K_j with p_j equal to v_{j−1}
forces v_j to the other value, and a parity K_j forces v_j = v_{j−1} + p_j + c for every p_j. So with these choices every v_j is
forced, y among them, and the joint value on S with y flipped is not allowed by the chain; by L2 it is not allowed by the base.
Betweenness is a switch of not-all-equal, and switching keeps freedom, so the same holds for it and for any mixture of the three.

*Every set of k + 1 is free.* Drop x: given any values on p₁, …, p_k and y, choose v_{k−1}, …, v₀ backward, each allowed by L0 (two
of K_j's distinctions are set, choose the third). Drop y: forward from x in the same way. Drop p_j: choose forward from x to v_{j−1}
and backward from y to v_j, then p_j is allowed for the pair (v_{j−1}, v_j) by L0. In each case L2 extends the chain's values to the
base. So S is a bond, and b(x, y) ≤ (k + 2) − 1 = k + 1. ∎

## Lo. Lower bound: b(x, y) ≥ s(x, y) + 1 for any three-place knots passing K2

Let S be a bond holding x and y, and suppose S misses the third branch T_j of some path knot K_j. Given allowed states of the
knots inside L_j and of those inside R_j, the pair (v_{j−1}, v_j) has an allowed p_j by L0, and T_j's knots extend it by L1. So the
allowed states restricted to S are every pairing of an allowed value on S ∩ L_j with an allowed value on S ∩ R_j: the projection
onto S is the product of the projections onto S ∩ L_j and S ∩ R_j. S is constrained, so one factor is not full, and that part is a
constrained proper subset of S (x is not in R_j and y is not in L_j). But every proper subset of a bond is free (K2). So S meets
every T_j. The k third branches are disjoint from each other and from x and y, so |S| ≥ k + 2 and b(x, y) ≥ k + 1. ∎

The same splitting works for knots with more places passing K2, with "a branch at K_j that S misses" in place of T_j.

## Theorem

**On every knot tree of parity, not-all-equal and betweenness knots, in any mixture, bond distance is steps apart plus one on every
pair.** (U and Lo.) In particular bond distance has no hub shortcut: a hub of any size is part of a knot tree and the theorem covers
it, unlike the cumulant distance δ (`TREE-STEPS-20261118-001A`, H2).

## C. Equality needs knots that pass a value on (advisor's counterexample)

Under the clause "not all ones" (forbid 111; K1 and K2 hold), on a chain of k ≥ 2 clauses no bond holds the two ends. Given any
values on a set S, set every distinction outside S to 0; a clause is then broken only if all three of its distinctions are in S and
set to 1. So if S is constrained it contains a whole clause, which is itself constrained; a bond containing a clause is that clause,
and a clause holds both ends only when k = 1. ∎ So the lower bound holds for every three-place knot passing K2, and equality
needs knots that pass a value on, as parity, not-all-equal and betweenness do by U.

## M. The mixed cycle

Close a not-all-equal path of k knots from x to y by a parity knot (x, y, z). Then {x, y, z} is a bond: x + y + z is fixed, while x
and y are free of each other (the path's ends, by the splitting argument of Lo applied to the path) and z appears only in the parity
knot, so every pair is free. So b(x, y) = 2 = s(x, y) + 1, whereas δ_K reads k (`TREE-STEPS-20261118-001A`). The parity knot is read
as one knot. ∎

## Parity bases

On a base cut out by parity knots, a set is free exactly when no sum of the parity checks has its support inside it, so the bonds
are the minimal supports of such sums, the circuits of the matroid of the allowed states, and b − 1 = δ = δ_K
(`CUMULANT-DIST-20261118-001A`, D1; `TREE-STEPS-20261118-001A`, K2).

## Computed, not proved (ticket B)

- On rings of three to six knots: under not-all-equal and under alternating laws, b = s + 1 on every pair; under parity, b − 1 = δ
  on every pair, and b falls below s + 1 on rings of three and four knots, where the ring's private distinctions together form a
  parity bond (the sum of all its knots).
- Post hoc (not predicted): b satisfies the triangle inequality on every pair of the 16 rings and mixed cycles; τ, which δ and δ_K
  equal there, fails it on every not-all-equal ring and δ_K on every mixed cycle.
