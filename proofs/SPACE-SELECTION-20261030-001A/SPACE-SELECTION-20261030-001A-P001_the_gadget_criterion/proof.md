# The gadget criterion: when the wave reproduces itself on a gluing

Status: Proved

Ticket `SPACE-SELECTION-20261030-001A`, 2026-10-30.

**What it uses:**
- `SIMPLEX-GASKETS-20261029-001A`: the standing wave and its exactness on every Sierpinski gasket.
- `WAVE-UNIQUENESS-20261029-001A`: among knots on the gaskets, the wave is forced; the sector method.
- Classical: Seymour's theorem (a minimal non-2-colourable hypergraph has at least as many edges as vertices, 1974), and property B.

## Standard statement

**Setting.**
- **Gadget.** n triangles, each with three slots in roles a (the base), b and c.
  - Corner A fills the base slot of one triangle T_A, corner B the b-slot of one triangle T_B, and corner C the c-slot of one triangle T_C.
  - Every other slot belongs to an *inner vertex*, which collects slots from at least two distinct triangles.
  - The triangles are connected through inner vertices.
  - The gadget is *linear* when two triangles share at most one vertex.
- **Laws and exactness.**
  - A law is a table W[x_a, x_b, x_c] on bits, with spins s = 1 − 2x.
  - The *corner relation* R(x_A, x_B, x_C) is the sum over the inner bits of the product of W over the triangles.
  - W is *exact* on the gadget when R = λW with λ ≠ 0.
  - Substituting the gadget into its own triangles builds a *tower*. It is finitely ramified: copies meet only at corners.
- **The standing wave as a pencil.** For each triangle let E = s_a + s_b + s_c and |x| = x_a + x_b + x_c. Then
  - (−1)^a sin(θE)/sin θ = w_q := K + q·M, with q = sin 3θ / sin θ = 1 + 2 cos 2θ;
  - K = (−1)^a (0, 1, −1, 0)[|x|] is signed not-all-equal, the knot (q = 0);
  - M = [a = b = c] is the all-equal indicator.
  - q = 3 (θ → 0) and q = −1 (θ = π/2) are the degenerate members (−1)^a E and −s_b s_c.
- **Two companion pencils.**
  - The cosine wave: (−1)^a cos(θE)/cos θ = (−1)^a (p, 1, 1, p)[|x|], with p = 2 cos 2θ − 1.
  - The plain pencil without signs: (t, 1, 1, t)[|x|], where t = 0 is plain not-all-equal.
  - As tables they are gauges of one another: w_q = −(s_a s_b s_c)·cos_(−q) and w_q = −(s_b s_c)·plain_(−q).
- **Base count.** m_v is the number of base incidences of an inner vertex v.

**Results.**
- **Lemma 1 (sectors).** Let ζ = e^(iθ) with ζ² ≠ 1. Then

  R_θ(s) = (ζ − ζ⁻¹)^(−n) Σ_ε s_A ζ^(ε_A s_A + ε_B s_B + ε_C s_C) Z(ε),

  where Z(ε) = Σ_σ (Π_t σ_t) Π_v f_v(S_v).
  - The sum runs over sector assignments σ ∈ {±1}^n with (σ_TA, σ_TB, σ_TC) = ε.
  - S_v is the sum of the sectors of the triangles at v.
  - f_v(S) = ζ^S + (−1)^(m_v) ζ^(−S).
  - For the cosine wave, drop Π σ_t and replace ζ − ζ⁻¹ by ζ + ζ⁻¹.
- **Theorem 1 (flip parity is automatic).**
  - Σ_v m_v = n − 1 for every gadget, so Z(−ε) = −Z(ε). The standing wave's corner relation is invariant under complementing the corners,
    on every gadget.
  - The cosine wave's corner relation has parity (−1)^n, so the cosine wave is exact on no gadget with an even number of triangles.
