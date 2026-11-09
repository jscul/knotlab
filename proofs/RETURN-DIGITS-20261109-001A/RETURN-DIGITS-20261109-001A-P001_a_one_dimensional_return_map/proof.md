# A one-dimensional return map and its digit recursion

Status: Proved by hand (Theorems 1 to 5, with finite checks 1 to 5 of `check.py`); check 6 is an exact computation. The target
registered with this ticket, the collapse at every power of two, is not proved; Theorem 5 reduces it to a statement about one
linearized matrix polynomial.

Ticket `RETURN-DIGITS-20261109-001A`, 2026-11-09 (pre-registered in commit aaa3e7be3).

## Standard statement

- **Setting.** n = 2^m, h = n/2, over GF(2). A is the walk of the n × n torus of rule-60 rings cut open both ways and A_cone its
  quarter-turn cone; `CONE-COLLAPSE-20261109-001A` proved det(I − wA_cone) = det(I + C_s(w)), C_s the (n/2) × (n/2) return map of
  the cut line on J-symmetric vectors.
- **The ring.** A_h = F[K]/(K^h) with the ball basis W_k (k < h), W_k(t + 1/t) = Σ_{|j|≤k} t^j: W_0 = 1, W_1 = 1 + K,
  W_(k+1) = K W_k + W_(k−1). For a parameter c, T_h(c) is the matrix in this basis of f ↦ (K + c)·(ιf)(K + c) mod K^h, where
  ι(W_k) = W_(h−1−k) and (ιf)(K + c) substitutes K + c into the representative of degree below h; R is the reversal k ↦ h − 1 − k
  and S_h(c) = T_h(c) R, the same map without ι.

**Theorem 1 (the return map is one-dimensional).** C_s(w) = w^(n+1) T_h(w^(−2)). So λ ≠ 0 is an eigenvalue of A exactly when
det(λ^(n+1) I + T_h(λ²)) = 0.

**Theorem 2 (the reversal is a multiplication).** ι is multiplication by ε = W_(h−1) in A_h, and ε² = 1. Explicitly
ε = 1 + Σ_{j=1}^{m−1} K^(h − h/2^j), and ε_2h = 1 + K^h ε_h.

**Theorem 3 (without the reversal, a trace).** S_h(c) has the h distinct eigenvalues c/(ζ + ζ^(−1)), ζ an (n + 1)-th root of unity
other than 1, with eigenvectors (K + c)/(K² + cK + z²) (z the eigenvalue). Equivalently its eigenvalues are c·x for the h elements
x of GF(n) of trace 1, and det(zI + S_h(c)) = c^h (1 + L_m(z/c)), L_m(X) = X + X² + X⁴ + ... + X^(2^(m−1)).

**Theorem 4 (the digit recursion).** In the basis W_0, ..., W_(h−1), K^h W_0, ..., K^h W_(h−1) of A_2h,

S_2h(c) = [[S_h, p S_h], [E, S_h + p E]],  multiplication by ε_2h = [[I, 0], [ε_h, I]],  p = c^h,

with E(f) = (coefficient of K^(h−1) in f)·1; so T_2h = S_2h ε_2h is built from T_h and S_h, starting from T_1 = S_1 = [c]. Moreover

det(zI + T_2h(c)) = det(z² I + S_h(c)² + c^h z (ε_h S_h(c) + E)).

**Theorem 5 (the cone polynomial is a linearized determinant).** On F[k]/(k^h) let N be multiplication by k and S the map
g ↦ (k + 1) g(k + 1) mod k^h (= S_h(1)). Then

det(I − μ A_cone) = μ^(−h) det( μ S^(−1) + Σ_{i=1}^{m} μ^(2^i) N^(h − 2^(i−1)) ).

The matrix is a 2-polynomial Σ_{i=0}^{m} μ^(2^i) C_i in μ with C_0 = S^(−1), C_i = N^(h−2^(i−1)) and C_m = I, all over GF(2): the
shape of the trace polynomial of GF(2n), Σ_{i=0}^{m} μ^(2^i).

**The collapse, restated.** By Theorem 5, every eigenvalue of A is a (2n − 1)-th root of unity exactly when every nonzero root μ of
det(Σ_i μ^(2^i) C_i) lies in GF(2n). Equivalently (Theorem 1), when the spectral curve det(zI + T_h(c)) = 0 meets z² = c^(n+1) only
where z⁴ = c³. Not proved.

**Computed (check 6).** At sides 4 to 32, 1 + Tr_(GF(2n))(μ) divides det(I − μA_cone) exactly once and the quotient is a square: the
parity law of `CONE-COLLAPSE-20261109-001` (an eigenvalue λ has odd multiplicity exactly when Tr(1/λ) = 1), with μ = 1/λ.

## Nearest known result

- **Ingredients.** Dickson and Chebyshev polynomials over GF(2); partial fractions on the circle; linearized (2-)polynomials and
  the trace of GF(2^(m+1)); Lucas' theorem.
