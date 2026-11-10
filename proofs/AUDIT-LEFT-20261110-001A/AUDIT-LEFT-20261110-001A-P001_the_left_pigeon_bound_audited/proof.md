# The left-pigeon bound, re-derived and audited

Status: Survives the audit. Every step was re-derived and holds; four fresh reviewers found no failing step. The proof stays V1 and
conditional on A55. The result is **not new in substance**: the 2n-pigeon formula is Pudlák and Thapen's rWPHP_n, and a stronger
bound, exp(Ω(n)), follows in a few lines from Pang's degree–size relation (arXiv 2610.00837, 30 September 2026); see §8.4.

Ticket `AUDIT-LEFT-20261110-001A`, 2026-11-10. This is the note for review asked for in sub-goal B116, written as an audit of
`WIDE-LEFT-20261110-001A` (proof written in one session, V1). Everything below is derived again from Braun's stated results, with every
constant and quantifier explicit; it does not lean on the earlier proof's wording. Four fresh reviewers, not shown either proof, attacked
the steps; their findings are in the audit section.

## 1. Statement

**Formulas.** Fix l ≥ 2 and n = 2^l. Holes are h ∈ {0,1}^l. In WLP_n the pigeons are all x ∈ {0,1}^{l+1} (2n of them); in LP_{n+1}
they are the codes of 0, 1, …, n in l + 1 bits. Both formulas have the variables

- f_{x,t} for each of their pigeons x and t ∈ [l] (the pigeon row f_x: the hole of x),
- g_{h,j} for every hole h and j ∈ [l + 1] (the hole row g_h: a pigeon code),

and, for each of their pigeons x, every hole h and every j ∈ [l + 1], the clause

  C_{x,h,j} = (f_{x,0} ≠ h_0) ∨ … ∨ (f_{x,l−1} ≠ h_{l−1}) ∨ (g_{h,j} = x_j),

of width l + 1. So WLP_n has v = 2nl + n(l + 1) = n(3l + 1) variables and |J| = 2n²(l + 1) clauses. LP_{n+1} has
(n + 1)l + n(l + 1) variables and (n + 1)n(l + 1) clauses.

**Theorem (W).** Let l ≥ 20, k = ⌊n/(64 l³)⌋. Every dag-like Res(⊕) refutation of WLP_n with S lines satisfies
3S + 2n²(l + 1) ≥ exp(0.005·k/l²). The same holds for every dag-like Res(⊕) refutation of LP_{n+1}. Hence S ≥ exp(Ω(n/log⁵ n)), and the
bound exceeds the trivial 2n²(l + 1) from l = 48 on (n = 2^48); below that it says nothing.

(The constant 0.005 is loose: the density reviewer proved 0.0238 for every l ≥ 20, which makes the bound non-trivial from l = 45. The
statement keeps 0.005 and drops the earlier "− 1", which was slack.)

## 2. What is used from Braun (arXiv 2609.23015, revision at commit 8904bf09)

| # | Result (label in his LaTeX) | Lean declaration | Used for | Hypotheses as used |
| --- | --- | --- | --- | --- |
| B1 | Generic criterion and density form (thm:generic, cor:generic-density) | `generic_CNF_subspace_criterion`, `generic_CNF_density_bound_simple` | the size bound from a separated space (step 6) | any clause set with a covering family of width ≤ w; `old` ⊇ Booleanity and the covering clause polynomials; h, k ≥ 1; h(k+1)+1 ≤ v; U of degree ≤ k with no nonzero element derivable at B = k(max(2h+w, 4h+1)+1) |
| B2 | Substitution and fixed-weight replay (lem:substitution) | `PolynomialCalculusSubstitution` | σ in step 3 | substituted polynomials of degree ≤ T = l; axiom images derivable through T·B |
| B3 | Boolean reduction (lem:boolean) | `BooleanReduction` | axiom images in step 3 | none |
| B4 | Multiplying a completed line (lem:pc-product) | `PolynomialCalculusReuse` | Ideal ⊆ Cons; q·Ideal_d ⊆ Ideal_{d+deg q} | none |
| B5 | Degree-preserving decoder transfer (lem:decoder) | `compactDecoder_PC` | τ in step 3 | any m, l ≥ 2 |
| B6 | Stability (cor:stability) | `functionalUnary_pc_eq_ns`, `functionalUnary_ns_stable` | step 3 | any m, N ≥ 1, 2B′ − 1 ≤ N, k ≤ B′ |
| B7 | Moment extension (thm:moments) | `matching_normalized_annihilator` | step 4 | any m, N ≥ 1, 2B′ − 1 ≤ N |
| B8 | Binary cube degree drop (lem:cube-drop) | `cubeDifference_ns` | step 4 | each source variable tagged with one coordinate (scalar depending only on it) or untagged with an image of degree ≤ 1; every generator's image is the same in every branch and is 0 or a target generator |

