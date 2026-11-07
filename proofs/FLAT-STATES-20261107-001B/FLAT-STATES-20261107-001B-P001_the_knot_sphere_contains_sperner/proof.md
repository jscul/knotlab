# The knot sphere contains Sperner's lemma

Status: Proved (statements 1 and 3 by hand, with exhaustive and solver checks; statement 2 by hand from statement 1 and
`FLAT-STATES-20261107-001A`, checked for m = 3..6). The width bound it was meant to give is reduced, not proved.

Ticket `FLAT-STATES-20261107-001B`, 2026-11-07.

## Standard statement

Let Sperner_m be the 2D Sperner problem on the side-m triangular grid with a fixed boundary: corners coloured 0, 1, 2, and each side
taking its far corner's colour after its first vertex. A solution is a fully labelled small triangle. In the one-sided version, the
solution must be oriented like the boundary.
1. **Local lemma.** Double the grid. Give each vertex the label 2c and each edge midpoint the label halfway between its ends. Colour the
   fine points by these labels through the six sublattice patterns. Then a fine line is violated only inside a fully labelled triangle
   oriented counterclockwise, and every such triangle holds at least one. Clockwise ones hold none; they hold a full face, an
   antivortex.
2. **Reduction.** For m ≥ 3 and k ≥ 2m + 4 there is a map Φ from Sperner_m colourings to assignments of the octahedral knot sphere K_k.
   - Each point's colour reads at most two Sperner colours.
   - The violated lines of Φ(c) lie exactly inside the full triangles of c oriented like the boundary.
   - Hence the one-sided Sperner_m problem reduces to "find a violated line of K_k" by decision trees of depth at most 2. Query
     lower bounds and resolution-width lower bounds for Sperner_m transfer to K_k with constant loss.
3. **Window criterion.** Pebble some vertices of a Sperner grid with colours. A state whose only full triangle is T (counterclockwise)
   exists iff an integer difference system on the pebbles' sheets has no negative cycle. Equivalently, every closed walk through
   pebbles must admit its required winding.
   - **Obstruction bound.** If T is feasible and T′ is not, some closed walk through pebbles winds differently around T and T′ and
     satisfies Σ_free (ℓ_i − 2) ≤ |ω_S| + 3|w| + 2. Here the ℓ_i are its free segments' lengths, ω_S is the forced winding along its
     adjacent-pebble steps, and w is its winding around T′.

## Nearest known result

- **Sperner as PPAD.** 2D Sperner is PPAD-complete (Papadimitriou 1994; Chen–Deng 2009). The one-sided ("positive") versions sit with
  PPADS.
- **Query complexity.** Finding a trichromatic triangle needs Ω(√N) queries on N vertices (Crescenzi–Silvestri 1998). O(√N)
  suffices (Friedl–Ivanyos–Santha–Verhoeven 2005).
