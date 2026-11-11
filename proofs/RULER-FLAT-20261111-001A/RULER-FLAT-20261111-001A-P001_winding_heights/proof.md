# The ruler on tori, by winding heights

Status: Proved

Ticket `RULER-FLAT-20261111-001A`, 2026-11-11. The statement was frozen in `research/RULER-FLAT-20261111-001/preregistration.md`
before this proof was written.

Words (2026-11-11). The statements use the literature's words for a given substrate: a triangle is a knot, a vertex a
distinction, an edge a co-knotted pair and a triangulated surface a two-fold weave (Intuitions guide, Glossary).

## Standard statement

Let W = Λ/L be a 6-regular triangulation of the torus (the triangular lattice modulo a sublattice). Consider the 2-colourings of W
with no monochromatic triangle (the triangular Ising antiferromagnet's ground states on the torus). There is an integer invariant M(L),
the largest margin of an admissible tilt, such that: ground states exist if M ≥ 0; for two vertices at graph distance d, the smallest
non-shattered vertex set containing both whose every co-1 subset is shattered has at least min(d, M/3) + 2 vertices, and exactly d + 2
when d < M/3; and if M > 3 the only minimal non-shattered sets of at most three vertices are the triangles. The same holds for the
6-regular triangulations of the Klein bottle whose glide reflection has its axis parallel to a lattice edge, with M defined over the whole
deck group.

## Nearest known result

The plane theorem (`RULER-20261111-001`), and quasi-periodic height functions with a tilt for periodic tilings and dimers (Kenyon,
Okounkov and Sheffield, among others), with the Kirszbraun-type extension criterion. No proved range for the minimal forbidden
patterns on a torus was found. Classification: known-with-delta (the delta is T1 to T4).

## Setting

As in `RULER-20261111-001`: forward steps (1, 0), (0, 1), (−1, −1); D(x, y) the least number of forward steps from x to y, with
D(x, y) + D(y, x) = 3δ(x, y) and δ ≤ D; c(x) = x₁ + x₂ mod 3; for a site x and a spin s, r(x, s) ∈ {0, …, 5} the residue that is
≡ c(x) mod 3 and ≡ s mod 2. Sites of W are cosets x + L; a lift of x is a site of Λ in its coset.

For ℓ ∈ L let ρ(ℓ) be the residue class mod 6 that is even and ≡ ℓ₁ + ℓ₂ mod 3; ρ is a homomorphism L → Z/6. A **tilt** is a
homomorphism τ: L → Z with τ ≡ ρ mod 6; it is **admissible** when τ(ℓ) ≤ D(0, ℓ) for all ℓ ∈ L. Its margin is
M_τ = min over ℓ ≠ 0 of D(0, ℓ) − τ(ℓ) (≥ 0 when admissible), and M = M(W) is the largest M_τ. Applying the bound to ℓ and −ℓ for a
shortest ℓ gives M ≤ 3w/2, w the edge-width; and M ≡ 0 mod 3, since D(0, ℓ) ≡ ℓ₁ + ℓ₂ ≡ τ(ℓ) mod 3.

## Lemmas

**Lemma T0 (admissible tilts are slopes in a triangle).** A tilt τ extends to a linear functional τ̂(x) = αx₁ + βx₂ on R², and τ is
admissible exactly when α ≤ 1, β ≤ 1 and −α − β ≤ 1.

*Proof.* D(0, ·) is positively homogeneous and linear on each of the three sectors between the forward steps, where it equals 1 on
(1, 0), (0, 1), (−1, −1); so τ̂ ≤ D(0, ·) on R² exactly when it holds on those three rays. Lattice directions are dense and both sides
are homogeneous and continuous, so τ ≤ D on L is the same condition. ∎ (The margin M_τ is then the least value of the gauge
D(0, ·) − τ̂ over nonzero lattice vectors.)

**Lemma T1 (torus heights).** The states of W are the L-periodic states of Λ. Their heights (Lemma 1 of the plane proof, normalized
so that σ = h mod 2) satisfy h(x + ℓ) = h(x) + τ(ℓ) for one tilt τ, and that tilt is admissible.

*Proof.* A periodic σ has periodic step pattern, so h(x + ℓ) − h(x) does not depend on x and is additive in ℓ: a homomorphism τ. It is
even (σ periodic) and ≡ c(ℓ) mod 3 (h ≡ c + k), so τ ≡ ρ mod 6. And τ(ℓ) = h(x + ℓ) − h(x) ≤ D(x, x + ℓ) = D(0, ℓ) by Lemma 2. ∎

**Lemma T2 (the criterion with a tilt).** Let S be a set of sites of W with a fixed lift x̃ of each x ∈ S, p a pattern on S, τ an
admissible tilt, and on the complete digraph on S (loops included) put

w_τ(x, y) = ⌊(min over ℓ ∈ L of [D(x̃, ỹ + ℓ) − τ(ℓ)] − r(ỹ, p(y)) + r(x̃, p(x))) / 6⌋.

Then p extends to a state of W whose height has tilt τ if and only if this digraph has no negative cycle.

*Proof.* A state of W with tilt τ has, on the lifts, heights g(ỹ + ℓ) = g(ỹ) + τ(ℓ) with g ≡ r mod 6 (τ(ℓ) ≡ ρ(ℓ) keeps the residues
consistent), and Lemma 2 gives g(ỹ) + τ(ℓ) − g(x̃) ≤ D(x̃, ỹ + ℓ) for all x, y, ℓ; with g = r + 6m this is m(y) − m(x) ≤ w_τ(x, y).
Conversely, given integers m satisfying these (possible exactly when there is no negative cycle, loops included), put g on every lift
by g(ỹ + ℓ) = r(ỹ) + 6m(y) + τ(ℓ) and extend by h(z) = min over lifts of g(·) + D(·, z). The pairwise condition holds for all pairs of
lifts, so by Lemma 3 of the plane proof h is a height function agreeing with g on the lifts (the infimum is finite since τ is
admissible); translating the set of lifts by ℓ adds τ(ℓ) to every candidate, so h(z + ℓ) = h(z) + τ(ℓ), and h mod 2 is an L-periodic
state of Λ, a state of W, with the pattern p. ∎

As in the plane, the numerator is ≡ 0 mod 3 (D(x̃, ỹ + ℓ) ≡ c(ỹ) + c(ℓ) − c(x̃) and τ(ℓ) ≡ c(ℓ)), so it is 6w + e with e ∈ {0, 3}.

**Lemma T3 (the two kinds of negative cycle).** Let x₁, …, x_k be a negative simple cycle of the digraph of Lemma T2, with ℓᵢ ∈ L
attaining the minimum on the edge xᵢ → xᵢ₊₁. Put y₁ = x̃₁ and yᵢ₊₁ = x̃ᵢ₊₁ + ℓ₁ + ⋯ + ℓᵢ, a walk in Λ from y₁ to y₁ + ℓ_tot,
ℓ_tot = Σ ℓᵢ. Then:
- (wrapping) if ℓ_tot ≠ 0, 3k ≥ M_τ + 6;
- (closed) if ℓ_tot = 0, the sites y₁, …, y_k of Λ have diameter at most k − 2, and the pattern yᵢ ↦ p(xᵢ) does not extend to a state of
  Λ.

*Proof.* Σ w = (Σ [D(yᵢ, yᵢ₊₁) − τ(ℓᵢ)] − Σ e)/6 ≤ −1 (the residue terms telescope: r at yᵢ is r(x̃ᵢ) + τ(offset) mod 6), and Σ e ≤
3k. Wrapping: Σ D(yᵢ, yᵢ₊₁) ≥ D(y₁, y₁ + ℓ_tot) = D(0, ℓ_tot) and Σ τ(ℓᵢ) = τ(ℓ_tot), so 3k ≥ D(0, ℓ_tot) − τ(ℓ_tot) + 6 ≥ M_τ + 6.
Closed: Σ τ(ℓᵢ) = 0 and the walk is closed, so as in the plane 3k ≥ 3 diam + 6; and the plane digraph on the yᵢ with the pattern
p(xᵢ) has the same cycle weight (its numerators are congruent mod 6 to the ones above), so by Lemma 4 of the plane proof the pattern
does not extend in Λ. ∎

## Theorems

Fix an admissible tilt τ with M_τ = M (when M ≥ 0).

**T1.** If M ≥ 0, W has states. Take one site x and either spin: the digraph of Lemma T2 has one vertex and one loop, of weight
⌊min over ℓ of [D(x̃, x̃ + ℓ) − τ(ℓ)] / 6⌋ = 0 (ℓ = 0 gives 0 and admissibility gives the rest ≥ 0), so the one-site pattern
extends. With Lemma T1 (a state's tilt is admissible), W has states exactly when M ≥ 0.

**Key step (minimal constrained sets).** Let S ⊆ W be constrained with every proper subset free (a bond, or a tie, or a frozen
distinction), and p a pattern on S that does not extend. Then p does not extend with tilt τ, so Lemma T2 gives a negative simple
cycle C. If C is closed, its plane pattern does not extend in Λ, so p restricted to C's sites does not extend in W (a state of W would
lift to one of Λ carrying it); hence C's sites form a constrained subset of S, so they are all of S, and the lifts yᵢ give |S| ≥
diam_Λ{yᵢ} + 2. If C wraps, |S| ≥ |C| ≥ M/3 + 2.

**T2.** For u ≠ v at distance δ, β_W(u, v) ≥ min(δ, M/3) + 1.

*Proof.* A bond S containing u and v has, by the key step, either |S| ≥ M/3 + 2, or |S| ≥ diam{yᵢ} + 2 for lifts yᵢ of all its sites,
which include lifts of u and v at distance at least δ_W(u, v). ∎

**T4.** If M > 3, W is read faithfully.

*Proof.* By the key step a minimal constrained set of one or two sites would need a closed cycle on at most two sites with lifts of
diameter at most 0, impossible for distinct sites, or a wrapping cycle with 3k ≥ M + 6 for k ≤ 2: impossible for k = 1 when M ≥ 0,
and for k = 2 when M > 0. So nothing is frozen and there is no tie (this part needs only M ≥ 3). A minimal constrained triple needs a wrapping cycle, 9 ≥ M + 6, impossible as M > 3, or a closed cycle on lifts
of diameter at most 1: three pairwise adjacent sites of Λ, a triangle, whose image is a knot of W (distinct sites, as w ≥ 2). Knots are
constrained, so the non-free triples are exactly the knots. ∎

**T3.** If δ = δ_W(u, v) < M/3, then β_W(u, v) = δ + 1.

*Proof.* The lower bound is T2. For the upper bound take lifts ũ, ṽ at distance δ and the plane bond S̃ of `RULER-20261111-001`
(one side of a triangle of side δ with the opposite corner), δ + 2 sites of diameter δ. Since δ < M/3 ≤ w/2, distinct sites of S̃ are
not congruent mod L, so S̃ projects to a set S of δ + 2 distinct sites containing u and v. S is not free: its plane forbidden pattern
cannot occur in a state of W, which would lift. Let T ⊊ S and q a pattern on T. If q did not extend with tilt τ, Lemma T2 would give a
negative cycle C on sites of T. A wrapping C would need |C| ≥ M/3 + 2 > δ + 2 > |T|. A closed C has lifts yᵢ = s̃ᵢ + offᵢ of sites s̃ᵢ ∈
S̃ with diameter at most |C| − 2 ≤ δ − 1; for two of them, |offᵢ − offⱼ| ≤ δ(yᵢ, yⱼ) + δ(s̃ᵢ, s̃ⱼ) ≤ 2δ − 1 < w, so all offsets are
equal and the yᵢ are one translate of sites of T̃. The plane pattern on them then does not extend in Λ, against the freeness of the
plane bond's co-1 subsets (translations of Λ preserve its states). So every co-1 subset of S is free, and S is a bond of W. ∎

## Klein bottles

A 6-regular Klein bottle is W′ = Λ/G, G = L ∪ gL, with g(x) = Ax + s, A a reflection of the lattice with AL = L, As + s ∈ L, and G
acting freely; its states are the G-invariant states of Λ. Of the six reflections, three permute the forward steps (their axes are
parallel to lattice edges; one is (x₁, x₂) ↦ (x₂, x₁)) and three send them to the backward steps (axes perpendicular to edges). Call g an
**edge glide** or an **altitude glide** accordingly. The kind does not depend on the presentation: isomorphic Klein bottles have
deck groups conjugate by a symmetry of the lattice, whose linear part keeps the forward steps or swaps them with the backward ones,
and either way conjugation keeps the kind (no isomorphism class in the check has both). Lemma K0 says the same without coordinates.

**Lemma K0 (the kind, read from the knots).** g is an edge glide exactly when the pairs of W′ can be directed so that every knot is a
directed cycle. Every torus can be so directed.

*Proof.* In Λ such a direction is fixed by one pair: a knot directed on one of its pairs is directed on all three, and any two knots
are joined by a chain of knots sharing pairs. So Λ has exactly two, the forward steps and the backward ones. A direction on W′ lifts
to a G-invariant one on Λ, so every γ ∈ G keeps one of the two, hence keeps the forward steps; conversely, when every γ keeps the
forward steps they descend to W′. Translations keep them, so every torus is directed. ∎

### Edge glides (proved)

Every γ ∈ G then maps forward steps to forward steps, so D(γx, γy) = D(x, y) and c(γx) = c(x) + c(γ0), γ0 the image of the
origin. The **edge-width** is w = min over γ ≠ 1 and x of δ(x, γx).

**Lemma K1 (heights).** A state's height satisfies h(γx) = h(x) + τ(γ) for a homomorphism τ: G → Z that is even, ≡ c(γ0) mod 3,
and satisfies τ(γ) ≤ D(x, γx) for every x. On L, τ is a torus tilt with τ(Aℓ) = τ(ℓ), and τ(g) = τ(As + s)/2. Conversely, for a
torus tilt τ on L with τ ∘ A = τ on L and τ(As + s) ≡ 0 mod 4, putting τ(ℓ ∘ g) = τ(ℓ) + τ(As + s)/2 defines such a homomorphism
(a **Klein tilt**), and if τ is admissible on L then τ(γ) = τ̂(γx − x) ≤ D(x, γx) for every γ ∈ G and x.

*Proof.* h ∘ γ is a height of σ ∘ γ = σ (γ keeps the step rule), so it differs from h by a constant τ(γ), additive in γ, even and
≡ c(γ0) mod 3 as in Lemma T1; τ(γ) ≤ D(x, γx) is Lemma 2. Conjugation gives τ(Aℓ) = τ(gℓg⁻¹) = τ(ℓ), and g² is the translation by
As + s. For the converse, τ̂ (Lemma T0) is A-invariant on R² since L spans it, so τ̂(As + s) = 2τ̂(s) and τ(g) = τ̂(s). The residues are right: A
permutes the forward steps, so c ∘ A = c, τ(As + s) ≡ c(As + s) = 2c(s) mod 3, hence τ(g) ≡ c(s) = c(g0) and τ(ℓ ∘ g) ≡ c(ℓ + s);
and τ(g) is even by the mod-4 condition. For
γ = ℓ ∘ g and any x, γx − x = (Ax − x) + s + ℓ with τ̂(Ax − x) = 0, so τ(γ) = τ̂(γx − x), likewise for translations, and
τ̂ ≤ D(0, ·) on R² (Lemma T0). Additivity holds since τ̂(γγ′x − x) = τ̂(γ(γ′x) − γ′x) + τ̂(γ′x − x). ∎

The margin of a Klein tilt is M_τ = min over γ ≠ 1 and x of D(x, γx) − τ(γ), the gauge D(0, ·) − τ̂ over all displacement vectors
of G, and M = M(W′) is the largest. As for tori, M ≡ 0 mod 3, and M ≤ 3w/2 since
[D(x, γx) − τ(γ)] + [D(γx, x) − τ(γ⁻¹)] = 3δ(x, γx), the second bracket being the margin term of γ⁻¹ at γx.

**Theorem K (T1 to T4 for edge glides).** Lemmas T2 and T3, the key step and T1 to T4 hold for W′ word for word, with G for L, γ for
ℓ, a Klein tilt for the tilt, and M and w as just defined.

*Proof.* The lifts of a site are its G-orbit (G acts freely). Lemma T2: put g(γx̃) = r(x̃) + 6m(x) + τ(γ); since every γ preserves D,
the pairwise condition between γ′x̃ and γỹ is the one between x̃ and γ′⁻¹γỹ, which is the inequality m(y) − m(x) ≤ w_τ(x, y) with
w_τ(x, y) = ⌊(min over γ ∈ G of [D(x̃, γỹ) − τ(γ)] − r(ỹ) + r(x̃))/6⌋, and the residues stay consistent because τ(γ) ≡ c(γ0) mod 3
and is even. The infimum defining h is finite since D(γx̃, z) + τ(γ) ≥ D(γx̃, x̃) + τ(γ) − D(z, x̃) ≥ −D(z, x̃), and h(γz) = h(z) +
τ(γ) because γ permutes the lifts and preserves D; so h mod 2 is G-invariant. Lemma T3: with γᵢ attaining the minimum on the edge
xᵢ → xᵢ₊₁, put Γ₁ = 1, Γᵢ₊₁ = Γᵢγᵢ and yᵢ = Γᵢx̃ᵢ; then D(yᵢ, yᵢ₊₁) = D(x̃ᵢ, γᵢx̃ᵢ₊₁), the walk ends at Γ_{k+1}y₁, Σ τ(γᵢ) =
τ(Γ_{k+1}), and a cycle wraps when Γ_{k+1} ≠ 1, with 3k ≥ D(y₁, Γ_{k+1}y₁) − τ(Γ_{k+1}) + 6 ≥ M_τ + 6. In the closed case the residue
at yᵢ is ≡ r(x̃ᵢ) + τ(Γᵢ) mod 6, so the plane digraph on the yᵢ has the same cycle weight, as before. The key step, T1, T2 and T4 use
nothing else. T3: since δ < M/3 ≤ w/2, distinct sites of the plane bond S̃ are not G-related, so it projects to δ + 2 distinct sites;
for two lifts Γᵢs̃ᵢ, Γⱼs̃ⱼ of a closed cycle, at distance at most δ − 1, put γ = Γᵢ⁻¹Γⱼ: then δ(s̃ᵢ, γs̃ⱼ) ≤ δ − 1 and
δ(s̃ⱼ, γs̃ⱼ) ≤ δ(s̃ⱼ, s̃ᵢ) + δ(s̃ᵢ, γs̃ⱼ) ≤ 2δ − 1 < w, so γ = 1: the lifts are one image ΓT̃ of the lifts of T's sites, and the plane pattern on them
does not extend in Λ, against the freeness of the plane bond's co-1 subsets (lattice symmetries preserve the plane's states). ∎

