# The cut-open torus walk: its symmetries, the torus it comes from, and what is special at powers of two

Status: Proved by hand where marked (Theorems 1 to 5); checks 9 to 12 of `check.py` are computations.

Ticket `FULL-REACH-PROOF-20261108-001A`, 2026-11-09.

## Standard statement

- **The walk.** Let G be the n × n grid graph: its vertices are the rings, its 2n(n − 1) edges the contacts. Each contact reads the
  next contact around each of its two rings, always in the same rotational sense (rule 60), and a read that would need a cut contact
  dies. Over GF(2) this is a 0/1 matrix A on the contacts, A[c, d] = 1 when c reads d: the adjacency matrix of the medial digraph of
  G with the alternating orientation (every ring's contacts form a directed cycle, every inner face's contacts the opposite one),
  with the outer face's arcs removed. (A^k)[c, d] is the number of walks of length k from c to d, mod 2, and c **reads** d when some
  power has (A^k)[c, d] = 1.
- **Coordinates.** Doubled coordinates as in `FULL-REACH-20261108-001A`: the contacts are the points (X, Y) of [0, N]² with
  N = 2n − 2 and X + Y odd; h = X odd, v = X even; an h reads (X − 1, Y − 1) and (X + 1, Y + 1), a v reads (X + 1, Y − 1) and
  (X − 1, Y + 1). T is the null-boundary path walk on the 2n − 1 sites [0, N] (rule 90): T[s, s ± 1] = 1.
- **The question** (`FULL-REACH-20261108-001`). **Full reach** at side n: every contact reads some contact of every ring. Computed:
  it holds at every side from 3 to 48 except 8, 16 and 32. The goal of the epic is a proof that it fails exactly at the powers of
  two from 8.

**Theorem 1 (the walk and its mirror add up to a product).** A + Aᵀ = T ⊗ T on the contacts: c and d are joined in A or in Aᵀ
exactly when they differ by (±1, ±1).

**Theorem 2 (symmetries).** The quarter turn ρ(X, Y) = (Y, N − X) commutes with A; the mirror P(X, Y) = (X, N − Y) and the diagonal
reflection D(X, Y) = (Y, X) carry A to Aᵀ. So PA and DA are symmetric matrices, A is self-adjoint for the pairings xᵀPy and xᵀDy, and
(A^k)[c, d] = (A^k)[Pd, Pc] = (A^k)[Dd, Dc] = (A^k)[ρc, ρd] for every k: c reads d exactly when Pd reads Pc, and exactly when Dd
reads Dc. Full reach is therefore the same statement as "the contacts of every ring together read every contact" (the draft's
Lemma 1, the case P), and every failing set is invariant under the quarter turn.

**Theorem 3 (the torus it comes from).** Let M be the walk on the contacts of the uncut torus of side n (doubled coordinates mod 2n,
the same rule, no deaths). A is the principal submatrix of M on the contacts off the two cut lines X = 2n − 1 and Y = 2n − 1. With
R(w) = (I − wM)⁻¹ = Σ_k w^k M^k and C the 2n cut contacts (n h's on X = 2n − 1, n v's on Y = 2n − 1):

(I − wA)⁻¹ = R_UU − R_UC R_CC⁻¹ R_CU,  det(I − wA) = det(I − wM) · det R_CC(w).

So the box's walk counts are the torus's, corrected through the 2n × 2n cut-set matrix R_CC, and c never reads d in the box
exactly when R_cd(w) = R_cC(w) R_CC(w)⁻¹ R_Cd(w).

**Theorem 4 (at powers of two the torus dies and the cut lines are circles).** Let n = 2^m.
- (a) M^n = 0, and M^(n − 1) ≠ 0.
- (b) R(w) is a polynomial of degree below n, and its block on each cut line is the circulant (1 + w²(s + s⁻¹))⁻¹ =
  Σ_(k < n/2) w^(2k) (s + s⁻¹)^k, the Green's function of a circle of n points (s the shift along the line).
- (c) Hence det(I − wA) = det R_CC(w): the whole spectrum of A, a 2n(n − 1)-dimensional walk, is the determinant of a 2n × 2n matrix of
  polynomials of degree below n, whose diagonal blocks are circle Green's functions and whose off-diagonal blocks count torus walks
  between the two cut lines. The cylinder (the torus cut along one line) is nilpotent too.

