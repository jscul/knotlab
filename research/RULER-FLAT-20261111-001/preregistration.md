# The ruler on flat worlds: pre-registration

Epic `RULER-FLAT-20261111-001` (RULER-20261111-001 direction 1; G1, question 9; program topology, group spacing), 2026-11-11, at the
coordinator's go-ahead under the owner's standing mandate. The statement and the failure criterion are frozen before the proof is
written out. The canonical K1–K3 test is unchanged.

## Setting

As in `RULER-20261111-001`: the triangular lattice Λ = Z², forward steps (1,0), (0,1), (−1,−1), D(x, y) the least number of forward
steps, c(x) = x₁ + x₂ mod 3, NAE on every triangle; a bond is a set of three or more distinctions that is not free while every co-1
subset is; β is the least size of a bond through two distinctions, minus one; δ_W is graph distance in W.

A 6-regular torus is W = Λ/L for a sublattice L (Altshuler). For ℓ ∈ L let ρ(ℓ) ∈ Z/6 be the class that is even and ≡ ℓ₁ + ℓ₂ mod 3.
A **tilt** is a homomorphism τ: L → Z with τ(ℓ) ≡ ρ(ℓ) mod 6; it is **admissible** when τ(ℓ) ≤ D(0, ℓ) for every ℓ ∈ L. The
**margin** of W is M(W) = max over admissible τ of min over ℓ ∈ L ∖ {0} of D(0, ℓ) − τ(ℓ) (and −∞ if there is no admissible tilt). It
depends only on L, is a multiple of 3, and is at most 3/2 times the edge-width.

## Frozen statement (tori)

For every 6-regular torus W with M = M(W):
- **T1.** If M ≥ 0, W has NAE states.
- **T2 (lower bound).** For distinctions u ≠ v at distance δ, β_W(u, v) ≥ min(δ, M/3) + 1.
- **T3 (the ruler).** If δ < M/3, then β_W(u, v) = δ + 1, and the side-and-apex set of the plane projects to a bond of W.
- **T4 (faithful).** If M > 3, W is read faithfully: nothing frozen, no tie, and the three-element bonds exactly the knots.

**Failure criterion.** A torus and a pair with δ < M/3 and β_W ≠ δ + 1, or a torus with M > 3 that is not read faithfully: either is
a counterexample to the frozen statement, reported as such. The finite checks compare the statement with every torus with 12 to 96
distinctions already read (`KNOTS-ALONE-20261111-001`, `LONG-LOOP-20261111-001` and its stress test) and with new exact readings.

## Klein bottles

A Klein bottle state is a height function that is quasi-periodic under the translations and anti-symmetric under the glide
(h(gx) = κ − h(x)). The torus proof extends a pattern by the least height compatible with it, which is not anti-symmetric. So the
Klein bottle case is attempted: if an equivariant extension lemma is proved, the analogous statement is claimed; otherwise the Klein
bottles stay computed (`LONG-LOOP-20261111-001`'s faithfulness; the equality was not computed there), and the missing lemma is named.

## Prior work

Quasi-periodic height functions with a tilt (slope) are standard for periodic dimer and tiling models (Kenyon, Okounkov and
Sheffield); the extension criterion is the plane's (`RULER-20261111-001`, with the Kirszbraun-type literature). No proved range of
the minimal forbidden patterns on a torus was found. Prediction from the computed record, not a claim: the range δ < M/3 is
conservative, since LONG-LOOP found the equality at distance 3 on every torus of edge-width at least 6, some of which have M = 9.

## Disclosed before freezing

The margin M was computed for every torus with 12 to 80 distinctions (no law run): it takes the values 0 to 15, is 3/2 the edge-width
rounded down to a multiple of 3 in most cases, and is smaller for some (M = 3 at edge-width 5, 6 and 7 for a few lattices).

## Stop rule

A refereed proof for tori, or the first counterexample; Klein bottles proved or left computed. Then report and hold.

## Correction after freezing (2026-11-11)

Found by the referee, logged in `docs/CORRECTIONS.md` (Not a block); the text above is left as frozen. "Anti-symmetric under the
glide (h(gx) = κ − h(x))" holds only for one-sided weaves whose co-knotted pairs cannot be directed so that every knot is a directed
cycle (drawn: the glide mirror perpendicular to a lattice edge). When they can (mirror parallel to an edge), the glide keeps the
height's direction of climb, h(gx) = h(x) + κ, and the two-sided proof carries over; that half is proved (Lemma K0 and Theorem K in
the proof).
