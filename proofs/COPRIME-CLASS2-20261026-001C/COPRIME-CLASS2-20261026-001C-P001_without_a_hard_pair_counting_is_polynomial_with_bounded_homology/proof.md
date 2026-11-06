# Without a hard pair, counting is polynomial with bounded homology

Status: Proved

## Standard statement

**Hypotheses (K).**
- **The group.** p is a prime, and G = N ⋊ C_r with p ∤ r. N is a finite p-group with a C_r-invariant subgroup A ≤ Z(N), and A and
  B = N/A are elementary abelian.
- **The cocycle.** N is described by a C_r-equivariant bilinear cocycle β: B × B → A, so that N ≅ A × B with
  (a, b)(a′, b′) = (a + a′ + β(b, b′), b + b′).
- **The commutator pairing** is κ(b, b′) = β(b, b′) − β(b′, b), equivariant and alternating.
- **Eigencomponents.** Over a splitting field F_q (r | q − 1), B̄ = ⊕_χ B̄_χ and Ā = ⊕_ρ Ā_ρ, with
  κ_{χ,χ′}: B̄_χ × B̄_{χ′} → Ā_{χχ′}.
- **A hard pair** is (χ, χ′) with χ, χ′ and χχ′ all nontrivial and κ_{χ,χ′} ≠ 0.

**Theorem 2.** Suppose G satisfies (K) and has no hard pair. Fix a bound C. Then |Hom(π₁(M), G)| is computable in time polynomial
in the size of the input, for closed orientable 3-manifolds M with |H₁(M; Z)| ≤ C given by triangulations or balanced
presentations.

**Examples.**
- **Heisenberg groups.** For G = H(F_q) ⋊ C_r with h ↦ (αx, βy, αβz), the only possibly nonzero component is κ_{α,β}. So there is
  no hard pair exactly when α = 1, β = 1 or αβ = 1.
- **SL(2,3)** = Q₈ ⋊ C₃. A = Z(Q₈) has the trivial character, so every component lands in Ā₁. This recovers
  `SL23-BOUNDED-20261025-001A` for this group.
- **Nilpotent groups** (r = 1) have only the trivial character. This is the Samperton–Weiß setting (class 2, bounded H²).

**The other side** (`COPRIME-CLASS2-20261026-001D`). For the Heisenberg family over odd prime fields, a hard pair makes counting
#P-hard already on r-surgeries of knots. So the criterion "is there a hard pair?" decides that family.

## Nearest known result

- **Samperton and Weiß (arXiv:2602.02885v2), Theorem 2 and Lemma 3.1.2.** Class-2 nilpotent G with |H²(M, Z(G))| bounded: the
  obstruction map is quadratic, and Gauss sums count its zeros. Theorem 2 here extends this to coprime cyclic twisting without a
  hard pair.
- **`SL23-BOUNDED-20261025-001A`.** A central (Z/2)^m layer over an elementary abelian layer over a nilpotent top.
- **Maria and Spreer (2020).** TV₄ is polynomial with bounded rank of first homology.
- **Novelty.** Candidate-local-delta, with folklore risk medium. The point is that the condition "no hard pair" is exactly what
  keeps every unbounded part of the obstruction linear or pairwise.

## 1. Characters and cocycles

- Fix ψ: π → C_r, and let C′ = ψ(π). Maps π → G over ψ are pairs (c, ζ) made of:
  - a cocycle c ∈ Z¹(π; B_ψ) whose obstruction o_ψ(c) = [β_*(c ⌣ c)] ∈ H²(π; A_ψ) vanishes;
  - a lift, counted by |Z¹(π; A_ψ)| (central-extension obstruction theory: Matei–Suciu; `SL23-BOUNDED-20261025-001A` §2).
- If |H₁(M)| ≤ C, there are at most C maps ψ.

## 2. The bounded part

- By Maschke (p ∤ r), B = B₁ ⊕ B₊ and A = A₁ ⊕ A₊. Here B₁ is fixed by C′, and B₊ is the sum of the nontrivial isotypic components.
- Then Z¹(π; B_ψ) = Hom(π, B₁) ⊕ Z¹(π; B₊).
- The first summand has at most |B₁|^{d} elements, with d = dim H¹(M; F_p) ≤ log_p C. It is enumerated.
- The hypothesis restricts to C′: if χ, χ′ and χχ′ are nontrivial on C′, they are nontrivial on C_r.

