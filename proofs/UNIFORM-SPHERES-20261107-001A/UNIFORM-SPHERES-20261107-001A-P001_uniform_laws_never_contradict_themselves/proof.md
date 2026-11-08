# Uniform laws never force the knot's contradiction

Status: Proved (theorems 1–4 by hand). Theorem 5 and the contrast are computed (`check.py`).

Ticket `UNIFORM-SPHERES-20261107-001A`, 2026-11-07.

## Standard statement

**Laws.** A *law of lines and co-lines* is:
- a finite set of points;
- lines (triples);
- co-lines (cyclic sequences of points of length d ≥ 2).

It must satisfy two conditions:
- every corner of a line (a pair of its points) is a consecutive pair of exactly one co-line, and every consecutive pair of a co-line is a
  corner of exactly one line;
- every point's link alternates lines and co-lines in a single cycle.

**The surface it builds.** Points, corners, lines and co-lines are then the vertices, edges and faces of a closed surface, built by the
law alone. The knot is the signed not-all-equal constraint on the lines. The co-lines are the faces whose agreements
`COUNT-SURFACES-20261107-001A` counts: under every assignment,

  violated lines − Σ_c ⌊agree_c / 2⌋ = (χ − |D|)/2,

where D is the set of co-lines the signs make even.

**The Cayley law** C(G; x, y) of a finite group G = ⟨x, y⟩, with w = (xy)⁻¹:
- points G;
- lines {g, gx, gxy};
- co-lines the cosets g⟨x⟩, g⟨y⟩, g⟨w⟩ in their cyclic order.

A law is *uniform* when every point has the same co-line sizes (d1, d2, d3). Its signs are *uniform* when every line carries the same
sign pattern on its three sides, with the sides labelled so that each co-line's corners all lie between the same two sides. A Cayley law
has such a labelling: corners of types y, w, x lie between sides (1, 2), (2, 0), (0, 1).

1. **Cayley laws are laws.** C(G; x, y) builds a closed orientable surface, and every point has co-line sizes (|x|, |y|, |w|).
2. **The curvature formula.** A uniform law has χ = n(1/d1 + 1/d2 + 1/d3 − 1). Hence it is:
   - a sphere exactly for (2,2,d) with n = 2d, (2,3,3) with n = 12, (2,3,4) with n = 24, and (2,3,5) with n = 60;
   - a torus or Klein bottle for (3,3,3), (2,4,4), (2,3,6);
   - hyperbolic otherwise.

   Each spherical type is realized by Cayley laws on V4 and the dihedral groups D_d, A4, S4 and A5. These are the antiprisms and the snub
   tetrahedron, cube and dodecahedron, with each digon collapsed to an edge.
3. **Uniform signs never force the lines.** With uniform signs every even co-line is an even face, so

     χ − |D| ≤ n(Σ_{d_i odd} 1/d_i − 1) ≤ 0.

   The count never forces the knot's lines to fail on any uniform law. On every uniform sphere it forces faces to over-agree instead.
4. **Non-uniform signs give only shallow contradictions.**
   - Kasteleyn signs (no even face) exist on every sphere, are unique up to gauge, and are never uniform there.
   - Under them the knot fails on every uniform sphere, but only on at most 60 points or on a (2,2,d) law.
   - A (2,2,d) law is a cyclic chain of width 1, on which binary search finds a violated line with at most 2⌈log₂ d⌉ + O(1) queries:
     the search problem is in FP^dt.
5. **Computed.**
   - With uniform signs the knot is satisfiable on every tested uniform law: V4, D_3..D_12, A4, S4, A5, wallpaper quotients of all three
     flat types, and PSL(2,7) of type (2,3,7), the Klein quartic law (genus 3, 168 points).
   - It is also satisfiable on all 327 circulant laws with n ≤ 48, up to affine equivalence, except the Fano plane (Z7, lines
     {g, g+1, g+3}, all signs equal).
   - The Fano plane's contradiction is not the count's: its type (7,7,7) gives D = ∅ on a genus-3 surface, so the count forces only faces.

**Contrast.** The knot sphere K_k has exactly two kinds of points, (3,3,3) and (2,3,3): the twelve points at its six digons (check 7).
With Kasteleyn signs, which differ from uniform ones at the digons, its contradiction is PPADS^dt-complete (`COUNT-TFNP-20261107-001B`).

## Nearest known results

- **Vertex-transitive maps.**
  - The curvature formula is the angle count of vertex-transitive maps.
  - The spherical list is the classical one: prisms, antiprisms and the Archimedean solids. Ours are the snub-type maps whose
    alternate faces are triangles.
  - Cayley maps of (2,3,n) triangle-group quotients: Biggs, "Cayley maps and symmetrical maps" (1972); Gross–Tucker, *Topological Graph
    Theory* (1987), §§6.2–6.3.
  - The Klein quartic is the (2,3,7) Hurwitz surface of PSL(2,7).
