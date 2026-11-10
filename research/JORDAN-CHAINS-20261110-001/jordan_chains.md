# The Jordan chains from one polynomial

Epic `JORDAN-CHAINS-20261110-001` (program foundations, group `collapse`, sub-goal B73), 2026-11-10. Pre-registered in commit 25ab6ffa4.

## The question

- **Where it comes from.** `KLOOSTERMAN-BOUNDS-20261110-001` proved that at sides n = 2^m the eigenvectors of the cut-open torus at each
  eigenvalue are G·Y^j (Y = k² + k, j < ⌈k/2⌉) for one least polynomial G, k = n/2 − deg G, and computed that k is the Kloosterman index
  of the eigenvalue. The Jordan blocks of the Kloosterman law, 2k − 1, 2k − 5, ..., fall by 4 as Y^j gains a power. Its direction 1 had
  the coordinator's go-ahead on 2026-11-10.
- **The question.** Does G·Y^j head a Jordan chain of length exactly 2k − 1 − 4j, so that the eigenvalue's multiplicity is k(k + 1)/2 with
  k read off G alone? And can that be proved?

## The question in standard terms

For the analytic matrix family Z(w) on polynomials of degree below n/2 whose determinant carries the cone's spectrum, what are the partial
multiplicities at w = a ∈ GF(2n)*, and which kernel vectors realize them?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **One family carries the spectrum.** Z(w) = S + w^(1−n)M_(ε(w⁻²k)) has det Z(w) = w^((n/2)(1−n)) det(I + C_s(w)) and Z(a) is the kernel operator at the eigenvalue 1/a; it is S + (a + δ)·M_(Φ(a² + δ²)) in w = a + δ, so its first derivative is a⁻¹(Z(a) + S). | proved | A |
| 2 | **Self-adjoint at every w.** So its Jordan blocks at a are those of a ⌈k/2⌉ × ⌈k/2⌉ symmetric matrix function on the eigenvectors. | proved | A |
| 3 | **The first order is a degree.** That matrix's first-order term is a⁻¹ times the Hankel matrix of the top coefficients of N(G) = G(k)G(k + 1), a polynomial of degree n/2 − k in Y; so there is exactly one Jordan block of size 1 when k is odd and none when k is even. | proved | A |
| 4 | **The first step of each chain.** a⁻¹·k·G·Y^i is the second vector of the chain G·Y^i heads, whenever 2i < k − 1. | proved | A |
| 5 | **The chain lemma.** G·Y^j heads a Jordan chain of exactly 2k − 1 − 4j, and these are the Jordan blocks, at every eigenvalue for sides 8 to 64 (64 registered before it was run) and at nine eigenvalues of side 128 covering k = 1 to 15. So the multiplicity k(k + 1)/2 is read off deg G alone. | computed, exact | A, side-64 run, stress test |
| 6 | **Where it stops.** The lemma is conclusion 3 at every order; beyond the first, the reduction's corrections (Hasse derivatives of Φ, shifted Hankel matrices of N(G)) were not put in closed form. The collapse also needs the degree law (B74). | the gap | A |

## Answer

The chains are as predicted, and their first order is proved. At every eigenvalue tested, G·Y^j heads a Jordan chain of exactly
2k − 1 − 4j: at every eigenvalue for sides 8 to 64, and at nine eigenvalues of side 128 up to the eigenvalue 1 with k = 15. So an
eigenvalue's multiplicity is fixed by the degree of its one polynomial, k(k + 1)/2 with k = n/2 − deg G, and the collapse reduces to the
degree law of B74. Proved: one family carries the spectrum, it is self-adjoint at every parameter, and its first-order term on the
eigenvectors is a Hankel matrix of the top coefficients of G's norm G(k)G(k + 1). That norm has degree n/2 − k, so the matrix vanishes
except one corner. This is exactly why one Jordan block has size 1 when k is odd and none does when k is even. The higher orders, which
would prove the whole lemma, were not reached.

## Reading

**Interpretation, not a theorem.**
- **The norm does the work.** At first order everything is the degree of N(G) = G·τG, the polynomial in Y that the shift leaves fixed;
  the chain lengths say that each further order costs two more top coefficients of a deformed norm. A proof at every order would follow the
  least solution as the eigenvalue moves off a.
- **Parity of the parameter.** In characteristic 2 the parameter enters as w·Φ(w²), so the Taylor coefficients come in pairs, the odd one
  a⁻¹ times the even one; the chains are odd in length, 2k − 1 − 4j.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every check is exact over GF(2n), apart from the determinant identity of conclusion 1, checked at six random points
  of GF(2^16) per side (a nonzero polynomial of degree below 2^9 vanishes at a random point with probability below 2^(−7)).
- **Census-only.** Conclusion 5.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 5 (sides 8 to 64) | side 128, nine values of a with k = 1, 2, 3, 4, 6, 7, 8, 11 and 15 | passed: at all nine, G·Y^j heads a chain of exactly 2k − 1 − 4j and these are the blocks, up to [29, 25, 21, 17, 13, 9, 5, 1] at the eigenvalue 1 (k = 15) (JORDAN-CHAINS-S1, 1,652 s) |
| Conclusion 5 at side 64 | registered before it was run | JORDAN-CHAINS-A1 |
| Conclusions 1 to 4 (proved) | — | proofs by hand; checks at sides 4 to 64 |