**Coverage by the replay.** All eight declarations are in the import closure of `claims/BitPHPPreprintRevision1.lean`, the aggregate
whose build, axiom report and fresh-kernel replay (`leanchecker --fresh`) passed in `BPHP-RES-PARITY-AUDIT-20261019-001A` (the aggregate
imports `GenericCNFDensityBound`, so the generic criterion was replayed too, not only the main theorem). The earlier audit's definitional
review (`…001B`) covered the Res(⊕) proof system and the main theorem's statement, which B1 shares (`AffineDAG`, `Fin S` lines). For
B1, B5, B6, B7 and B8 the Lean statements were read for this audit and match the uses above; in particular B5–B7 hold for every number of
rows m, so 2n pigeons are covered, and B8 is stated for an arbitrary tagging, so a cube whose coordinates are hole rows is covered.

**Not covered by any formal check.** Steps 2–7 below, written by this program: the transfer, the reduction (with its one-row
interpolation), the spare-row cube and its coefficient isolation, and the density count. Braun's row-cube lemma (lem:row-cube) is not used:
its cube has only pigeon coordinates.

## 3. Step 1: the transfer to n + 1 pigeons

The codes 0, …, n of LP_{n+1} are elements of {0,1}^{l+1} (n + 1 > 2^l needs l + 1 bits, and n ≤ 2^{l+1} − 1), so LP_{n+1}'s pigeons
are a subset of WLP_n's. Its pigeon rows f_x are WLP_n's rows for the same x, with the same l bits; its hole rows g_h are WLP_n's, with the
same l + 1 bits; and its clause C_{x,h,j} is, symbol for symbol, WLP_n's clause C_{x,h,j}. So var(LP_{n+1}) ⊆ var(WLP_n) and
LP_{n+1} ⊆ WLP_n as clause sets. A dag-like Res(⊕) refutation of LP_{n+1} uses only axioms from LP_{n+1}, so it is, line for line, a
refutation of WLP_n (in Braun's formal system the leaves are clauses of the set I, and enlarging I keeps every derivation valid). Hence
S(LP_{n+1}) ≥ S(WLP_n). No restriction is needed: both formulas use (l + 1)-bit hole rows and the same clause shape.

## 4. Step 2: the polynomial objects

- **The system.** F_WLP = {u² − u : every variable u} ∪ {P_{x,h,j}}, P_{x,h,j} = [f_x = h]·(g_{h,j} + x_j), [f_x = h] = Π_t (1 + f_{x,t} + h_t).
  P_{x,h,j} is the clause polynomial of C_{x,h,j} in B1's sense (the literal f_{x,t} ≠ h_t has true-indicator f_{x,t} + h_t, the literal
  g_{h,j} = x_j has 1 + g_{h,j} + x_j). Cons_B and Ideal_B are as in Braun §2.
- **The unary system** F^fun_{2n,n}: cells X_{y,z} (pigeon y, hole z), Booleanity, row and column exclusions, row sums ρ_y − 1.
- **The decoder** τ̃: f_{x,t} ↦ β_{x,t} = Σ_{z : z_t = 1} X_{x,z}, g_{h,j} ↦ γ_{h,j} = Σ_{y : y_j = 1} X_{y,h}.
- **Row-linear space** L_k: monomials of degree ≤ k with at most one variable per row (pigeon rows of l variables, hole rows of l + 1).
- **Kernel** K_k = {p ∈ L_k : τ̃(p) ∈ Ideal_k(F^fun_{2n,n})}.

## 5. Step 3: the reduction

**Lemma 1.** Let l ≥ 2, B ≥ 2, 0 ≤ k ≤ lB and 2lB − 1 ≤ n. If p ∈ Cons_B(F_WLP) has degree ≤ k, then τ̃(p) ∈ Ideal_k(F^fun_{2n,n}).

