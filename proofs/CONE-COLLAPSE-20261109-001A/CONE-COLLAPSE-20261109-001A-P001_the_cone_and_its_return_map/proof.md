# The cone and its return map

Status: Proved by hand (Theorems 1 to 4, with finite checks 1 to 3 of `check.py`); the Smith form (check 4) and the laws of checks 5
to 8 are exact computations at sides 4 to 64. The collapse at every power of two is not proved.

Ticket `CONE-COLLAPSE-20261109-001A`, 2026-11-09.

## Standard statement

- **The walk.** As in `FULL-REACH-PROOF-20261108-001A`: the contacts of the n × n torus of rule-60 rings cut open both ways are the
  points (X, Y) of [0, N]², N = 2n − 2, with X + Y odd (h: X odd, v: X even). An h reads (X ± 1, Y ± 1) with equal signs, a v reads
  (X ± 1, Y ∓ 1); a read that leaves the box dies. A[c, d] = 1 when c reads d, over GF(2). In graph terms A is the adjacency matrix
  of the alternating medial digraph of the n × n grid with the outer face's arcs removed. The uncut walk M lives on the side-2n
  torus (coordinates mod 2n); the box is the torus without the cut lines C1 = {(2n − 1, 2y)} and C2 = {(2x, 2n − 1)}, x, y ∈ Z_n.
- **The question.** `FULL-REACH-PROOF-20261108-001` computed that every eigenvalue of A is a (2n − 1)-th root of unity exactly at
  n = 4, 8, 16, 32, 64 among sides 3 to 64, and reduced the spectrum at n = 2^m to det R_CC(w), R(w) = Σ_k w^k M^k. Its direction 1:
  prove the collapse at every power of two.

**Theorem 1 (two particles).** On the 2n − 1 sites 0, ..., N of a side let T_e and T_o swap the two ends of every even and every odd
bond {e, e + 1}, and let R and L be the shifts with R[x, x + 1] = 1 and L[x + 1, x] = 1. Index the contact (X, Y) by the Kronecker pair
(Y, X). Then on the contacts

A = T_e ⊗ R + T_o ⊗ L = L ⊗ T_e + R ⊗ T_o.

A contact reads by moving its Y across its even bond while X steps right, or across its odd bond while X steps left; equally by
moving its X across its even bond while Y steps down, or across its odd bond while Y steps up.

**Theorem 2 (the cone).** At every side the quarter turn ρ(X, Y) = (Y, N − X) maps contacts to contacts, has no point of period 1 or
2, and commutes with A. Let A_cone be the walk on the T = n(n − 1)/2 orbits, A_cone[o, o′] = the number of contacts of o′ read by
one contact of o, mod 2. Then over GF(2)

det(xI − A) = det(xI − A_cone)⁴.

**Theorem 3 (the dyadic resolvent).** At n = 2^m, on the side-2n torus M² = τ₂ and M^(2^j) = τ_(2^j) for j ≥ 1, where τ_d is the sum of
the four translations by d along the axes; so M^n = 0 and

R(w) = (I − wM)⁻¹ = (I + wM) ∏_{j=1}^{m−1} (I + w^(2^j) τ_(2^j)).

**Theorem 4 (the return map).** Let n = 2^m ≥ 2, G = R_{C1C1}, H = R_{C1C2} (rows indexed by y, columns by x), J the reversal
x ↦ n − 1 − x and K = S + S⁻¹ the circle's walk on Z_n. Then

1. G = R_{C2C2} = (I + w²K)⁻¹, R_{C2C1} = HJ, and JHJ = H;
2. with B = G⁻¹H = (I + w²K)H and C = BJ, det(I − wA) = det(I + C)²;
3. C commutes with J, and with C_s the (n/2) × (n/2) matrix C_s[i, k] = C[i, k] + C[i, n − 1 − k] (i, k < n/2), the action of C on
   the J-symmetric vectors, det(I + C) = det(I + C_s)²;
