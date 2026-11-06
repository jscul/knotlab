# Counting maps from 3-manifold groups to nilpotent-by-cyclic groups: pairs, triples and a coprime dichotomy

A consolidated presentation for independent review, corrected and expanded after an independent AI review.

- **Provenance.** Prespatial Labs, contact-first program. Written by Claude on 2026-10-27 at the repository owner's request
  (`COPRIME-PAIRS-20261027-001B`).
- **Predecessor.** The frozen presentation of `COPRIME-DICHOTOMY-20261027-001D`. This text replaces it for reading; the frozen file
  is unchanged.
- **What it consolidates.** The tickets `COPRIME-CLASS2-20261026-001`, `CLASSK-DICHOTOMY-20261026-001`,
  `BEYOND-CLASS2-20261027-001`, `TRIPLE-SYSTEM-20261027-001`, `COPRIME-DICHOTOMY-20261027-001` (A, B, C, D) and
  `COPRIME-PAIRS-20261027-001A`.
- **Frozen predecessors.** Their proof files are unchanged, and `check.py` verifies the SHA256 values recorded by the independent
  reviews. Corrections are made here and in the successor proof `COPRIME-PAIRS-20261027-001A`.
- **Review status.** All reviews so far are independent AI reviews by Codex with finite reimplementations (V2). None is a human
  expert review or a formal certification.
  - Earlier reviews covered `CLASSK-DICHOTOMY-20261026-001C`, `BEYOND-CLASS2-20261027-001C` and `TRIPLE-SYSTEM-20261027-001` A
    and C.
  - The review of `COPRIME-DICHOTOMY-20261027-001` (A, C, D; `research/COPRIME-DICHOTOMY-20261027-001/codex_review_20261027.md`)
    found no blocking counterexample. Its finite checks, written without importing producer code, were:
    - 80 literal-matrix comparisons of the steering coefficient κ_t at orders 3–6 on U₄(F_p) ⋊ diag(1, t, 1, t), all passing, 78
      nonzero. The wrong constant 2 was rejected in all 48 nonzero cases where it differs from κ_t.
    - Exact pinned counts 305 on 6₁ and 93,025 = 305² on 6₁ # 6₁ (p = 5, d = 4): multiplicativity, and a chiral control.
    - Replays of the producers' checks.
  - It asked for four corrections and two expansions. They are made in §§2, 6 and 9, and in `COPRIME-PAIRS-20261027-001A`.

## 0. Summary

Let G = N ⋊ C_r, with N a finite p-group of exponent p and class c < p and r | p − 1. We count homomorphisms π₁M → G for closed
oriented 3-manifolds M with H₁(M; F_p) = 0 and boundedly many sectors.

The obstruction theory of such counts is governed by the Lie algebra 𝔫 = log N, graded by the characters of C_r. Two conditions
decide everything that is decided here:

- **pairs:** nontrivial characters bracket only with their inverses;
- **triples:** the resulting symmetric pair has an abelian Lie triple system.

| | statement | scope | status |
| --- | --- | --- | --- |
| Theorem A | pairs and triples hold at the sector order ⇒ the count is rigid, a pure dimension formula; polynomial time | every class c < p, no grading | proved; AI-reviewed (V2) |
| Theorem B1 | class 2 and a pair failure ⇒ #P-hard | class (K) = class 2 | proved; AI-reviewed (V2) |
| Theorem B2 | pairs hold, triples fail ⇒ #P-hard | graded, class ≤ 4, every sector order d | proved; AI-reviewed (V2), corrected and expanded |
| Theorem B3 | the cross-layer pair x (1), y (α), α² ≠ 1 ⇒ #P-hard | one class-3 example | proved |
| Corollary C | polynomial iff the criterion holds at every occurring sector order | all graded class ≤ 4 algebras except one residual family | proved, with the residual family open |
| Open | pair failures in classes 3 and 4 | — | under study in `COPRIME-PAIRS-20261027-001` |

**Interpretation boundary.**
- r counts the characters of the cyclic action, not the values of Boolean variables. The coefficients lie in F_p with p ≥ 5.
- "Pairs versus triples" refers to Lie brackets of character components.
- These are counting-complexity statements about fixed finite groups. They are not a 2-CNF/3-CNF theorem, an emergence result, or
  a bridge from the K1–K3 knot criterion to complexity.

## 1. Setting and notation

- **The group.**
  - p ≥ 5 is prime; Theorem A only needs p odd. r | p − 1, and ζ ∈ F_p^× has order r.
  - N is a finite p-group of exponent p and nilpotency class c < p, and 𝔫 = log N is its Lie algebra over F_p (Lazard [La];
    [Kh, Ch. 9–10]).
  - C_r = ⟨σ⟩ acts on N by automorphisms, and G = N ⋊ C_r.
- **Characters.** Since r is prime to p, the action on 𝔫 is semisimple (Maschke): 𝔫 = ⊕_{j ∈ Z/r} 𝔫_j, with σ acting on 𝔫_j by ζ^j
  and [𝔫_i, 𝔫_j] ⊆ 𝔫_{i+j}.
- **Graded.** Hardness assumes 𝔫 = L₁ ⊕ ⋯ ⊕ L_c graded ([L_i, L_j] ⊆ L_{i+j}), with C_r preserving the grading.
- **Sector orders.**
  - For d | r, C_d = ⟨σ^{r/d}⟩. Its characters are the classes α mod d, and 𝔤_α := 𝔫^{(d)}_α = ⊕_{j ≡ α (d)} 𝔫_j.
  - 𝔫′_d := ⊕_{α ≢ 0} 𝔤_α is the *odd* part and 𝔤₀ the *even* part.
- **Manifolds.**
  - M is closed and oriented with H₁(M; F_p) = 0. So H₁(M) is finite of order prime to p, and H¹(π₁M; F_p) = H²(π₁M; F_p) = 0
    (the second by Hopf [Ho]).
  - A **sector** is ψ ∈ Hom(H₁(M), C_r). Its order is |ψ(π₁M)|, which divides D(M) = gcd(r, exponent of H₁(M)).
  - Hom(π₁M, G) = ⊔_ψ Hom_ψ.
- **Bounded sectors.** Polynomial algorithms assume |Hom(H₁(M), C_r)| ≤ C₀. This is the bounded-2-rank assumption of the r = 2
  papers, and in general a bound on the r-torsion rank of H₁. Without it the number of sectors is exponential. It is a standing
  hypothesis of every polynomial statement below.
- **Cochains.** Twisted cochains follow the left convention c(gh) = c(g) + χ(g) c(h).

## 2. Statements

### 2.1 The criterion and its structure

**Definition.** For d | r:
- (P2_d) **pairs:** [𝔤_α, 𝔤_β] = 0 whenever α, β and α + β are all nonzero mod d;
- (P3_d) **triples:** [[𝔤_α, 𝔤_{−α}], 𝔤_β] = 0 for all nonzero α, β.

The **criterion at d** is (P2_d) ∧ (P3_d).

**Lemma 2.1 (the parity automorphism).** Let θ_d act by +1 on 𝔤₀ and by −1 on 𝔫′_d.
- (P2_d) holds iff θ_d is a Lie automorphism of 𝔫. Then θ_d commutes with the C_r action: (P2_d) supplies a **compatible parity
  automorphism**.
- The following are equivalent:
  - (i) the criterion at d;
  - (ii) [𝔫′_d, 𝔫′_d] ⊆ 𝔤₀ and [[𝔫′_d, 𝔫′_d], 𝔫′_d] = 0;
  - (iii) the subalgebra generated by 𝔫′_d is 𝔫′_d ⊕ Z, with Z = [𝔫′_d, 𝔫′_d] ⊆ 𝔤₀ central in it;
  - (iv) θ_d is an automorphism of 𝔫 whose −1 part has an abelian Lie triple system.
