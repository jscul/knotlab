# The roots of the linearized determinant

Epic `LINEAR-ROOTS-20261109-001` (program foundations, sub-goal B58), 2026-11-09. Pre-registered in commit 76cc32e30.

## The question

- **Where it comes from.** `RETURN-DIGITS-20261109-001` proved that at sides n = 2^m the cut-open torus's cone polynomial is
  det(Σ_{i=0}^{m} μ^(2^i) C_i), the trace polynomial of GF(2n) with GF(2) matrices for coefficients, so that the collapse (every
  eigenvalue a (2n − 1)-th root of unity) holds exactly when that determinant's roots lie in GF(2n). Its direction 1, selected, became
  sub-goal B58; this epic takes it up under the owner's autonomy rule.
- **The question.** Prove that every root of the linearized determinant lies in GF(2n), or say exactly what is left.

## The question in standard terms

Over GF(2), with A_cone the quarter-turn quotient of the alternating medial digraph of the n × n grid (outer face removed), n = 2^m:
is every root of det(I − μA_cone) in GF(2n), and with what multiplicity?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The Kloosterman law.** With K(a) = Σ_{x ∈ GF(2n)} (−1)^(Tr(x + a/x)), the eigenvalue 1/a has K(a)(K(a) − 2)/8 copies, \|K(a)\|/4 eigenvectors and Jordan blocks 1, 5, 9, ... (K(a) > 0) or 3, 7, 11, ... (K(a) < 0). In elliptic-curve terms the multiplicity is (t² − 1)/8, t the trace of Frobenius of y² + xy = x³ + a, whose j-invariant is the eigenvalue. | computed, exact: multiplicities and blocks at sides 4 to 128, eigenvector counts at 4 to 512 | A, stress test |
| 2 | **The count.** K(a) ≡ 0 mod 4 and Σ_a K(a)(K(a) − 2)/8 = n(n − 1)/2, the whole degree; so lower bounds on the multiplicities at every a would prove the collapse and the law together. | proved | A |
| 3 | **One kernel per eigenvalue.** The eigenvectors at 1/a are the polynomials F of degree below n/2 with (k + 1)F(k + 1) ≡ Ω_b(k)F(k) mod k^(n/2), b = √a, Ω_b(k) = b + Σ_{i=2}^{m} b^(2^i) k^(h − 2^(i−2)). | proved | A |
| 4 | **The trace in the multiplier.** On GF(2n)*, Ω_b(y) = y^h Tr(b⁴/y) + b²/y^h: the trace of GF(2n) appears beside the shift y ↦ y + 1, the two ingredients of a Kloosterman sum. | proved | A |
| 5 | **The shift is the Kloosterman curve.** The curve on which the return map's shift K ↦ K + c lifts to the cut line's coordinate is birational to Y² + Y = x + c^(−4)/x, whose point count over GF(2n) is governed by K(a) at the eigenvalue 1/a. | proved | A |
| 6 | **The period.** The law predicts A_cone^(e(2n − 1)) = I for the least power of two e at least its largest block: 4, 8, 16, 16, 32, 32 at sides 4 to 128, the computed periods. | computed | A |
| 7 | **The eigenvalue 1.** Its multiplicity is (t² − 1)/8 for the curve y² + xy = x³ + 1 over GF(2n), whose traces are −1, −3, 5, 1, −11, 9, 13, −31, ... (t_(r+1) = −t_r − 2t_(r−1)): 3, 0, 15, 10, 21, 120 at sides 4 to 128. | computed | A |
| 8 | **Other sides.** At the sides 3 to 20 that are not powers of two the eigenvalues are not even in the field of (2n − 1)-th roots of unity. | computed | A |

## Answer

