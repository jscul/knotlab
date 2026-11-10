# Hole-row separation for bit LeftPigeon

Epic `HOLE-SEP-20261110-001` (program complexity), 2026-11-10.

## The question

- **Where it comes from.** `SEP-LEFT-20261110-001` reduced a dag-like Res(⊕) lower bound for the binary left-pigeon principle LP_n, a
  PPADS-complete principle, to one statement: row-linear separation over its hole rows (sub-goal B103). The coordinator confirmed B103
  on 2026-11-10 at max effort, asking for the exact statement and a stop rule first.
- **Frozen first.** `separation_statement.md` beside this note (0596397e3): the reduction (R), the kernel bound (K), predictions P1 and
  P2, and stop rules (a) a theorem, (b) the killed combination, (c) the failing step.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Separation is a static kernel question.** If 2lB − 1 ≤ n, every row-linear polynomial of LP_n derived in PC degree B lies in the kernel K_k of the reduced decoder (pigeon bits to row sums, hole bits to weighted hole sums Σ_y y_j X_y,h) modulo Braun's unary degree-k ideal. So any subspace of L_k missing K_k is separated. | proved (from Braun's lemmas) | A |
| 2 | **The kernel starts with the inverse-counting identities.** κ_{a,j} = Σ_h a(h)·g_h,j + Σ_x x_j·a(f_x), for a = 1 or a = h_t: "summing over holes equals summing over pigeons", true for an inverse map though not a consequence of LP_n. They lie in K_1 for every n, and span it at n = 4, 8, 16 and 32. | proved; computed (pre-registered, P1) | A, B |
| 3 | **The kernel is large at small sizes, and falls.** At degree 2 the kernel is 73%, 49% and 32% of L_2 at n = 4, 8, 16 (and 19% at n = 32 in the stress test, as predicted), tracking (l + 1)² k / v (the share of κ's times L_{k−1}); P2 (below 1% at n = 16) is refuted, and the frozen rule (b) stops the route. | computed (pre-registered) | B |

## Answer

Not proved. The route reduces hole-row separation to the size of one kernel, and that kernel is not zero: it contains every
inverse-counting identity and its products, a share of about (l + 1)² k / v of the row-linear space. That stops this epic by its frozen
rule. But the rule's reading, that a kernel of that size closes the route, was wrong: a complement of the kernel loses only the factor
1 − fraction in the lower bound, and the fit gives a fraction near 1/(48 l) at the degree the bound needs. The question is now sharp:
does the kernel fraction stay bounded away from 1 at k ≈ n/(24 l²)?

## What a bound for bit LeftPigeon would mean for the sphere's count

Nothing directly. The count's own Res(⊕) route is closed by its polynomial-calculus degree O(√n) (`RES-XOR-COUNT-20261110-001A`,
Lemma 1), and LeftPigeon reaches the count only through `COUNT-SYSTEMS-20261110-001A`'s decision-tree reductions, which Res(⊕) is not
closed under. A bound for LP_n would be a bound for the class the count belongs to, PPADS, not for the count.

## Reading

**Interpretation, not a theorem.**
- **The left inverse's own identity is what the route cannot see.** The decoder empties every hole that no pigeon names, and with empty
  holes "a hole names its pigeon" becomes "summing over holes is summing over pigeons". The left-pigeon principle does not imply that
  (its empty holes may name anyone), and the small instances confirm it is never derived, but every argument that passes through the
  pigeonhole principle's unary form inherits it.

## Lag cutoffs and census-only claims

- **No lag cutoff;** not a dynamics epic.
- **Census-only.** Conclusions 2 and 3 at n ≤ 16 (P1 also at n = 32) are exact readings; the kernel bound for all n is not proved. The
  family named under rule (b) was found after the run and is partly identified (`interpretation.md` of ticket B).

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| P1, K_1 spanned by the identities (2) | n = 32 (read to 16) | pass: dim K_1 = 36 |
| The fit (l + 1)² k / v (3) | n = 32, k = 2, predicted before the run in [0.15, 0.21] | pass: 0.195 (12,287 of 63,094), against 0.202 |

