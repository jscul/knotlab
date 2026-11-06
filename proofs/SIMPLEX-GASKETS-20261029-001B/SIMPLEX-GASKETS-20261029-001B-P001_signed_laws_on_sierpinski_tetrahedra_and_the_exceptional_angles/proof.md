# Signed laws on Sierpinski tetrahedra and the exceptional angles

Status: Proved

Ticket `SIMPLEX-GASKETS-20261029-001B`, 2026-10-29.

## Standard statement

**Setting.**
- **As in `SIMPLEX-GASKETS-20261029-001A`.**
  - SG^d_k has up simplices T(v) = (v, v+e₁, …, v+e_d) with |v| ≤ k − 1, and #T = C(k+d−1, d) of them. Its corners are A = 0 and
    B_i = k e_i.
  - The corner relation is R, and a law is exact when R = λw with λ ≠ 0.
  - s = (−1)^x and E = s₀ + … + s_d.
  - The *sine wave* is w_θ = (−1)^(x₀) sin(θE)/sin θ, with factor λ_(d,k)(y), a monic integer polynomial in y = 2 cos θ.
- **The cosine wave.** c_θ(x) = (−1)^(x₀) cos(θE).
- **Census laws.**
  - A census law is f(x₀, m), where m is the number of ones among x₁, …, x_d, with values in {−1, 0, 1} and the first nonzero entry
    +1.
  - It is written as two rows of signs, f(0, 0..d) then f(1, 0..d). For example `+-0+ +0-+` is the Legendre law in d = 3.
- **Complement and flip.** *Complement* changes every bit. The *non-base flip* changes x₁, …, x_d only.

**Results.**
- **Theorem 1 (cosine waves, every dimension).** For every d, k and θ:
  - if #T is odd, R(c_θ) = μ c_θ;
  - if #T is even, R(c_θ) = ν w_θ: the cosine wave becomes the sine wave.
  - As functions of θ, μ and ν have finitely many zeros per level.
  - **The twist.** Multiplying by (−1)^|x| relates the families. In odd d it maps the sine wave at θ to a multiple of the sine wave at
    π/2 − θ. In even d it maps the sine wave at θ to a multiple of the cosine wave at π/2 − θ.
  - **Consequence for d = 2.** The law (−1)^a[NAE], whose period k ≡ 1, 2 (mod 4) was found in `SIGNED-GASKETS-20261029-001B`, is
    c_(π/6). Its period is the parity of #T = k(k+1)/2.
- **Theorem 2 (θ = π/4 fails at the even levels).** For d ≥ 2 and even k, the corner relations of w_(π/4) and c_(π/4) are zero. So
  y² − 2 divides λ_(d,k).
- **Lemma 3 (complement and flip).**
  - Complementing every bit preserves exactness, with the same factor.
  - If w(x̄) = ±w(x) and k is odd, the non-base flip of w is exact whenever w is, with factor ±λ.
- **Theorem 4 (parity in every dimension).**
  - Even parity is exact on SG^d_k exactly when k is a power of 2.
  - Odd parity is exact exactly when k = 1, or k is a power of 2 and d is even. For odd d and even k, odd parity's corner relation is
    even parity.
  - The factor is 2^(C(k+d−1, d−1) − d).
- **Theorem 5 (the census).**
  - **Sizes.** On SG^3_k for k = 2 to 5 (3,280 laws), 75 laws are exact at some level, 13 of them with a knot support (K1–K3). On
    SG^4_k for k = 2, 3 (29,524 laws), 75 are exact, with 8 knots.
  - **Families.** Every family law is exact exactly at the levels its theorem allows, except where its factor vanishes (listed
    below).
  - **Sporadic knots.** The knot laws outside the families are 6 in d = 3 (three complement pairs) and 2 in d = 4 (one pair).
  - **Every-level knots.** The knot laws exact at every computed level are exactly standing waves. In d = 3 these are the sine waves
    at π/3 and π/6. In d = 4 they are the sine wave at π/3 and the cosine wave at π/6.
