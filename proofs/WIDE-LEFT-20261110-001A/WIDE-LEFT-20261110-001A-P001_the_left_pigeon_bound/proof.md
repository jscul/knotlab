# A dag-like Res(⊕) lower bound for the binary left-pigeon principle

Status: Proved by hand from Braun's lemmas (arXiv 2609.23015, cited; formalized in Lean in his repository and audited in
`BPHP-RES-PARITY-AUDIT-20261019-001`), with the numbers checked in `check.py` and the spare-row lemma checked on small instances by
`WIDE-LEFT-20261110-001B`. Not externally reviewed.

Ticket `WIDE-LEFT-20261110-001A`, 2026-11-10. The target and its steps were frozen first in
`research/WIDE-LEFT-20261110-001/target_statement.md` (ca1f7e64e), after the novelty and transfer check in `novelty_and_transfer.md`
(4784c56f6).

## Standard statement

- **The formulas.** n = 2^l holes. WLP_n has 2n pigeons with rows f_x of l bits (the hole of x) and n hole rows g_h of l + 1 bits (a
  pigeon's code; with 2n pigeons every code names one), and the clauses "f_x ≠ h or g_h,j = x_j" for every pigeon x, hole h and bit j:
  v = 2nl + n(l + 1) variables, |J| = 2n²(l + 1) clauses, each a linear clause of width l + 1. LP_{n+1} is the same with pigeons
  x ≤ n: the binary left-pigeon principle, whose search problem is PPADS-complete (`COUNT-SYSTEMS-20261110-001A`).
- **Res(⊕), PC, Braun's system and lemmas** as in `HOLE-SEP-20261110-001A`: the unary functional system F^fun_{m,N} (cells X_x,h,
  Booleanity, row and column exclusions, row sums ρ_x = 1), its degree-B Nullstellensatz span Ideal_B, the reduced decoder τ̃ (f_x,t to
  β_x,t = Σ_{z : z_t = 1} X_x,z, g_h,j to γ_h,j = Σ_y y_j X_y,h) and the kernel K_k ⊆ L_k.

**Theorem (W).** Let l ≥ 20 and k = ⌊n/(64 l³)⌋. Every dag-like Res(⊕) refutation of WLP_n with S lines satisfies
3S + 2n²(l + 1) ≥ exp(0.005·k/l² − 1), so S ≥ exp(Ω(n / log⁵ n)). The same holds for every refutation of LP_{n+1}.

## Nearest known result

- **Braun (2026)** proves exp(Ω(n/l²)) for bit PHP with n + 1 pigeons (extended to more pigeons in
  `HOLE-CRITERION-COLOURING-20261019-001B`). WLP_n derives bit PHP's collision clauses in one resolution step each, so (W) is
  stronger than a bound for bit PHP with 2n pigeons and does not follow from Braun's (`novelty_and_transfer.md`).
- **Other Res(⊕) bounds** (Efremenko, Garlík and Itsykson, regular, bit PHP; Byramji and Impagliazzo, depth-restricted, weak bit PHP;
  the lifting line) are for bit PHP or lifted formulas.
- **Classification.** New as far as found: no Res(⊕) bound of any kind for left-pigeon, injective-with-retraction or PPADS-complete
  principles was found (searches of 2026-11-10). Known-with-delta in technique: every step uses Braun's machinery, and the new pieces are
  the substitution (`SEP-LEFT-20261110-001A`, Lemma 1), Theorem (R) (`HOLE-SEP-20261110-001A`), the spare-row cube (Lemma 2 below) and
  the density count. It inherits the status of Braun's preprint, unrefereed but Lean-formalized and audited here.

## Proof

**Lemma 1 (R′).** If B ≥ 2, k ≤ B and 2lB − 1 ≤ n, every p ∈ L_k with p ∈ Cons_B(WLP_n) has τ̃(p) ∈ Ideal_k(F^fun_{2n,n}).
*Proof.* As Theorem (R) of `HOLE-SEP-20261110-001A`, with 2n pigeons: the substitution g(h) := Σ_x [f_x = h]·x sends each axiom to a sum
of collisions [f_x = h][f_x′ = h], members of Ideal_{2l} of Braun's compact base Q_{2n,l}, and lines of degree B to degree lB
(`SEP-LEFT-20261110-001A`, Lemma 1, whose argument does not use the number of pigeons); Braun's degree-preserving transfer (any m,
l ≥ 2) and his stability corollary (any m, N = n ≥ 2lB − 1) then give τ̃(p) ∈ Ideal_{lB} ∩ Pol_{≤k} = Ideal_k, since τ([f_x = h]) ≡ X_x,h
modulo Ideal_l (all n labels are holes). ∎

