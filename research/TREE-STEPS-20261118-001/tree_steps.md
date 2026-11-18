# Where the cumulant distance is steps apart, and a repair

Epic `TREE-STEPS-20261118-001`, 18 November 2026, by Claude. It takes `CUMULANT-DIST-20261118-001`'s direction 1, prove that the
cumulant distance is steps apart on every knot tree, pivoted with the coordinator's approval once the advisor showed the statement
false (hubs). Goals G1 and G16; tests A97; sub-goal B200. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `0a8ea0e9f` at 07:44:47 UTC (it records the pivot);
  the run went from 07:44 to 07:45 UTC through the shared runner (`TREE-STEPS-B1`, 156 cases, none failed).
- Proofs: [proof.md](../../proofs/TREE-STEPS-20261118-001A/TREE-STEPS-20261118-001A-P001_hubs/proof.md).
- Code: [treelib.py, job.py, merge.py, checks.py](../../experiments/TREE-STEPS-20261118-001B/TREE-STEPS-20261118-001B-E001_trees/).
- Results: [results.json](../../artifacts/TREE-STEPS-20261118-001B/TREE-STEPS-20261118-001B-E001_trees/results.json).

## The answer

**In the owner's terms.**
- **Why the first distance fails on big trees.** It charges one step per extra distinction and rewards how strongly a set is
  bound beyond its parts. Distinctions that all hang on one hub move together, and the joint binding of many copies of one coin
  grows factorially, faster than the one step charged for each. With sixteen not-all-equal knots on one distinction (both other
  distinctions of each taken), the hub pays for itself, and a far distinction comes out nearer than its steps (proved; the
  advisor's counterexample). Below that size no single hub can do it: a distinction in at most fifteen knots is safe, and the
  program's bases have at most six.
- **The repair: count only sets that are bound and have no smaller bound set holding the pair.** That is the knot test's K2 ("forget
  any one and the rest is free") in cumulant form. A hub set always contains a smaller bound set holding the pair, so the repaired
  distance ignores hubs. It is the count's τ wherever the two distinctions correlate (proved), bond distance minus one on every
  parity base (proved), and steps apart on every not-all-equal tree, every parity tree, and every mixed tree whose path between the
  two has no parity knot (proved). The one case left, a mixed tree whose path holds a parity knot, is computed, not proved.
- **On every tree of six knots under every law assignment (1,216 bases, 94,848 pairs) and on 80 random trees of seven knots, both
  distances are steps apart on every pair, and agree** (computed; one size past the earlier range).

So the repaired distance keeps everything the first one read, parity and not-all-equal alike, and drops the factorial shortcut:
on knot trees it is one step per knot under either law (proved except one mixed case, computed there).

| Base | δ (first distance) | δ_K (irreducible sets) |
| --- | --- | --- |
| A correlated pair (C ≠ 0) | ≤ τ, and below it where a larger set binds more (weave patch) | τ exactly (proved) |
| Parity bases | bond distance − 1 (proved) | the same (proved) |
| Not-all-equal trees | steps apart to 7 knots (computed); below it with a hub of 32 copies (proved) | steps apart (proved) |
| Parity trees | steps apart (proved) | steps apart (proved) |
| Mixed trees, no parity knot on the path | steps apart to 7 knots (computed); a hub can break it | steps apart (proved) |
| Mixed trees, a parity knot on the path | steps apart to 7 knots (computed) | steps apart to 7 knots (computed); proof open |
| Hub trees (≥ 16 knots on one distinction) | below steps apart, O(k / log k) | steps apart (proved) |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 5 gates | held | all pass |
| P1 | every six-knot tree, every law assignment: δ = steps apart | held | 0 of 94,848 pairs differ (1,216 bases) |
| P2 | the same: δ_K = steps apart | held | 0 of 94,848 |
| P3 | 80 random seven-knot trees (≤ 3 knots per distinction): both = steps apart | held | 0 of 8,400 |
| P4 | δ = δ_K on every pair of P1 and P3 | held | no pair differs |

4 of 4 held.

## What it means for A97

Sub-goal B200 asked for one distance read from the states that reads parity and not-all-equal bases alike. The first attempt
(`CUMULANT-DIST-20261118-001`) did on small trees and failed on large ones through a factorial growth of cumulants. The repaired
distance, built on the knot test's own K2, keeps the unification and removes the failure: on every knot tree checked it is one step
per knot under either law, and on each law's own bases it is that law's established reading (τ, bond distance). The premise that
distance is the only form of information gains a single distance for both laws, read from the states. It still ignores which value
is called 1 (A103), so split grids remain a ring. A97 stays under challenge, with this study added.

## Known results, and what this adds

Known, cited once: the tangent numbers as the cumulants of a fair coin; Brillinger's law of total cumulance; tree cumulants
(Zwiernik and Smith 2012) as the literature's way to tame cumulant growth on trees; irreducible correlations (Schneidman, Still,
Berry and Bialek 2003); matroid connectivity. What this adds: the hub threshold for the program's knots (32 copies), and the
irreducible-set distance, which is the knot test's K2 in cumulant form, with its proofs (K1 to K4) and the computed checks.

