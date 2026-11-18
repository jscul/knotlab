# What a rule that never nests its fills keeps, and when it refills

Status: Proved

Ticket `NEVER-NEST-20261118-001A`, 18 November 2026, by Claude. Epic `NEVER-NEST-20261118-001`. Written before the run.

## Words

As in `MEET-ORDERS-20261118-001A` (the line, betweenness, KF3, fills, odd sets, Lemma C) and `STATE-RULES-20261117-001A`:
- **Splits.** A split is a non-constant state together with its complement; its two **sides** are the distinctions at 1 and at
  0. A step that adds no state keeps the splits (each extended by the new distinction).
- **Crossing.** Two splits cross when all four intersections of their sides are non-empty. Adding a distinction never removes a
  crossing.
- **Chains.** A chain is a set of splits whose sides can be chosen nested. The number of orders λ is the least number of chains
  covering the splits; **two orders** means λ = 2 with a bipartite crossing graph.
- **The grid of two chains.** Let a base have two orders, with chains C₀ of a splits and C₁ of b splits, sides chosen nested
  T₁ ⊂ T₂ ⊂ ⋯ in each. A distinction lies in an up-set of each chain's chosen sides, so it has a **cell** (i, j): the number of
  C₀'s chosen sides and of C₁'s that do not hold it. Two distinctions with one cell lie on the same side of every split, so they
  agree in every state: one would be a copy of the other. So each cell holds at most one distinction, and n ≤ (a + 1)(b + 1).
  The base is a **full grid** when every cell holds one.
- **Subdivision.** One knot B(u, p, v) whose old pair differs in exactly two states, that is, on exactly one split t.
- **The rules** (`research/NEVER-NEST-20261118-001/preregistration.md`).
  - NN takes the fills after which the base has two orders, and a subdivision when there is none.
  - NNF is the same with any old pair allowed in a knot, not only pairs that already share one.
  - CC takes the **corner fills across crossing splits**, and a subdivision when there is none. A corner fill is
    {B(x, r, y), B(c, x, r), B(c, y, r)} on old distinctions where c differs from x on exactly one split t₁, from y on exactly one
    other split t₂, and t₁ and t₂ cross; then r is c with both t₁ and t₂ changed. CC reads which two splits separate c from x and
    from y, and whether those two cross.

## Statements

- **N1. A subdivision keeps the number of orders.** It replaces t by two nested splits that cross exactly what t crossed, and
  changes no other crossing. So k and λ are unchanged. NN and NNF never stall on a base with two orders (a pair differing on one
  split always exists there: two distinctions in neighbouring cells), and once they have two orders they keep them.
- **N2. Fills of triples give a full grid only with one or two middles.** On a line of m + 1 distinctions with fills of triples
  that keep two orders (Lemma C), let the h distinct middles be c₁ < ⋯ < c_h, and set c₀ = 0, c_{h+1} = m and
  gᵢ = c_{i+1} − cᵢ.
  - The fills with middle cᵢ have their ends in [c_{i−1}, cᵢ) × (cᵢ, c_{i+1}], so there are at most g_{i−1} gᵢ of them.
  - The two chains have s₀ = g₀ + g₂ + ⋯ and s₁ = g₁ + g₃ + ⋯ splits.
  - n ≤ (m + 1) + Σᵢ g_{i−1} gᵢ ≤ (s₀ + 1)(s₁ + 1). The base is a full grid exactly when h ≤ 2 and every fill these bounds allow
    is present. With h ≥ 3 middles, fills of triples alone never complete it (fills of larger odd sets can).
- **N3. From a full grid, NNF refills every new row or column, forever.** (A full grid here has both chains non-empty.)
  - On a full grid no fill keeps two orders, so NNF subdivides.
  - After the subdivision the only fills that keep two orders are the empty cells of the new row or column, and every one of
    them is a fill.
  - So NNF fills that row or column in some order and is a full grid again: it passes through a full grid after every new row
    or column, keeps two orders at every step, and never stalls. Nothing is remembered: the rule reads the states only.