*Proof.* Let Q_{2n,l} be Braun's compact base on the 2n pigeon rows (Booleanity of the f bits and the collisions
E_{xy} = Π_t (1 + f_{x,t} + f_{y,t}), x ≠ y). Let σ fix every f_{x,t} and send g_{h,j} ↦ Σ_y y_j·[f_y = h] (degree l).

(a) *Axiom images.* σ(f² − f) = f² − f. Over GF(2), σ(g_{h,j}² − g_{h,j}) = Σ_y y_j([f_y = h]² − [f_y = h]), which lies in
Ideal_{2l}(Bool) by B3. And σ(P_{x,h,j}) = Σ_{y ≠ x} y_j [f_x = h][f_y = h] + x_j([f_x = h]² − [f_x = h]). The last term is in
Ideal_{2l}(Bool) by B3. For y ≠ x, [f_x = h][f_y = h] − [f_x = h]·E_{xy} has degree ≤ 2l and vanishes at every Boolean point (where
f_x = h, both factors read [f_y = f_x]), so it is in Ideal_{2l}(Bool) by B3, and [f_x = h]·E_{xy} is a legal multiple of a generator at
degree 2l. So every axiom image is in Ideal_{2l}(Q_{2n,l}) ⊆ Cons_{2l}(Q_{2n,l}) (B4), and 2l ≤ lB because B ≥ 2.

(b) *Replay.* By B2 with T = l (every substituted polynomial has degree ≤ l; an axiom of degree ≤ B has its image derivable through
2l ≤ lB), σ(p) ∈ Cons_{lB}(Q_{2n,l}). By B5 (l ≥ 2, any m), τσ(p) ∈ Cons_{lB}(F^fun_{2n,n}), and by B6 (N = n ≥ 2lB − 1) this is
Ideal_{lB}(F^fun_{2n,n}).

(c) *One-row interpolation.* For a pigeon y and a hole h, R = τ([f_y = h]) = Π_t (1 + h_t + Σ_{z : z_t=1} X_{y,z}) is a polynomial in
row y of degree l. Booleanity and the row-y exclusions reduce it, with legal multiples of degree ≤ l, to c + Σ_z c_z X_{y,z}; the constant
c becomes Σ_z c X_{y,z} through c(ρ_y − 1), of degree 1. Every generator used vanishes at the one-hot point e_z of row y, where R equals
[z = h]; so the linear form is X_{y,h} and τ([f_y = h]) − X_{y,h} ∈ Ideal_l(F^fun_{2n,n}). Hence τσ(g_{h,j}) − γ_{h,j} =
Σ_y y_j(τ([f_y = h]) − X_{y,h}) ∈ Ideal_l, and τσ(f_{x,t}) = β_{x,t} exactly.

(d) *Telescoping.* For a monomial u_1⋯u_s of p (s ≤ k), τσ(Π u_i) − τ̃(Π u_i) = Σ_i τσ(u_1)⋯τσ(u_{i−1})·(τσ(u_i) − τ̃(u_i))·τ̃(u_{i+1})⋯τ̃(u_s).
The i-th term is an element of Ideal_l times a polynomial of degree ≤ l(i − 1) + (s − i), so by B4 it lies in Ideal_{ls} ⊆ Ideal_{lB}.
Thus τ̃(p) ∈ Ideal_{lB} and deg τ̃(p) ≤ k ≤ lB, so τ̃(p) ∈ Ideal_k by B6. ∎

(The earlier proof stated k ≤ B; k ≤ lB is all that is used.)

## 6. Step 4: the spare-row lemma

**Stars.** A hole star with centre q ∈ {0,1}^l is {q} ∪ {q + e_i : i ∈ [l]}; a pigeon star with centre c ∈ {0,1}^{l+1} is
{c} ∪ {c + e_j : j ∈ [l + 1]}. Fix k pairwise disjoint pigeon stars (union P) and a family of pairwise disjoint hole stars with union E
(the theorem takes 2k of them; k suffice). Let U_0 ⊆ L_k be spanned by the row-linear monomials of degree ≤ k that use no pigeon row f_y
with y ∈ P and no hole row g_z with z ∈ E.

**Lemma 2.** If n ≥ 2k + 1 and at least k hole stars are fixed, then U_0 ∩ K_k = {0}.

