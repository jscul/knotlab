# Kloosterman multiplicities and the collapse

Status: Partial (pre-registered 2026-11-09, before the proof attempt).

Ticket `LINEAR-ROOTS-20261109-001A`, epic `LINEAR-ROOTS-20261109-001` (sub-goal B58).

## What is registered

Let n = 2^m, h = n/2 and q = 2n, and let A_cone be the quarter-turn cone of the walk of the n × n torus of rule-60 rings cut open both
ways, over GF(2) (`CONE-COLLAPSE-20261109-001A`): det(I − μA_cone) = det(I + C_s(μ)) = μ^(−h) det(Σ_{i=0}^{m} μ^(2^i) C_i)
(`RETURN-DIGITS-20261109-001A`, Theorems 1 and 5). For a in GF(q) let

K(a) = Σ_{x ∈ GF(q)} (−1)^(Tr(x + a/x)),  1/0 = 0,

the Kloosterman sum of GF(q) with the term x = 0 included (Tr the trace of GF(q) over GF(2)).

1. **The count (to be proved).** Σ_{a ∈ GF(q)*} K(a)(K(a) − 2)/8 = n(n − 1)/2, the degree of the cone polynomial. So if every
   a ∈ GF(q)* is a root of det(I − μA_cone) of order at least K(a)(K(a) − 2)/8, then every eigenvalue of A_cone lies in GF(q) (the
   collapse) and each order is exactly K(a)(K(a) − 2)/8.
2. **The Kloosterman law (computed).** For every a ∈ GF(q)*, the eigenvalue λ = 1/a of A_cone has
   - algebraic multiplicity K(a)(K(a) − 2)/8;
   - geometric multiplicity |K(a)|/4, the dimension of the kernel of I + C_s(a);
   - Jordan blocks of sizes 1, 5, 9, ..., K(a) − 3 when K(a) > 0, and 3, 7, 11, ..., |K(a)| − 1 when K(a) < 0 (none when K(a) = 0).

   With t = 1 − K(a), the trace of Frobenius of the elliptic curve y² + xy = x³ + a over GF(q) (whose j-invariant is 1/a = λ), the
   multiplicity is (t² − 1)/8: the k(k + 1)/2 law of `CONE-COLLAPSE-20261109-001` has |t| = 2k + 1.

**Target.** (2), or the lower bounds of (1), hence the collapse at every power of two. To be proved, or left open with the gap stated.

**How (2) was found.** By exact computation before this registration: its algebraic multiplicities at sides 4, 8, 16, 32, 64 and 128
for every eigenvalue class, against the class data of `CONE-COLLAPSE-20261109-001` (check 5 of its ticket A and its stress run), and its
geometric multiplicities at sides 4 to 64 for every a ∈ GF(q)*, as kernels of I + C_s(a) built from `RETURN-DIGITS-20261109-001A`'s
T_h. Also computed: at the sides n = 3 to 24 that are not powers of two, the cone's characteristic polynomial has an irreducible factor
whose degree does not divide the order of 2 modulo 2n − 1, so there its eigenvalues do not all lie in the field of (2n − 1)-th roots of
unity.

**Replaced first step.** B58's first step, a polynomial matrix M(μ) with (Σ μ^(2^i) C_i) M(μ) = μ^a (μ^(2n) + μ)^b I, exists exactly
when the collapse holds, and its least b is the largest Jordan block; the law above gives that block, so the attempt goes through the
lower bounds of (1) instead.

## Planned checks

- (1) for m = 1 to 8 (q = 4 to 512), exactly.
- (2)'s geometric multiplicities at side 128 for every a ∈ GF(256)* (after this registration), and its algebraic multiplicities and
  Jordan blocks at 4 to 128 against `CONE-COLLAPSE-20261109-001`'s data.
- Stress run: (2)'s geometric multiplicities at side 256 (every a ∈ GF(512)*).