- **Not a collapse of the action.** The C_d action need not factor through C₂. For example, a one-dimensional abelian algebra over
  F₇ with an order-3 scalar action satisfies (P2) and (P3), and its action still has order 3. Only the bracket structure behaves as
  for an involution. (The predecessor's title, "collapse to an involution", is corrected here.)

**Lemma 2.2 (divisors).** The criterion at d implies the criterion at every divisor of d.

**Lemma 2.3 (only near triples).** Under (P2_d), [[𝔤_α, 𝔤_{−α}], 𝔤_β] = 0 whenever β ≢ ±α. So under (P2_d), the criterion fails iff
some near triple [[𝔤_a, 𝔤_{−a}], 𝔤_{±a}] is nonzero.

**Lemma 2.4 (parity).** Under (P2_d), a nonzero Lie monomial in odd elements has even character iff its degree is even.

### 2.2 The polynomial side

**Theorem A.**
- **Hypotheses.** π is a group with H¹(π; F_p) = H²(π; F_p) = 0, and ψ: π → C_r has image of order d, with the criterion holding at
  d. No grading is assumed.
- **The count.**

  |Hom_ψ(π, G)| = Π_{α ≢ 0 (d)} |Z¹(π; F_p^{αψ})|^{dim 𝔤_α}.

- **Rigidity.** Every homomorphism lands in exp(𝔫′_d ⊕ Z) ⋊ C_d.
- **Without the criterion** the right side is still an upper bound.
- **Corollary.** If the criterion holds at D(M) for every M in a class of manifolds with boundedly many sectors, counting is
  polynomial on that class. The terms are twisted Fox matrices over F_p.

### 2.3 The hard side

In each case the input is a knot diagram K, and the output is the count for a fixed surgery on K. Reductions are polynomial-time
Turing reductions, and each is a reduction **for each fixed group G**: its anchor graph and constants depend on G.

**Theorem B1 (class 2).** Let 𝔫 have class 2, so G is of class (K), and let (P2_d) fail for some d | r. Then counting
|Hom(π₁ S³_d(K), G)| is #P-hard.
- Every map from π₁ S³_d(K) (H₁ = Z/d) to G lands in G_d = N ⋊ C_d.
- Also, for G itself with d = r, counting on knot groups π₁(S³ ∖ K) is #P-hard.

**Theorem B2 (triples under the pair condition).** Let 𝔫 be graded of class ≤ 4, p ≥ 5, and d | r with (P2_d) holding and (P3_d)
failing. Then counting |Hom(π₁ S³_{d/p}(K), G)| is #P-hard.
- For d = 2 (`TRIPLE-SYSTEM-20261027-001C`), the 2-surgeries S³₂(K) are also used.
- The proof for every d is `COPRIME-PAIRS-20261027-001A` (successor of `COPRIME-DICHOTOMY-20261027-001C`).

**Theorem B3 (the cross-layer pair).** Let 𝔫_× be the free class-3 algebra on x (trivial character) and y (character α), with α ≠ 1
and α² ≠ 1. Counting |Hom(π₁ S³_r(K), N_× ⋊ C_r)| is #P-hard, although the class-2 quotient is polynomial.

### 2.4 The dichotomy

**Corollary C.**
- **Scope.** Fix a divisor-closed set 𝒟 of divisors of r. Consider closed oriented M with H₁(M; F_p) = 0, boundedly many sectors,
  and sector orders in 𝒟. For example, |H₁(M)| ≤ C gives 𝒟 = {d | r : d ≤ C}.
- **Statement.** For graded 𝔫 of class ≤ 4 and p ≥ 5:
  - polynomial if the criterion holds at every d ∈ 𝒟;
  - #P-hard if it fails at some d ∈ 𝒟 where (P2_d) holds, or 𝔫 has class 2.
- **Open.** The only undecided algebras are those of class 3 or 4 whose criterion fails, at every failing d ∈ 𝒟, through (P2_d).
  Theorem B3 is one such algebra that is known to be hard.
- **A remark on divisors.** (P2_2) holds for every algebra, since 1 + 1 ≡ 0. So if 2 ∈ 𝒟, the criterion at 2 must hold for an
  algebra to be in the open family. For example, the free class-3 algebra on two generators of one odd character a fails (P3_2):
  [[y₁, y₂], y₁] ≠ 0 with all three factors odd mod 2. So its counting is #P-hard whenever 2 ∈ 𝒟, by Theorem B2 at d = 2.

## 3. Proofs of the structural lemmas

**Lemma 2.1.**
- **θ_d.** It respects [𝔤₀, ·] in any case, and respects [𝔤_α, 𝔤_β] for α, β ≠ 0 iff these lie in 𝔤₀, which is (P2_d). It commutes
  with σ, which acts on each 𝔤_α by scalars.
- **(i) ⇒ (ii).** By (P2_d), [𝔫′, 𝔫′] = Σ_α [𝔤_α, 𝔤_{−α}] ⊆ 𝔤₀. By (P3_d) its bracket with 𝔫′ vanishes.
- **(ii) ⇒ (i).** For α, β and α + β all nonzero, [𝔤_α, 𝔤_β] ⊆ 𝔤₀ ∩ 𝔤_{α+β} = 0.
- **(ii) ⇒ (iii).** Left-normed words of length ≥ 3 in 𝔫′ vanish, and Jacobi gives [[a, b], z] = 0 for z ∈ Z.
- **(iii) ⇒ (ii)** is immediate.
- **(iv).** Given (P2_d), the triple system of the −1 part is [[𝔫′, 𝔫′], 𝔫′] (Jacobson [Ja]; Loos [Lo]).
- **The example.** In dimension one every bracket vanishes, so (P2) and (P3) hold for any scalar action. ∎

**Lemma 2.2.** Lifts of nonzero classes mod d′ are nonzero mod d.
- (P2_d) kills [𝔤_α, 𝔤_β] for lifts of a failing pair mod d′.
- For a triple, take lifts α and γ of α′ and −α′:
  - if α + γ ≢ 0 mod d, the inner bracket vanishes by (P2_d);
  - otherwise γ = −α, and (P3_d) applies. ∎

**Lemma 2.3.** [[x, y], w] = [x, [y, w]] − [y, [x, w]], and both brackets vanish by (P2_d) when β ≢ ±α. ∎

**Lemma 2.4.** Induct on [P, Q].
- If both have odd degree, their nonzero characters sum to 0 by (P2_d).
- Otherwise a zero character is added. ∎

## 4. Proof of Theorem A

Write Z¹_α = Z¹(π; F_p^{αψ}). H¹(π; F_p) = 0 gives Z¹_0 = Hom(π, F_p) = 0.

- **Lower bound.**
  - H = exp(𝔫′ ⊕ Z) ⋊ C_d is a subgroup, and exp(Z) is central and fixed.
  - H/exp(Z) = 𝔫′ ⋊ C_d is a vector group. Its homomorphisms over ψ are ⊕_{α≢0} Z¹_α ⊗ 𝔤_α.
  - Each lifts uniquely through the central extension: the obstruction lies in H²(π; F_p) ⊗ Z = 0, and lifts form a torsor under
    Hom(π, Z) = 0.
- **Upper bound.**
  - Along the C_r-stable lower central series, the fibres of successive lifting maps are empty or torsors under
    Z¹(π; γ_k/γ_{k+1}), with π acting through ψ.
  - Splitting by characters, and using Σ_k dim (γ_k/γ_{k+1})_α = dim 𝔤_α (Lazard is equivariant), gives the same product.
- **Conclusion.** The bounds agree.
- **The corollary.** The sector ψ = 0 contributes the trivial homomorphism alone. Each other sector is given by the formula, at
  order dividing D(M), where Lemma 2.2 applies. ∎

**Remark.** At r = 2 this is `TRIPLE-SYSTEM-20261027-001A`. In class 2 it is the polynomial side of the class-(K) dichotomy, whose
algorithm (`COPRIME-CLASS2-20261026-001C`) was proved separately. Theorem A needs neither a grading nor a class bound beyond c < p.
The review confirmed the lower and upper bounds and the divisor argument.

## 5. Tools common to the hard side

### 5.1 Sector isolation (Lemma I)

**Lemma I** (`CLASSK-DICHOTOMY-20261026-001C` §3).
- **Hypotheses.** f₁, …, f_N are non-negative rational functions on loopless multigraphs. Each is multiplicative under disjoint
  union with f_i(∅) = 1, and f₁ > 0. Let h = Σ c_i f_i with c_i > 0, and I = {i : f_i = f₁}.
- **Conclusion.** There is a fixed multigraph F such that (Σ_{i∈I} c_i) f₁(Γ) is computed from h(Γ ⊔ F^{⊔j}), j = 0, …, R − 1,
  by one Vandermonde solve.
- **Proof idea.**
  - For each i ∉ I there is a witness F_i with f_i(F_i) ≠ f₁(F_i).
  - F = ⊔_i F_i^{⊔ a_i}: each unwanted equality f_i(F) = f₁(F) is a proper hyperplane in the multiplicities a, and finitely many
    hyperplanes miss a large grid.
- **Per fixed group.** F, R and the constants depend on G. The result is a reduction for each fixed G, not a uniform algorithm with
  G as input.

### 5.2 Bulatov–Grohe

Bulatov and Grohe [BG] classify EVAL(A) for symmetric non-negative matrices: #P-hard unless every connected component is rank one,
or bipartite of the corresponding rank-one form. Cai, Chen and Lu [CCL, Theorem 2.1 and Corollary 2.1] state it so, with the
hardness side for input multigraphs. All uses below present the hard partition function as Z_W(Γ) = Z_f(Γ^{(2)}), with W = f²
entrywise; edge doubling avoids any need for f ≥ 0. A positive diagonal entry W(0, 0) makes the component of 0 non-bipartite.

## 6. Proof of Theorem B2 (triples under the pair condition)

This section is the uniform proof for every sector order d. The case d = 2 is the earlier proof with t = −1. Full details,
including every lemma below with its proof, are in `COPRIME-PAIRS-20261027-001A`. Notation: τ ∈ C_r has order d, and the character
α of C_d acts by ζ_d^α. A character value t ∈ F_p^× also denotes the local system F^t (meridian ↦ t).

### 6.1 Pinning at slope d/p

**Lemma 6.1.** For M = S³_{d/p}(K),

  |Hom(π₁M, G)| = Σ_{e ∈ (r/d)Z/rZ} p^{dim 𝔫 − dim 𝔫^{σ^e}} P_{σ^e}(K),  P_υ(K) = #{ρ: π_K → G : ρ(μ) = υ}.

*Proof.*
- ρ(λ) ∈ N has order dividing p, so the relator μ^d λ^p imposes only ρ(μ)^d = 1.
- By Schur–Zassenhaus [Go, Thm 6.2.1], elements of order dividing d in Nσ^e are the N-conjugates of σ^e, and
  C_N(σ^e) = exp(𝔫^{σ^e}). ∎

**Lemma 6.2.**
- P_υ(K₁ # K₂) = P_υ(K₁) P_υ(K₂), because π_{K₁#K₂} = π_{K₁} ∗_{⟨μ⟩} π_{K₂}.
- P_υ(unknot) = 1 and P_υ(K) ≥ 1.

**Consequence: no channels.** Cross-summand "channel terms", which carry the trivial-character layer through the shared meridian
at slope d/1, do not occur at slope d/p.
- Measured: at slope d/1 the exact counts on K # K differ from the squares (1929 against 61² at p = 5; 7489 against 127² at
  p = 7). At slope d/p they equal the squares (`COPRIME-DICHOTOMY-20261027-001B-E002`, R1).
- Independently: 93,025 = 305² for 6₁ # 6₁ at p = 5, d = 4 (Codex review).

### 6.2 The pinned layered count; Fox normalization; Squier duality; the corrected Artin identity

**The layered count.**
- Pinned lifts through γ_k/γ_{k+1} form torsors under the relative cocycles {c : c(μ) = 0}. These are ≅ H¹(X; F^t) at nontrivial
  characters and 0 at the trivial character.
- Obstructions lie in H²(X; F^t) ≅ H¹(X; F^{t⁻¹})^*, and H²(X, μ; F_p) = 0. So

  P_τ(K) = #{ξ ∈ ⊕_{k, α≢0} V_α ⊗ L_{k,α} : o(ξ) = 0},  V_α = H¹(X; F^{ζ_d^α}).

**Fox colours** (free differential calculus [Fo]). In a closed braid β on n strands, colours propagate by:
- g > 0: (s_i, s_{i+1}) ↦ ((1 − t⁻¹)s_i + t⁻¹s_{i+1}, s_i);
- g < 0: (s_i, s_{i+1}) ↦ (s_{i+1}, t s_i + (1 − t)s_{i+1}).

Bur_t(β) is their product. Cocycles are its fixed vectors; coboundaries are the constant vectors 𝟙.

**Lemma 6.2.0 (Fox normalization; corrected).** For the closure relators R_q = x_q⁻¹ β(x)_q, the literal Fox matrix under the
left convention is t⁻¹(Bur_t(β) − I), not I − Bur_t(β) as the predecessor stated.
- Indeed c(R_q) = c(x_q⁻¹) + t⁻¹ c(β(x)_q) = t⁻¹(c(β(x)_q) − c(x_q)).
- The two differ by the invertible scalar −t⁻¹, so they have the same column space and left kernel. The obstruction test (o lies
  in the column space) and the steering computation, which uses the actual relator values, are unchanged; so is κ_t below.
- Checked on 240 characters of random braids (`COPRIME-PAIRS-20261027-001A` check 1); the review's literal-matrix computation
  agrees with κ_t.

**Lemma 6.3 (Squier form [Sq]).** J_t, lower unitriangular with (J_t)_{qq′} = (t − 1)t^{q−q′−1} for q > q′, satisfies
Bur_{t⁻¹}(g)^T J_t Bur_t(g) = J_t for every letter. At t = −1 it is the form J of `BEYOND-CLASS2-20261027-001C`. Further:
- J_t^T 𝟙 = (t^{n−1−q})_q;
- if t^d = 1 ≠ t, then Σ_{i<d} (J_t^T s)_{o+i} = Σ_{i<d} t^i s_{o+i}.

The invariance is a local two-row identity, checked symbolically in Z[t, t⁻¹] for n ≤ 7 and mod p for n ≤ 12; Squier's theorem is
therefore not load-bearing.

**Lemma 6.4 (left kernel).** A central obstruction vector o at character t lies in the column space iff ⟨o, J_t^T s⟩ = 0 for all
s ∈ Fix Bur_{t⁻¹}(β). Moreover ⟨o, J_t^T 𝟙⟩ = 0 always.

*Proof.*
- **Left-kernel vectors.** J_t^T s are left-kernel vectors by Lemma 6.3.
- **Dimensions.** dim H¹(X; F^t) = dim H²(X; F^t) = dim H¹(X; F^{t⁻¹}), by the Euler characteristic and duality with local
  coefficients ([Wa, Ch. 2]; [Ha, §3.H]). So these vectors fill the kernel.
- **The coboundary vector.** A positive letter maps (a, b) ↦ (a⁻¹ba, a) and preserves the **reverse** product ba (Artin [Ar];
  [Bi, Ch. 1]). So β(x)_{n−1} ⋯ β(x)₀ = x_{n−1} ⋯ x₀.
  - With P_j = x_{n−1} ⋯ x_j this gives the identity among relations Π_{j = n−1, …, 0} P_j R_j P_j⁻¹ = 1.
  - Its coefficient vector (t^{n−j})_j = t · J_t^T 𝟙 annihilates every central obstruction vector. ∎

**Correction (erratum to `BEYOND-CLASS2-20261027-001C` Lemma 2.2(iii)).**
- That proof wrote Artin's identity with the forward product β(x)₀ ⋯ β(x)_{n−1} = x₀ ⋯ x_{n−1} and the conjugators x₀ ⋯ x_q.
  Under the stated action the forward product is not preserved: (a, b) ↦ (a⁻¹ba, a) sends ab to a⁻¹ba².
- The correct identity is the reversed one above. At t = −1 its coefficients are (−1)^{n−j} = −J^T 𝟙, the vector the proof needs.
  The count, the steering formula and every downstream statement are unchanged.
- The reversed identity holds on 60 of 60 random braids and the forward one fails on 57.

**The Fourier form.** Q(ξ; s) = Σ ⟨o_{k,α}(ξ), J^T s_{k,α}⟩, extended polynomially. Then

  P_τ(K) = p^{−D} Σ_{ξ, s} ω^{Q(ξ; s)}.

### 6.3 Summands without local forms

Every summand of a connected sum carries classes at t₀ and t₀⁻¹ together, because dim V_t = dim V_{t⁻¹}. For d ≥ 3 these are
distinct characters, and their local Massey products can obstruct.
- **Measured.** Twist knots and other chiral knots obstruct; 12 of 12 measured cases have lift fractions 0.125–0.5 (E002, R2). The
  review's 6₁ count (61 of 125 class data lift) is an independent chiral control.
- **The remedy.** Use summands whose local forms vanish. The constructions, by the order of t₀:

**Canonical pinned coordinates (Lemma 6.5.0).** Let K be a knot, τ of order d, (P2_d), class ≤ 4. Write a pinned homomorphism as
ρ(g) = exp(Σ_k v_k(g)) τ^{ψ(g)}, with v_k(g) ∈ L_k.
- (a) v₁ is odd and is a pinned cocycle: its even part is a pinned trivial-character cocycle, hence 0.
- (b) The odd part v₂^odd is a pinned cocycle, because the odd part of D₂ = −½[v₁ ⌣ v₁] is a sum of [odd, odd] brackets, which
  are even. The even part v₂^ev is the unique pinned solution of δv₂^ev = D₂(v₁), since H¹(X, μ; F_p) = H²(X, μ; F_p) = 0.
- (c) v₃^ev is likewise unique. The odd part v₃^odd exists iff the layer-3 obstruction vanishes.
- (d) The odd layer-4 defect does not involve v₃^odd: v₃^odd enters layer 4 only through [v₁, v₃^odd], which is even (Lemma 2.4).

So the odd obstructions of layers 3 and 4 are well-defined polynomial functions of ξ = (v₁, v₂^odd). Every automorphism φ of π_K
with φ(μ) = μ acts on ξ by precomposition, linearly, and ob(ξ ∘ φ) = φ^* ob(ξ): uniqueness makes the even parts natural. On knot
models, the odd layer-2 residuals vanish identically and the odd layer-4 residuals do not change when the odd layer-3 cocycles do,
while the even ones move (`COPRIME-PAIRS-20261027-001A` check 3).

**(a) Order 2: T(2, p).** This is (b) with k = 1.

**(b) Even order 2k: the (k,1)-cable C_k of T(2, p).** The braid is the k-cable of σ₁^p followed by δ_k^{1−kp} on the first bundle,
with δ_k = σ₁ ⋯ σ_{k−1}.
- **Spectrum.** For t^k = −1, Bur_t(δ_k) acts on F^k/𝟙 as t⁻¹C, with C the k-cycle on the augmentation quotient. Its eigenvalues
  are t⁻¹ω, ω running over the nontrivial k-th roots of unity, never 1.
- **Colourings (new).** Fix Bur_t(C_k) = {(a𝟙, b𝟙)}, the colourings constant on each bundle, at every t with t^k = −1.
  - A positive fat crossing conjugates the under-bundle by the over-bundle's product Y, with χ(Y) = t^k = −1. So
    c(Y⁻¹zY) = −c(z) + (1 − t)c(Y): patterns (colours modulo constants) transform by (P_L, P_R) ↦ (−P_R, P_L).
  - A fixed pattern would need D̄P_L = −P_L, where D̄ = (t⁻¹C)^{1−kp} has eigenvalues −t⁻¹ω. That is impossible.
  - Constant bundles transform by (a, b) ↦ (2a − b, a), a unipotent matrix whose p-th power is the identity mod p.
  - So dim H¹(X_C; F^t) = 1, and the class is the bundle jump b − a, the same pattern at every such t. Elsewhere,
    Δ_{C_k}(t) = Δ_{T(2,p)}(t^k) ≡ (t^k + 1)^{p−1} (Seifert [Se]; [Li, Ch. 6]) leaves only constants.
- **Acyclicity.** At t^k = −1 the companion torus and the cable space S (the mapping torus of the k-punctured disc with monodromy
  δ_k) are F^t-acyclic: for S, by the Wang sequence and the spectrum.
- **The homomorphism (corrected).** Let θ′ = τ^k, which acts by −1 on U = ⊕_{α∈R} 𝔤_α, R = {α : ζ_d^{αk} = −1}. Let u: π_T → Z be
  the integer abelianization and c a cocycle for the sign character g ↦ (−1)^{u(g)} with c(μ_T) = 0. Then

  ρ₀(g) = exp(c(g)A) θ′^{u(g)},  A ∈ U,

  is a homomorphism, since θ′^m(A) = (−1)^m A for every integer m.
  - The exponent must be the integer u(g). θ′ need not have order 2: for d = 12 and a character of order 4, k = 2 and θ′ has order 6,
    and a mod-2 exponent would not define a homomorphism. The predecessor's ψ(g) is replaced.
  - ρ₀(μ_T) = θ′ and ρ₀(λ_T) = 1, because λ_T ∈ π″ and c is a homomorphism on the kernel of the sign.
- **Gluing.** ρ_S(a_i) = τ and ρ_S(c) = 1 satisfy the cable-space relations and agree with ρ₀ on the boundary torus (μ_T ↦ τ^k,
  λ_T ↦ 1). Restriction H¹(X_C; F^t) → H¹(X_T; F^{−1}) is an isomorphism (Mayer–Vietoris), and varying the layer-ℓ part of A moves
  the layer-ℓ lift through its whole pinned torsor (`TRIPLE-SYSTEM-20261027-001C` §2). So every class datum at R is realized.
- **Scope.** This holds for **every** algebra, in every class < p, with no condition on brackets.
- **Checked.** The characteristic polynomials of Bur_t(δ_k) (258 cases), the fixed colourings at eight (p, k), the integer-exponent
  map on T(2, 13) with θ′ of order 6, and lifting on eight (p, d, k) and four algebras including a pair-failing one.

**(c) Odd order ≥ 3: a negative amphichiral two-bridge knot.**
- t₀ is then a square and t₀ ≠ t₀⁻¹. K_m = b(4m² + 1, 2m) has Δ = −m²(t + t⁻¹) + 2m² + 1. With m ≡ ±√t₀/(t₀ − 1) its roots are
  exactly t₀^{±1}, simple, and Δ(−1) = (t₀ + 1)²/(t₀ − 1)² ≠ 0.
- It is negative amphichiral: (2m)² ≡ −1 (mod 4m² + 1); the mirror of b(α, β) is b(α, −β); and two-bridge knots are invertible
  (Schubert [Sch]; [BZ, Ch. 12]).
- **Lemma 6.5.** Under (P2_d) and class ≤ 4, such a summand is unobstructed.
- *Proof.*
  - **The u-pairing** P(c₊, c₋) = ⟨u ⌣ c₊ ⌣ c₋, [X, ∂X]⟩ is perfect at a simple root, with c₋ read in
    H¹(X, ∂X; F^{t₀⁻¹}) ≅ H¹(X; F^{t₀⁻¹}).
    - V_± are one-dimensional: H¹(X; M) ≅ Hom_Λ(A, M) over Λ = F_p[t^{±1}] when t − 1 acts invertibly on M ([Le]; [Hi]).
    - u ⌣ (−) is, up to a nonzero scalar, the connecting map of 0 → F^{t₀} → E → F^{t₀} → 0 with E = Λ/(t − t₀)². The comparison
      map Hom_Λ(Λ/(t − t₀), E) → Hom_Λ(Λ/(t − t₀), E/(t − t₀)E) is zero, because the (t − t₀)-torsion of E is (t − t₀)E. So
      the connecting map is injective, and P is perfect by duality.
  - **The sign.** Let h be the amphichiral homeomorphism, with h_*(μ) = gμg⁻¹, and φ = c_{g⁻¹} ∘ h_*. Then φ(μ) = μ, φ^* acts on
    V_± by scalars ε_±, inner automorphisms act trivially on products of trivial total character, φ^*u = u, and h reverses
    [X, ∂X]. So ε₊ε₋ = −1.
  - **Balance.** By Lemma 6.5.0, L(ξ, s) = ⟨ob_k(ξ) ⌣ s, [X, ∂X]⟩ (k = 3, 4) is a polynomial in the canonical coordinates, linear
    in the dual s, with L(ξ ∘ φ, φ^* s) = −L(ξ, s). Each monomial at character a has three data factors with characters summing to
    a. By (P2_d) and Lemma 2.4, a nonzero Lie part needs two factors from V₊ and one from V₋; the shapes (3, 0) and (0, 3) need
    [𝔤_{±a}, 𝔤_{±a}] ≠ 0, excluded since 2a ≢ 0. The canonical even parts obey the same count. With the dual, every monomial uses
    V₊ twice and V₋ twice.
  - So L(ξ ∘ φ, φ^* s) = (ε₊ε₋)² L(ξ, s) = L(ξ, s), hence L = 0, and ob_k = 0 by perfect duality. ∎
- **Why not one construction.** Simple roots of strongly negative amphichiral knots are squares (Hartley–Kawauchi [HK]). Every
  non-square has even order, where (b) applies.
- **Measured.** E002 R2: 66 amphichiral rows and 56 cable rows never obstruct. The cable rows include a pair-failing algebra.

### 6.4 Steering at a character of order d

- **The insertion.** Insert cable_d(P4, o): each of the four strands of P4 = [[A₁₂, A₂₃], A₃₄] is replaced by a bundle of d
  strands.
- **Bundle values.** Let Y_j = z_{o+dj+d−1} ⋯ z_{o+dj} be the reverse-order product of the bundle's labels. It lies in N, because d
  labels from Nτ multiply to Nτ^d = N.
- **Leaves.** ℓ_j = Σ_i t^{d−1−i} c(z_{o+dj+i}) at character t. It vanishes on coboundaries.

**Proposition 6.6 (the steering rule).** Under (P2_d) and class ≤ 4, on data where the lower obstructions vanish, the odd
obstructions of layers 3 and 4 change by

  ΔQ(ξ; s) = Σ_t κ_t Σ_j ⟨W_j⁽³⁾(ℓ(ξ))_t, ℓ_j(s_t)⟩,  κ_t = t⁻² − t⁻¹.

W_j⁽³⁾ is the Dynkin degree-3 Lie part of the conjugator of strand j ([Re, Thm 1.4]; [MKS, Ch. 5]), evaluated on the odd layer-1
and layer-2 leaves; W₀⁽³⁾ = −[X₁, [X₂, X₃]]. At t = −1, κ_t = 2, as before.

*Proof outline.*
- **The cable** conjugates bundle j by W_j(Y). This is checked in the free group for d = 2, …, 6.
- **The conjugator.** The odd part of log ρ(W_j(Y)) is W_j⁽³⁾ on the odd leaves: degree-4 terms and in-bundle brackets are even
  (Lemma 2.4).
- **The shift.** Conjugating a label nτ by e^Λ shifts its t-part by −(1 − t⁻¹)Λ_t.
- **Transport and pairing.** The shift is transported by Bur_t, and the closure rows change by o′ − o = −Bur_t(β[ℓ:])Δ. This uses
  the actual relator values, whatever scalar normalizes the Fox matrix (Lemma 6.2.0). Pairing with J_t^T s and the bundle identity
  give the factor −(1 − t⁻¹)t⁻¹.
- **Even corrections.** All corrections are even, and pinned even parts are rigid. ∎

**Measured** (E002, R3 and R4): exact equality on 48 single insertions and 10 gadgets at d = 3, 4, 5, 6.
- This includes layer-4 obstructions through free layer-2 classes, on amphichiral and cable bases.
- The controls fail as required: κ = 2 in place of κ_t, forward-order bundles, and a twist-knot base.
- **Independent** (Codex review): 80 literal-matrix comparisons at orders 3–6 on class-3 matrix targets, 78 nonzero; the constant 2
  is rejected in all 48 nonzero cases where it differs from κ_t.

### 6.5 The gadget, the reading strands, the edge weight, and the conclusion

Fix a near triple at a (Lemma 2.3), t₀ = ζ_d^a, and a summand type S of §6.3 with root characters R ∋ ±a.

**Lemma 6.7 (reading strands; new).** Each summand type has a closed-braid representative whose first and last strands receive
different colours under the class at every α ∈ R.
- **Cables.** The braid of §6.3(b) as it stands: its first strand lies in bundle 1 and its last in bundle 2, whose colours differ by
  the bundle jump b − a ≠ 0 at every t with t^k = −1.
- **Amphichiral summands** (R = {t₀^{±1}}). Take any closed braid of K_m.
  - The class colourings at t₀ and t₀⁻¹ are non-constant, so each partitions the strands into at least two colour classes.
  - **Two-partition lemma.** Two partitions of a set, each with at least two blocks, admit a pair of points in different blocks of
    both. (If x, y are in different blocks of the first partition, they share a block of the second. A point z outside that block
    shares the first-partition block of both x and y, a contradiction.)
  - So some strands q′, q have colours differing at both characters. Let η move q′ to position 0 and q to position n − 1, each as
    an over-strand, so their colours are preserved. Then η⁻¹βη has the same closure, its colourings are Bur(η) applied to those of
    β, and its first and last strands carry the colours of q′ and q.
- **Checked.** The two-partition lemma exhaustively for n ≤ 6; 120 random conjugates of five amphichiral braids, 10 of which had
  unseparated first and last strands, all separated after the conjugation; a gadget built on such a conjugated figure-eight
  representative replicates the steering rule.

**The gadget for a loopless multigraph Γ.**
- **Base.** A connected sum of: for each vertex, S followed by d − 2 unknot blocks; for each edge and k = 1, 2, 3, d − 1 unknot
  blocks followed by S. Each summand copy's reading strand is its last strand.
- **Unknot blocks** add no class and copy the colour of the strand before them, at every character.
- **Insertions.** For each edge (u, v), the strands (r_u, d − 2 copies of u's colour, r_v) and three private bundles (d − 1 copies,
  r_{e,k}) are moved as over-strands to adjacent positions. Then cable_d(P4) is inserted and the move undone. The insertions do not
  change H¹: the bundle products have trivial character, so commutator conjugators act trivially on Fox colours.

**Lemma 6.8 (basis; new).** At each α ∈ R, V_α of the base is the direct sum of one line per summand copy, and the functionals
X_v = c(r_v) − c(strand 0) and z_{e,k} = c(r_{e,k}) − c(the strand before its unknot run) form a basis of V_α^*.
- A class of the copy in block j colours the strands before block j constantly, block j by its class colouring, and every later
  strand by the constant shifted by the block's jump J_j, nonzero by Lemma 6.7.
- X_v takes the value J_j on every vertex copy up to and including v's, and 0 on private copies. z_{e,k} takes J_j on its own copy
  only. The matrix is triangular with diagonal J_j ≠ 0.

**The form.** Because Σ_i t^{d−1−i} = 0, the leaves are exactly X_v − X_u and the private coordinates z_{e,k} at every character.
So Q = Σ_e T(X_v − X_u, z_{e,1}, z_{e,2}, z_{e,3}), where T uses each leaf once (the P4 tensor).

**The edge weight** (with the actual coefficients κ_t). f(σ) = Σ_π ω^{T(σ, π)}, with σ = (data, dual) ∈ U ⊕ U′.
- f is integer, real and even, and f(0) is its maximum: rescaling one private leaf (data and dual together) by λ ≠ 0 multiplies T
  by λ.
- At σ = (0, s*) only the j = 0 term survives: T = −κ_{t*}⟨[π₁, [π₂, π₃]], s*⟩. So f(0, s*) counts the zeros of a trilinear form,
  and the nonzero constant κ_{t*} does not change the zero set. With s* detecting the near triple, 0 < f(0, s*) < f(0).
- **Corrected.** The predecessor of the proof (`COPRIME-DICHOTOMY-20261027-001C`, Lemma 7.1) also asserted that f does not depend
  on the κ_t. Rescaling private duals does not prove that, because the j = 0 term contains the fixed vertex dual. The valid
  statement is the relabeling f_κ(A, S) = f₁(A, KS), with K rescaling every dual character component; but no form of independence
  is needed, and none is used.
- **Checked.** Exact counts at six (p, d, algebra) cases; at (7, 3) a direct exponential sum including κ_{t*} = 2 equals the count
  times |U|.

**The conclusion.**
- P_τ(K_Γ) = λ^n μ^m Z_f(Γ).
- The closed count is Σ_e c_e P_{σ^e}(K_Γ), multiplicative in Γ (with K_{Γ⊔Γ′} = K_Γ # K_{Γ′}). Lemma I isolates the sector of τ.
- W = f² has the minor f(0)⁴ − f(0, s*)⁴ ≠ 0 and W(0, 0) > 0, so Bulatov–Grohe applies. ∎

## 7. Proof of Theorem B1 (class 2, the class-(K) route)

This is `CLASSK-DICHOTOMY-20261026-001A` and C, built on `COPRIME-CLASS2-20261026-001B` and D. The logical chain:

1. **Layered count** (`COPRIME-CLASS2-20261026-001B` Theorem 1).
   - The obstruction is a twisted cup product.
   - Duality turns it into a trilinear form T on V_{χ} × V_{χ′} × V_{(χχ′)⁻¹}, with each component determined by κ_{χ,χ′}.
2. **Steering by Y-graphs** (`COPRIME-CLASS2-20261026-001B` (c), (d)).
   - Y-surgery with leaves in ker ψ changes every eigen-component of the triple cup product by the alternating product of the leaf
     functionals. This is Massuyeau's lemma ([Ma, Lemma 3.2]) in the r-fold cover.
   - Pure leaves (eigenprojected loops) realize prescribed components.
3. **Gadget manifolds** (`CLASSK-DICHOTOMY-20261026-001A`).
   - S³_r(K_Γ), with one twist knot K_{m(τ)} per coordinate. m(τ) ≡ τ(τ − 1)⁻², so its roots are exactly τ^{±1}.
   - One Y-graph per edge.
   - The count is Σ_k c_k λ_k^n μ_k^m Z_{W_k}(Γ), with W_1 positive, even, and of rank ≥ 2 exactly for a hard pair (three slot
     patterns).
4. **Realization** (`CLASSK-DICHOTOMY-20261026-001C` Lemma R). The gadgets are explicit knot diagrams, by Habiro's description of
   Y-surgery ([Hab]; [GGP]) and the constructions of `COPRIME-CLASS2-20261026-001D` §3.
5. **Lemma I and Bulatov–Grohe.**

**Knot groups.** The knot-exterior count adds one trivial-character coordinate. Splitting by its value gives multiplicative pieces,
and Lemma I applies again.

**Why class 2 needs no special summands.** Base triple products vanish on connected sums of twist knots at the class-(K) slot
patterns (CLASSK C, Lemma R). With cup products only, no layer above can feed a local Massey term.

**Corollary D of `CLASSK-DICHOTOMY-20261026-001C`** gives the refinement by allowed sector orders (G_d with d ≤ C), which is the
class-2 case of Corollary C here.

## 8. Proof of Theorem B3 (the cross-layer pair)

This is `BEYOND-CLASS2-20261027-001A`.
- The layered count gives

  |Hom_{ψ_k}(π₁M, G_×)| = |Z¹(π₁M; F_{α^k})| · |Hom_{ψ_k}(π₁M, H_{α,α} ⋊ C_r)|,

  where H_{α,α} is the Heisenberg group with both generators of character α.
- That group has a hard pair (α, α) when α² ≠ 1, so B1 applies.
- The class-2 quotient G_×/γ₃ = H_{1,α} ⋊ C_r has no hard pair.
- In the language of §2, the pair failure is (α, α) between layer 1 (y) and layer 2 ([x, y]).

## 9. Corrections and clarifications incorporated

From the predecessor presentation (unchanged in substance):

1. **Artin product order** (§6.2). The forward identity in `BEYOND-CLASS2-20261027-001C` Lemma 2.2(iii) is replaced by the reversed
   identity. The same vector, up to sign, results; nothing downstream changes.
2. **Sector count.** The polynomial algorithms need a bounded number of sectors: bounded 2-rank at r = 2, bounded r-torsion rank in
   general. Theorem A itself needs only H¹ = H² = 0 with F_p coefficients, and no grading.
3. **Lemma I is per fixed group.** The anchor and constants depend on G.
4. **Channel terms at r > 2.** They are removed by slope d/p (§6.1). Local Massey forms are removed by the summands of §6.3.
5. **Scope of B2 in classes 3 and 4.** It needs (P2_d). Pair failures in classes 3 and 4 are open (§14).
6. **Interpretation.** r counts action characters. The results are counting-complexity statements only (§0).
7. **Process.** The first frozen run of the r > 2 experiment (`COPRIME-DICHOTOMY-20261027-001B-E001`) crashed on a construction
   error before any verdict. It is kept as invalid, and E002 reran it with that single parameter corrected.

New, from the review of `COPRIME-DICHOTOMY-20261027-001`:

8. **Parity automorphism.** "The action collapses to an involution" is replaced by "(P2_d) supplies a compatible parity
   automorphism" (Lemma 2.1). The original action need not factor through C₂.
9. **Fox normalization.** The literal Fox matrix of the closure relators is t⁻¹(Bur_t − I), not I − Bur_t (Lemma 6.2.0). The column
   space, the obstruction test and κ_t are unchanged.
10. **The cable exponent.** The gluing homomorphism is exp(c(g)A) θ′^{u(g)} with the integer abelianization u (§6.3(b)). θ′ may
    have order greater than 2 (order 6 at d = 12, k = 2).
11. **The edge-weight lemma.** The unproved claim that f does not depend on the κ_t is withdrawn; the hardness proof uses the actual
    coefficients (§6.5).

Expansions requested by the review:

12. **Canonical pinned coordinates** (Lemma 6.5.0), on which the amphichiral symmetry acts linearly, with the naturality of the even
    parts and the independence of the odd layer-4 obstruction from the odd layer-3 data.
13. **Reading strands and the basis** (Lemmas 6.7 and 6.8): cable colourings are bundle constants; the two-partition lemma and an
    over-strand conjugation give amphichiral representatives; the cumulative coordinates are triangular.

Minor precision changes (`COPRIME-PAIRS-20261027-001A`):

14. t₀ = −1 is covered by C₁ = T(2, p); outside t^k = −1 the cable's twisted cohomology vanishes by the satellite formula; the
    u-pairing and the obstruction pairings are read in H³(X, ∂X; F_p).

## 10. References

Theorem numbers follow the cited editions; where a book's numbering could not be confirmed, the chapter is given.

**Group theory and Lie theory.**
- **[La]** M. Lazard, Sur les groupes nilpotents et les anneaux de Lie, Ann. Sci. ÉNS (3) 71 (1954) 101–190. (The Lazard
  correspondence; equivariance under automorphisms.)
- **[Kh]** E. I. Khukhro, p-Automorphisms of Finite p-Groups, LMS Lecture Note Ser. 246 (Cambridge 1998), Ch. 9–10.
- **[Go]** D. Gorenstein, Finite Groups (Harper & Row 1968), Theorem 6.2.1 (Schur–Zassenhaus). Maschke's theorem (coprime
  semisimplicity) is standard.
- **[Ja]** N. Jacobson, Lie and Jordan triple systems, Amer. J. Math. 71 (1949) 149–170.
- **[Lo]** O. Loos, Symmetric Spaces I (Benjamin 1969).
- **[Re]** C. Reutenauer, Free Lie Algebras (Oxford 1993), Theorem 1.4 (Dynkin–Specht–Wever).
- **[MKS]** W. Magnus, A. Karrass, D. Solitar, Combinatorial Group Theory (Interscience 1966), Ch. 5 (the Magnus expansion).

**Topology.**
- **[Ho]** H. Hopf, Fundamentalgruppe und zweite Bettische Gruppe, Comment. Math. Helv. 14 (1942) 257–309.
- **[Ha]** A. Hatcher, Algebraic Topology (Cambridge 2002), §3.H (local coefficients).
- **[Wa]** C. T. C. Wall, Surgery on Compact Manifolds, 2nd ed. (AMS 1999), Ch. 2 (Poincaré and Lefschetz duality with local
  coefficients).
- **[Fo]** R. H. Fox, Free differential calculus I, Ann. of Math. 57 (1953) 547–560.
- **[Ar]** E. Artin, Theory of braids, Ann. of Math. 48 (1947) 101–126.
- **[Bi]** J. Birman, Braids, Links, and Mapping Class Groups, Ann. of Math. Stud. 82 (Princeton 1974), Ch. 1.
- **[Sq]** C. C. Squier, The Burau representation is unitary, Proc. Amer. Math. Soc. 90 (1984) 199–202.
- **[Le]** J. Levine, Knot modules. I, Trans. Amer. Math. Soc. 229 (1977) 1–50.
- **[Hi]** J. Hillman, Algebraic Invariants of Links, 2nd ed. (World Scientific 2012), Ch. 2–3.
- **[Sch]** H. Schubert, Knoten mit zwei Brücken, Math. Z. 65 (1956) 133–170.
- **[BZ]** G. Burde, H. Zieschang, M. Heusener, Knots, 3rd ed., de Gruyter Stud. Math. 5 (2014), Ch. 12 (two-bridge knots).
- **[Se]** H. Seifert, On the homology invariants of knots, Quart. J. Math. Oxford (2) 1 (1950) 23–32 (satellite formula).
- **[Li]** W. B. R. Lickorish, An Introduction to Knot Theory, GTM 175 (Springer 1997), Ch. 6.
- **[HK]** R. Hartley, A. Kawauchi, Polynomials of amphicheiral knots, Math. Ann. 243 (1979) 63–70.

**Clasper theory** (the class-(K) route only).
- **[Hab]** K. Habiro, Claspers and finite type invariants of links, Geom. Topol. 4 (2000) 1–83.
- **[GGP]** S. Garoufalidis, M. Goussarov, M. Polyak, Calculus of clovers and finite type invariants of 3-manifolds, Geom. Topol. 5
  (2001) 75–108.
- **[Ma]** G. Massuyeau, Cohomology rings, Rochlin function, linking pairing and the Goussarov–Habiro theory of three-manifolds,
  Algebr. Geom. Topol. 3 (2003), Lemma 3.2 (as cited in `COPRIME-CLASS2-20261026-001B`).
- **[Mo]** D. Moussard, Equivariant triple intersections, Ann. Fac. Sci. Toulouse Math. (2017), Proposition 2.5 and Theorem 2.7.

**Complexity.**
- **[BG]** A. Bulatov, M. Grohe, The complexity of partition functions, Theoret. Comput. Sci. 348 (2005) 148–186.
- **[CCL]** J.-Y. Cai, X. Chen, P. Lu, Graph homomorphisms with complex values: a dichotomy theorem, SIAM J. Comput. 42 (2013)
  924–1029; arXiv:0903.4728. Theorem 2.1 and Corollary 2.1.
- Membership in #P of counting homomorphisms from a finitely presented group to a fixed finite group: a homomorphism is a tuple of
  generator images checked against the relators in polynomial time.

**Neighbouring results.**
- **[SW]** Samperton–Weiss, arXiv:2602.02885v2, Theorem 2.
- **[Ga]** Galindo, arXiv:2605.06984v2, Theorems 1.1–1.2.
- **[KS]** G. Kuperberg, E. Samperton, Computational complexity and 3-manifolds and zombies, Geom. Topol. 22 (2018), §5.3.
- **[Ro]** Rowell, Contemp. Math. 482 (2009); arXiv:0803.1258, §3.3.5, Conjecture 3.2.
- **[MS]** D. Matei, A. I. Suciu, Counting homomorphisms onto finite solvable groups, J. Algebra 286 (2005) 161–186.
- **[No]** Nosaka, arXiv:1808.08532, Theorem 3.1.

## 11. Literature comparison

- **Samperton–Weiss [SW].**
  - Class-2 nilpotent targets are polynomial when |H²(M; Z(G))| is bounded.
  - With bounded homology, nilpotent targets (r = 1) are trivially easy. The coprime action is what creates hardness here.
  - Our hard examples have unbounded twisted H², so they do not contradict their theorems.
- **Galindo [Ga].** A dichotomy for Turaev–Viro-type invariants and hardness for nonabelian targets, with unbounded homology. Our
  regime, bounded H₁ with coprime twisting, is different.
- **Kuperberg–Samperton [KS] and Rowell [Ro].** Solvable targets were left open; Rowell conjectured polynomial counting on link
  groups for solvable G. The class-(K) knot-group corollary contradicts that conjecture (Conjecture 3.2(b)) for every class-(K) group
  with a hard pair, unless every #P function is polynomial.
- **Moussard [Mo].** Equivariant triple intersections in the infinite cyclic cover, the closest precursor of the class-(K)
  steering.
- **Matei–Suciu [MS]; Nosaka [No].** Twisted lifting obstructions; triple cup products of cyclic branched covers.
- **Hartley–Kawauchi [HK].** Used only to explain why amphichiral summands reach square roots only.
- **Searches.** The searches in these epics were bounded and found no statement of these dichotomies. That is not an exhaustive
  novelty check. The review rechecked the Samperton–Weiss and Galindo boundaries in the primary sources.

## 12. Finite validation (separate from the proofs)

Finite checks support but do not discharge uniform claims.

| artifact | what it checks | independence |
| --- | --- | --- |
| `COPRIME-CLASS2-20261026-001B`, `-C`, `-D` checks | Y-steering, Potts gadgets, twist-knot roots | producer |
| `CLASSK-DICHOTOMY-20261026-001B` (experiment) | 108 group-fixture comparisons, all sectors, closed and knot exterior | producer, frozen contract |
| `BEYOND-CLASS2-20261027-001B` (experiment) | base, steering κ = 2, gadgets, two models, group-law counts | producer, frozen contract |
| `TRIPLE-SYSTEM-20261027-001B` (experiment) | class-4 steering on six algebras | producer, frozen contract |
| Codex reviews of BEYOND-CLASS2 and TRIPLE-SYSTEM | independent 4×4 and 6×6 matrix models; 168 and 216 cases; noncentral class-4 corrections | independent AI review (V2) |
| `COPRIME-DICHOTOMY-20261027-001A` check | Lemma 2.1 on 24 algebras; group-law counts at r = 3, 6; class-4 lifting | producer |
| `COPRIME-DICHOTOMY-20261027-001B-E002` | pinning (exact counts), local forms (134 rows), steering at d = 3–6 (48 insertions, 10 gadgets) | producer, frozen contract |
| `COPRIME-DICHOTOMY-20261027-001C` check | Squier form in Z[t^{±1}], reversed Artin identity, summand lemmas, cable lemma, exact edge-weight counts | producer |
| Codex review of COPRIME-DICHOTOMY | 80 literal-matrix comparisons of κ_t at orders 3–6; counts 305 and 305² on 6₁ and 6₁ # 6₁ | independent AI review (V2) |
| `COPRIME-PAIRS-20261027-001A` check | Fox normalization; canonical coordinates on knot models; cable colourings, spectra and the integer-exponent map; reading strands; κ in the edge weight; gadgets with a conjugated representative | producer |

## 13. Uniform proof obligations (for reviewers)

These are the steps that finite checks do not cover. A reviewer should verify them by hand.

1. **Theorem A.** The lower and upper bounds (§4); the equivariant identification of the lower-central-series quotients.
2. **Lemma 6.1.** Slope d/p, Schur–Zassenhaus, centralizer sizes.
3. **Lemma 6.4.** The dimension count, and the identity-among-relations argument with the reversed product.
4. **Lemmas 6.5.0 and 6.5.**
   - The canonical coordinates and the naturality of the even parts.
   - Perfectness of the u-pairing at simple roots (the Bockstein argument).
   - The sign relation ε₊ε₋ = −1.
   - The (2,2)-balance of every obstruction monomial under (P2_d) in class ≤ 4.
5. **§6.3(b).**
   - The fixed colourings of C_k (fat crossings and the spectrum of δ_k).
   - Acyclicity of the cable space at t^k = −1.
   - The gluing of the integer-exponent homomorphism.
   - That the one-parameter family covers every layer's pinned torsor.
6. **Proposition 6.6.** That every correction term is even. This is the class-4 bookkeeping of `TRIPLE-SYSTEM-20261027-001C` §3 with
   characters, using Lemma 2.4.
7. **§6.5.**
   - Lemmas 6.7 and 6.8 (reading strands, basis).
   - The exactness of the leaves (the unknot-block colour copies).
   - Edge-weight integrality and realness; the count at (0, s*).
8. **Lemma I and the Bulatov–Grohe hypotheses** as applied (block-rank-1 and multigraphs).
9. **The class-(K) route.** The Y-graph realization (Lemma R) rests on cited topology that the reviews did not independently
   reconstruct.

## 14. Open problems

1. **Pair failures in classes 3 and 4** (the residual family of Corollary C). Under study in `COPRIME-PAIRS-20261027-001`.
   - Without (P2_d) there is no parity. Steering corrections can land at root characters, and edges that read a pair bracket also
     carry degree-3 and degree-4 terms.
   - Known special case: Theorem B3.
2. **Class ≥ 5.**
   - Lemma 6.5 kills (2,2)-balanced terms but not (3,3)-balanced ones.
   - Proposition 6.6 needs degree-5 conjugator parts.
   - Cable summands survive in every class.
3. Non-graded algebras whose associated graded criterion differs.
4. p = 2 and 3; manifolds with p-torsion in H₁; unboundedly many sectors.
5. **Knot exteriors at d ≥ 3** (beyond class (K)). The pinned count is the knot-group count with fixed meridian image of order d.
   A knot-exterior dichotomy needs the sectors where the meridian image has larger order; it has not been written.
6. Approximate counting, partly studied for UT₃ in the Rowell note.

## Appendix: artifact index

| ticket | artifact | role |
| --- | --- | --- |
| `COPRIME-CLASS2-20261026-001B` | P001 | Heisenberg layered count, Y-steering (Massuyeau) |
| `COPRIME-CLASS2-20261026-001C` | P001 | class-(K) polynomial side (bounded H₁) |
| `COPRIME-CLASS2-20261026-001D` | P001 | Heisenberg hardness, Potts gadgets, knot groups |
| `CLASSK-DICHOTOMY-20261026-001A` | P001 | sector partition functions on gadgets |
| `CLASSK-DICHOTOMY-20261026-001C` | P001 | class-(K) dichotomy, Lemma I, knot groups |
| `BEYOND-CLASS2-20261027-001A` | P001 | cross-layer pair (Theorem B3) |
| `BEYOND-CLASS2-20261027-001C` | P001 | U₄ at r = 2, J-duality (corrected here), steering κ = 2 |
| `TRIPLE-SYSTEM-20261027-001A` | P001 | Theorem A at r = 2 |
| `TRIPLE-SYSTEM-20261027-001C` | P001 | Theorem B2 at d = 2 |
| `COPRIME-DICHOTOMY-20261027-001A` | P001 | Theorem A at every r |
| `COPRIME-DICHOTOMY-20261027-001B` | E001 (invalid, crashed), E002 (supported) | pinning, local forms, steering at d ≥ 3 |
| `COPRIME-DICHOTOMY-20261027-001C` | P001 | Theorem B2 at every d (frozen; superseded for reading) |
| `COPRIME-DICHOTOMY-20261027-001D` | P001 | the predecessor presentation (frozen) |
| `COPRIME-PAIRS-20261027-001A` | P001 | Theorem B2 at every d, corrected and expanded |
