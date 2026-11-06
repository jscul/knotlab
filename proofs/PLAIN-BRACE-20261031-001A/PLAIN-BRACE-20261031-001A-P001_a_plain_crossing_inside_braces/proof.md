# A plain crossing inside braces

Status: Proved

Ticket `PLAIN-BRACE-20261031-001A`, 2026-10-31.

**What it uses:**
- **`PLAIN-COUNT-20261031-001A`:** the Pfaffian certificate on instances whose pieces are found as components (`plain_lib`).
- **`SOFT-CROSS-20261031-001A`:** the certificate argument of Theorem 5 (`SEYMOUR-COUNT-20261030-001A`, Lemma 1(iii);
  `THREEFOLD-AMPLITUDE-20261030-001C`, Lemma 4) and the multi-site interpolation scheme.
- **`TWIST-COUNT-20261030-001A`:** junction tensors and twisted branches.
- **`PLAIN-COUNT-20261031-001B`:** the brace test (`page_lib`).
- **External, not replayed:**
  - Kasteleyn's theorem;
  - Vandermonde systems with distinct nodes are invertible;
  - unique factorization in the Eisenstein integers Z[ω], whose units are the sixth roots of unity.

## Why this ticket exists

`PLAIN-COUNT-20261031-001` proved plain triple systems with Pfaffian incidence graphs hard to count. Its instances, however, contain 2-edge
cuts (caps and long edges), so none is a brace, and a single junction of plain pages is never a crossing. This ticket builds an exact
crossing, by interpolation, inside braces, from nothing but plain cubes.

## Standard statement

**Setting.**
- **The cube junction.** A square (c0, c1, c2, c3), with c0 and c2 points, is glued by trisum to two plain cubes, and its square edges are
  deleted. Its tensor W(z0, z1, z2, z3) is a 4 × 4 matrix from (z0, z1) to (z2, z3), where:
  - z0, z2 are the colours of c0, c2;
  - z1, z3 are the colours of the host neighbours of c1, c3.
- **A site with k junctions** replaces a crossing of edges e (wire A) and f (wire B).
  - Wire A runs from e's point end: point end − l_s − c0 [junction 0] c2 − λ₀ − c0 [junction 1] … c2 [junction k−1] − line end.
  - Wire B runs from f's line end: line end − π_s − c1 [junction 0] c3 − π₀ − c1 [junction 1] … c3 [junction k−1] − point end.
  - The start rung l_s − π_s and the rungs λ_j − π_j between junctions close every leg. There are no caps.
  - N is the rung's matrix: N[(z2, z3), (a, b)] = NAE(z2, a, b)·[z3 = b].

