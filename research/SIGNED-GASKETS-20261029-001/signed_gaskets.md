# A knot that builds every gasket

Epic `SIGNED-GASKETS-20261029-001`, 2026-10-29.

## The question

- **The owner's request (2026-10-29).** "Yes, please continue," on the recommendation of `SIGNED-SUBDIVISION-20261029-001`.
  Scoping had found one signed not-all-equal law exact on the level-k Sierpinski gaskets for k = 2 to 11. Prove it for every k,
  explain it, and find which other signed laws do the same.
- **Setting.** SG_k is a triangle cut into k², keeping its k(k+1)/2 up triangles. One three-bit law sits on each up triangle, glued
  at shared vertices, and R_k is the corner relation.
  - A law is exact when R_k = λ_k w with λ_k ≠ 0.
  - Exactness at level k builds a tower: a finitely ramified self-similar space of dimension log(k(k+1)/2)/log k, which tends to 2.
- **Why it matters.**
  - `SHARED-SUBDIVISION-20261029-001` and `SIGNED-SUBDIVISION-20261029-001` showed that no non-affine knot reproduces itself under
    shared subdivision of the plane, with counts, signs or real weights.
  - Finitely ramified towers were known to carry signed knots at k = 2 (`INTERFERENCE-20261029-001B`).
  - The gaskets of level k fill the gap in dimension between those towers and the plane.
- **Intuitions targeted:** space from logic without a drawn space; everything relational (harmonies as cancelling phases); the
  two/three boundary.

**The evidence:**
- [Signed not-all-equal reproduces itself on every level-k Sierpinski gasket](../../proofs/SIGNED-GASKETS-20261029-001A/SIGNED-GASKETS-20261029-001A-P001_signed_not_all_equal_reproduces_itself_on_every_gasket/proof.md) (A, proof);
- [Which signed laws reproduce themselves on which gaskets](../../proofs/SIGNED-GASKETS-20261029-001B/SIGNED-GASKETS-20261029-001B-P001_which_signed_laws_reproduce_themselves_on_which_gaskets/proof.md) (B, proof and exact census);
- scoping (scratch, not evidence): the first factors and residues, the search for structure, and the tetrahedral probe behind the
  recommendation.

## Outcome in one paragraph

**A knot builds exactly self-similar space of every dimension below 2.**
- **A (proved for every k).**
  - The law is the Legendre symbol modulo 3 with a sign on its first corner: w(a, b, c) = (−1)^a ((a+b+c) | 3). It is also the
    multiplication of the Eisenstein field, and a standing wave of two opposite sixth-root phases, (−1)^a sin(πE/3)/sin(π/3).
  - On every level-k gasket its corner relation is λ_k w.
  - The proof splits each copy into its two phases. The gasket's two edges from the first corner lock the phases at the three
    corners together, and flipping every phase is odd, so the phases always recombine into the same wave.
  - λ_k is never zero: modulo 3 the gasket collapses to ±w, because the only surviving edge sets are the empty set and the two
    edges of the gasket.
  - The same proof covers a whole family of real laws, (−1)^a sin(θE)/sin θ. Signed not-all-equal is the only member that is a knot.
- **B (census and families).** Of the 1,168 signed laws, 68 are exact on some gasket up to level 12.
  - 26 lie in families proved for every k: rotations, relabelings by position parity, a field-twisted variant with period 4 in k,
    and linear parity at powers of 2 (Lucas).
  - 42 are single-level coincidences: 30 three-excluded laws at k = 3 and 12 not-all-equal laws at k = 5.
- **The plane stays out of reach.** For laws on up triangles, the subdivided plane is these gaskets plus the triangles that join
  them, and the joining triangles are exactly what the earlier epics found fatal to exactness.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | Signed not-all-equal = (−1)^a((a+b+c)\|3) = (−1)^a sin(πE/3)/sin(π/3) = the product of Q(ω) in the basis of primitive sixth roots (a as output); its row matrices satisfy M₀M₁ = I = M₀ + M₁. |
