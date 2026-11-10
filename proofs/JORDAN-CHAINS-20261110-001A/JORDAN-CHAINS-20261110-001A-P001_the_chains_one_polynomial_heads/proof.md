# The chains that one polynomial heads

Status: Proved by hand (Theorems 1 to 3 and the lemma, with finite checks 1 to 4 of `check.py`); the chain lemma is an exact computation
(check 5, the registered side-64 run of check 6, and the stress run of check 7). The target registered with this ticket, a proof of the chain lemma, is not reached; its first order is
proved (Theorem 3), and the point where the argument stops is stated at the end.

Ticket `JORDAN-CHAINS-20261110-001A`, epic `JORDAN-CHAINS-20261110-001` (sub-goal B73), 2026-11-10 (pre-registered in commit 25ab6ffa4).

## Standard statement

- **Setting.** n = 2^m, h = n/2, q = 2n; V = F[k]_(<h); S F = (k + 1)F(k + 1) mod k^h; M_P multiplication by P mod k^h; ⟨F, G⟩ the sum of the
  coefficients of FG below degree h; τ: k ↦ k + 1 and Y = k² + k. For a ∈ GF(q)* and b = √a, X_b = S + M_(Ω_b) is the operator of
  `KLOOSTERMAN-BOUNDS-20261110-001A`: its kernel holds the cone's eigenvectors at 1/a and equals G·F[Y]_(<J), G the least-degree solution,
  k = h − deg G, J = ⌈k/2⌉ (Theorem 3 there).
- **The family.** Z(w) = S + M_(Ω(w)), Ω(w) = w^(1−n) ε(w⁻²k) = Σ_e w^(1−n−2e) k^e, e over 0 and h − h/2^j (1 ≤ j < m).

**Theorem 1 (the family).** det Z(w) = w^(h(1−n)) det(I + C_s(w)), so the order of det Z at w = a is the algebraic multiplicity of the
cone's eigenvalue 1/a; Z(a) = X_b. With Φ(u) = u^(−h) ε(u⁻¹k), Ω(w) = w·Φ(w²), so in w = a + δ

Z(a + δ) = S + (a + δ)·M_(Φ(a² + δ²)),

and the Taylor coefficients Z_i of order i ≥ 1 are multiplications, with Z_(2i+1) = a⁻¹Z_(2i) for i ≥ 1 and Z_1 = a⁻¹(Z_0 + S).

