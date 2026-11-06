# Probe: growing, interacting obstruction blocks for UT₃(F₄) ⋊ C₃

Ticket `UT3-INTERACT-PROBE-20261026-001`, 2026-10-26.
- **What it is.** A bounded follow-up to `UT3-TWIST-PROBE-20261025-001`, authorized by the owner through Codex, with a budget of 60
  minutes. The clock started at 19:32:27Z, and the consolidated run finished at 19:41:54Z.
- **What it is not.** Documentation, not a proof. The probe is reproducible with `run_probe.py` (together with `bimap.py`), whose
  output is `probe_output.json`.

## Target

- **The group.** As in the previous probe: F₄ = F₂[ω]/(ω² + ω + 1); N = UT₃(F₄), written as triples (x, y, z) with (x, y, z)(u, v, w)
  = (x + u, y + v, z + w + x·v); G = N ⋊ ⟨h⟩.
- **The action.** α(x, y, z) = (ω²x, ω²y, ωz). The control action is (ωx, y, ωz).
- **Rechecked facts.**
  - Target: Z(G) = 1; G′ = N, of order 64 and non-abelian; [G, G′] = G′.
  - Control: G′ is abelian of order 16.

## The object measured: the obstruction bimap

**Definition.** Fix ψ with ψ(meridian) = 1. Set
- V_x = V_y = H¹(M; F₄_{ω²}), with F₂-dimension u = v;
- W = the span, in H²(M; F₄_ω), of the obstruction classes;
- B(a, b) = the obstruction class of the G/A-representation with cocycle (a, b), which is the twisted cup product [a ⌣ b].

**How it is computed.**
- B is read from the A-parts of the relators, which are exactly bilinear at cocycle level. Only x·y terms occur, including the
  diagonal terms coming from inverses (x, y, 0)⁻¹ = (x, y, xy).
- It is reduced modulo im(δ₁).
- Sanity assertions in `bimap.py`:
  - pure x- or pure y-cocycles have zero obstruction;
  - coboundaries are cocycles and pair to zero;
  - a sample of sums satisfies bilinearity.

**H² bookkeeping (the clarification requested).**
- **The presentation complex.** It is balanced (the Wirtinger relators minus one, plus μ³λ), and K_P ≃ M − B³.
- **The extra dimension.** coker(δ₁) on K_P equals H²(M − B³; A_ψ) = H²(M; A_ψ) ⊕ F₄, so its F₂-dimension is H²(M) + 2. The reason:
  for ψ ≠ 1, H³(M; A_ψ) ≅ (A_ψ*)_π = 0, while H³(M, M − B³; A_ψ) ≅ A.
- **Where the classes live.** The obstruction class of a representation of π₁ lies in H²(π; A_ψ). That group injects into
  H²(M; A_ψ), because M → Bπ is 2-connected, which in turn injects into H²(K_P; A_ψ).
- **Lift counts are unaffected.** Liftability is the vanishing of the class in coker(δ₁), so all lift counts stand.
- **A mislabel corrected.** The "ambient" column of `UT3-TWIST-PROBE-20261025-001` was coker(δ₁) on P, that is H²(M) + 2. That
  probe's note defines it correctly, but its final chat message called it H²(M).
- **Measured.** In every case H²(M; A_ψ) = coker − 2 = dim H¹(M; F₄_{ω²}), as Poincaré duality requires. Whenever the bimap is
  non-zero, W = H²(M; A_ψ): the obstruction classes span all of H²(M).

## The decomposition certificate

**The certificate.**
- **Remove the null directions.** Drop the left and right radicals, and restrict W to the image span. The result is a bimap that is
  non-degenerate and full.
- **The centroid.** C(B) = {(f, g, h) ∈ End_{F₂}(U) × End(V) × End(W) : B(fu, v) = h B(u, v) = B(u, gv)}.
- **It is commutative** for non-degenerate full bimaps. For example, hh′ = h′h on the image, and then nondegeneracy forces ff′ = f′f.
- **Decompositions are idempotents.** Direct-sum decompositions (U = ⊕U_i, V = ⊕V_i, W = ⊕W_i, with B(U_i, V_j) = 0 for i ≠ j and
  B(U_i, V_i) ⊆ W_i) correspond to frames of idempotents in C(B). This is the standard theory of bimaps (Wilson), cited.
- **Counting them.** In a commutative F₂-algebra, x ↦ x² is F₂-linear. So the idempotents form the subspace ker(Frob − 1), whose
  dimension is the number of local factors, which is the number of blocks of the finest decomposition. The primitive idempotents give
  the blocks and their sizes.

**The transformations covered.**
- **All independent F₂-linear changes of basis** of U, V and W, that is GL_{F₂}(U) × GL(V) × GL(W).
- **Not only F₄-linear ones.** The F₂-centroid contains F₄, as ω acting on all three spaces. Its idempotents commute with ω, so every
  F₂-linear decomposition is automatically F₄-linear.
