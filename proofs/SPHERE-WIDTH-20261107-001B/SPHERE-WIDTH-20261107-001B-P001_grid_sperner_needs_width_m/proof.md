# Grid Sperner needs resolution width Θ(m)

Status: Proved by hand. It reuses `SPHERE-WIDTH-20261107-001A`'s argument; the winding bound and the isoperimetric constant are by
sketch there. The boundary lemma's ingredients and the locality are checked by computation.

Ticket `SPHERE-WIDTH-20261107-001B`, 2026-11-07.

## Standard statement

**Theorem.** Let Sperner_m be 2D Sperner on the side-m triangular grid with the fixed boundary of `FLAT-STATES-20261107-001B`:
corners 0, 1, 2, each side taking its far corner's colour after its first vertex. Clauses forbid fully labelled small triangles,
either all of them or only those oriented like the boundary. Every resolution refutation has width at least c·m − 1, for an absolute
constant c > 0. Width O(m) suffices.

**Corollaries.**
1. **Itsykson et al.'s CSP.** Their 2D Sperner CSP ϕ_n lets side vertices take either colour of their side, and fixing those colours
   restricts it to Sperner_n. A restriction never needs more width, so ϕ_n also needs width Ω(n). Only tree-like size was known.
2. **The knot sphere.** `FLAT-STATES-20261107-001B` reduces one-sided Sperner_m to the knot sphere K_{2m+4} by depth-2 decision trees.
   This gives width Ω(k) for K_k a second time, independently of `SPHERE-WIDTH-20261107-001A`'s sphere argument.

## Nearest known result

- **Known bounds for 2D Sperner.** Tree-like resolution size 2^Θ(n) (Itsykson–Malova–Oparin–Sokolov 2014,
  [arXiv:1412.1124](https://arxiv.org/abs/1412.1124)). Query complexity Θ(√N) (Crescenzi–Silvestri 1998;
  Friedl–Ivanyos–Santha–Verhoeven 2005).
- **TFNP.** PPAD/PPADS correspond to unary Nullstellensatz and unary Sherali–Adams (Göös et al. 2022). Those results concern
  polylogarithmic versus polynomial scales, not linear width on grids.
- **Classification.** new as far as found. A general-resolution width bound for grid Sperner was not found in the literature.

## Setting

**Heights** (`FLAT-STATES-20261107-001B`).
- **States as heights.** A Sperner state whose only fully labelled triangle is T, oriented like the boundary, is an integer height h
  read mod 3 as colours. Its steps lie in {−1, 0, 1} and it winds by 3 around T.
- **Trivialization.** Cut along three disjoint dual paths ("arcs") from T to the three boundary doors. Each crossing shifts by ±1, so
  the rise weights 1 − t lie in {0, 1, 2}.
- **The window criterion.** The pebbles' sheets satisfy s_q − s_p ≤ ⌊(d(p, q) + c_p − c_q)/3⌋, and a state exists iff this system
  has no negative cycle.
- **Pebbles.** The boundary's colours are constants of the formula, not variables, so Spoiler pebbles only interior vertices, at most
  w of them.

**Certificates** (as in `SPHERE-WIDTH-20261107-001A` lemmas 2–3). If T is feasible and T′ is not, a negative cycle at T′ through
distinct pebbles (interior or boundary) closes into a walk B. B winds differently around T and T′, or meets T.

## Boundary lemma

If T′ lies at depth at least R₀ = C₀·w and outside the density-bad set, then every certificate walk B that visits a boundary vertex
stays within distance C₁·w of the boundary, with C₁ < C₀.

*Proof.*
- **Where negative terms come from.** A term b_i = ⌊(d_i + c_i − c_{i+1})/3⌋ is negative only if d_i ≤ 1. Then the segment is one
  edge of weight ≥ 1 plus zero-weight edges, each a positive arc crossing. Consecutive positive crossings happen only within distance
  O(1) of T′, where the arcs meet. Pebbles are far from T′, so a negative segment is a single edge between pebbles.
- **Counting them.** Such an edge touches a Spoiler pebble (at most 2w such segments in a pebble-simple cycle) or is one of the six
  boundary features: the three doors and the three corner diagonals. So Σ_{b<0} b ≥ −(2w + 6), and Σ_{b>0} b ≤ 2w + 5.
- **Long segments are paid for.** A segment with d ≥ 5 has b ≥ (d − 4)/3. Segments of that kind have total length O(w + 1), since a
  winding around the deep T′ would cost Ω(R₀) per turn. Every other segment has length at most 7.
- **Excursions are short.** An excursion of B (a sub-walk between boundary visits) is either one chord of length ≤ 7, or contains
  Spoiler pebbles and has length O(w). Each starts and ends on the boundary, so all of B lies within O(w) of it. ∎

## The game

**Safe positions.** Let w ≤ c·m. Safe triangles lie at depth at least R₀ and outside the density-bad set D(P) of
`SPHERE-WIDTH-20261107-001A`. They form a set of size Ω(m²) − O(w²), which is nonempty for small c. The deep region is a smaller
triangle, hence connected.

**Transfer between safe T and T′.**
- **Walks through the boundary.** A certificate walk through a boundary pebble lies within C₁·w < R₀ of the boundary (boundary lemma).
  It misses the deep region, so it cannot separate T from T′ or meet T.
- **Pure Spoiler walks.** So the walk avoids the boundary. Then its length is at most 2r − 3 + 3|wind| ≤ 8r (lemma 3's winding
  bound). Planar isoperimetry inside the triangle and the density argument put T or T′ in D(P), a contradiction.

**Duplicator.** Duplicator answers from states whose full triangle is safe, exactly as in `SPHERE-WIDTH-20261107-001A`. The family is
closed under restriction, extends, and never falsifies a clause. So the width is at least w − 1 = Ω(m), by Atserias–Dalmau. ∎

**Upper bound.** The primal graph has treewidth O(m), so Davis–Putnam refutes in width O(m).

## Checks

`check.py` (`result.json`). The checks use a single-ray trivialization, under which the boundary features also include a few short
chords near the ray's foot. They still number O(1), which is all the lemma needs.

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Certificates, m = 10, 12 (random consistent clustered pebbles) | 54 of 54: negative terms only at segments of length ≤ 4 touching a Spoiler pebble or a boundary feature; every walk separates; 7 pure Spoiler walks, all with length ≤ 2r − 3 + \|H\| (largest ratio 2.0); walks through the boundary reach depth ≤ 3 |
| 2 | Locality, m = 18 | a chain of 12 pebbles whose colours advance ω ≤ 4 times blocks only triangles within distance 3; for ω ≥ 5 no single-full-triangle state fits it |

Check 2 explains why the free boundary does no harm. A pebble chain can force at most a few colour turns before its colours fit no
state at all, so consistent answers never let far-away pebbles pay for a long chord.

## What this does not establish

- **Size.** Resolution size for grid Sperner is not addressed.
- **Constants.** They are not optimized, and the sketched parts are inherited from `SPHERE-WIDTH-20261107-001A`.
