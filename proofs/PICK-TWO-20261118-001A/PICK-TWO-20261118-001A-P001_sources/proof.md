# Where the number of orders comes from: caps, prices, conservation and one fill

Status: Proved

Ticket `PICK-TWO-20261118-001A`, 18 November 2026, by Claude. Epic `PICK-TWO-20261118-001`. Written before the run.

## Words

As in `NEVER-NEST-20261118-001A`: splits, their sides and crossing; chains; λ (the least number of chains covering the splits) and
k (the chromatic number of the crossing graph); cells of the grid of d chains; a **full d-grid** holds every cell; fills (no state
added) and subdivisions (one middle knot on a pair differing on one split, two states added). For two splits that do not cross,
exactly one of the four intersections of their sides is empty, and which one it is says how they nest. Call this the pair's
**relation**; for a crossing pair, the relation is that it crosses.

The rules (`research/PICK-TWO-20261118-001/preregistration.md`): CAP(d), PRICE(f), KEEP, CC, ODD, FRESH, NEWCROSS and SEED.

## Statements

- **S1. λ never decreases.** No fill or subdivision lowers λ or k.
- **S2. CC keeps every relation, so it keeps the start's number of orders.** A corner fill across crossing splits never lands in an
  empty intersection, and a subdivision keeps every relation. So k and λ, which depend only on the relations, never change under
  CC: from a 2 × 2 pattern it keeps two orders, from Q₃ three, from a line one.
- **S3. A cap of d orders refills from a full d-grid.** From a full d-grid (d ≥ 2, every chain non-empty), CAP(d) only subdivides,
  then fills the new layer cell by cell back to a full d-grid, forever. The fills it takes are exactly the empty cells.
- **S4. The corner knot set is always a fill, and at a full grid it raises the orders by exactly one.**
  - For any old distinctions a, c, b, the knots {B(a, r, b), B(c, a, r), B(c, b, r)} pin r on every state: r agrees with a and b
    where they agree, and where they differ it takes the value of whichever of the two differs from c. So unless r is a copy,
    this is a fill.
  - On a full d-grid, let a, c, b be three cells in a row along a chain C with two or more splits. Then r makes the two splits of C
    on either side of c cross, and nothing else changes. So λ becomes exactly d + 1.
  - On Q_d no fill exists.
- **S5. A greedy price picks the number of orders through its increments.** Let PRICE(f) take the moves that minimise
  (states added) + f(λ after), with f strictly increasing.
  - It takes a fill that keeps λ whenever one exists.
  - At a full grid other than a cube it raises (by one) if f(λ + 1) − f(λ) < 2, and subdivides if the difference exceeds 2.
  - From a line it fills iff f(2) − f(1) < 2, and otherwise stays a line forever.
  - So for a linear price f(λ) = wλ the choice is the same at every λ: below w = 2 it raises at every full non-cube grid, above
    it never leaves the line. A price that holds D orders at a full grid needs f(D + 1) − f(D) ≥ 2, and one that rose to D needed
    f(D) − f(D − 1) < 2: the number is written into f.
- **S6. One fill on a line makes exactly two orders.** Its new crossings join the splits whose chosen sides hold the new
  distinction to those whose sides do not, a bipartite set, and each of the two sets stays a chain. So every first fill of a line
  gives λ = k = 2 (`STATE-RULES-20261117-001A`, S4, for the fills of triples). KEEP therefore never fills a line, and leaves the
  start's λ unchanged from any start.
- **S7. After its first fill, SEED keeps a bipartite crossing graph.** Every new crossing it allows gives a split that crossed
  nothing exactly the crossers of a split that already crossed something, and no two splits that already crossed something come
  to cross. Such a split joins the crossing graph as a second copy of an existing vertex, which keeps it bipartite.

## Proofs

**S1.** Restricting the new base to the old distinctions turns each new split into an old one, keeps nesting (a side contained in
another stays contained), and keeps non-crossing pairs non-crossing. So a cover of the new splits by chains gives one of the old
splits with no more chains, and a crossing between the restrictions of two new splits is a crossing of the new splits. ∎

**S2.** Let r be a corner fill: c differs from x on one split t₁ and from y on one other, t₂, the two cross, and r agrees with c
except on t₁ (where it takes x's side) and t₂ (where it takes y's). Take two old splits s, s′ that do not cross.
- If neither is t₁ or t₂, r lies on c's sides of both, an occupied intersection.
- If s = t₁ and s′ ≠ t₂, r lies on x's sides of both (x agrees with c on s′), an occupied intersection. The same holds with t₂
  and y.
- s, s′ cannot be t₁ and t₂, which cross.