| A, Theorem 2 | R_k = λ_k w for every k ≥ 1; and R_k = λ_k(θ) w_θ for w_θ = (−1)^a sin(θE)/sin θ, with only θ ≡ ±π/3 giving a knot support. |
| A, Theorem 3 | λ_k ∈ Z, λ_k ≡ (−1)^⌊k/2⌋ (mod 3); indeed R_k ≡ (−1)^N w (mod 3). λ_k = 1, −1, −4, 13, 85, −634, −7492, 115321, … |
| A, Corollary 4 | Exact towers of every level k, dimensions log(k(k+1)/2)/log k → 2; the corner relation's support is a knot (K1–K3). |
| B, Lemmas 1–2 | The gasket's symmetries and complement preserve exactness; relabeling by position parity carries exact laws to exact laws at odd k. |
| B, Theorem 3 | (−1)^a [NAE] is exact exactly at k ≡ 1, 2 (mod 4) when its factor is nonzero (checked to k = 22) and never at k ≡ 0, 3 (cosine form). |
| B, Theorem 4 | Unsigned parity is exact exactly at powers of 2, with factor 2^(k−1). |
| B, Theorem 5 | Census to k = 12: 68 exact laws; 26 in the families, 42 sporadic (30 at k = 3, 12 at k = 5). |

## Reading

- **Space from a law, in the program's terms.**
  - A non-affine knot now builds exactly self-similar spaces whose dimension approaches 2 from below. Nothing is drawn: the law on
    one triangle, glued to copies of itself, fixes the space.
  - The plane is the limit it cannot reach. What separates the gaskets from the plane is coupling between neighbouring gaskets, the
    joining triangles.
- **Harmonies.** The law is a standing wave of two opposite phases (ω^E and ω^(−E)). Exactness is the statement that the two phases
  never mix on a gasket: each travels as a product, and the edges hold them in step.
  - This is the owner's "incommensurables cancelling" in a precise form. The all-equal tuples are where the two phases cancel
    exactly (sin 3θ = 0).
- **Two/three boundary.** The knot is a three-place relation whose cancelling witness (one hidden phase) is complex. With
  nonnegative weights no such law exists (`INTERFERENCE-20261029-001A`).
- **What the gaskets select.** Only two mechanisms persist across infinitely many levels: the standing wave, with its variants, and
  linear parity at powers of 2. Everything else is a single-level coincidence.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — signed not-all-equal on every level-k gasket | **Status:** Successful | Proved for every k with a nonzero factor (A); census and families (B). The second family's factor is nonzero to k = 22 and unproved beyond; the sporadic laws are unexplained. |
| Local direction — exact self-reproduction of knots on finitely ramified gaskets in the plane | Practically exhausted in two dimensions | The persistent mechanisms are classified. What remains (sporadic laws, the second family's factor) is completion at low payoff. |
| Broader exploration — space from a law (question 9) | Known alternatives | The sector proof never uses the dimension. Scoping (not evidence): in three dimensions the four-place standing wave (−1)^a sin(θE)/sin θ vanishes exactly on the tuples with two ones, so every member is a knot (not exactly two ones; knotlab: K1–K3, minimum width 4). It is exact on the level-2 and level-3 Sierpinski tetrahedra at four angles. |
| Long-term goal — space from logic without a drawn space | Capability gained | A knot builds exactly self-similar space of every dimension below 2; the plane is excluded. |
| Next recommendation — the standing-wave law in every dimension | **Next step:** Continue, as a fresh epic. Prove exactness of the (d+1)-place standing wave on every level-k simplex gasket in every dimension d, and decide its nonvanishing. Find for which (d, θ) its support is a knot. Compare with the program's three-dimensional obstructions (`HUB-DIMENSION-20261024-001`). | It would give knots building exactly self-similar spaces of every dimension below d, in every d. A continuous family of knots, one for each angle, reproduces itself in three dimensions. |
| Interest — that recommendation | **3/3 — Hot** | The proof route is the same, and two levels already check in three dimensions. The family is a family of knots there, where the program had found space building blind to three dimensions. Main uncertainty: nonvanishing of the factor at generic angles, and whether the four-place knot has the contact-first standing the program wants (which places are loops and which the contact). |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: scoping only (two levels in three dimensions, four angles, one knot check, seconds of CPU). Stop if the edge-locking fails in some dimension, or after a proof for every d and k. |

**Recommendation.** **Continue**, as a fresh epic: the standing-wave law in every dimension (3/3). Two alternatives were
considered.
- Proving the second family's factor nonzero, and explaining the sporadic laws (1/3). This is completion at low payoff.
- Testing whether the full real family (−1)^a sin(θE)/sin θ, which is not a knot in the plane, reproduces itself under shared
  subdivision of the plane (1/3). It is cheap, but its laws carry no knot.
