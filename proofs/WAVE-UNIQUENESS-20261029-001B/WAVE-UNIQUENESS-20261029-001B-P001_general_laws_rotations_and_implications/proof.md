# General three-bit laws: rotations of the wave and implication laws

Status: Proved

Ticket `WAVE-UNIQUENESS-20261029-001B`, 2026-10-29.

**What it uses:**
- `WAVE-UNIQUENESS-20261029-001A`: the classification of symmetric laws, its sector method and its exact engine.
- `SIGNED-GASKETS-20261029-001B`, Lemma 1: the six symmetries of the gasket permute the roles and the corners together, so a law is exact
  iff each of its role permutations is. Complementing every bit also preserves exactness.

## Standard statement

**Setting.**
- **Laws.** General three-bit laws w[a, b, c] with complex weights, on the level-k Sierpinski gaskets SG_k. Exactness is as in ticket A.
- **Three strata.**
  - **G (generic).** w = u₁v₁y₁ + u₂v₂y₂ with u₁, u₂ independent, v₁, v₂ independent and y₁, y₂ independent: tensor rank two, decomposition
    unique.
  - **R (rank one in a corner).** w = u(a)M[b][c] or a rotation of it. This includes the products, which have tensor rank one.
  - **W.** The rest: vanishing hyperdeterminant with full multilinear rank (W-type tensors).
- **Pairings.** ⟨x, y⟩ = x₀y₀ + x₁y₁. J is the rotation (x₀, x₁) ↦ (−x₁, x₀), and e₀ = (1, 0), e₁ = (0, 1).

**Results.**
- **Lemma 1 (level 2 in G).**
  - R₂ = Σ_ijk C_ijk u_i v_j y_k with C_ijk = ⟨v_i, u_j⟩⟨y_i, u_k⟩⟨y_j, v_k⟩. So level 2 holds iff C₁₁₁ = C₂₂₂ ≠ 0 and the six
    off-diagonal C_ijk vanish.
  - Each off-diagonal C_ijk is a product of two cross pairings and a nonzero diagonal one. The six conditions are the edges of a hexagon
    on the cross pairings X₁ = ⟨v₁, u₂⟩, X₂ = ⟨v₂, u₁⟩, Y₁ = ⟨y₁, u₂⟩, Y₂ = ⟨y₂, u₁⟩, Z₁ = ⟨y₁, v₂⟩, Z₂ = ⟨y₂, v₁⟩.
  - The vanishing cross pairings must cover the hexagon, and it has exactly five minimal covers.
  - **Three covers of size four** force the law to be symmetric in a pair of roles. Up to a symmetry of the gasket, that is the class
    of ticket A.
  - **Two covers of size three:** the *cyclic branch* u₂ ⊥ v₁, v₂ ⊥ y₁, y₂ ⊥ u₁, and its mirror image.
- **Theorem 2 (the cyclic branch).** Write u₂ = Jv₁, v₂ = Jy₁, y₂ = Ju₁ and w = u₁v₁y₁ + c·u₂v₂y₂.
  - Level 2 holds iff c² = 1.
  - Levels 2 and 3 hold iff one of u₁, v₁, y₁ is a coordinate vector, e₀ with c = 1 or e₁ with c = −1.
  - These are the *implication laws*. Up to the symmetries and the complement, they are
    w = e₀ ⊗ v ⊗ y + Jv ⊗ Jy ⊗ e₁, whose support is the implication "a = 1 ⇒ c = 1".
  - There are twelve types: six ordered pairs of roles times two values.
- **Theorem 3 (implication laws build every gasket).** For every k ≥ 1 and all v, y, the corner relation of e₀ ⊗ v ⊗ y + Jv ⊗ Jy ⊗ e₁ is
  ⟨v, y⟩^(k−1) (v₀y₀)^(m_k) times the law, where m_k = (k − 1) + (k − 1)(k − 2)/2.
  - With v = (1, s) and y = (1, t) the factor is (1 + st)^(k−1).
  - If v₀ = 0 or y₀ = 0 the factor is 0.
  - The same holds for all twelve types.
- **Proposition 4 (rank one in a corner).** For w = u(a)M[b][c], R_k = u ⊗ M^k times a scalar (k = 2, 3). So exactness forces M² = cM, c ≠ 0:
  either a product u ⊗ x ⊗ z, or u(a)[b = c]. The rotations give x(b)[a = c] and x(c)[a = b].
- **Corollary 5 (general laws, strata G and R).** A general law of the strata G or R is exact at levels 2 to 5 iff it is one of these:
  - the image under a symmetry of the gasket of a final class of ticket A: standing waves with their limits, the laws u(a)[b = c], or the
    frozen laws F and F̄;
  - an implication law;
  - a product.
  - **Knots.** The only knots among them are the three rotations of signed not-all-equal.