*Proof.* Let p ∈ U_0 be nonzero of degree t ≤ k and M_0 a monomial of p of degree t. Its variables are f_{x,a_x} for x in a set A of
pigeons and g_{h,b_h} for h in a set H of holes, |A| + |H| = t, one per row, all rows outside P and E. Assign distinct stars: to each
x ∈ A a hole star, with z⁰_x = its centre q and z¹_x = q + e_{a_x}; to each h ∈ H a pigeon star, with y⁰_h = its centre c and
y¹_h = c + e_{b_h}, and a further hole star whose centre is the parking hole e_h. This needs t ≤ k hole stars and |H| ≤ k pigeon stars.
The selected rows are A ∪ {y⁰_h, y¹_h}, the selected columns {z⁰_x, z¹_x} ∪ H ∪ {e_h}; they are pairwise distinct (A ∩ P = ∅,
H ∩ E = ∅, distinct stars are disjoint).

For ε ∈ {0,1}^{A ∪ H} let φ_ε set: X_{x, z^{ε_x}_x} = 1 and X_{x, z^{1−ε_x}_x} = 0 (tagged with x); X_{y^{ε_h}_h, h} = X_{y^{1−ε_h}_h, e_h} = 1
and X_{y^{1−ε_h}_h, h} = X_{y^{ε_h}_h, e_h} = 0 (tagged with h); every other cell in a selected row or a selected column = 0 (untagged,
image 0); every remaining cell = itself (untagged, image of degree 1). Then:

