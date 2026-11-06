# What the twist sees of a three-manifold

Status: Proved

Ticket `SIGNED-3D-20261029-001B`, 2026-10-29.

**What it uses:**
- from `SIGNED-3D-20261029-001A-P001`: the twelve signed laws and their factors;
- from `TWIST-3D-20261025-001A-P001`:
  - the values of the counting laws;
  - the sampler and homology code for ordered triangulations;
- classical background, cited and not admitted as local evidence:
  - the cup product on ordered simplicial cochains;
  - the Steenrod square Sq¹ = ρβ, the mod-2 reduction of the integral Bockstein;
  - Wu's formula;
  - the linking form of a closed oriented three-manifold.

## Standard statement

**Setting.** M is a closed orientable three-manifold with an ordered triangulation having V vertices and T tetrahedra.
- h = |H¹(M; Z/2)|.
- **The cubic form.** ℓ(a) = ⟨a ∪ a ∪ a, [M]⟩ ∈ Z/2 for a ∈ H¹(M; Z/2).
- **Its Gauss sum.** D(M) = Σ_(a ∈ H¹(M; Z/2)) (−1)^ℓ(a).
- **Normalization.** The state sum c of a law with factors (λ, μ) is normalized as N = c (λ³/μ)^V λ^(−T).

**Results.**
- **Theorem 1 (values).** For the twelve classes of `SIGNED-3D-20261029-001A`:
  - **The counting laws** give N = 1, 1, 2, h/2, h/2, h and 1 (all 0, all 1, all equal, even cocycles, odd cocycles, even or odd, free).
  - **The twisted laws** on even or on odd cocycles give D(M)/2.
  - **The mixed laws on even-or-odd** give (D(M) + h)/2 with one part twisted, and D(M) with both.
  - On the triangulation, ℓ(x) = Σ_t x₀₁x₁₂x₂₃, the twisted law's exponent.
- **Proposition 2 (one bit).** On a closed orientable three-manifold, a ↦ ℓ(a) is linear. So D(M) is h when the cubic form vanishes and 0
  otherwise.
- **Proposition 3 (the linking form).** ℓ(a) = 2 lk(βa, βa) mod 2, where β: H¹(M; Z/2) → H²(M; Z) ≅ H₁(M) is the Bockstein.
  - Hence D(M) = 0 exactly when some element t of H₁(M) with 2t = 0 has lk(t, t) = 1/2.
  - **Free classes.** ℓ vanishes on classes that lift to integer classes.
  - **Cyclic homology.** For H₁ = Z/n: D = 1 if n is odd, 0 if n ≡ 2 (mod 4), and 2 if n ≡ 0 (mod 4). For H₁ = Z, D = 2.
- **Corollary 4 (the twist sees beyond the counting laws).**
  - **Not a function of homology.** D is not determined by H₁(M). RP³ # RP³ (lk = ⟨1/2⟩ ⊕ ⟨1/2⟩) has D = 0, while the quaternion space S³/Q₈
    (a³ = 0 for every a) has D = 4; both have H₁ = (Z/2)².
  - **On the samples.** Among the sampled triangulations with H₁ = (Z/2)², both D = 0 and D = 4 occur, while every counting law takes the same
    value on them.
  - **So:** one bit per edge, with signs and order, sees exactly h and one further bit: whether the linking form takes the value 1/2 on an
    element of order 2. Counting sees only h.

## Nearest known result

- **In the repository.**
  - `TWIST-3D-20261025-001A` and `HUB-DIMENSION-20261024-001A`: counting laws see only h.
  - `SIGNED-3D-20261029-001A`: the census.
- **Outside.**
  - The twisted Z/2 Dijkgraaf–Witten invariant is classical, as is its expression through ⟨a³, [M]⟩ and the linking form. Work on mod-2
    Dijkgraaf–Witten invariants writes the Z/2 linking form as a triple cup product (arithmetic Dijkgraaf–Witten theory) and evaluates
    lens spaces through the mod-2 linking number.
  - Also classical:
    - the linearity of a ↦ a³ on orientable three-manifolds (Wu);
    - the cohomology rings of RP³ # RP³ and S³/Q₈;
    - the linking forms of lens spaces (Conway, Friedl and Herrmann, "Linking forms revisited").
- **Classification.** Classical throughout. The local content is the identification of the program's census laws with these invariants,
  checked on samples.

## Proof of Theorem 1

- **The counting laws.** `TWIST-3D-20261025-001A`, Corollary 2.
- **The twisted law on even cocycles.**
  - Its support consists of the labellings with every face even, which are the mod-2 1-cocycles x, and its weight is the same for both
    orientations. So c = Σ_(x∈Z¹) (−1)^(Σ_t x₀₁x₁₂x₂₃).
  - With the Alexander–Whitney cup product on ordered cochains, (x ∪ x ∪ x)[0123] = x₀₁x₁₂x₂₃.
  - The sum of all tetrahedra is the mod-2 fundamental cycle, because every face lies in two tetrahedra. So the exponent is
    ⟨x³, [M]⟩, which depends only on the class of x.
  - Hence c = |B¹| · D(M) = 2^(V−1) D(M) for connected M, and N = c/2^V = D(M)/2.