- **Open.** The stratum W is not classified here. Its symmetric members (ticket A's tangent stratum) give only (−1)^a E, F and F̄.

| Stratum | Laws exact at levels 2-5 | Every level? | Knots |
| --- | --- | --- | --- |
| G, size-four covers | rotations of ticket A's two-sector classes (standing waves) | yes, where the factor is nonzero | signed not-all-equal and its rotations |
| G, cyclic covers | implication laws (12 types, 2 parameters each) | yes: factor (1 + st)^(k−1) | none |
| R | products u x z; u(a)[b = c] and its rotations | yes, where the factor is nonzero | none |
| W | not classified (symmetric part: (−1)^a E, F, F̄) | — | — |

## Nearest known result

- **In the repository.** `WAVE-UNIQUENESS-20261029-001A` covers symmetric laws. `SIGNED-GASKETS-20261029-001B` is the ±1 census with knot
  supports in the plane.
- **Outside.** Kruskal uniqueness of tensor rank-two decompositions, the 2×2×2 hyperdeterminant and the normal form of W-type tensors are
  classical.
- **Classification.** Lemma 1 and Proposition 4 are elementary. Theorems 2 and 3: no overlap found (candidate local delta).

## Proof of Lemma 1

- **The identity.** Summing the three inner vertices of SG₂ pairs the vectors meeting there. The bottom vertex pairs v of T(0,0) with u of
  T(1,0), the left vertex pairs y of T(0,0) with u of T(0,1), and the middle vertex pairs y of T(1,0) with v of T(0,1). The identity is
  checked symbolically (check 1).
- **Diagonal coefficients.** In G the eight tensors u_i v_j y_k form a basis, so exactness means the coefficient tensor is λ times the
  diagonal. In particular the diagonal pairings are nonzero.
- **The hexagon.** The six off-diagonal coefficients each contain exactly two cross pairings, and these pairs are the edges X₁Y₁, Y₁Z₁,
  Z₁X₂, X₂Y₂, Y₂Z₂, Z₂X₁ of a hexagon. A set of vanishing pairings must meet every edge.
- **The covers.** Enumeration gives the minimal covers {X₁, Y₂, Z₁}, {X₂, Y₁, Z₂}, {X₁, X₂, Y₁, Y₂}, {X₁, X₂, Z₁, Z₂} and {Y₁, Y₂, Z₁, Z₂}
  (check 2).
- **Size four forces a pair symmetry.** In C², two vectors orthogonal to the same nonzero vector are parallel.
  - For {X₁, X₂, Y₁, Y₂}, u₂ ⊥ v₁, y₁ gives v₁ ∥ y₁, and likewise v₂ ∥ y₂. So w is symmetric in (b, c).
  - The other two give symmetry in (a, c) or (a, b).
  - A role permutation, which is a symmetry of the gasket, then makes the law symmetric in the two non-base corners, and ticket A
    applies. ∎

## Proof of Theorem 2

- **Level 2.** In the cyclic branch the diagonal products coincide, because J preserves the pairing:
  C₂₂₂ = ⟨Jy₁, Jv₁⟩⟨Ju₁, Jv₁⟩⟨Ju₁, Jy₁⟩ = C₁₁₁. So level 2 is c² = 1, together with the nonvanishing of the diagonal pairings.
- **The charts.** Write each of u₁, v₁, y₁ as (1, x) or (x, 1), giving 8 charts that cover every vector.
- **The computation.** In each chart, the level-2 minors, saturated by the diagonal pairings and by c, leave exactly (c − 1)(c + 1). The
  level-3 minors at c = 1 leave exactly "some (1, x)-coordinate x is 0", a vector equal to e₀. At c = −1 they leave "some (x, 1)-coordinate
  is 0", a vector equal to e₁ (check 3).
- **The implication laws.** The case u₁ = e₀ is e₀⊗v⊗y + Jv⊗Jy⊗e₁. The others follow by the rotation of roles, which maps the cyclic
  branch to itself and moves the special vector, by the complement (e₀ ↔ e₁), and by the reflection (the mirror branch). ∎

## Proof of Theorem 3

- **The sectors.** Sector 1 is e₀ ⊗ v ⊗ y and sector 2 is Jv ⊗ Jy ⊗ e₁, with v = (v₀, v₁) and y = (y₀, y₁) arbitrary.
- **Expansion.** Expand the corner relation over a sector for every triangle. A vertex factor is the pairing of the vectors that meet at
  that vertex.
- **Vanishing factors** (check 4):
  - ⟨u₂, v₁⟩ = ⟨Jv, v⟩ = 0 on the bottom edge (base of T(i, 0), b-corner of T(i−1, 0)).
  - ⟨u₁, y₂⟩ = ⟨e₀, e₁⟩ = 0 on the left edge (base of T(0, j), c-corner of T(0, j−1)).
  - ⟨y₁, v₂⟩ = ⟨y, Jy⟩ = 0 on the top edge (c-corner of T(i, k−1−i), b-corner of T(i−1, k−i)).
  - At an inner vertex (base of T(i, j), b-corner of T(i−1, j), c-corner of T(i, j−1)), Σ_x u₁(x)v_s(x)y₂(x) = 0 because u₁ = e₀ and
    y₂ = e₁.
- **The closure rules.** A sector assignment with nonzero weight therefore obeys three rules.
  - If T(i, j−1) has sector 2, so does T(i, j): up every column, from the left-edge and inner rules.
  - If T(i, 0) has sector 2, so does T(i−1, 0): left along the bottom row.
  - If T(i−1, k−i) has sector 2, so does T(i, k−1−i): down-right along the top row.
- **All or nothing.** Start from any sector-2 triangle and go up its column, along the top row to T(k−1, 0), left along the bottom row, and
  up every column. Every triangle is then in sector 2. So only the all-1 and the all-2 assignments survive.
- **Their weights.** There are k − 1 bottom, k − 1 left and k − 1 top vertices, and (k−1)(k−2)/2 inner ones.
  - All-1 has bottom factors ⟨e₀, v⟩ = v₀, left factors ⟨e₀, y⟩ = y₀, top factors ⟨y, v⟩, and inner factors v₀y₀.
  - All-2 has bottom factors ⟨Jv, Jy⟩ = ⟨v, y⟩, left factors (Jv)₁ = v₀, top factors (Jy)₁ = y₀, and inner factors v₀y₀.
  - So both weigh ⟨v, y⟩^(k−1) (v₀y₀)^(m_k).
- **Conclusion.** Their corner terms are the two sectors, so R_k = ⟨v, y⟩^(k−1) (v₀y₀)^(m_k) w. The other types follow by symmetry.
- **Check 4** confirms all twelve types in exact integers for k = 2 to 9. ∎

## Proof of Proposition 4

- **The factorization.** For w = u(a)M[b][c] the b–c edges of the triangles form disjoint paths along the anti-diagonals |v| = s. The top
  one runs from B to C and gives (M^k)[x_B][x_C]. The others are closed sums giving scalars, and A carries u(x_A). So
  R_k = u ⊗ M^k times a scalar. Check 5 verifies this symbolically for k = 2, 3.
- **The consequence.** Exactness at level 2 forces M² = cM with c ≠ 0. Then M is diagonalizable with eigenvalues in {0, c}.
  - Rank one gives M = xzᵀ, a product.
  - Rank two gives M ∝ I, the law u(a)[b = c].
- **The other corners.** The rotations follow by symmetry, and check 5 confirms them exact for k = 2 to 8. ∎

## Proof of Corollary 5

- **Stratum G.** Lemma 1 splits G into the size-four covers, which go to ticket A's Theorem 1 by symmetry, and the cyclic covers, handled
  by Theorems 2 and 3.
- **Stratum R.** Proposition 4.
- **Knots.**
  - Implication supports fail K2, since forgetting b leaves a ⇒ c.
  - Products and u(a)[b = c] are not knots either.
  - Among ticket A's classes only signed not-all-equal is a knot, so the knots are its rotations (check 6). ∎

## What the computation checks

`check.py` (about 40 seconds):
- **Lemma 1.** The level-2 coefficient identity (symbolic, twelve vector entries) and the hexagon with its five minimal covers. Random
  instances confirm that the size-four covers are pair-symmetric.
- **Theorem 2.** The cyclic branch in eight charts, by Gröbner bases.
- **Theorem 3.** The vanishing pairings and weights (symbolic), and all twelve types exact at levels 2 to 9 with factor (1 + st)^(k−1)
  (exact integers).
- **Proposition 4.** The rank-one identity, with the rotations exact at levels 2 to 8.
- **Knots,** and controls:
  - a cyclic law without a coordinate vector fails level 3;
  - a perturbed implication law fails;
  - c = 2 fails level 2.

## Reading

- **The wave is forced among knots, not among all laws.**
  - Besides the standing wave, whole families of laws reproduce themselves at every scale: implication laws, products and laws forcing two
    corners equal.
  - None of them is a knot. The implication laws compose like a one-dimensional chain: their factor (1 + st)^(k−1) is that of a path of k
    edges, and a sector change can only sweep through the whole gasket.
- **Two/three.** Every persistent law other than the wave is degenerate as a relation. In the knot sense, signed not-all-equal and its
  rotations are the only three-place laws that build every gasket.

## Nonclaims

- **The stratum W** (vanishing hyperdeterminant, full multilinear rank) is not classified. A numerical search is recorded as scoping in the
  decision note.
- **"Every level"** holds where the factor is nonzero.