- *Generators (B8's hypothesis).* In every branch each selected row has exactly one 1, in a selected column, and each selected column has
  exactly one 1. So Booleanity of a set cell, every exclusion with a set or zeroed cell, and the row sum of a selected row map to 0; the
  row sum of a residual row, and the generators among residual cells, map to the corresponding generator of F^fun_{m′,n′} on the residual
  rows and columns (m′ = 2n − |A| − 2|H|, n′ = n − 2t), because the cells they lose are 0 in every branch. None depends on ε.
- *The images of the decoder's linear forms.* For x ∈ A, β_{x,a} ↦ bit a of z^{ε_x}_x, which is q_a + ε_x if a = a_x and the constant
  q_a otherwise. For h ∈ H, γ_{h,b} ↦ bit b of y^{ε_h}_h, which is c_b + ε_h if b = b_h and c_b otherwise. For any other row of U_0
  (a pigeon row outside A ∪ P, a hole row outside H ∪ E) the form β or γ maps to a linear form in residual cells only, independent of ε
  (its cells in selected columns, respectively selected rows, are 0). Rows in P or E, whose forms would depend on ε (a parked pigeon's
  bits, the bits of a pigeon sitting in z⁰_x or e_h), do not occur in U_0.
- *Coefficient isolation.* So for a monomial M of p, φ_ε(τ̃(M)) is a product of factors each depending on at most one coordinate, and at
  most one factor depends on each coordinate (M has at most one variable per row, and only the selected bit of a selected row depends on
  its coordinate). If some coordinate has no factor, summing over that coordinate cancels M in pairs. Otherwise M contains all t selected
  bits, so M = M_0 (deg M ≤ t), and Σ_ε Π (base + ε_r) = Π_r 1 = 1. Hence Δτ̃(p) = Σ_ε φ_ε(τ̃(p)) = 1.

If τ̃(p) ∈ Ideal_k(F^fun_{2n,n}), B8 gives 1 = Δτ̃(p) ∈ Ideal_{k−t}(F^fun_{m′,n′}). But n′ = n − 2t ≥ max(1, 2(k − t) − 1) because
n ≥ 2k + 1, so B7 gives a normalized functional on F^fun_{m′,n′} annihilating Ideal_{k−t}, a contradiction. So τ̃(p) ∉ Ideal_k and
p ∉ K_k. ∎

**Why 2n pigeons.** The pigeon pair y¹_h = c + e_{b_h} must be a pigeon for every direction b_h ∈ [l + 1]. With 2n pigeons every
(l + 1)-bit code is one; with n + 1, a top-bit direction from a centre below n leaves the pigeons (`KERNEL-FRAC-20261110-001A` shows the
route then certifies only a constant).

## 7. Step 5: separation, and step 6: the count

**Separation.** Take k = ⌊n/(64l³)⌋ ≥ 1 (l ≥ 20), h the largest integer with 2lk(4h + 2) ≤ n + 1, w = l + 1, B = k(4h + 2). Then
h ≥ (n + 1)/(8lk) − 3/2 ≥ 8l² − 3/2, so 2h + w ≤ 4h + 1 and B = k(max(2h + w, 4h + 1) + 1), as B1 requires; 2lB − 1 ≤ n; B ≥ 2;
k ≤ B. If p ∈ U_0 ∩ Cons_B(F_WLP), Lemma 1 puts p in K_k, and Lemma 2 gives p = 0. So U_0 is separated at degree B.

**Stars exist.** A linear code of length L whose parity-check matrix has L distinct nonzero columns in GF(2)^r, r = ⌈log₂(L + 1)⌉, has
distance ≥ 3 and 2^{L−r} ≥ 2^L/(2L + 1) words. With L = l this gives ≥ n/(2l + 1) ≥ 2k hole centres, with L = l + 1 at least
2n/(2l + 3) ≥ k pigeon centres, at pairwise distance ≥ 3, so the stars are disjoint (check 3).

**The count.** Let s = k·l(l + 2) + 2k(l + 1)² be the variables in the stars. Choosing k variables from distinct rows outside the stars
one at a time leaves at least v − s − i(l + 1) choices at step i, so dim U_0 ≥ e_k ≥ Π_{i<k}(v − s − i(l + 1))/k!. With
k!·C(v + k, k) = Π_{i=1}^{k}(v + i) and log(1 − x) ≥ −2x for x ≤ 1/2,

  log(dim U_0 / C(v + k, k)) ≥ −(2ks + (l + 2)k(k − 1) + 2k)/v ≥ −k(l + 2)/(32l³) − 2k/n,

using 2s/k + (l + 2) = 6l² + 13l + 6 ≤ (2l + 4)(3l + 1) for l ≥ 2 and k ≤ n/(64l³). The gain is
hk²/(v + k) ≥ (k(n + 1)/(8l) − 1.5k²)/(n(3l + 2)) ≥ k/(8l(3l + 2)) − k/(128l⁴). So the exponent is at least k·b(l) with

  l²·b(l) = l/(8(3l + 2)) − (l + 2)/(32l) − 1/(128l²) − 2l²/2^l.

Each term is increasing in l for l ≥ 3 (the first rises, the others fall), so l²·b(l) ≥ l²·b(20) = 0.005165 for every l ≥ 20, with limit
1/24 − 1/32 = 1/96 (check 1).

**Step 6.** B1's density form with U = U_0 gives 3S + |J| ≥ (dim U_0 / C(v + k, k))·exp(hk²/(v + k)) ≥ exp(0.005·k/l²). With
k ≥ n/(64l³) − 1 this is exp(Ω(n/l⁵)) = exp(Ω(n/log⁵ n)). Step 1 gives the same for LP_{n+1}. ∎

## 8. The audit

### 8.1 How it was run

Four fresh reviewers (Claude, the same model as the author, given only the statements, the definitions and Braun's sources, and told not
to open the earlier proof) attacked one step each: the spare-row lemma, the density count, the reduction with the transfer, and the
literature. Each wrote its own derivation and its own code. The author re-derived the whole proof (§§3–7) and rewrote the numeric checks
from scratch.

### 8.2 The steps

| Step | Attack | Outcome |
| --- | --- | --- |
| Transfer (§3) | Write both variable and clause sets literally; does a refutation of the subset refute the superset in Braun's system? | Holds. Containment checked by enumeration for l = 2 to 5 (e.g. 6,336 ⊆ 12,288 clauses at l = 5); Braun's refutations are DAGs from initial clauses, size counts nodes, unused variables are allowed. |
| Reduction (Lemma 1) | Degree accounting in the substitution lemma; the axiom images; one-row interpolation; does B5–B7 hold for m = 2n rows? | Holds, for every polynomial of degree ≤ k (row-linearity is not used). Axiom images checked exactly at l = 2 (all 96 in Ideal_4(Q_{8,2})); interpolation exact for l = 2 to 5; stability with more rows than N + 1 checked at (m, N, B) = (7, 3, 2), (9, 3, 2), (8, 5, 3), (12, 5, 3) and failing, as it should, when 2B − 1 > N. The reviewer instantiated Braun's Lean lemmas at m = 2·2^l in a scratch file against his build: it elaborated with only the three standard axioms. No in-range instance is computable: clause axioms enter only at B ≥ l + 1, which with 2lB − 1 ≤ n forces n ≥ 128. |
| Spare-row lemma (Lemma 2) | Do all generators map correctly for every cube shape; does Δτ̃(p) = 1 hold for all n and t ≤ k; corner cases; are the exclusions needed; are 2n pigeons needed? | Holds (C1–C4 all hold). Generators checked in every branch for every shape up to n = 64, k = 4 (786,560 generators); Δτ̃(p) = 1 exactly in the free ring at n = 8, 16, 32 and by random evaluation at n = 64, 128, with negative controls caught; dim(U_0 ∩ K_k) = 0 exactly at k = 1 (n = 8, 16, 32) and k = 2 (n = 16, 32; dim U_0 = 43,932 at n = 32). Without 2n pigeons it fails: with n + 1 the top-bit monomials g_{h,l}g_{h′,l} lie in the kernel (dimension 15 at n = 16, k = 2). |
| Density count (Lemma 3) | Re-derive with explicit constants; numerics at high precision; star existence; Braun's statement and its Lean form; the B93 cap | Holds, with a better constant: 0.0238·k/l² is provable for every l ≥ 20 (0.005 is stated). Numerics at 140 digits for l = 20 to 200 agree with this note's check 2 (e.g. 0.02437·k/l² at l = 20). The bound says nothing below l = 48 (l = 45 with the exact density). The Lean statement has the paper's hypotheses, the constant 3 and \|J\|. |

**One presentation gap, no failing step.** The earlier proof's Lemma 2 assumed its stars and listed side conditions (2k(l + 1) ≤ n,
k(l + 2) ≤ 2n, n ≥ 2k − 1) that do not imply the stars exist: at l = 8 and k = 13 or 14 all three hold but 2k disjoint hole stars do
not fit (Delsarte's bound gives A(8, 3) ≤ 25). The lemma is still true as stated, since it presupposes the stars, and the theorem proves
existence separately in its range (greedy there, a linear code here). The conditions were redundant, and n ≥ 2k + 1 (for n′ ≥ 1 at t = k)
was left implicit. This note states Lemma 2 with k hole stars and n ≥ 2k + 1; nothing else changes. Not a correction: no published claim
used the side conditions to build the stars.

**The cap (B93) does not bind,** and cannot: a PC refutation of degree d caps the density form at exp(d²/(36v)), and the separation at B
already forces d ≥ B + 1 ≈ n/(2l), about l times the degree that would contradict the bound (check 4; the density reviewer derived the
sharper cap exp(B²/(96(v + k))), with the same conclusion). The cap killed the count's route because the count's PC degree is O(√n); here
the degree is nearly linear.

### 8.3 Known upper bounds

None contradicts the bound. Tree-like resolution refutes bit PHP, hence the 2n-pigeon formula and LP_{n+1}, in size 2^{O(n)}
(Dantchev, Galesi, Ghani and Martin, SICOMP 2024), which caps any exponent at linear. Buss–Pitassi's subexponential resolution
refutations need exponentially many pigeons and the unary encoding. The quasi-polynomial refutations of rWPHP_n are in systems Res(⊕) is not
known to simulate: narrow random resolution (Pudlák–Thapen, Prop. 3.5), Res(log) through the unary weak pigeonhole principle, and unary
Sherali–Adams (PPADS^dt). No polynomial-calculus refutation of degree o(n/log n) of any of these formulas is known; known degree lower
bounds are linear.

### 8.4 Novelty (this changes the earlier claim)

- **The formula is known.** WLP_n is exactly Pudlák and Thapen's retraction weak pigeonhole principle rWPHP_n ("Random resolution
  refutations", CCC 2017; *Comput. Complexity* 28, 2019, §3.3: bits of f(x) for x < 2n and of g(y) for y < n, clauses
  f(x) = y → (g(y))_i = x_i), with resolution width ≥ n (their Prop. 3.4). The search problem appears also as Lossy-Code (Korten) and
  WPHP-witnessing (Jeřábek).