**Theorem 2 (self-adjoint family).** S and every multiplication are self-adjoint for ⟨ , ⟩ (`KLOOSTERMAN-BOUNDS-20261110-001A`,
Theorem 1), so Z(w) is self-adjoint for every w, and its partial multiplicities at a (the eigenvalue's Jordan blocks) are those of its
Lyapunov–Schmidt reduction to ker X_b, a J × J symmetric matrix function of δ.

**Theorem 3 (the first order).** For 0 ≤ i, j < J, ⟨Z_1·GY^i, GY^j⟩ = a⁻¹·[Y^(h−1−i−j)] N(G), N(G) = G(k)G(k + 1) ∈ F[Y], a polynomial of
degree h − k in Y. So this J × J matrix vanishes except, when k is odd, at its last diagonal entry, which is a⁻¹ times the square of G's
leading coefficient. Hence the eigenvalue 1/a has exactly one Jordan block of size 1 when k is odd and none when k is even.

**Lemma (the first step).** For 2i < k − 1, φ_1 = a⁻¹·k·G·Y^i solves Z_0φ_1 = Z_1·GY^i: every G·Y^i with 2i < k − 1 heads a chain of
length at least 2, with this explicit second vector.

**The chain lemma (computed).** G·Y^j heads a Jordan chain of length exactly 2k − 1 − 4j, for every j < J, and these lengths are the Jordan
blocks, at every a for sides 8 to 32 (check 5) and 64 (check 6, the run registered before it was made), and for nine values of a at
side 128 in the stress run (check 7). So the eigenvalue's multiplicity is Σ_j (2k − 1 − 4j) = k(k + 1)/2 with k = h − deg G, read
off the least solution alone; with the degree law of `KLOOSTERMAN-BOUNDS-20261110-001` (deg G = h − k_a, computed) this is the
Kloosterman multiplicity. Theorem 3 is the lemma's statement about blocks of size 1.

**Where the argument stops.** The chain lemma is Theorem 3 at every order: the reduced J × J matrix should have entries of order exactly
δ^(2k−1−2(i+j)) in a nondegenerate anti-triangular pattern. At first order the reduction is the Hankel matrix of N(G)'s top coefficients
and the degree of N(G) does all the work; at higher orders the Schur-complement corrections involve the Hasse derivatives of Φ and
shifted Hankel matrices of N(G) (for instance [k^(h−1)](k·Y^j) is 1 exactly at the j = h − 1 − 2^t), and no closed form for them was
found. Even with the chain lemma, the collapse needs the degree law (sub-goal B74).

## Nearest known result

- **Ingredients.** Partial multiplicities of analytic matrix functions and their Lyapunov–Schmidt (Schur complement) reduction; the
  first-order rank formula for the number of size-1 blocks (Gohberg, Lancaster and Rodman); self-adjoint analytic families.
- **Classification.** New as far as found (bounded search, as `LINEAR-ROOTS-20261109-001`); the ingredients are classical.

## Proof of Theorem 1

By `RETURN-DIGITS-20261109-001A`, Theorems 1 and 2, I + C_s(w) = I + w^(n+1)T_h(w⁻²) with T_h(c) = S_h(c)M_ε; the substitution K = ck carries
S_h(c) to c·S and M_(ε(K)) to M_(ε(ck)) (proof of Theorem 5 there), a change of basis. So I + C_s(w) is similar to I + w^(n−1)S·M_(ε(w⁻²k)),
and multiplying on the right by M_(ε(w⁻²k)) (determinant 1, unipotent, and an involution) and by w^(1−n) gives
w^(1−n)M_(ε(w⁻²k)) + S = Z(w). Hence det Z(w) = w^(h(1−n)) det(I + C_s(w)). At w = a ∈ GF(q), w^(1−n)ε(w⁻²k) = Ω_b(k)
(`LINEAR-ROOTS-20261109-001A`, proof of Theorem 2), so Z(a) = X_b. Since w^(−n) = (w²)^(−h), Ω(w) = w·Φ(w²); in characteristic 2,
(a + δ)² = a² + δ², so Ω(a + δ) = (a + δ)·Σ_i Φ^[i](a²)δ^(2i), Φ^[i] the Hasse derivatives. Reading off powers of δ: Z_(2i) = a·M_(Φ^[i](a²))
for i ≥ 1, Z_(2i+1) = M_(Φ^[i](a²)), and Z_0 = S + a·M_(Φ(a²)), Z_1 = M_(Φ(a²)) = a⁻¹(Z_0 + S). ∎

## Proof of Theorem 2

Each Taylor coefficient is S plus a multiplication or a multiplication, so each is self-adjoint. For a self-adjoint family the cokernel
of Z_0 is dual to its kernel through ⟨ , ⟩, and the Lyapunov–Schmidt reduction (the Schur complement of the restriction of Z to a
complement of the kernel, invertible near δ = 0) is a J × J matrix function with the same partial multiplicities; it is symmetric
because Z is. ∎

## Proof of Theorem 3

For F, F′ in the kernel, ⟨Z_1F, F′⟩ = a⁻¹⟨(Z_0 + S)F, F′⟩ = a⁻¹⟨SF, F′⟩, and ⟨SF, F′⟩ = [k^(h−1)](F(k + 1)F′(k))
(`KLOOSTERMAN-BOUNDS-20261110-001A`, proof of Theorem 1). For F = GY^i, F′ = GY^j this is [k^(h−1)](N(G)·Y^(i+j)), with N(G) = G·τG
τ-invariant, a polynomial in Y of degree deg G = h − k. For any polynomial P in Y, [k^(h−1)]P = [Y^(h−1)]P, because [k^(h−1)]Y^l =
binom(l, h − 1 − l) mod 2 is 1 exactly at l = h − 1 (the argument in that proof: a sum equal to 2^(m−1) − 1 has no carries).
So ⟨Z_1GY^i, GY^j⟩ = a⁻¹[Y^(h−1−i−j)]N(G), zero when h − 1 − i − j > h − k, that is i + j < k − 1. As i + j ≤ 2J − 2, which is k − 1
for odd k and k − 2 for even k, only the entry i = j = J − 1 for odd k survives, and it is a⁻¹ times the leading coefficient of N(G),
the square of G's. The number of Jordan blocks of size 1 of an analytic family at a point is the rank of the first-order term of its
reduction (the map from the kernel to the cokernel induced by Z_1), here 1 or 0. ∎

## Proof of the lemma

For a polynomial r in Y with deg(G·r) < h, X_b(G·r) = 0 (Theorem 3 there), and the identity (k + 1)τG + Ω_bG = k^hR_G holds exactly. Then
S(kGY^i) = (k + 1)τ(k)τ(G)Y^i = (k + 1)²τG·Y^i ≡ (k + 1)Ω_bG·Y^i and M_(Ω_b)(kGY^i) = kΩ_bGY^i, so
Z_0(kGY^i) ≡ Ω_bGY^i ≡ S(GY^i) mod k^h, the polynomial kGY^i having degree h − k + 2i + 1 < h. And Z_1GY^i = a⁻¹(Z_0 + S)GY^i = a⁻¹S(GY^i).
So Z_0(a⁻¹kGY^i) = Z_1GY^i. ∎

## Checks

`check.py` (one process, about a minute; `--write` rewrites `result.json`):
- **0.** The dependencies (`KLOOSTERMAN-BOUNDS-20261110-001A`'s manifest and library) bound by hash.
- **1.** Theorem 1: the determinant identity at random points of GF(2^16), sides 4 to 16; Z(a) = X_b and the Taylor coefficients (against a
  direct series expansion, and the odd ones a⁻¹ times the even ones), every a, sides 4 to 64.
- **2.** Theorem 2: every Taylor coefficient self-adjoint, every a, sides 4 to 32.
- **3.** Theorem 3: the first-order matrix and the number of size-1 blocks, every a, sides 8 to 64.
- **4.** The lemma, every a and i, sides 8 to 64.
- **5.** The chain lemma, every a, sides 8 to 32.
- **6.** The registered side-64 run (`research/JORDAN-CHAINS-20261110-001/side64.json`, long-running JORDAN-CHAINS-A1): the chain lemma at
  every a.
- **7.** The stress run (`research/JORDAN-CHAINS-20261110-001/stress_test.json`, JORDAN-CHAINS-S1): the chain lemma at side 128 for nine
  values of a, k = 1, 2, 3, 4, 6, 7, 8, 11 and 15.