The script is `stress_test.py` beside this note, its output `stress_test.json`, registered with its prediction before launch
(9b468ca80) as HOLE-SEP-S1; it ran in about 7 minutes.

## Literature and provenance

- **Sources.** Braun, arXiv 2609.23015 (his §3 moments and stability, §4 decoder transfer and row-linear separation, §9 criterion);
  `SEP-LEFT-20261110-001A`; for the field's frontier, Efremenko, Garlík and Itsykson (regular Res(⊕), *SIAM J. Comput.* 2025),
  Byramji and Impagliazzo (weak bit PHP, arXiv 2511.20023), Efremenko and Itsykson (ECCC TR25-039, TR25-188), Bhattacharya and
  Chattopadhyay (arXiv 2507.23008), Alekseev and Itsykson (ECCC TR24-128).
- **Searched and not found.** Any Res(⊕) lower bound, regular, depth-restricted or dag-like, for a PPADS-complete principle, the
  left-pigeon principle, injective pigeonhole principles or sink-of-line.
- **Classification.** Conclusion 1 is new as far as found and elementary given Braun's lemmas; conclusion 2's identities are new as far
  as found; no lower bound is claimed, so the strong novelty claim, a first Res(⊕) bound for a PPADS-complete principle, is not made.

## Workspace assumptions

- **Relied on.** None of the register's entries.
- **Added.** None.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A), one pre-registered computation (B), the post-hoc naming of the killed family, one stress test, one
  correction.
- **Administrative.** The frozen statement, this note and the closure.

## Pending the owner

- None new.
- Carried: as in `SEP-LEFT-20261110-001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — hole-row separation for bit LeftPigeon | **Status:** Obstructed (by its frozen rule) | The kernel is 32% at n = 16, k = 2; the rule's reading of that was wrong |
| Local direction — the decoder's kernel | Continue | The corrected question is sharp and the readings fit a small fraction at the needed degree |
| Broader exploration — G3 | Known alternatives | Cutting planes (B82), the parity reduction (B101) |
| Long-term goal — G3 Hardness at three places | Capability gained | Separation for the left-pigeon principle is now one counting question about a kernel |

**Corrections:** one, the frozen rule's reading (Not a block; `docs/CORRECTIONS.md`). **Goals:** a G3 checkpoint (capability gained);
B103 taken; one sub-goal added. **Assumptions:** none.

- **What the attempt leaves open.** A bound on dim K_k at k ≈ n/(24 l²); the unidentified part of K_2.

**Next step:** Continue — bound the decoder's kernel at the degree the bound needs.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The decoder's kernel is a vanishing fraction (G3) | 3/3 — Barrier | 2/3 — Testable | Freeze the target, dim K_k ≤ (1 − e^{−k²/(6n)})·dim L_k at k ≈ n/(24 l²); prove K_k is the row-linear part of the ideal generated by the κ's (identify the rest of K_2 first, then a dimension count), checked at k = 3 and 4 on n = 8, 16 → the theorem, or a kernel family of share near 1 | Recommended |
| 2 | Cutting planes on the count (sub-goal B82, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |
| 3 | A parity reduction from PIGEON to SINK (sub-goal B101, G3) | 3/3 — Barrier | 1/3 — Stated | As recorded | Alternative · deferred |

1. **The kernel bound.** Payoff 3: with Theorem (R) and `SEP-LEFT-20261110-001A`'s Theorem 2 it gives a dag-like Res(⊕) lower bound
   for a PPADS-complete principle. Concreteness 2: an exact linear-algebra statement with a conjectured description and small-size
   evidence.
2. **Cutting planes.** As in `COUNT-SYSTEMS-20261110-001`.
3. **The parity reduction.** As in `RES-XOR-COUNT-20261110-001`.

**Recommendation.** Continue with direction 1, recorded as a sub-goal under the owner's rule for untaken 3/3 directions, for the
coordinator to confirm.
