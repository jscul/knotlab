# The reduced form at every order

Status: Proved by hand (Theorems 1 to 5, with finite checks 1 to 5 of `check.py`); the leading form, the registered target, is an exact
computation (check 6 at every a for sides 8 to 128, and the stress run of check 7 at every a of side 256). Its proof is reached for the
first three orders (Theorem 5), and the point where the argument stops is stated at the end.

Ticket `CHAIN-ORDERS-20261110-001A`, epic `CHAIN-ORDERS-20261110-001` (sub-goal B73 continued), 2026-11-10 (pre-registered in commit
c252175e4).

## Standard statement

- **Setting.** n = 2^m, h = n/2, q = 2n, V = F[k]_(<h) over a field F ⊇ GF(q), S F = (k + 1)F(k + 1) mod k^h, M_P multiplication by P
  mod k^h, ⟨F, F′⟩ = Σ_(j<h) [k^j](FF′), τ: k ↦ k + 1, Y = k² + k. Z(w) = S + M_(Ω(w)), Ω(w) = w^(1−n) ε(w⁻²k), is the family of
  `JORDAN-CHAINS-20261110-001A` (Theorem 1 there: det Z(w) = w^(h(1−n)) det(I + C_s(w)), Z(a) = X_b with b = √a, Z self-adjoint).
- **At an eigenvalue parameter.** a ∈ GF(q)*, G the monic least-degree element of ker X_b, k = h − deg G, J = ⌈k/2⌉, so ker X_b =
  K = G·F[Y]_(<J) (`KLOOSTERMAN-BOUNDS-20261110-001A`, Theorem 3). N = N(G) = G(k)G(k + 1), a monic polynomial in Y of degree h − k.
  δ = w − a, u = δ/a, L(x) = x + x² + x⁴ + ⋯, and ε_t = 1 when t ∈ {1, 2, 4, 8, …}, else 0.
- **The reduction.** M(w) is the symmetric Lyapunov–Schmidt reduction of Z to K in the basis G·Y^j: with B(w)(F, F′) = ⟨Z(w)F, F′⟩
  and a complement W of K, M = B_KK − B_KW B_WW⁻¹ B_WK, a J × J symmetric matrix of power series. Its partial multiplicities at a are the
  Jordan blocks of the cone at 1/a (`JORDAN-CHAINS-20261110-001A`, Theorem 2). The target uses the monomial complement W_0, spanned by
  the k^d with d ∉ {deg G + 2j}.

**Theorem 1 (the sparse Taylor form).** Ω(a + δ) ≡ (1 + δ/a)·(Ω_a + Σ_(r=1)^(m−1) δ^(2^r) k^(h − 2^(r−1))) mod δ^n. The perturbation is
k^h L(δ²/k) (its polar terms, a polynomial in k), the same linearized polynomial as Ω_a = b + k^h L(a²/k); so near a,
Z(w) ≡ S + (w/a)·(b + k^h L(w²/k)) mod (w − a)^n.

**Theorem 2 (one moment matrix).** Let ψ(w) ∈ F[Y]/(Y^h) be the element congruent to (Ω(w) + k + 1)/(kΩ(w) + (k + 1)²) mod k^h (the
ring F[Y]/(Y^h) is identified with F[k]/(k^h) by Y ↦ k² + k), and H(w) = [ψ_(i+j+1)(w)]_(0 ≤ i, j < h/2), its Hankel (moment) matrix.
Near every a ∈ GF(q)*, Z(w) is equivalent as an analytic matrix family to diag(H(w), I_(h/2)). So the Jordan blocks of the cone at 1/a
are the partial multiplicities of one moment matrix.

**Theorem 3 (the leading matrix).** For every k ≥ 1 the matrix Γ^(k) = [ε_(k−i−j)]_(0 ≤ i, j < ⌈k/2⌉) is invertible over GF(2):
det Γ^(2c) = det Γ^(c) · det Γ^(c−1) and det Γ^(2c+1) = (det Γ^(c))², and every determinant is 1. Equivalently, the Hankel determinants of
g(z) = Σ_(r≥0) z^(2^r − 1) and of (g − 1)/z are all 1 over GF(2): g = 1/(1 + z/(1 + z/(1 + ⋯))), the Stieltjes continued fraction with
every coefficient 1.

