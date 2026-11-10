# The Kloosterman lower bounds

Epic `KLOOSTERMAN-BOUNDS-20261110-001` (program foundations, group `collapse`, sub-goal B58), 2026-11-10. Pre-registered in commit
78a919ba5.

## The question

- **Where it comes from.** `LINEAR-ROOTS-20261109-001` found by exact computation that at sides n = 2^m the cut-open torus's eigenvalue
  1/a occurs K(a)(K(a) − 2)/8 times, with |K(a)|/4 eigenvectors, K the Kloosterman sum of GF(2n), and proved that these multiplicities add
  up to the cone's whole degree. Lower bounds at every a would therefore prove the collapse. Its direction 1 had the coordinator's
  go-ahead on 2026-11-10, with the instruction to report the kernel count precisely, and where the argument stops, if the bounds stalled.
- **The question.** Prove the lower bounds: first that the kernel at each eigenvalue has dimension at least |K(a)|/4, then the Jordan
  chains.

## The question in standard terms

For b ∈ GF(2n)*, the kernel of F ↦ (k + 1)F(k + 1) + Ω_b(k)F(k) mod k^(n/2) on polynomials of degree below n/2: is its dimension
|K(b)|/4, and why?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Self-adjoint.** The operator whose kernel holds the eigenvectors is self-adjoint for the pairing ⟨F, G⟩ = the sum of the coefficients of FG below degree n/2, so the eigenvectors are the radical of one symmetric form. | proved | A |
| 2 | **One shift multiplier.** Any two eigenvectors F_1, F_2 at the same eigenvalue satisfy F_1(k)F_2(k + 1) = F_1(k + 1)F_2(k): their ratio is unchanged by the cut line's shift. | proved | A |
| 3 | **One polynomial per eigenvalue.** The eigenvectors are G·r(Y), Y = k² + k, for one polynomial G of least degree, so their number is ⌈(n/2 − deg G)/2⌉. | proved | A |
| 4 | **The Padé form.** The same count is n/4 minus the rank of one explicit (n/4) × (n/4) Toeplitz matrix, built from a power series ψ in Y. | proved | A |
| 5 | **The degree law.** deg G = n/2 − k, where k(k + 1)/2 is the eigenvalue's multiplicity (2k + 1 = \|K − 1\|), at every eigenvalue for sides 8 to 512. With conclusion 3 this is the eigenvector count \|K\|/4. | computed, exact | A, stress test |
| 6 | **The Padé rank.** The Toeplitz rank equals the linear complexity of ψ's coefficients, n/4 − \|K\|/4, at every eigenvalue for sides 8 to 64. | computed, exact | A |
| 7 | **Where it stops.** The eigenvector lower bound is now exactly deg G ≤ n/2 − k, one degree per eigenvalue; nothing found ties that degree to the Kloosterman sum, and the Jordan chains were not reached. | the gap | A |

## Answer

The lower bounds are not proved, but the eigenvector half is now one degree per eigenvalue. Every eigenvector at an eigenvalue is a
single polynomial G times a polynomial in Y = k² + k. That follows from two short proofs: the operator is self-adjoint, and any two
eigenvectors have the same ratio under the cut line's shift. So the number of eigenvectors is ⌈(n/2 − deg G)/2⌉, and the Kloosterman
count |K|/4 is exactly the statement deg G = n/2 − k, where k(k + 1)/2 is the multiplicity. That degree law holds at every eigenvalue
for sides 8 to 512, with 256 and 512 checked after registration. An equivalent form is the rank of one explicit Toeplitz matrix per
eigenvalue. Where it stops: no argument found ties deg G to the Kloosterman sum, and the Jordan chains, which the collapse needs, were
not reached.

## Reading

**Interpretation, not a theorem.**
- **Why one polynomial.** The cut line's shift k ↦ k + 1 is an involution, and an eigenvector is an approximate eigenfunction of it.
  Two approximate eigenfunctions with the same multiplier differ by a shift-invariant factor, a function of Y; the multiplier is a
  norm-one function, Hilbert's Theorem 90 in a quadratic extension.
- **The Kloosterman count as a degree.** The count |K|/4 becomes a statement about how far below n/2 the least solution's degree can
  drop. In Padé terms it is the defect of an explicit power series: its coefficients satisfy a recurrence |K|/4 shorter than a generic
  sequence's.
- **The chains.** The Jordan blocks of the law decrease by 4, the same pattern as multiplying by Y in the cyclic basis G·Y^j. That
  suggests G·Y^j heads a chain of length 2k − 1 − 4j. This was not tested.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every check is exact over GF(2n).
- **Census-only.** Conclusions 5 and 6.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusions 3 and 5 (ticket A: sides 8 to 128) | sides 256 and 512, every b ∈ GF(512)* and GF(1024)* | pass |
| Conclusions 1, 2, 4 (proved) | — | proofs by hand; checks at sides 4 to 64 |

The script is `stress_test.py` beside this note, with `stress_test.json` and `stress_test_log.txt`; it ran in a few minutes, under the
ten-minute threshold of `docs/LONG_RUNNING.md`.

## Literature and provenance

- **Sources.** Hilbert's Theorem 90; Padé approximation and the ranks of Toeplitz and Hankel matrices (Kronecker, Iohvidov); Kloosterman
  sums over GF(2^r) and the curves y² + xy = x³ + a (Lachaud and Wolfmann).
