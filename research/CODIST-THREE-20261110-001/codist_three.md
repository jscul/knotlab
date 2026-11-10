# The co-distance-3 cancellation

Epic `CODIST-THREE-20261110-001` (program foundations, group `collapse`, sub-goal B73), 2026-11-10. Pre-registered in commit 56e1ba31d,
with the stop rule frozen there; at the coordinator's go-ahead, the last epic on the collapse line for now.

## The question

- **Where it comes from.** `LEADING-FORM-20261110-001` stopped at order 2: the reduction's second vector needs a second solution of the
  eigenvalue's equation, and at co-distance 3 its corrections add exactly 1 to a pure part of 1. Its direction 1 had the coordinator's
  go-ahead, bounded to co-distance 3.
- **The question.** Can the co-distance-3 cancellation be derived: do the reduction's coefficients at λ⁴ and λ⁵ vanish on every entry
  with i + j ≤ k − 3, by writing the second vector on the pair of solutions?

## The question in standard terms

For the reduction M(λ) of the self-adjoint family Ẑ to the eigenvectors G·Y^j, prove [λ⁴]M_ij = [λ⁵]M_ij = 0 for i + j ≤ k − 3, from
explicit second vectors of the Jordan chains.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The second order is a gap.** N·L(Y) has no terms from degree h − k + 1 to h − 2, and a²G(0)² at Y^(h−1), where N = G(k)G(k + 1) and L(Y) = Y + Y² + ⋯ + Y^(h/2). This is the second-order solvability in its plainest form. | proved | A |
| 2 | **Half of order 4 cancels.** At co-distance at least 3 the order-4 coefficient splits into five pieces; the two that only involve the second vector's Wronskian vanish, one by the gap and one because a double sum over powers of two collapses in characteristic 2. | proved | A |
| 3 | **A canonical second vector.** R_x + k(W_x + P·R_x)/Q, with R_x the remainder of W_x·Q″ by Q (G = Q + kP, Bezout cofactors Q″, P″), is a second chain vector; every other differs by a kernel vector, which does not change the order-4 coefficient. | proved | A |
| 4 | **The rest of order 4.** With the canonical vector the remaining three pieces add to 0 at all 862 pairs at sides 16 to 64, so the order-4 coefficient vanishes there. | computed, exact | A |
| 5 | **Where it failed.** The remaining identity is about the high coefficients of a quotient by Q, not found in closed form; the order-5 coefficient was not reduced; a first continued-fraction reading of the reduction (the top coefficients of ξN/(1 + ξ(k + 1 + Λ″_0))) does not show the leading form. | the gap | A |

## Answer

The co-distance-3 cancellation was not derived, so by the frozen rule the collapse line is parked. What was reached: the second-order
fact becomes a gap in one product, N·L(Y), and with it half of the order-4 coefficient cancels by proof. The power-of-two pattern of the
leading form appears there for a visible reason: in characteristic 2 a double sum over pairs of powers of two keeps only the diagonal.
The other half of order 4 is an identity about a quotient by Q, true at every pair tested but not derived, and order 5 was not reached.

## Reading

**Interpretation, not a theorem.**
- **Where the powers of two come from.** The extraction [k^(h−2)] reads a polynomial in Y at the degrees h − 1 − 2^t, and L(Y) carries
  the powers 2^t′; their double sum collapses to the doubled powers. That is the characteristic-2 arithmetic behind ε_t in the leading
  form, seen here at its first nontrivial order.
- **What a proof would need.** The high coefficients of quotients by Q, the Padé denominator: the Euclidean algorithm of the eigenvalue's
  Padé function along the parameter, which neither this epic nor `LEADING-FORM-20261110-001` put in closed form.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every check is exact over GF(2n).
- **Census-only.** Conclusion 4.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 1 (proved) | side 128 | passed (check 1 runs to side 128) |
| Conclusions 2 and 3 (proved) | — | proofs by hand; checks at sides 16 to 64 |
| Conclusion 4 (sides 16 to 64) | side 128 | not run; the order-4 coefficient itself is checked to side 256 by `CHAIN-ORDERS-20261110-001` |

## Literature and provenance

- **Sources.** Bezout cofactors and the Euclidean algorithm over F[Y]; Wronskians over F(k)/F(Y); sums over powers of two in
  characteristic 2.
- **Related records here.** `LEADING-FORM-20261110-001`, `CHAIN-ORDERS-20261110-001`, `JORDAN-CHAINS-20261110-001`,
  `KLOOSTERMAN-BOUNDS-20261110-001`.
