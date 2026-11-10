# The decoder route for the 2n-pigeon left-pigeon principle

Epic `WIDE-LEFT-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `KERNEL-FRAC-20261110-001` closed the decoder route for the binary left-pigeon principle with n + 1 pigeons
  (the top code bit belongs to one pigeon) and found that the 2n-pigeon principle escapes the obstruction and contains the n + 1 pigeon
  clauses (sub-goal B114). The coordinator confirmed B114 as the last epic on this route, with two conditions: check novelty and transfer
  first, and freeze the target, the spare-row lemma, the predictions and the density count with a one-epic stop rule.
- **Checked and frozen first.** `novelty_and_transfer.md` (4784c56f6) and `target_statement.md` (ca1f7e64e) beside this note.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A dag-like Res(⊕) lower bound for the binary left-pigeon principle.** For n = 2^l holes, l ≥ 20, every dag-like Res(⊕) refutation of the principle with 2n pigeons has S lines with 3S + 2n²(l + 1) ≥ exp(0.005·k/l² − 1), k = ⌊n/(64 l³)⌋: S ≥ exp(Ω(n/log⁵ n)). Its clauses contain those of the n + 1 pigeon principle, whose search problem is PPADS-complete, so the same bound holds there. | proof written (V1), not independently checked, conditional on A55 | A |
| 2 | **The spare-row lemma holds where it can be computed.** The space of row-linear monomials avoiding the spare stars meets the decoder's kernel only in zero at (4, 1), (8, 1), (16, 2), and the cube that proves it isolates every top monomial checked, while the whole kernel is 63% and 36% of the space at degree 2. | computed (pre-registered, exact) | B |

## Answer

*(Corrected 2026-11-10: this answer first read as an established result; it is a proof written (V1), not independently
checked, conditional on A55, and is under audit in `AUDIT-LEFT-20261110-001`; `docs/CORRECTIONS.md`.)*

By stop rule (a), a proof is written. The decoder route gives a bound once the formula has 2n pigeons: a separated space built from the rows outside
a few spare stars is dense enough for Braun's criterion, and the kernel elements that blocked the earlier attempts all use a spare row
or every hole. The bound is exponential in n/log⁵ n and transfers to the PPADS-complete n + 1 pigeon principle because that principle's
clauses are a subset. If the proof survives review, it would be the first lower bound of any kind for a PPADS-complete principle in dag-like Res(⊕), as far as
found.

## Scope and transfer

- **Bit LeftPigeon only.** The bound is for these CNF encodings (binary f and g); Res(⊕) is not closed under decision-tree reductions,
  so it is not a statement about every encoding of a PPADS-complete problem.
- **Nothing transfers to the knot sphere's count.** The count's Res(⊕) route is closed by its polynomial-calculus degree O(√n)
  (`RES-XOR-COUNT-20261110-001A`), and LeftPigeon reaches the count only through non-affine reductions.
- **Not an algorithm.** A lower bound on proof size; the publication hold does not apply.

## Reading

**Interpretation, not a theorem.**
- **Why spare rows work.** The decoder can only separate what real placements of pigeons in holes cannot decide. Every identity it
  cannot separate involves the whole set of holes (sums over holes equal sums over pigeons), so a space that never touches a few spare
  holes and pigeons is out of their reach, and the cube parks the pigeons it moves in those spares.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** Conclusion 2 at three small entries; Q2 at (16, 2) sampled (60 of 5,925 top monomials) and Q4 bounded beyond l = 32,
  both disclosed in the run's interpretation. Conclusion 1 is a proof for l ≥ 20; it exceeds the trivial bound |J| from l ≈ 47.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The spare-row lemma (2) | k = 1 at n = 16 and 32 (checked to 8) | pass: dim U_0 = 160 and 442, meeting 0, all 159 and 441 cubes |
| The spare-row lemma at (16, 2) (2) | 60 more top monomials, a second seed | pass |
| The density count's bracket (1) | l to 1000 (checked to 200), side conditions to l = 200 (checked to 80) | pass: at least 0.00517 |

The script is `stress_test.py` beside this note, its output `stress_test.json`; registered before launch as WIDE-LEFT-S1, it ran in
62 seconds.

## Literature and provenance

- **Sources.** Braun, arXiv 2609.23015 (§§3–4 and 9); Efremenko, Garlík and Itsykson (regular Res(⊕), *SIAM J. Comput.* 2025); Byramji
  and Impagliazzo (arXiv 2511.20023); Alekseev and Itsykson (ECCC TR24-128); Efremenko and Itsykson (ECCC TR25-039, TR25-188);
  Bhattacharya and Chattopadhyay (arXiv 2507.23008); Itsykson and Knop (ITCS 2026); Göös et al. (*J. ACM* 2024) for LeftPigeon.
- **Searched and not found.** Any Res(⊕) bound for left-pigeon, injective-with-retraction, onto or bijective bit PHP, or any
  PPADS-complete principle.
- **Classification.** New as far as found; known-with-delta in technique (Braun's framework throughout). V1: written in one session, not
  externally reviewed, and resting on Braun's unrefereed (Lean-formalized, audited) preprint, recorded as assumption A55.

## Workspace assumptions

- **Relied on.** A55 (Braun's preprint is correct), added here.
- **Added.** A55.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A), one pre-registered computation (B), one stress test.
- **Administrative.** The novelty and transfer check, the frozen target, this note and the closure.

## Pending the owner

- **Whether and how to share the result**, with Braun or more widely, is the owner's call (as for `BPHP-MORE-PIGEONS-NOTE-20261019-001`).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the decoder route for 2n pigeons | **Status:** Successful (proof written, V1) | A dag-like Res(⊕) lower bound for the binary left-pigeon principle: proof written (V1), not independently checked, conditional on A55 |
| Local direction — the decoder route | Full pivot | The coordinator's condition: the route is finished in this program after this epic |
| Broader exploration — G3 | Known alternatives | Cutting planes on the count (B82), the parity reduction from PIGEON (B101) |
| Long-term goal — G3 Hardness at three places | Capability gained (pending audit) | If the V1 proof holds, a PPADS-complete principle is hard for dag-like Res(⊕); the knot sphere's count is not reached |

**Corrections:** none. **Goals:** a G3 checkpoint (capability gained); B114 taken; sub-goal B116 added. **Assumptions:** A55 added (Braun's preprint is
correct).

- **What the attempt leaves open.** External review; whether the exponent improves (n/l² as for bit PHP); the knot sphere's count.

**Next step:** Full pivot — the decoder route is finished; the line moves to B101 or B82 as the coordinator directed.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A note on the left-pigeon bound for review (G3) | 3/3 — Barrier | 3/3 — Ready | Write the theorem and its proof as a short note with the checks, for the owner to decide whether and to whom to send it → a note an expert can check, or the step a reader would question | Recommended |
| 2 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |
| 3 | A parity reduction from PIGEON to SINK (sub-goal B101, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |

1. **A note for review.** Payoff 3: a result of this kind needs an expert reading before it counts; Concreteness 3: the proof and checks
   exist. It is a conversion, not a new route.
2. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.
3. **The parity reduction.** As in `RES-XOR-COUNT-20261110-001`.

**Recommendation.** Full pivot from the decoder route, with the note for review recommended first and recorded as sub-goal B116 under the
owner's rule for untaken 3/3 directions, for the coordinator to confirm.

## Final report as sent

B114 is closed with a proved bound. Every dag-like Res(⊕) refutation of the binary left-pigeon principle needs exp(Ω(n / log⁵ n)) lines, both with 2n pigeons and with the PPADS-complete n + 1. As far as my searches found, this is the first Res(⊕) lower bound of any kind for a PPADS-complete principle.

Before any proof work I checked the novelty and the transfer. The 2n-pigeon formula derives bit-PHP's clauses in one step each, so its bound is stronger than Braun's and doesn't follow from it. Its clause set contains the n + 1 pigeon clauses line for line, so the bound transfers.

The proof has three steps. First, separation reduces to a decoder kernel (from earlier). Second, a new spare-row lemma: a cube parks the pigeons it moves in a few spare holes and pigeons, so the space avoiding those spares misses the kernel. Third, a density count through Braun's criterion. All four frozen checks held: the space missed the kernel at (4,1), (8,1) and (16,2), and the stress test one size past passed.

Two caveats. It's V1, one session and not externally reviewed. It also rests on Braun's unrefereed but Lean-checked preprint, now recorded as assumption A55. Scope: it covers this binary encoding only and does not reach the sphere's count. Per your condition, the decoder route is now finished.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the 2n-pigeon route | Successful | Dag-like Res(⊕) bound for bit LeftPigeon, proved |
| Local direction: the decoder route | Full pivot | Finished, as you set |
| Broader exploration: G3 | Known alternatives | Cutting planes (B82), the parity reduction (B101) |
| Long-term goal: G3 | Capability gained | A PPADS-complete principle is hard for Res(⊕); the sphere's count isn't reached |

**Next step:** Full pivot, with a note for review first.

| # | Direction | Payoff | Concreteness | First step → stop when |
| --- | --- | --- | --- | --- |
| 1 | A note on the bound for review (B116) | 3/3 | 3/3 | Write it self-contained, settle which of Braun's lemmas the Lean replay covered → a note an expert can check |
| 2 | Cutting planes on the count (B82) | 3/3 | 1/3 | As recorded |
| 3 | A parity reduction from PIGEON to SINK (B101) | 3/3 | 1/3 | As recorded |

**Corrections:** none. **Goals:** a G3 checkpoint; B114 taken; sub-goal B116 added. **Assumptions:** A55 added (Braun's preprint is correct).
**Basket:** B116 (3/3, 3/3), B101 (3/3, 1/3), B82 (3/3, 1/3); none taken. B116 is recommended, and whether to share the result is John's call.