4. det(I − wA_cone) = det(I + C_s(w)).

Every entry of C is an odd polynomial in w of degree at most n + 1. B is the cut lines' first-passage matrix: B[y, x] counts the walks
from (2n − 1, 2y) to (2x, 2n − 1) that do not come back to C1, by length.

**Computed (checks 4 to 8; the stress run at 128 pending).**
- **The Smith form.** At 4, 8 and 16 the nontrivial invariant factors of I + C_s(w) over GF(2)[w] are those of I − wA_cone: the i-th
  largest is the product over eigenvalue classes of rev(m_λ)^(b_i(λ)), b_i(λ) the i-th largest Jordan block of λ.
- **The Jordan law.** At 4, 8, 16, 32 and 64 every eigenvalue λ of A_cone is a (2n − 1)-th root of unity, with algebraic multiplicity
  k(k + 1)/2 for an integer k = k_λ ≥ 0 and Jordan blocks of sizes 2k − 1, 2k − 5, 2k − 9, ..., down to 1 or 3.
- **The parity law.** The multiplicity k_λ(k_λ + 1)/2 is odd exactly when Tr(1/λ) = 1, Tr the trace of GF(2n) over GF(2).
  Equivalently tr(A_cone^j) = 1 exactly when j is a power of two modulo 2n − 1 (checked for j = 1 to 2n − 1).
- **Stability.** P_n(w) = det(I − wA_cone) at sides n and 2n agree below degree 2n and differ at degree 2n (n = 4 to 32).
- **The return map's characteristic polynomial.** det(z + C_s) = Σ_j e_j z^(n/2 − j) with e_1 = w + w³, the w-adic valuation of
  e_j equal to j(2j − 1), e_(n/2) = w^(n(n − 1)/2) and e_(n/2 − 1) = w^((h − 1)(2h − 3)) (Σ_{i<m} w^(2^i − 1))², h = n/2 (sides 4 to 32).
  So the eigenvalues of C_s have w-adic valuations 1, 5, 9, ..., 2n − 3, and tr C_s⁻¹ = w^(−(2n − 1)) Σ_{i=1}^{m} w^(2^i).

**Open.** The collapse itself at every power of two, and the laws above beyond 64.

## Nearest known result

