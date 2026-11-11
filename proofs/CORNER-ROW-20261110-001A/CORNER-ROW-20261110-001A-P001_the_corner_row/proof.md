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

## Training result, recorded before side 64 (2026-11-11)

The exact rows at the training sides 4, 8, 16 and 32 were computed by the frozen method (`research/CORNER-ROW-20261110-001/rows.py`,
`rows_training.json`; the largest linear complexity in s was 8, 20, 54 and 136, against the bound n(n − 1)).

**No rule in the frozen alphabet was found** for the entries other than four next to the corners. Those four were known before
registration, from C1 and the four-corner formula of `RETURN-LAW-20261110-001C`: ρ_(L,0) = 1/(1 + L(s²)),
ρ_(L,n−2) = ρ_(R,1) = s^n ρ_(L,0), ρ_(R,n−2) = s^(2n−1) ρ_(L,0); besides, ρ_(L,n−3) = ρ_(R,0). By the frozen definition the verdict on the
closed form is therefore **no pattern**, whatever side 64 shows. What the training rows show instead (computed, 4 to 32):
- the irreducible factors of the reduced denominators across the row are exactly the minimal polynomials over GF(2) of the classes
  a ∈ GF(2n)* whose Kloosterman sum K(a) = Σ_(x ∈ GF(2n)) (−1)^Tr(x + a/x) (1/0 = 0) is not zero, every such class in some entry
  (`kclass.py`); no rule in the alphabet is known for the Kloosterman zeros;
- every reduced denominator is a perfect square, and the largest exponent of a class's factor over the row is 2⌈|K(a)|/8⌉
  (`denomsq.py`, `kclass.py`);
- along each wall the entries obey no short linear recurrence in b over GF(2)(s): the order at random points is n/2, that of a
  generic sequence of n − 1 terms (`recb.py`).

**Held-out predictions for side 64**, committed here before any exact entry at side 64 is computed. They are observations outside the
frozen alphabet and cannot change the verdict; they test whether the reason for it holds one size up.
- **P1.** The factors of the denominators across the row are exactly the minimal polynomials of the classes a ∈ GF(128)* with K(a) ≠ 0.
- **P2.** Every reduced denominator is a perfect square.
- **P3.** The largest exponent of each class's factor over the row is 2⌈|K(a)|/8⌉.
- **P4.** Along each wall the recurrence order in b at random points is 32.
- **P5.** The relations next to the corners: ρ_(L,62) = ρ_(R,1) = s^64 ρ_(L,0), ρ_(R,62) = s^127 ρ_(L,0), ρ_(L,61) = ρ_(R,0).
