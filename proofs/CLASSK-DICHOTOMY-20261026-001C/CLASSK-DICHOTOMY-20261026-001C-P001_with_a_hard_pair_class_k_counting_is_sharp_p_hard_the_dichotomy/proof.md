# With a hard pair, class-(K) counting is #P-hard with H₁ = Z/r: the dichotomy

Status: Proved

## Standard statement

**Setting.**
- p is an odd prime and r divides p − 1.
- G = N ⋊ C_r is of class (K) (`COPRIME-CLASS2-20261026-001C`). N is a central extension of an elementary abelian B by a C_r-invariant
  elementary abelian A, given by an equivariant bilinear cocycle; κ is the commutator pairing.
- A **hard pair** is a pair of characters (χ, χ′) of C_r with χ, χ′ and χχ′ nontrivial and κ_{χ,χ′} ≠ 0.
- For d | r, write G_d = N ⋊ C_d for the subgroup over the subgroup of order d. Its characters are the restrictions to C_d.

**Theorem C (hardness).** If G has a hard pair, the following problem is #P-hard under polynomial-time Turing reductions:
- **Input:** a knot diagram K.
- **Output:** |Hom(π₁(S³_r(K)), G)|.

Every such manifold has H₁ = Z/r. The reduction makes at most r oracle calls per value of a fixed Bulatov–Grohe partition function.

**Corollary D (dichotomy, closed manifolds).** Fix C ≥ 1. For closed orientable 3-manifolds with |H₁(M; Z)| ≤ C, given by
triangulations or balanced presentations, counting homomorphisms π₁M → G is:
- polynomial if no G_d with d | r and d ≤ C has a hard pair;
- #P-hard (Turing) otherwise.

For C ≥ r the criterion is simply whether G has a hard pair.

**Corollary E (knot groups).** If G has a hard pair, counting |Hom(π₁(S³ ∖ K), G)| for knots given by diagrams is #P-hard, with at
most r|B| oracle calls. This holds also when some commutator component involves the trivial character. With
`COPRIME-CLASS2-20261026-001C`, whose algorithm covers knot groups, knot-group counting for class-(K) groups over odd prime fields is
polynomial exactly when there is no hard pair. So Rowell's Conjecture 3.2(b), which asks for exact polynomial counting on link
groups for every finite solvable group, fails for every class-(K) group with a hard pair unless every #P function is computable in
polynomial time.

**Examples.**
- **Heisenberg groups.** For H(F_p) ⋊ C_r acting by (αx, βy, αβz), the only component is κ_{α,β}, so this is
  `COPRIME-CLASS2-20261026-001D`.
- **The free class-2 group on characters (ζ, ζ², ζ³) at p = 7, r = 6.** It is #P-hard for C ≥ 6 and polynomial for C ≤ 5.
  - Restricted to C_3 the characters become (ω, ω², 1). The only commutator between nontrivial ones has trivial product.
  - Restricted to C_2 they become (−1, 1, −1), whose product is again trivial.

## Nearest known result

- **`COPRIME-CLASS2-20261026-001D`.** The Heisenberg family, with four Potts gadgets. This ticket replaces the gadgets by Bulatov–Grohe
  and covers all of class (K).
- **`CLASSK-DICHOTOMY-20261026-001A`.** The count as a positive sum of sector partition functions, used here.
- **`NEXT-DIRECTION-SCAN-20261026-001A`.** It sketched this route and listed its gaps. They are closed here:
  - sector isolation, by Lemma I;
  - the pattern-1 knot, by `PATTERN1-CHECKPOINT-20261026-001`, with all three patterns checked in `CLASSK-DICHOTOMY-20261026-001B`;
  - knot groups with trivial-character commutators, by §6.
- **Bulatov–Grohe, Theoret. Comput. Sci. 348 (2005).** For a symmetric, connected, non-bipartite matrix with non-negative algebraic
  entries, EVAL(A) is polynomial if rank A ≤ 1 and #P-hard otherwise. This is stated so as Theorem 2.1 of Cai–Chen–Lu
  (arXiv:0903.4728), whose hardness side is for input graphs with multiple edges and no loops. Our construction accepts such
  multigraphs.
