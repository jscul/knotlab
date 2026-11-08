# Round spheres need one hidden bit per incidence

Status: Proved by hand. The finite claims (balls, markings, widths, the region-map census) are checked by computation with controls.

Ticket `SPHERE-GROWTH-20261107-001A`, 2026-11-07.

## Standard statement

Knot spaces are read off two-coloured triangulations T of closed surfaces (`COUNT-SURFACES-20261107-001A`):
- points are the triangles of one colour and lines the triangles of the other;
- incidences are T's sides, and co-lines are T's vertices;
- a co-line of T-degree 2d has d points.

The **two-kind law** asks every co-line to have two or three points (T-degree 4 or 6). A co-line of two points is a **digon**.
- K_m is the octahedral knot sphere, the m-frequency octahedron of `SPHERE-WIDTH-20261107-001A`, with n = 4m² points.
- The capped tube T(m, L, τ) is a lattice cylinder of circumference 3m and L rows. Each end is closed by a lattice triangle of side
  m, the top one turned by τ. T(m, m, 0) is K_m.

**Laws.**
- A **law of radius r without hidden states** is a set of allowed radius-r balls (rooted at a co-line, up to isomorphism, colours
  kept). Its spheres are those whose balls are all allowed.
- A law **with hidden states** also puts a bit on every incidence. It allows a sphere when some choice of bits makes every ball allowed.
- The **seam law** has one bit per incidence (seam or not) and two rules:
  - **S1.** All four incidences of a digon are seams.
  - **S2.** A co-line of three points has no seam, or exactly one pair of opposite seams.

**Theorem 1 (six digons).** Every closed sphere of the two-kind law has exactly six digons. Under the local Kasteleyn sign rule (at
each co-line of d points the signs on its incidences have parity d + 1) its knot contradicts itself.

**Theorem 2 (the tube lemma).** Let r ≥ 1, m ≥ 2r + 1 and L ≥ 2r + 1. Every radius-r ball of T(m, L, τ) is a radius-r ball of K_m.
- So a law of radius r without hidden states that allows K_m allows every such tube.
- The tube's knot (with Kasteleyn signs) contradicts itself, but resolution refutes it in width O(m) at every length L.

**Theorem 3 (the seam law).** A closed sphere of the two-kind law has a seam marking if and only if it is K_m for some m. K_m has
exactly one marking: the 12m incidences on its octahedron's edges.
- So the seam law's spheres are exactly the octahedral knot spheres, at every size.
- Each one's knot needs resolution width Θ(√n) (`SPHERE-WIDTH-20261107-001A`) and size 2^Θ(√n) (`SPHERE-SIZE-20261107-001B`).

**Theorem 4 (growth needs branching).** A growth law without branching grows at most one closed surface from a seed. So a law that
grows round spheres of every size must branch somewhere. The seam law leaves only the size m free.

## Nearest known result

- **Local views.** Theorem 2 is the indistinguishability argument behind lower bounds for locally checkable properties: a radius-r
  verifier cannot tell apart two inputs with the same balls.
- **Locally checkable proofs** (Göös–Suomela, PODC 2011; *Theory of Computing* 2016) add certificate bits on nodes or edges.
  Theorem 3 says that, among two-kind spheres, being an octahedral knot sphere has a locally checkable proof with one bit per incidence.