**Theorem 4 (an even family plus one shift).** With λ = u/(1 + u), so that δ = aλ/(1 + λ), the family Ẑ(λ) = (1 + λ)Z(a + δ) satisfies

Ẑ(λ) ≡ Z_0 + λS + Σ_(r=1)^(m−1) a^(2^r) · λ^(2^r)/(1 + λ^(2^r)) · M_(k^(h − 2^(r−1))) mod λ^n,

an even function of λ plus λS, with the same partial multiplicities at λ = 0 as Z at a. Its coefficients: Ẑ_1 = S, Ẑ_2 = a²M_(k^(h−1)),
Ẑ_3 = 0, Ẑ_4 = a²M_(k^(h−1)) + a⁴M_(k^(h−2)), and so on.

**Theorem 5 (orders two and three).** Let W′ be a complement of K containing k·G·Y^j for every j with 2j < k − 1, and M the reduction of
Ẑ to K along W′. For x = G·Y^i, y = G·Y^j with i + j ≤ k − 2 and 2i < k − 1: [λ]M(x, y) = [λ²]M(x, y) = 0; if also 2j < k − 1,
[λ³]M(x, y) = [Y^(h−2−i−j)] N, which is 1 at i + j = k − 2 and 0 below. Consequently every eigenvalue 1/a has exactly k mod 2 Jordan
blocks of size 1, none of size 2, and exactly one of size 3 when k is even and none when k is odd, as the chain lemma says. For k ≤ 2
these are all the blocks: [1] at k = 1 and [3] at k = 2.

**Computed (the leading form, the registered target).** With the monomial complement W_0 and G monic, for every a and 0 ≤ i, j < J,

M_ij(u) = u^(2k − 1 − 2(i + j)) · (ε_(k−i−j) + O(u)),

that is, the leading part of the reduction is the Hankel matrix of u⁻¹Y^k L(u²/Y): its anti-diagonal i + j = k − 2^(r−1) starts at
u^(2^r − 1) with coefficient 1, and every other entry starts later. This holds at every a for sides 8 to 64 (found before
registration), 128 (after registration) and 256 (the stress run). With Theorem 3 it gives the whole chain lemma: M = λ·D·U·D with
D = diag(λ^(k−1−2i)) and U(0) = Γ^(k) invertible, so G·Y^j heads a Jordan chain of exactly 2k − 1 − 4j and these are the Jordan blocks.

**Where the argument stops.** The leading form is proved for the anti-diagonals i + j ≥ k − 2 among chains of length at least 2
(Theorem 5), which settles the blocks of size at most 3. By the 2n + 1 rule of self-adjoint perturbation theory, the leading coefficient
at u^(2t−1) needs the reduction's vectors up to order t − 1. The first, k·x, is explicit; the second already leaves the multiples of G,
because Z_0(G·p) = S(G)·Δp and Δ maps F[k] onto F[Y], which does not contain k + 1. The pure vectors k^r·x would give the coefficient
[Y^(h−t−i−j)]N, which is 1 at every co-distance t = k − i − j. The computed leading form says these contributions cancel except where t
is a power of two, the orders at which the family's perturbation k^h L(δ²/k) acts. That cancellation was not found in closed form. Even
with the chain lemma, the collapse needs the degree law (sub-goal B74). The valuations alone would do with it: they give the multiplicity
at least k(k + 1)/2, and with deg G ≤ h − k_a the Kloosterman multiplicities, which fill the cone's degree.

## Nearest known result

- **Ingredients.** Partial multiplicities and the Lyapunov–Schmidt reduction of analytic matrix functions (Gohberg, Lancaster and
  Rodman); Padé approximation and Hankel matrices; Stieltjes continued fractions and their Hankel determinants (Stieltjes, Wall,
  Flajolet); the 2n + 1 rule (Wigner); Artin–Schreier roots in characteristic 2 (L² + L = x).
- **Classification.** New as far as found for this walk (the bounded search of 2026-11-09); the ingredients are classical. The
  continued fraction of Σ z^(2^r − 1) over GF(2) follows at once from L² + L = z; Theorem 3's recursion proves the determinants directly.

## Proof of Theorem 1