- **The count.** COUNT-SURFACES-20261107-001A; on the knot sphere, COUNT-TFNP-20261107-001B.
- **Question 9 so far.**
  - LOGIC-AXIS-20261107-001 and OPEN-END-GROWTH-20261107-001: uniform laws without ends give rulers, and a growth rule grows the
    number line.
  - THREEFOLD-SURFACES-20261030-001: the Fano plane is the 7-vertex torus, and Fano atoms are handles.
- **Classification.**
  - Theorems 1–2 are known-with-delta: classical maps, read as laws that build their surfaces.
  - Theorems 3–4 are new as far as found: the knot's count on self-built surfaces, and the bound on uniform contradictions.

## 1. Cayley laws

*Proof of theorem 1.*
- **Corners.** The line {g, gx, gxy} has three corners, (g, gx), (gx, gxy) and (gxy, g). They are consecutive pairs of the cosets
  g⟨x⟩, gx⟨y⟩ and gxy⟨w⟩, of types x, y and w (since gxy·w = g).
- **Each corner once.** A consecutive pair (h, hx) of an x-coset is a corner of exactly one line, the one starting at h. Likewise
  (h, hy) belongs to the line starting at hx⁻¹, and (h, hw) to the line starting at hw.
- **The link.** Around a point g the faces are:
  - the line {g, gx, gxy}, then the coset g⟨x⟩;
  - the line {gx⁻¹, g, gy}, then g⟨y⟩;
  - the line {gy⁻¹x⁻¹, gy⁻¹, g}, then g⟨w⟩, back to the start.

  That is one 6-cycle.
- **Orientability.** In the triangulation of COUNT-SURFACES-20261107-001A, side k of every line is glued to side k of its k-th point
  by the identity on corners. The orientation bits are then 0 on points and 1 on lines, consistent everywhere (check 1). ∎

## 2. The curvature formula

*Proof of theorem 2.*
- **Counting.** There are n lines and 3n corners. Counting point–co-line incidences by slot, there are Σ_i n/d_i co-lines.
- **Euler.** χ = n − 3n + (n + Σ_i n/d_i) = n(Σ_i 1/d_i − 1).
- **Spheres.** χ = 2 needs Σ 1/d_i > 1 and n = 2/(Σ − 1). With d_i ≥ 2 the solutions are (2,2,d), (2,3,3), (2,3,4), (2,3,5) (check 2,
  every type with entries up to 60).
- **Flat.** Σ = 1 gives (3,3,3), (2,4,4), (2,3,6).
- **Realizations.** V4 with three involutions; D_d with two reflections; A4, S4, A5 with x of order 2, y of order 3 and xy of order 3, 4,
  5 (check 1). ∎

## 3. Uniform signs

*Proof of theorem 3.*
- **Each co-line's flip.** A co-line of size d has d corners, each between sides a and b of its line. With uniform signs σ its flip is
  d(σ_a + σ_b) mod 2, so d + flip ≡ d(1 + σ_a + σ_b).
- **Which co-lines are even.** If d is even the co-line is even (in D). If d is odd it is in D iff σ_a ≠ σ_b.
- **The bound.** |D| ≥ Σ_{d_i even} n/d_i, so χ − |D| ≤ n(Σ_{d_i odd} 1/d_i − 1).
- **Odd sizes.** An odd co-line has at least 3 points, and there are at most three slots, so Σ_{d_i odd} 1/d_i ≤ 1. Hence χ − |D| ≤ 0, and
  COUNT-SURFACES's identity gives no violated line.
- **On spheres** the type contains a 2, so D holds every digon. There are at least six: 6 for V4, 2d for (2,2,d), n/2 ≥ 6 for
  (2,3,·). So |D| > 2 = χ, and the identity forces over-agreement.
- **Check 3** confirms all of this for every law above and all eight patterns, on random assignments. ∎

## 4. Non-uniform signs

*Proof of theorem 4.*
- **Kasteleyn signs on spheres.** By COUNT-SURFACES-20261107-001A, Kasteleyn signs exist (χ even), form one class (H₁ = 0), and force a
  violated line. They are not uniform, because by theorem 3 a uniform pattern leaves every digon even (check 5).
- **Size.** By theorem 2 a uniform sphere has at most 60 points, unless its type is (2,2,d).
- **(2,2,d) laws are chains.** Each point lies on exactly one of the two d-gon co-lines C and C′. Remove these two faces: what remains
  is an annulus A whose points all lie on its two boundary circles. Its edges are the corners and its faces the lines and digons.
  - **One cap corner per line.** At a point p of C, the two lines next to C in p's link are distinct, so no line has two cap corners.
    There are 2d cap corners and 2d lines, so each line has exactly one.
  - **No chord inside one cap.** Suppose a chord joined two points of C. It would cut off a disk bounded by the chord and k edges of C.
    Triangulating that disk takes k − 1 triangles (digons add none). But its k cap edges need k distinct lines, a contradiction.
  - **Hence the chain.** Every interior edge joins C to C′, and the faces sit in one cyclic order around A, consecutive faces sharing a
    chord. Cutting along one chord removes two points and splits the faces into two arcs.
