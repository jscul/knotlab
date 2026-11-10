# Separation through the decoder's kernel

Status: Proved by hand from Braun's decoder transfer and stability corollary (arXiv 2609.23015, §§3–4, cited; formalized in Lean in his
repository, audited in `BPHP-RES-PARITY-AUDIT-20261019-001`). The ingredient identities are checked in `check.py`.

Ticket `HOLE-SEP-20261110-001A`, 2026-11-10. The statement was frozen first in
`research/HOLE-SEP-20261110-001/separation_statement.md` (commit 0596397e3) as (R).

## Standard statement

- **LP_n, Q_{m,l}, L_k, Lemma 1** as in `SEP-LEFT-20261110-001A`: n = 2^l holes (l ≥ 2), m = n + 1 pigeons, pigeon rows f_x of l bits,
  hole rows g_h of l + 1 bits, axioms [f_x = h]·[g_h,j ≠ x_j]; the substitution g(h) := G(h) = Σ_x [f_x = h]·x.
- **Braun's unary system** F^fun_{m,n}: cells X_x,h, Booleanity, row and column exclusions, row sums ρ_x = Σ_h X_x,h = 1; Ideal_k its
  degree-k Nullstellensatz span, Cons_B its degree-B PC consequences; his decoder τ(b_x,t) = Σ_{z : z_t = 1} X_x,z.
- **The reduced decoder** τ̃ on row-linear monomials: a pigeon bit f_x,t goes to β_x,t = Σ_{z : z_t = 1} X_x,z, a hole bit g_h,j to the
  weighted hole sum γ_h,j = Σ_y y_j X_y,h, a monomial to the product. **The kernel** K_k = {p ∈ L_k : τ̃(p) ∈ Ideal_k(F^fun_{m,n})}.

**Theorem (R).** Let l ≥ 2, B ≥ 2, k ≤ B and 2lB − 1 ≤ n. If p ∈ L_k lies in Cons_B(LP_n), then p ∈ K_k. Hence every subspace U of L_k
with U ∩ K_k = {0} is separated from LP_n at degree B.

**Proposition (the known kernel).** For each hole bit j ≤ l and each affine function a of the hole label (a = 1, or a = h_t for t < l),
the inverse-counting identity κ_{a,j} = Σ_h a(h)·g_h,j + Σ_x x_j·a(f_x), with a(f_x) = 1 or f_x,t (for a = 1 the second sum is the
constant c_j), lies in K_1. The (l + 1)² identities are independent.

## Nearest known result

- **Braun's §4** proves row-linear separation for bit PHP with a cube argument through the decoder, and his §3 proves, through chessboard
  homology, that below degree n/2 the unary system's PC consequences are its Nullstellensatz span and that low-degree consequences have
  low-degree certificates (Corollary on old filtration stability). Theorem (R) combines these with `SEP-LEFT-20261110-001A`'s Lemma 1;
  the delta is that, for the left-pigeon principle, the separation question becomes the static kernel K_k.
- **Classification.** New as far as found, and elementary given Braun's lemmas.

## Proof

**Theorem (R).** Let p ∈ L_k ∩ Cons_B(LP_n).
1. *Substitution.* By `SEP-LEFT-20261110-001A`'s Lemma 1, p(f, G) ∈ Cons_{B′}(Q_{m,l}) with B′ = max(lB, 2l) = lB.
2. *Decoding.* By Braun's degree-preserving transfer (his Lemma on the old-base transfer, for l ≥ 2), τ(p(f, G)) ∈ Cons_{B′}(F^fun_{m,n}).
3. *Stability.* Since n ≥ 2B′ − 1, Braun's stability corollary gives Cons_{B′}(F^fun) = Ideal_{B′}(F^fun) and
   Ideal_{B′} ∩ Pol_{≤k′} = Ideal_{k′} for every k′ ≤ B′.
4. *Reduction to τ̃.* Modulo Ideal_1, τ([b_x,t = h_t]) is Σ_{z : z_t = h_t} X_x,z (one row-sum relation when h_t = 0), and the product of
   these over t reduces, by row exclusions and Booleanity, to the single cell X_x,h: so τ([f_x = h]) ≡ X_x,h modulo Ideal_l, and
   τ(G(h)_j) ≡ γ_h,j modulo Ideal_l (checks 1 and 2). For a row-linear monomial with a pigeon bits and b hole bits, a + b ≤ k, multiply the
   b congruences: each error is a degree-l certificate times a polynomial of degree at most l(b − 1) + a, so
   τ(p(f, G)) ≡ τ̃(p) modulo Ideal_{lk} ⊆ Ideal_{B′}.
5. So τ̃(p) ∈ Ideal_{B′} ∩ Pol_{≤k} = Ideal_k, that is p ∈ K_k. ∎

**Proposition.** Σ_h a(h)·γ_h,j = Σ_x x_j Σ_h a(h) X_x,h. For a = h_t the inner sum is β_x,t = τ̃(f_x,t), so τ̃(κ_{a,j}) = 0. For a = 1 it is
ρ_x, and Σ_x x_j (ρ_x − 1) ∈ Ideal_1, so τ̃(κ_{1,j}) ∈ Ideal_1. The identities have different hole-row coefficient patterns, hence are
independent. Check 3 confirms both for n = 4, 8, 16, 32. ∎

## What the kernel means

Under the substitution, κ_{a,j} says that summing a(h)·g(h)_j over the holes equals summing a(f(x))·x_j over the pigeons: true when g is
the inverse of f on its image and every other hole is empty. It is not a consequence of LP_n (`SEP-LEFT-20261110-001B` finds L_1 fully
separated at every degree read), but the substitution, which empties every hole no pigeon names, makes it one, so the route through τ̃
cannot separate it. `HOLE-SEP-20261110-001B` reads how far this reaches at degree 2 and 3.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | τ([f_x = h]) reduces to X_x,h modulo Ideal_l, every x and h, n = 4, 8 | pass |
| 2 | τ(G(h)_j) reduces to γ_h,j, n = 4, 8 | pass |
| 3 | The (l + 1)² inverse-counting identities lie in K_1 and are independent, n = 4, 8, 16, 32 | pass |

## Nonclaims

- **No bound on dim K_k** is proved here; Theorem (R) turns separation into that question.
- **Braun's lemmas are cited**, not reproved.
- **Nothing here reaches the knot sphere's count.**
