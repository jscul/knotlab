# Kloosterman multiplicities and the collapse

Status: Proved by hand (Theorems 1 to 3 and Proposition 4, with finite checks 1 to 3 of `check.py`); the Kloosterman law and its
corollaries are exact computations (checks 4 to 7 and the stress run), and check 8 is a computation at other sides. The target
registered with this ticket, the law's lower bounds and with them the collapse at every power of two, is not proved.

Ticket `LINEAR-ROOTS-20261109-001A`, epic `LINEAR-ROOTS-20261109-001` (sub-goal B58), 2026-11-09 (pre-registered in commit 76cc32e30).

## Standard statement

- **Setting.** n = 2^m, h = n/2, q = 2n, over GF(2). A is the walk of the n × n torus of rule-60 rings cut open both ways and A_cone
  its quarter-turn cone (`CONE-COLLAPSE-20261109-001A`): det(xI − A) = det(xI − A_cone)⁴ and
  det(I − μA_cone) = det(I + C_s(μ)) = μ^(−h) det(Σ_{i=0}^{m} μ^(2^i) C_i) (`RETURN-DIGITS-20261109-001A`, Theorems 1 and 5), with
  C_s(w) = w^(n+1) T_h(w^(−2)) and T_h(c) the map f ↦ (K + c)(εf)(K + c) mod K^h, ε = W_(h−1) = 1 + Σ_{j=1}^{m−1} K^(h − h/2^j).
- **Kloosterman sums.** For a ∈ GF(q), K(a) = Σ_{x ∈ GF(q)} (−1)^(Tr(x + a/x)) with 1/0 = 0 (Tr the trace of GF(q) over GF(2)).
  K(a) = 1 + 𝒦(a) for the usual sum 𝒦(a) over x ≠ 0, and K(a) = 1 − t_a where t_a is the trace of Frobenius of the elliptic curve
  y² + xy = x³ + a over GF(q), whose j-invariant is 1/a (Lachaud and Wolfmann).

**Theorem 1 (the count).** For every a ∈ GF(q), K(a) ≡ 0 mod 4, and Σ_{a ∈ GF(q)*} K(a)(K(a) − 2)/8 = q(q − 2)/8 = n(n − 1)/2, the
dimension of A_cone. Hence: **if every a ∈ GF(q)* is a root of det(I − μA_cone) of order at least K(a)(K(a) − 2)/8, then every
eigenvalue of A is a (2n − 1)-th root of unity (the collapse), A_cone is invertible, and the eigenvalue 1/a has algebraic
multiplicity exactly K(a)(K(a) − 2)/8.**

**Theorem 2 (the kernel as a difference equation).** For a ∈ GF(q)* let b = √a. Then ker(I + C_s(a)) is isomorphic to the space of
F ∈ F[k]/(k^h) (polynomials of degree below h) with

(k + 1) F(k + 1) ≡ Ω_b(k) F(k) (mod k^h),  Ω_b(k) = b ε(b^(−4) k) = b + Σ_{i=2}^{m} b^(2^i) k^(h − 2^(i−2)).

**Theorem 3 (the trace in the multiplier).** For b ∈ GF(q), as Laurent polynomials in k,

k^h Ω_b(k) = b² + k^(2h) L(b⁴/k),  L(x) = Σ_{i=0}^{m} x^(2^i),

L the trace polynomial of GF(q). So for y ∈ GF(q)*, Ω_b(y) = y^h·Tr(b⁴/y) + b²/y^h, with Tr(b⁴/y) ∈ {0, 1}.

**Proposition 4 (the shift is the Kloosterman curve).** For c ≠ 0, the curve r + r⁻¹ = t + t⁻¹ + c, on which T_h(c)'s substitution
K ↦ K + c lifts from the cut line's coordinate K = t + t⁻¹, is birational to Y² + Y = x + c^(−4)/x (by u = rt, x = u/c²,
Y = t/(r + t)). Over GF(q) the latter has q − 2 + K(c^(−4)) points with x ≠ 0; at the eigenvalue 1/a, where c = a^(−2), this is
q − 2 + K(a), since K(a⁸) = K(a).

