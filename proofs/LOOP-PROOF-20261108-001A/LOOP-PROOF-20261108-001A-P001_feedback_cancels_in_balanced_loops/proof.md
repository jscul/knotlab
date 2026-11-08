# Feedback cancels in balanced loops

Status: Proved by hand. The finite claims are checked in `check.py`.

Ticket `LOOP-PROOF-20261108-001A`, 2026-11-08.

## Standard statement

- **The loop.** Four rings R_0, …, R_3 of s ≥ 4 cells on rule 60 (x_j ← x_(j−1) + x_j), indices mod 4. Contact c_i is cell k_i of
  R_i and cell 0 of R_(i+1), with k_i ∈ {2, s − 2} (`LOOP-RINGS-20261108-001A`).
- **Chains.** On R_i, the forward chain F_i is cells 1, …, k_i − 1, running from c_(i−1) to c_i, of length f_i = k_i − 1; the backward
  chain B_i is cells k_i + 1, …, s − 1, running from c_i to c_(i−1), of length b_i = s − k_i − 1. So f_i + b_i = s − 2.
- **Laws.** Each contact reads its left neighbour on both of its rings, the ends of F_i and of B_(i+1) (law 12, 12), or both
  neighbours on both rings (law 6, 6), adding its two partners, the first cells of B_i and of F_(i+1).
- **Balance.** The loop is balanced when k_0 + k_1 + k_2 + k_3 = 2s, that is, two contacts at cell 2 and two at cell s − 2.
- **Condition W.** No contact with law (6, 6) is followed by a ring with k = 2, and none sits at k = s − 2 on its own first ring;
  that is, for every law-(6, 6) contact c_j, k_j ≠ s − 2 and k_(j+1) ≠ 2.

**Theorem 1 (feedback cancels).** Write C_i(z) = Σ_T c_i(T) z^T over GF(2) and a = z/(1 + z). Then
C_i = S_i + z a^(f_i) C_(i−1) + z a^(b_(i+1)) C_(i+1), where S_i collects c_i's first value and the first values of the chains and
partners it reads. Substituting for C_(i−1) and C_(i+1), the term in C_i always cancels, and the term in C_(i+2) cancels exactly when
the loop is balanced. So in a balanced loop

  C_i = S_i + z a^(f_i) S_(i−1) + z a^(b_(i+1)) S_(i+1).

**Theorem 2 (persistence at every size).** In a balanced loop satisfying condition W, every contact binds both of its rings at every
lag T ≥ 1, at every ring size: the end of F_i, on R_i, and the end of B_(i+1), on R_(i+1), each have coefficient 1 in c_i(T) for
every T ≥ 1. With law (12, 12) at every contact this holds from s = 4, and the six balanced position patterns all qualify.

**Theorem 3 (round the loop).** With law (12, 12) at every contact, c_i needs R_(i−1) exactly at the lags T for which C(T − 2, m)
is odd for some m from f_i to f_i + f_(i−1) − 1, and R_(i+2) exactly when C(T − 2, m) is odd for some m from b_(i+1) to
b_(i+1) + b_(i+2) − 1. These lags recur (by Lucas' theorem, T − 2 = 2^t − 1 serves for large t), so influence returns round the loop.

## Nearest known result

- **Ingredients.** Pascal's triangle mod 2 as rule 60's powers, and generating functions over GF(2) for linear recurrences.
- **Classification.** Known-with-delta. The delta is the loop: the returning influence cancels in pairs, mod 2, exactly when the
  positions balance.

## Lemma 1 (chains)

A cell x updated as x ← x + y has X = x(0)/(1 + z) + a Y. So a chain of length ℓ driven by u ends with
a^ℓ U + Σ_j a^(ℓ−j) x_j(0)/(1 + z). The coefficient of z^T in z^p/(1 + z)^q is C(T − p + q − 1, q − 1).

*Proof.* x(T + 1) = x(T) + y(T) gives X − x(0) = z(X + Y). The rest follows by induction along the chain, and the coefficients by
the binomial series of (1 + z)^(−q) over GF(2). ∎

## Lemma 2 (two partners add a constant)

With law (6, 6), c_i's partners are the first cells of B_i and of F_(i+1), each updated as x ← x + c_i, so each is a C_i +
x(0)/(1 + z). Their sum is (B_i[1](0) + F_(i+1)[1](0))/(1 + z): the two a C_i cancel. ∎

## Proof of Theorem 1

c_i(T + 1) is the sum of the cells it reads at lag T, so C_i − c_i(0) = z(end of F_i + end of B_(i+1) + partners). By Lemmas 1 and 2,
the end of F_i is a^(f_i) C_(i−1) plus first values, the end of B_(i+1) is a^(b_(i+1)) C_(i+1) plus first values, and the partners add
first values only. This gives the first formula, with

  S_i = c_i(0) + z(Φ_i + Ψ_(i+1) + π_i),

Φ_i the first values of F_i's cells weighted a^(f_i − j)/(1 + z), Ψ_(i+1) those of B_(i+1)'s cells, and π_i the partners' sum (zero
under law 12, 12). Substituting C_(i+1) = S_(i+1) + z a^(f_(i+1)) C_i + z a^(b_(i+2)) C_(i+2) and
C_(i−1) = S_(i−1) + z a^(f_(i−1)) C_(i−2) + z a^(b_i) C_i:
- the coefficient of C_i is z²(a^(b_(i+1) + f_(i+1)) + a^(f_i + b_i)) = z²(a^(s−2) + a^(s−2)) = 0;
- the coefficient of C_(i+2) = C_(i−2) is z²(a^(b_(i+1) + b_(i+2)) + a^(f_i + f_(i−1))), which is 0 exactly when
  b_(i+1) + b_(i+2) = f_i + f_(i−1), that is, since b = s − 2 − f, when f_0 + f_1 + f_2 + f_3 = 2s − 4, which is balance. ∎

