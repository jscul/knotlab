# SL(2,3) counting is polynomial with bounded homology

Status: Proved

## Standard statement

**Hypotheses (H).** G is a finite group with:
- a central subgroup A ≅ (Z/2)^m;
- a normal subgroup N ⊇ A with N/A ≅ (Z/2)^k;
- a nilpotent quotient G/N.

**Notation.**
- For a finite presentation P = ⟨X | R⟩, let E ∈ F₂^{R×X} be the exponent-sum matrix mod 2.
- ℓ = dim ker(Eᵀ) is the F₂-dimension of H² of the presentation complex.

**Theorem 1.** Under (H):

  |Hom(P, G)| = 2^{m·dim H¹(P; F₂)} · Σ_{ψ ∈ Hom(P, G/N)} #{v ∈ L_ψ : Q_ψ(v) = 0}.

- **The lift space.** L_ψ ⊂ (F₂^k)^X is the affine space of lifts of ψ to G/A, cut out by linear equations over F₂.
- **The obstruction.** Q_ψ: L_ψ → F₂^{mℓ} has coordinates that are polynomials of degree at most 2.
- **The algorithm.** Fix G and a bound d on dim H¹(P; F_p) for the primes p dividing |G/N|, and on ℓ. Then the right-hand side is
  computable in time polynomial in the size of P.

**Corollary 2 (3-manifolds).** For balanced presentations (|R| = |X|), ℓ = dim H¹(P; F₂). Closed orientable 3-manifolds have balanced
presentations:
- from Heegaard diagrams;
- from integral surgery on a knot diagram, where the Wirtinger relators minus one plus μ^p λ give one.

So for fixed G satisfying (H), counting Hom(π₁(M), G) is polynomial for closed orientable 3-manifolds with |H₁(M)| bounded, given in
these forms.

**Corollary 3 (SL(2,3)).**
- **It satisfies (H)** with A = {±I}, N = Q₈ and G/N = Z₃.
- **It is not abelian-by-nilpotent.** Its normal subgroups are 1, Z₂, Q₈ and SL(2, 3), and none that is abelian has a nilpotent
  quotient. Its Fitting height is 2.
- **So the line is not "abelian-by-nilpotent".** With bounded first homology, counting maps into SL(2,3) is polynomial, so the
  polynomial side strictly contains the abelian-by-nilpotent groups of `BOUNDED-H1-20261025-001B`. S₄, of Fitting height 3, is
  #P-hard there (`CLOSED-H1-20261025-001C`).

## Nearest known result

- **Samperton and Weiß**, *Obstruction theory and the complexity of counting group homomorphisms*, arXiv:2602.02885v2 (2026).
  - Lemma 3.1.1: the obstruction map Hom(Γ, B) → H²(Γ, A) is quadratic for a class-2 nilpotent G = A ×_η B.
  - Lemma 3.1.2: zeros of a quadratic map into a bounded abelian group are counted by Gauss sums.
  - Theorem 2: class-2 nilpotent targets are polynomial on triangulated 3-manifolds with |H²(M; Z(G))| bounded.
  - Their domain is the untwisted group Hom(Γ, B). Footnote 11 says it is "not clear" that the method extends to twisted
    coefficients. They do not treat non-nilpotent targets.
- **Matei and Suciu** (2005) count epimorphisms onto finite solvable groups through cohomology, without complexity bounds.
- **`BOUNDED-H1-20261025-001B`.** Abelian-by-nilpotent targets; it supplies Lemmas 1.2 and 1.3 below.
- **Counting zeros of quadratic polynomials over F₂ in polynomial time** is classical: Ehrenfeucht and Karpinski (1990), and Gauss
  sums of quadratic forms. It is cited, and implemented and tested here.
- **What is new here.**
  - The domain of the quadratic obstruction is the twisted cocycle space of the A₄ level. It can be exponentially large, while the
    obstruction lands in the untwisted, bounded group H²(·; F₂).
  - This makes SL(2,3) the first target in the workspace that is polynomial with bounded homology but not abelian-by-nilpotent.
- **Novelty.** `candidate-local-delta`, with folklore risk medium: it is a natural combination of known methods. No source in the
  bounded scan treats SL(2,3) or non-nilpotent central extensions (`research/SL23-BOUNDED-20261025-001/scan.md`).

## 1. Three levels

**Lemma 1.1 (central lifts).** Let ρ̄: P → G/A be a homomorphism.
- **The signs.** Choose lifts g̃_x ∈ G of ρ̄(x). Each relator then evaluates to an element σ_r ∈ A.
- **Changing a lift.** Replacing g̃_x by g̃_x·a, with a ∈ A, changes σ_r by ε_x(r)·a. Here ε_x(r) is the exponent sum of x in r mod
  2, and A is central of exponent 2.