- **Theorem 2 (the criterion).**
  - The eight functions s_A ζ^(ε·s) are independent iff ζ⁴ ≠ 1, i.e. q ∉ {−1, 3}. For such q the wave is exact iff the six mixed sector sums
    Z(ε) (ε not constant) vanish and Z(+++) ≠ 0.
  - Z(+++) = ζ^(3n−3) + lower terms is never identically zero.
  - Every gadget is of one of two kinds:
    - *generic*: R(q) = λ(q)·w_q identically, with λ monic of degree n − 1. The gadget is then exact for every q outside the roots of λ.
    - *special*: the gadget is exact for at most n values of q, the roots of the gcd of the proportionality defects.
  - Generic ⟺ the six mixed sector sums vanish identically.
- **Theorem 3 (mechanisms, and the conjecture refuted).**
  - (a) **Locking.** Suppose every mixed sector assignment meets an inner vertex of odd base count with S_v = 0. Then the gadget is generic.
    - Frames are an instance: T_B and T_C joined to T_A by chains of two-triangle vertices with one base incidence each.
    - At the angle π/k a factor vanishes iff k | S_v (odd base count) or 2S_v ≡ k mod 2k (even base count).
    - Locking in this wider sense gives exactness at q = 1 + 2cos(2π/k) wherever λ ≠ 0: at the knot q = 0 (k = 3), the quarter wave q = 1
      (k = 4) and q = 2 (k = 6).
  - (b) **Balanced cancellation.** Suppose, for each mixed ε, the surviving assignments cancel within classes of equal vertex-factor
    multisets {(m_v mod 2, |S_v|)}. Then the gadget is generic.
  - (c) **Neither is necessary.**
    - The Sierpinski gadget is locked.
    - The twin gadget (A,B,v3)(v4,v5,C)(v3,v4,v6)(v4,v5,v6) is exact by balanced cancellation and is not locked. A flip of its last
      triangle pairs the survivors.
    - Gadgets with six triangles (not linear) and seven (linear) are generic, but their cancellation needs identities between different
      products of vertex factors.
  - (d) **The conjecture.** The recommended criterion "sector locking plus odd flip parity" is therefore refuted as a characterization.
    Parity is always odd, and locking is sufficient but not necessary. The criterion is the vanishing of six signed sums, an interference
    condition that no purely local mechanism captures.
- **Theorem 4 (substitution).** Let G be exact with factor λ_G and H exact with factor λ_H. Replacing a triangle of G by H gives an exact
  gadget with factor λ_G λ_H.
  - Replacing every triangle gives λ_G λ_H^(n_G).
  - The k-th tower level is exact with factor λ_G^((n^k − 1)/(n − 1)).
  - So the exact gadgets of a law form a family closed under substitution, and each builds an exact tower.
- **Theorem 5 (interference).** Let W be any law with nonnegative values and support not-all-equal, for example plain not-all-equal. Then W
  is exact on no gadget with fewer than 7 triangles. By contrast, signed not-all-equal is exact on the 3-triangle Sierpinski gadget, with
  λ = −1.
- **Theorem 6 (no selected growth exponent).** Let P be a finite set of triangles glued to an inner vertex p of G at that vertex only, every
  other vertex of P lying in two triangles of P (a *tadpole*).
  - Then R_(G+P) = h·R_G, where h, the internal sum of P, does not depend on s_p.
  - Corner chains are unchanged, so the corner growth rate ρ of the tower is unchanged.
  - The Pasch configuration (p,1,2)(p,3,4)(1,3,5)(2,4,5) gives h = (q − 1)(q + 1)(q² + 3), with h(0) = −3.
  - Attaching j such tadpoles to the Sierpinski gadget gives exact linear gadgets with 3 + 4j triangles and ρ = 2. Their growth exponents
    log(3 + 4j)/log 2 are unbounded. The law selects no growth exponent.
- **Proposition 7 (the knot on sectors).** At the knot angle θ = π/3:
  - a vertex of two triangles with odd base count locks their sectors, as at every angle;
  - a vertex of three triangles with odd base count has factor −i√3·σ₁σ₂σ₃·NAE(σ₁, σ₂, σ₃);
  - no factor of even base count vanishes.
  - So in the sector picture a three-fold contact acts on the phases of its triangles as the not-all-equal knot, up to a sign gauge.

## Nearest known result

