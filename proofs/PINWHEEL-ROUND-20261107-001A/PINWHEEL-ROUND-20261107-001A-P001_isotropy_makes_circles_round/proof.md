# Isotropy makes logical circles round: the pinwheel law

Status: Proved by hand, conditional on cited published theorems about the pinwheel space (Radin). The substitutions, the frame
mechanism, the 1:1 pattern, the vertex-cycle lemma and the bounds are checked by computation (`check.py`).

Ticket `PINWHEEL-ROUND-20261107-001A`, 2026-11-07.

## Standard statement

1. **Isotropy principle.** Let Ω be a compact space of tilings of the plane with finite local complexity up to rigid motions.
   Suppose Ω is invariant under rotations, and the action of ℝ² on Ω by translations is uniquely ergodic.
   - **The distances.** For each tiling T, let D_T be a metric on the edges of T's plane graph. It must be covariant under rigid
     motions, satisfy c·|x − y| − C ≤ D_T ≤ C·|x − y| + C, and bound the distance between edges that share a vertex.
   - **The conclusion.** For almost every T and every unit vector u, D_T(e_T(0), e_T(nu))/n → μ. Here e_T(x) is the edge nearest
     to x, and the constant μ > 0 is the same for all u.
2. **Pinwheel bond distance.** Take the least bond (minimal edge cut) of a pinwheel tiling's graph containing two given edges,
   or the least cycle containing them, minus one. Either satisfies 1, so both are asymptotically a multiple of Euclidean distance
   in every direction.
3. **Two non-round contrasts.**
   - **The frame-consistent cut.** Cutting the same right triangle (legs 1:2) into the same five copies, but frame-consistently,
     gives tiles in four orientations only.
   - **The 1:1 triangle.** Halving the right triangle with legs 1:1 repeatedly gives the periodic tetrakis triangulation. Its two
     bond distances have polygonal unit balls: an octagon with Gołąb π = 10/3, and a square with π = 4.
4. **Few orientations at finite scale.** A disc of radius R in a pinwheel tiling meets O(log R) tile orientations.

## Nearest known result

- **Radin and Sadun**, "The isoperimetric problem for pinwheel tilings", Comm. Math. Phys. 177 (1996) 255–263.
  - **Paths.** In a pinwheel tiling, the shortest path along tile edges between points at Euclidean distance R has Euclidean length
    R + o(R).
  - **Near-circles.** Unions of tiles exist whose area/perimeter² is arbitrarily close to a disc's.
  - **No rate.** Their proof gives no rate. Later work on rates for related constructions: Cai and Chen, "The Squishy Grid
    Problem" (arXiv:2507.23105). Benjamini calls such graphs slack-isometric to the plane.
- **Radin**, "Symmetry of tilings of the plane", Bull. AMS 29 (1993), and "The pinwheel tilings of the plane", Ann. of Math. 139
  (1994). The pinwheel system is uniquely ergodic under translations, has complete rotational symmetry, and is forced by local
  matching rules. A 2022 paper on substitutions over compact alphabets (arXiv:2204.07516) reproves the unique ergodicity.
- **Isotropy arguments** for random tessellations: Vahidi-Asl and Wierman (1990, 1992).
- **Classification: known-overlap-found.** That pinwheel tilings are large-scale Euclidean is known for the length-weighted edge
  metric. The delta, as far as found:
  - bond distance, which counts distinctions and uses no lengths, is round, by a principle covering every covariant law;
  - the frame mechanism, with the frame-consistent and 1:1 cuts as non-round contrasts;
  - the O(log R) orientation count, which makes the roundness a large-scale trend.

## Terms

- **Tiles.** A tile is a right triangle written (O, P, Q): the right-angle vertex, the end of the long leg, the end of the short leg.
- **Its frame.** Its frame is the direction of its long leg modulo π/2.
- **Its handedness** is the sign of (P − O) × (Q − O).
- **The cuts.** With legs 1:2 and H the foot of the altitude from O:
  - **Pinwheel (Conway).** Let M be the midpoint of OP, F₁ the midpoint of OH, F₂ the midpoint of HP. The five copies of scale
    1/√5 are (H, O, Q), (F₁, M, O), (F₁, M, H), (F₂, H, M), (F₂, P, M). Four copies meet at M, and (F₁, M, O), (F₁, M, H) and
    (F₂, H, M), (F₂, P, M) are mirror pairs.
  - **Frame-consistent.** (H, O, Q) and the midpoint subdivision of (H, P, O) into four copies.
  - **Isosceles.** With legs 1:1, the triangle is halved by its altitude.
- **The pinwheel space.** It is the set of tilings every patch of which is congruent to a patch of some iterate of the pinwheel
  substitution, with the usual tiling topology.