- **Samperton–Weiß (arXiv:2602.02885v2).** Polynomial time for class-2 nilpotent G with bounded |H²(M; Z(G))|. With coprime twisting,
  bounded H₁ is not enough, and the hard pair is the exact criterion in class (K).
- **Galindo (arXiv:2605.06984).** Hardness for every nonabelian G with unbounded homology.
- **Kuperberg–Samperton (2018), Rowell (2009).** The solvable case is open there, and Rowell conjectures polynomial counting on link
  groups.
- **Novelty.** Candidate new: an exact dichotomy for all class-(K) groups over odd prime fields with r | p − 1, both for closed
  manifolds with bounded H₁ and for knot groups.
  - Folklore risk: medium. The ingredients are standard (Bulatov–Grohe, clasper realization, Vandermonde interpolation over disjoint
    unions).
  - Searches this epic, and those of the earlier epics, found no statement of it.

## Proof

### 1. Realization

**Lemma R.** Fix a slot triple S of one of the three patterns of `CLASSK-DICHOTOMY-20261026-001A`. A polynomial-time algorithm takes a
loopless multigraph Γ (n vertices, m edges) to a knot diagram K_Γ such that:
1. M_Γ = S³_r(K_Γ) is a Γ-gadget manifold for S (Theorem A's hypotheses), with ψ the meridian character;
2. the leaves of the Y-graphs have linking number 0 with the base knot.

K_Γ has O(m(n + m)) crossings, with a constant depending on p and r.

**Proof.** This is the construction of `COPRIME-CLASS2-20261026-001D` §3 applied to the gadget tensors of Theorem A. That construction
uses the group nowhere. Each step is a cited part of D or B:

- **The base.** There is one twist knot K_{m(τ)} per gadget coordinate, with τ the coordinate's character and m(τ) ≡ τ(τ − 1)⁻² mod p
  (a nonzero integer representative).
  - By D §2 each summand contributes one dimension to V_τ and one to V_{τ⁻¹}, and nothing else.
  - Different types within one pattern have disjoint root sets:
    - in P1, s_i = s_j⁻¹ would force the third character to be trivial;
    - in P2, {s, s⁻¹} meets {t, t⁻¹} only if s = 1 or s³ = 1.
  - So the dimensions are those of Theorem A's hypothesis 1.
  - T₀ = 0 on every component. T splits over the summands, and a component with characters from one summand's {τ, τ⁻¹} must be
    (τ, τ, τ) with τ³ = 1, where an alternating form on a line vanishes.
- **Pure leaves** (D §3, steps 2–3; B (d)).
  - In each summand's ball there is a leaf in ker ψ, made of band-summed copies of a band loop around two arcs. Each copy is repeated
    r⁻¹τ^{−j} mod p times with bands winding j times around a meridian.
  - Its functional is nonzero exactly on that summand's line in V_τ. It vanishes on other summands, because coboundaries vanish on
    loops in ker ψ.
  - These functionals are the coordinates. Each copy encircles one arc positively and one negatively, so every leaf has linking number
    0 with the base knot.
- **The Y-graphs.** There is one per edge e = (u → v). Its leaves are:
  - the balanced band sum x_u − x_v of the two vertex leaves (D §3, steps 4–5);
  - the leaf of the edge's second-slot summand (y_e or p_e);
  - the leaf of its third-slot summand (t_e, w_e or q_e).

  The Y-graphs are pairwise disjoint and disk-framed, with ψ ≡ 0 on every closed loop through a vertex and an edge. Each has a private
  leaf, so the result is S³_r(K_Γ) with the Seifert framing preserved (D §3, steps 6–7; Habiro, Props. 3.3–3.4).
- **Steering** (`COPRIME-CLASS2-20261026-001B` (c), (d)).
  - Each Y-graph adds ε f_{1e} ∧ f_{2e} ∧ f_{3e} to the alternating triple-product form. Here ε = ±1 is a fixed convention, absorbed
    into f_{3e}.
  - Pure leaves change only the permutations of S, and H₁ and every V_θ are unchanged.
  - So T = 𝒯_Γ.
- **Size** (D §3, "Size").
  - Each leaf has at most r(p − 1) copies, each with at most r − 1 windings.
  - The disjoint Y-graph surgeries are tangle replacements, and edges and bands cross O(n + m) arcs.
  - In the experiment `CLASSK-DICHOTOMY-20261026-001B`: K₂ needs 1,761 crossings, the digon 4,124 and K₂ ⊔ K₂ 3,622 (p = 7).

**Status of the realization.** It rests on D's proof and on two cited facts: Massuyeau's lemma (through B) and the description of a
Y-graph surgery as surgery on its six-component link (Habiro; Garoufalidis–Goussarov–Polyak). End to end it has been checked on
explicit surgeries:
- pattern 1 at p = 7, r = 6 (`PATTERN1-CHECKPOINT-20261026-001`);
- all three patterns at (7, 6) and pattern 2 at (5, 4), every sector, closed and knot exterior (`CLASSK-DICHOTOMY-20261026-001B`).

### 2. The count

By Theorem A (`CLASSK-DICHOTOMY-20261026-001A`):

  h(Γ) := |Hom(π₁M_Γ, G)| = Σ_{k ∈ Z/r} c_k f_k(Γ), with f_k(Γ) = λ_k^n μ_k^m Z_{W_k}(Γ).

Here c_k > 0, each f_k is multiplicative over disjoint unions, and f_1 > 0. For the slot triple of a hard pair, the matrix
𝐖 = [W_1(x − y)] is symmetric with positive entries and rank at least two (Theorem A (a)–(c)).

### 3. Isolating one sector

**Lemma I.** Let f_1, …, f_N map loopless multigraphs to the non-negative rationals, each multiplicative under disjoint union with
f_i(∅) = 1, and with f_1 > 0 everywhere. Let I = {i : f_i = f_1 as functions}, and let h = Σ_i c_i f_i with c_i > 0. Then:
- there is a multigraph F with f_i(F) ≠ f_1(F) for every i ∉ I;
- from h(Γ ⊔ F^{⊔j}) for j = 0, …, R − 1, where R is the number of distinct values f_i(F), one computes (Σ_{i ∈ I} c_i) f_1(Γ) by
  solving one Vandermonde system.

**Proof.**
- **Witnesses.** For i ∉ I pick F_i with f_i(F_i) ≠ f_1(F_i), and put F = ⊔_i F_i^{⊔ a_i} with integers a_i ≥ 1.
- **Zero values.** If f_i(F_{i′}) = 0 for some i′, then f_i(F) = 0 < f_1(F).
- **Positive values.** Otherwise f_i(F) = f_1(F) means Σ_{i′} a_{i′} log(f_i(F_{i′})/f_1(F_{i′})) = 0. The coefficient at i′ = i is
  nonzero, so this is a proper hyperplane in a-space.
  - Finitely many proper hyperplanes cannot cover the grid {1, …, N₀}^{N−|I|} once N₀ exceeds their number, since each meets it in at
    most N₀^{N−|I|−1} points.
- **The solve.** By multiplicativity, h(Γ ⊔ F^{⊔j}) = Σ_z (Σ_{i : f_i(F) = z} c_i f_i(Γ)) z^j.
  - Solving the Vandermonde system in the distinct values z recovers each bracket.
  - By the choice of F, the bracket at z = f_1(F) is exactly Σ_{i ∈ I} c_i f_1(Γ).

F and the constants (the values f_i(F), the set I, and Σ_{i∈I} c_i) depend only on G. The reduction below is a fixed algorithm for
each fixed G, as usual in dichotomy proofs.

### 4. Proof of Theorem C

- **The hard problem.** Let S be the slot triple of a hard pair. By §2 and Bulatov–Grohe, EVAL(𝐖) is #P-hard on loopless
  multigraphs. 𝐖 is connected and non-bipartite because all its entries are positive, and its rank is at least two.
- **The reduction.** Given Γ, for j = 0, …, R − 1 (R ≤ r):
  1. build K_{Γ ⊔ F^{⊔j}} by Lemma R (F is fixed, so its size is polynomial in |Γ|);
  2. query the counting oracle.

  Lemma I with f_i = f_k yields (Σ_{k∈I} c_k) λ_1^n μ_1^m Z_{W_1}(Γ), hence Z_{W_1}(Γ) = EVAL(𝐖)(Γ).
- **Membership.** Counting homomorphisms from a finitely presented group to a fixed finite group is in #P.

So the problem is #P-complete under Turing reductions.

### 5. Proof of Corollary D

**The polynomial side.**
- The algorithm of `COPRIME-CLASS2-20261026-001C` treats each ψ: π → C_r separately, and uses only that no pair of characters with
  χ, χ′ and χχ′ nontrivial on C′ = ψ(π) carries a nonzero commutator (its §2: "the hypothesis restricts to C′").
- C′ has order d dividing gcd(|H₁|, r), so d ≤ C.
- If no G_d with d | r and d ≤ C has a hard pair, that proof applies verbatim to every ψ.

**The hard side.**
- If G_d has a hard pair with d | r and d ≤ C, apply Theorem C to G_d. G_d is of class (K) with d | p − 1.
- For π with H₁ = Z/d, every map to C_r lands in C_d, so |Hom(π, G)| = |Hom(π, G_d)|.
- These manifolds have |H₁| = d ≤ C.

**Input formats.** A knot diagram gives a balanced presentation of π₁(S³_r(K)) in polynomial time: the Wirtinger relators with one
dropped, plus μ^r λ. A triangulation can also be built in polynomial time by standard methods. Both are formats accepted by C.

### 6. Proof of Corollary E (knot groups)

Let X be the exterior of K_Γ, with π = π₁X, H₁(X) = Z and the characters ψ_k = kψ. The count over ψ_k is
|Z¹(π; A_{ψ_k})| · |B¹(π; B_{ψ_k})| · #{x ∈ H¹(X; B_{ψ_k}) : o(x) = 0}, as in Theorem A §1. Four facts are needed.

**(a) Nontrivial characters.** For θ nontrivial on the meridian, restriction gives H^i(S³_r(K_Γ); F_θ) ≅ H^i(X; F_θ) for i = 1, 2,
compatibly with cup products (D §5): the filling torus and its boundary are θ-acyclic. So all components with nontrivial characters
are those of the closed gadget manifold.

**(b) The trivial character.** H¹(X; F_p) = F_p·u, with u the abelianization mod p, and H²(X; F_p) = 0. The trivial-character
coefficient of x is u ⊗ β with β ∈ B^{(k)}_1 = ⊕_{χ^k = 1} B_χ, and no condition lands in the trivial character.

**(c) The u-pairing.** The only new triple products are P(v, w) = ⟨u ⌣ v ⌣ w, [X, ∂X]⟩ for v ∈ V_θ and w ∈ V_{θ⁻¹}. On X_Γ, P
equals the u-pairing of the base exterior X₀, and that pairing is block-diagonal over the base summands.
- **Invariance.** Work in the 0-surgeries M₀(K) = S³_0(K).
  - u extends, ψ is defined (the longitude lies in the commutator subgroup), and for θ ≠ 1 the θ-twisted cohomology is that of X.
  - The Y-surgeries preserve the Seifert framing (D §3, step 7), so they turn M₀(K₀) into M₀(K_Γ).
  - By B (c), applied to the component (1, θ, θ⁻¹), each Y-graph changes P by a sum of products that each contain u(ℓ) for some leaf
    ℓ. Since u(ℓ) = lk(ℓ, K₀) mod p = 0 by Lemma R (2), P does not change.
- **Block-diagonality.** X₀ is the union of the summand exteriors X_i along meridional annuli, which are θ-acyclic for θ ≠ 1.
  - Excision gives H¹(X₀; F_θ) = H¹(X₀, ∪annuli; F_θ) = ⊕_i H¹(X_i, annuli; F_θ).
  - A class from X_i is therefore represented by a cochain supported in X_i.
  - Cup products of cochains supported in different pieces vanish, and u restricts to u on each piece.

**(d) Splitting by β.** Fix β.
- The terms of o(x) that involve u ⊗ β are κ^{(k)}_{1,θ}(β, ·) applied through P to x_θ. By (c) they pair, inside each base summand,
  that summand's component of x_{τ^{±1}} with that summand's test coordinate.
- All other conditions are those of the closed gadget manifold (Theorem A §2): local edge and vertex conditions plus free components.
- So for fixed β the number f_{k,β}(Γ) of solutions comes from a system whose variables and equations split along the components of
  Γ. Hence f_{k,β} is multiplicative.
- For β = 0 it is the closed sector-k count.
- The constants are |B¹(B_{ψ_k})| |B¹(A_{ψ_k})| p^{dim A^{(k)}_1} times p^{(linear in n, m)}, from H¹(X; A_{ψ_k}).

So

  |Hom(π₁X_Γ, G)| = Σ_k Σ_{β ∈ B^{(k)}_1} c′_k F_{k,β}(Γ),

with c′_k > 0 and each F_{k,β} multiplicative and non-negative. F_{1,0} = λ′^n μ′^m Z_{W_1}(Γ) is positive.

Lemma I applied to the at most r|B| functions F_{k,β}, and Bulatov–Grohe as in §4, prove Corollary E. The polynomial side is
`COPRIME-CLASS2-20261026-001C`: its algorithm needs only bounded dim H¹ (here 1), boundedly many ψ (here r) and H²(X; A₁) = 0.

## Check

`check.py` (numpy) imports read-only:
- `ck_lib.py` from `CLASSK-DICHOTOMY-20261026-001A-P001`;
- the extended-model code from `CLASSK-DICHOTOMY-20261026-001B-E001` (predict.py, ck_specs.py);
- that experiment's frozen artifact rows.

It checks:
1. **Bulatov–Grohe hypotheses.** For every hard pair of the experiment groups and of random class-(K) groups, W_1 is positive, even
   and not constant, and rank 𝐖 ≥ 2. For groups without a hard pair, every sector has rank one.
2. **Lemma I on concrete groups.**
   - **Groups:**
     - two nonconstant sectors (free class 2 in ψ¹, Heisenberg-type in ψ⁵);
     - two equivalent nonconstant sectors (I = {1, 5});
     - a Heisenberg group.
   - Anchors are found among small multigraphs, and exact Vandermonde solves recover (Σ_{I} c_k) f_1(Γ) on test graphs.
   - h(Γ ⊔ F) is also computed directly on the union.
3. **Knot groups on the extended model.** Σ_β f_{k,β} equals the knot count, f_{1,0} equals the closed count, and every f_{k,β} is
   multiplicative on K₂ ⊔ K₂.
4. **End to end.** From the experiment's measured counts:
   - every closed sector count on K₂ ⊔ K₂ is the square of that on K₂;
   - every knot-exterior count on K₂ ⊔ K₂ equals Σ_β f_{k,β}(K₂)², not the square of the K₂ count when a trivial-character commutator
     is present.
5. **The refinement.** Hard pairs of G_d for d | r, including the free class-2 example (#P-hard exactly for C ≥ 6).
6. **Size data.** Crossings of the experiment's surgeries.

## Scope

- **What is proved.** Theorem C and Corollaries D and E for p odd and r | p − 1, under Turing reductions.
- **Cited:**
  - Bulatov–Grohe (through Cai–Chen–Lu, Theorem 2.1);
  - the realization of `COPRIME-CLASS2-20261026-001D` §3, which cites Habiro and Massuyeau;
  - `COPRIME-CLASS2-20261026-001B` (c) and (d);
  - `COPRIME-CLASS2-20261026-001C` for the polynomial side.
- **Not covered:**
  - p = 2, where diagonal Bockstein terms appear;
  - extension fields (r ∤ p − 1);
  - groups outside class (K);
  - approximate counting;
  - a uniform bound in G (F depends on G).
- **Review.** No external review. No P versus NP claim.