- **In the repository.** `SIMPLEX-GASKETS-20261029-001A` and `WAVE-UNIQUENESS-20261029-001A` fix the Sierpinski gluing and study the laws.
  This ticket fixes the law and studies the gluings.
- **Outside.**
  - Decimation on finitely ramified (p.c.f., nested) fractals, and the renormalization problem for harmonic structures: which gluings admit
    a nondegenerate fixed point of a Dirichlet form (Lindstrøm 1990, Sabot 1997, Kigami). This is the closest classical analog, for
    positive quadratic forms instead of signed three-bit laws.
  - Sector or Fourier expansions of transfer weights are standard.
  - Property B and m(3) = 7 (the Fano plane) are classical, and so is Seymour 1974.
- **Classification.**
  - Lemma 1 and Theorem 4 are elementary. Theorem 5 is a short consequence of classical facts.
  - Theorems 1–3, 6 and Proposition 7, in this setting: no overlap found (candidate local delta).

## Proof of Lemma 1

- Write w_θ(s) = s_a (ζ^E − ζ^(−E))/(ζ − ζ⁻¹) = (ζ − ζ⁻¹)⁻¹ Σ_σ σ s_a ζ^(σE) and expand the product over the triangles.
- The spin of an inner vertex v then appears as s_v^(m_v) ζ^(s_v S_v), and Σ_(s = ±1) s^(m) ζ^(sS) = ζ^S + (−1)^m ζ^(−S) = f_v(S).
- The corner spins remain:
  - s_A, since A sits in the base slot of T_A;
  - ζ^(σ_TA s_A + σ_TB s_B + σ_TC s_C).
  - When two corners share a triangle, the patterns ε that disagree there have empty sums.
- The cosine wave has s_a cos(θE)/cos θ = (ζ + ζ⁻¹)⁻¹ Σ_σ s_a ζ^(σE), with no σ in front. ∎

## Proof of Theorem 1

- **Base slots.** Each triangle has one base slot. T_A's base slot is the corner A. B and C occupy b- and c-slots. So the other n − 1 base
  slots all lie at inner vertices, and Σ m_v = n − 1.
- **Flipping every sector.** It multiplies Π σ_t by (−1)^n, and f_v(−S) = (−1)^(m_v) f_v(S). So Z(−ε) = (−1)^(n + n − 1) Z(ε) = −Z(ε).
  Equivalently, w_q is invariant under complementing its three bits, hence so is R.
- **The cosine wave** is odd under complementing (c(−s) = −c(s)), so R(−s) = (−1)^n R(s).
  - If n is even, R(−s) = R(s).
  - Then R = λc would give λc(s) = R(s) = R(−s) = −λc(s), so λ = 0. ∎

## Proof of Theorem 2

- **Independence.** The eight functions factor as (s_A ζ^(ε_A s_A)) ⊗ ζ^(ε_B s_B) ⊗ ζ^(ε_C s_C). Each 2×2 factor has determinant
  ±(ζ² − ζ⁻²). The 8×8 determinant is (ζ⁴ − 1)¹²/ζ²⁴, computed in the check.
- **The criterion.** The target is w = (ζ − ζ⁻¹)⁻¹ (g_+++ − g_−−−). By independence, R = λw iff:
  - the six mixed coefficients vanish;
  - Z(−−−) = −Z(+++), which always holds by Theorem 1;
  - Z(+++) ≠ 0.
- **The leading term.**
  - The assignment σ ≡ + has S_v = deg v at every inner vertex, hence the term ζ^(Σ deg v) = ζ^(3n−3) with coefficient 1.
  - Take any other σ with corner sectors +. Some triangle is −. Since the triangles are connected through inner vertices, some inner vertex
    meets both a + and a − triangle and has |S_v| ≤ deg v − 2.
  - So that term has smaller top degree, and the leading term ζ^(3n−3) survives.
- **In q.**
  - R(q) is a polynomial of degree at most n, since each triangle contributes K + qM.
  - Its q^n coefficient is the contraction with M on every triangle. That forces all vertices of the connected gadget equal, giving
    [A = B = C] = M(corners).
  - If R = λ(q)(K + qM) identically, comparing q^n coefficients gives λ_n K + λ_(n−1) M = M, so λ_n = 0 and λ_(n−1) = 1.
  - Otherwise put λ := R(0, 0, 1). The defects R_x − λ·w_q(x) have degree at most n and are not all zero, so at most n values of q are
    exact.