## Limitations

- The mixed case with a parity knot on the path is computed (trees to seven knots), not proved; a sketch is in the proof file.
- Nested hubs (copies gathered through shared knots) are not covered by H2; δ might shortcut on bounded-degree trees through them.
  δ_K is immune to every set that contains a smaller binding set, nested or not.
- δ_K's search is exponential in the set size, as δ's.

## Reproduce

```sh
d=experiments/TREE-STEPS-20261118-001B/TREE-STEPS-20261118-001B-E001_trees
.venv/bin/python -B $d/checks.py
.venv/bin/python -B scripts/longrun.py launch $d/job.py --out runs/tree-steps --workers 8 --case-mem 1500M
.venv/bin/python -B $d/merge.py runs/tree-steps
```

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2), asked for the lower bound before any freeze. It found the counterexample (H1, H2 here), proved the
parity-path lemma and the cases of two and three distinctions, and suggested tree cumulants or restricted sets as repairs. The
irreducible-set repair and K1 to K4 are mine; the advisor was not asked about them.

## Referee

Pending. To be run by the coordinator's background referee thread.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: where δ is steps apart, and a repair | **Status:** Successful (referee pending) | Hub threshold proved; the irreducible distance proved hub-free, τ on correlated pairs, bond distance on parity bases, steps apart except one mixed case (computed); 4 of 4 held |
| Local direction: one distance for both laws (B200) | Promising | The repair keeps the unification on knot trees; cycles and value conventions remain |
| Broader exploration: cumulant distances | Known alternatives | Tree cumulants and irreducible correlations are classical; the K2 form is the program's |
| Long-term goal: G1 and G16 | G1 capability gained; G16 capability gained | G1: one state-read distance gives one step per knot under either law on trees. G16: the knot test's K2 as the rule that keeps a distance honest |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove δ_K = steps apart on mixed trees whose path has a parity knot (minimal covers have only trivial even subsets) | 2/3 | 2/3 | the GF(2) rank of a minimal cover's parity incidence → stop at a proof or a tree where δ_K < k | Alternative |
| 2 | δ_K on cycles and the program's large bases: the cubic parity system, the weave, mixed laws on the weave | 2/3 | 2/3 | δ_K on small rings and a weave patch (= τ there by K1), then the parity cube → stop at its growth | Alternative |
| 3 | Nested hubs: can δ shortcut on trees with at most six knots per distinction? | 1/3 | 2/3 | the cumulant of two-level hubs by the law of total cumulance → stop at a shortcut or a local balance bound | Alternative |

**Corrections:** none for this study (the correction it prompted, to `CUMULANT-DIST-20261118-001`, is logged there).

**Goals:** G1 checkpoint (capability gained: the irreducible-set distance gives one step per knot under either law on knot trees,
hub-free) and G16 checkpoint (capability gained: the knot test's K2 as the rule that keeps a cumulant distance from shortcutting);
no goal changed.

**Assumptions:** A97 gains this study; no new entry.

## The final report as sent (18 November 2026)

**Outcome:** the distance is mended, and the mend is the knot test's own rule. The first distance went wrong on big trees because a
hub of many distinctions bound to one gets an outsized binding: it needs 32 copies, i.e. 16 knots on one distinction (proved). The
fix is to count only sets that are bound and contain no smaller bound set holding the pair, which is K2 ("forget any one and the
rest is free") said of cumulants. The repaired distance ignores hubs (proved). It equals the count's τ wherever two distinctions
correlate and bond distance minus one on parity bases (proved). It is steps apart on every not-all-equal tree, every parity tree,
and every mixed tree whose path has no parity knot (proved). On every six-knot tree under every mix of laws, it is steps apart on
all 94,848 pairs (computed). One mixed case is still unproved. 4 of 4 frozen predictions held. The epic is closed with the referee
pending.

The position table, the next-step line and the three directions as in Position above.

**Corrections:** one Block, already reported, on CUMULANT-DIST's "every knot tree"; none for this study. **Goals:** G1 and G16
checkpoints (capability gained). **Assumptions:** A97 gains this study.