**Results.**
- **Lemma 1 (the site is a matrix power).** As a map from (colour of e's point end, colour of π_s) to (colour seen by e's line end, colour of
  f's point end), the site acts by (NW)^k. Restoring e and f is the identity.
- **Lemma 2 (the cube junction).** All 24 labellings of a plain cube page give one tensor. S′ = NW is

  [[2, 3, 2, 5], [8, 4, 8, 9], [9, 8, 4, 8], [5, 2, 3, 2]],

  with characteristic polynomial (x² − 19x − 1)(x² + 7x + 13).
- **Lemma 3 (the lattice condition).** The eigenvalues are ε, −1/ε, π and π̄:
  - ε = (19 + √365)/2 is a unit of norm −1;
  - π = (−7 + i√3)/2 is an Eisenstein prime of norm 13.

  So for count vectors n ≠ n′ in ℕ⁴ of equal total, Π λ_i^{2n_i} ≠ Π λ_i^{2n′_i}.
- **Theorem 4 (a plain crossing).** For a single site, the count with the crossing restored is Σ_j f_j Z(2j + 1), where Z(k) is the count with
  k junctions and

  f = (−53451621/2804438, 521319/200317, −23524/200317, 853/2804438)

  is the unique cubic with x f(x²) ≡ 1 modulo the characteristic polynomial.
  - For m sites with a shared odd k, C(m + 3, 3) counts determine the count with every crossing restored.
  - Only odd k give planar hosts.
- **Corollary 5 (K₃,₃).** #col(K₃,₃) = 6 is recovered from plain instances with 1, 3, 5 and 7 junctions (20, 48, 76 and 104 vertices). Each
  instance:
  - is cubic bipartite and carries no sign;
  - is certified Pfaffian and non-planar;
  - has a planar, cyclically 4-edge-connected host;
  - has three twisted branches at every junction;
  - passes the direct brace test (20, 48 and 76 vertices).

## Nearest known result

- **Crossovers by interpolation are standard** (Valiant; Cai, Lu and Xia), and so is the hardness of the problem on general graphs (Fan and
  Cai 2020).
- **New** (no overlap found, candidate local delta): a crossing simulated inside plain Pfaffian braces, from plain cubes. Also new are the
  reversed site that makes it a matrix power, and its arithmetic.

## Proof of Lemma 1

**Each piece is a factor.**
- The start rung l_s is a line on e's point end (colour x), c0(0) (colour a) and π_s (colour y). π_s is c1(0)'s host neighbour, so y is
  carried on wire B. As a map (x, y) ↦ (a, y), l_s is N.
- Each junction maps (c0, c1's neighbour) to (c2, c3's neighbour) by W.
- Each rung λ_j − π_j maps (c2(j), π_j) to (c0(j+1), π_j) by N, with π_j being c3(j)'s and c1(j+1)'s host neighbour.

**The product.** The site is N W N W … N W = (NW)^k, from (x, y) to (colour of the last c2, colour of f's point end).

**The original edges.**
- e's line end sees the last c2, and f's line end sees π_s.
- Restoring e and f makes e's line end see x and f's line end see f's point end: (s_A, s_B) = (x, y), which is the identity.

**Check.** Section 2 confirms Z(k) = Σ R (S′)^k on K₃,₃ for k = 1, …, 7, R being the rest of K₃,₃ (80, 1680, 31500, … up to 4159886188). ∎

## Proof of Lemma 2

Computation (section 1). The cube's symmetry group acts transitively on labelled squares, so all labellings give one tensor. ∎

## Proof of Lemma 3

**The two numbers.**
- **ε is a unit, not a root of unity.** ε·(19 − √365)/2 = (361 − 365)/4 = −1, so ε̄ = −1/ε. Since ε > 1, ε is no root of unity.
- **π and π̄ are non-associate primes.** ππ̄ = (49 + 3)/4 = 13, a rational prime that splits in Z[ω] into π and π̄.
- **π/π̄ is not a root of unity.** The roots of unity in Q(ω) have order dividing 6, and (π/π̄)⁶ ≠ 1.

**Suppose two products coincide.** If Π λ^{2n} = Π λ^{2n′} with a = n₁ − n₂, b = n₃, c = n₄, then

ε^{2(a−a′)} = π^{2(b′−b)} π̄^{2(c′−c)}.

- **Both sides are rational.** The left side lies in Q(√365) and the right in Q(√−3), whose intersection is Q.
- **The π side.** A rational πʲπ̄ˡ equals its conjugate π̄ʲπˡ, so (π/π̄)^{j−l} = 1 and j = l. The right side is then 13^{2(b′−b)}.
- **The ε side.** A rational εʲ equals ε̄ʲ = (−1/ε)ʲ, so ε^{2j} = ±1 and j = 0. Hence a = a′, and then b = b′ and c = c′.
- **Conclusion.** With n₁ − n₂ = n′₁ − n′₂ and equal totals, n = n′.

**Check.** Section 3 confirms the certificate, and the distinctness numerically for every total m ≤ 8. ∎

## Proof of Theorem 4

**A single site.**
- Z(k) = ⟨R, S′^k⟩ by Lemma 1.
- **Finding f.** The λ_i are nonzero and the λ_i² distinct, so some cubic f has λ_i f(λ_i²) = 1 for all i, that is, S′ f(S′²) = I.
- **f is rational.** It is unique, and the characteristic polynomial is rational, so f is Galois-stable. Section 4 solves x f(x²) − 1 ≡ 0
  modulo (x² − 19x − 1)(x² + 7x + 13) over Q.
- So ⟨R, I⟩ = Σ_j f_j Z(2j + 1).

**Many sites.**
- Expand every site's S′^k = Σ_i λ_i^k P_i. The count with all sites at the same odd k = 2t + 1 is Σ_n (Π λ^n)(Π λ^{2n})^t A_n, over count
  vectors n of total m.
- By Lemma 3 the nodes Π λ^{2n} are distinct. So t = 0, …, N − 1 with N = C(m + 3, 3) determine every A_n, and the count with every
  crossing restored is Σ_n A_n.

**Why odd k.** A site with an even number of junctions makes no net crossing, so the host is not planar (section 5). ∎

## Proof of Corollary 5

Computation (sections 4 and 5):
- **Recovery.** The rational formula and the algebraic Vandermonde solve both give 6 from Z(1), Z(3), Z(5) and Z(7).
- **Certificates and tests.** The instances are certified and tested as listed.
- **The brace property in general.** It follows from ticket B's cube junction lemma and Hall's condition. ∎

## What the computation checks

`check.py` (about 30 seconds):
- **1–4:** as above.
- **5, the instances and the even-k control.** For k = 2, 4 and 6 the host is not planar.
- **6, controls:**
  - a single plain cube junction is not a crossing (nonzero turning entries);
  - three counts cannot give the identity (no solution with f₃ = 0);
  - the 21 distinct plain ladder steps built from cube, prism and truncated-octahedron pages are nonsingular, and each generates a
    4-dimensional commutative algebra.
- **Observations (not controls):**
  - SOFT-CROSS A's unreversed site, with its cap replaced by a rung, also spans the exact crossing for this junction;
  - pairs of steps from this family generate 6 dimensions, not the full 8.

## Reading

- **A plain junction is never a crossing, but a ladder of them is.** The crossing hides in (NW)^k as its k = 0 term, and interpolation brings
  it out. It does so inside braces, the most connected of the knot's graphs, with nothing but plain cubes.
- **The arithmetic of the crossing.** Its four rates are a unit of Q(√365) and the two Eisenstein primes above 13.
  - The Eisenstein integers are where the knot's own angle lives. The junction's similitude multiplier in `TWIST-COUNT`,
    α² + αβ + β² = |α + β e^{iπ/3}|², is the same norm form, and 13 = 3² + 3·1 + 1².
  - This is an observation, not a claim.

## Nonclaims

- **The reversal is a convenience.** For this junction the unreversed site also works. The reversed one is chosen for its matrix-power form
  and its rational recovery formula.
- **The brace property of general instances is ticket B's.** Here it is tested on the K₃,₃ instances.
- **Many sites are proved, not run.** K₃,₃ has a single crossing.