- **A stronger bound follows from Pang (2026).** Shuo Pang, "A degree–size relation for resolution over polynomials", arXiv 2610.00837
  (v1 30 September 2026, v2 24 October 2026; unrefereed, AI-assisted per its disclosure), proves for Res(⊕) that a constant-width CNF
  with no F₂-PC refutation of degree D ≥ 32w needs size exp(Ω(D²/n)) (Corollary 1.3), and exp(Ω(N)) for bit PHP with N < m = O(N)
  pigeons (Theorem 7.2(e)), by the affine substitution x_{i,t} ↦ Σ_{v ∈ N_G(i), v_t = 1} X_{i,v} into graph FPHP on a bounded-degree
  boundary expander. The same substitution with g_{h,j} ↦ Σ_{y ∈ N_G(h), y_j = 1} X_{y,h} (this note's decoder τ̃, applied to proof
  lines rather than to polynomials) sends each clause C_{x,h,j} to a disjunction of affine equations implied by the graph-FPHP constraints
  on pigeon x's row and hole h's column, O(1) variables when both degrees are bounded. So a size-S Res(⊕) refutation of rWPHP_n or of
  LP_{n+1} gives one of graph FPHP with O(n) pigeons of size O(S), and Pang's Theorem 7.2(d)–(e) argument gives S ≥ exp(Ω(n)). No
  source states this for rWPHP or LeftPigeon; the derivation is the literature reviewer's, rechecked here against Pang's text, and it
  rests on Pang's theorem and Mikša–Nordström's degree bound for graph FPHP. It is stronger than Theorem (W) by the factor log⁵ n in the
  exponent and needs neither Braun's criterion nor the spare-row cube.