- **The odd and mixed laws.**
  - The odd labellings, with every face odd, are x + 1 for even cocycles x. The odd twisted weight is the even twisted weight of x, so
    it gives the same value.
  - The even-or-odd laws add an even part and an odd part, each twisted or not. ∎

## Proof of Proposition 2

- **Expanding the cube.** In H*(M; Z/2) the cup product of degree-one classes commutes, so (a + b)³ = a³ + b³ + a²b + ab².
- **The cross term.** By the Cartan formula, a²b + ab² = Sq¹(ab).
- **Wu's formula.** Sq¹ into the top degree is multiplication by v₁ = w₁(M), which vanishes for orientable M. So ⟨Sq¹(ab), [M]⟩ = 0, and ℓ
  is linear.
- **The value of D.** A nonzero linear form takes the value 1 on half of H¹, so D = 0. Otherwise D = h. ∎

## Proof of Proposition 3

- **The Bockstein form.** For degree-one classes, a ∪ a = Sq¹a = ρβa. So ℓ(a) = ⟨a ∪ ρβa, [M]⟩.
- **The linking form.**
  - The linking form is lk(βz, y) = ⟨z ∪ y, [M]⟩ ∈ Q/Z for z ∈ H¹(M; Q/Z) and torsion y ∈ H²(M; Z).
  - With z = a/2 it gives lk(βa, y) = ⟨a ∪ ρy, [M]⟩/2, hence lk(βa, βa) = ℓ(a)/2.
  - The image of β is the set of t with 2t = 0, by the Bockstein exact sequence. So ℓ ≡ 0 exactly when lk(t, t) = 0 for all such t.
- **Free classes.** Classes that lift to integer classes have βa = 0.
- **Cyclic homology.** For H₁ = Z/n the linking form is lk(g, g) = q/n with q prime to n.
  - For even n the element of order 2 is t = (n/2)g, and lk(t, t) = nq/4.
  - If n = 2m with m odd, q is odd and nq/4 = mq/2 ≡ 1/2. If 4 divides n, it is ≡ 0.
  - For odd n, H¹(M; Z/2) = 0 and D = 1. ∎

## Proof of Corollary 4

- **RP³ # RP³.** Its cohomology ring is that of the two summands, each with a³ ≠ 0, so ℓ ≠ 0 and D = 0.
- **S³/Q₈.** Its mod-2 cohomology in degrees up to 3 is that of the quaternion group: x² + xy + y² = 0 and x²y + xy² = 0. These give
  x³ = x²y + xy² = 0 and likewise y³ = 0, so ℓ ≡ 0 and D = 4.
- **The samples.** Check 5 finds sampled triangulations with H₁ = (Z/2)² and D = 0 (four tetrahedra) and D = 4 (three tetrahedra). Every
  counting law takes the values (2, 2, 2, 4, 1) on both, so they are different manifolds that counting cannot tell apart. ∎

## What the computation checks

`check.py` (about 10 seconds) uses 76 sampled ordered triangulations with 1 to 4 tetrahedra. Their first homology is 0, Z, Z/2, Z/3,
Z/4, Z/5, Z/7, Z/8 or (Z/2)².
- **Two cochain formulas for the cubic form.** On every 1-cocycle of every sample, the triple cup product Σ_t a₀₁a₁₂a₂₃ (the law)
  equals the Bockstein formula Σ_t a₀₁ · (½ δã)₁₂₃. This is an independent formula, Steenrod's Sq¹ = ρβ at the cochain level. Both are
  constant on classes.
- **Linearity** of ℓ for every pair of classes, so D ∈ {0, h}.
- **The twelve state sums**, normalized, against Theorem 1.
- **The cyclic rule of Proposition 3**, by homology type.
- **The (Z/2)² dichotomy.**
- **Controls.**
  - The star cubic (−1)^(x₀₁x₀₂x₀₃) fails the move identities and is not a function of the class on some sample.
  - A sample with H₁ = Z/2 has D = 0.

## Reading

- **Interference sees one more bit.**
  - Counting with one bit per edge sees a three-manifold only through h = |H¹(M; Z/2)|.
  - With signs and the vertex order it also sees whether the linking form gives 1/2 on an element of order 2. That bit is not a function
    of homology: it separates RP³ # RP³ from S³/Q₈.
- **Only one bit, and only as a phase.**
  - The relation underneath is still the cocycle (parity) relation, and the sign is a linear functional of the class.
  - So in three dimensions interference does not build new structure. It reads one more global bit off the same parity.
- **Harmonies.** The twisted law is a cancellation in the sense the owner means. Classes with a³ ≠ 0 cancel those with a³ = 0 exactly
  when the cubic form is nonzero, and that cancellation is the information.

## Nonclaims

- Only one bit per edge with weights in {−1, 0, 1}.
- The identification of specific manifolds relies on cited cohomology rings. The samples are not identified beyond their homology and D.
- Nothing is claimed about larger labels, complex phases or Turaev–Viro-type weights.