- **Decorated matching rules.** Hidden decorations force global structure that bare local rules cannot (Penrose; Goodman-Strauss,
  *Matching rules and substitution tilings*, Annals of Mathematics 1998; Radin's pinwheel, 1994). The seam bits are such a decoration.
- **Flat cone spheres.** A two-kind sphere is a flat sphere with six cone points of angle 4π/3. Thurston (*Shapes of polyhedra*, 1998)
  parametrizes the triangulations of non-negative curvature by lattice points of a complex hyperbolic space.
  - The K_m are the spheres whose cone points are joined by twelve lattice-direction saddle connections forming an octahedron.
  - The Goldberg–Coxeter octahedra GC(k, l) with l ≠ 0 are symmetric too, but they are not lattice-aligned, so the seam law rejects them.
- **Classification.** New as far as found. Folklore risk is moderate: each step (local views, Gauss–Bonnet on a flat surface,
  developing a flat disc) is standard, and the seam rule is simple.

## Proof of Theorem 1

- **Six digons.** In a triangulation 3F = 2E, so Euler's formula gives Σ_v (6 − deg v) = 6χ. With degrees 4 and 6 this reads
  2·#digons = 6χ. So a sphere has six digons (a projective plane would have three, a torus or Klein bottle none).
- **The contradiction.** The local rule makes every co-line odd, so D = ∅. On a sphere χ = 2 > |D| = 0, and the count identity of
  `COUNT-SURFACES-20261107-001A` (viol − E = (χ − |D|)/2) forces a violated line under every assignment.
- **Every choice is the same formula.** Kasteleyn signings on the sphere form one gauge class (the classes are an H₁(S; F₂)-torsor). So
  every signing the rule allows gives the same formula up to renaming literals. ∎

## Proof of Theorem 2

- **Balls near the bottom cap.** A co-line on row j ≤ r sees rows up to j + r ≤ 2r < L. So its ball holds only the bottom cap and the
  band. The same co-line of K_m = T(m, m, 0) sees the same, since 2r < m.
- **Balls near the top cap.** The band is invariant under turning the cylinder. Turning by τ carries the top region of T(m, L, τ)
  (rows ≥ L − 2r ≥ 1) onto the top region of K_m.
- **Balls in the band.** A ball touching neither cap is a flat lattice hexagon, since the circumference 3m exceeds 2r and it does not
  wrap. K_m has flat balls of radius r: a co-line near a face's centre is at distance about 2m/3 > r from all six corners, and a ball
  that meets no corner is flat, even across the octahedron's edges.
- **The contradiction stays easy.** The tube is a sphere, so Theorem 1 applies. Its points have a path decomposition whose bags are a
  few consecutive rows, so its width is O(m). Davis–Putnam elimination along it refutes in width O(m) and size n · 2^O(m), at every L.
- **Computed.** The threshold m = 2r already suffices for r ≤ 3, and m = 2r − 1 fails. An elimination order by distance from one cap
  has width 4m + 1 on tubes of every length tried (m ≤ 4, L ≤ 8m). ∎

## Proof of Theorem 3

Let T be a two-kind sphere with a seam marking.

1. **Seams run straight between digons.**
   - By S2 a seam at a co-line of three points continues through the opposite incidence. By S1 all four incidences at a digon are seams.
   - Following a seam straight on is reversible. So the seams form straight paths that end only at digons, plus possibly closed straight
     loops through co-lines of three points.
   - Two straight paths never meet at a co-line of three points, since that co-line would have four seams.
2. **Loops can be dropped.** Removing a closed loop leaves a marking, since at its co-lines it was the only seam pair. So it suffices
   to study the **core**: the 24 rays leaving the six digons, which pair up into 12 **segments**.
3. **Every face of the core is a lattice triangle.**
   - Cut T along the segments. A face R holds no digon inside, so R is flat.
   - Along a segment, R has three triangles at each co-line (angle π). At a digon visit it has one (angle π/3), since the four seams
     there separate the digon's four triangles.
   - Gauss–Bonnet for the cut-open face gives (2π/3)·k = 2π·χ(R) = 2π(2 − b), with k corner visits and b boundary components.
   - Each boundary component contains a digon, so k ≥ b ≥ 1. This forces b = 1 and k = 3.
   - So R is a disc whose boundary has three corners of angle π/3 joined by straight segments. Its developing map is a locally convex
     immersion, hence an embedding, onto an equilateral lattice triangle of some side a_R.
4. **The faces form an octahedron.**
   - Each digon has four corner visits. So there are 24 visits, F = 8 faces, E = 12 segments and V = 6 digons, and the core is
     connected (b = 1 for every face).
   - The two colours alternate across a seam, and all triangles along an equilateral lattice triangle's boundary have one colour. So
     the faces alternate too.
   - Hence the dual of the segment map is a cubic bipartite plane multigraph on 4 + 4 vertices with six faces of length 4.
   - Every such graph is the cube: its biadjacency matrix is J − P for a permutation matrix P (checked over all embeddings). So the
     segment map is the octahedron.
5. **All sides are equal.** Adjacent faces share a whole segment, so a_R is constant: a_R = m.
6. **T is K_m.** Eight equilateral lattice triangles of side m, glued along the octahedron corner to corner, give K_m.
7. **One marking.** On K_m the core is the octahedron's twelve edges. A closed straight loop avoiding the corners must cross an edge at
   a lattice point, which would give that co-line four seams. So K_m's marking is unique.

**Conversely**, K_m's octahedron edges satisfy S1 and S2.

**Hardness.** The seam law fixes no signs. The local Kasteleyn rule gives the gauge class of `SPHERE-WIDTH-20261107-001A` and
`SPHERE-SIZE-20261107-001B`, so their bounds apply. ∎

## Proof of Theorem 4

A growth law without branching maps each configuration to its next step. From a seed its run is one sequence, which stops at its first
closed surface if it has one. ∎

## Checks

`check.py`, with `seam_lib.py`, runs in under a minute and reproduces `result.json`.

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | K_m built two ways agrees (m ≤ 5); every tube (m ≤ 4, L ≤ m + 3, every τ) and 60 grown spheres are two-kind spheres with six digons | pass |
| 2 | Local Kasteleyn signs leave no even co-line; the count identity holds; the knot is unsatisfiable on K_2..K_5, three tubes and five grown spheres | pass |
| 3 | Tube lemma for r ≤ 3: every tube's balls occur in K_m for m ≥ 2r; at m = 2r − 1 none of the tubes passes | pass |
| 4 | Elimination width 4m + 1 on T(m, L, 0) for L up to 8m (n up to 400); on K_m (m ≤ 8) it rises with m | pass |
| 5 | Seam law: K_m (m ≤ 5) has exactly one marking, its octahedron's edges; all 60 tubes and 60 grown spheres have one iff they are a K_m (only T(m, m, 0) and 10 octahedra) | pass |
| 6 | Control: if S2 allows any two seams, non-round tubes get markings | pass |
| 7 | Region-map census: 24 matrices, each J − P (the cube) | pass |
| 8 | Random growth: 60 closed spheres in 711 tries; the only round ones are octahedra, even at sizes 32 and 128 shared with K_2 and K_4 | pass |

## What this does not establish

- **No growth rule is built.** Theorem 3 is a law that admits exactly the round spheres. A local process that grows K_m must keep
  twelve seams the same length, and how it could is open.
- **Only the lattice-aligned octahedra.** GC(k, l) with l ≠ 0 and other round shapes are rejected; other laws would be needed.
- **Hidden bits are witnesses.** Whether the seam law together with the knot is a native knot (K1–K3) is not assessed.
- **Resolution only.** Together with the Sherali–Adams results of the earlier epics; no other proof system, and no P vs NP claim.
