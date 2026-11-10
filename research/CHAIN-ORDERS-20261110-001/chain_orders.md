# The chain lemma at every order

Epic `CHAIN-ORDERS-20261110-001` (program foundations, group `collapse`, sub-goal B73 continued), 2026-11-10. Pre-registered in commit
c252175e4.

## The question

- **Where it comes from.** `JORDAN-CHAINS-20261110-001` computed that at each eigenvalue of the cut-open torus at side 2^m the
  eigenvector G·Y^j heads a Jordan chain of exactly 2k − 1 − 4j, k = n/2 − deg G, and proved its first order. Its direction 1 had the
  coordinator's go-ahead on 2026-11-10.
- **The question.** Does the chain lemma hold at every order, and can that be proved? Registered route: the leading part of the reduction
  of the family to the eigenvectors is u⁻¹Y^k L(u²/Y), u = (w − a)/a, L(x) = x + x² + x⁴ + ⋯, and its leading matrix is invertible.

## The question in standard terms

For the self-adjoint analytic family Z(w) on polynomials of degree below n/2 whose determinant carries the cone's spectrum, what is the
Lyapunov–Schmidt reduction to ker Z(a) = G·F[Y]_(<⌈k/2⌉) at each a ∈ GF(2n)*, to the orders that fix its Smith form?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The family's perturbation is sparse.** Near each a, Z(w) = S + (w/a)·(b + k^h L(w²/k)): the parameter enters only through w/a and through L, one term at each power of two. | proved | A |
| 2 | **One moment matrix.** Z(w) is equivalent to diag(H(w), I), H(w) the Hankel matrix of one explicit power series ψ(w) = (Ω + k + 1)/(kΩ + (k + 1)²) in Y. So the Jordan blocks at 1/a are the partial multiplicities of a single moment matrix. | proved | A |
| 3 | **The leading form.** On the eigenvectors G·Y^j, the reduction's entry (i, j) starts at u^(2k−1−2(i+j)), with coefficient 1 when k − i − j is a power of two and 0 otherwise: its leading part is the Hankel matrix of u⁻¹Y^k L(u²/Y). This holds at every eigenvalue for sides 8 to 256 (64 and below before registration, 128 after, 256 in the stress run). | computed, exact | A, stress test |
| 4 | **Its leading matrix is invertible for every k.** [k − i − j a power of two] has determinant 1 over GF(2), by a recursion that halves k; it is the Hankel matrix of the continued fraction 1/(1 + z/(1 + z/⋯)). So conclusion 3 is the whole chain lemma. | proved | A |
| 5 | **The bottom three orders.** Every eigenvalue has exactly k mod 2 Jordan blocks of size 1, none of size 2, and exactly one of size 3 when k is even and none when k is odd. For k ≤ 2 this is the whole chain lemma. | proved | A |
| 6 | **Where it stops.** Orders 4 and up need the reduction's second vector, which leaves the multiples of G; the pure vectors k^r·G·Y^i would give coefficient 1 at every co-distance, and the computed form says these cancel except at powers of two. That cancellation was not found in closed form. The collapse also needs the degree law (B74). | the gap | A |

## Answer

The chain lemma comes down to one explicit statement, and that statement holds everywhere tested. Near each eigenvalue the family is a
single moment matrix. On the eigenvectors G·Y^j its reduction starts, entry by entry, at u^(2k−1−2(i+j)), with leading coefficient 1
exactly when k − i − j is a power of two. That leading matrix is invertible for every k, so this form gives each eigenvalue's whole Jordan
structure: 2k − 1, 2k − 5, …. The form holds at every eigenvalue for sides 8 to 256. Proved: the reduction to one moment matrix, the
leading matrix's invertibility, and the bottom three orders (no block of size 2; one block of size 1 when k is odd, one of size 3 when
it is even). The orders from four on are not proved.

## Reading

**Interpretation, not a theorem.**
- **The same polynomial on both sides.** The family's perturbation is k^h L(δ²/k) and the reduction's leading part is u⁻¹Y^k L(u²/Y):
  the linearized polynomial L, one term per power of two, appears in the input at the bottom coefficients and in the output at the top
  ones. The continued fraction of L(z)/z, 1/(1 + z/(1 + ⋯)), is what makes the leading matrix invertible.
- **A characteristic-zero pattern in characteristic two.** The blocks 2k − 1, 2k − 5, … are those of the symmetric square of one Jordan
  block of size k in characteristic 0 (Sym²V_(k−1) = V_(2k−2) ⊕ V_(2k−6) ⊕ ⋯ for sl₂). Over GF(2) neither the symmetric nor the exterior
  square of one Jordan block gives them in general: the exterior square agrees only at k = 1, 2 and 4 and the symmetric square only at
  k = 1, and at k = 3 and from 5 to 15 both differ, their blocks capped at a power of two (computed, check 8).