**Lemma 2 (S, the spare-row lemma).** Let E be the union of 2k pairwise disjoint hole stars {q, q + e_0, …, q + e_{l−1}} and P the union
of k pairwise disjoint pigeon stars {p, p + e_0, …, p + e_l}, and let U_0 be the span of the row-linear monomials of degree at most k on
the rows outside E and P. If 2k(l + 1) ≤ n, k(l + 2) ≤ 2n and n ≥ 2k − 1, then U_0 ∩ K_k = {0}.

*Proof.* Let p ∈ U_0 be nonzero, of degree t, and M_0 one of its monomials of degree t: pigeon bits (x, t_x) for x ∈ A and hole bits
(h, j_h) for h ∈ H, |A| + |H| = t ≤ k, all rows outside E and P. Give each selected bit its own star (at most k pigeon stars are needed and
at most |A| + |H| ≤ 2k hole stars):
- for x ∈ A, a hole star's pair z⁰, z¹ = q, q + e_{t_x}, which differ exactly in bit t_x;
- for h ∈ H, a pigeon star's pair y⁰, y¹ = p, p + e_{j_h}, which differ exactly in bit j_h, and a parking hole e = q of another hole star.

For ε ∈ {0, 1}^t let φ_ε be the substitution: for x ∈ A put x in z^{ε_x} (X_x,z = 1 there, every other cell of row x and of columns z⁰, z¹
zero); for h ∈ H put y^{ε_h} in h and y^{1−ε_h} in its parking hole (those two cells 1, every other cell of rows y⁰, y¹ and of columns h,
e zero); every other cell is left as a variable of the residual system F^fun_{m′,n′}, m′ = 2n − |A| − 2|H|, n′ = n − 2t. A cell in a
selected row of one coordinate and a selected column of another is 0 in every branch, so each substituted value depends on one
coordinate only. Every generator of F^fun_{2n,n} goes to zero or to a generator of the residual system, the same in every branch:
selected rows hold exactly one 1, selected columns at most one, and residual rows and columns lose only cells that are 0. By Braun's
binary cube degree-drop lemma, Δ = Σ_ε φ_ε maps Ideal_k(F^fun_{2n,n}) into Ideal_{k−t}(F^fun_{m′,n′}).

Now apply Δ to τ̃(p) monomial by monomial. Under φ_ε:
- β_x,t for x ∈ A becomes the bit t of z^{ε_x}: it depends on ε_x exactly when t = t_x;
- γ_h,j for h ∈ H becomes the bit j of y^{ε_h}: it depends on ε_h exactly when j = j_h;
- every other factor of a monomial of U_0 (a pigeon or hole row outside the selected ones, and outside E and P) becomes a residual linear
  form that does not depend on ε, since its cells in selected rows and columns are 0 in every branch.
So a monomial of p that lacks some selected bit is independent of that coordinate and cancels in pairs over GF(2). A monomial of p that
holds all t selected bits has degree at least t, hence equals M_0, and its image under each φ_ε is the product of the t selected
values; summing over the cube gives Π (0 + 1) = 1. So Δτ̃(p) = 1 exactly.

Since n′ = n − 2t ≥ 2(k − t) − 1, Braun's moment extension gives a normalized functional λ on the residual system annihilating
Ideal_{k−t}. Then μ = λ∘Δ annihilates Ideal_k(F^fun_{2n,n}) and μ(τ̃(p)) = 1, so τ̃(p) ∉ Ideal_k: p ∉ K_k. ∎

(The stars exist: centres at pairwise distance at least 3 give disjoint stars, and greedy choice finds n/(1 + l + C(l, 2)) ≥ 2k hole
centres and k pigeon centres in the range of the theorem; check 3.)

