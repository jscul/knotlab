# What of Braun's bit-PHP argument transfers to bit LeftPigeon

Status: Proved by hand from Braun's theorems (arXiv 2609.23015, cited; formalized in Lean in his repository and audited in
`BPHP-RES-PARITY-AUDIT-20261019-001`). The identities and inequalities are checked in `check.py`.

Ticket `SEP-LEFT-20261110-001A`, 2026-11-10.

## Standard statement

- **Bit PHP** (Braun's compact base Q_{m,l}). n = 2^l holes, m = n + 1 pigeons, pigeon rows b_x of l bits, axioms
  E_xx′ = Π_t (1 + b_x,t + b_x′,t) ("rows x and x′ name the same hole") and the Boolean axioms, over F2.
- **Bit LeftPigeon LP_n.** Pigeon rows f_x (l bits: the hole of pigeon x) and hole rows g_h (l + 1 bits: a pigeon's code), axioms
  A_x,h,j = [f_x = h]·[g_h,j ≠ x_j] for every pigeon x, hole h and bit j, where [f_x = h] = Π_t (f_x,t + 1 + h_t) has degree l. These are
  the clause polynomials of the clauses "f_x ≠ h or g_h,j = x_j" of the left-pigeon principle (pigeons 0, …, n; g(f(x)) = x), a
  PPADS-complete search problem (`COUNT-SYSTEMS-20261110-001A`). LP_n has v = (n + 1)l + n(l + 1) variables.
- **Row-linear spaces.** L_k: polynomials spanned by monomials of degree at most k with at most one bit from each row; over the pigeon
  rows only (L_k^pig) or over all rows (L_k).
- **Cons_B, separation, Braun's generic criterion** (Theorem 9.1 and Corollary 9.2) as in `RES-XOR-COUNT-20261110-001A`.

**Theorem.**
1. **(Lemma 1)** For every polynomial p in the pigeon rows only, p ∈ Cons_B(LP_n) implies p ∈ Cons_{max(lB, 2l)}(Q_{m,l}). With Braun's
   row-linear separation, every nonzero p ∈ L_k^pig is separated from LP_n at every degree B with 2·max(lB, 2l) − 1 ≤ n and
   4(k − 1) < n.
2. **(Theorem 2)** Let l ≥ 4 and k ≤ n/2. If L_k is separated from LP_n at degree k(12l + 2), every dag-like Res(⊕) refutation of LP_n
   with S nodes has 3S + n(n + 1)(l + 1) ≥ exp(k²/(3n) − 2).
3. **(Lemma 3)** Σ_h g_h,j + c_j, with c_j = #{x : x_j = 1} mod 2, lies in L_1 and becomes 0 under the substitution of Lemma 1; for
   l ≥ 2, c_j = 0 for j < l and c_l = 1.
4. **(Lemma 4)** For U = L_k^pig and every k with k(12l + 2) in Lemma 1's range, Braun's density bound is below 1: the pigeon rows alone
   certify nothing.

So B100 comes down to one statement: **row-linear separation of LP_n over all rows at degree k(12l + 2), for some k = ω(√(n log n))**,
which with Theorem 2 gives a superpolynomial dag-like Res(⊕) bound for a PPADS-complete principle, and with k = n/polylog an
exponential one.

## Nearest known result

- **Braun (2026).** The exponential dag-like Res(⊕) bound for bit PHP; its Steps 1 and 2 are generic (his §9), and Step 3, row-linear
  separation through degree about n/2, is specific to bit PHP's base; his Remark 9.3 knows no second formula with a separated space of
  useful density. LP_n is bit PHP with a left inverse added: its clauses imply bit PHP's, so a Res(⊕) bound for LP_n would be strictly
  stronger.
- **His §9 on unary PHP.** The substitution from unary to bit PHP makes affine forms nonlinear, so Theorem 9.1 does not transfer that
  way. Lemma 1 substitutes in the other direction, inside the polynomial calculus, where degree is what matters, so it does transfer;
  it is the counting step, not separation, that it cannot reach (Lemma 4).
- **Classification.** New as far as found: the reduction for this formula to one separation statement, with the small-instance evidence
  of `SEP-LEFT-20261110-001B`. Every step is elementary given Braun's paper.

## Proof

**Lemma 1.** Put G(h)_j = Σ_x [f_x = h]·x_j, a polynomial of degree l in the pigeon rows (x_j is the j-th bit of x's code, a constant).
- *The axioms.* Since [f_x = h]² = [f_x = h] modulo the Boolean axioms, A_x,h,j with g := G becomes
  [f_x = h]·(Σ_{x′} [f_x′ = h]x′_j + x_j) = [f_x = h]·Σ_{x′ ≠ x} [f_x′ = h]x′_j, and [f_x = h][f_x′ = h] = [f_x = h]·E_xx′ modulo the
  Boolean axioms. So every image lies in Ideal_{2l}(Q_{m,l}) (check 1: every pigeon assignment for n = 4, random ones for n = 8, 16).
- *Booleanity of g.* G(h)_j² − G(h)_j = Σ_x x_j([f_x = h]² − [f_x = h]) over F2, in the Boolean ideal within degree 2l.
- *The lines.* A line q(f, g) of degree at most B becomes q(f, G) of degree at most lB. Multiplying a line of degree at most B − 1 by a
  pigeon bit raises its image's degree by one; multiplying by g_h,j becomes multiplying by G(h)_j, of degree l, which Braun's lemma on
  multiplying a completed line (§2) does through degree l(B − 1) + l = lB.
So a derivation of p from LP_n in degree B becomes one of p(f, G) from Q_{m,l} in degree max(lB, 2l); for p in the pigeon rows,
p(f, G) = p. Braun's row-linear separation (his §4: no nonzero f ∈ L_k lies in Cons_B(Q_{m,l}) when 2B − 1 ≤ n and 4(k − 1) < n) then
gives the second sentence. ∎

**Theorem 2.** Apply Braun's Corollary 9.2 to LP_n with the covering family its own clauses: linear clauses of width w = l + 1, |J| =
n(n + 1)(l + 1), whose clause polynomials are the A_x,h,j. With h = 3l, D = max(2h + w, 4h + 1) = 12l + 1 and B = k(D + 1) = k(12l + 2);
the hypothesis h(k + 1) + 1 ≤ v holds for k ≤ n/2. So 3S + |J| ≥ δ·exp(hk²/(v + k)) with δ = dim L_k / C(v + k, k).
- dim L_k is the elementary symmetric sum e_k of the row sizes (n + 1 rows of l bits, n of l + 1). Choosing rows one at a time,
  k!·e_k ≥ Π_{i<k} (v − i(l + 1)), while k!·C(v + k, k) = Π_{i≤k} (v + i); so δ ≥ exp(−((l + 2)k(k − 1) + 2k)/v) for k ≤ n/2.
- With v = 2nl + n + l, l ≥ 4 and k ≤ n/2: v + k ≤ 2.5nl, so hk²/(v + k) ≥ 1.2k²/n, and the loss is at most
  ((l + 2)/(2l))k²/n + 2k/v ≤ 0.75k²/n + 1.
- So 3S + |J| ≥ exp(0.34k²/n − 1) ≥ exp(k²/(3n) − 2). Check 3 confirms the inequality with the exact e_k for l = 4 to 20 and
  k from 1 to n/2 (smallest margin 2 in the logarithm, at small k). ∎

**Lemma 3.** Σ_h [f_x = h] = Π_t ([f_x,t = 0] + [f_x,t = 1]) = 1 as a polynomial, so Σ_h G(h)_j = Σ_x x_j = c_j. Among the codes 0, …,
2^l − 1, exactly 2^{l−1} have bit j set for j < l, and the extra pigeon 2^l has only bit l set (check 2). ∎ These polynomials are
consequences of the substitution, not necessarily of LP_n, so Lemma 1 says nothing about them; `SEP-LEFT-20261110-001B` finds them
separated at every degree read (they lie in L_1 over all rows, separated through degree 3 at n = 4 and at least 4 at n = 8).

**Lemma 4.** For U ⊆ L_k^pig, δ ≤ e_k(l, …, l)/C(v + k, k) with n + 1 rows, about 2^{−k}, while hk²/(v + k) ≤ 1.5k²/n; and Lemma 1
reaches only k(12l + 2) ≤ (n + 1)/(2l), so k ≤ n/(24l²). Check 4 computes the exact bound for l = 2 to 20 and every such k (at least
k = 1): its logarithm is at most −0.57, so the bound is below 1. ∎

## Remarks

- **What is left is Step 3 for the hole rows.** Under Braun's decoder τ to the unary functional PHP (b_x,t ↦ Σ_{z: z_t = 1} X_x,z),
  [f_x = h] ↦ X_x,h and G(h)_j ↦ Σ_x x_j X_x,h: a hole-row bit becomes a weighted hole sum. Separating L_k over all rows needs
  matching-moment functionals that isolate products of such hole sums, as Braun's cube argument isolates products of pigeon sums; his
  moments exist through degree (n + 1)/2. Whether the cube argument adapts is the open step, and Lemma 3's kernel polynomials need it
  most, since the substitution sends them to constants.
- **Why the reduction is worth having.** A row-linear separation theorem for LP_n would give the first dag-like Res(⊕) lower bound for
  a PPADS-complete principle and answer Braun's Remark 9.3. It would not reach the knot sphere's count, whose embedding costs the
  degree (`RES-XOR-COUNT-20261110-001A`, Lemma 1).

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Lemma 1's identity for every axiom: n = 4 on all 1,024 pigeon assignments, n = 8 and 16 on 300 random ones | pass |
| 2 | Lemma 3: Σ_h G(h)_j = c_j on the same assignments | pass |
| 3 | Theorem 2's inequality with exact e_k, l = 4 to 20, k up to n/2 | pass: margin at least 2 |
| 4 | Lemma 4: the pigeon-row bound below 1 on 252 cases, l = 2 to 20 | pass: log bound at most −0.57 |

## Nonclaims

- **No Res(⊕) lower bound for LP_n is claimed**: Theorem 2 is conditional on the separation statement, which is open.
- **Braun's theorems are cited**, not reproved; their Lean formalization is his, audited in `BPHP-RES-PARITY-AUDIT-20261019-001`.
- **Nothing here reaches the knot sphere's count.**