**The Kloosterman law (computed).** For every a ∈ GF(q)*, the eigenvalue λ = 1/a of A_cone has
- algebraic multiplicity K(a)(K(a) − 2)/8 = (t_a² − 1)/8, so CONE-COLLAPSE's k(k + 1)/2 law has |t_a| = |K(a) − 1| = 2k + 1;
- geometric multiplicity |K(a)|/4, the dimension of ker(I + C_s(a));
- Jordan blocks 1, 5, 9, ..., K(a) − 3 when K(a) > 0, and 3, 7, 11, ..., |K(a)| − 1 when K(a) < 0; no eigenvalue when K(a) = 0 (a
  Kloosterman zero). These are CONE-COLLAPSE's blocks 2k − 1, 2k − 5, ....

Computed exactly: the multiplicities and blocks for every eigenvalue class at sides 4, 8, 16, 32, 64 and 128 (check 5, against the class
data of `CONE-COLLAPSE-20261109-001`); the geometric multiplicities for every a at sides 4 to 128 (check 4) and, in the stress run, at
256 and 512.

**Consequences of the law (computed where stated).**
- **The period.** A_cone^(e(2n−1)) = I for the least power of two e at least the largest block: e = 4, 8, 16, 16, 32, 32 at sides 4 to
  128, the periods computed by `FULL-REACH-PROOF-20261108-001` (for A, 4 to 64) and `CONE-COLLAPSE-20261109-001` (for the cone, 128)
  (check 6).
- **The eigenvalue 1.** K(1) = 1 − t_(m+1) for y² + xy = x³ + 1, whose traces over GF(2^r) are t_1 = −1, t_2 = −3,
  t_(r+1) = −t_r − 2t_(r−1); so 1 is an eigenvalue of multiplicity (t_(m+1)² − 1)/8: 3, 0, 15, 10, 21, 120 at sides 4 to 128 (check 7).

**Computed at other sides (check 8).** At the sides 3 to 20 that are not powers of two, the cone's characteristic polynomial has an
irreducible factor whose degree does not divide the order of 2 modulo 2n − 1; its eigenvalues do not all lie in the field of
(2n − 1)-th roots of unity, so no argument through that field alone (a reflection group of odd order, for instance) proves the collapse
at every side where 2n − 1 is defined.

**Open.** The lower bounds of Theorem 1, which would prove the collapse and the law together. Theorem 2 makes the geometric half a
statement about one h × h kernel per a; Theorem 3 and Proposition 4 show where the Kloosterman sum enters (the phase Tr(b⁴/y) beside
the shift y ↦ y + 1, and the curve of the shift itself), but no argument turns either into the count.

## Nearest known result

- **Ingredients.** Kloosterman sums over GF(2^r): K ≡ 0 mod 4 and the relation to the curves y² + xy = x³ + a (Lachaud and Wolfmann,
  1990); their first and second moments (classical); Kloosterman zeros, which here are exactly the missing eigenvalues (Dillon's bent
  functions use the same zeros).
- **Search.** A bounded web search on 2026-11-09 for Kloosterman sums with eigenvalue multiplicities of walks, cellular automata or
  matrices over GF(2) found none; the nearest hits are Kloosterman sums as eigenvalues of Cayley graphs (the opposite roles) and as
  coefficients of characteristic polynomials modulo powers of two.
- **Classification.** New as far as found.

## Proof of Theorem 1

The involution x ↦ a/x of GF(q)* has one fixed point, √a, whose term is (−1)^(Tr(0)) = 1; the term x = 0 is 1; the other q − 2
elements form (q − 2)/2 = 2^m − 1 pairs with equal terms. So K(a) = 2 + 2P with P a sum of 2^m − 1 terms ±1, an odd number, and
K(a) ≡ 0 mod 4. Hence K(a)(K(a) − 2)/8 is a non-negative integer (K(a) ≤ 0 or K(a) ≥ 4).

With 𝒦 = K − 1: Σ_{a ∈ GF(q)} 𝒦(a) = Σ_{x ≠ 0} (−1)^(Tr(x)) Σ_a (−1)^(Tr(a/x)) = 0 and 𝒦(0) = Σ_{x ≠ 0} (−1)^(Tr(x)) = −1, so
Σ_{a ≠ 0} 𝒦(a) = 1. And Σ_{a ∈ GF(q)} 𝒦(a)² = Σ_{x, y ≠ 0} (−1)^(Tr(x + y)) Σ_a (−1)^(Tr(a(1/x + 1/y))) = q·#{x = y} = q(q − 1), so
Σ_{a ≠ 0} 𝒦(a)² = q² − q − 1. Then Σ_{a ≠ 0} K(a)(K(a) − 2) = Σ_{a ≠ 0} (𝒦(a)² − 1) = q² − 2q.