- **The two laws on a tiling's plane graph G.** The graph has vertices at tile corners and edges the boundary segments between
  consecutive vertices.
  - **The corner law** puts a parity knot at each vertex. Its knots are the bonds of G, which are the cycles of the tile adjacency
    graph G\*.
  - **The tile law** puts a parity knot on each tile over its boundary segments. Its knots are the cycles of G.
  - **Bond distance δ** is the least knot through two variables, minus one. It is a metric (`NATIVE-NETWORK-20261021-001` B,
    Theorem 2).

## Theorem 1 (isotropy principle)

Let Ω, D and e_T be as in standard statement 1. There is μ > 0 such that, for almost every T with respect to the unique invariant
measure m, and for every unit vector u, D_T(e_T(0), e_T(nu))/n → μ.

*Proof.*

1. **Subadditive.** Fix u, and put X_{j,n}(T) = D_T(e_T(ju), e_T(nu)). The triangle inequality gives X_{0,n} ≤ X_{0,j} + X_{j,n}.
2. **Stationary.** The translation τ(T) = T − u preserves m, and X_{j+1,n+1} = X_{j,n} ∘ τ by covariance.
3. **Integrable.** By the linear upper bound, 0 ≤ X_{0,1} ≤ 2C.
4. **A limit exists.** By Kingman's subadditive ergodic theorem, X_{0,n}/n → ξ_u almost surely, with ξ_u invariant under τ.
5. **ξ_u does not depend on T.**
   - **Invariant under every translation.** For any v,
     |X_{0,n}(T − v) − X_{0,n}(T)| ≤ D_T(e(0), e(v)) + D_T(e(nu), e(nu + v)) ≤ 2C|v| + 2C, a bound independent of n.
     So ξ_u(T − v) = ξ_u(T) for every v.
   - **Constant.** Unique ergodicity makes m ergodic for the translation action, so ξ_u is almost surely a constant μ(u).
6. **The same in every direction.**
   - **The measure is rotation-invariant.** For a rotation R, R_\*m is invariant under translations, because R conjugates
     translations to translations. By uniqueness, R_\*m = m.
   - **So μ is too.** By covariance, X_{0,n}(RT; Ru) = X_{0,n}(T; u), so ξ_{Ru} under m has the law of ξ_u under m. Hence
     μ(Ru) = μ(u).
7. **All directions at once.**
   - Take a countable dense set of directions; convergence holds for all of them almost surely.
   - For any u and u′, |D_T(e(0), e(nu)) − D_T(e(0), e(nu′))| ≤ Cn|u − u′| + C.
   - So limsup and liminf in any direction lie within C|u − u′| of μ. Letting u′ → u gives the limit μ.
8. **μ is positive**, by the lower bound c|x − y| − C. ∎

## Corollary 2 (the pinwheel's parity laws are round)

**Statement.** For almost every pinwheel tiling, both laws have bond distance μR + o(R) in every direction: an exactly round
circle.
- The constants μ_corner and μ_tile differ.
- Neither distance uses a length: each counts distinctions.

*Proof.* Check the hypotheses of Theorem 1.

**The space.** The pinwheel space is compact and has finite local complexity up to rigid motions. It is invariant under rotations:
- the space is closed under rigid motions by definition;
- every tiling in it contains tiles in a dense set of orientations.

Its translation action is uniquely ergodic (Radin 1993, 1994).

**Upper bound, corner law.**
- **Around a vertex.** At an interior vertex v, the tiles meeting v, in angular order, form a cycle of G\* whose dual edges are
  exactly the segments at v. A tile cannot appear twice around a vertex, since tiles are convex.
- **Two segments at a vertex.** Hence δ ≤ deg(v) − 1 ≤ Δ − 1 for any two segments sharing a vertex. Here Δ, the largest degree,
  is 8 (finite local complexity).
- **Along a path.** By the triangle inequality, δ(e, f) ≤ (Δ − 1)(h + 1), where h counts the segments of a shortest vertex path.
  Tiles have bounded size, so h ≤ C|x − y| + C.

**Lower bound, corner law.**
- A cycle of G\* through e\* and f\* contains two disjoint dual paths between their tiles, so δ ≥ 2·d_{G\*} − 1.
- Each dual step moves at most twice a tile's diameter.

**The tile law.** It is the same with G and G\* exchanged.
- **Upper bound.**
  - The segments on one tile's boundary lie on that tile's boundary cycle in G. A pinwheel tile has at most 4 boundary segments,
    so any two of them have δ ≤ 3.
  - Along a path of adjacent tiles, consecutive tiles share a segment. So by the triangle inequality, δ(e, f) ≤ 3(t + 1), where t
    is the number of tiles on a shortest dual path, and t ≤ C|x − y| + C.