**Theorem 5 (a transfer identity, every n).** On the h's, h(i, j) = (2i + 1, 2j) with i ∈ [0, n − 2] and j ∈ [0, n − 1], A² acts as
(M_h f)(i, j) = f(i, j − 1) + f(i, j + 1) + [j ≥ 1] f(i − 1, j) + [j ≤ n − 2] f(i + 1, j). Let L and R be the shifts on [0, n − 2]
(i reads i − 1, i reads i + 1), T_(n−1) = L + R, y = xI + T_(n−1), and u_k the Chebyshev polynomials over GF(2) (u_(−1) = 0, u_0 = 1,
u_(k+1) = y u_k + u_(k−1)). Then

det(xI − M_h) = det( u_n(y) + u_(n−1)(y) L + R u_(n−1)(y) + R u_(n−2)(y) L ),

an (n − 1) × (n − 1) determinant. At n = 2^m: u_(n−1)(y) = y^(n−1), u_(n−2)(y) = 1 + Σ_(r=1)^(m−1) y^(n − 2^r), u_n = y^n + u_(n−2),
and T_(n−1) is a single nilpotent Jordan block, so y^n = x^n.

**Proposition 6 (when one layer is a field).** If the minimal polynomial of A⁴ on a layer is irreducible of degree equal to the layer's
dimension n(n − 1)/2, every contact reads every contact. This holds at sides 3, 5, 7 and 11 and at no other side from 3 to 24
(check 13), so it explains full reach there and nowhere else.

**Computed (exact).**
- **The collapse.** Among sides 3 to 64, every eigenvalue of A is a (2n − 1)-th root of unity exactly at 4, 8, 16, 32 and 64, where
  A^(e(2n − 1)) = I with e = 4, 8, 16, 16 and 32 (the smallest power of two that works, exact; check 9 and the stress run). At every
  other side a random vector's minimal polynomial already has a root of another order, which is a rigorous certificate. At a power of
  two n, GF(2n) is a field and its nonzero elements are exactly the (2n − 1)-th roots of unity, so the spectrum lies in GF(2n); at other
  sides GF(2n) does not exist, and the right statement is the one about roots of unity.
- **Triangular multiplicities.** At 4, 8, 16 and 32 every eigenvalue of A⁴ on a layer has algebraic multiplicity k(k + 1)/2 and
  geometric multiplicity 2k − 1 for some k ≥ 1 (at 16: 15, 10, 6, 3, 1 and 1 for six of the seven classes of GF(32)^*, none for the
  class of ζ⁻¹). Side 64 is in the stress run.
- **The corner's module.** The contact next to a corner reads a module holding each eigenvalue once (a single Jordan block, of size 1
  or 2): degree 40 of a possible 112 at side 8, 108 of 480 at 16, 272 of 1,984 at 32.
- **The failing set** at 8 and 16 is the predicted one (check 11), as in `FULL-REACH-20261108-001A`; the stress run reads 64.

**Open.** The theorem itself: that full reach fails exactly at the powers of two from 8. In particular (i) that every eigenvalue is a
(2n − 1)-th root of unity at every power of two, (ii) the failing set at every power of two, and (iii) full reach at every other side.
Theorem 4 reduces (i) at a power of two to the 2n × 2n polynomial determinant det R_CC(w); Theorem 3 reduces (ii) to an identity
between torus walk counts.

## Nearest known result