Ω(w) = w^(1−n)(1 + Σ_(j=1)^(m−1) (w⁻²k)^(e_j)) with e_j = h − h/2^j. In characteristic 2, (a + δ)^(2^s) = a^(2^s) + δ^(2^s), so
(a + δ)^(−n) = (a^n + δ^n)⁻¹ ≡ a^(−n) and (a + δ)^(−2e_j) = (a + δ)^(−n)(a + δ)^(n/2^j) ≡ a^(−n)(a^(n/2^j) + δ^(n/2^j)) mod δ^n. Hence

Ω(a + δ) ≡ (1 + δ/a)·a^(1−n)(1 + Σ_j a^(−2e_j) k^(e_j)) + (1 + δ/a)·a^(1−2n) Σ_j δ^(n/2^j) k^(e_j) mod δ^n.

The first term is (1 + δ/a)Ω_a. Since a^(q−1) = 1 and q = 2n, a^(1−2n) = 1; with r = m − j, n/2^j = 2^r and e_j = h − 2^(r−1). For the
second form: Ω_a = b + Σ_(i=2)^m b^(2^i) k^(h−2^(i−2)) (`LINEAR-ROOTS-20261109-001A`), and b^(2^(r+2)) = (a²)^(2^r), so
Ω_a = b + Σ_(r=0)^(m−2) (a²)^(2^r) k^(h−2^r) = b + k^h L(a²/k), and the perturbation is k^h L(δ²/k); L is additive, so the sum is
b + k^h L((a + δ)²/k), and 1 + δ/a = w/a. ∎

## Proof of Theorem 2

Write F ∈ V as F = A + kC with A, C ∈ F[Y]_(<h/2); this is a linear isomorphism, since F[k] = F[Y] ⊕ kF[Y] and deg F < h exactly
when deg A, deg C < h/2. Then τF = A + (k + 1)C and, in characteristic 2,

(k + 1)τF + Ω(w)F = A·(Ω(w) + k + 1) + C·(kΩ(w) + (k + 1)²) = N_w·A + D_w·C.

D_w has constant term 1, so it is a unit mod k^h, and Z(w)F = D_w·(ψ(w)A + C) mod k^h. Through the ring isomorphism
ι: F[Y]/(Y^h) → F[k]/(k^h), Y ↦ k² + k (Y has valuation 1), this is Z(w) = M_(D_w) ∘ ι ∘ Π(w) ∘ (the isomorphism F ↦ (A, C)), with
Π(w)(A, C) = ψ(w)A + C mod Y^h. Split F[Y]/(Y^h) into the parts of degree below h/2 and from h/2 on: Π(w)(A, C) = ((ψA)_(<h/2) + C,
(ψA)_(≥h/2)). The substitution C ↦ C + (ψ(w)A)_(<h/2) is analytic in w and invertible, and turns Π(w) into (A, C) ↦ (C, T(w)A) with
T(w)A = (ψ(w)A)_([h/2, h)), whose matrix is [ψ_(h/2+i−j)]; reversing the order of the input basis makes it [ψ_(i+j+1)] = H(w). All the
other factors are invertible and analytic near a, so Z(w) is equivalent to diag(H(w), I). (At w = a this is
`KLOOSTERMAN-BOUNDS-20261110-001A`, Theorem 4.) ∎

## Proof of Theorem 3

ε_(2t) = ε_t for t ≥ 1, and ε_(2t+1) = 1 only for t = 0. Write J = ⌈k/2⌉ and Γ = Γ^(k).

- **k = 2c.** J = c and i + j ≤ 2c − 2, so an entry with i + j odd is ε of an odd number above 1, hence 0. For i = 2i′, j = 2j′ the
  entry is ε_(2(c−i′−j′)) = Γ^(c)_(i′j′), and for i = 2i′ + 1, j = 2j′ + 1 it is ε_(2(c−1−i′−j′)) = Γ^(c−1)_(i′j′); the index ranges are
  i′ < ⌈c/2⌉ and i′ < ⌈(c − 1)/2⌉. So Γ is Γ^(c) ⊕ Γ^(c−1) after sorting the indices by parity.
