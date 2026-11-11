# The corner's row of the block inverse: exact rows, a frozen rule, a held-out test

Status: **Partial rule only** under the frozen criteria (status class closed-null). Rules hold for the six entries next to the corners,
all known or derivable before registration; none was found for the other 2(n − 1) − 6 entries. The training verdict and five
predictions were committed in 128b2e30d before any entry at side 64 was computed; that commit called the outcome "no pattern", which is
corrected here. Computed instead, exactly at 4 to 64 with side 64 held out: the row's denominators are supported exactly on the classes
a ∈ GF(2n)* whose Kloosterman sum K(a) is not zero, every such class appearing; they are perfect squares with largest exponent
2⌈|K(a)|/8⌉; and along each wall the entries have the generic linear complexity n/2. Proposition 1 is proved. Read by an independent
referee pass, whose findings are folded in (see the decision note).

Ticket `CORNER-ROW-20261110-001A`, epic `CORNER-ROW-20261110-001` (pre-registered in commit c53bb2861).

## Standard statement

- **The walk, the box and K_n** are as in `RETURN-LAW-20261110-001C`: the box [0, N]², N = 2n − 2, at n = 2^m; the corner c = (0, 1); the
  v-grid with columns 0, …, n − 1 and rows 0, …, n − 2; K_n the block operator of Theorem 7 on the rows of the two end columns, over
  GF(2)(s), s = w².
- **The row.** ρ_(X,b) = [K_n^(−1)]_((L,0),(X,b)), X ∈ {L, R}, b = 0, …, n − 2. Each entry is a rational function of s of linear
  complexity at most n(n − 1), the number of v contacts: the walk alternates between v and h contacts, so in s each entry is a coordinate
  of e_c(I − sA²)^(−1), with A² acting on the v contacts.
- **Kloosterman sums.** K(a) = Σ_(x ∈ GF(2n)) (−1)^Tr(x + a/x) with 1/0 = 0, the extended Kloosterman sum, a multiple of 4; for a ≠ 0 the
  curve y² + xy = x³ + a over GF(2n) has 2n + K(a) points, counting the point at infinity (Lachaud and Wolfmann 1990; Katz and Livné
  1989). "The class of a" is the set of its conjugates a^(2^i), on which K is constant; m_a(s) is its minimal polynomial over GF(2).

**Proposition 1 (the row is the walk to the side walls).** For every n ≥ 2, ρ_(L,b)(w²) is the series of the walks from c to the v contact
(0, 2b + 1) and ρ_(R,b)(w²) the series of the walks to (N, 2b + 1).

**The verdict under the frozen criteria: a partial rule only.** Rules in the frozen alphabet were found for six entries, all next to the
corners, and for no other:
- ρ_(L,0) = 1/(1 + L(s²)), the corner's return law (C1 of `RETURN-LAW-20261110-001C`);
- ρ_(R,n−2) = s^(2n−1)/(1 + L(s²)) at the far corner ρ²c = (N, N − 1), and ρ_(L,n−2) = s^n/(1 + L(s²)) and
  ρ_(R,0) = s^(n−1) + s^(3n−1)/(1 + L(s²)) one step from the corners ρc = (1, N) and ρ³c = (N − 1, 0), the only contacts that the
  contacts (0, N − 1) and (N, 1) read. All three come from the four-corner formula of `RETURN-LAW-20261110-001C`,
  Σ_i G_(c, ρ^i c) ρ^i = C_m(w⁴)/(1 + w^(2n−1)ρ) + w^(2n−3)ρ³ with ρ⁴ = 1, since C_m(x)/(1 + x^(2n−1)) = 1/(1 + L(x)) over GF(2);