- **Rule 90 with null boundaries.** T on 2^r − 1 sites is nilpotent and on other lengths not; the classical analysis is by
  Chebyshev polynomials over GF(2) (Martin, Odlyzko and Wolfram 1984; Sutner's σ-automata). Theorem 5's u_k are those polynomials.
- **Medial graphs over GF(2).** Straight-ahead walks on medial graphs and the bicycle space (Rosenstiehl and Read) concern a
  different orientation; the alternating medial digraph's adjacency over GF(2) is the rule-60 network of this program.
- **Principal submatrices.** Theorem 3's block formula is the Schur complement; using a nilpotent cover to make a finite system's
  spectrum a boundary determinant is standard in transfer-matrix work.
- **Classification.** Theorems 1 to 5 are new as far as found for this walk; their ingredients are classical. No search beyond the
  sources of `FULL-REACH-20261108-001` was made.

## Proof of Theorem 1

Take an h at (X, Y). Its row in A holds (X − 1, Y − 1) and (X + 1, Y + 1), the two diagonal neighbours with equal signs inside the box.
Its row in Aᵀ holds the contacts that read it: a v at (X', Y') reads (X' + 1, Y' − 1) and (X' − 1, Y' + 1), so the readers of (X, Y)
are (X − 1, Y + 1) and (X + 1, Y − 1), the neighbours with opposite signs. Together they are the four points (X ± 1, Y ± 1) in the box,
the row of T ⊗ T. The same holds for a v with the signs exchanged. ∎

## Proof of Theorem 2

ρ sends an h (X odd, Y even) to (Y, N − X), whose first coordinate is even: a v. It sends the h's steps ±(1, 1) to ±(1, −1), the v's
steps, and the v's steps ±(1, −1) to ±(−1, −1), the h's. So c reads d exactly when ρc reads ρd, and ρA = Aρ. P keeps the parity of X
and sends c reading d = c ± (1, 1) (c an h) to Pc and Pd = Pc ± (1, −1); Pd is a v and reads Pd ∓ (1, −1) = Pc. So c reads d exactly
when Pd reads Pc: PAP = Aᵀ. D swaps h and v and sends an h's step (1, 1) to (1, 1) at a v, which is a v's reader's step: as for P,
DAD = Aᵀ. Then (PA)ᵀ = AᵀP = PAPP = PA, and likewise DA. Finally PA^kP = (PAP)^k = (A^k)ᵀ, so
(A^k)[c, d] = (A^k)ᵀ[Pc, Pd] = (A^k)[Pd, Pc], and the same for D; for ρ, (A^k)[ρc, ρd] = (ρA^kρ⁻¹)[ρc, ρd] = (A^k)[c, d]. ∎

## Proof of Theorem 3

The box's contacts are the torus's contacts with X ≤ 2n − 2 and Y ≤ 2n − 2, that is, off the lines X ≡ −1 and Y ≡ −1. A read changes
each coordinate by one, so a box contact reads into the box or onto a cut line, and in the box such a read dies: A keeps exactly the
rows and columns of M off the cut set. The block formula for the inverse of a principal submatrix of I − wM is the Schur complement,
and det(I − wM) = det((I − wM)_UU) · det(((I − wM)⁻¹)_CC)⁻¹ with (I − wM)_UU = I − wA. ∎

## Proof of Theorem 4

Let σ and τ be the translations by (2, 0) and (0, 2) of the torus. They keep each class (h, v) and have order n there. By the read
rule M² acts on each class as Δ = σ + σ⁻¹ + τ + τ⁻¹ (the four two-step moves; the two walks back to the start cancel). Over GF(2) and
for a power of two, (u + v)^(n/2) = u^(n/2) + v^(n/2) for commuting u, v, so Δ^(n/2) = σ^(n/2) + σ^(−n/2) + τ^(n/2) + τ^(−n/2) = 0,
since σ^(n/2) = σ^(−n/2). So M^n = 0. (M^(n − 1) ≠ 0 is check 7.)

R(w) = Σ_(k < n) w^k M^k = (I + wM)(1 + w²Δ)⁻¹, and the class-to-same-class part is (1 + w²Δ)⁻¹ = Σ_k w^(2k) Δ^k with
Δ^k = Σ_(a + b = k) C(k, a) S_σ^a S_τ^b, S_σ = σ + σ⁻¹. A cut line of h's has fixed X, so its block of R keeps the terms with no net
σ-power. The coefficient of σ⁰ in S_σ^a is C(a, a/2) for 0 ≤ a < n/2 (no wrap-around below n), and S_σ^a = 0 for a ≥ n/2; C(a, a/2)
is odd only for a = 0. So the block is Σ_k w^(2k) S_τ^k = (1 + w² S_τ)⁻¹. The line of v's is the same with σ and τ exchanged. Then
det(I − wM) = 1 (M is nilpotent) and Theorem 3 gives det(I − wA) = det R_CC(w). For the cylinder cut along the h-line alone, its
determinant is det((1 + w² S_τ)⁻¹) = 1 because S_τ is nilpotent, so the cylinder's walk is nilpotent. ∎

## Proof of Theorem 5

Write f_j for the row j of f, a vector on [0, n − 2]. M_h acts by (M_h f)_j = f_(j − 1) + f_(j + 1) + X_j f_j with X_0 = R,
X_(n−1) = L and X_j = L + R = T_(n−1) between: it is block tridiagonal with identity blocks off the diagonal. For such a matrix,
det(xI − M_h) = det P_n(x), where P_(−1) = 0, P_0 = I and P_(j+1) = (xI + X_j) P_j + P_(j−1) (the transfer recursion; signs vanish
over GF(2)): elimination of f_1, ..., f_(n − 1) from (xI − M_h) f = 0 expresses f_j = P_j f_0 and leaves the single block condition
P_n f_0 = 0, and the block LU factorization shows the determinants agree. For 1 ≤ j ≤ n − 2 the recursion is P_(j+1) = y P_j + P_(j−1),
whose solution with P_0 = I and P_1 = xI + R = y + L is P_j = u_j(y) + u_(j−1)(y) L (induction; it holds for j = 0 and 1). The last
step uses X_(n−1) = L, that is, xI + L = y + R:

P_n = (y + R)(u_(n−1) + u_(n−2) L) + u_(n−2) + u_(n−3) L = u_n + u_(n−1) L + R u_(n−1) + R u_(n−2) L.

At n = 2^m the Chebyshev identities u_(2k+1) = y u_k² and u_(2k) = (u_k + u_(k−1))² over GF(2) give u_(2^r − 1) = y^(2^r − 1) and
u_(2^m − 2) = (y^(2^(m−1) − 1) + u_(2^(m−1) − 2))², whence the stated sums by induction. T_(n−1) is rule 90 on 2^m − 1 sites, a single
nilpotent Jordan block, so T^n = 0 and y^n = x^n + T^n = x^n. ∎

## Proof of Proposition 6

Let L₀ be a layer and μ the minimal polynomial of Q = A⁴ acting on row vectors of L₀. If μ is irreducible of degree D = dim L₀, then
GF(2)[Q] is the field GF(2^D) and L₀ is a one-dimensional vector space over it, so every nonzero row vector of L₀ generates L₀:
e_c GF(2)[Q] = L₀ for every c in L₀. A is invertible and carries each layer onto the next (Lemmas 2 and 3), so the rows e_c A^k cover
L₀A^r = L_r for r = 0 to 3: their span is everything, and c reads every contact. Q on another layer is conjugate to Q on L₀ by a
power of A. A divisor of μ of degree D found from random vectors is μ itself; one of lower degree rules irreducibility out, since an
irreducible μ of degree D is the minimal polynomial of every nonzero vector. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | `FULL-REACH-20261108-001A`'s frozen contract bound by hash | pass |
| 1–3 | The draft's lemmas: Aᵀ = PAP (sides 2 to 12), the four layers (2 to 12), A invertible (2 to 16) | pass |
| 4 | Theorem 1, sides 2 to 16 | pass |
| 5 | Theorem 2, sides 2 to 16 | pass |
| 6 | Theorem 3, sides 2 to 12 | pass |
| 7 | Theorem 4: M^n = 0 and M^(n − 1) ≠ 0 at 2, 4, 8, 16; the cut-line blocks; det(I − wA) = det R_CC(w) at 2, 4, 8 (characteristic polynomial by Hessenberg reduction) | pass |
| 8 | Theorem 5, sides 2 to 8 (both sides as polynomials over GF(2)) | pass |
| 9 | Computed: the collapse at 4, 8, 16 and at no other side from 3 to 24 | pass |
| 10 | Computed: the triangular multiplicities at 4, 8, 16 | pass |
| 11 | Computed: the failing set at 8 and 16, and 44 and 68 contacts missing some contact | pass |
| 13 | Proposition 6: the layer polynomial irreducible of full degree exactly at 3, 5, 7, 11 among sides 3 to 24 | pass |
| 12 | The stress run (`research/FULL-REACH-PROOF-20261108-001/stress_test.json`): sides 3 to 64, multiplicities at 32 and 64, ring census at 49, 50 and 64 | see the decision note |

## Nonclaims

- **Not the theorem.** Nothing here proves full reach at any side, or its failure at any side not computed.
- **The collapse at powers of two is computed**, to 64; Theorem 4 is the reduction, not its proof.
- **The square grid only**, cut open both ways; rule-60 rings with law (12, 12) contacts (A30, A32, A37, A38).