- **k = 2c + 1.** J = c + 1. An entry with i + j even is nonzero only if 2c + 1 − i − j = 1, i.e. at the corner i = j = c. For
  i = 2i′ and j = 2j′ + 1 the entry is ε_(2(c−i′−j′)) = Γ^(c)_(i′j′). After sorting by parity, Γ = [[D_e, B], [Bᵀ, D_o]] with B the
  even-by-odd block, B_(i′j′) = ε_(c−i′−j′), and the corner in D_e or D_o. If c is odd, B is Γ^(c) and the corner lies in D_o while
  D_e = 0, so det Γ = det(B)². If c is even, B has one more row than columns, its first c/2 rows form Γ^(c), and the corner is the
  single entry of D_e, in the extra row's position; expanding along that 1 (a Schur complement) gives det Γ = det(Γ^(c))².

With det Γ^(0) = 1 (empty), Γ^(1) = Γ^(2) = [1], every determinant is 1 by induction. For the second form: reversing rows and columns
turns Γ^(k) into [g_(c′+i+j)] with g_t = ε_(t+1) and c′ = k + 1 − 2J ∈ {0, 1}; g = Σ z^(2^r − 1) satisfies zg² = g + 1 over GF(2), so
g(1 + zg) = 1 and g = 1/(1 + zg), the S-fraction with every coefficient 1, whose Hankel determinants are products of its coefficients
(Stieltjes). ∎

## Proof of Theorem 4

From Theorem 1, Z(a + δ) = S + (1 + u)(Ω_a + E) mod δ^n with E = Σ_r δ^(2^r) k^(h−2^(r−1)). With λ = u/(1 + u), 1 + u = 1/(1 + λ) in
characteristic 2, so (1 + λ)Z = (1 + λ)S + Ω_a + E = Z_0 + λS + E, and δ^(2^r) = a^(2^r)λ^(2^r)/(1 + λ)^(2^r) =
a^(2^r)λ^(2^r)/(1 + λ^(2^r)). The factor 1 + λ is a unit and λ ↦ u has nonzero derivative, so the partial multiplicities agree. ∎

## Proof of Theorem 5

Write B_r for the bilinear form of [λ^r]Ẑ: B_1(x, y) = ⟨Sx, y⟩ = [k^(h−1)](τx·y), B_2(x, y) = a²x(0)y(0) (as ⟨k^(h−1)F, F′⟩ = F(0)F′(0)),
B_3 = 0. For x ∈ K the reduction's vector is Φ_x = x + Σ_(r≥1) λ^r ψ_r(x) with ψ_r(x) ∈ W′ and B(λ)(Φ_x, w) = 0 for all w ∈ W′; then
M(x, y) = B(λ)(Φ_x, y), so [λ^r]M(x, y) = Σ_(r′=1)^r B_(r′)(ψ_(r−r′)(x), y) with ψ_0 = x (B_0 vanishes against K).

**First vector.** For x = G·Y^i with 2i < k − 1, Z_0(kx) = Sx (`JORDAN-CHAINS-20261110-001A`, the lemma), so kx ∈ W′ satisfies
B_0(kx, w) + B_1(x, w) = 0, and ψ_1(x) = kx.

**Orders one and two.** [λ]M(x, y) = B_1(x, y) = [Y^(h−1−i−j)]N (Theorem 3 there), zero for i + j ≤ k − 2. Next
[λ²]M(x, y) = ⟨S(kx), y⟩ + a²x(0)y(0) = [k^(h−1)]((k + 1)N·Y^s) + a²G(0)²[s = 0], s = i + j. The identity (k + 1)τG = Ω_aG + k^h R_G
(exact, as G ∈ K) gives (k + 1)N ≡ Ω_aG² mod k^h, so [k^(h−1)]((k + 1)NY^s) = [k^(h−1)](Ω_aG²Y^s). Recall that [k^(h−1)](Ω_aP) =
b[k^(h−1)]P + Σ_(i′=2)^m b^(2^i′)[k^(2^(i′−2)−1)]P.
- s = 0: G² has only even powers, so only i′ = 2 contributes, b⁴G(0)² = a²G(0)², which cancels a²G(0)².
- s ≥ 2 even: G²Y^s = (GY^(s/2))² has only even powers and no constant term, so every term vanishes (and x(0)y(0) = 0).
- s odd: put H = G·Y^((s−1)/2) with coefficients h_c. Then G²Y^s = H²k + H²k², whose odd coefficients are [k^(2c+1)] = h_c², so
  [k^(h−1)](Ω_aG²Y^s) = b h_(h/2−1)² + Σ_(i′≥3) b^(2^i′) h_(2^(i′−3)−1)² = (Σ_(r=0)^(m−2) b^(2^(r+2)) h_(2^r − 1))², using
  b^(1/2) = b^(2^m) in GF(2^(m+1)). The sum is [k^(h−1)]((Ω_a − b)H) = [k^(h−1)](Ω_aH) − b[k^(h−1)]H. Now H ∈ K, so
  Ω_aH ≡ (k + 1)τH mod k^h, a polynomial of degree deg H + 1 = h − k + s ≤ h − 2; both coefficients of k^(h−1) vanish.

