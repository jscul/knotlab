# From the row to the laws

Status: Partial (pre-registered 2026-11-11, before any exact row is computed).

Ticket `CORNER-ROW-20261110-001B`, epic `CORNER-ROW-20261110-001` (B140, at the coordinator's go-ahead after `RETURN-LAW-20261110-001`).

## What is registered

At n = 2^m, K_n is the block operator of RETURN-LAW-20261110-001C (Theorem 7) on V_L + V_R, the n - 1 rows of the first and last columns of the v-grid. Its corner row e_(L,0) K_n^-1 has 2(n - 1) entries rho_(X,b)(s) in GF(2)(s), X in {L, R}, b = 0, ..., n - 2: rho_(L,b)(w^2) is the series of the walks from c = (0, 1) to the v contact (0, 2b + 1) and rho_(R,b)(w^2) to (N, 2b + 1), N = 2n - 2 (the decomposition counts exactly the walks that end on an end column). Known: rho_(L,0) = 1/(1 + L(s^2)) at 4 to 512 (C1, exact) and rho_(R,n-2) = s^(2n-1)/(1 + L(s^2)) (the far corner, computed to 128). Targets B1 (the rule is the row for every m, proving C1) and B2 (the count of B137 from the row and its vanishing at every power of two from 8), with criteria frozen in proof.md. Retired without work unless ticket A's full rule passes at side 64.

## Criteria, frozen

- **Only if ticket A's full rule passes at side 64; otherwise retired without work.**
- **Target B1.** A proof for every m that the rule's row r satisfies r K_n = e_(L,0), so that it is the corner row; this proves the return law C1 of RETURN-LAW-20261110-001C for every power of two.
- **Target B2.** The count of REACH-HALVES-20261110-001A (B137) from the row by Corollary 10 of RETURN-LAW-20261110-001C, and its vanishing at every power of two from 8: the failing half of full reach.
- **Proved:** a proof by hand for every m, each formula checked exactly at sides 4 to 128, read by an independent referee pass before publication. **Obstructed:** the attempt names the lemma that would finish, checks it exactly at 4 to 128, and says why it was not proved. **Refuted:** a side to 128 where the rule or the count fails.