- **The two descriptions agree.**
  - If the mixed sums vanish identically, R = λw for all but finitely many q, hence identically.
  - Conversely, if R = λw identically, the mixed sums vanish at infinitely many ζ, hence identically. ∎

## Proof of Theorem 3

- **(a) Locking.**
  - At every mixed σ some factor f_v(0) = ζ⁰ − ζ⁰ = 0, so every term of the six mixed sums vanishes. Theorem 2 then applies.
  - A frame forces σ_TB = σ_TA = σ_TC: a two-triangle vertex with one base incidence has f(σ + σ′) = 0 exactly when σ ≠ σ′.
  - At ζ = e^(iπ/k), f_v(S) = 0 iff ζ^(2S) = (−1)^(m_v + 1). That is k | S for odd m_v, and 2S ≡ k mod 2k for even m_v.
  - Locking at π/k kills the mixed sums at that ζ, and the gadget is exact there iff λ ≠ 0.
- **(b) Balanced cancellation.**
  - A surviving term is (Π_t σ_t)(Π_(m_v odd) sgn S_v)·Π_v F(m_v mod 2, |S_v|), with F(m, k) = ζ^k + (−1)^m ζ^(−k).
  - If the signed count of each class of equal multisets is zero, each mixed sum is a zero combination of products.
- **(c) The examples.** All are checked exactly:
  - the six mixed sums of each gadget as Laurent polynomials;
  - the class counts;
  - exactness as polynomials in q.
  - For the twin gadget the involution is the flip of its last triangle: it swaps the factors at the two vertices it shares with no base
    slot, and it reverses Π σ.
- **(d)** follows from (a)–(c) and Theorem 1. ∎

## Proof of Theorem 4

- **The relation.** In the corner relation of G∘_t H, sum first over the inner vertices of the copy of H. This replaces the factor W on t by
  R_H = λ_H W. What remains is the corner relation of G, multiplied by λ_H.
- **It is a gadget.**
  - The corners of H have degree one in H, so the vertices of t keep their degrees.
  - Inner vertices of H keep at least two triangles.
  - Connectivity is preserved.
- **Iteration** gives the full substitution and the tower. ∎

## Proof of Theorem 5

- **Positivity.** R(0, 0, 0) is a sum of nonnegative terms. It vanishes iff no assignment with A = B = C = 0 makes every triangle not all
  equal.
  - By complement symmetry the same holds for A = B = C = 1.
  - So R(0, 0, 0) = 0 iff the 3-graph H = G ∪ {ABC} is not 2-colourable, where a colouring is proper when no edge is monochromatic.
- **Exactness** needs R(0, 0, 0) = 0 and R(0, 0, 1) = λW(0, 0, 1) ≠ 0. The latter makes G 2-colourable.
- **A minimal obstruction.** Let H′ ⊆ H be minimal non-2-colourable. It contains ABC, and Seymour gives |V(H′)| ≤ |E(H′)| ≤ n + 1.
- **Small vertex sets.** Exhaustively, every 3-graph on at most 6 vertices with at most 9 edges is 2-colourable. (Five vertices need all 10
  triples; six need one triple of each of the 10 complementary pairs.) So |V(H′)| ≥ 7, hence n ≥ 6.
- **Six triangles.** If n = 6, then H′ = H has 7 edges on 7 vertices.
  - By the exhaustive enumeration, the 7-edge non-2-colourable 3-graphs on 7 vertices are the 30 labelled Fano planes, all 3-regular.
  - But A has degree 2 in H: T_A and ABC.
  - So n ≥ 7.
- **The signed knot.** Its value on the Sierpinski gadget is λ(0) = −1 (Theorem 2, checked). ∎

## Proof of Theorem 6

- **h is constant.** w_q is invariant under complementing its three bits. Complementing all spins of P together with s_p leaves every factor
  unchanged, so h(s_p) = h(−s_p). Summing over P first gives R_(G+P) = h·R_G.