- **The symmetry V_x = V_y is not imposed.** That makes the equivalence coarser, so indecomposability under it is the stronger
  statement.

**Implementation checks.**
- **Random basis changes.** Three random independent F₂ basis changes per case leave the block counts and sizes unchanged, in every
  case with n ≤ 12 and in every control.
- **Section and representatives.** Changing the section to z = x·y, and applying two coboundary shifts of the cocycle
  representatives, leave the blocks unchanged for n = 6 and 9.
- **A bug fixed on the way.** A first version of the shift test added per-coordinate noise rather than coboundaries. It produced the
  impossible W = 10 > H²(M) and was fixed.
- **Not checked for basis changes:** n = 15, to save time.

## Families (all with H₁ = Z/3 by Smith normal form, ψ(meridian) = 1)

| Family | Members | Blocks (over F₄) |
| --- | --- | --- |
| Control: (3₁)^{#k} | k = 1, …, 4 | k blocks of size 1×1→1: decomposable, as required |
| F1: closures of (σ₁σ₂⁻¹)ⁿ | n = 2, 4, 5, 7, 8 | at most one 1×1×1 block (8₁₈); otherwise radical or zero |
| F2: closures of (σ₁³σ₂³)^m | m = 1, 2, 4, 5 | m = 1, 5: two singleton blocks; m = 2, 4: all radical |
| Chain control: σ₁³ ⋯ σ_{n−1}³, the connected sum of n − 1 trefoils | n = 3, 6, 9 | n − 1 singleton blocks |
| **Coupled: the chain times one full twist Δ²** | n = 3, …, 12 and 15 | **n = 3m (m ≥ 2): one inseparable block of size 2m − 1 (F₂ sizes 6, 10, 14, 18 for m = 2, …, 5) plus m − 1 singletons.** n = 3: radical only. Other n ≤ 11: no twisted cohomology. |

F1 and F2 are 3-braid closures, which keep the twisted cohomology at most 2-dimensional over F₄, so they cannot grow.

## Counts

- **Two independent counting routes agree.** Gauss sums over the obstruction map, and the rank-sum Σ_a 2^{corank B(a,·)} over the
  bimap, give 27,328 for n = 6 and 6,409,984 for n = 9.
- **Block counts.** The number of pairs (a, b) with B(a, b) = 0 on a block:

  | Block size over F₄ | 1 | 3 | 5 | 7 |
  | --- | --- | --- | --- | --- |
  | Count | 7 | 244 | 8,176 | 367,684 |

- **Corank distributions of the big blocks over F₄**, deconvolved from the totals:
  - d = 3: {0: 24, 1: 39, 2: 0, 3: 1};
  - d = 5: {0: 360, 1: 498, 2: 120, 3: 45, 4: 0, 5: 1}.

  For d = 3 the singular locus is 13 points of PG(2, 4), the size of three concurrent lines.
- **Easy control** on the coupled family: span 0 (n = 6, 9).
- **Brute force** is not feasible for the coupled family, which has at least 45 generators. The counting pipeline was validated by
  brute force on small manifolds in `UT3-TWIST-PROBE-20261025-001`.

## Observed versus proved

**Proved, by short arguments or cited theory:**
- B is the twisted cup product;
- the H² bookkeeping;
- decompositions correspond to idempotents of the centroid;
- counts factorize over blocks.

**Measured exactly, but not a general theorem:**
- the coupled family's inseparable block grows as 2m − 1 for m = 2, …, 5;
- the controls are decomposable.

**Not established:**
- a formula for c_d;
- any hardness. The family has a single manifold per size, so it encodes no arbitrary instances.
- The quoted bilinear-system hardness (Chlopecki–Samperton, reported as in preparation) concerns non-homogeneous systems. It would need
  its own reduction to our homogeneous zero-obstruction counts.

## Assessment and next recommendation

- **Outcome: growing, intrinsic interaction.**
  - On valid closed manifolds with H₁ = Z/3, the coupled family has inseparable blocks of size 3, 5, 7 and 9 over F₄.
  - They are certified indecomposable under all independent F₂-linear changes of basis, with implementation checks up to n = 12.
  - Its connected-sum control decomposes fully.
- **No hardness is inferred.** Growing blocks defeat factorization, but a closed form for c_d could still make the family efficiently
  countable. The determinant locus suggests algebraic structure.
- **Novelty.** The certificate is standard. Its use on twisted cup-product obstructions, and the measured growth, are new as far as
  scanned. Folklore risk is high for the method and low to medium for the observation.
- **Next recommendation.** Identify the structure of the coupled block, for example its autotopism group, its determinant locus for
  d = 5 and 7, and whether it is a known bimap. That decides whether c_d has a closed form, the cheapest discriminator between
  "interacting but countable" and a possible hardness route. Only then, test whether twists placed at chosen positions can steer the
  blocks to encode inputs.
