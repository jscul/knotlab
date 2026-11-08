# Full reach on the cut-open torus

Epic `FULL-REACH-20261108-001` (program foundations), 2026-11-08. A preliminary record: the coordinator switched the line to growing a
network of rings from a law before a proof was attempted.

## The question

- **Where it comes from.** `GENUS-CUT-20261108-001` found, by computation, that after a ring of cuts round the n × n torus in each
  direction every uncut contact still needs every ring on sides 3 to 20 except 8 and 16. The coordinator relayed its direction 2 on
  2026-11-08: prove that every contact reaches every ring unless n is a power of two of at least 8, or find the first n where it fails.
- **The question.** On the cut-open torus, which sides keep full reach?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Only powers of two fail, to side 48.** Every uncut contact needs every ring on every side from 3 to 48 except 8, 16 and 32. There n − 4 contacts (4, 12 and 28) each never need the three rings of one corner. | exploratory census, exact | A |

## Answer

The stop rule's first outcome is not reached, and the claim does not fail: it holds exactly on every side from 3 to 48, with the
failures exactly at 8, 16 and 32. No proof was attempted before the switch.

## Reading

**Interpretation, not a theorem.**
- **Powers of two again.** Cutting the torus open removes the cancellation of the two ways round, which kept even sides from the
  antipode (`LATTICE-NET-20261108-001`). What remains at sides 2^m is a cancellation inside the square itself, of the kind Lucas'
  theorem gives for binomial coefficients mod 2.
- **Not a metric.** Nothing here is a length or a distance.

## Lag cutoffs and census-only claims

- **No lag cutoff.** The census is exact: walk counts are followed until the next row lies in the span of the earlier ones.
- **Census-only.** Conclusion 1 is computed for sides 3 to 48 only.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Only powers of two fail (1) | the census itself runs to side 48, 28 sides past `GENUS-CUT-20261108-001A`'s check | pass |

## Literature and provenance

- **Sources.** Walks on grids with absorbing boundaries and their mod-2 counts; Lucas' theorem.
- **Classification.** Ticket A: new as far as found, a census.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut both ways.

## Ratio

Since the epic opened:
- **Substantive.** One exact census (A).
- **Administrative.** This note and the closure.

## Pending the owner

- **Counted length as a native magnitude**, which gates distance across time; the owner has been asked again by the coordinator.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — full reach on the cut-open torus | **Status:** Inconclusive | The claim holds to side 48 with the failures exactly at the powers of two from 8; no proof yet |
| Local direction — composed topology across time | Continue | The proof is the next step on this question, once the line returns to it |
| Broader exploration — G5 with G1 | Known alternatives | Growing a network of rings from a law (taken next, at the coordinator's switch); which lattices compose everywhere |
| Long-term goal — G5 Dynamics (question 4) | No demonstrated advance | A computed pattern, not yet a theorem |

**Corrections:** none. **Goals:** a G5 checkpoint (no demonstrated advance). **Assumptions:** none added.

- **What the attempt leaves open.** A proof that full reach fails exactly at the powers of two from 8.

**Next step:** Continue — selected: #1, after the growth epic.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove full reach on the cut-open torus | 2/3 — Substantial | 3/3 — Ready | Write the walk counts on the cut-open grid as images of the doubled torus and find where the powers of two cancel → a proof, or the first side where the claim fails | Selected · parked |
| 2 | Grow a network of rings from a law (G1, with G5) | 3/3 — Major | 1/3 — Stated | Taken next as its own epic | Selected |

1. **The proof.** Ready; the census fixes the statement.
2. **Growth.** Taken next at the coordinator's switch.

**Recommendation.** Continue with the proof after the growth epic.