- **N4. From any line, NNF reaches a full grid before its first subdivision.** On a line with fills that keep two orders, as long
  as the grid of two chains covering it has an empty cell, some empty cell r has two neighbours x, y and the corner c next to
  both occupied, and its corner fill keeps two orders. So NNF fills until the grid is full, at n = (s₀ + 1)(s₁ + 1) with
  s₀ + s₁ = n₀ − 1, and N3 takes over. From the line, NNF therefore passes through a full grid after every new row or column,
  with two orders at every step after the first.
- **N5. CC keeps two orders, refills from a full grid, and never fills a line.**
  - On a base with two orders, every corner fill across crossing splits is an empty cell of the grid, so it keeps two orders.
  - From a full grid, after a subdivision, each empty cell of the new row or column next to a filled one in it has a corner fill
    across crossing splits; so CC refills it, and from a full grid it passes through a full grid after every new row or column,
    forever.
  - On a line no two splits cross, so CC only subdivides: it stays a line. Its first crossing must be given, as the 2 × 2 pattern
    gives it.

## What each rule reads and what it is given

- **NN** reads the states and the pairs that share a knot, and checks after each candidate fill whether the base has two orders.
- **NNF** reads only the states, and checks the same. The number of orders is read from all the splits at once (k and λ). What
  the rule is given is the number two: it takes the fills after which there are at most two orders, and nothing marks which split
  belongs to which order. A rule told to keep the number of orders it has would never fill a line. *After the referee (R1,
  section 1):* it is also given the step for when no such fill exists, a subdivision, which N1 and N3 use; and NNF is the cheapest
  rule with the cap added, which uncapped makes every order (`CUBE-DOUBLING-20261118-001A`), so the two is wholly the cap's.
- **CC** reads, for each candidate, two splits near one distinction and whether they cross. Whether two splits cross depends on
  every distinction, so this is a reading of two splits, not a strictly local one (wording after the referee). It is given its
  first crossing.
- **The class law** of `LOCAL-ROOM-20261118-001` is given a class for every split, by the start and by inheritance.

## Proofs

**N1.** Let u and v lie on different sides X ∋ u, Y ∋ v of t and on one side of every other split. B(u, p, v) gives p the value
of u and v on every state where they agree, and leaves it free on the two states of t. So every split s ≠ t gains p on the side
S that holds u and v, and t becomes t_u = (X ∪ {p}, Y) and t_v = (X, Y ∪ {p}).
- *Other crossings.* For s, s′ ≠ t, and for s against t_u or t_v, p joins the intersection that already holds u (or v), so no
  empty intersection is filled: each pair crosses after exactly when it crossed before. t_u and t_v do not cross, since
  Y ∩ X = ∅.
- *k.* The crossing graph gains a second copy of t's vertex, joined to the same neighbours and not to t's copy. The chromatic
  number and bipartiteness are unchanged.
- *λ.* Take a cover by chains. Let s share a chain with t, with chosen sides nested with X (the case of Y is the same). Since u
  and v lie on one side of s, either s's chosen side lies within X and holds neither u nor v (so not p), or it holds X and
  then u and v (so p). Either way it stays nested with X and with X ∪ {p}, so putting t_v ⊂ t_u in t's chain gives a cover of
  the same size. Conversely, deleting p from a cover of the new splits gives a cover of the old ones (deletion keeps nesting, and
  t_u, t_v both become t), with no more chains. ∎

**N2.**
- *Ends.* Let f = (x, cᵢ, z) and let g be a fill with middle c′ > cᵢ. Lemma C forbids c′ ∈ (x, z), and c′ > cᵢ > x, so z ≤ c′.
  With c′ = c_{i+1} this gives z ≤ c_{i+1}; symmetrically x ≥ c_{i−1}. The bounds c₀ = 0 and c_{k+1} = m hold trivially. Two
  fills with one odd set agree in every state, so one would be a copy. Hence at most g_{i−1} gᵢ fills have middle cᵢ.
- *Chains.* Lemma C's proof colours step k (the state with the first k distinctions at 1) by the parity of the number of middles
  below k, and each colour is a chain. The steps in (cᵢ, c_{i+1}] number gᵢ and have colour i mod 2, so s₀ and s₁ are as stated.
- *Count.* n = (m + 1) + F, with F the number of fills. Each product g_{i−1} gᵢ pairs a gap of even index with one of odd
  index, a different pair for each i, while s₀ s₁ sums gₐ g_b over all such pairs. So F ≤ Σ g_{i−1} gᵢ ≤ s₀ s₁, and
  (m + 1) + s₀ s₁ = (s₀ + 1)(s₁ + 1) since m = s₀ + s₁.