**Order three.** For 2j < k − 1 as well, Sy = Z_0(ky), so the self-adjointness of S and Z_0 gives
⟨Sψ_2(x), y⟩ = ⟨ψ_2(x), Z_0(ky)⟩ = ⟨Z_0ψ_2(x), ky⟩. The vector ψ_2(x) is defined by
⟨Z_0ψ_2(x) + S(kx) + a²x(0)k^(h−1), w⟩ = 0 for all w ∈ W′; take w = ky ∈ W′ (and (ky)(0) = 0): ⟨Z_0ψ_2(x), ky⟩ = ⟨S(kx), ky⟩. So
[λ³]M(x, y) = ⟨Sψ_2(x), y⟩ + B_2(kx, y) + B_3(x, y) = ⟨S(kx), ky⟩ = [k^(h−1)]((k + 1)k·τx·y) = [k^(h−1)](N·Y^(s+1)) =
[Y^(h−2−s)]N, since [k^(h−1)]P = [Y^(h−1)]P for P ∈ F[Y] (`JORDAN-CHAINS-20261110-001A`, proof of Theorem 3). It is lc(N) = 1 at
s = k − 2 and 0 for s < k − 2, as deg N = h − k.

**The blocks.** Let K′ = span{G·Y^i : 2i < k − 1}. For k even K′ = K and M = O(λ³) by the orders one and two. For k odd, K = K′ ⊕ C
with C spanned by G·Y^(J−1); M_CC = λ(1 + O(λ)) (Theorem 3 there: the corner of the first-order matrix is lc(N) = 1), and
M_(K′C) = O(λ³) (the pairs have s ≤ k − 2 and 2i < k − 1). The Schur complement M′ = M_(K′K′) − M_(K′C)M_CC⁻¹M_(CK′) then has
M′ ≡ M_(K′K′) mod λ⁵, and the partial multiplicities of M are {1} together with those of M′. In both cases the matrix on K′ is
λ³·(N′ + O(λ)) with N′ = [[Y^(h−2−i−j)]N] on K′, so its blocks of size 3 number rank N′: for k even N′ is zero but for its corner
i = j = J − 1 (s = k − 2), rank 1; for k odd all its entries have s ≤ k − 3, rank 0. No block has size 2, and all other blocks have
size at least 4. For k = 1 this is [1]; for k = 2, J = 1 and the one block is 3. ∎

## Checks

`check.py` (one process, about two minutes; `--write` rewrites `result.json`):
- **0.** The dependencies (`JORDAN-CHAINS-20261110-001A`'s manifest and library) bound by hash.
- **1.** Theorem 1 against the exact Taylor coefficients, every a, sides 4 to 128.
- **2.** Theorem 2: the partial multiplicities of H(w) against those of Z(w), every a, sides 8 to 32, and against 2k − 1 − 4j (the
  blocks of Z by the registered run JORDAN-CHAINS-A1) at side 64.
- **3.** Theorem 3 for k < 1000.
- **4.** Theorem 4 against the family built from the exact Taylor coefficients, every a, sides 4 to 64.
- **5.** Theorem 5: the first three orders with the complement W′, and the vanishing of the first two orders with the monomial complement,
  every a, sides 8 to 128.
- **6.** The leading form, the target, every a, sides 8 to 128.
- **7.** The stress run (`research/CHAIN-ORDERS-20261110-001/stress_test.json`, CHAIN-ORDERS-S1): the leading form at every a of side 256.
- **8.** The reading's comparison: over GF(2), the blocks of the exterior square of one Jordan block of size k + 1 (group and Lie
  actions) and of the symmetric square of one of size k, against 2k − 1 − 4j, k = 1 to 15.
