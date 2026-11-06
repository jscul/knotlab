# Bits see a three-manifold only through its mod-2 cohomology

Status: Proved

Ticket `HUB-DIMENSION-20261024-001A`, 2026-10-24.

**What it uses:**
- from `SURFACE-GLUING-20261024-001` (closed): native gluing pairs every shared distinction, and a hub-free network is determined by
  its graph and its slots;
- classical background, cited and not admitted as local evidence:
  - **(P)** any two triangulations of a closed three-manifold are related by finitely many 2–3 and 1–4 moves and their inverses
    (Pachner 1991; for singular triangulations, Matveev 1987 and Piergallini 1988);
  - cellular cohomology with coefficients in the field with two elements.

## Standard statement

**Setting.**
- **Triangulations.** A *triangulation* of a closed orientable three-manifold M is a set of tetrahedra whose faces are glued in pairs;
  faces of one tetrahedron may be glued together.
  - V, E, F and T count vertices, edges, triangles and tetrahedra after the gluing.
  - F = 2T, and V − E + F − T = 0, so E = V + T.
- **Edge laws.** An *edge law* puts one bit on each edge. It has two symmetric rules:
  - a set W of allowed numbers of 1-edges in a triangle;
  - a set Q of allowed classes of tetrahedron labellings, up to the 24 symmetries of the tetrahedron (there are 11 classes).
  - The *count* c(T) is the number of edge labellings satisfying every triangle and every tetrahedron.
- **Edge bits are hubs; face bits are native.**
  - An edge bit is shared by every triangle around its edge, so it is a hub whenever the edge lies in three or more triangles.
  - The *native network* of a triangulation puts one bit on each face. Each face bit is shared by exactly two tetrahedra, with one
    four-place rule per tetrahedron. Its graph is the dual graph of the triangulation.
- **The move identities.**
  - **2–3 move.** Two tetrahedra sharing a face become three sharing a new edge. For every labelling of the nine boundary edges whose
    six boundary triangles are allowed, the three-tetrahedron side must equal λ times the two-tetrahedron side, for a constant λ.
  - **1–4 move.** One tetrahedron becomes four around a new vertex. The same must hold with a constant μ.

**Theorem 1 (census).** An edge law satisfies both identities, and allows some configuration, exactly when its allowed tetrahedron
classes, restricted to those whose faces obey W, form one of seven sets:

| Law | Allowed tetrahedra | (λ, μ) |
| --- | --- | --- |
| all 0 | the zero labelling | (1, 1) |
| all 1 | the all-ones labelling | (1, 1) |
| all equal | both constant labellings | (1, 1) |
| free | every labelling | (2, 16) |
| even parity | every face has an even number of 1-edges | (1, 2) |
| odd parity | every face has an odd number of 1-edges | (1, 2) |
| even or odd | all four faces have the same parity | (1, 2) |

Of the 32,768 laws:
- 5,703 pass both identities;
- 8,097 allow no configuration in either move;
- the other 18,968 fail.

**Corollary 2 (the invariants).** For the seven laws, N(T) = c(T) · (λ³/μ)^V · λ^(−T) does not change under either move. Given (P),
it depends only on M:
- for the four trivial laws it is 1, 1, 2 and 1;
- for even and odd parity it is |H¹(M; Z/2)|/2;
- for "even or odd" it is |H¹(M; Z/2)|.

**Theorem 3 (parity counts flat connections).** For a connected triangulation, the even-parity count is c(T) = |H¹(M; Z/2)| · 2^(V−1).

**Proposition 4 (failing laws fail globally).** The check samples random 2–3 and 1–4 moves on singular triangulations starting from
the one-tetrahedron triangulations of the sphere, L(4,1) and L(5,2). Every failing law that is ever allowed on the sample changes its
ratio on some sampled move. So no normalization makes it an invariant.

**Proposition 5 (native networks are blind to dimension three).**
- A native network is determined by the dual graph of the triangulation and the slots of its faces. The gluing maps, which carry the
  three-dimensional information, do not enter.
- The one-tetrahedron triangulations of the sphere and of L(4,1) with face pairing (0,1)(2,3) have the same native network, so every
  face law counts them equally.
- Their edge-parity counts are 1 and 2.

**Corollary 6 (what bits see).**
- **The invariants.** Among symmetric edge laws, the three-manifold invariants are the constants and |H¹(M; Z/2)|.
- **What they miss.** No such law separates manifolds with equal mod-2 first cohomology, for example the sphere and L(5,2).
- **Reading.** Bits see dimension three only through hubs, and then only through the mod-2 first cohomology, which the two-dimensional
  skeleton of the triangulation already determines.

## Nearest known result

- **Theorem 3 and Corollary 2.** Classical: the untwisted Dijkgraaf–Witten invariant for the group with two elements,
  |Hom(π₁(M), Z/2)|/2.
- **Theorem 1 and Proposition 4.** No census of Boolean edge laws under Pachner moves was found in the bounded scan. Novelty:
  `candidate-local-delta`; folklore risk low to medium.
- **Proposition 5.** Elementary. The one-tetrahedron manifolds are those of Burton's census.

## Proof

### Theorem 1

The identities are finite conditions: 512 labellings of the nine boundary edges for the 2–3 move, with two values of the new edge,
and 64 labellings of the six boundary edges for the 1–4 move, with 16 values of the new edges. The check evaluates them for all 32,768
laws and records the allowed tetrahedron classes of the passing laws: exactly the seven sets of the table, with the ratios shown.