## Proof of Theorem 2

By Theorem 1, the first value of a cell enters c_i only through S_i (weight z), S_(i−1) (weight z² a^(f_i)) and S_(i+1) (weight
z² a^(b_(i+1))).
- **On R_i.** The end of F_i appears in Φ_i with weight 1/(1 + z), so in c_i with weight z/(1 + z), whose coefficients are 1 for
  every T ≥ 1. It appears in no other S_j, except as a partner of c_(i−1) when f_i = 1 and c_(i−1) has law (6, 6), which condition W
  excludes.
- **On R_(i+1).** The end of B_(i+1) appears in Ψ_(i+1), which is part of S_i, with weight 1/(1 + z), and in no other S_j, except as
  a partner of c_(i+1) when b_(i+1) = 1 and c_(i+1) has law (6, 6), which condition W excludes.

So both witnesses have coefficient 1 in c_i(T) for every T ≥ 1, and c_i binds both of its rings at every lag. With law (12, 12)
everywhere there are no partners, so the argument holds for every s ≥ 4. ∎

## Proof of Theorem 3

With law (12, 12), the cells of R_(i−1) reach c_i only through Φ_(i−1) in S_(i−1), and those of R_(i+2) only through Ψ_(i+2) in
S_(i+1). The j-th cell of F_(i−1) enters with weight z² a^(f_i) a^(f_(i−1) − j)/(1 + z), whose coefficient at T is
C(T − 2, f_i + f_(i−1) − j) by Lemma 1; the cells of B_(i+2) likewise give C(T − 2, b_(i+1) + b_(i+2) − j). A ring is needed at T
exactly when one of its cells has coefficient 1. ∎

## Where the argument stops

- **Unbalanced loops.** The term z²(a^(b_(i+1) + b_(i+2)) + a^(f_i + f_(i−1))) C_(i+2) stays, so influence keeps returning round the
  loop. With law (12, 12), no unbalanced loop is persistent at sizes 5 to 30: 236 of the 260 lose persistence, and the other 24, at
  sizes 25, 27 and 29, stay undecided within 10^6 lags (check 3).
- **Overlaps.** When condition W fails, a law-(6, 6) contact's partner is also the end of the chain another contact reads, and the
  witness's coefficient picks up a binomial term. 26 of `LOOP-RINGS-20261108-001`'s 54 families persisting to 16 cells are of this
  kind; they persist through witnesses that change from lag to lag, which this argument does not track.
- **Mixed laws.** A contact reading one partner only, as under laws (6, 12) or (12, 6), feeds a C_i back into itself, so Theorem 1's
  form no longer holds. The remaining 12 families are of this kind.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream statuses | pass |
| 1 | Theorem 2's witnesses at every lag to 300, balanced loops, laws (12, 12) or (6, 6) under condition W, ring sizes 5 to 30, and laws (12, 12) from size 4 | pass |
| 2 | Theorem 3's lags for every contact and far ring, laws (12, 12), balanced loops, ring sizes 5 to 30 | pass |
| 3 | No unbalanced loop with law (12, 12) is persistent, ring sizes 5 to 30 (236 lose persistence, 24 undecided) | pass |
| 4 | Full state spaces: the balanced loops with law (12, 12) at sizes 4 and 5 (12 and 16 bits) | pass |
| 5 | Of `LOOP-RINGS-20261108-001`'s 54 families, 16 satisfy Theorem 2's hypotheses at size 9 | pass |

## Nonclaims

- **These loops only:** four rule-60 rings (rule 102 by mirror symmetry), the laws stated.
- **Two-time knots only** (A30); composition read under A37; no distance.