- **Tree-like resolution.** The 2D Sperner CSP needs tree-like resolution size 2^Θ(n) (Itsykson–Malova–Oparin–Sokolov 2014,
  [arXiv:1412.1124](https://arxiv.org/abs/1412.1124)).
  - Their adversary keeps a coloring and a path whose "buffer" hides the trichromatic triangle. That is the Sperner form of the vortex
    and its strings.
  - Their CSP lets side vertices choose between the side's two colours, while statement 2 fixes the boundary; the models differ.
- **Width.** A resolution width lower bound for grid Sperner was not found in the literature.
- **Classification.** new as far as found for statement 2: the knot's Euler count on the sphere contains one-sided 2D Sperner, with the
  six corner disclinations playing the Sperner boundary. Statement 3 is the standard difference-constraint (McShane, Bellman–Ford)
  argument applied to Sperner heights.

## 1. Local lemma

**The coarse triangles.** In fine coordinates the coarse up-triangle (2a, 2b), (2a+2, 2b), (2a, 2b+2) contains:
- the fine lines U at its three corners;
- the fine face D in its middle.

The coarse down-triangle contains three fine faces and one fine line, U(2a+1, 2b+1).

**Not fully labelled.** Its colours lie in {c, c + 1}, so all labels lie in {2c, 2c + 1, 2c + 2}.
- No fine triangle sees both 2c and 2c + 2: a midpoint between ends coloured c and c + 1 carries 2c + 1.
- So every fine triangle's labels lie within two consecutive values, and `SPHERE-COUNT-20261106-001A` lemma 1 makes it
  not-all-equal.

**Fully labelled.** The labels are 0, 2, 4 at the corners and 1, 3, 5 at the midpoints, winding once around the middle face. Whether
a fine line is monochromatic depends on the sublattice phase. Check 1 enumerates all 27 colourings for both coarse orientations and
all three phases:
- counterclockwise full triangles always hold a violated line;
- clockwise ones never do.

This matches `SPHERE-COUNT-20261106-001A` lemma 2, where counterclockwise vortices are lines and clockwise ones are faces. ∎

## 2. The reduction

**The region.** In an octant of K_k whose up-triangles are points, take R = {(x0 + X, y0 + Y) : X, Y ≥ 0, X + Y ≤ 2m}, with x0 = y0 = 1
and k ≥ 2m + 4 so that R avoids the octant's edges. Develop frames over R. R holds no corner, so this is consistent by
`FLAT-STATES-20261107-001A` statement 1.

**Outside R.** Fix one flat state with its vortex in R. Its cut star runs from the vortex to three adjacent pairs of boundary edges of
R, one pair just after each corner of R, and then on to the six corners of K_k (disjoint paths; they exist for m ≥ 3).
- Every point outside R takes this state's colours, which violate no line outside R.
- On the boundary of R, the state's labels in R's frame are a constant plus 0, 2 or 4 on the three sides, with the odd values only at
  the three crossing midpoints.
- So they are exactly the doubled labels of the Sperner boundary in the statement: corners 0, 1, 2 (up to a constant), sides
  monochromatic after their first vertex.

**Inside R.** Points of R get the doubled labels of the Sperner colouring, read in R's frame. A vertex reads its own colour; a midpoint
reads its two ends. Boundary points read fixed colours that agree with the outside state.

**Where lines can be violated.**
- Lines outside R, or meeting R only in its boundary, see the outside state's colours, so they are not violated.
- Lines inside R lie inside one coarse triangle, and statement 1 applies.

Check 2 runs every colouring for m = 3, 4, 5 (3, 27 and 729 colourings) and 3,000 random ones for m = 6. In every case:
- the violated lines lie exactly in the full triangles oriented like the boundary;
- the net orientation is 1;
- each point reads at most two Sperner colours. ∎

**Consequences.**
- **Queries.** A decision tree that finds a violated line of K_k with q queries gives one that solves one-sided Sperner_m with at most
  2q queries. If the Ω(m) query bound of Crescenzi–Silvestri holds for this fixed boundary (their model was not compared), finding a
  violated line on K_k needs Ω(k) = Ω(√n) queries.
- **Width.** By the pebble-game reading of width (Atserias–Dalmau): if Sperner_m has resolution width Ω(m), then K_k has width
  Ω(k) = Ω(√n). A Duplicator for Sperner_m becomes one for K_k by answering each point through its at most two Sperner colours. The
  pebble simulation of `TWO-ROUND-BRIDGE-20261106-001B` carries the bound to the decorated three-fold spaces.
- **Size.** Size bounds do not transfer automatically, because a depth-2 reduction can blow up clauses exponentially in their width.

## 3. The window criterion

**Heights.** A Sperner colouring with exactly one full triangle T (counterclockwise) is an integer height h on the plane cut along a
ray from T:
- every edge satisfies |h(v) − h(u) + τ(u, v)| ≤ 1, with τ = ±3 on edges crossing the ray;
- colours are h mod 3.

Steps lie in {−1, 0, 1}, and a triangle is full iff its steps sum to ±3.

**Sheets.** Pebbled colours fix h mod 3 at the pebbles, so write h(p) = c_p + 3 s_p.
- With the sheets fixed, a height exists iff the pebble-to-pebble bounds h(q) − h(p) ≤ d(p, q) hold. Here d is the shortest-path
  distance for edge weights 1 − τ. This is the standard difference-constraint (McShane) extension.
- So existence is equivalent to the integer system s_q − s_p ≤ ⌊(d(p, q) − c_q + c_p)/3⌋ having no negative cycle.

**Closed walks.** A cycle of this system is a closed walk Γ through pebbles p_1, …, p_r (with multiplicity) and segments of lengths
ℓ_i. Along segment i, the colour change Δ_i lies in A_i = {x ≡ c_{i+1} − c_i (mod 3) : |x| ≤ ℓ_i}. The cycle is consistent iff
3·wind(Γ, T) ∈ ΣA_i. This sumset is an arithmetic progression of step 3 from Σ min A_i to Σ max A_i.

**Obstruction bound.**
- An adjacent-pebble step (ℓ_i = 1) is forced. A free step has max A_i ≥ ℓ_i − 2 and min A_i ≤ −(ℓ_i − 2).
- If T is feasible and T′ is not, some Γ has 3·wind(Γ, T′) outside ΣA_i while 3·wind(Γ, T) is inside it. So the windings differ and
  Σ_free (ℓ_i − 2) ≤ |ω_S| + 3|wind(Γ, T′)| + 2. ∎

Check 3 compares the criterion with a solver on grids of side 5, 6 and 7: all 1,411 pairs (pebbled colouring, triangle) agree, 966 of
them infeasible.

## What remains: the width bound

**The Duplicator.** Keep the full triangle where no "tight" closed walk through pebbles separates it from where it was. By statement 3,
the only obstructions are walks whose free segments are short in total, compared with the forced winding |ω_S| along their
adjacent-pebble chains.

**The missing lemma (winding control, open).** Duplicator can answer so that every chain of adjacent pebbles carries forced winding at
most (half its end-to-end distance) + O(1). With it, every obstructing walk has length O(its pebbles). The union of their insides has
area O(w²), so with w ≤ c·m pebbles the giant region survives, and Sperner_m has width Ω(m). Hence K_k has width Ω(k).

**Evidence and caveat.**
- Itsykson et al.'s path-and-buffer adversary keeps exactly such chains flat when nothing is forgotten (tree-like setting). The pebble
  game adds forgetting, which only removes constraints.
- But the vortex may circle pebble clusters many times. Whether forced windings can then accumulate is the open point.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Local lemma, bulk, exhaustive (2 orientations × 3 phases × 27 colourings) | violated lines only in counterclockwise full triangles, at least one in each |
| 2 | Reduction, m = 3..6 | all 3,759 colourings: violated lines exactly in the boundary-oriented full triangles; at most two Sperner colours per point |
| 3 | Window criterion vs solver, sides 5..7 | 1,411 of 1,411 agree (966 infeasible) |