**Lemma 3 (D, the count).** Let l ≥ 20, k = ⌊n/(64 l³)⌋ ≥ 1 and h the largest integer with 2l·k(4h + 2) ≤ n + 1. Then B = k(4h + 2)
meets Lemma 1's condition, D = 4h + 1 ≥ 2h + (l + 1), h(k + 1) + 1 ≤ v, and
log(dim U_0 / C(v + k, k)) + hk²/(v + k) ≥ 0.005·k/l² − 1.
*Proof.* The side conditions are direct (h ≥ (n + 1)/(8lk) − 3/2 ≥ 8l² − 3/2). Write s = k(l + 2)l + 2k(l + 1)² for the variables in the
stars, so the rows outside them carry v − s variables. Choosing k rows one at a time, k!·e_k ≥ Π_{i<k} (v − s − i(l + 1)), and
k!·C(v + k, k) = Π_{i≤k} (v + i), so with 1 − x ≥ e^{−2x} for x ≤ 1/2,
log(dim U_0 / C(v + k, k)) ≥ −(2ks + (l + 2)k(k − 1) + 2k)/v.
With v = n(3l + 1), k ≤ n/(64 l³) and (6l² + 13l + 6)/(3l + 1) ≤ 2l + 4 this loss is at most k(l + 2)/(32 l³) + 2k/n. The gain is
hk²/(v + k) ≥ (k(n + 1)/(8l) − 1.5k²)/(n(3l + 2)) ≥ k/(8l(3l + 2)) − k/(128 l⁴). So the total is at least
k·[1/(8l(3l + 2)) − (l + 2)/(32 l³) − 1/(128 l⁴) − 2/n] ≥ 0.005·k/l² for l ≥ 20 (check 1: the bracket times l² is at least 0.00517 for
l from 20 to 200, and it increases to 1/24 − 1/32 beyond). Check 2 evaluates the left side directly: term by term for l ≤ 32, by the
sequential bound to l = 80. ∎ (The −1 in the statement absorbs rounding at the smallest l.)

**Theorem (W).** By Lemma 1 and Lemma 2, U_0 is separated from WLP_n at degree B (a derived element of U_0 lies in U_0 ∩ K_k = {0}).
Braun's Corollary 9.2, applied to WLP_n with its own clauses as the covering family (width w = l + 1, |J| = 2n²(l + 1)), accuracy h and
this U_0, gives 3S + |J| ≥ (dim U_0 / C(v + k, k))·exp(hk²/(v + k)) ≥ exp(0.005·k/l² − 1) by Lemma 3. With k ≈ n/(64 l³) this is
exp(Ω(n/l⁵)). For LP_{n+1}: its clauses are a subset of WLP_n's (`novelty_and_transfer.md`), so every refutation of LP_{n+1} refutes
WLP_n. ∎

## Remarks

- **Why 2n pigeons.** With n + 1 pigeons the top code bit belongs to one pigeon and the decoder route certifies only a constant
  (`KERNEL-FRAC-20261110-001A`); with 2n every code is a pigeon, and the spare-row cube needs pigeon pairs in every bit direction, which
  only full codes provide.
- **Where the bound takes hold.** k ≥ 1 needs n ≥ 64 l³ (l ≥ 20), and the bound exceeds |J| only for l around 45 and up; it is an
  asymptotic statement.
- **What it says about PPADS.** It is a dag-like Res(⊕) lower bound for a CNF encoding a PPADS-complete search problem, in the binary
  encoding used here. Res(⊕) is not closed under decision-tree reductions, so it is not a statement about every PPADS-complete formula,
  and it says nothing about the knot sphere's count (`RES-XOR-COUNT-20261110-001A`).

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The bracket of Lemma 3 times l², l = 20 to 200 | pass: at least 0.00517 |
| 2 | Lemma 3's side conditions and its inequality, l = 20 to 80 | pass |
| 3 | Star centres: the counting bound, l = 20 to 80; greedy search, l = 8 to 14 | pass |

Lemma 2 on small instances, and its cube identities, are `WIDE-LEFT-20261110-001B`'s checks.

## Nonclaims

- **Braun's lemmas are cited, not reproved;** the theorem is as reliable as his preprint and its formalization.
- **No external review** has been made; this is a V1 proof written in one session.
- **Nothing here transfers to the knot sphere's count** or to other encodings of PPADS-complete problems.
