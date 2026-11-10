# The leading form at every order

Epic `LEADING-FORM-20261110-001` (program foundations, group `collapse`, sub-goals B73 and B91), 2026-11-10. Pre-registered in commit
f8e8b996c, with the stop rule and the halving test frozen there (`preregistration.md` beside this note).

## The question

- **Where it comes from.** `CHAIN-ORDERS-20261110-001` reduced the chain lemma to one leading form: on the eigenvectors G·Y^j the
  reduction of the cut-open torus's family starts at u^(2k−1−2(i+j)) with coefficient [k − i − j a power of two]. It computed the form at
  every eigenvalue to side 256 and proved it for co-distance t = k − i − j ≤ 2. Its directions 1 (B73) and 2 (B91, as a side check) had
  the coordinator's go-ahead on 2026-11-10.
- **The question.** Can the form be proved at every order, by closed forms of the reduction's vectors order by order (route A), or by
  an induction on k if the reduction splits when the index halves (route B)?

## The question in standard terms

For the self-adjoint analytic family Ẑ(λ) on polynomials of degree below n/2, what are the Schur-complement vectors of its reduction
to ker Ẑ(0) = G·F[Y]_(<⌈k/2⌉), order by order, and does the reduction at k = 2c decouple over the parity of the power of Y?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The index does not halve.** At all 61 eigenvalues with even k ≥ 4 for sides 16 to 64, in every variant of the frozen test (two complements, two parametrizations), the reduction has a nonzero entry mixing even and odd powers of Y below order 2k. B91's strong form is refuted at these sides; the halving of the leading matrix, proved, stands. | computed, exact, frozen | B |
| 2 | **The operator is a Wronskian.** G·Z_0F ≡ (k + 1)·W(G, F) mod k^h for every F, W(A, B) = A(k)B(k + 1) + B(k)A(k + 1); so the chain equations become equations among polynomials in Y. | proved | A |
| 3 | **The second vector's Wronskian.** For every second chain vector, W(G, φ_2) = N·Y^i·(1 + L(Y)) + a²G(0)²[i = 0]Y^(h−1) mod Y^h, L(Y) = Y + Y² + ⋯ + Y^(h/2). | proved | A |
| 4 | **A second solution.** There is G′ of degree h + k − 1 − 2J solving the kernel equation to order h − J − 1 with W(G, G′) = c·Y^(h−J−1), so every F is [W(G′, F)G + W(G, F)G′]/(cY^(h−J−1)). (G(0) ≠ 0 is needed, and holds at every eigenvalue to side 128.) | proved | A |
| 5 | **Where the cancellation sits.** At co-distance 3 the pure part of the order-5 coefficient is 1 and the corrections to the second vector add exactly 1, so the coefficient is 0; in 97 of 129 cases the correction's self-pairing alone carries it. | computed, exact | A |
| 6 | **Where it stops.** By the frozen rule the attempt ends at order 2: the second vector has a closed form only through the second solution G′ and a few top coefficients the degree bound fixes, and the cancellation at co-distance 3 was not derived from it. | the gap | A |

## Answer

Neither route reached the leading form beyond co-distance 2. The reduction does not split when the index halves: at every tested
eigenvalue the entries that mix even and odd powers of Y are nonzero below order 2k, so the induction on k has no foothold, and by the
frozen rule the co-distance route was taken. There the family turned out to be a Wronskian: G·Z_0 is (k + 1) times W(G, ·), which gives
the second chain vector's Wronskian in closed form and a second solution G′ whose Wronskian with G is a single power of Y. But the
second vector itself needs G′, and the cancellation that makes the co-distance-3 coefficient vanish (the corrections adding 1 to a pure
part of 1) was not derived. The attempt stops at order 2, as frozen.

## Reading

**Interpretation, not a theorem.**
- **Two solutions, as in a continued fraction.** G and G′ behave like consecutive convergents: their Wronskian is a monomial,
  c·Y^(h−J−1). The leading matrix of `CHAIN-ORDERS-20261110-001` is itself the Hankel matrix of a continued fraction. A proof of the
  leading form would likely run the Euclidean algorithm of the eigenvalue's Padé function along the parameter.