- **Existence.** So ρ̄ lifts iff σ ∈ A^R lies in the image of E ⊗ A, that is, iff w·σ = 0 ∈ A for every w ∈ ker(Eᵀ).
- **Number of lifts.** If one lift exists, the lifts form a torsor for Hom(P, A), of size 2^{m·dim H¹(P; F₂)}. ∎

**Lemma 1.2 (affine lifts through N/A).** Fix ψ: P → G/N and coset representatives s: G/N → G with s(1) = 1. The lifts of ψ to G/A
are the maps x ↦ s(ψ(x))·v_x, with v ∈ (N/A)^X satisfying one F₂-linear equation system per relator. They form an affine space L_ψ,
computed by Gaussian elimination, as in `BOUNDED-H1-20261025-001B`.

**Lemma 1.3 (maps to G/N).** |Hom(P, G/N)| ≤ |G/N|^d, and the maps are enumerated by central F_p lifting. Proved in
`BOUNDED-H1-20261025-001B`.

## 2. The obstruction is quadratic

Write N/A additively.

**The section.** Choose a basis n₁, …, n_k of N modulo A, and set ñ(v) = Π_{i: v_i = 1} n_i in a fixed order.

**Lemma 2.1.** ñ(u)ñ(v) = ñ(u + v)·β(u, v), with β: N/A × N/A → A bilinear.
- **Proof.** N has class at most 2, with N′ ⊆ A and squares in A. Reordering the product creates a commutator [n_i, n_j] ∈ A for each
  inverted pair, and a square n_i² ∈ A for each repeated i. So β(u, v) = Σ_{i>j} u_i v_j [n_i, n_j] + Σ_i u_i v_i n_i², which is
  bilinear. ∎

**Lemma 2.2.** For h ∈ G/N, s(h)·ñ(v)·s(h)⁻¹ = ñ(h·v)·α_h(v), where h·v is the conjugation action on N/A. The map α_h: N/A → A is
quadratic.
- **Proof.** Conjugation by s(h) is an automorphism of N, and A is central. Expanding both sides on u + v gives
  α_h(u + v) = α_h(u) + α_h(v) + β(hu, hv) + β(u, v).
- **Conclusion.** Its polarization is bilinear. Over F₂, such a function is a polynomial of degree at most 2. ∎

**Inverses.** ñ(v)⁻¹ = ñ(v)·β(v, v), since ñ(v)² = ñ(0)·β(v, v) = β(v, v).

**Proposition 2.3.** Let r be a relator, ψ ∈ Hom(P, G/N), and g̃_x = s(ψ(x))·ñ(v_x) for arbitrary v ∈ (N/A)^X. Write the value of r on
the g̃_x as s(1)·ñ(c(v))·a(v). Then c is affine-linear in v, and every F₂-coordinate of a(v) is a polynomial of degree at most 2 in the
coordinates of v.

*Proof.*
1. **Inverses.** Expand each g̃_x^{±1}, using the inverse formula for ñ(v)⁻¹.
2. **Move the representatives.** Push every s(·)^{±1} to the right through the ñ-factors, using Lemma 2.2. Each step multiplies by a
   quadratic A-factor, and replaces v_x by h·v_x for an h ∈ G/N fixed by ψ and the word.
3. **The representatives collect.** They collect into S_r = Π s(ψ(x_i))^{ε_i}, which maps to ψ(r) = 1 in G/N. So S_r ∈ N, and
   S_r = ñ(c_r)·a_r is a constant depending only on ψ.
4. **Multiply the ñ-factors** with Lemma 2.1: Π ñ(w_i) = ñ(Σ w_i)·Π_{i<j} β(w_i, w_j). Then
   ñ(Σ w_i)·ñ(c_r) = ñ(Σ w_i + c_r)·β(Σ w_i, c_r).
5. **Read off.** Each w_i is linear in v, so c(v) = Σ w_i + c_r is affine, and a(v) is a sum of constants, linear terms and bilinear
   terms. ∎

**Consequence.**
- L_ψ is the solution set of c_r(v) = 0 for all r.
- On L_ψ, the relator signs σ_r(v) = a_r(v) are quadratic.
- So the conditions of Lemma 1.1 are the vanishing of Q_ψ(v) = (w·σ(v))_{w ∈ basis of ker Eᵀ}: mℓ quadratic forms.

## 3. Counting the zeros

**Lemma 3.1.**
- **The count.** #{v ∈ L_ψ : Q_ψ(v) = 0} = 2^{−mℓ} Σ_{χ} Σ_{v ∈ L_ψ} (−1)^{χ·Q_ψ(v)}, with χ ranging over (ker Eᵀ)^m.
- **Each inner sum** is the Gauss sum of a quadratic polynomial on an affine F₂-space of dimension D ≤ k·|X|.
- **Pairwise elimination.** Σ_{u_i,u_j} (−1)^{u_i(u_j + α) + u_j β} = 2·(−1)^{αβ}, for α and β affine in the remaining variables. So a
  cross term u_i u_j can be eliminated, adding the quadratic αβ. When no cross terms remain, the sum is ±2^{D′} or 0.
