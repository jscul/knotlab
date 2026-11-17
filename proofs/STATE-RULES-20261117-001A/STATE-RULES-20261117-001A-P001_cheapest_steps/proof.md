# What the cheapest steps keep and make

Status: Proved

Ticket `STATE-RULES-20261117-001A`, 17 November 2026, by Claude. Epic `STATE-RULES-20261117-001`. Statements S1 to S5 are proved
below; S6 is the advisor's derivation, stated as a conjecture and checked by ticket B. Ticket B's frozen computation checks every
statement on its cases.

## Words

- **Base.** A set of allowed states on distinctions 0..n−1, built from betweenness knots. B(x, y, z) excludes 010 and 101 on
  (x, y, z): y lies between x and z. Such a base is complement-closed and holds both constant states. Its N states, up to flipping,
  are its **splits** (two-sided partitions of the distinctions), plus the constants.
- **Step.** A step adds distinction p with a set of betweenness knots, each on a triple containing p. An **extension** is the set of
  states the knots leave. It is admitted when:
  - every old state still extends;
  - p is constrained (N′ < 2N);
  - p is not tied to an old distinction (equal to it in every state).
- **Orientation.** On a line 0..n−1 with splits s_t = {0..t−1} | {t..n−1}, p's orientation on s_t is L (p with {0..t−1}) or R. The
  old point x has orientation R on s_t for t ≤ x and L for t > x, so its pattern is R^x L^(n−1−x): monotone.
- **Orders.** The splits' crossing graph joins two splits when all four of their intersections are non-empty.
  - k is its chromatic number, the least number of trees.
  - λ is the least number of chains of nested oriented splits covering all splits. That is the least number of lines whose product
    holds the distinctions with the disagreement count as twice the L1 distance: Eppstein's lattice dimension, computed as s minus a
    maximum matching of the semicube graph.
  - "Two orders" means k = λ = 2. A line is λ = 1, a tree k = 1.
- **Disagreement count.** d(u, v) is the number of states in which u and v differ. It is even, at least 2 for untied distinctions,
  and at most N − 2, since the constants agree everywhere.

## Statements

- **S1. Single-knot costs.**
  - B(u, p, v) leaves N′ = N + d(u, v): p is forced to u's value where u = v, and free elsewhere.
  - B(u, v, p) leaves N′ = 2N − d(u, v): p is forced to v's value where u ≠ v, and free elsewhere.
  - So every single knot leaves at least N + 2 states. N + 2 is reached exactly by a **subdivision**, B(u, p, v) with d(u, v) = 2,
    and by a **pendant**, B(u, v, p) with d(u, v) = N − 2 (u and v separated by every split).
- **S2. One knot per step keeps the number of orders.** If a base has an adjacent pair (d = 2), then every fewest-states one-knot
  step keeps k and λ, and the new base again has an adjacent pair. So from the line of three, the 2 × 2 cut system and the
  three-leaf star, (k, λ) stays (1, 1), (2, 2) and (1, 2) at every size, in every run.
- **S3. One step from a line makes at most two orders.** Every admitted extension of a line, with any number of knots, has k ≤ 2
  and λ ≤ 2. It is a line exactly when it is one of the n + 1 placements, all at N + 2.
- **S4. The zero-cost steps of a line.** With at most three betweenness knots, the admitted extensions of a line on n with N′ = N
  are exactly the C(n, 3) **fills** F(a, c, b) = {B(a, p, b), B(c, a, p), B(c, b, p)}, a < c < b. Each makes two orders. From one
  knot (n = 3) there is exactly one: the 2 × 2 cut system.
- **S5. The first two cheapest three-knot steps from one knot.**
  - The fewest-states rule with up to three knots per step reaches the 2 × 2 cut system at n = 4 with certainty.
  - At n = 5 its options are exactly 8 extensions at N + 2, the 4 subdivisions and the 4 pendants, in two classes.