## 3. The shape of the obstruction

**Components.** Over F_q, write c = Σ_χ c_χ. Then o(c) = Σ_{χ,χ′} β_*(c_χ ⌣ c_{χ′}).
- For degree-one classes, the mixed terms combine into κ-terms.
- For p odd, the diagonal terms are ½κ_*(c_χ ⌣ c_χ).
- For p = 2 they are κ-terms plus an F₂-additive term D(c_χ) ∈ H²(A_{χ²}), from the symmetric part of β.

**Nontrivial components ρ.**
- A term with χχ′ = ρ ≠ 1 and κ_{χ,χ′} ≠ 0 has χ = 1 or χ′ = 1, because there is no hard pair.
- So for fixed c₁ the A₊-components of o are affine in c₊. The p = 2 terms D are F₂-linear.

**The trivial component.**
- It is a quadratic function of c.
- Its values lie in H²(π; A₁) ⊆ H²(M; A₁), which has at most |A₁|^{d} elements. So there are boundedly many quadratic conditions.

## 4. Counting

For each ψ and each enumerated c₁:
1. Solve the affine conditions over F_p, which gives an affine space L of cocycles c₊.
2. Count the common zeros on L of k = O(1) quadratic polynomials over F_p:

   #zeros = p^{−k} Σ_{θ ∈ F_p^k} Σ_{x ∈ L} e_p(θ · Q(x)).

   - For p odd, each inner sum is a quadratic Gauss sum, evaluated by diagonalization in polynomial time (Samperton–Weiß,
     Lemma 3.1.2).
   - For p = 2, the Arf invariant does the same (`SL23-BOUNDED-20261025-001A` §3).
3. In the bilinear case (Heisenberg groups), the inner sum is simply p^{dim L − rank(θ ∘ B)}.

**Computing the inputs.** Cocycle spaces, the cochain-level obstruction (relator words evaluated on lifts), and its reduction
modulo coboundaries in the presentation complex are all polynomial-time linear algebra. The class vanishes in H²(π) exactly when it
vanishes in H² of the presentation complex, because H²(π) → H²(K_P) is injective.

## 5. Why a hard pair breaks this

- Suppose κ_{χ,χ′} ≠ 0 with χ, χ′ and χχ′ all nontrivial. Then the A_{χχ′}-component of the obstruction is bilinear in two
  unbounded parts.
- It lands in a space dual to V_{(χχ′)⁻¹}, which is unbounded as well.
- Neither enumeration nor a bounded quadratic system applies. `COPRIME-CLASS2-20261026-001D` shows that for the Heisenberg family
  this is #P-hard.

## Check

`check.py` uses only the standard library and imports `cp_lib.py` read-only from `COPRIME-CLASS2-20261026-001B-P001`; it runs in
under a second.

1. **The polynomial route against enumeration.**
   - Seven groups without a hard pair: (α, β) = (2, 3), (4, 4), (2, 1), (1, 2) at p = 5, r = 4; (2, 4) at p = 7, r = 3; (3, 5) and
     (1, 3) at p = 7, r = 6.
   - Each on S³_s(K) for K ∈ {6₁, 4₁, 3₁} and s ∈ {r, rp}; the rp-surgeries have p-torsion in H₁.
   - For every character, the polynomial route agrees with direct enumeration. That is 56 cases with both sides nonempty.
   - The two routes: enumerating the trivial side followed by linear algebra; or a sum over the bounded space of θ.
2. **Brute force.** Totals |Hom| on rp-surgeries agree with brute-force enumeration in eight cases:
   - (2, 3) at p = 5: 500 and 3500;
   - (4, 4) at p = 5: 500 and 6500;
   - (2, 1) at p = 5: 500 and 3500;
   - (2, 4) at p = 7: 1029 and 1029.
3. **Control.** The hard pattern (2, 2) at p = 5 is not covered by the route.

## Scope

- **Hypotheses.** (K), with bounded |H₁|.
- **Cited:**
  - Samperton–Weiß Lemma 3.1.2 (quadratic Gauss sums over finite abelian groups);
  - Matei–Suciu (twisted lifting);
  - the injectivity H²(π) → H²(K_P).
- **The general theorem is proved.** The check exercises the Heisenberg case, with small knots and p-torsion.
- No P versus NP claim.