The roots were not proved to lie in GF(2n), but the question now has an exact answer waiting for its proof. Every eigenvalue of the
cut-open torus at side 2^m comes with a multiplicity given by a Kloosterman sum over GF(2n): the eigenvalue λ appears
K(1/λ)(K(1/λ) − 2)/8 times, with |K(1/λ)|/4 eigenvectors, and not at all when K(1/λ) = 0. Equivalently, λ is the j-invariant of an
elliptic curve over GF(2n), and its multiplicity is (t² − 1)/8 for that curve's trace of Frobenius t. This matches every eigenvalue at
sides 4 to 128 and every eigenvector count to side 512. A classical identity, the second moment of Kloosterman sums, makes these
multiplicities add up to exactly the cone's degree n(n − 1)/2. So the collapse would follow from lower bounds alone: if every
λ ∈ GF(2n)* appears at least K(1/λ)(K(1/λ) − 2)/8 times, nothing is left over for eigenvalues outside GF(2n). The bounds are the gap.
On the way, the eigenvectors at each λ were reduced to one kernel, and the trace of GF(2n) and the Kloosterman curve were found
inside the return map, which is where a proof would start.

## Reading

**Interpretation, not a theorem.**
- **Why powers of two.** At other sides the spectrum is not even in the field of (2n − 1)-th roots of unity, so the collapse is not
  the shadow of a symmetry group of odd order; at powers of two the eigenvalues are j-invariants and the multiplicities are traces of
  Frobenius. The arithmetic of elliptic curves over GF(2n) is doing the work.
- **The symmetric square.** The Jordan blocks of the law are those of the symmetric square of one block of size k = (|t| − 1)/2. The
  "single particle" of B59 would then be a k-dimensional object attached to the curve with j-invariant λ.
