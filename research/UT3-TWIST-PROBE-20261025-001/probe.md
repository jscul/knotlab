# Probe: does the twisted lifting obstruction of UT₃(F₄) ⋊ C₃ grow?

Ticket `UT3-TWIST-PROBE-20261025-001`, 2026-10-25.
- **What it is.** One bounded pass, authorized by the owner through Codex.
- **What it is not.** Documentation, not a proof. The measurements are reproducible with `probe.py`, whose output is
  `probe_output.json`. Frozen evidence from `SL23-BOUNDED-20261025-001` and `CLOSED-H1-20261025-001` is imported read-only.

## The group

- **F₄.** F₂[ω]/(ω² + ω + 1).
- **N = UT₃(F₄).** Written as triples (x, y, z), with (x, y, z)(u, v, w) = (x + u, y + v, z + w + x·v).
- **G = N ⋊ ⟨h⟩**, of order 192, with h n h⁻¹ = α(n).

| Action | α(x, y, z) | Facts (computed) |
| --- | --- | --- |
| **Probe target** | (ω²x, ω²y, ωz) | Z(G) = 1; G′ = N, of order 64 and non-abelian; [G, G′] = G′. Not abelian-by-nilpotent; Fitting height 2. |
| **Control** | (ωx, y, ωz) | G′ is abelian of order 16. Metabelian, so already polynomial (`BOUNDED-H1-20261025-001B`). |

**The two layers.** A = Z(N) = F₄. A character ψ: π₁(M) → C₃ twists it by ω. Over ψ:
- A is the module F₄_ω;
- N/A = F₄² is (F₄_{ω²})² for the target, and F₄_ω ⊕ F₄ for the control.

## Inputs and observables

