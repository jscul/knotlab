# Balance cancels the feedback in loops of any length

Status: Proved by hand. The finite claims are checked in `check.py`.

Ticket `LOOP-ANY-20261108-001A`, 2026-11-08.

## Standard statement

- **The loop.** r ≥ 2 rings R_0, …, R_(r−1) of s cells on rule 60, indices mod r. Contact c_i is cell k_i of R_i and cell 0 of
  R_(i+1), with 2 ≤ k_i ≤ s − 2 (`LOOP-RINGS-20261108-001A`, `LOOP-PROOF-20261108-001A`).
- **Chains.** On R_i, F_i runs from c_(i−1) to c_i over f_i = k_i − 1 cells and B_i from c_i back to c_(i−1) over b_i = s − k_i − 1
  cells, so f_i + b_i = s − 2.
- **Laws.** Each contact reads the ends of the two chains arriving at it, F_i's on R_i and B_(i+1)'s on R_(i+1) (law 12, 12), or also
  its two partners (law 6, 6).
- **Balance.** k_0 + … + k_(r−1) = rs/2, equivalently f_0 + … + f_(r−1) = r(s − 2)/2.
- **Condition W.** No law-(6, 6) contact c_j has k_j = s − 2 or k_(j+1) = 2 (`LOOP-PROOF-20261108-001A`).

Over GF(2), write C_i(z) = Σ_T c_i(T) z^T and a = z/(1 + z).

**Theorem 1 (the feedback is a polynomial in a shift).** The contacts satisfy C = S + KC with K = z(A + cA^(−1)). Here A is the
weighted cyclic shift with A_(i, i−1) = a^(f_i), c = a^(s−2) is a scalar, and S collects first values. So A^r = a^F I, with
F = f_0 + … + f_(r−1).

**Theorem 2 (balance cancels the diagonal).** In a balanced loop every diagonal entry of (I − K)^(−1) is 1.

**Theorem 3 (persistence for every number of rings).** In a balanced loop satisfying condition W, every contact binds both of its
rings at every lag T ≥ 1, at every ring size. The witnesses are the end of F_i on R_i and the end of B_(i+1) on R_(i+1), each with
coefficient 1 in c_i(T) for every T ≥ 1. In particular the antipodal loops, with every k_i = s/2, persist for every number of rings
and every even ring size.

**Theorem 4 (when the feedback is finite).** The series (I − K)^(−1) = Σ_m K^m is a finite sum exactly when r is a power of two and
the loop is balanced. Then K^(r/2) = 0. For four rings this is `LOOP-PROOF-20261108-001A`'s closed form.

## Nearest known result

- **Ingredients.** Generating functions over GF(2), the binomial theorem in characteristic 2, and the symmetry C(m, j) = C(m, m − j).
- **Classification.** Known-with-delta. The delta is the loop of contacts: going back and forth across any ring costs the same,
  a^(s−2), so the feedback is A + cA^(−1), and balance makes every return to a contact cancel.

## Proof of Theorem 1

As in `LOOP-PROOF-20261108-001A`, Theorem 1: C_i = S_i + z a^(f_i) C_(i−1) + z a^(b_(i+1)) C_(i+1), the partners of a law-(6, 6) contact
adding only first values. So K = z(A + B), with A_(i, i−1) = a^(f_i) and B_(i, i+1) = a^(b_(i+1)). Then
(AB)_(i, i) = a^(f_i + b_i) = a^(s−2), and AB has no other entries, so AB = cI and B = cA^(−1). Going once round,
A^r = (Π_i a^(f_i)) I = a^F I. ∎

## Proof of Theorem 2

(I − K)^(−1) = Σ_(m ≥ 0) z^m M^m with M = A + cA^(−1). Since A and A^(−1) commute,
M^m = Σ_j C(m, j) c^j A^(m − 2j). A power A^n has diagonal entries only when n = tr, and then A^(tr) = a^(tF) I. So the diagonal
entry of M^m is the sum over t of C(m, j_t) c^(j_t) a^(tF), where j_t = (m − tr)/2.
- **t = 0.** C(m, m/2) is even for m ≥ 2. By Lucas' theorem C(2j, j) is odd only if every binary digit of j is a digit of 2j,
  and for j ≥ 1 the lowest digit of j is not.
- **t and −t.** j_(−t) = m − j_t, so C(m, j_(−t)) = C(m, j_t). Their sum is C(m, j_t) c^(j_t) a^(tF) (1 + c^(tr) a^(−2tF)). Balance
  says F = r(s − 2)/2, so c^r = a^(r(s−2)) = a^(2F), and the bracket vanishes.

So M^m has zero diagonal for every m ≥ 1, and (I − K)^(−1) has diagonal 1. The identities hold in the field of Laurent series
GF(2)((z)), where a is invertible. ∎

## Proof of Theorem 3

C_i = Σ_j ((I − K)^(−1))_(i, j) S_j. The end of F_i enters S_i through Φ_i with weight z/(1 + z), and no other S_j. The end of
B_(i+1) enters S_i through Ψ_(i+1) with the same weight, and no other S_j. Condition W rules out either being a partner read by
another contact (`LOOP-PROOF-20261108-001A`). By Theorem 2 each therefore has coefficient generating function z/(1 + z) in C_i, which
is 1 at every T ≥ 1. The antipodal loops have Σ k_i = rs/2 and use law (12, 12). ∎

## Proof of Theorem 4

- **Powers of two.** Let r = 2^p and suppose the loop is balanced. In characteristic 2, M^(r/2) = A^(r/2) + c^(r/2) A^(−r/2), and
  A^(−r/2) = a^(−F) A^(r/2). So M^(r/2) = (1 + c^(r/2) a^(−F)) A^(r/2). Balance gives (c^(r/2))² = a^(2F), and squaring is injective
  in characteristic 2, so c^(r/2) = a^F and M^(r/2) = 0.
- **Unbalanced.** M^r = (a^F + c^r a^(−F)) I, a nonzero scalar, so M is not nilpotent.
- **Not a power of two.** Write r = 2^p q with q odd and q ≥ 3. Then M^(2^p) = N + dN^(−1), with N = A^(2^p) and d = c^(2^p). N^q is
  a scalar, and x^q minus a scalar is separable for odd q. So N is diagonalisable over an algebraic closure, with at least three
  distinct eigenvalues μ. N + dN^(−1) has eigenvalues μ + d/μ, which all vanish only if every μ satisfies μ² = d. In characteristic 2
  that equation has a single root, so M is not nilpotent. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream statuses | pass |
| 1 | Theorem 3's witnesses at every lag to 300, balanced loops of 2 to 8 rings at ring sizes 4 to 20, random positions and antipodal ones | pass |
| 2 | The antipodal loops of 2 to 10 rings at every even size from 4 to 16 | pass |
| 3 | Theorem 4 by exact rational functions over GF(2): M^(r/2) = 0 for balanced loops of 2, 4 and 8 rings; M^n ≠ 0 up to n = 2r for balanced loops of 3, 5, 6 and 7 rings and unbalanced ones of 4 | pass |
| 4 | Full state spaces: balanced loops of 2, 3, 4 and 5 rings at size 4, every contact persistent | pass |

## Nonclaims

- **Sufficient, not necessary.** Unbalanced loops can persist too (`LOOP-ANY-20261108-001B`); this proof does not cover them.
- **These loops only:** rule-60 rings (rule 102 by mirror symmetry), the stated laws.
- **Two-time knots only** (A30); composition under A37; no distance.