- **The bit-PHP corollary is known and stronger.** A bound for rWPHP_n implies one for bit PHP with 2n pigeons, which Pang's
  Theorem 7.2(e) already gives at exp(Ω(n)); ECCC TR26-316 (Alekseev, Gryaznov, Itsykson, Pitassi, Robere, Tzameret, 10 November 2026,
  Theorem 3.2) gives 2^{Ω(n²/(m l²))} for every m > n in semantic ΣΠΣ-PC, and re-proves Braun's theorem.
- **Attribution.** Göös et al. (*J. ACM* 2024) call the PPADS^dt-complete problem Reversible-Pigeon, citing Göös et al., "Further
  collapses in TFNP" (CCC 2022), Lemma 1, where it is inj-PHP; the name LeftPigeon is Buss and Johnson's. LeftPigeon's PPADS^dt-completeness
  is folklore (Bonacina–Thapen, ECCC TR22-089, Prop. 2.6). The 2n-pigeon formula itself is not known to be PPADS-complete; the PPADS
  statement is for LP_{n+1}, through §3.
- **What remains of the contribution.** A second, longer route to a weaker bound, through Braun's generic criterion: the first separated
  space of useful density for a formula other than bit PHP (Braun's Remark 9.3 asked for one), as far as found. That is a statement about
  the criterion, not a new lower bound.

## 9. Checks

`check.py` (run with the workspace venv for mpmath; written independently of the earlier proof's check script):

| # | Check | Result |
| --- | --- | --- |
| 1 | l²·b(l) increasing from l = 3 to 1,000 (exact rationals); value at 20 | pass: 0.005165 at l = 20, limit 1/96 |
| 2 | Parameters, B1's and Lemmas 1–2's side conditions, and the exponent's lower bound against 0.005·k/l², l = 20 to 200 at 80 digits; dim U_0 exactly for l = 20 to 30 | pass: the left side is 4.9 to 5.2 times 0.005·k/l²; first non-trivial l = 48 |
| 3 | The code construction: distance ≥ 3 by enumeration for lengths 3 to 12; enough centres for l = 20 to 1,000 | pass |
| 4 | The degree cap (`RES-XOR-COUNT-20261110-001A`): the PC degree that would contradict the bound, against B | pass: B is 109 to 1,088 times larger |
| 5 | Minimum parity decision trees at n = 2, exhaustively (`pdt.c`) | WLP_2: 8 leaves, depth 3; LP_3: 10 leaves, depth 4; bit PHP 3→2 and 4→2: 6 leaves, depth 3 |

Check 5 is a sanity check only: l = 1 is far outside the theorem (l ≥ 20, and the bound says nothing below l = 48), and n = 4 already has
28 variables, beyond exhaustive search; it confirms only that the superset WLP_2 is no harder than LP_3.

## Nonclaims

- **Not an independent human review.** The re-derivation is by the earlier proof's author; the reviewers are fresh instances of the same
  model. A proof-complexity expert's reading is still needed before the result counts.
- **Conditional on A55.** Braun's results B1–B8 are cited; their Lean proofs were replayed in a fresh kernel in October, and their
  statements were read against the use here, but the preprint is unrefereed.
- **Nothing transfers to the knot sphere's count** or to other encodings of PPADS-complete problems (Res(⊕) is not closed under
  decision-tree reductions).