- **Cost.** This takes O(D³) operations (Dickson; see Samperton and Weiß, Lemma 3.1.2).
- **The coefficients** of Q_ψ come from its values at the points of weight at most 2 of a parametrization of L_ψ (O(D²)
  evaluations). Proposition 2.3 guarantees degree at most 2. ∎

## 4. Proofs

**Theorem 1.**
- **The formula.** Lemmas 1.1–1.3 and Proposition 2.3 give it.
- **Running time.** For fixed G and bound d, the algorithm uses:
  - at most |G/N|^d maps ψ;
  - a Gaussian elimination for each L_ψ;
  - O(D²) relator evaluations for the coefficients of Q_ψ;
  - 2^{mℓ} ≤ 2^{md} Gauss sums of cost O(D³) each.

  All of this is polynomial in |X| + Σ_r |r|. ∎

**Corollary 2.**
- **Balanced presentations.** For |R| = |X|, the presentation complex has Euler characteristic 1. So h² = h¹ over F₂, and ℓ =
  dim H¹(P; F₂) ≤ log₂|H₁(M)| for a closed orientable 3-manifold.
- **Sources.** Heegaard diagrams give balanced presentations of π₁(M). For integral surgery on a knot diagram with n arcs, the n − 1
  independent Wirtinger relators and the relator μ^p λ give one.
- **Other inputs.** Converting a triangulation into a Heegaard diagram in polynomial time is standard and cited (see the Ennes–Maria
  route quoted by Samperton and Weiß). ∎

**Corollary 3.**
- **Hypotheses (H)** hold with A = {±I}, N = Q₈ (N/A ≅ V₄) and G/N ≅ Z₃.
- **The normal subgroups** are 1, Z₂, Q₈ and SL(2, 3) (check part 1).
- **Not abelian-by-nilpotent.** The abelian ones are 1 and Z₂, with quotients SL(2,3) and A₄, neither nilpotent. Q₈ is nilpotent with
  quotient Z₃, so the Fitting height is 2. ∎

## Check

`check.py` uses the standard library only and imports nothing from other proofs. It runs in about 1 s. Its output is `result.json`.

1. **Structure.**
   - SL(2, 3): centre of order 2, normal subgroups of orders 1, 2, 8 and 24, no abelian normal subgroup with a nilpotent quotient, and
     Fitting height 2.
   - S₄ admits no structure (H) (control).
   - Q₈, D₈ and Z₂ × SL(2, 3) satisfy (H), the last with m = 2.
2. **Gauss sums.** 400 random quadratic polynomials agree with brute force.
3. **The algorithm against brute force.**
   - Integral surgeries S³_p(K), for p ∈ {0, 1, 2, 3, 4, 6, −6} and K ∈ {3₁, 4₁, 8₁₈, 4₁ # 4₁, 10₁₂₄}, counted by brute force over all
     homomorphisms of the knot group with ρ(μ)^p ρ(λ) = 1.
   - 25 random presentations, counted exhaustively.
   - All of this for each of the four groups: 240 cases, all equal.
   - At random points, every relator sign is checked to be a polynomial of degree at most 2.
4. **Scale.** SL(2, 3) on S³₆ of (4₁)^{#k}:
   - for k = 12 there are 48 generators and lift spaces of dimension 26, counted in 0.3 s (134,250,498 maps);
   - brute force confirms k ≤ 3;
   - the counts follow 2·(2^{k+1} + (−1)^k)². This is observed, not claimed.
5. **Controls.**
   - Dropping the obstruction overcounts on S³₂(3₁) and on S³₆(4₁ # 4₁).
   - It changes nothing on S³₃(8₁₈), where H²(M; F₂) = 0.

## Scope

- **Covered.** The class (H): a central layer that is an elementary abelian 2-group, over an elementary abelian 2-layer, over a
  nilpotent quotient.
- **Not covered.**
  - Central layers of odd exponent. Their cocycles need not be bilinear (carries).
  - Non-central or twisted obstruction targets: Samperton and Weiß's open twisted case.
  - Fitting-height-2 groups with deeper nilpotent layers, where the obstruction can have degree 3 or more.
- **Cited, not proved.**
  - The Gauss-sum algorithm, which is implemented and tested here.
  - Lemmas 1.2 and 1.3, from `BOUNDED-H1-20261025-001B`.
  - The conversion of triangulations to balanced presentations.
- **No overclaim.** No claim about P versus NP.