For the consequence: det(I − μA_cone) has degree at most T = n(n − 1)/2. If each a ∈ GF(q)* is a root of order at least
K(a)(K(a) − 2)/8, these orders add up to at least T, so the degree is exactly T (A_cone is invertible), every root lies in GF(q)*,
and each order is exactly K(a)(K(a) − 2)/8. A root μ = a is the eigenvalue 1/a, a (2n − 1)-th root of unity, and A has the cone's
eigenvalues (`CONE-COLLAPSE-20261109-001A`, Theorem 2). ∎

## Proof of Theorem 2

By `RETURN-DIGITS-20261109-001A`, Theorems 1 and 2, v ∈ ker(I + C_s(a)) exactly when T_h(c)v = zv with c = a^(−2), z = a^(−(n+1)),
and T_h(c)f = S_h(c)(εf), S_h(c) the map f ↦ (K + c)f(K + c) mod K^h. Substituting K = ck carries S_h(c) to c·S, S g = (k + 1)g(k + 1)
mod k^h, and multiplication by ε(K) to multiplication by ε(ck) (as in the proof of Theorem 5 there). So the equation reads
c·S(ε(ck)f) = zf for f(k) = v(ck); with F = ε(ck)f, a bijection since ε(ck)² = 1 in F[k]/(k^h), it reads S F = (z/c)ε(ck)F. Since
a^q = a and q = 2n, (a^(−n))² = a^(−1), so z/c = a^(1−n) = √a = b, and c = b^(−4). Finally ε(b^(−4)k) = 1 + Σ_j b^(−4e_j)k^(e_j),
e_j = h − h/2^j, and b·b^(−4e_j) = b^(1 − 2n + 2^(m+1−j)) = b^(2^(m+1−j)), using b^(2n) = b. With i = m + 1 − j (i = 2, ..., m),
e_j = h − 2^(i−2). ∎

## Proof of Theorem 3

k^(2h)(b⁴/k)^(2^i) = b^(2^(i+2)) k^(2h − 2^i). For i = 0, ..., m − 2 these are k^h times the terms b^(2^(i+2)) k^(h − 2^i) of Ω_b
(index i + 2 = 2, ..., m). For i = m − 1 the term is b^(2^(m+1)) k^h = b k^h, since b^q = b: k^h times Ω_b's constant term. For i = m it is
b^(2^(m+2)) k^0 = b², which cancels the leading b². On GF(q)*, L(x) = Tr(x). ∎

## Proof of Proposition 4

Put u = rt and v = r + t. The curve is (r + t)(1 + 1/(rt)) = c, that is v(u + 1) = cu. So r and t are the roots of X² + vX + u with
v = cu/(u + 1); writing X = vY, Y² + Y = u/v² = (u + 1)²/(c²u) = u/c² + 1/(c²u), which is Y² + Y = x + c^(−4)/x with x = u/c². The
maps (t, r) ↦ (x, Y) = (rt/c², t/(r + t)) and back (t = vY, r = v(Y + 1)) are rational. For each x ∈ GF(q)* the equation in Y has two
solutions when Tr(x + c^(−4)/x) = 0 and none otherwise, giving Σ_{x ≠ 0} (1 + (−1)^(Tr(x + c^(−4)/x))) = q − 1 + 𝒦(c^(−4)) points.
K is constant on Frobenius orbits (Tr(y²) = Tr(y)), so K(a⁸) = K(a). ∎

## Checks

`check.py` (one process, a few seconds; `--write` rewrites `result.json`):
- **0.** The dependencies (`RETURN-DIGITS-20261109-001A`'s manifest and library, `CONE-COLLAPSE-20261109-001A`'s library, result and
  stress data) bound by hash.
- **1.** Theorem 1 for q = 4 to 512.
- **2.** Theorem 2's isomorphism, as equal kernel dimensions for every a, sides 4 to 32.
- **3.** Theorem 3 as a polynomial identity for every b, sides 4 to 256, and by evaluation on GF(q)*, sides 4 to 64.
- **4.** The geometric law for every a, sides 4 to 128.
- **5.** The algebraic law and the Jordan blocks, every class, sides 4 to 128.
- **6.** The law's period exponent against the computed periods, sides 4 to 128.
- **7.** K(1) = 1 − t_(m+1), sides 4 to 128.
- **8.** Sides 3 to 20 other than powers of two.
- **9.** The stress run (`research/LINEAR-ROOTS-20261109-001/stress_test.json`): the geometric law at sides 256 and 512.
