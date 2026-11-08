# One-sided additive paths of every length

Status: Proved by hand from `RECUR-PROOF-20261108-001A`'s lemmas. The finite claims are checked in `check.py`.

Ticket `RECUR-PROOF-20261108-001B`, 2026-11-08.

## Standard statement

- **The setting.** A path of n ≥ 3 rings R_0, …, R_(n−1), each of s ≥ 4 cells, as in `NATIVE-PATH-20261108-001A`: contact c_i is
  cell 0 of R_i and, for i ≥ 2, cell k_(i−1) of R_(i−1), with every k_j ∈ {2, s − 2}. Every non-contact cell runs its ring's rule,
  60 or 102.
- **The laws.** c_1 reads its partner on R_0 and its partner on R_1 (the neighbour that reads it back). Each later contact c_i reads
  both of its neighbours on R_(i−1) and its partner on R_i.

**Theorem.** Mirror every rule-102 ring, and let e = (k_1' − 1) + … + (k_(n−2)' − 1) over the mirrored positions. Then:
1. every contact binds both of its rings at every lag T ≥ 1;
2. the last contact c_(n−1) binds R_(n−1) at every lag, and R_0 exactly at the lags T at which C(T − (n − 1), e) is odd;
3. so, by Lucas' theorem, the path composes at recurring lags with every contact persistent (A37) at every length and every ring
   size, with composing lags of density 2^(−w), w the number of ones in e, and at every lag from the light cone on (A34) never.

For n = 4 this is `RECUR-PROOF-20261108-001A`'s theorem; for n = 3 it gives chains of three rings.

## Proof

By `RECUR-PROOF-20261108-001A`'s Lemma 2, mirror to rule 60 everywhere.
- **Persistence.** c_1 reads only its two partners, so c_1(T) = R_0[1](0) + R_1[1](0) for T ≥ 1 (Lemma 1). For i ≥ 2, c_i reads its
  partner R_(i−1)[k_(i−1) + 1] on R_(i−1), its partner R_i[1] on R_i, and the end R_(i−1)[k_(i−1) − 1] of the chain from c_(i−1)'s
  partner R_(i−1)[1]. The chain depends only on contacts before c_i and cells they read, never on c_i's partners' first values, so by
  Lemma 1, c_i(T) = R_(i−1)[k_(i−1) + 1](0) + R_i[1](0) + R_(i−1)[k_(i−1) − 1](T − 1), and c_i binds both of its rings at every lag.
- **Which cells of R_0 matter.** As for four rings, only R_0[1](0): the rest of R_0 feeds nobody outside it.
- **The first ring's coefficient.** By Lemma 3, R_0[1](0) has coefficient C(T − 1, 0) in c_1, C(T − 1, 1) in c_1's partner on R_1,
  C(T − 1, k_1 − 1) at the chain's end, C(T − 2, k_1 − 1) in c_2, and in general C(T − i, (k_1 − 1) + … + (k_(i−1) − 1)) in c_i: each
  contact adds one lag, and each partner and chain cell adds one to the lower index. For i = n − 1 this is C(T − (n − 1), e).
- **Part 3** follows by Lucas' theorem as in ticket A; e ≥ n − 2 ≥ 1, so the composing lags miss infinitely many lags. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream statuses | pass |
| 1 | The theorem's predictions at every lag through the eventual cycle, rule 60 everywhere, n = 3 to 10 rings, ring sizes 4 to 16, every choice of positions | pass |
| 2 | The same on 400 random paths with rule 60 or 102 on each ring, n = 3 to 8, against the mirrored positions | pass |
| 3 | Full state spaces: n = 3 at ring sizes 4 and 5, and n = 5 at ring size 4 (up to 16 bits), every choice of positions | pass |

## Nonclaims

- **These families only;** the rule-90 families of `RECUR-PATH-20261108-001A` are not covered.
- **Two-time knots only** (A30).