So r never lands in an empty intersection, and no relation changes. A subdivision changes none either (`NEVER-NEST-20261118-001A`,
N1).
- k depends only on which pairs cross.
- λ is the number of splits minus a largest matching of the graph joining sides X, Y of different splits with X ∪ Y the whole set
  (Eppstein's formula). X ∪ Y is the whole set exactly when the complements of X and Y have empty intersection, which is the
  pair's relation.

So neither k nor λ changes. ∎

**S3.** This is `NEVER-NEST-20261118-001A`'s N3 with d chains.
- *The chains are fixed.* The crossing graph of a full d-grid is complete d-partite. A cover by d chains is a cover by d
  independent sets, which must be the d parts.
- *Fills are empty cells.* A fill keeps the splits and only adds crossings. If it made two splits of one chain cross, those two
  with one split of each other chain would be d + 1 pairwise crossing splits, and λ ≥ k ≥ d + 1. So a fill keeping λ ≤ d lies in an
  up-set of each chain's nested sides, that is, in a cell, and the cell is empty since the fill is no copy. On a full grid there
  is none, so CAP(d) subdivides.
- *After a subdivision.* A subdivision across chain j makes its split two nested twins (N1), and a new layer whose only
  distinction is p. For an empty cell r of that layer, the cells x and y next to it along chain j are old and present, and in
  every coordinate r is the middle value of p, x and y (along j: the new value between its two neighbours; elsewhere r's own
  value, shared by x and y). So the three middle knots on the pairs of p, x, y pin r to the majority on every state: a fill.
  These cells are exactly the fills offered, the layer fills, and the base is a full d-grid again. ∎

**S4.**
- *The pins.* Where a = b, B(a, r, b) pins r = a; the end knots, where they pin, pin r = a = b too.
- Where a ≠ b, c equals exactly one of them, say b. Then B(c, a, r) ("a lies between c and r") pins r = a, and B(c, b, r) pins
  nothing. So every state extends uniquely.
- *At a full grid.* Put a, c, b at positions i − 1, i and i + 1 along C, with t_i the split between a and c and t_{i+1} the one
  between c and b. Then r takes a's side of t_i, b's side of t_{i+1}, and c's side of every other split. On t_i and t_{i+1}, nested
  in C, that is the one empty intersection (below t_i and above t_{i+1}), so they come to cross.
- For any other pair, r lies with a, b or c, as in S2, so no other relation changes. Then t_i and t_{i+1}, with one split of each
  other chain, are d + 1 pairwise crossing splits, so λ ≥ d + 1. And C without t_i, the single split t_i, and the other chains are
  d + 1 chains (r is monotone along C without t_i), so λ = d + 1.
- *On Q_d.* Every split crosses every other, so a fill creates no crossing, keeps every chain of one split, and lies in a cell;
  every cell is occupied. ∎

**S5.** By S1 every move has λ after ≥ λ.
- *Scores.* A fill keeping λ scores f(λ); a subdivision keeps λ (N1) and scores 2 + f(λ); every other fill scores at least
  f(λ + 1).
- *Fills first.* So a fill keeping λ is strictly best when one exists.
- *At a full grid that is not a cube.* No fill keeps λ (S3's argument with d = λ), and S4 gives a fill raising λ by exactly one,
  which beats any larger jump since f is increasing. So the rule compares f(λ + 1) with 2 + f(λ).
- *On a line.* Every fill gives λ = 2 (S6), so the rule compares f(2) with 2 + f(1). ∎

**S6.** On a line the splits are the cuts, nested as t₁ ⊂ t₂ ⊂ ⋯ ⊂ t_m (each t_k the side holding the first k distinctions).
- *Which pairs come to cross.* A pair t_i ⊂ t_j (i < j) comes to cross exactly when the new distinction r lies in t_i and not in
  t_j, the empty intersection. Let A be the cuts whose side holds r and B the rest. Every new crossing joins A to B.
- *Two chains.* Within A, adding r to every side keeps them nested; within B, no side changes. So A and B are chains: λ ≤ 2.
- *At least two.* Some pair crosses, since r is constrained and no copy, so its value changes more than once along the cuts.
  Then λ ≥ k = 2.
- *KEEP.* It takes only fills that leave λ unchanged, and subdivisions keep λ. On a line no fill does, so KEEP subdivides forever.
  ∎

**S7.** Let u be a split that crossed nothing, and let it gain crossings in an allowed fill. Then its crossers afterwards are those
of a split v that already crossed something, and v is not among them. So u is a second copy of v, joined to the same vertices. Any
proper two-colouring extends by giving u v's colour. Subdivisions add such copies too (N1). By S6 the crossing graph after the
first fill is bipartite, so it stays so. ∎

## What this leaves to the computation

- Whether CAP(d) for d ≥ 3 reaches a full d-grid from a line before it first subdivides. For d = 2 this is
  `NEVER-NEST-20261118-001A`'s N4. For d ≥ 3 the advisor proves it only while the base stays connected.
- How fast PRICE's λ grows below the threshold, and what the tie at w = 2 does.
- λ (not only k) for FRESH, NEWCROSS and SEED, and whether their two-order bases are full grids.
- That λ equals the largest set of pairwise crossing splits on every base grown from a line (the advisor's argument; checked on
  every base reached).

## Provenance

Local; builds on `NEVER-NEST-20261118-001A`, `STATE-RULES-20261117-001A` and `CUBE-DOUBLING-20261118-001A`. The advisor gave S4's
general pinning, the exactly-one raise, S5's exception for cubes and jumps larger than one, and the rules FRESH and SEED; it was
consulted before the freeze. Eppstein's formula for the lattice dimension and medians of three are classical.