- **Proposition 6 (exceptional angles).**
  - Computed: the exact factor polynomials for d = 2 (k ≤ 8), d = 3 (k ≤ 5) and d = 4 (k ≤ 3).
  - **Rational ones.** The only exceptional angles that are rational multiples of π are π/2 (every k ≥ 2) and π/4 (exactly the even
    k).
  - **Irrational ones.** Every other exceptional angle is an irrational multiple of π. Their number grows with k, and the smallest
    shrinks by a factor of about 0.58 per level in d = 2.

| d = 3 family | Law | Knot | Exact at (2–5) | Reason |
| --- | --- | --- | --- | --- |
| sine wave π/3 (Legendre) | `+-0+ +0-+` | yes | 2, 3, 4, 5 | A |
| sine wave π/6 (signed majority) | `++0- -0++` | yes | 2, 3, 4, 5 | A |
| sine wave π/4 (signed odd parity) | `0+0- -0+0` | yes | 3, 5 | A; Theorem 2 at 2, 4 |
| non-base flips of these three | `+0-+ +-0+`, `+0-- --0+`, `+0-0 0-0+` | yes | 3, 5 | Lemma 3 |
| even parity | `+0+0 0+0+` | yes | 2, 4 | Theorem 4 |
| cosine wave π/4, and its flip | `+0-0 0+0-`, `0+0- +0-0` | yes | none (allowed at 5, factor zero) | Theorem 1 |
| sporadic | `+0-+ 0+-0`, `0+-0 -+0-` / `+-0+ 0-+0`, `0+-0 +0-+` / `+0-- 0++0`, `0++0 --0+` | yes | 2, 3 / 3 / 2 | none known |