- **The cancellation is in the corrections.** The pure vectors k^r·x would give coefficient 1 at every co-distance; at co-distance 3
  the corrections cancel it, mostly through their own pairing. The parity structure survives only partly (S2 at 33 of 61 eigenvalues
  in one variant), not as a splitting.
- **Nothing here is a length or a distance.**

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every check is exact over GF(2n).
- **Census-only.** Conclusions 1 and 5.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 1 (sides 16 to 64, frozen) | — (the frozen test fixed its sides; it refutes, so a larger side cannot reverse it) | not run |
| Conclusions 2 to 4 (proved) | side 128 | passed (checks 1 to 3 run to side 128) |
| Conclusion 5 (sides 16 to 64) | side 128 | not run; the co-distance-3 coefficient itself is checked to side 256 by `CHAIN-ORDERS-20261110-001` |

## Literature and provenance

- **Sources.** Wronskians over the quadratic extension F(k)/F(Y); consecutive Padé approximants and the monomial determinant of
  consecutive convergents; the 2n + 1 rule of self-adjoint perturbation theory.
- **Related records here.** `CHAIN-ORDERS-20261110-001` (the leading form, three orders), `JORDAN-CHAINS-20261110-001`,
  `KLOOSTERMAN-BOUNDS-20261110-001` (the kernel and its Padé form).
- **Classification.** New as far as found; the bounded search of 2026-11-09, not a priority claim.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`. A45 does not bear on the spectrum.
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways, at sides 2^m.

## Ratio

Since the epic opened:
- **Substantive.** Ticket B (the frozen test) and ticket A (five theorems, five checks).
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the leading form at every order | **Status:** Inconclusive | Stopped at order 2 by the frozen rule; the halving route refuted at sides 16 to 64; the family's Wronskian form and a second solution proved |
| Local direction — the collapse at powers of two | Continue, bounded | The cancellation at co-distance 3 is located (the corrections, on the second solution); the degree law is untouched |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B80 |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | The second chain vector needs a second solution of the eigenvalue's equation; the index does not halve |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned); sub-goal B73 attempted again (stopped at order 2) and re-rated
by this report; sub-goal B91 retired (its strong form refuted); B74 and B59 rated again. **Assumptions:** none added.

- **What the attempt leaves open.** The leading form beyond co-distance 2, the degree law, and with them the collapse.

**Next step:** Continue — selected: #1, bounded to co-distance 3, unless the coordinator chooses otherwise.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The leading form through the pair of solutions (B73) | 3/3 — Breakthrough | 2/3 — Testable | Write the co-distance-3 coefficient ⟨Sψ_2, ψ_2′⟩ through the Wronskians of the pair (G, G′), N(G), N(G′) and G·τG′, and prove that the corrections add 1 → co-distance 3 proved and a recursion for the pair; stop if co-distance 3 is not proved in one epic, and park the line | Selected · not started |
| 2 | The degree of the least solution (B74) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B74 → deg G ≤ n/2 − k, or why the identity cannot see K | Alternative · not started |
| 3 | The curve behind each eigenvalue (B59) | 3/3 — Breakthrough | 1/3 — Stated | As recorded in B59 → the mechanism, or a reason none exists | Alternative · not started |

1. **The pair.** Payoff 3: with B74 it proves the collapse. Concreteness 2: the second solution and the second vector's Wronskian are
   explicit, and the cancellation to explain is located.
2. **The degree.** Payoff 3: the eigenvector law as a theorem. Concreteness 1: the pair (G, G′) is new material but gives no route yet.
3. **The curve.** Payoff 3: as recorded. Concreteness 1.

**Recommendation.** Continue with #1, bounded to co-distance 3. The chain line has now taken three epics for three orders; if
co-distance 3 does not yield, the collapse line should be parked behind other goals rather than pressed further.