- *Equality.* The second inequality is an equality exactly when every pair of an even and an odd gap is consecutive, that is,
  h ≤ 2: for h ≥ 3, g₀ g₃ > 0 is missing. The first is an equality exactly when every allowed fill is present. And with h ≥ 3, no
  fill of a triple holds a step of the first gap and a step of the fourth in different halves (a fill with middle cᵢ has its
  halves within [c_{i−1}, c_{i+1}]), so those steps never cross and the crossing graph is not complete bipartite. ∎

**N3.** Let the base be a full grid with chains C₀ (a splits) and C₁ (b splits), a, b ≥ 1. Its crossing graph is complete
bipartite: for splits T ∈ C₀ and T′ ∈ C₁, the four cells next to their meeting point hold distinctions in all four intersections.
- *(i) A fill that keeps two orders is an empty cell.* A fill keeps the splits, and the crossing graph can only gain edges. If
  it stays bipartite, its bipartition is still (C₀, C₁), since a connected bipartite graph has only one, so no two splits of one
  chain may come to cross. For nested chosen sides T ⊊ T′, three intersections are non-empty, and T \ T′ is empty. They come
  to cross exactly when the new distinction r lies in T and not in T′. So r lies in an up-set of each chain's chosen sides,
  that is, in a cell, and that cell is empty, since r is no copy. On a full grid there is no empty cell, so there is no such
  fill.
- *(ii) The subdivisions are between neighbouring cells.* Two distinctions differing on exactly one split are in cells that
  differ by one in one coordinate. Let the subdivision be between (i, j₀) and (i, j₀ + 1) across a split of C₁ (C₀ is the same).
  By N1 the base keeps two orders, with chains C₀ and C₁′ of b + 1 splits, and its crossing graph is complete bipartite. In the
  new grid the old columns up to j₀ keep their index, the later ones move up by one, and the new column j₀ + 1 holds only p.