| d = 4 family | Law | Knot | Exact at (2–3) | Reason |
| --- | --- | --- | --- | --- |
| sine wave π/3 (Legendre) | `+0-+0 0+-0+` | yes | 2, 3 | A |
| cosine wave π/6 (twisted Legendre) | `+0--0 0++0-` | yes | 2, 3 | Theorem 1 (#T = 5, 15) |
| non-base flips of these two | `0+-0+ +0-+0`, `0++0- +0--0` | yes | 3 | Lemma 3 |
| even and odd parity | `+0+0+ 0+0+0`, `0+0+0 +0+0+` | yes | 2 | Theorem 4 |
| sine and cosine waves π/4, and flips | `+--++ ++--+`, `++--+ -++--`, … | no (full support) | 3 | A; Theorem 2 at 2 |
| sine wave π/2 = (−1)^m | `+-+-+ +-+-+` | no | none | λ(0) = 0 |
| sporadic | `+-0+- 0-+0-`, `+0-+0 +-0+-` | yes | 3 | none known |

| d | k | Exceptional θ/π in (0, 1/2] (π − θ is exceptional too) |
| --- | --- | --- |
| 2 | 2 | 1/4, 1/2 |
| 2 | 3 | 0.1358, 1/2 |
| 2 | 4 | 0.0790, 1/4, 1/2 |
| 2 | 5 | 0.0464, 0.1602, 1/2 |
| 2 | 6 | 0.0271, 0.1069, 1/4, 0.2651, 1/2 |
| 2 | 7 | 0.0156, 0.0717, 0.1719, 0.1952, 0.3009, 1/2 |
| 2 | 8 | 0.0088, 0.0476, 0.1237, 0.1680, 1/4, 0.2618, 0.3111, 1/2 |
| 3 | 2 | 1/4, 1/2 |
| 3 | 3 | 0.0708, 0.1358, 0.4548, 1/2 |
| 3 | 4 | 0.0269, 0.0646, 0.1082, 0.1692, 1/4, 0.3218, 0.4571, 1/2 |
| 3 | 5 | 0.0103, 0.0272, 0.0505, 0.0799, 0.1145, 0.1508, 0.1900, 0.3262, 0.4153, 0.4728, 1/2 |
| 4 | 2 | 1/4, 1/2 |
| 4 | 3 | 0.0501, 0.0694, 0.1067, 0.2183, 1/2 |

- **Conjecture 7 (rational angles).** For every d ≥ 2 and k ≥ 2, the only rational exceptional angles are π/2 and, for even k, π/4.
  Ticket A excludes every odd prime-power denominator.
- **Conjecture 8 (uniqueness).** Among census laws, the knots exact at every level k ≥ 2 are exactly the sine waves with weights in
  {−1, 0, 1} and nonvanishing factor: the Legendre law, and in odd d also the π/6 wave.
  - The cosine wave drops out wherever #T is even, by Theorem 1.

## Nearest known result

- **In the repository.**
  - `SIGNED-GASKETS-20261029-001B` is the census in d = 2. Its families F1 to F4 and P are the cases d = 2 of the sine wave, the
    cosine wave (Theorem 1), Lemma 3 and Theorem 4. Its F3 conjecture, that the factor is never zero, is not settled here: the
    method of ticket A fails for the cosine factor, which is divisible by 3 at k = 6 and 9 in d = 2.
  - `SIMPLEX-GASKETS-20261029-001A` is the sine wave in every dimension.
- **Outside.**
  - Lucas's theorem for multinomial coefficients and the self-similarity of Pascal's simplex modulo 2 are classical.
  - So is the fact that the conjugates of 2 cos(2π/n) are all real.
  - No census of signed laws on Sierpinski tetrahedra or four-simplices, and no cosine-to-sine conversion, was found in the bounded
    search of ticket A.
- **Classification.**
  - Lemma 3 and Theorem 4 are elementary, and Theorem 4 is a direct extension of the classical Lucas argument.
  - Theorems 1 and 2, the census and Proposition 6: no overlap found (candidate local delta).

## Proof of Theorem 1

- **Sectors.** c_θ = (1/2) Σ_(σ=±1) s₀ ζ^(σE), the sine wave's expansion without the factor σ.
  - The vertex sums are the same as for the sine wave: ζ^S − ζ^(−S) at a base corner, ζ^S + ζ^(−S) elsewhere. So the axes again lock
    the sectors of all corner simplices to one σ₀.
  - R(c_θ) = 2^(−#T) s_A Σ_(σ₀) ζ^(σ₀E_c) Z_c(σ₀), where Z_c(σ₀) = Σ_(σ: σ_(T(0)) = σ₀) Π_(u summed) f_u(S_u).
- **The flip.** Reversing every sector changes only the #T − 1 summed base-corner factors, so Z_c(−1) = (−1)^(#T−1) Z_c(1).
  - So R(c_θ) = 2^(−#T) s_A Z_c(1)(ζ^(E_c) + (−1)^(#T−1) ζ^(−E_c)).
  - For #T odd this is 2^(1−#T) Z_c(1) c_θ.
  - For #T even it is 2^(1−#T) i Z_c(1) sin θ · w_θ.
- **Finitely many zeros.** As in ticket A, only the all-plus sector choice reaches the top ζ-degree (d+1)(#T − 1) in Z_c(1), with
  coefficient 1. So Z_c(1) is a nonzero Laurent polynomial with finitely many zeros on the unit circle.
- **The twist.** Write θ = π/2 − θ′ and |x| = (d + 1 − E)/2.
  - For even d, E is odd and sin(θE) = (−1)^((E−1)/2) cos(θ′E). So (−1)^|x| w_θ = (−1)^(d/2) c_(θ′)/sin θ.
  - For odd d, E is even and sin(θE) = −(−1)^(E/2) sin(θ′E). So (−1)^|x| w_θ = −(−1)^((d+1)/2) (sin θ′/sin θ) w_(θ′).
- **d = 2.** On the not-all-equal tuples (E = ±1), c_(π/6) = (√3/2)(−1)^a, and on the others (E = ±3) it is 0. ∎

## Proof of Theorem 2

- **The vertex factor at π/4.** Let u = a e_i + b e_j with i ≠ j, a, b ≥ 1 and a + b = k: a vertex on the edge from B_i to B_j.
  - It is no base corner (|u| = k), and it lies in exactly T(u − e_i) and T(u − e_j).
  - Its factor ζ^S + ζ^(−S) = 2 cos(πS/4), with S ∈ {0, ±2}, vanishes unless its two simplices carry opposite sectors.
- **The chain.** The simplices T((k−1−t) e_i + t e_j), t = 0, …, k − 1, form a chain whose neighbours share such a vertex. So every
  surviving term alternates sectors along it: the last simplex has sector (−1)^(k−1) times the first.
- **The contradiction.** The first and last are T((k−1)e_i) and T((k−1)e_j), both axis simplices locked to σ₀. So for even k no term
  survives, for both waves.
- **The factor.** λ_(d,k)(√2) = 0, and y² − 2, the minimal polynomial of √2, divides λ_(d,k). ∎

## Proof of Lemma 3

- **Complement.** x ↦ x̄ is a bijection of the configurations, so R_(w∘c)(y) = R_w(ȳ) = λ w(ȳ) = λ (w∘c)(y).
- **Flip: the substitution.** Substitute x_v = y_v ⊕ (|v| mod 2).
  - On T(v) with |v| even, the copy of w becomes the flipped law F(w) at y.
  - With |v| odd it becomes w(ȳ_v, y_(v+e_i)) = ε F(w)(y), where w(x̄) = ε w(x).
- **Flip: the corners.** A is unchanged, and for odd k every B_i is complemented. So R_(F(w))(y) = ε^(n_odd) R_w(y_A, ȳ_B) =
  ε^(n_odd) λ F(w)(y), where n_odd is the number of T(v) with |v| odd.
- **Even k.** The corners are unchanged and the identity fails in general. Check 8 confirms this for the Legendre law at k = 2, 4. ∎

## Proof of Theorem 4

- **Solving the layers.** The parity law b reads x(v + e_d) = x(v) + Σ_(i<d) x(v + e_i) + b (mod 2) on T(v).
  - Every vertex u with u_d ≥ 1 is fixed by T(u − e_d), and every simplex is used exactly once. So the solutions are the free
    assignments of the bottom facet Φ = {u_d = 0}, each extended uniquely.
- **The top corner.** By induction on layers, x(B_d) = Σ_(w∈Φ) M(w) x(w) + c_k b. Here M(w) is the multinomial coefficient
  k!/((k−|w|)! w₁! ⋯ w_(d−1)!), and the constants satisfy c₀ = 0 and c_t = d c_(t−1) + b. So c_k = b for even d and c_k = k b for odd
  d.
- **k a power of 2.** By Lucas, M(w) is odd only when the parts have disjoint binary digits, which here forces one part to equal k:
  w = A or w = B_i.
  - So the corner relation is 2^(|Φ| − d) times the parity law with constant c_k b, where |Φ| = C(k+d−1, d−1).
  - This is the law itself unless d is odd, k is even and b = 1, when it is even parity.
- **k not a power of 2.** Write k = 2^a + r with 0 < r < 2^a. Then M(r e₁) = C(k, r) is odd, and r e₁ is a summed vertex of Φ.
  Flipping it flips x(B_d), so every corner tuple occurs, and no parity law is reproduced. ∎

## Proof of Theorem 5

- **The computation.** Every census law and level was computed exactly. Weights in {−1, 0, 1} and at most 52 summed vertices keep
  every intermediate value below 2^62, so int64 arithmetic is exact.
- **The engine.** It agrees with direct enumeration on 160 law–level pairs: every census law exact on SG^3_2 or SG^4_2, 40 random
  laws on each, and 6 laws on SG^3_3.
- **The families.** They are generated from their definitions by the waves (rescaled to {−1, 0, 1}), parity, complement and flip.
  - Each is exact at every level where its theorem allows, except at these levels, where floating point confirms the corner relation
    is zero:
    - the sine wave π/4 at even k (Theorem 2);
    - the cosine wave π/4 at k = 2 in d = 4 (Theorem 2), and at k = 5 in d = 3 (observed, unexplained);
    - the sine wave π/2 (λ(0) = 0).
  - No family law is exact at a level its theorem forbids.
- **The rest.** The knot laws not in a family are the sporadic ones listed. The knot laws exact at every computed level are exactly
  the waves named. ∎

## Proof of Proposition 6

- **The polynomials.** λ_(d,k) comes from ticket A's sampling: d#T + 3 values of y modulo six primes, with the same polynomial from
  four primes. It is then factored over Z.
- **The rational roots.** The factors y and y² − 2 give π/2 and π/4.
- **Every other factor.** Each has fewer real roots than its degree. A root 2 cos(2πr) with r rational would have all its Galois
  conjugates of the form 2 cos(2πr′), hence real. So no root of such a factor is 2 cos of a rational multiple of π.
- **The angles.** The listed angles are the real roots in (−2, 2), converted to θ = arccos(y/2). ∎

## What the computation checks

`check.py` takes about five minutes and replays:
- the engine against direct enumeration;
- the full census, with families, zero factors, sporadic laws and every-level knots;
- Theorem 1 in floating point (d = 2 to 6, 60 cases, error below 10⁻¹² of the sum of absolute values), and exactly in integers for the
  cosine wave at π/6 (d = 2, k ≤ 8; d = 4, k ≤ 3);
- Theorem 2, in the polynomials and in floating point;
- the factorizations and angles of Proposition 6;
- Theorem 4 in 36 cases;
- Lemma 3 on 54 flip instances;
- controls: a random law fails; the cosine wave is not reproduced at even #T; odd parity becomes even in d = 3.

## Reading

- **Two waves, one attractor.**
  - The sine wave reproduces itself on every Sierpinski simplex.
  - The cosine wave reproduces itself only when the number of simplices is odd. Otherwise it turns into the sine wave, which then
    persists.
  - So under refinement the sine wave is the attractor of the pair. The d = 2 family with period 4 was the cosine wave all along.
- **What builds every level.** In both censuses, the knots that reproduce themselves at every computed level are standing waves.
  - Everything else is tied to an arithmetic of k: odd levels for the flips, powers of 2 for parity, odd #T for the cosine wave. Or it
    is sporadic.
  - This extends the d = 2 picture to three and four dimensions.
- **Exceptional angles.** The wave fails only at finitely many angles per level.
  - Two are rational: π/2 always, and π/4 at even levels, where the edges between non-base corners frustrate the phases.
  - The rest are irrational, crowd towards 0 as the level grows, and never hit an odd prime-power angle.

## Nonclaims

- The census covers only laws symmetric in the non-base corners with weights in {−1, 0, 1}, levels 2 to 5 (d = 3) and 2, 3 (d = 4).
  Conjectures 7 and 8 are open.
- The sporadic laws and the zero of the cosine wave at π/4, k = 5 are not explained.
- The cosine factor's nonvanishing at π/6, the F3 conjecture of `SIGNED-GASKETS-20261029-001B`, remains open.
- **Observations, unexplained.**
  - The sextic y⁶ − 5y⁴ + 8y² − 8 divides both λ_(2,3) and λ_(3,3).
  - The Legendre factor at level 3 is ±2^(C(d+2,3) − d) for d = 2, 3, 4 (−4, −128, 65536). At other angles π/q no such pattern holds:
    the norms carry large primes.