The scripts are `side64_run.py` and `stress_test.py` beside this note, with their JSON and log files; both run as capped background
units registered in `docs/LONG_RUNNING.md`.

## Literature and provenance

- **Sources.** Partial multiplicities of analytic matrix functions, their Schur-complement (Lyapunov–Schmidt) reduction and the rank
  formula for blocks of size 1 (Gohberg, Lancaster and Rodman); Hasse derivatives in characteristic p.
- **Related records here.** `KLOOSTERMAN-BOUNDS-20261110-001` (one polynomial per eigenvalue), `LINEAR-ROOTS-20261109-001` (the law).
- **Classification.** New as far as found; the search was the bounded one of 2026-11-09, not a priority claim.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`. The spectrum is a contact-level reading (A45 does not bear on it).
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways, at sides 2^m.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (three theorems and a lemma, five checks), the side-64 run and the stress run.
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the Jordan chains from one polynomial | **Status:** Partially successful | The chain lemma holds wherever tested and its first order is proved; the higher orders are not |
| Local direction — the collapse at powers of two | Continue | Two statements remain: the chain lemma beyond first order and the degree law |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B74 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Each eigenvalue's whole Jordan structure is now read off one polynomial's degree, by computation, and its bottom by proof |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained); sub-goal B73 advanced (first order proved, the chain lemma
computed) and re-rated by this report, B74 and B59 rated again. **Assumptions:** none added.

- **What the attempt leaves open.** The chain lemma beyond first order, the degree law, and with them the collapse.

**Next step:** Continue — selected: #1, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The chain lemma at every order (B73) | 3/3 — Breakthrough | 2/3 — Testable | Write the second-order term of the reduction with the explicit first step a⁻¹kGY^i, as moments of N(G) and the Hasse derivative of Φ, and show it vanishes except at the next anti-diagonal → an induction on the order, or the order where the pattern changes | Selected · not started |
| 2 | The degree of the least solution (B74) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B74 → deg G ≤ n/2 − k, or why the identity cannot see K | Alternative · not started |
| 3 | The curve behind each eigenvalue (B59) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B59 → the mechanism, or a reason none exists | Alternative · not started |

1. **The chains.** Payoff 3: with B74 it proves the collapse. Concreteness 2: the first order is proved and the second-order term is
   explicit.
2. **The degree.** Payoff 3: the eigenvector law as a theorem, and with #1 the collapse. Concreteness 1: no route yet.
3. **The curve.** Payoff 3: as recorded. Concreteness 1.

**Recommendation.** Continue with #1.

## Final report as sent

Sent to the owner on 2026-11-10 at 01:50 UTC and copied here verbatim.

The chains epic is closed and published. The prediction holds everywhere I tested it: at each eigenvalue, the eigenvector G·Y^j heads a Jordan chain of exactly 2k − 1 − 4j, and those are all the blocks. So an eigenvalue's whole Jordan structure, and its multiplicity k(k+1)/2, is read off the degree of its one polynomial. This holds at every eigenvalue for sides 8 to 64 (side 64 registered before running) and at seven of nine sampled eigenvalues at side 128 so far. The last two, including the eigenvalue 1 with k = 15, are still running.

I proved the bottom of the structure. The family carrying the spectrum is self-adjoint at every parameter, and its first derivative on the eigenvectors is a Hankel matrix of the top coefficients of G's norm G(k)G(k+1). That norm has degree n/2 − k, so all but one corner vanishes: exactly one size-1 block when k is odd, none when k is even. The higher orders aren't proved.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the Jordan chains from one polynomial | **Status:** Partially successful | The chain lemma holds wherever tested and its first order is proved |
| Local direction: the collapse at powers of two | Continue | Two statements remain: the chains beyond first order, and the degree law |
| Broader exploration: G5 with G1 | Known alternatives | Backlog B22–B74 |
| Long-term goal: G5 Dynamics | Capability gained | Each eigenvalue's Jordan structure is read off one polynomial's degree |

**Next step:** Continue with #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | The chain lemma at every order (B73) | 3/3 | 2/3 | Write the second-order term with the explicit first step a⁻¹kGY^i and show it vanishes except on the next anti-diagonal → an induction, or the order where it breaks | Selected |
| 2 | The degree of the least solution (B74) | 3/3 | 1/3 | As recorded in B74 | Alternative |
| 3 | The curve behind each eigenvalue (B59) | 3/3 | 1/3 | As recorded in B59 | Alternative |

**Corrections:** none. **Goals:** G5 checkpoint (capability gained); sub-goal B73 advanced and re-rated (3/3, 2/3); B74 and B59 stay open. **Assumptions:** none added. The side-128 stress run (JORDAN-CHAINS-S1) is still running, and I'll fold it in when it finishes. Commits: 25ab6ffa4 (pre-registration), 3d9912955 (epic), 692a8c533 and ceefda576 (tracking), 2eb84dc45 (shared docs).