- **Classification.** New as far as found; no search beyond these ingredients was made.

## Proof of Theorem 1

In sublattice coordinates an h contact (2a + 1, 2b) of the side-2n torus sits at s^a t^b and a v contact (2a, 2b + 1) at s^a t^b
(a, b ∈ Z_n). An h at g reads the v's at g·s and g·t⁻¹, a v at g reads the h's at g and g·s⁻¹t, so a walk h → v multiplies the
position by β = s + t⁻¹ and v → h by α = 1 + s⁻¹t; αβ = K_s + K_t, K_s = s + s⁻¹. Hence the generating functions of walks are
read off Δ⁻¹ (h → h, v → v), wβΔ⁻¹ (h → v), wαΔ⁻¹ (v → h), with Δ = 1 + w²(K_s + K_t), at the monomial g′/g. The cut line C1
is {s⁻¹ t^y}, C2 = {s^x t⁻¹}. So H[y, x] = [wβΔ⁻¹] at s^(x+1) t^(−1−y), and with G⁻¹ = 1 + w²K_t (Theorem 4 of
`FULL-REACH-PROOF-20261108-001A`), B = G⁻¹H has B[y, x] = [F] at s^(x+1) t^(−1−y), F = wβγΔ⁻¹, γ = 1 + w²K_t: multiplying by
t^(±1) shifts the t-exponent. Then C = BJ has C[y, x] = [F] at s^(−x) t^(−1−y).

Write γΔ⁻¹ = Σ_{j<n} Φ_j s^j (the Φ_j in F(w)[t]/(t^n − 1)). Then Φ_j = w^n D_(h−j)(Γ), Γ = K_t + w⁻², D_a the Dickson polynomial
(D_a(r + 1/r) = r^a + r^(−a), D_(−a) = D_a): indeed γ = w²Γ, Δ = γ + w²(s + s⁻¹), and the coefficient of s^j in (Σ Φ_j s^j)Δ is
w^(n+2)(Γ D_(h−j) + D_(h−j+1) + D_(h−j−1)) = 0 for 0 < j < n − 1 by the Dickson recurrence, and also at j = n − 1 (where the
neighbours are Φ_(n−2) and Φ_0 = w^n D_h), while at j = 0 the neighbours Φ_(n−1) = Φ_1 cancel and what is left is
γ w^n D_h(Γ) = γ w^n Γ^h = γ, since D_h = X^h for h a power of two, and Γ^h = w^(−n)(1 + w^n K_t^h) = w^(−n) as
K_t^h = t^(−h)(t^n + 1) = 0. As Φ_(n−j) = Φ_j, F = w(s + t⁻¹)Σ Φ_j s^j has s^(−x)-coefficient w(Φ_(x+1) + t⁻¹Φ_x). The J-symmetric
combination of columns k and n − 1 − k is therefore w(1 + t⁻¹)(Φ_k + Φ_(k+1)) = w^(n+1)(1 + t⁻¹) Γ W_(h−1−k)(Γ), by the identity
D_a(V) + D_(a+1)(V) = V W_a(V) (with V = r + 1/r both sides are r^a + r^(−a) + r^(a+1) + r^(−a−1), the sum Σ_{|j|≤a}(r^(j+1) + r^(j−1))
telescoping). Finally (1 + t⁻¹)W_i(K_t) = t^i + t^(−1−i), so for g = Σ_{i<h} g_i W_i the coefficient of t^(−1−i) in (1 + t⁻¹)g is g_i
(the exponents −1 − i and i′ never meet mod n for i, i′ < h). So C_s[i, k] is the W_i-coefficient of w^(n+1) Γ W_(h−1−k)(Γ) in A_h,
which is w^(n+1) T_h(w⁻²)[i, k]. ∎

## Proof of Theorem 2

In F[t]/(t^n − 1), W_(h−1) = N + t^h, N = Σ_j t^j the sum of all n group elements (the ball of radius h − 1 misses only t^h). Then
W_(h−1) W_k = (2k + 1)N + t^h W_k = N + t^h W_k = t^h(N + W_k), and N + W_k is the complement of the ball of radius k, which t^h
carries onto the ball of radius h − 1 − k. So W_(h−1) W_k = W_(h−1−k) in the symmetric part F[K_t] = A_h. And W_(h−1)² = N² + t^(2h)
= 1, since N² = nN = 0. From W_(h+j) = W_(h−1−j) + K^h W_j (the balls of radius h + j and h − 1 − j differ by t^(±h) times the ball of
radius j, and t^h + t^(−h) = D_h = K^h), W_(2h−1) = 1 + K^h W_(h−1): ε_2h = 1 + K^h ε_h, which unrolls to the stated sum. ∎

## Proof of Theorem 3