### Altitude glides (not proved)

Here every γ ∈ gL sends forward steps to backward ones, D(γx, γy) = D(y, x), and −h ∘ g is a height of the same state, so
h(gx) = κ − h(x): heights are quasi-periodic under L and anti-symmetric under the glide. Lemma T2's extension, the least height
compatible with the data, need not be anti-symmetric (h ↦ κ − h ∘ g sends least extensions to greatest ones). The extension lemma the
pre-registration named, that a g-compatible pattern which extends quasi-periodically also extends anti-symmetrically, is false as
phrased: the referee found 52 counterexamples, one on L = ⟨(3, 0), (0, 6)⟩ with A = ((−1, 1), (0, 1)), s = (1, 3), on the sites numbered 5 and
8 by `flat_worlds.klein` with the pattern (0, 1). The referee also sketched a version that requires the data heights themselves to be anti-symmetric and
holds when M_τ > 0 (average the least extension with its reflection and round by 2-SAT); no reading at distance is derived from it
here. Altitude-glide Klein bottles stay computed (`LONG-LOOP-20261111-001`: faithful at edge-width at least 5 to 48 distinctions).

## Scope and nonclaims

- The range δ < M/3 is a proved sufficient condition, not the exact range: the computed record has the equality at distance 3 on tori
  with M = 9 (`LONG-LOOP-20261111-001`), where T2 gives only the lower bound 4 = δ + 1 and T3 does not apply.