- **Classification.** New as far as found; the bounded search of 2026-11-09, not a priority claim.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`. A45 does not bear on the spectrum.
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways, at sides 2^m.

## The collapse line, parked

Parked 2026-11-10 by the frozen rule of this epic, as the coordinator set it.
- **Proved along the line.** Each eigenvalue's Jordan blocks at sides 2^m are those of one moment matrix, whose leading part is the
  Hankel matrix of u⁻¹Y^k L(u²/Y) (`CHAIN-ORDERS-20261110-001`); that leading matrix is invertible for every k; the blocks of size at
  most 3 are as the chain lemma says, and the lemma holds in full for k ≤ 2; the kernel operator is a Wronskian with a second solution
  of monomial Wronskian (`LEADING-FORM-20261110-001`); the second order is the gap of N·L(Y) (this epic).
- **Computed, not proved.** The leading form at every eigenvalue to side 256; the Kloosterman law and the degree law (to sides 128
  and 512); the collapse itself to side 128.
- **Open.** The leading form from order 4 on (B73), the degree of the least solution (B74), the curve behind each eigenvalue (B59).
- **Pick for a restart: B59.** Both B74 and B59 rate Payoff 3/3, Concreteness 1/3. B59 is the deeper target: the blocks are the
  characteristic-0 symmetric square of one Jordan block of size k and the multiplicities are Kloosterman's, so one k-dimensional object
  behind each eigenvalue would settle the chains, the degree and the field at once. B74 alone would leave the chains open.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (three theorems, four checks).
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the co-distance-3 cancellation | **Status:** Inconclusive | Half of the order-4 coefficient cancels by proof and the rest by computation; order 5 was not reduced |
| Local direction — the collapse at powers of two | Full pivot (parked) | The frozen rule: the cancellation was not derived in this epic |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B80 |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | The chains' next order needs the high coefficients of quotients by the Padé denominator |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned); sub-goals B73, B74 and B59 parked with the line (B59 picked for a
restart). **Assumptions:** none added.

- **What the attempt leaves open.** The order-4 identity for the canonical vector, order 5, and with them the chain lemma and the
  collapse.

**Next step:** Full pivot — the collapse line is parked; when it resumes, B59 first.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The curve behind each eigenvalue (B59) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B59 → the mechanism, or a reason none exists | Parked · picked for a restart |
| 2 | The degree of the least solution (B74) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B74 → deg G ≤ n/2 − k, or why the identity cannot see K | Parked |
| 3 | The leading form from order 4 on (B73) | 3/3 — Breakthrough | 1/3 — Stated | Put the high coefficients of the quotient (W_x + P·R_x)/Q in closed form → the order-4 identity, then order 5 | Parked |

1. **The curve.** Payoff 3: it would explain the multiplicities, the blocks and the field at once. Concreteness 1: no candidate object.
2. **The degree.** Payoff 3: the eigenvector law as a theorem. Concreteness 1: no route.
3. **The leading form.** Payoff 3: with B74 the collapse. Concreteness 1: three epics reached three orders; the next step needs a closed
   form not in sight.

**Recommendation.** Full pivot away from the collapse line, as frozen; restart it with B59.

## Final report as sent

Sent to the owner on 2026-11-10 at 04:01 UTC and copied here verbatim.

I didn't derive the co-distance-3 cancellation, so under the frozen rule the collapse line is now parked. The epic is closed and published.

**What I proved.** The chains' second step turns out to be a gap: N·L(Y), with N = G(k)G(k+1) and L(Y) = Y + Y² + Y⁴ + …, has no terms between degree n/2 − k + 1 and n/2 − 2. At co-distance 3 the order-4 coefficient splits into five pieces, and two of them vanish by that gap. One of those two vanishes because, in characteristic 2, a double sum over pairs of powers of two keeps only its diagonal. That's where the leading form's powers of two come from. I also wrote down an explicit second chain vector, built from G's Bezout cofactors.

**What's left.** The other three pieces add to 0 at all 862 pairs I tested (sides 16 to 64), but proving that needs the high coefficients of a quotient by the Padé denominator Q, which I couldn't put in closed form. Order 5 wasn't reached.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the co-distance-3 cancellation | **Status:** Inconclusive | Half of order 4 cancels by proof and the rest by computation. Order 5 wasn't reduced |
| Local direction: the collapse at powers of two | Full pivot (parked) | Per the frozen rule: not derived in this epic |
| Broader exploration: G5 with G1 | Known alternatives | Backlog B22–B80 |
| Long-term goal: G5 Dynamics | Obstruction learned | The next order needs high coefficients of quotients by the Padé denominator |

**Next step:** Full pivot. When the line resumes, start with B59.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | The curve behind each eigenvalue (B59) | 3/3 | 1/3 | As recorded in B59 | Parked, picked for a restart |
| 2 | The degree of the least solution (B74) | 3/3 | 1/3 | As recorded in B74 | Parked |
| 3 | The leading form from order 4 on (B73) | 3/3 | 1/3 | Close the quotient by Q → order 4, then order 5 | Parked |

**My pick between B74 and B59 is B59.** Both rate 3/3 and 1/3. The blocks look like the characteristic-0 symmetric square of a single block of size k, and the multiplicities are Kloosterman's, so finding one k-dimensional object behind each eigenvalue would settle the chains, the degree and the field together. B74 on its own would leave the chains open.

**Corrections:** none. **Goals:** G5 checkpoint (obstruction learned), and G5 is now Idle with the line parked. B73, B74 and B59 are parked. **Assumptions:** none added. Commits: 56e1ba31d (pre-registration), 71453e50a (epic), d2ae201d4 (shared docs), 5bcc42be2 (tracking).