- **Related records here.** `LINEAR-ROOTS-20261109-001` (the law), `RETURN-DIGITS-20261109-001`, `CONE-COLLAPSE-20261109-001`.
- **Classification.** New as far as found. The search was bounded, the one of 2026-11-09, and found no link between Kloosterman sums and
  the spectrum of a walk or matrix over GF(2). That is not a claim of priority.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`. The spectrum is a contact-level reading (A45 does not bear on it).
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways, at sides 2^m.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (four theorems, six checks) and the stress run.
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the Kloosterman lower bounds | **Status:** Partially successful | The eigenvector count is reduced, with proofs, to one degree per eigenvalue; that degree and the Jordan chains are not proved |
| Local direction — the collapse at powers of two | Continue | Two explicit statements remain, the degree of one polynomial and the chains it heads |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B74 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Each eigenvalue's eigenvectors are one polynomial, so the Kloosterman count is one degree |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained); sub-goals B73 and B74 added for directions 1 and 2 (both 3/3,
not taken by this epic), B58 advanced, B59 unchanged. **Assumptions:** none added.

- **What the attempt leaves open.** The degree law deg G = n/2 − k, the Jordan chains, and with them the collapse.

**Next step:** Continue — selected: #1, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The Jordan chains from one polynomial (B73) | 3/3 — Breakthrough | 2/3 — Testable | Compute the chain each G·Y^j heads at sides 4 to 64 and test the length 2k − 1 − 4j, which would make the multiplicity a function of deg G alone → a chain lemma, or the first j where a chain is shorter | Selected · not started |
| 2 | The degree of the least solution (B74) | 3/3 — Breakthrough | 1/3 — Stated | Bound deg G from the identity G·Δ = k^h Ω(k + 1)R + (k + 1)^(h+1) R(k + 1), Δ = Ω(k)Ω(k + 1) + Y, which ties G to its overflow R at the roots of Δ → deg G ≤ n/2 − k, or a reason this identity cannot see K | Alternative · not started |
| 3 | The curve behind each eigenvalue (B59) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B59 → the mechanism, or a reason none exists | Alternative · not started |

1. **The chains.** Payoff 3: with #2 they prove the collapse, and alone they reduce it to one degree per eigenvalue. Concreteness 2: the
   cyclic basis is explicit and the chains are a finite computation.
2. **The degree.** Payoff 3: it proves the Kloosterman eigenvector count, and with #1 the collapse. Concreteness 1: no route yet.
3. **The curve.** Payoff 3: as in B59. Concreteness 1.

**Recommendation.** Continue with #1.

## Final report as sent

Sent to the owner on 2026-11-10 at 01:15 UTC and copied here verbatim.

The lower-bounds epic is closed and published. The bounds aren't proved, but the eigenvector half now comes down to one degree per eigenvalue.

I proved that at each eigenvalue, every eigenvector is a single polynomial G times a polynomial in Y = k² + k. Two short facts give this: the operator is self-adjoint, and any two eigenvectors change by the same factor under the cut line's shift. So the exact count is ⌈(n/2 − deg G)/2⌉, or equivalently n/4 minus the rank of one explicit Toeplitz matrix. The Kloosterman count |K|/4 is then the single statement deg G = n/2 − k, where k(k+1)/2 is the multiplicity. That holds at every eigenvalue for sides 8 to 512, with 256 and 512 checked after registering.

Where it stops: evaluating on GF(2n) gives the shared shift factor but not the count. G has no zeros or factors that follow the Kloosterman trace classes, so nothing yet ties deg G to K. I didn't reach the Jordan chains, which the collapse needs.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the Kloosterman lower bounds | **Status:** Partially successful | Eigenvector count reduced, with proofs, to one degree per eigenvalue; that degree and the chains aren't proved |
| Local direction: the collapse at powers of two | Continue | Two explicit statements remain |
| Broader exploration: G5 with G1 | Known alternatives | Backlog B22–B74 |
| Long-term goal: G5 Dynamics | Capability gained | Each eigenvalue's eigenvectors are one polynomial |

**Next step:** Continue with #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | The Jordan chains from one polynomial (B73) | 3/3 | 2/3 | Test whether G·Y^j heads a chain of length 2k − 1 − 4j at sides 4 to 64, which would make the multiplicity depend on deg G alone → a chain lemma, or the first shorter chain | Selected |
| 2 | The degree of the least solution (B74) | 3/3 | 1/3 | Bound deg G through the identity tying G to its overflow at the roots of Δ = Ω(k)Ω(k+1) + Y → the bound, or why it can't see K | Alternative |
| 3 | The curve behind each eigenvalue (B59) | 3/3 | 1/3 | As recorded in B59 | Alternative |

**Corrections:** none. **Goals:** G5 checkpoint (capability gained); sub-goals B73 and B74 recorded, B58 advanced, B59 re-rated with this report. **Assumptions:** none added. The stress runs at sides 256 and 512 passed in under four minutes. Commits: 78a919ba5 (pre-registration), 14e1c98a1 (epic), 5efec71b6 (tracking), 6703cb974 (shared docs). The novelty claim still rests on the bounded search from yesterday, not a priority search.