- T2 permits shortcuts only where M/3 ≤ δ: at distance 3, only when M ≤ 6. The shortcuts LONG-LOOP and KNOTS-ALONE found are checked
  against this in `check.py` (C4).
- Klein bottles: Theorem K covers edge glides only; altitude glides are not claimed. In the checked range (to 48 distinctions) edge-glide
  Klein bottles have M ≤ 9, so T3 is exercised there only at distance 2.

## Checks

`check.py`, result in `result.json`. The recorded run is the last; two earlier runs had bugs in the check.
- **First run.** C1 reported mismatches on thin tori: the admissibility test looked only at lattice vectors in a box of radius 5 and
  let through tilts that fail on longer vectors. Lemma T0 made the test exact.
- **Second run.** Passed, but the referee found M wrong on 234 tori (of 7,048 recomputed): the search over tilts covered too few
  slopes (220 margins too low) and the lattice vectors behind the margin came from a box too small for thin lattices (14 too high,
  for example M = 9, not 12, on L = ⟨(1, 21), (0, 75)⟩). Several tori counted as having no admissible tilt had one.
- **Since then.** The margin and the criterion are exact, and the Klein checks were added run by run (C7 to C12). The tilts are all integer points of Lemma T0's triangle with the right
  residues; the minima over a coset u + L and over nonzero lattice vectors are taken over every vector of hexagonal length at most
  V + a + c, resp. V (V the index): D(0, ·) − τ̂ is linear and nonnegative on each of the three sectors between the forward steps, and
  L contains (V, 0), (0, c) and (−V, −V), so subtracting the sector's ray vector never raises it and every minimum is reached that
  close. The new margins agree with a wide brute force (tilts tested on every vector to hexagonal length 3V) on 400 random tori. Every
  torus of edge-width at least 2 has an admissible tilt (M ≥ 0), so all of them have states.