- ρ_(R,1) = ρ_(L,n−2) and ρ_(L,n−3) = ρ_(R,0), seen on truncated series before registration (c53bb2861: "its first two right-block
  entries equal its last two left-block entries"). They hold exactly at 4 to 64 and fail at every side 3, 5 to 7 and 9 to 12, so they
  are facts of the powers of two, not symmetries of the box.

At side 4 these six entries are the whole row; from side 8 on, 2(n − 1) − 6 entries have no rule. The frozen criteria call a rule for a
declared subset of the entries, stated before side 64 and passing there, a partial rule; "no pattern" needs that no rule be stated, or
that every stated rule fail. 128b2e30d stated C1 and the corner relations (its P5) before side 64, and they passed, so by the letter the
outcome is this partial rule. It adds nothing that was not known or derivable before registration. Ticket B was conditional on a full
rule and is retired as frozen. The line is parked as the coordinator asked ("if no pattern appears by side 64, stop"), since no rule
appeared beyond the corners.

**Computed (exact; `check.py`).**
- **The exact rows** at 4, 8, 16, 32 and the held-out 64 by the frozen method: largest linear complexity in s 8, 20, 54, 136 and 368,
  against the bound n(n − 1); every recovered rational function reproduces all 4n² terms computed, more than four times the bound.
- **K1, the support of the denominators.** The irreducible factors of the reduced denominators across the row are exactly the minimal
  polynomials m_a of the classes a ∈ GF(2n)* with K(a) ≠ 0, and each such class divides some entry's denominator: 2 of 3 classes at 4,
  3 of 5 at 8, 6 of 7 at 16, 11 of 13 at 32 and 17 of 19 at 64. Half of this follows from the spectrum: every reduced denominator divides
  the reversed minimal polynomial of A² on the v contacts, which is the product of m_a^(|K(a)|/2) over the classes with K(a) ≠ 0 at 4 to
  32 (check 8), the classes of the cone's spectrum (`LINEAR-ROOTS-20261109-001`, computed to 128). The row's own content is that it sees
  every such class. The corner entry alone sees only the classes with Tr(a) = 1, since 1 + L(s²) = (1 + L(s))² and 1 + L(a) = 1 + Tr(a)
  on GF(2n).
- **K2.** Every reduced denominator is a perfect square.
- **K3.** The largest exponent of m_a over the row is 2⌈|K(a)|/8⌉: 2 for |K| = 4 and 8, 4 for |K| = 12 and 16, and 6 for |K| = 20,
  which first occurs at side 64. It is not the spectrum's exponent |K(a)|/2, and falls below it from |K| = 8 on.
- **K4.** Along each wall the n − 1 entries have linear complexity exactly n/2 over GF(2)(s), the value for a generic sequence of that
  length, so they obey no linear recurrence in b of lower order. This is certified exactly (check 7): a sequence of 2k − 1 terms has
  linear complexity exactly k when its k × k Hankel matrix is nonsingular, and each wall's Hankel determinant is nonzero at a point of
  GF(2^31), where no denominator vanishes. The prediction in 128b2e30d was tested at random points only.
- **The six entries next to the corners** at 4 to 64, and the failure of the two power-of-two relations at 3, 5 to 7 and 9 to 12
  (check 6).
- **Held out.** 128b2e30d predicted K1 to K4 and the corner relations (P1 to P5) for side 64, and all held. Not every part was a test.
  The support half of K1 followed from the spectrum; two of P5's relations (ρ_(L,62) and ρ_(R,62)) had been computed at side 64 before
  registration, from the four-corner formula below w^1200 and the far corner's series; and P4 predicted the generic outcome. The real
  tests were that every class with K ≠ 0 appears (17 of 17), K2, and K3 with its exponent 6 at |K| = 20, a value no training side had.

**Reading (interpretation, not a theorem).** If K1 holds at every m, a rule in the alphabet that gave the denominators in factored form
would say, at every power of two, which classes of GF(2n) are Kloosterman zeros. No such description is known: zeros are found by
testing elements one at a time, through the curve's 2-Sylow subgroup (Ahmadi and Granger). That may be why no rule was found, but it is
a heuristic, since a rule could encode the zeros implicitly, as a product or a determinant, without describing them. The row's
denominators sit on the classes of the collapse line's Kloosterman law (`LINEAR-ROOTS-20261109-001`: the cone's eigenvalue 1/a has
K(a)(K(a) − 2)/8 copies), with exponents of their own. So a proof of B137's count through the row would meet that spectrum, which the
reduction of `REACH-HALVES-20261110-001A` did not need; whether the count itself needs it is open.

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

**Correction (2026-11-11, from the referee pass; the training result above is kept as committed).** Three of its statements are wrong.
- "No rule in the frozen alphabet was found for the entries other than four next to the corners." The alphabet also gives
  ρ_(R,0) = s^(n−1) + s^(3n−1)/(1 + L(s²)), and with ρ_(L,n−3) = ρ_(R,0) six entries have rules. The training search tested only
  relations ρ_k = s^e ρ_j and missed this affine one.