- **Corner chains.**
  - Corner chains of the tower obey d_(k+1)(XY) = min over corner paths in the gadget of the sum of d_k over the triangles traversed.
  - A path that enters P must leave through p again, so it is not simple.
  - Hence the minimum, and with it every d_k and ρ, is that of G.
- **Linearity.** The Pasch configuration is linear, and it shares only p with G.
- **The Pasch factor** h and the attachments with j = 1, 2 (7 and 11 triangles) are computed exactly in the check. ∎

## Proof of Proposition 7

- ζ = e^(iπ/3), so ζ³ = −1.
- **Odd base count** gives f(S) = ζ^S − ζ^(−S) = 2i sin(πS/3).
  - Three incidences: S ∈ {±1, ±3}. The value is ±i√3 at |S| = 1 and 0 at |S| = 3, and sgn S = −σ₁σ₂σ₃ on not-all-equal triples.
  - Two incidences: f = 0 iff S = 0.
- **Even base count** gives 2cos(πS/3) ∈ {±1, ±2}, never zero. ∎

## What the computation checks

`check.py` (about 20 seconds):
- **The pencils.** The pencil, sector and cosine identities, and the gauge relations, symbolically.
- **Theorem 1.** Flip parity on every gadget with up to five triangles (73,326 at n = 5). Complement invariance and the cosine parity at
  n = 3, 4.
- **Theorem 2.** The determinant of the eight sector functions. On every gadget with up to four triangles:
  - generic exactness ⟺ vanishing mixed sector sums;
  - the leading term of Z(+++);
  - λ monic of degree n − 1.
- **Theorem 3.**
  - On every gadget with up to four triangles: locking and balance imply exactness, and angle locking implies exactness at q = 0, 1, 2.
  - The Sierpinski and twin gadgets.
  - Two algebraic examples (6 and 7 triangles), exactly.
- **Theorem 4.** Four substitutions and the level-2 gasket, λ = (q² − 1)⁴.
- **Theorem 5.** The small-vertex lemma and the Fano enumeration, both exhaustive. Plain not-all-equal is exact on no gadget with
  n ≤ 4.
- **Theorem 6.** h for the Pasch tadpole. One and two tadpoles on the Sierpinski gadget: exact, linear, ρ = 2.
- **Proposition 7**, and controls:
  - a non-exact gadget has a nonzero mixed sum;
  - the sector functions are dependent at ζ = i;
  - a perturbed law fails;
  - the two summation routines agree.

## Reading

- **The law selects gluings by interference, not by a local rule.**
  - A gluing reproduces the harmony exactly when six signed sums over phase assignments cancel.
  - Phase locking at single contacts is one way. Mirror pairs of assignments are another. Beyond six triangles, cancellations between
    different products appear.
  - The criterion is global in the gluing but finite and exact.
- **Interference is what lets the knot build small spaces.**
  - Without signs, the not-all-equal knot needs at least seven triangles before it can reproduce itself. Excluding the all-equal corners
    then needs a non-2-colourable configuration, and the smallest is the Fano plane.
  - With signs, three triangles suffice. The all-equal corners are excluded by cancellation instead of by impossibility.
- **The knot reappears on phases.** At the knot angle a three-fold contact constrains the phases of its three triangles by the same
  not-all-equal relation (Proposition 7).
- **What is not selected.** Exact gluings are closed under substitution and under tadpoles. So the law fixes neither a single space nor a
  growth exponent. Which gluings occur, and how many, is the census of ticket B.

## Nonclaims

- **Growth.** Corner chains count triangles in the substitution tower. The growth rate ρ and the exponent log n / log ρ are combinatorial
  quantities of the gluing, not a metric or a dimension of a native space.
- **The gluing is still drawn.** Gadgets are chosen as finite gluings of triangles. The law decides only which of them it reproduces on.
- **Outside the stated proofs.** No classification for n ≥ 6 is claimed. The algebraic examples show only that the mechanisms of (a) and (b)
  are not exhaustive.
- **External inputs.** Theorem 5 uses Seymour's theorem as an external classical result. It is not replayed here.