Results of the recorded run. Tori: C1, the criterion of Lemma T2 against brute force, every pattern on every set of at most three sites
and 100 sets of four, every torus with 12 to 18 distinctions (136 tori, 850,580 patterns, no mismatch). C2: M ≡ 0 mod 3 and M ≤ 3w/2
on 2,450 tori to 96. C3: T4 on the 1,698 of them with M > 3. C4: T2 and T3 at distances 2 and 3 on every faithful torus to 96 (7,752
distance-2 pairs with M ≥ 9 have a bond of 4; the 2,394 distance-3 shortcuts all have M ≤ 6; 2,772 distance-3 pairs with M ≥ 12 have
bond distance 4). C5: T1 to 48. C6: a mutation (the tilt forced to 0) disagrees with brute force on 53,124 patterns. Edge-glide Klein
bottles: C7, the Klein criterion against brute force on the 60 raw presentations with 12 to 20 distinctions (481,074 patterns, no
mismatch; states exactly when M ≥ 0). C8: on the 53 isomorphism classes with 12 to 48 distinctions, M is the same on every
presentation, ≡ 0 mod 3 and at most 3w/2, states exist exactly when M ≥ 0, and the 34 with M > 3 are faithful. C9: T2 and T3 at
distances 2 and 3 from one distinction (72 distance-2 pairs with M ≥ 9 have a bond of 4; 78 distance-3 shortcuts, all at M ≤ 6; no
class has M ≥ 12). C10: dropping the glide terms from the criterion disagrees with brute force on 17,224 patterns. C11 (Lemma K0): of the 1,665 raw
one-sided presentations with 12 to 48 distinctions, the 582 edge glides are exactly the ones whose pairs can be directed so that every
knot is a directed cycle, and all 2,450 tori can be. C12: dropping the mod-4 condition on τ(As + s) disagrees with brute force on
18,082 patterns, so the condition is needed. The second referee's own computations (in the decision note) extend these, including
T3 at distance 3 on three edge-glide Klein bottles with M = 12.
