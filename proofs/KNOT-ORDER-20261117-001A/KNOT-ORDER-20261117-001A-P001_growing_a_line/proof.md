# How knots build an order: growing a line

Status: Proved

Ticket `KNOT-ORDER-20261117-001A`, 17 November 2026, by Claude. Epic `KNOT-ORDER-20261117-001`. `check.py` checks K1, K2 and K4
by enumeration. The proofs are below.

## Words

- **Betweenness knot.** B(a, b, c) is the knot excluding 010 and 101 on (a, b, c): b lies between a and c in the disagreement count
  (`DISTANCE-ORDER-20261117-001A`, statement 1). It is a not-all-equal knot with b read flipped, so it is pairwise.
- **Line.** A line on an order of n distinctions is the base whose states are the thresholds, the states whose values change at
  most once along the order: 2n states. It is the conjunction of B on every ordered triple, and its disagreement count is 2|i − j|.
- **The (p, q) state.** For p < q, it is the state 0…0 1…1 0…0 (and its flip) with changes after positions p and q.

## Statements

- **K1. A constraint must straddle.** In the order 1..n, a constraint of any arity that allows every threshold excludes the (p, q)
  state only if it has a place in each of the blocks [1, p], [p + 1, q] and [q + 1, n]. A line excludes every (p, q) state, so
  every such state needs a straddling constraint. That is necessary. Whether a given set of constraints is enough is checked
  directly, by the base's states.
- **K2. Local knots cannot make a line.** If every constraint's places lie in a window of r consecutive positions, the (1, r)
  state survives whenever n ≥ r + 1. For three consecutive places (r = 3), 0110 survives at n = 4.
- **K3. Growing at an end needs both ends.** Grow a line on 1..m to one on 1..m + 1 with m + 1 last.
  - Some added constraint holds the start 1 and the new m + 1, and some holds the current end m and m + 1.
  - With one knot per step, it is forced: B(1, m, m + 1).
  - So outward growth by one knot per step makes the start a hub, the one distinction in every knot. It is the reference for
    every other value: in the gauge y = x ⊕ x₁, B(1, m, m + 1) is the implication y_m ≤ y_(m+1).
- **K4. Inserting between neighbours needs only the neighbours.** B(k, new, k + 1) turns the line on 1..m into the line on 1..k,
  new, k + 1..m. A single betweenness knot keeps a line exactly at these m + 1 placements: m − 1 between neighbours and one beyond
  each end. Growing inward, "the new distinction between the last two placed", builds a line in which every distinction is in at
  most three knots, with no hub.
- **K5. The states identify the placements.** In a line, read from the disagreement counts alone, with names and growth history
  erased:
  - the ends are the pair at the largest count, 2(n − 1);
  - the neighbours are the pairs at count 2.
  So the states name all m + 1 admissible placements. Up to renaming, every placement gives the same base, a line on m + 1. The
  placement is a choice the rule makes, and no direction is stored in the result.
- **K6. The line is pairwise and a ruler.** A line is built from not-all-equal-class knots, so its pair counts and N determine it
  (`DISTANCE-ORDER-20261117-001A`, statement 3(a)). Its count 2|i − j| is an exact ruler with nothing skipped. Whatever knots
  generate it, the base implies B on every ordered triple: each distinction is related to every other.
- **K7. A two-way order from knots alone.** On an r × c grid, put B(a, b, c) on every triple with b coordinatewise between a and
  c. The allowed states are the row cuts and the column cuts, 2(r + c) − 2 of them. The disagreement count is twice the L1
  distance, and betweenness is exactly "inside the box". So the base holds two independent orders, its rows and its columns. This
  meeting pattern is given here; no growth rule for it is claimed.

## Proofs

**K1.** Compare the (p, q) state with a threshold that agrees with it outside the missed block:
- if the constraint has no place in [1, p], use the threshold that is 1 up to q and 0 after it: it agrees with the (p, q) state
  (0 on [1, p], 1 on [p + 1, q], 0 after q) on [p + 1, n];
- if it has none in [q + 1, n], use the threshold that is 0 up to p and 1 after it, which agrees on [1, q];
- if it has none in [p + 1, q], use the constant state equal to the (p, q) state's outer value, which agrees on [1, p] and
  [q + 1, n].

In each case the constraint sees, on its own places, a pattern that an allowed threshold shows, so it cannot exclude the (p, q)
state. ∎

**K2.** A window of r consecutive places meets all three blocks of (1, r) only if it contains positions 1, at least one of 2..r,
and r + 1, which is r + 1 positions. ∎

**K3.** The new (p, q) states are those with q = m: changes after p and after m, the new distinction differing from m. By K1, the
(1, m) state needs a constraint with places in [1, 1], [2, m] and [m + 1, m + 1], so it holds 1 and m + 1. The (m − 1, m) state
needs places in [1, m − 1], {m} and {m + 1}, so it holds m and m + 1. With one knot (i, j, m + 1) per step, both force i = 1 and
j = m. A three-place knot that excludes 010 on (1, m, m + 1) and keeps every monotone pattern must also exclude 101, by the flipped
states, and nothing else. So it is B(1, m, m + 1). The gauge remark: with y = x ⊕ x₁, B(1, m, m + 1) excludes y_m = 1, y_(m+1) = 0
when y₁ = 0, which is the implication y_m ≤ y_(m+1). ∎

**K4.** For B(k, new, k + 1): when x_k = x_(k+1) the new value is forced equal to them, and when they differ it is free. That
gives (2m − 2) + 2·2 = 2(m + 1) states, which are exactly the thresholds of 1..k, new, k + 1..m. For a single betweenness knot
(i, j, l) to keep a line, it must straddle every new (p, q) pattern of the new order, which forces its places to be the new
distinction and its two neighbours there (K1, as in K3). Each of the m + 1 positions gives one knot. Non-betweenness knots are
excluded by `check.py`'s exhaustive search for m ≤ 8, not by this proof. The inward spiral places each new distinction between
the two last placed, which are adjacent. Each distinction is in at most three knots: as a neighbour twice and as the new one once.
∎

**K5.** In a line the count is 2|i − j|, so the ends are the unique pair at 2(n − 1) and the neighbours the pairs at 2. ∎

**K6.** From the definitions and the earlier proof. ∎

**K7.** Every row cut and column cut is allowed: along any box triple a cut changes at most once. Conversely, an allowed state's
1-set and 0-set each contain every box spanned by two of their points (B forbids x_a = x_c ≠ x_b for b in the box), so both are
order-convex in the L1 sense. In a grid graph the subsets that are convex with convex complement are exactly the half-spaces, the
row cuts and column cuts (the halfspace fact for median graphs). There are 2(r − 1) + 2(c − 1) nonconstant ones and 2 constant
ones. Two points differ in 2 × (rows between them) + 2 × (columns between them) of them, so d = 2·L1. Betweenness is then the L1
interval, the box. ∎

## Provenance

- Betweenness axioms, and the order determined up to reversal: classical (Huntington and Kline 1917; Huntington 1924; Fishburn
  1971).
- Thresholds are the cut (split) system of a path, with d its cut metric; the grid's cuts are the split system of a product of
  paths (Buneman 1971; Deza and Laurent; median graphs).
- Deciding whether an arbitrary set of betweenness triples has a consistent order is NP-complete (Opatrný 1979). The growth here is
  easy because each step is exact.
- K1 to K5 are elementary.
- **The advisor** corrected the draft: it had claimed that every step must reach the start. Insertion between neighbours needs
  only the neighbours (K4). The advisor also gave K7 and the gauge reading of K3.