- **Kloosterman zeros are missing eigenvalues.** The a with K(a) = 0 (the ones Dillon's bent functions use) are exactly the
  λ = 1/a that do not occur.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every check is exact over GF(2) or GF(2n).
- **Census-only.** Conclusions 1, 6, 7 and 8.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 1, eigenvector counts (ticket A: sides 4 to 128) | sides 256 and 512, every a ∈ GF(512)* and GF(1024)* | pass: 511 of 511 and 1,023 of 1,023 |
| Conclusion 1, multiplicities and blocks (sides 4 to 128) | side 256 | not run: the cone has dimension 32,640 there, beyond this workspace's exact routines |
| Conclusions 2 to 5 (proved) | — | proofs by hand; checks at q = 4 to 512 (2), sides 4 to 32 (3), 4 to 256 (4) |

The script is `stress_test.py` beside this note, with `stress_test.json` and `stress_test_log.txt`; it ran in under four minutes, under
the ten-minute threshold of `docs/LONG_RUNNING.md`.

## Literature and provenance

- **Sources.** Kloosterman sums over GF(2^r), K ≡ 0 mod 4 and the curves y² + xy = x³ + a (Lachaud and Wolfmann, 1990); the moments
  of Kloosterman sums (classical); Kloosterman zeros and bent functions (Dillon).
- **Search.** A bounded web search on 2026-11-09 found no link between Kloosterman sums and the eigenvalue multiplicities of a walk,
  a cellular automaton or a matrix over GF(2); Kloosterman sums appear as eigenvalues of Cayley graphs, the opposite roles.
- **Related records here.** `RETURN-DIGITS-20261109-001`, `CONE-COLLAPSE-20261109-001`, `FULL-REACH-PROOF-20261108-001`.
- **Classification.** New as far as found.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`. The spectrum is a contact-level reading, so it does not depend on
  how rings are declared (A45).
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways, at sides 2^m.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (three theorems, a proposition, eight checks) and the stress run.
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the roots of the linearized determinant | **Status:** Partially successful | The multiplicities are found and add up to the whole degree, so lower bounds would prove the collapse; the bounds are not proved |
| Local direction — the collapse at powers of two | Continue | The target is now a lower bound at each eigenvalue, with an explicit kernel and the Kloosterman curve in hand |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B60 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | The walk's spectrum at powers of two has a closed form in classical arithmetic |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained); sub-goal B58 continues with a new first step, sub-goal B59
re-rated 3/3, backlog B60 added. **Assumptions:** none added.

- **What the attempt leaves open.** The lower bounds, and with them the collapse and the law; why the Jordan blocks are those of a
  symmetric square.

**Next step:** Continue — selected: #1, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the Kloosterman lower bounds (B58) | 3/3 — Breakthrough | 2/3 — Testable | Prove that the kernel of conclusion 3 has dimension \|K(a)\|/4, by evaluating the equation on GF(2n), where the multiplier carries the phase Tr(b⁴/y) beside the shift → that count proved, or the reason evaluation cannot see it | Selected · not started |
| 2 | The curve behind each eigenvalue (B59) | 3/3 — Breakthrough | 1/3 — Stated | Look for a k-dimensional space attached to y² + xy = x³ + 1/λ (or to the Kloosterman curve of conclusion 5) whose symmetric square has the cone's λ-part, at sides 4, 8, 16 → the mechanism, or a reason no such space exists | Alternative · not started |
| 3 | Other tori (B60) | 2/3 — Substantial | 3/3 — Ready | Compute the spectrum of the cut-open 2^m × 2^(m′) torus (m ≠ m′) and look for a two-parameter Kloosterman law → a law, or where it breaks | Alternative · not started |

1. **The lower bounds.** Payoff 3: they prove the collapse and the multiplicity law at once, by conclusion 2. Concreteness 2: the
   geometric half is one explicit h × h kernel per eigenvalue, and the trace and the curve are already inside it.
2. **The curve.** Payoff 3: it would explain the multiplicities, the Jordan blocks and the field at once. Concreteness 1: no candidate
   space is in hand.
3. **Other tori.** Payoff 2: a wider law, or a sharper sense of what is special about the square torus. Concreteness 3: the computation
   is direct with this epic's code.

**Recommendation.** Continue with #1.

## Final report as sent

Sent to the owner on 2026-11-10 at 00:38 UTC and copied here verbatim.

The roots epic is closed and published. The collapse still isn't proved, but every eigenvalue's multiplicity is now known exactly, and it's a Kloosterman sum over GF(2n). The eigenvalue 1/a occurs K(a)(K(a) − 2)/8 times, with |K(a)|/4 eigenvectors. In elliptic-curve terms it's (t² − 1)/8 for the curve y² + xy = x³ + a, whose j-invariant is that eigenvalue. Every eigenvalue matches at sides 4 to 128, and every eigenvector count matches up to side 512.

I proved these multiplicities add up to the cone's full size. So showing that each one is at least that large would prove the collapse, and that lower bound is the gap. The law also predicts the walk's period exactly at every side computed. At sides that aren't powers of two, the eigenvalues aren't even in the field of (2n − 1)-th roots of unity.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the roots of the linearized determinant | **Status:** Partially successful | Multiplicities found and shown to fill the spectrum; the lower bounds aren't proved |
| Local direction: the collapse at powers of two | Continue | One lower bound per eigenvalue, with an explicit kernel and the Kloosterman curve in hand |
| Broader exploration: G5 with G1 | Known alternatives | Backlog B22–B66 |
| Long-term goal: G5 Dynamics | Capability gained | The spectrum has a closed form in classical arithmetic |

**Next step:** Continue with #1. Unless you or the coordinator redirect, I'll start it next.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | Prove the Kloosterman lower bounds (B58) | 3/3 | 2/3 | Prove each eigenvalue's kernel has dimension \|K(a)\|/4 by evaluating it on GF(2n), where the trace of GF(2n) appears → that count proved, or why evaluation can't see it | Selected |
| 2 | The curve behind each eigenvalue (B59) | 3/3 | 1/3 | Find a k-dimensional space attached to the curve with j-invariant λ whose symmetric square is the cone's λ-part, at 4, 8, 16 → the mechanism, or why none exists | Alternative |
| 3 | Other tori (B66) | 2/3 | 3/3 | The cut-open 2^m × 2^m′ torus against Kloosterman-type sums → a wider law, or where it breaks | Alternative |

**Corrections:** none. **Goals:** G5 checkpoint (capability gained); B58 advanced with a new first step, B59 re-rated 3/3, B66 added. **Assumptions:** none added. The stress run at sides 256 and 512 passed in under four minutes. Commits: 76cc32e30 (pre-registration), e528d999e (epic), 4e5ab67e9 (shared docs). A bounded literature search found no earlier link between Kloosterman sums and the spectrum of a walk or matrix over GF(2). The nearest sources are on Kloosterman sums and elliptic curves in characteristic 2 ([arXiv 1104.3882](https://ar5iv.labs.arxiv.org/html/1104.3882), [arXiv 0801.2988](https://arxiv.org/pdf/0801.2988)) and on matrix Kloosterman sums ([arXiv 2210.07133](https://arxiv.org/pdf/2210.07133.pdf)).