- *(iii) Every empty cell of the new column is a fill.* For an empty cell r = (i′, j₀ + 1), the three distinctions p = (i, j₀ + 1),
  x = (i′, j₀) and y = (i′, j₀ + 2) are present. In each coordinate r's value is the middle one of theirs: i′ is the middle of i,
  i′, i′, and j₀ + 1 is the middle of j₀ + 1, j₀, j₀ + 2. So on every split r lies on the side that at least two of p, x and y
  share (the literature's median of three). The three knots B(p, r, x), B(p, r, y) and B(x, r, y) pin r, on each state, to the
  value of a pair that agrees there, and that value is r's. So every old state extends uniquely: a fill, constrained, and no
  copy because the cell was empty. It keeps two orders, since r lies in a cell (no crossing within a chain, and crossings
  between the chains were already complete). Every remaining empty cell keeps this certificate, since p, x and y stay.
- By (i) these are the only fills that keep two orders, so NNF fills the column in some order and reaches the full grid
  (a, b + 1). Then the argument repeats. ∎

**N4.** Let the base be the line 0, …, m with fills (any odd sets) and two orders, and take any cover by two chains C₀ and C₁. For
each split choose the side holding distinction 0. Two steps k < l of one chain do not cross, and three of their four intersections
hold 0, m and the line distinctions k, …, l − 1, so the fourth is empty and P_k ⊂ P_l. So the chosen sides are nested along each
chain; 0 has cell (0, 0) and m has cell (s₀, s₁), where s₀ + s₁ = m; and the line's distinctions occupy cells along a path P whose
cells increase by one in one coordinate at each step. Each empty cell lies on one side of P, say below it.
- *A minimal empty cell.* Write the cells below P as those (i, j) with j less than every j′ for which (i, j′) is on P. Order them by
  (i, j) ≤ (i′, j′) when i ≤ i′ and j ≥ j′, and take an empty one r = (i, j) that is minimal. Let x = (i − 1, j), y = (i, j + 1) and
  c = (i − 1, j + 1). Since P only increases, its cells in column i − 1 lie no higher than its lowest cell b in column i, and
  j < b. So each of x, y and c is on P or below it. Those on P are occupied, and those below P are smaller than r, so occupied too.
- *Its fill.* c differs from x on one split (between columns j and j + 1) and from y on one other (between rows i − 1 and i). The
  knots {B(x, r, y), B(c, x, r), B(c, y, r)} pin r, on each state, to the value of x and y where they agree, to x's on the split
  between c and x, and to y's on the split between c and y. That is the value of the cell (i, j) on every state. So every old state
  extends uniquely: a fill, and no copy, since r was empty. r lies in a cell, so no two splits of one chain come to cross, and the
  base keeps two orders.
- Cells above P are the same with the order reversed. So NNF has a fill while the grid has an empty cell, and it never subdivides
  before the grid is full. A fill adds no split, so the chains always hold m splits between them; while the crossing graph is not
  connected they may be regrouped, and the argument applies to the cover at each step. ∎

**N5.**
- *Empty cells.* In a base with two orders and a connected crossing graph, crossing splits t₁ and t₂ lie in different chains. A
  corner fill r agrees with x on every split of t₁'s chain (B(x, r, y) where x = y, and B(c, x, r) on t₁) and with y on every split
  of t₂'s chain. So r is monotone along both chains: it lies in a cell, and that cell is empty since r is no copy. No two splits of
  one chain come to cross, so two orders are kept.
- *Refilling.* After a subdivision of a full grid between (i, j₀) and (i, j₀ + 1) (N3 (ii)), take an empty cell r = (i′, j₀ + 1) of
  the new column with a filled neighbour q = (i′ ∓ 1, j₀ + 1) in it (at first q = p). Let c = (i′ ∓ 1, j₀) and x = (i′, j₀), both
  old. c differs from q on the column split t between j₀ and j₀ + 1, and from x on the row split between i′ ∓ 1 and i′. These two
  cross: their four quadrants hold c, q, x and the old cell (i′, j₀ + 2), present since the old grid was full. So r has a corner fill
  across crossing splits, CC fills the column outward from p, and by the first point it takes no other fill. At a full grid there
  is no empty cell, so CC subdivides (N1 keeps the two orders). ∎
- *A line.* A line's splits are nested in one chain, and no two cross. ∎

## After the read-out: N6 (proved after the run, prompted by it)

- **N6. Under CC, a split that crosses nothing never comes to cross anything.** So from a line with one fill of (a, c, b), CC
  reaches a full grid exactly when a = 0 and b = m, the line's two ends; otherwise it never does.
- *Proof.* Let t cross no split. A corner fill r agrees with c on every split but t₁ and t₂, which cross each other, so t is
  neither. For any split s, r lies in the quadrant of (t, s) that holds c, unless s is t₁ or t₂; then it lies in the quadrant
  that holds x (or y). Either way the quadrant was occupied, so t gains no crossing. A subdivision changes no crossing (N1), and
  the two splits made from a subdivided t cross what t crossed. A full grid with both chains non-empty has a complete bipartite
  crossing graph, so no split crosses nothing; hence a fill whose span misses a step of the line, which leaves that step's split
  crossing nothing, rules out every full grid. If a = 0 and b = m, the line with the fill has a complete bipartite crossing graph
  K_{c, m − c}. The minimal empty cell of N4 then has a corner whose two splits lie in different chains, so they cross, and CC
  fills the grid; N5 does the rest. ∎
- A uniform first fill has a = 0 and b = m with chance (n₀ − 2) / C(n₀, 3) = 6 / (n₀ (n₀ − 1)): 0.30, 0.20, 0.14 and 0.11 for
  n₀ = 5 to 8.

## What this leaves to the computation

- Whether NN, whose knots may only join pairs that already share a knot, reaches a full grid from a line, and whether it refills
  as NNF does. The certificate in (iii) uses the pairs (p, x) and (p, y), and right after a subdivision p shares knots only with u
  and v.
- Which shapes NNF's and CC's grids take, and how CC grows after one fill of a line instead of the 2 × 2 pattern.

## Provenance

Local; builds on `MEET-ORDERS-20261118-001A` (Lemma C and its colouring) and `STATE-RULES-20261117-001A`. The median of three in
a product of two chains is classical (median graphs; the grid ℤ² is one). The advisor proposed the bound of N2's ends (the
chain of grids), and checked N1 to N3 before the freeze (see the decision note).