- **Halving.** The leading matrix at k = 2c splits into those at c and c − 1 over the even and odd powers of Y, and the chains match:
  at k = 2c the chain of G·Y^(2i) has length 2(2c − 1 − 4i) + 1 and that of G·Y^(2i+1) has 2(2(c − 1) − 1 − 4i) + 1, twice a chain at
  index c or c − 1, plus one. The eigenvectors with even and odd powers of Y may behave like those at half the index.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every check is exact over GF(2n) or GF(2).
- **Census-only.** Conclusion 3.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 3 (sides 8 to 128) | side 256, every a in GF(512)* (k up to 22) | passed: no failures among 511 values of a (CHAIN-ORDERS-S1, 256 s) |
| Conclusion 4 (proved) | k < 1000 | passed |
| Conclusions 1, 2 and 5 (proved) | — | proofs by hand; checks at sides 4 to 128 |

The script is `stress_test.py` beside this note, with its JSON and log files; it ran as a capped background unit registered in
`docs/LONG_RUNNING.md`.

## Literature and provenance

- **Sources.** Partial multiplicities and the Lyapunov–Schmidt reduction of analytic matrix functions (Gohberg, Lancaster and Rodman);
  Padé approximation and Hankel matrices; Stieltjes continued fractions and their Hankel determinants; Wigner's 2n + 1 rule;
  Artin–Schreier roots in characteristic 2.
- **Related records here.** `JORDAN-CHAINS-20261110-001` (the chains, their first order), `KLOOSTERMAN-BOUNDS-20261110-001` (one
  polynomial per eigenvalue, the Padé form at w = a), `LINEAR-ROOTS-20261109-001` (the law).
- **Classification.** New as far as found; the search was the bounded one of 2026-11-09, not a priority claim. The continued fraction of
  Σ z^(2^r − 1) over GF(2) is immediate from L² + L = z.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`. The spectrum is a contact-level reading (A45 does not bear on it).
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways, at sides 2^m.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (five theorems, eight checks) and the stress run.
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the chain lemma at every order | **Status:** Partially successful | The lemma is one explicit leading form, true at every eigenvalue to side 256, with its leading matrix invertible by proof; the form itself is proved for its first three orders |
| Local direction — the collapse at powers of two | Continue | Two statements remain: the leading form from order 4 on, and the degree law |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B80 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Each eigenvalue's Jordan structure is the leading part of one moment matrix, a linearized polynomial; its bottom three orders are proved |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained); sub-goal B73 advanced (the leading form computed to side 256, its
leading matrix invertible, the bottom three orders proved) and re-rated by this report; sub-goal B91 added for direction 2 (halving
the index); B74 and B59 rated again. **Assumptions:** none added.

- **What the attempt leaves open.** The leading form from order 4 on, the degree law, and with them the collapse.

**Next step:** Continue — selected: #1, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The leading form at every order (B73) | 3/3 — Breakthrough | 2/3 — Testable | Find the reduction's second vector in closed form from the moment matrix of ψ = (P + ξτG)/(Q + kξτG), G = Q + kP, and check that it cancels the coefficient at u⁵ on co-distance 3 → an induction on the co-distance by the 2n + 1 rule, or the first order with no closed form | Selected · not started |
| 2 | Halving the index (B91) | 3/3 — Breakthrough | 2/3 — Testable | Test whether the reduction at k = 2c, split by the parity of the power of Y, is u times the reductions at c and c − 1 with u replaced by u², to the orders that fix the blocks → a renormalization lemma and an induction on k, or the order where the splitting fails | Alternative · not started |
| 3 | The degree of the least solution (B74) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B74 → deg G ≤ n/2 − k, or why the identity cannot see K | Alternative · not started |
| 4 | The curve behind each eigenvalue (B59) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B59 → the mechanism, or a reason none exists | Alternative · not started |

1. **The leading form.** Payoff 3: with B74 it proves the collapse, and alone it proves the chain lemma. Concreteness 2: the first three
   orders are proved and the obstruction at the second vector is explicit.
2. **Halving.** Payoff 3: an induction on k would prove the leading form at once. Concreteness 2: the splitting of the leading matrix is
   proved and the full splitting is a direct computation.
3. **The degree.** Payoff 3: the eigenvector law as a theorem, and with #1 the collapse. Concreteness 1: no route yet.
4. **The curve.** Payoff 3: as recorded. Concreteness 1.

**Recommendation.** Continue with #1; #2 attacks the same statement by another route and could replace it if the second vector has no
closed form.
