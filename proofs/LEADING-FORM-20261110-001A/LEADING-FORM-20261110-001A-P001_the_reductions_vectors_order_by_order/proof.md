# The reduction's vectors order by order

Status: Proved by hand (Theorems 1 to 5, with finite checks 1 to 4 of `check.py`); check 5 is an exact computation. The target
registered with this ticket, the leading form at every order, is not reached: by the frozen stop rule the attempt ends at order 2,
and where it stops is stated at the end.

Ticket `LEADING-FORM-20261110-001A`, epic `LEADING-FORM-20261110-001` (sub-goal B73), 2026-11-10 (pre-registered in commit f8e8b996c).

## Standard statement

- **Setting.** As `CHAIN-ORDERS-20261110-001A`: n = 2^m, h = n/2, q = 2n, V = F[k]_(<h), a ∈ GF(q)*, b = √a, Z_0 = X_b, G the monic
  least-degree element of K = ker Z_0 = G·F[Y]_(<J), k = h − deg G, J = ⌈k/2⌉, N = G(k)G(k + 1), and the family
  Ẑ(λ) = Z_0 + λS + Σ_r a^(2^r)λ^(2^r)/(1 + λ^(2^r))·M_(k^(h−2^(r−1))) (Theorem 4 there), with coefficients Ẑ_s.
- **The Wronskian.** W(A, B) = A(k)B(k + 1) + B(k)A(k + 1), a polynomial in Y = k² + k, symmetric and F[Y]-bilinear; R = F[Y]/(Y^h) is
  identified with F[k]/(k^h) by Y ↦ k² + k, under which k corresponds to L(Y) = Y + Y² + Y⁴ + ⋯ + Y^(h/2).

**Theorem 1 (Z_0 is a Wronskian).** For every F ∈ V, G·Z_0F ≡ (k + 1)·W(G, F) mod k^h. Also G(1) = b·G(0).

**Theorem 2 (the chain equations).** If φ_0 = x, φ_1, … is a Jordan chain of Ẑ (Z_0φ_r = Σ_(s=1)^r Ẑ_sφ_(r−s)), then
W(G, φ_r) ≡ G·τφ_(r−1) + (G/(k + 1))·Σ_(s≥2) Ẑ_sφ_(r−s) mod k^h; the converse holds when G(0) ≠ 0.

**Theorem 3 (the second vector's Wronskian).** For x = G·Y^i with 2i < k − 1 and φ_1 = kx, every second chain vector φ_2 has

W(G, φ_2) = [N·Y^i·(1 + L(Y)) + a²G(0)²·[i = 0]·Y^(h−1)] mod Y^h,

and this polynomial has degree below h − J.

**Theorem 4 (a second solution).** If G(0) ≠ 0, there is G′ ∈ V of degree exactly h + k − 1 − 2J with Z_0G′ ≡ 0 mod k^(h−J−1) and
W(G, G′) = c·Y^(h−J−1), c ≠ 0.

**Theorem 5 (the decomposition).** For every F ∈ F(k), c·Y^(h−J−1)·F = W(G′, F)·G + W(G, F)·G′. So the second chain vector is
φ_2 = [W(G′, φ_2)·G + W(G, φ_2)·G′]/(c·Y^(h−J−1)), with W(G, φ_2) given by Theorem 3 and W(G′, φ_2) ≡ W(G, φ_2)·G′/G mod Y^(h−J−1);
the remaining coefficients of W(G′, φ_2) are fixed only by deg φ_2 < h, up to the kernel.

**Computed (where the attempt stops).** G(0) ≠ 0 at every a for sides 8 to 128 (check 1). At co-distance 3 (i + j = k − 3,
2i, 2j < k − 1), with a complement W′ containing k·G·Y^j for 2j < k − 1, the reduction's coefficient at λ⁵ is ⟨Sψ_2(x), ψ_2(y)⟩ (the
order-5 terms of the family cancel in pairs). Splitting ψ_2 = k²x + η, the pure part ⟨S(k²x), k²y⟩ = [Y^(h−3−i−j)]N is 1, and the
corrections add exactly 1, so the coefficient is 0, the leading form's ε_3: 129 cases at sides 16 to 64; in 97 of them the
correction's self-pairing ⟨Sη(x), η(y)⟩ alone is 1 (check 5).

**Where the argument stops.** The frozen rule: the first order r ≥ 2 with no closed form of ψ_r in G, k, Y, a and the family's terms
ends the attempt. At r = 2 the Wronskian W(G, ψ_2) is in closed form (Theorem 3), but ψ_2 itself needs the second solution G′
(Theorems 4 and 5) and the top coefficients of W(G′, ψ_2), which only the degree bound fixes; and the cancellation at co-distance 3
(the corrections adding 1 to the pure part) was not derived from it. So the attempt ends at order 2: the leading form stays proved
through co-distance 2 (`CHAIN-ORDERS-20261110-001A`, Theorem 5), and computed beyond.

