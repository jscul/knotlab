# The return map digit by digit

Epic `RETURN-DIGITS-20261109-001` (program foundations), 2026-11-09. Pre-registered in commit aaa3e7be3.

## The question

- **Where it comes from.** `CONE-COLLAPSE-20261109-001` proved that the cut-open torus's spectrum is four copies of a cone's and that
  at n = 2^m the cone's spectrum is det(I + C_s(w)), C_s an (n/2) × (n/2) return map of the cut line; every eigenvalue is a
  (2n − 1)-th root of unity at sides 4 to 128 (computed). Its direction 2, the return map digit by digit, had the coordinator's
  go-ahead on 2026-11-09, with leave to follow it into direction 1 (the single particle behind the symmetric square).
- **The question.** Write C_s through the dyadic product of the uncut walk's resolvent, find a recursion in m, and use it to prove
  the collapse at every power of two, or find where the recursion fails.

## The question in standard terms

Over GF(2), is every root of det(I − μ A_cone) in GF(2n) when n = 2^m (A_cone the quarter-turn quotient of the alternating medial
digraph of the n × n grid, outer face removed)?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The return map is one-dimensional.** C_s(w) = w^(n+1) T_h(w⁻²), h = n/2, where T_h(c) is the map f ↦ (K + c)(ιf)(K + c) mod K^h on F[K]/(K^h) in the ball basis W_k(t + 1/t) = Σ_{\|j\|≤k} t^j, ι(W_k) = W_(h−1−k). | proved | A |
| 2 | **The reversal is a multiplication.** ι is multiplication by ε = W_(h−1) = 1 + Σ_j K^(h−h/2^j), an involution. | proved | A |
| 3 | **Without the reversal, a trace.** S_h(c) = T_h(c)R has eigenvalues c/(ζ + ζ⁻¹), ζ an (n + 1)-th root of unity, that is c times the h elements of GF(n) of trace 1: det(zI + S_h) = c^h(1 + L_m(z/c)). | proved | A |
| 4 | **The digit recursion.** In the basis W_i, K^h W_i of F[K]/(K^2h), S_2h = [[S_h, c^h S_h], [E, S_h + c^h E]] and ε_2h = [[I, 0], [ε_h, I]], from T_1 = [c]; and det(zI + T_2h) = det(z² + S_h² + c^h z(ε_h S_h + E)). | proved | A |
| 5 | **The cone polynomial is a linearized determinant.** det(I − μA_cone) = μ^(−h) det(Σ_{i=0}^{m} μ^(2^i) C_i), C_0 = S⁻¹, C_i = N^(h − 2^(i−1)), C_m = I, over GF(2) on F[k]/(k^h) (N = multiplication by k, S g = (k + 1)g(k + 1)): the shape of the trace of GF(2n). | proved | A |
| 6 | **The collapse, restated.** Every eigenvalue is a (2n − 1)-th root of unity exactly when every nonzero root of that determinant lies in GF(2n); equivalently, when the spectral curve det(zI + T_h(c)) = 0 meets z² = c^(n+1) only where z⁴ = c³. | proved (the equivalences); the statement open | A |
| 7 | **The trace factor.** 1 + Tr_(GF(2n))(μ) divides det(I − μA_cone) exactly once and leaves a square, at sides 4 to 128: the parity law of `CONE-COLLAPSE-20261109-001`. | computed, exact | A, stress test |

## Answer

The recursion in m exists and is proved: the return map at side 2^(m+1) is built from the one at 2^m by a two-by-two block rule,
starting from the one-by-one matrix [c]. It says what is special about powers of two. Take away one reversal and the return map's
eigenvalues are exactly c times the elements of GF(n) of trace 1. Put the reversal back (it is multiplication by an involution) and
the cone polynomial becomes the determinant of a linearized polynomial Σ_{i=0}^{m} μ^(2^i) C_i with coefficients over GF(2) and
top coefficient the identity, which is the shape of the trace polynomial of GF(2n). For the trace itself, Tr(μ)² + Tr(μ) = μ^(2n) + μ
puts every root in GF(2n) in one line; for the matrix version that last step is the gap. The trace factor shows up exactly once in
the cone polynomial, with a square left over, at every side read.

## Reading

**Interpretation, not a theorem.**
- **Why GF(2n).** The walk's spectrum sits where the trace of GF(2n) would put it: the matrix coefficients interpolate between the
  scalar trace (all C_i = 1) and the cut-open torus. The un-reversed map lives on GF(n) (trace 1), the reversal ε is the half-turn
  t^h of the cut line, and together they climb one field, from GF(n) to GF(2n).
- **The single particle.** The eigenvalues of S_h, c times the trace-1 elements of GF(n), are the natural single-particle levels; the
  cone's symmetric-square multiplicities would then come from how ε pairs them. Not shown.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every check is exact over GF(2) or GF(2)[c] except the stress test's determinant identity at h = 8 and 16, which
  is checked at 24 random points of GF(2^16) each (a nonzero polynomial of degree below 2^9 vanishes at a random point with
  probability below 2^(−7)).
- **Census-only.** Conclusion 7.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Theorem 1 (sides 4 to 32) | side 64 | pass |
| Theorem 2 (h to 64) | h = 128 | pass |
| Theorem 3 (h to 32) | h = 64 | pass |
| Theorem 4 (recursion to 32, identity exact to h = 4) | 32 → 64; the identity at h = 8, 16 | pass (no mismatch at 24 random points each) |
| Theorem 5 and the trace factor (sides 4 to 32) | 64 (exact), 128 (against CONE-COLLAPSE-S1 below degree 129) | pass: at 64 the determinant is μ^32 times the cone polynomial; at 128 it has degree 8128 past μ^64 and agrees below degree 129; at both the trace factor divides exactly once and leaves a square |