- **The dihedral case concretely.** Put the rotation r_j in block j and the reflection f_j in block −j. Then
  L(r_j) = {r_j, f_{−j}, r_{j+1}} and L(f_j) = {f_j, r_{−j}, f_{j+1}}, which is width 1 (check 6).
- **Binary search.** Query one chord's two points, cut the cycle there, and keep an arc whose lines cannot all hold given its two end
  chords. Splitting at a middle chord, one half keeps that property, since the two halves share only that chord. Each round queries two
  points. Check 6 (dihedral blocks, which give the same rounds): at most 18 queries at n = 512. ∎

## 5. The census

| Law | Type | n | χ | Uniform signs | Kasteleyn signs |
| --- | --- | --- | --- | --- | --- |
| V4, D_3..D_12 | (2,2,d) | 2d | 2 | all 8 patterns satisfiable; faces forced | unsatisfiable (cyclic chain) |
| A4, S4, A5 | (2,3,3), (2,3,4), (2,3,5) | 12, 24, 60 | 2 | all satisfiable; faces forced | unsatisfiable |
| (3,3,3) / Z_k² ⋊ C3 | (3,3,3) | 27, 48 | 0 | satisfiable; the two equal-sign patterns are Kasteleyn | every class satisfiable |
| (2,4,4), (2,3,6) quotients | flat | 18–96 | 0 | satisfiable; faces forced | every class satisfiable |
| PSL(2,7) | (2,3,7) | 168 | −4 | satisfiable; faces forced | 4 sampled classes satisfiable |
| Fano plane, Z7 {0,1,3} | (7,7,7) | 7 | −4 | **unsatisfiable** for equal signs (not by the count) | equal signs are Kasteleyn |
| 327 circulant laws, n ≤ 48 | various | ≤ 48 | various | satisfiable except the Fano plane | — |

## Checks

`check.py` (`result.json`), about a minute:

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | 18 Cayley laws | closed orientable surfaces; every point of type (\|x\|, \|y\|, \|xy\|); χ = n(Σ 1/d − 1) |
| 2 | Spherical types up to 60 | exactly (2,2,d), (2,3,3), (2,3,4), (2,3,5) with n = 2d, 12, 24, 60 |
| 3 | Uniform signs, 8 patterns per law | even co-lines are even faces; χ − \|D\| ≤ 0; the identity holds; spheres force faces |
| 4 | The knot under uniform signs | satisfiable on every law but the Fano plane; the circulant census finds only the Fano plane |
| 5 | Kasteleyn signs | unsatisfiable on every uniform sphere, satisfiable on flat and hyperbolic laws; no uniform pattern is Kasteleyn on a sphere |
| 6 | Antiprism chains, d = 3..256 | width 1; binary search ≤ 2 log₂ d + 8 queries (18 at n = 512) |
| 7 | The knot sphere K_2..K_6 | exactly two kinds of points: (3,3,3) and twelve (2,3,3) |
| 8 | Controls | a mis-glued law is not a surface; the count with χ + 2 fails; blocks by rotation alone give width > 1 |

## Reading

**Interpretation, not a theorem.**
- **A self-built surface.** A uniform law lays out its own closed surface, with nothing drawn: its points, the pairs its lines and
  co-lines share, and the faces they close.
- **Its shape.** The co-line sizes alone decide the shape: flat (a torus) at Σ 1/d = 1, hyperbolic below, and a sphere above, which is
  then small or a thin antiprism.
- **Coherence.** On any uniform law with its own uniform signs the knot is never forced to contradict itself.
- **Where curvature lives.** Positive curvature sits on digons, two lines sharing two points. A digon closes only under a sign that
  breaks the uniformity.
- **So the knot's deep contradiction is a mark of non-uniformity.** The PPADS-complete count of the knot sphere needs two kinds of places
  and six sign defects, one at each digon. A uniform law can grow flat space without end, but not a large sphere.

## What this does not establish

- **Growth.** Only laws with one kind of point are classified. Laws with a bounded number of kinds of points could still build large
  spheres (the knot sphere has two). A law that grows its own six defects is not constructed.
- **Non-count contradictions.** These are surveyed only on circulant laws with n ≤ 48 and on the uniform laws listed. Whether
  arbitrarily large uniform laws can be unsatisfiable without the count, as the Fano plane is, is open.
- **Non-orientable uniform laws.** Laws twisted by orientation-reversing elements were not treated.