- **S6 (conjecture; the advisor's derivation).** Under that rule:
  - the probability of two orders is 1/2 at n = 6 and 0 at n = 7;
  - the base at n = 2^d is the cube Q_d in every run, so the number of orders grows like log₂ n.

## Proofs

**S1.** For B(u, p, v), the excluded patterns 010 and 101 on (u, p, v) bite only where u = v, and there they force p = u. The
other d(u, v) states allow both values. So N′ = (N − d) + 2d. For B(u, v, p), the patterns bite only where u ≠ v, and there they
force p = v; so N′ = d + 2(N − d). Since 2 ≤ d ≤ N − 2, both are at least N + 2. Equality holds for the first iff d = 2, and for
the second iff d = N − 2. ∎

**S2.** By S1 the fewest-states one-knot steps are subdivisions and pendants. Deleting p gives back the old split system. Crossings
and nestings survive restriction, so neither k nor λ can drop. It remains to show they cannot rise.
- **A subdivision.** Let X be the one split separating the adjacent pair u, v, with u on side A and v on side B.
  - p is free on X's two states and equals u = v elsewhere. So X becomes two splits, A ∪ {p} | B and A | B ∪ {p}, and on every
    other split p joins the side holding u and v.
  - Each copy crosses exactly the splits X crossed: p joins a part that already holds u or v. The two copies are nested with each
    other. So they are non-adjacent twins in the crossing graph and take X's colour: k is unchanged.
  - In a chain through X, oriented …Y ⊂ A ⊂ Z…, no Y contains u: it would then separate u from v, but X is their only split. So
    p ∉ Y, and p ∈ Z. The chain becomes …Y ⊂ A ⊂ A ∪ {p} ⊂ Z…: λ is unchanged.
  - u and p are adjacent.
- **A pendant.** Let u and v be separated by every split.
  - p is forced to v's value on every non-constant state and free on the constants. It copies v, plus the trivial split {p}.
  - A trivial split crosses nothing, so k is unchanged.
  - In any chain, v lies in all of the oriented sides or in none. If v ∈ X₁ but v ∉ X₂ ⊇ X₁, impossible; and if v ∉ X₁ but v ∈ X₂,
    then u ∈ X₁ ⊂ X₂ while u, v are separated by X₂. Orient a chain so that v is in every side. Then {p} ⊂ X₁ ∪ {p}, and {p} heads
    the chain: λ is unchanged.
  - v and p are adjacent.

The three starts have adjacent pairs, and their (k, λ) are (1, 1), (2, 2) and (1, 2) by direct reading. ∎

**S3.** Every old state extends with p = 0, p = 1 or both. So each old split s_t reappears with p on its left (the L-copy,
{0..t−1} ∪ {p}), on its right (the R-copy) or as both copies. The constants add the trivial split {p} when they allow both
values.
- L-copies are nested among themselves, and so are R-copies.
- An L-copy of s_i and an R-copy of s_j cross exactly when i < j. Then p lies in {0..i−1} ∪ {p} but not in {0..j−1}, and the other
  three intersections hold points of the line.
- For i ≥ j the two copies are nested.
- {p} is nested with every L-copy.

So the L-copies (with {p}) form one chain and the R-copies another: λ ≤ 2. All crossings run between the two chains, so k ≤ 2.

A line on n + 1 distinctions has 2(n + 1) = N + 2 states, all its splits in one chain. So exactly one complementary pair of
states is doubled, and nothing crosses.
- **If it is a split's pair, s_t.** p sits between t − 1 and t: an insertion between neighbours.
- **If it is the constants' pair.** p copies an old point x, plus {p}. That is a chain only when x is an end.
- **Two doubled splits.** These cross (the L-copy of the first and the R-copy of the second).

These are the n + 1 placements (`KNOT-ORDER-20261117-001A`, K4). A pendant at an inner point is a tree (k = 1, λ = 2). ∎

**S4.** N′ = N means p is forced on every state, so it has an orientation on each split.
- **The constants need a middle knot.** End-role knots leave p free there, so some B(u, p, v) is present. It forces R on the splits
  left of u and L on those right of v, and nothing in between.
- **An end-role knot B(w, x, p)** forces one interval, the splits between w and x, all to x's side: R when x > w, L when x < w.

With at most three knots, at least one of them middle:
- **One middle knot and two end knots.** The middle knot leaves (u, v] open, and two constant intervals must cover it, since
  overlapping opposite values kill a state.
  - If one value covers it, p's pattern is monotone, a tie.
  - If R comes before L, the pattern is again monotone.
  - Otherwise the pattern is R^a L^i R^j L^r with i, j ≥ 1. That is F(a, c, b) with c = a + i and b = c + j, and its three knots
    give exactly this pattern.
- **Two middle knots.** Their open intervals must meet, or the splits between them are forced both ways. They leave the intersection
  open, which one end knot can cover only with one value: monotone again.
- **Three middle knots.** Monotone.

The patterns R^a L^i R^j L^r with i, j ≥ 1 are counted by four parts summing to n − 1, two of them positive: C(n, 3). Each has an L
before an R, so two splits cross, and by S3 k = λ = 2. For n = 3 the one fill is the 2 × 2 cut system. ∎

**S5.** n = 4 is S4 at n = 3. The 2 × 2 cut system has two splits and all four orientations occupied, so a zero-cost step would be
a tie, and N′ ≥ N + 2.

N′ = N + 2 means p is free on exactly one complementary pair of states:
- **One split's pair.** Then that split doubles, with p between the copies and its side on the other split fixed. These are the 4
  subdivisions, one knot B(u, p, v) on each of the 4 adjacent pairs.
- **The constants.** Then p's orientation is a corner's, plus the trivial split {p}. These are the 4 pendants, each B(opposite
  corner, corner, p).

All are admitted and distinct as state sets. The subdivisions form one class and the pendants another, under the square's
symmetries. ∎

**S6** is not proved here. The advisor's derivation:
- **At n = 6.** Every unoccupied orientation of the three splits is forceable by three knots from both n = 5 classes. Forceability
  only grows with the points present.
- **The two orders at n = 6.** Subdivision then fill gives two orders for 1 of 3 zero-cost options, pendant then fill for 2 of 3:
  1/2 in all.
- **Doubling.** From a full Q_d, the N + 2 steps are d·2^(d−1) subdivisions and 2^d pendants. In both classes every unoccupied
  orientation is again forceable, so the cube refills by n = 2^(d+1).

## Provenance

- **Classical.**
  - Split systems and compatibility: Buneman 1971; Bandelt and Dress 1992.
  - Median graphs embedded in products of trees iff the crossing graph is k-colourable: Bandelt and van de Vel 1989.
  - Lattice dimension of partial cubes by a matching: Eppstein 2005.
  - Every graph is a crossing graph: Klavžar and Mulder.
- **Local.**
  - The cost formulas and the line placements are from `KNOT-ORDER-20261117-001A`.
  - S2's conservation, S3, S4's count and S5 are new as far as I know, and so is the reading in the program's terms.
- **The advisor** gave S2's twin argument (k), S4's "any three points, not only neighbours", the n = 5 count and S6. It corrected
  its own first claim that three-knot steps cost N + 2 like single ones: the fills cost nothing.