## Nearest known result

- **Ingredients.** Wronskians and the two-dimensional F(Y)-space F(k) (the quadratic extension by Y = k² + k); consecutive Padé
  solutions with a monomial Wronskian (the determinant of consecutive convergents of a continued fraction); the 2n + 1 rule.
- **Classification.** New as far as found for this walk (bounded search of 2026-11-09); the ingredients are classical.

## Proof of Theorem 1

As G ∈ K, (k + 1)τG + Ω_aG = k^h R_G exactly (`KLOOSTERMAN-BOUNDS-20261110-001A`). Then G·Z_0F = (k + 1)G·τF + Ω_aG·F ≡
(k + 1)(G·τF + F·τG) mod k^h. At k = 0 the exact identity reads G(1) + bG(0) = 0, as Ω_a(0) = b. ∎

## Proof of Theorem 2

Multiply Z_0φ_r = Σ_s Ẑ_sφ_(r−s) by G and use Theorem 1; k + 1 is a unit mod k^h. For s = 1, Ẑ_1 = S and G·Sφ/(k + 1) = G·τφ. When
G(0) ≠ 0, G is a unit mod k^h and the steps reverse. ∎

## Proof of Theorem 3

Theorem 2 with r = 2: G·τ(kx) = (k + 1)·G·τx = (k + 1)·N·Y^i, and with Ẑ_2 = a²M_(k^(h−1)),
(G/(k + 1))·a²k^(h−1)x ≡ a²G(0)x(0)k^(h−1) = a²G(0)²[i = 0]k^(h−1) mod k^h. Under the identification of R with F[k]/(k^h),
k + 1 ↦ 1 + L(Y) (Σ_t (k^(2^(t+1)) + k^(2^t)) telescopes to k + k^h) and k^(h−1) ↦ Y^(h−1) (as Y^(h−1) = k^(h−1)(1 + k)^(h−1)). So
W(G, φ_2) is congruent mod Y^h to the stated polynomial. Its leading terms cancel, so deg_k W(G, φ_2) ≤ deg G + deg φ_2 − 1 ≤ 2h − k − 2,
and its degree in Y is at most h − J − 1; a polynomial of degree below h is its own class mod Y^h. ∎

## Proof of Theorem 4

Let D = h + k − 1 − 2J (h − 1 for k even, h − 2 for k odd). The F of degree at most D with Z_0F ≡ 0 mod k^(h−J−1) form a space of
dimension at least D + 1 − (h − J − 1) = k − J + 1. The polynomials F with W(G, F) = 0 are those with F/G ∈ F(Y), the module G·F[Y]
(`KLOOSTERMAN-BOUNDS-20261110-001A`, proof of Theorem 3: it is G_Λ·F[Y] with G = G_Λ·Y^(v_0), and v_0 = 0 as G(0) ≠ 0); those of degree
at most D are the G·r with deg r ≤ k − J − 1, a space of dimension k − J, all in K and so among the solutions. Hence some solution G′
has W(G, G′) ≠ 0. By Theorem 1, (k + 1)W(G, G′) ≡ G·Z_0G′ ≡ 0 mod k^(h−J−1), so the polynomial W(G, G′) in Y is divisible by
Y^(h−J−1). Its leading terms cancel, so its degree in k is at most deg G + D − 1 = 2(h − J − 1), and W(G, G′) = c·Y^(h−J−1) with c ≠ 0.
If deg G′ < D the degree bound would drop below 2(h − J − 1) and force W = 0; so deg G′ = D. ∎

## Proof of Theorem 5

G and G′ are independent over F(Y), since W(G, G′) ≠ 0, so they are a basis of the two-dimensional F(Y)-space F(k); write
F = αG + βG′. As W is F(Y)-bilinear with W(F, F) = 2F·τF = 0, W(G, F) = β·W(G, G′) and W(G′, F) = α·W(G′, G) = α·W(G, G′). For
F = φ_2 a polynomial, the numerator W(G′, φ_2)G + W(G, φ_2)G′ is divisible by Y^(h−J−1); at k = 0, where G is a unit, this is the
stated congruence. ∎

## Checks

`check.py` (one process, about a minute; `--write` rewrites `result.json`):
- **0.** The dependencies (`CHAIN-ORDERS-20261110-001A`'s manifest and library) bound by hash.
- **1.** Theorem 1 on a basis of V, and G(0) ≠ 0 with G(1) = bG(0), every a, sides 8 to 128.
- **2.** Theorems 2 and 3: W(G, φ_2) for an exact second chain vector of every G·Y^i with 2i < k − 1, every a, sides 8 to 128 (1,094
  vectors).
- **3.** Theorem 4: the second solution, its degree and W(G, G′), every a with k ≥ 2, sides 8 to 128.
- **4.** Theorem 5 on a basis of V, sides 8 to 64.
- **5.** The split of the co-distance-3 coefficient, every a, sides 16 to 64 (129 cases).
