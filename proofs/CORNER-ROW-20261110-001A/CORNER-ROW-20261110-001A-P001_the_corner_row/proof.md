# The corner's row of the block inverse: exact rows, a frozen rule, a held-out test

Status: Partial (pre-registered 2026-11-11, before any exact row is computed).

Ticket `CORNER-ROW-20261110-001A`, epic `CORNER-ROW-20261110-001` (B140, at the coordinator's go-ahead after `RETURN-LAW-20261110-001`).

## What is registered

At n = 2^m, K_n is the block operator of RETURN-LAW-20261110-001C (Theorem 7) on V_L + V_R, the n - 1 rows of the first and last columns of the v-grid. Its corner row e_(L,0) K_n^-1 has 2(n - 1) entries rho_(X,b)(s) in GF(2)(s), X in {L, R}, b = 0, ..., n - 2: rho_(L,b)(w^2) is the series of the walks from c = (0, 1) to the v contact (0, 2b + 1) and rho_(R,b)(w^2) to (N, 2b + 1), N = 2n - 2 (the decomposition counts exactly the walks that end on an end column). Known: rho_(L,0) = 1/(1 + L(s^2)) at 4 to 512 (C1, exact) and rho_(R,n-2) = s^(2n-1)/(1 + L(s^2)) (the far corner, computed to 128). Target: one uniform rule for every entry at every power of two, found on the training sides 4, 8, 16, 32 and tested on the held-out side 64, with the closed form, the partial rule and no pattern defined in proof.md and frozen here. Found before registration (exploration in RETURN-LAW-20261110-001, truncated series to s^64 at 4, 8, 16): the row does not pair the way the quadrant's does (entry 2k = t0 entry 2k - 1); its first two right-block entries equal its last two left-block entries. Nothing exact.

## Criteria, frozen

- **Exact rows (frozen method).** For each entry, the coefficients of its walk series in w, from the bitset walk, to 4(2n(n - 1)) + 8n terms; Berlekamp-Massey over GF(2) returns the minimal recurrence, which is exact because the linear complexity is at most the box's dimension 2n(n - 1); the reduced numerator and denominator follow, written in s = w^2. Cross-check against Theorem 7's block inverse to s^40 at 4, 8 and 16.
- **Training and held-out sides.** Training: n = 4, 8, 16, 32. Held out: n = 64. No exact entry at side 64 is computed before a rule is committed; the search is not extended past 64.
- **Closed form.** A rule R giving, for every m >= 2 and every (X, b), the reduced rational function rho_(X,b) (or its numerator and denominator) such that (i) R is stated in a commit made before any exact entry at side 64 is computed; (ii) R's statement has a length independent of m and uses only s; integer arithmetic on m, n, b and X and their binary digits; the polynomials D_k(x) = det(I + xP_k) and E_k(x) = det(I + xP_k^o) over GF(2) (P_k the path on k vertices, P_k^o with a loop at one end), C_j(x) = sum_(i <= j) x^(2^i - 1) and L_j(x) = sum_(i <= j) x^(2^i); substitution of a monomial s^e for x; finite sums and products over explicitly described index sets; and one quotient per entry; (iii) R reproduces exactly every entry at the four training sides and at side 64.
- **Partial rule.** The same for a declared subset of the entries or of their parts (for instance every denominator, or one block), stated before side 64 and passing there.
- **No pattern.** No rule, full or partial, is stated after the training sides, or every stated rule fails at side 64. Then the line (B137, B140, B141) is parked.