- **Lower bound.** A cycle of G through e and f contains two disjoint vertex paths between their ends, so δ ≥ 2·d_G − 1. Each step
  of G moves at most one tile side.

Covariance holds because both laws are defined from the tiling alone. ∎

## Proposition 3 (the two non-round contrasts)

(a) **The frame mechanism.**
- **All siblings share a frame.** All five children of a tile have their legs along the parent's altitude and hypotenuse, in both
  cuts.
- **The turn.** That frame is the parent's frame turned by s·φ, with φ = arctan(1/2) (mod π/2) and s = ±1 given by the parent's
  handedness.
- **The consistent cut.** It gives every child the handedness opposite to its parent's. Every line of descent then turns by the
  same sequence of signs, so all tiles of a level share one frame: four orientations.
- **The pinwheel cut.** It gives three children one handedness and two the other. Lines of descent turn by different sums of ±φ,
  so the frames multiply.
- **Infinitely many.** φ/π is irrational by Niven's theorem (tan φ = 1/2 is rational and not 0 or ±1), so the frames never repeat.
- **Computed.** The pinwheel has 3, 8, 12, …, 28 orientations at levels 1–7 (4k for k ≥ 2).

(b) **The isosceles cut gives the tetrakis triangulation.**
- **The induction.** At an even level 2j, every tile is half of a grid square, cut by one diagonal. Two further halvings turn a
  square with either diagonal into four sub-squares whose diagonals meet at its centre (an X).
- **The pattern.** So the sub-square with index (a, b) has its NE diagonal exactly when a + b is even, at every level j ≥ 1.
  This is the checkerboard-diagonal (Union Jack, tetrakis) triangulation, which is periodic.
- **Its circles.** By `LOGIC-CIRCLE-20261107-001` A (Theorem 1 and its table):
  - the corner law (the law on the tetrakis graph) has as circle half the velocity octagon of 4.8.8, with π = 10/3 and anisotropy
    √5/2;
  - the tile law (three-place knots on the 4.8.8 graph) has a square, with π = 4 and anisotropy √2.
- **Two ways to fail.** The isosceles cut mixes handedness, but its angle π/4 is rational. The consistent cut has the irrational
  angle but no mixing. The pinwheel has both.

## Proposition 4 (roundness is a large-scale trend)

**Statement.** A disc of radius R in a pinwheel tiling meets at most C·(log R + 1) tile orientations.

*Proof.*
- **Supertiles.** Every pinwheel tiling is uniquely a union of level-j supertiles, for every j (Radin's recognizability). Choose j
  with √5^j comparable to R.
- **Few of them.** By area, the disc meets at most N₀ supertiles of level j.
- **Few frames in each.** By (a), each supertile's tiles have at most j + 1 frames: the supertile's frame plus a sum of j turns of
  ±φ with a fixed parity. That is at most 4(j + 1) orientations.
- **The bound.** In total, at most 4N₀(j + 1) = O(log R). ∎

**What it means.** At every finite radius the pinwheel has finitely many directions, like a polygon with O(log R) sides. Its circle
is round only in the limit.

## The check

`check.py`, which runs in under a minute, verifies the following.
- **The substitutions.** All three, at levels up to 6 (14 for the isosceles cut), give congruent right triangles with legs in the
  stated ratio and the exact area of the top triangle. This is integer arithmetic.
- **Orientations per level.** The pinwheel has 4k orientations for k = 2, …, 7; the consistent cut 4; the isosceles cut 4.
- **Handedness.** The pinwheel's children split 3:2; the consistent cut's are all opposite to their parent.
- **The isosceles pattern** is exactly the checkerboard-diagonal triangulation at levels 2, 4, …, 14.
- **The vertex-cycle lemma** holds at all 2137 interior vertices of the level-5 pinwheel. The largest degree is 8.
- **The bounds** of Corollary 2 hold on 40 sampled pairs of the level-6 corner law, with exact least cycles.
- **Orientations within distance R of the centre** at level 7: 7, 11, 13, 19, 20, 24, 28 for R = 2, …, 100, within the O(log R)
  bound. The consistent cut stays at 4.
- **Controls**, all rejected:
  - the consistent cut as a candidate for orientation growth;
  - a pinwheel cut with one mirror copy relabelled (no longer congruent);
  - the isosceles pattern with the parity flipped;
  - the vertex-cycle lemma with one tile removed.

## Nonclaims

- **Cited facts.** Radin's unique ergodicity, rotational symmetry and recognizability for the pinwheel are cited, not re-proved.
  Corollary 2 is conditional on them.
- **Not new for lengths.** That pinwheel tilings are large-scale Euclidean for the length-weighted edge metric is Radin and
  Sadun's. New here is that the program's distance, which counts distinctions, is round too, with the contrasts.
- **Rates.** No rate of convergence is proved; ticket B measures one.