Let f (degree < h, top coefficient f_(h−1)) satisfy S_h f = zf: as polynomials, (1) (K + c)f(K + c) = z f(K) + f_(h−1)K^h. Substituting
K ↦ K + c gives (2) K f(K) = z f(K + c) + f_(h−1)(K + c)^h; eliminating f(K + c) between them,

(z² + K² + cK) f(K) = f_(h−1) [(K + c)^(h+1) + z K^h].

So f_(h−1) ≠ 0 and Q = K² + cK + z² divides N = (K + c)^(h+1) + zK^h. Conversely if Q | N, then f = N/Q satisfies (1): Q is invariant
under K ↦ K + c and N(K + c) = K^(h+1) + z(K + c)^h, so (K + c)f(K + c) − zf(K) = K^h Q/Q. For a root κ of Q, κ(κ + c) = z², and
N(κ) = 0 ⟺ (z²/κ)^(h+1) = zκ^h ⟺ (z/κ)^(n+1) = 1; the other root κ′ = z²/κ then satisfies it too. With z/κ = ζ, κ + κ′ = c gives
z = c/(ζ + ζ⁻¹), ζ ≠ 1 (else c = 0). These are h distinct values, so S_h is diagonalizable with them as eigenvalues. Each y = ζ + ζ⁻¹
lies in GF(n) (y^n = ζ^(−1) + ζ) with X² + yX + 1 irreducible over GF(n) (its roots ζ^(±1) are not in GF(n)), that is Tr(1/y) = 1;
there are h such y, so x = 1/y runs over the elements of GF(n) of trace 1, the roots of 1 + L_m. ∎

## Proof of Theorem 4

Write f ∈ A_2h as f_0 + K^h f_1 with f_0, f_1 of degree < h, and α(g) for the coefficient of K^(h−1) in g. Then
(K + c)f_0(K + c) = S_h f_0 + α(f_0)K^h and the same for f_1, while (K + c)^h = K^h + c^h; so modulo K^(2h)

(K + c) f(K + c) = (S_h f_0 + p S_h f_1) + K^h (S_h f_1 + α(f_0) + p α(f_1)),

which is the stated block form. By Theorem 2, ε_2h f = f_0 + K^h(f_1 + ε_h f_0). The basis K^h W_i equals W_(h+i) + W_(h−1−i) (as in
Theorem 2), which gives the change of basis P = [[I, R], [0, I]] to the ball basis of A_2h used by check 4. For the determinant, put
g = (I + pε_h) f_0 + p f_1 (p ≠ 0 as c ≠ 0), so f_1 = p⁻¹(g + f_0) + ε_h f_0, a change of coordinates X with det X = p^(−h). The top
row of T_2h gives S_h g and the bottom row S_h(ε_h f_0 + f_1) + E g = p⁻¹S_h(g + f_0) + E g, so (zI + T_2h)X =
[[zI, S_h], [z p⁻¹ + zε_h + p⁻¹S_h, z p⁻¹ + E + p⁻¹S_h]]. As zI commutes with the lower left block, its determinant is
det(z(z p⁻¹ + E + p⁻¹S_h) − (z p⁻¹ + zε_h + p⁻¹S_h)S_h) = p^(−h) det(z² + S_h² + p z(ε_h S_h + E)), and dividing by det X gives the
identity. ∎

## Proof of Theorem 5

Scaling K = ck carries S_h(c) to c·S (S = S_h(1)) and ε(K) to ε(ck) = 1 + Σ_j c^(e_j) k^(e_j), e_j = h − h/2^j. With c = λ² and
z = λ^(n+1), det(zI + T_h(c)) = det(λ²S)·det(λ^(n−1)S⁻¹ + 1 + Σ_j λ^(2e_j) N^(e_j)); with μ = 1/λ, multiplying the second factor by
μ^n gives μS⁻¹ + μ^n + Σ_j μ^(n − 2e_j) N^(e_j), and n − 2e_j = 2^(m−j); re-indexing i = m − j (and i = m for the term μ^n, N^0)
gives the stated sum. The powers of λ are collected by Theorem 1 and det(I − μA_cone) = det(I + C_s(μ)). ∎

## Checks

`check.py` (one process, a few seconds; `--write` rewrites `result.json`):
- **0.** The dependencies (`CONE-COLLAPSE-20261109-001A`'s manifest and `collapse_lib.py`) bound by hash.
- **1.** Theorem 1 against the torus at sides 4 to 32.
- **2.** Theorem 2 for h = 1 to 64.
- **3.** Theorem 3's characteristic polynomial, symbolically in c, for h = 1 to 32.
- **4.** Theorem 4's recursion for h = 1 to 16, and its determinant identity exactly for h = 1 to 4.
- **5.** Theorem 5 at sides 4 to 32, against the cone polynomials (the cone's characteristic polynomial at 4 to 16, its spectrum at 32).
- **6.** The factor 1 + Tr_(GF(2n)) at sides 4 to 32.
- **7.** The stress run (`research/RETURN-DIGITS-20261109-001/stress_test.json`), pending at closure.