- "Those four were known before registration, from C1 and the four-corner formula." The four-corner formula gives ρ_(L,n−2), ρ_(R,n−2)
  and ρ_(R,0), and C1 gives ρ_(L,0); the relations ρ_(R,1) = ρ_(L,n−2) and ρ_(L,n−3) = ρ_(R,0) had been seen on truncated series only.
- "They are observations outside the frozen alphabet and cannot change the verdict." P5 is in the alphabet. With C1 it is a partial
  rule stated before side 64 and passing there, so the frozen outcome is the partial rule, not no pattern (the verdict above).

Logged in `docs/CORRECTIONS.md`, 2026-11-11.

## Nearest known result

- **Kloosterman sums over binary fields.** Their values and their link to the ordinary elliptic curves over GF(2^r) (Lachaud and
  Wolfmann, IEEE Trans. Inform. Theory 36 (1990); Katz and Livné, C. R. Acad. Sci. Paris 309 (1989)); a deterministic test for a single
  zero by point halving (Ahmadi and Granger, Math. Comp. 83 (2014)); their values and zeros (Lisoněk, SETA 2008, and later). No closed
  form for the set of zeros was found.
- **Related records here.** `LINEAR-ROOTS-20261109-001` (the cone's multiplicities K(K − 2)/8), `KLOOSTERMAN-BOUNDS-20261110-001` and
  the collapse line it opened; `RETURN-LAW-20261110-001C` (the block operator, the corner entry, the four-corner formula, Corollary 10).
- **Classification.** The support restriction is inherited from the spectrum. New as far as found: that the corner's walk to the side
  walls sees every class with K(a) ≠ 0, that its denominators are perfect squares, and their exponents 2⌈|K(a)|/8⌉, which are not the
  spectrum's. Not a priority claim.

## Proof of Proposition 1

In the decomposition of `RETURN-LAW-20261110-001C`'s Theorem 7, a walk from c is cut at its visits to the two end columns into row
steps on an end column and segments between end visits. A walk from c that ends on an end column at row b is a finite sequence of such
pieces from (L, 0) to (X, b), so the walks from c to the v contact of column X at row b are counted by the (X, b) entry of
Σ_k (I − K_n)^k = K_n^(−1) in row (L, 0). Column 0 is X = 0 and column n − 1 is X = 2n − 2 = N; row b is Y = 2b + 1. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Proposition 1 against the block inverse of Theorem 7, to s^40 at 4, 8, 16 | pass |
| 2 | The exact rows reproduce all 4n² walk terms computed, at 4 to 64 | pass |
| 3 | The training rows equal the file committed in 128b2e30d; the held-out file equals a fresh computation | pass |
| 4 | The predictions of 128b2e30d (K1 to K3, K4 at random points, the corner relations P5) at 4 to 32 and at the held-out side 64 | pass |
| 5 | The protocol: commit 128b2e30d holds the verdict and P1 to P5, not the side-64 rows | pass |
| 6 | The six entries next to the corners at 4 to 64; the two power-of-two relations fail at 3, 5 to 7 and 9 to 12 | pass |
| 7 | K4 exactly: each wall's n/2 × n/2 Hankel determinant is nonzero at points of GF(2^31), at 4 to 64 | pass |
| 8 | The spectrum at 4 to 32: the reversed minimal polynomial of A² on the v contacts against the Kloosterman classes and the row's exponents; the corner entry's classes | pass |

## Nonclaims

- **This is not a proof that no closed form exists.** None was found in the frozen alphabet beyond the six entries next to the
  corners, after a training search of about six minutes that tested only monomial relations between entries; the affine rule for
  ρ_(R,0) was found by the referee.
- K1 to K4 are computed at five sides, one of them held out; none is proved. K4 is certified exactly at those sides.
- The six corner formulas are exact at 4 to 64 (the exact rows). At other powers of two they rest on C1, proved side by side to 512,
  and on the four-corner formula, computed below w^1200 at 4 to 64 and below w^2000 at 128; none is proved for every m.
- The reason offered for the missing rule, the Kloosterman zeros, is interpretation.