Why the identities give invariance under the moves:
- **Factorization.** The count is a sum over labellings of the edges outside the move region of the constraints there, times the
  region's contribution. The region's contribution depends only on its boundary labelling.
- **The boundary.** The boundary triangles are common to both sides of the move. The identity relates the two sides for every
  boundary labelling with allowed boundary triangles. Rules are 0 or 1, so a boundary triangle glued to another boundary triangle,
  counted once instead of twice, changes nothing.
- **Singular triangulations.** Identifications among the region's boundary edges only restrict which boundary labellings occur, and
  the identity holds for each of them. The new edge, triangles and vertex are new.
- So a 2–3 move multiplies c by λ, and a 1–4 move by μ. ∎

### Corollary 2

- **Invariance.** N changes by λ · λ^(−1) = 1 under a 2–3 move (T increases by one) and by μ · (λ³/μ) · λ^(−3) = 1 under a 1–4 move
  (V increases by one, T by three). Given (P), N depends only on M.
- **The trivial laws.**
  - The all-0 and all-1 laws have c = 1.
  - "All equal" has c = 2 on a connected triangulation.
  - "Free" has c = 2^E and N = 2^(E − V − T) = 1.
- **Parity.**
  - Even parity has λ = 1 and μ = 2, so N = c/2^V = |H¹|/2 by Theorem 3.
  - The all-ones labelling makes every triangle odd. Adding it is a bijection between even and odd solutions.
  - "Even or odd" forces all faces to one parity, since adjacent tetrahedra share faces and the dual graph is connected. So its count
    is twice the even count. ∎

### Theorem 3

- **Even-parity labellings are cocycles.** An edge labelling c with an even number of 1-edges on every triangle is a 1-cocycle of the
  cellular cochain complex with coefficients Z/2: its coboundary vanishes on every triangle.
- **The tetrahedron rule is implied.** The allowed tetrahedron classes are the cocycles on one tetrahedron: zero, the star of a vertex,
  and a four-cycle, which are coboundaries of zero, one and two vertex labels.
- **Counting.** So c(T) = |Z¹| = |H¹| · |B¹|, and |B¹| = |C⁰|/|H⁰| = 2^V/2 for a connected triangulation. ∎

### Proposition 4

- **The sample.** The check runs four random walks of up to five moves from each of the four one-tetrahedron starting triangulations
  (two of the sphere, L(4,1), L(5,2)), keeping at most 13 edges. Its 65 moves are 37 of type 2–3 and 28 of type 1–4.
- **The test.** For every law it records the ratio c(after)/c(before) on each move.
  - Every passing law keeps one ratio per move kind.
  - Every failing law that is ever allowed on the sample either takes two different ratios for one kind, or goes from zero to
    non-zero.
  - Laws allowing no configuration in either move are never allowed on the sample. ∎

### Proposition 5

- **The native network.** It consists of one four-place rule per tetrahedron, with each face bit shared by the two slots of the faces
  glued together. These data are the dual graph with its slot labels; the vertex correspondences of the gluings never enter.
- **The example.** Among the one-tetrahedron triangulations whose faces 0, 1 and 2, 3 are glued, the check finds one with H₁ = 0 (the
  sphere) and one with H₁ = Z/4 (L(4,1)), each with one vertex.
- **Native counts.** Their native networks coincide, so every face law gives them equal counts; the check confirms this for all 32
  symmetric four-place rules.
- **Edge parity.** By Theorem 3 the counts are 2^(0 + 1 − 1) = 1 and 2^(1 + 1 − 1) = 2. ∎

### Corollary 6

By Theorem 1, Proposition 4 and Corollary 2, the symmetric edge laws that give invariants give the constants or |H¹(M; Z/2)|.
H¹(M; Z/2) = Hom(H₁(M), Z/2) vanishes for the sphere and for L(5,2). ∎

## Checks

`check.py` uses the standard library only (seed 20261024), with its own triangulation code (gluings, edge classes with orientation,
vertex links, orientability, H₁ by Smith normal form, mod-2 cohomology) and its own 2–3 and 1–4 moves on singular triangulations.

It confirms:
- the census of Theorem 1;
- the certificates of Proposition 4 (65 sampled moves);
- that the moves keep validity and H₁;
- Theorem 3 on all 65 sampled triangulations;
- Proposition 5;
- the failure of the Fibonacci rule. With every boundary edge 1, the two-tetrahedron side allows one labelling and the
  three-tetrahedron side two; the rule also breaks on a sampled move.

**Controls.**
- **The 2–3 identity needs its new edge.** Dropping the new edge's sum from it rejects parity.
- **The ratio test detects a change of manifold.** Comparing the sphere with L(4,1) as if one move related them breaks parity's
  ratio.
- **The vertex factor matters.** Replacing 2^(dim H¹ + V − 1) by 2^V disagrees with the parity counts.

## What this does not show

- **Other kinds of law.** It does not cover laws on ordered (branched) triangulations, laws with several bits per edge (labels in a
  larger group, which count homomorphisms of the fundamental group), laws with bits on faces and edges together, or weighted laws
  (ticket B).
- **Other manifolds.** It does not cover non-orientable manifolds.
- **Where a failing law fails.** Proposition 4 proves that each failing law is not an invariant, by exhibiting two moves of one kind
  with different ratios. It does not say on which manifolds that law fails.
