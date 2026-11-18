# One distance for parity and not-all-equal knots

Epic `CUMULANT-DIST-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes sub-goal B200 (one
distance read from the states that reads parity and not-all-equal bases alike) in place of `ROW-ARRANGE-20261118-001`'s direction 3,
as the go-ahead allowed once a concrete handle appeared. Goals G1 and G16; tests A97. **Referee pending.** **Corrected on 18 November
2026 (before the referee, see Correction): "steps apart on every knot tree" is false for large not-all-equal trees with a hub.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `6d9f3ed9b` at 07:23:35 UTC; the run went from
  07:23:47 to about 07:25 UTC.
- Proofs: [proof.md](../../proofs/CUMULANT-DIST-20261118-001A/CUMULANT-DIST-20261118-001A-P001_delta/proof.md).
- Code: [cumlib.py, run.py, score.py, checks.py](../../experiments/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta/);
  post hoc `posthoc.py`.
- Results: [results.json](../../artifacts/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta/results.json), the
  parts, and [posthoc.json](../../artifacts/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta/posthoc.json).

## The answer

**The distance.** For two distinctions x and y, look at every set of distinctions holding both, and ask how strongly the set is
bound together beyond what its parts explain: its joint cumulant κ_S, the literature's Ursell function. Charge one step for each
distinction the set needs beyond the two, and −log₃ |κ_S| for how weak the binding is:

δ(x, y) = min over S ∋ x, y of (|S| − 2) + max(0, −log₃ |κ_S|).

It is read from the allowed states alone, and it ignores both the distinctions' names and which of their two values is called 1.

**In the owner's terms.**
- **One knot is one step, under either law.** A parity knot binds its three distinctions with nothing visible in pairs; a
  not-all-equal knot binds them through its pairs. Both come out at distance 1 between any two of their distinctions.
- **On small trees of knots the distance is steps apart, whichever law each knot has; on every parity tree it is (proved).**
  Computed for not-all-equal and mixed trees on all 19,730 pairs of 380 trees (every tree to five knots under every assignment of
  the two laws, and to six knots under one law). *Corrected the same day:* it fails on large not-all-equal trees with a hub. Hang
  32 knots on x and take one distinction from each together with x and y: their joint cumulant is the 34th cumulant of a fair coin
  times (−1/3)^(32 + k), and the coin's cumulants grow factorially, so with k ≥ 33 steps the distance falls below steps apart
  (proved; 65 knots; asymptotically it is O(k/log k)). See Correction. Bond distance gives parity trees this and not-all-equal ones nothing; the disagreement count gives
  not-all-equal trees this and parity ones nothing; this one distance gives both, and their mixtures.
- **On parity bases it is bond distance minus one** (proved; checked on 7,450 pairs of 300 random bases), so it keeps everything
  bond distance read there, the cube of three orders grown from one knot included.
- **On not-all-equal bases it is the count's τ where pairs carry the binding**: exactly so on a chain grid (every pair of a 4 × 4
  patch), and below τ only where a pair's correlation nearly cancels (three pairs of a small weave patch, where a four-set binds
  them more strongly than the pair does).
- **Where the laws part: cycles.** On rings of knots, not-all-equal distances spread above and below steps apart, while parity
  rings of five or more knots keep steps apart exactly, and only rings of three and four are shortened by the ring's own circuit.
- **What it cannot do.** A split grid's ruler (twice the L1 distance) depends on which value is called 1: up to flipping values,
  a split line is a ring, its two ends as near as neighbours (proved), and this distance reads the line of eight as a ring of eight.
  So one distance that ignores values reads parity and not-all-equal knots alike, but not the orders a betweenness growth builds,
  which need the values. In two orders the obstruction is partial: pair readings cannot tell a corner's neighbour from the far
  corner, but no flip of values carries one to the other, so the full structure can.

| Base | δ | Bond distance | Count (τ) |
| --- | --- | --- | --- |
| One knot, either law | 1 on every pair | 2 (one knot), offset 1 | parity: blank; not-all-equal: 1 |
| Knot trees, any mixture of laws | steps apart (proved for parity, computed for the rest) | steps apart + 1 for parity, 2 on not-all-equal pairs | steps apart on not-all-equal trees, blank on parity |
| Parity bases | least circuit − 2 = bond distance − 1 (proved) | the reading | blank |
| Chain grid (4 × 4 patch) | τ on every pair (computed) | 2 on co-knotted pairs, no ruler | τ |
| Weave patch, radius 2 | τ except 3 pairs where τ is 4 to 4.9 and δ 3.1 to 3.2 | steps apart + 1 | τ |
| Parity rings | steps apart from five knots; shortened at three, four | the ring's circuit | blank |
| Not-all-equal rings | τ, above and below steps apart | — | τ |
| Split line of eight | the ring of eight (0.26, 0.63, 1.26, 3.26) | 2 | folded |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 7 gates (recursion, pruning, invariances, circuits, one knot, a moment mutant) | held | all pass |
| P1 | parity bases: δ = least circuit − 2 | held | 0 of 7,450 pairs differ (300 bases) |
| P2 | knot trees, every law assignment to 5 knots, pure to 6: δ = steps apart | held | 0 of 19,730 pairs differ (380 bases) |
| P3 | mixed chains: κ({ends} ∪ parity pendants) = (−1/3)^a | held | 62 of 62 |
| P4 | separated four-sets on not-all-equal chains: κ₄ = −2·3^(−(d₁ + d₂)) | **failed** | the frozen code put the pairs on each side in the exponent; the advisor's formula uses the cross pairs and holds on all 491 (post hoc), as does the exact identity κ₄ = −m_xy m_uv − m_xv m_uy |
| P5 | rings: parity shortens some pair; not-all-equal δ = τ | **failed** | not-all-equal held; parity rings of five and six knots keep steps apart exactly (the ring's circuit is no shorter there) |
| P6 | chain grid 4 × 4: δ = τ; bubble ≤ 4.5 | held | 120 of 120 pairs; bubble 2.99 |
| P7 | weave patch: δ = τ on every pair | **failed** | 3 of 171 pairs (two steps apart) have δ = 3.10 to 3.18 below τ = 3.99 to 4.88, via four-sets |
| P8 | split line of eight: switching rotation, invariant \|κ\|, largest δ = 2 + log₃ 2 | **failed** | rotation and invariance held; the largest δ is 2 + log₃ 4 = 3.26 (κ₄ = −1/4 at the antipode), not 2.63 |
| P9 | split grids: a switching equivalence takes a corner's neighbour to the far corner | **failed** | none on 3 × 3, 3 × 4 or 4 × 4 (|C| and the triangle products agree, the full structure does not) |

4 of 9 held. The four that hold are the B200 content: one distance, parity and not-all-equal alike, on trees and on parity bases,
and no shortcut on the chain grid. Of the five that failed, one is a coding error in the test (P4, which holds as stated), and
four are informative: parity rings of five or more do not part from steps apart (P5), the weave patch's near-cancelling pairs are
bound more strongly in fours (P7), the advisor's cap on the split line was too low (P8), and in two orders switching does not hide
the far corner (P9).

## What it means for A97

The owner's premise is that distance is the only form of information. Until now each law needed its own distance: bond distance
for parity, the disagreement count for not-all-equal. One distance read from the states, built from how strongly sets of
distinctions are bound beyond their parts, reads both alike on small trees of knots and on every parity tree, and reduces to each
  on its own law's bases; on large not-all-equal trees with a hub it falls below steps apart (see Correction). So
for knots the premise can be met with one distance. What it does not read is the value convention: the orders a betweenness growth
builds, and the split grid's ruler, need to know which value is called 1, and a distance that ignores values sees a split line as a
ring. A97 stays under challenge, with this study added; the value convention is recorded as a new assumption (A103).

## Known results, and what this adds

Known, cited once: Ursell functions and cumulant inequalities (Lebowitz; Aizenman's tree bound); connected information and
irreducible correlations (Schneidman, Still, Berry and Bialek 2003; Linden, Popescu and Wootters), whose canonical example is
parity; tree metrics from correlations (log-det and information distances: Steel; Choi, Tan, Anandkumar and Willsky; Chow and
Liu); matroid circuits and connectivity (Tutte); switching and two-graphs (Seidel; Zaslavsky; Toulouse); circular split systems
(Bandelt and Dress). What this adds: the single functional with the clamp, applied to the program's knots; the statements that it is
bond distance minus one on parity bases and steps apart on knot trees under any mixture of laws; and the switching reading of
split lines as rings. Each is short once seen; a targeted literature check before claiming novelty is left to the referee.

## Limitations

- Trees are computed, not proved, beyond parity (and beyond four-sets for not-all-equal); mixed trees to five knots, pure to six.
- The chain grid and the weave are finite patches (4 × 4; radius 2), so boundaries shape the correlations; the weave's three
  shortcut pairs sit at the patch edge.
- The search is exponential in the set size; it is exact here only because the bases are small or the bound stops it.
- δ is not shown to satisfy the triangle inequality in general.

## Reproduce

```sh
d=experiments/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta
.venv/bin/python -B $d/checks.py
for p in trees mixed_identity nae_separated linear rings chain_patch bubble weave_patch split_line split_grid; do .venv/bin/python -B $d/run.py --part $p; done
.venv/bin/python -B $d/run.py --score
.venv/bin/python -B $d/posthoc.py     # labelled post hoc
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` was asked once before the freeze ([question](advisor/question_1.md),
[answer](advisor/answer_1_fable.md); `modelUsage` names claude-fable-5-2). It recommended this study over the ladder, and gave D1 to
D5 (proved here), the clamp counterexample, and P1 to P8. It was wrong on the split line's cap (P8: 2.63 against 3.26) and did not
know P9. Not consulted after the read-out.

## Correction (18 November 2026, before the referee)

The study's next step was to prove that δ is steps apart on every knot tree. Asked for the lower bound, the advisor
(claude-fable-5-2) found that it is false, and I checked it:
- **Lemma (proved).** If σ is a uniform ±1 and u₁, …, u_n are independent of it and of each other with means μ_i, then
  κ(σu₁, …, σu_n) = κ_n(σ) ∏ μ_i: the joint moments are those of μ_iσ. The cumulants of a fair coin, |κ_{2j}(σ)| = 1, 2, 16, 272,
  7936, …, are the tangent numbers and grow factorially.
- **Counterexample (proved).** A path of k not-all-equal knots from x to y, and N more not-all-equal knots hung on x, with b_i one of
  the hung knot i's other distinctions. Rooted at x, every spin of S = {x, y, b₁, …, b_N} is σ = s_x times independent factors of
  mean −1/3 (one per knot crossed), so κ_S = κ_{N+2}(σ)(−1/3)^{N+k}. Checked on the bases at (N, k) = (2, 1), (4, 1) and (2, 2).
  Exactly, log₃|κ₃₄(σ)| = 64.075 > 64, so with N = 32 and k ≥ 33 (a tree of 65 knots) δ(x, y) ≤ k − 0.075; with N = 34, δ ≤ k − 1.70.
  Choosing N with log₃ |κ_{N+2}| ≥ N + k gives δ ≤ N, and log₃ |κ_{N+2}| grows like N log N, so δ = O(k / log k) on such trees.
- **What stands.** δ = bond distance − 1 on every parity base and so steps apart on every parity tree (proved); a parity path knot
  whose branch misses S forces κ_S = 0; sets of two and three never shortcut; separated four-sets never shortcut; every tree to five
  knots under every law assignment and to six under one law (computed). The hub needs at least 32 knots on one distinction (or the
  advisor's compact variant, 48 knots), so the bases of the program's other studies, with at most six knots per distinction, are not
  reached by this mechanism; whether bounded-degree trees can shortcut is open.
- **Verdict.** A **Block** on the reading "δ = steps apart on every knot tree under either law": the unification of the two laws by
  this distance holds on small trees and on every parity tree, not on all trees. Logged in `docs/CORRECTIONS.md` and knotlab's
  `HISTORY.md`. A repair is to read cumulants that factor along the tree (the literature's tree cumulants, Zwiernik and Smith 2012),
  or to admit at most one distinction per branch; `TREE-STEPS-20261118-001` takes this up.

## Referee

Pending. To be run by the coordinator's background referee thread.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: one distance for parity and not-all-equal knots (B200) | **Status:** Partially successful (referee pending) | One distance reads both laws alike on knot trees and reduces to bond distance and to τ on each law's bases; it cannot read value-dependent orders (split grids); 4 of 9 held |
| Local direction: the cumulant distance | Promising | Proofs for trees of both laws, the triangle inequality and larger bases are open |
| Broader exploration: correlation and information distances | Known alternatives | Ursell functions, tree metrics and switching are classical; the functional and its readings are the program's |
| Long-term goal: G1 and G16 | G1 capability gained (narrowed: small trees and parity trees); G16 capability gained | G1: one state-read distance gives steps apart on small knot trees and every parity tree, either law. G16: what the two laws share and where they part (cycles), read from states |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | *(Answered the same day: false in general, see Correction.)* Prove δ = steps apart on every knot tree, any mixture of laws (the lower bound beyond four-sets) | 2/3 | 2/3 | bound the cumulants of sets of six and eight on not-all-equal trees by the separation lemma → stop at a proof or a tree where a larger set wins | Alternative |
| 2 | The cumulant distance on the program's large bases: the cubic parity system grown from one knot and the endless weave (exact kernels), and mixed laws on the weave | 2/3 | 2/3 | δ on the weave from four-point dimer correlations → stop at its outline and growth | Alternative |
| 3 | What reads the value convention: a statistic of the states, invariant under renaming but not switching, that recovers the split grid's L1 and the orders, and why betweenness growth fixes it (A103's challenge) | 2/3 | 2/3 | the switching group of grown split bases → stop at the least added datum (the all-equal states) | Alternative |
| 4 | Two orders without values: which switching-invariant statistic tells a corner's neighbour from the far corner in a split grid (P9) | 1/3 | 3/3 | four-point cumulants at the corner → stop at the first that separates | Alternative |

**Corrections:** none at the close; on the same day one Block on the reading "steps apart on every knot tree" (see Correction).

**Goals:** G1 checkpoint (capability gained: one distance read from the states gives steps apart on every knot tree under either
law) and G16 checkpoint (capability gained: where parity and not-all-equal readings agree and part, read from the states); no goal
changed.

**Assumptions:** A97 gains this study; new A103 (a base's values are data, not labels: which value is called 1 is part of a base).

## The final report as sent (18 November 2026)

*As sent; its "every tree of knots" was corrected the same day (see Correction).*

**Outcome (sub-goal B200): one distance read from the states now reads parity and not-all-equal knots alike.** For two
distinctions, it charges one step for each extra distinction a set holding both needs, plus how weakly that set is bound beyond
what its parts explain (its joint cumulant). One knot comes out as one step under either law. On every tree of knots, whatever mix
of the two laws, it is steps apart: proved for parity, and computed on 19,730 pairs. On parity bases it is bond distance minus one
(proved). On a chain grid it is the count's τ. The laws part only on cycles. The limit: it ignores which value is called 1, and up
to flipping values a split line is a ring (proved). So the orders a betweenness growth builds still need the values, which I've
recorded as new assumption A103. 4 of 9 frozen predictions held. The misses: one was a coding slip in a test (the statement
holds), and four were informative surprises. The epic is closed with the referee pending.

The position table, the next-step line and the four directions as in Position above.

**Corrections:** none. **Goals:** G1 and G16 checkpoints (capability gained); no goal changed. **Assumptions:** new A103 (a base's
values are data); A97 gains this study.