**Inputs.** Integral surgery S³₃(K), as balanced presentations: the Wirtinger relators minus one, plus μ³λ.
- H₁ = Z/3 was verified by Smith normal form for every manifold used.
- K runs over (4₁)^{#k}, (3₁)^{#k}, (8₁₈)^{#k}, and the tripled alternating diagrams of C₃, C₅ and C₇.

**Observables**, for each character ψ:
- **D** = dim_{F₂} of the space L of lifts of ψ to G/A, which are twisted cocycles.
- **ambient** = dim_{F₂} H²(P; A_ψ), the cokernel of the twisted coboundary on A-cochains.
- **span** = dim_{F₂} of the span, in H²(P; A_ψ), of the actual obstruction classes o(c) for c ∈ L.
  - It is computed from the coefficient vectors of the degree-2 map c ↦ o(c), reduced modulo coboundaries.
  - It is the number of independent scalar conditions that liftability imposes.
- **liftable** = #{c ∈ L : o(c) = 0}, from Gauss sums over the characters of the span.
- **|Hom(π₁M, G)|** = Σ_ψ liftable(ψ)·|Z¹(P; A_ψ)|, checked by brute force over all homomorphisms where feasible.

## Measurements

| Manifold (H₁ = Z/3) | Action | D | ambient | span | liftable / 2^D | \|Hom(π₁M, G)\| | Brute force |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S³₃((4₁)^{#k}), k = 1, 2, 3 | target | 4k + 4 | 2k + 2 | **0** | 1 | 8,193; 524,289; 33,554,433 | k ≤ 2 agree |
| S³₃((3₁)^{#k}), k = 1, …, 4 | target | 4k + 4 | 2k + 2 | **2k** | (7/16)^k | 1 + 128·28^k | k ≤ 2 agree |
| S³₃((8₁₈)^{#k}), k = 1, 2, 3 | target | 8k + 4 | 4k + 2 | **2k** | (7/16)^k | 229,377; 411,041,793; 736,586,891,265 | — |
| S³₃((3₁)^{#k}), k = 1, 2, 3 | control | 2k + 2 | 2k + 2 | **0** | 1 | 513; 8,193; 131,073 | k ≤ 2 agree |
| S³₃(D(C_n⁽³⁾)), n = 3, 5, 7 | target | 8, 4, 4 | 4, 2, 2 | **0** | 1 | — | — |

**Section independence.** Replacing the section (x, y) ↦ (x, y, 0) by (x, y) ↦ (x, y, x·y) leaves every span and every count
unchanged. So the growth is intrinsic: it concerns cohomology classes, not representatives.

## What is proved (short arguments)

1. **The obstruction is a cup product.**
   - With the section (x, y, 0) and the complement ⟨h⟩, α preserves z = 0, so conjugation adds no correction.
   - The 2-cocycle of N over N/A is β((x, y), (u, v)) = x·v, which is bilinear.
   - So o(c) = [c_x ⌣ c_y] ∈ H²(π; F₄_ω), using F₄_{ω²} ⊗ F₄_{ω²} → F₄_ω. This is standard central-extension obstruction theory.
2. **Knot surgeries reduce to the exterior.** In S³_p(K), the core of the surgery torus is homologous to the meridian. So when ψ is
   non-trivial on the meridian, it is non-trivial on the boundary torus and on the core. Twisted cohomology of a circle or torus with
   no fixed vectors vanishes, so Mayer–Vietoris gives H*(M; ·_ψ) ≅ H*(X_K; ·_ψ).
3. **Connected sums are block-diagonal.**
   - The exteriors of K₁ # K₂ are glued along a meridional annulus, whose twisted cohomology vanishes.
   - So H¹ = H¹(X₁) ⊕ H¹(X₂), and H² injects into the sum of the restrictions.
   - Hence a₁ ⌣ a₂ = 0 for classes from different summands. The bilinear map (a, b) ↦ a ⌣ b is block-diagonal, and every count
     factorizes over the summands. This explains 1 + 128·28^k.
4. **The general count is a rank-sum.** liftable(ψ) = |B¹|²·Σ_{a ∈ H¹} |ker(b ↦ a ⌣ b)|, with a, b in H¹(M; F₄_{ω²}): a sum, over
   first-level classes, of 2 to the corank of a linear map depending on the class. It has the same shape as S₄'s bicycle law, where the
   dimension of a level depends on the level below.

## What is measured but not explained in general

- **Collapse for the figure-eight.** It is consistent with Σ₃(4₁) being the Hantzsche–Wendt manifold, a cited fact.
  - There H₁ = (Z/4)², every mod-2 class lifts to Z/4, and squares vanish.
  - The ω²-eigenspace is one-dimensional over F₄ per summand, so a ⌣ b = λa² = 0.
- **The trefoil and 8₁₈ blocks.** Each summand contributes an obstruction block of F₂-rank 2, with liftable fraction 7/16.

## Assessment

- **Does the effective obstruction grow? Yes, on a valid family.**
  - On S³₃((3₁)^{#k}), with H₁ = Z/3, the obstruction span grows as 2k. That is intrinsic and section-independent.
  - Samperton and Weiß's twisted-coefficient caveat is real: the obstruction target cannot be assumed bounded.
- **Does that indicate hardness? No, not on any tested family.** The growth is block-diagonal (connected sums), so counts factorize
  and stay polynomial. The prime knots tested (3₁, 8₁₈, tripled cycles) keep bounded blocks.
- **Why these families cannot discriminate.** Connected sums produce direct sums of fixed blocks by construction (item 3). Tripled
  cycles keep the twisted cohomology bounded.
- **The control behaves as predicted.** The easy action has span 0 throughout: its untwisted y-coordinate has no cocycles when H₁ =
  Z/3, so the cup product vanishes.

## Novelty

- **Routine.** Item 1 is standard obstruction theory (compare Samperton–Weiß Lemma 3.1.1, untwisted), and items 2–3 are routine
  Mayer–Vietoris.
- **New as far as scanned.**
  - The observation that the twisted obstruction of this group grows on bounded-homology knot surgeries, in block-diagonal form.
  - The reduction to a rank-sum of twisted cup products.
- **Closest sources.**
  - Samperton and Weiß, arXiv:2602.02885v2: footnote 11 (twisted case unclear), and §1.5, which reports Chlopecki and Samperton's
    hardness for counting solutions of non-homogeneous symmetric bilinear systems over F₂. That paper was not read.
  - Matei and Suciu (2005).

## Next decision

The smallest missing test is a bounded-homology family whose twisted cup product a ⌣ b on H¹(M; F₄_{ω²}) is not block-diagonal.
- **Candidates.** Prime knots, or surgeries on links with bounded linking determinant, whose 3-fold cyclic branched covers have a
  growing, indecomposable ω²-eigenspace with nonzero products: twisted doubles, satellites of the trefoil, pretzel families.
- **What to measure.**
  - Whether the rank-sum Σ_a 2^{corank(a ⌣ ·)} stops factorizing.
  - Whether the realizable bilinear maps include arbitrary sparse systems. If so, hardness would follow along the lines of the
    bilinear-system results.
- **Recommendation.** This is a separate, bounded epic if pursued; the probe stops here.