The script is `stress_test.py` beside this note, with `stress_test.json` and `stress_test_log.txt`; it ran in 109 seconds, under the ten-minute threshold of `docs/LONG_RUNNING.md`.

## Literature and provenance

- **Sources.** Dickson and Chebyshev polynomials over GF(2); linearized polynomials and the trace of a finite field (Lidl and
  Niederreiter, Finite Fields, chapter 3); Lucas' theorem; the Schur complements of `FULL-REACH-PROOF-20261108-001A`.
- **Related records here.** `CONE-COLLAPSE-20261109-001` (the cone and the return map, the parity law), `FULL-REACH-PROOF-20261108-001`.
- **Classification.** New as far as found; no search beyond these sources was made.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`. The spectrum is a contact-level reading, so it does not depend on
  how rings are declared (A45).
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways, at sides 2^m.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (five theorems, seven checks) and the stress run.
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the return map digit by digit | **Status:** Partially successful | The recursion is found and proved, and turns the cone polynomial into a linearized determinant; the collapse is not proved |
| Local direction — the collapse at powers of two | Continue | One explicit statement is left: the roots of Σ μ^(2^i) C_i lie in GF(2n) |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B48 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Why powers of two are special now has an algebraic form: a trace polynomial of GF(2n) with matrix coefficients |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.** That every root of the linearized determinant lies in GF(2n), and with it the collapse; why the
  multiplicities are k(k + 1)/2.

**Next step:** Continue — selected: #1, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The roots of the linearized determinant | 3/3 — Breakthrough | 2/3 — Testable | Find polynomial matrices M(μ) with (Σ μ^(2^i) C_i) M(μ) = μ^a (μ^(2n) + μ)^b I at n = 4, 8, 16 and read their shape, as Tr² + Tr = μ^(2n) + μ does for the scalar trace → a proof of the collapse, or a side where no such shape exists | Selected · not started |
| 2 | The single particle | 2/3 — Substantial | 1/3 — Stated | Read the cone's k(k + 1)/2 multiplicities off the trace-1 eigenvalues of S_h and how ε pairs them, at 4, 8, 16 → the multiplicity law, or none | Alternative · not started |
| 3 | The multiplicities from the linearized form | 1/3 — Incremental | 2/3 — Testable | Peel the trace factor repeatedly (1 + Tr, then the square root of the rest) at 4 to 128 and look for a rule for each layer → a description of k, or no rule | Alternative · not started |

1. **The roots.** Payoff 3: it would prove the collapse at every power of two; Concreteness 2: the operators are explicit and small,
   and the scalar case is one line.
2. **The single particle.** Payoff 2: it would explain the multiplicities and the Jordan blocks; Concreteness 1: no mechanism yet.
3. **The layers.** Payoff 1: a description, not a proof; Concreteness 2: the computation is direct.

**Recommendation.** Continue with #1.

## Final report as sent

Sent to the owner on 2026-11-09 at 23:32 UTC and copied here verbatim.

The return-map epic is closed and published. The collapse at every power of two still isn't proved, but it now comes down to one explicit statement. The cut line's return map turns out to be a one-dimensional operator, and a two-by-two block rule builds it digit by digit from the one-by-one matrix [c]. Take away one reversal and its eigenvalues are exactly c times the trace-1 elements of GF(n). The reversal itself is multiplication by an involution. Put back together, the cone polynomial is the determinant of the trace polynomial of GF(2n), μ + μ² + μ⁴ + … + μⁿ, with GF(2) matrices for coefficients. For the scalar trace, one line puts every root in GF(2n). The matrix version is the gap. All five theorems passed one size past what was checked (up to side 128), in 109 seconds.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the return map digit by digit | **Status:** Partially successful | The recursion is found and proved and turns the cone polynomial into a linearized determinant; the collapse isn't proved |
| Local direction: the collapse at powers of two | Continue | One statement is left: the roots of Σ μ^(2^i) C_i lie in GF(2n) |
| Broader exploration: G5 with G1 | Known alternatives | Backlog B22–B50 |
| Long-term goal: G5 Dynamics | Capability gained | Why powers of two are special now has an algebraic form |

**Next step:** Continue with #1. I'm opening it as a new epic now and will pre-register it before the proof attempt.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | The roots of the linearized determinant | 3/3 | 2/3 | Find matrices M(μ) with L(μ)M(μ) = μ^a(μ^(2n) + μ)^b I at 4, 8, 16 and read their shape → a proof of the collapse, or a side where no such shape exists | Selected |
| 2 | The single particle | 2/3 | 1/3 | Read the k(k+1)/2 multiplicities off the trace-1 eigenvalues and how the involution pairs them → the multiplicity law, or none | Alternative |
| 3 | The multiplicities from the linearized form | 1/3 | 2/3 | Peel the trace factor layer by layer at 4 to 128 → a rule for k, or none | Alternative |

**Corrections:** none. **Goals:** G5 checkpoint (capability gained). **Assumptions:** none added. The epic is commit c4c8fb8bd. Its goals-doc and intuition-doc entries went in with the growth thread's commit 53d46a27a, since both threads were writing the shared docs at the same moment.