- **Ingredients.** Schur complements of a unimodular polynomial matrix; modules over GF(2)[Z/4] = GF(2)[ε]/(ε⁴); Frobenius on
  commuting translations (Lucas' theorem); the Clebsch–Gordan decomposition Sym²(V_k) = V_(2k−1) ⊕ V_(2k−5) ⊕ ... of sl₂.
- **Classification.** New as far as found; no literature search beyond these ingredients was made. The Jordan law is not the
  symmetric square of a Jordan block in characteristic 2 (whose type differs at every k ≥ 2) nor its exterior square (which agrees
  only at k ≤ 2 and k = 4; the table is in the decision note): it is the characteristic-0 pattern, appearing in characteristic 2.

## Proof of Theorem 1

Let (X, Y) be a contact. If Y is even, its even bond is {Y, Y + 1} and its odd bond {Y − 1, Y}, so T_e ⊗ R sends it to (X + 1, Y + 1)
and T_o ⊗ L to (X − 1, Y − 1); Y even means X odd, an h, whose reads are exactly these. If Y is odd, its even bond is {Y − 1, Y} and
its odd bond {Y, Y + 1}, giving (X + 1, Y − 1) and (X − 1, Y + 1), the reads of a v. Site N lies on no even bond (N is even and N + 1
is outside) and site 0 on no odd bond, and R and L have no image outside [0, N]; so a move is absent exactly when the read leaves the
box. The second form is the same argument with X and Y exchanged: if X is odd its even bond {X − 1, X} comes with Y − 1 (L) and its
odd bond {X, X + 1} with Y + 1 (R), giving (X − 1, Y − 1) and (X + 1, Y + 1); if X is even, (X + 1, Y − 1) and (X − 1, Y + 1). ∎

So A moves two particles on one segment at once, the X particle and the Y particle; which way the second goes depends on the bond
the first crosses. Over two steps the first returns and the second moves two sites, so away from the box's edges A² is the sum of two
independent walks; at the top and bottom rows (and the left and right columns for v) one direction of the move is lost
(`FULL-REACH-PROOF-20261108-001A`, Theorem 5).

## Proof of Theorem 2

ρ keeps X + Y odd (Y + N − X ≡ X + Y, N even) and the box. ρ²(X, Y) = (N − X, N − Y) fixes only (n − 1, n − 1), where X + Y = 2n − 2 is
even, not a contact; so every orbit has four contacts. ρ sends an h at (X, Y) to the v at (Y, N − X) and its reads (X ± 1, Y ± 1) to
(Y ± 1, N − X ∓ 1), the reads of that v; likewise for a v. So ρAρ⁻¹ = A.

Let V be the GF(2)-space on the contacts, a module over Λ = GF(2)[ρ] = GF(2)[ε]/(ε⁴), ε = ρ + 1 (ρ⁴ = 1 and (ρ + 1)⁴ = ρ⁴ + 1 = 0).
Since ρ acts freely, V is free over Λ of rank T, with one contact of each orbit as a basis. A commutes with ε, so the chain
V ⊃ εV ⊃ ε²V ⊃ ε³V ⊃ 0 is A-invariant, and for j ≤ 3 multiplication by ε^j induces an A-equivariant map V/εV → ε^jV/ε^(j+1)V, onto,
between spaces of dimension T (V ≅ Λ^T and ε^jΛ/ε^(j+1)Λ ≅ GF(2)), hence an isomorphism. The characteristic polynomial of A is the
product of those on the four quotients, each that of A on V/εV. In the basis of orbit classes [o], A[e_r′] = Σ_{c reads r′} [e_c], and
the coefficient of [o] counts the contacts of o reading r′, which by the symmetry equals the number of contacts of o′ (the orbit of r′)
read by one contact of o: the matrix is A_cone. ∎

## Proof of Theorem 3

From an h at (X, Y), M reads (X ± 1, Y ± 1), v contacts, which read (X ± 2, Y) and (X, Y ± 2); from a v the same. So M² = τ₂, the sum
of the four translations by 2 along the axes, on any torus. Translations commute, so over GF(2) (τ₂)^(2^(j−1)) = τ_(2^j): the cross
terms cancel in pairs. On the side-2n torus a translation by n equals its inverse, so τ_n = 2(t_X^n + t_Y^n) = 0 and M^n = 0. Then
(I − wM)⁻¹ = Σ_{k<n} (wM)^k = ∏_{j=0}^{m−1} (I + (wM)^(2^j)), by the binary expansion of k (each k < n uniquely). ∎

## Proof of Theorem 4

(1) ρ extends to the torus as (X, Y) ↦ (Y, −2 − X) mod 2n and is a symmetry of M (the proof of Theorem 2), so R[ρc, ρc′] = R[c, c′].
It sends (2n − 1, 2y) to (2y, 2n − 1), the point of C2 with x = y, and (2x, 2n − 1) to (2n − 1, 2(n − 1 − x)), the point of C1 with
y = n − 1 − x. So R_{C2C2} = G, H[y, x] = R_{C2C1}[y, n − 1 − x] (R_{C2C1} = HJ), and applying ρ twice, H[y, x] = H[n − 1 − y, n − 1 − x]
(H = JHJ). G = (I + w²K)⁻¹ is Theorem 4 of `FULL-REACH-PROOF-20261108-001A` (from Theorem 3: a walk from C1 back to C1 has zero net
X-displacement, which over GF(2) leaves only the Y-translations, ∑_j w^(2j) K^j).

(2) R_CC = [[G, H], [HJ, G]] (C1 then C2). det G = 1, since G⁻¹ = I + w²K and K is nilpotent (K^(n/2) = S^(n/2) + S^(−n/2) = 0). By
the Schur complement, det R_CC = det G · det(G − HJG⁻¹H) = det(I + G⁻¹HJG⁻¹H) over GF(2). G is a symmetric circulant, so GJ = JG;
JH = HJ by (1); so B = G⁻¹H commutes with J, G⁻¹HJG⁻¹H = BJB = B²J, and with C = BJ, C² = B²: det R_CC = det(I + C²J). Write
J = I + N with N² = 0 (J² = I), N commuting with C. Then I + C²J = (I + C²)(I + (I + C²)⁻¹C²N), the second factor is unipotent
((XN)² = X²N² = 0 for X commuting with N), and I + C² is invertible over GF(2)(w) (C has no constant term: H counts walks between the
disjoint lines). So det R_CC = det(I + C²) = det(I + C)². Finally det(I − wA) = det R_CC (`FULL-REACH-PROOF-20261108-001A`,
Theorem 4).

(3) C commutes with J, so it preserves S = ker(J + I), of dimension n/2 with basis s_k = e_k + e_(n−1−k), k < n/2 (J has no fixed
point, n being even). (J + I)V = S, since s_k = (J + I)e_k and dim (J + I)V = n − dim S = n/2. So J + I induces a C-equivariant
isomorphism V/S → S, and det(I + C) = det(I + C|_S) det(I + C|_(V/S)) = det(I + C|_S)². The vector Cs_k lies in S, so it is
Σ_{i<n/2} c_i s_i with c_i its coefficient on e_i, C[i, k] + C[i, n − 1 − k]: the matrix of C|_S is C_s.

(4) By (2) and (3), det(I − wA) = det(I + C_s)⁴; by Theorem 2, reversed, det(I − wA) = det(I − wA_cone)⁴. Over GF(2), f⁴ = g⁴ gives
(f + g)⁴ = 0, so f = g.

Parity and degree: a walk alternates h and v contacts, so walks from C1 (h) to C2 (v) have odd length; R has degree below n and
G⁻¹ = I + w²K raises it by 2. First passage: decomposing a walk from C1 to C2 at its last visit to C1 gives H = G·F, F the generating
matrix of walks that leave C1 and do not return, so F = G⁻¹H = B. ∎

## Checks

`check.py` (one process, about two minutes; `--write` rewrites `result.json`):
- **0.** The dependency (`FULL-REACH-PROOF-20261108-001A`'s manifest) bound by hash.
- **1.** Theorem 1 at sides 2 to 16.
- **2.** Theorem 2: freeness, commutation and the ranks T(4 − j) of (ρ + 1)^j at sides 2 to 12; charpoly(A) = charpoly(A_cone)⁴ at
  2 to 8.
- **3.** Theorem 4 at sides 2, 4, 8, 16 (the block relations, G⁻¹, CJ = JC, odd entries), with det(I − wA_cone) = det(I + C_s) at 4,
  8, 16 and det(I − wA) = det(I + C)² = det(I + C_s)⁴ at 4 and 8.
- **4.** The Smith form at 4, 8, 16 against the Jordan blocks of check 5.
- **5.** For every class of (2n − 1)-th roots of unity at 4 to 64, the kernel dimensions of m_λ(A_cone)^j: the multiplicities fill the
  cone (the collapse), are triangular with Jordan blocks 2k − 1, 2k − 5, ..., and are odd exactly when Tr(1/λ) = 1.
- **6.** tr(A_cone^j) for j = 1 to 2n − 1 at 4 to 64.
- **7.** The cone polynomials of n and 2n below degree 2n.
- **8.** The return map's characteristic polynomial at 4 to 32.
- **9.** The stress run at 128 (`research/CONE-COLLAPSE-20261109-001/stress_test.json`), pending at closure.
