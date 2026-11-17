# Can the top tie itself to the frozen strand, or do the 13 grow?

Epic `MODE-BOND-20261117-001`. It takes direction #1 of `TWO-ENDS-20261117-001` at the coordinator's go-ahead (2026-11-17 22:40
UTC), within John's request of 16:52 UTC to reopen the line. It serves G17, with G1, and ran on 2026-11-17. Proof note:
[proof.md](../../proofs/MODE-BOND-20261117-001A/MODE-BOND-20261117-001A-P001_components/proof.md). Code by the thread. The canonical
K1–K3 test is unchanged. **Referee pending.** It uses Theorem G of `TWO-ENDS-20261117-001`, which that study's referee confirmed as
written, and nothing that rests on Theorem N.

## The question

The 13 mutants of 8db5da810c00 that pass every carrier found are 5 distinct patterns. TWO-ENDS found that one composite blocks the
product test for them: along a self-similar orbit type, an all-equal orbit stays all equal and a split orbit below forces a split
one above. A bounded bond would have to tie the top level to that link through members near the top. Can it?

## Answer

**No. The 13 grow linearly, proved:** L_N(3, s) ≥ (⌊(s − 1)/5⌋ + 3)/2 at every depth, for all 5 patterns.

The reason is simpler than the search that was planned:
- **No knot joins the link to the top.** In the blocks of the self-similar type and of its two parent types, every knot lies in the
  orbit and its first child. The self-similar orbit is the second child, joined to its parent by no knot.
- **So the link lives in separate components.** Every self-similar subtree is a separate component, which never reaches level 3. At
  depth 11, none of the 3,512 addresses of self-similar orbits shares a component with level 3.
- **A bond lies in one component (Lemma J).** So no bond with a member at level 3 can use the link.
- **On the top's own component the product test passes.** Every composite of 5 steps along joined children is a product, and
  Theorem G, applied to that component, gives linear growth.

In the program's words: the strand that never forgets is a separate strand. The top's own strands all forget within five levels,
so whatever holds the top to a far level must keep adding members as the distance grows.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Lemma J: a bond lies in one component | proved |
| 2 | Theorem G on the component of level k: products along joined children force linear growth | proved (Theorem G, refereed, with a joined-path lemma) |
| 3 | The 5 patterns (13 descriptions): self-similar subtrees unjoined; on the top's component ℓ₀ = 5; L ≥ (⌊(s − 1)/5⌋ + 3)/2 | proved with finite checks (SAT gate at depth 11) |
| 4 | The joined product test agrees with forgetting on all 786 census descriptions (181 patterns), and passes exactly the 13 of the 39 | computed |
| 5 | All 39 third-class descriptions (16 patterns), and so all 2,380 fresh and mutated small-orbit descriptions (583 patterns), are decided | follows (with KEEP-REACH and CARRIER) |
| 6 | In every bounded one, the reach is held at two ends (two-orbit, block or stem bonds), so the bottom band is never needed here | follows |

**The whole small-orbit population of KEEP-REACH, decided.**

| Descriptions (patterns) | Verdict | By |
| --- | --- | --- |
| 1,081 (244) | grow | Theorem F (forgetting) |
| 1,260 | bounded | Theorem K (two-orbit bonds) |
| 14 (6) | grow | Theorem F′ (forgetting on actual values) |
| 12 (5) | bounded | Theorem K\* (orbit-and-block and stem bonds) |
| 13 (5) | grow | Theorem G on the top's component (this study) |

The 1,260 bounded descriptions with a two-orbit bond are 323 patterns, if every group of identical descriptions carries one verdict,
as the referee found for the census. That is the 583 less the 244 and the 16.

## Predictions

Frozen in [predictions.md](predictions.md), commit 7451de98b, before any Part A computation.
- **P1 holds.** No gadget at a level-3 type for any of the 5 patterns.
- **P2 holds so far.** The test finds gadgets for 3 of the 5 bounded controls: 70,260 for bace53f8f952-58, 904 for -111 and 62 for
  -147. The two ca1efb37ad88 controls were still running at the close (LONG_RUNNING `MODE-BOND-A1`). A separate check is complete:
  the joined product test fails for all 12 bounded descriptions, as it must.
- **P3 holds, trivially.** No crossing of the link can meet level 3, so paired crossings add nothing.
- **P4 does not apply.** No gadget appeared.

The contract planned a decorated search. Reading the blocks made it unnecessary. The decorated closure was still run as frozen. It
agrees: it finds pairs only at the self-similar type, and every entry block is a product with its self-similar child for all 426 and
347 sibling restrictions.

## Lessons

- Before reading a composite as a carrier, check that it shares a component with the end in question. The link that blocked the
  product test, and KEEP-REACH's deep pair projections that never become products, sit in components that never meet the top.
- Counting distinct patterns and reading the blocks themselves are cheaper than any search, and should come first.

## Advisor

Used once, on the design before the freeze (`advisor/design_answer.md`). It proposed the decorated saturation (run, and in agreement),
flagged the third incompatibility type and the off-line members (both in the closure), and expected no gadget at 70 to 75%. It did
not point to the disconnection, nor did the two referees or the earlier studies.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt (the 13) | **Status:** Successful | Linear growth proved for all 5 patterns |
| Local direction (small-orbit addressed patterns) | Known alternatives | The KEEP-REACH population is fully decided; what is left is completeness and rates |
| Broader exploration (G17's addressed line) | Continue | Does the same toolkit decide every small-orbit description? |
| Long-term goal (G17, with G1) | Capability gained | Bounded or growing reach is now decided for every small-orbit description seen |

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A83 used; none added.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Is the toolkit complete for small orbits? | 2/3 — Substantial | 3/3 — Ready | Draw a fresh sample of small-orbit descriptions, about ten times KEEP-REACH's, deduplicated to patterns. Run the five tests: forgetting, two-orbit bonds, block and stem bonds, forgetting on actual values, and the joined product test. Stop at the first pattern none decides, which is a new phenomenon, or when the sample is exhausted, which supports a conjecture that the toolkit decides small orbits | Selected · awaiting go-ahead |
| 2 | Two ends or three, in general | 2/3 — Substantial | 2/3 — Testable | Look for a pattern whose bounded reach needs the bottom band, beyond the small-orbit population where none does | Alternative · deferred |
| 3 | Exact rates of growth (B186) | 2/3 — Substantial | 2/3 — Testable | The 13 read about one member per two levels, while the proof gives one per ten; least-mark costs would give the exact rate | Alternative · deferred |

The reasons for each rating:
1. **Completeness.** Payoff 2: a decision procedure for bounded reach on small orbits would close the line's main question. A
   counterexample would show a new way for the top to be held, or to forget. Concreteness 3: the five tests exist, are fast, and are
   gated.
2. **Two ends or three.** Payoff 2: it decides C* as first stated. Concreteness 2: it needs a population where the bottom band
   could matter.
3. **Rates.** As filed.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.

## Hand-off to the referee

**Files.**
- This folder: the note, design, predictions and advisor Q/A; `decorated.py`, `run_decorated.py`, `decorated.json`; `growth13.py`,
  `growth13.json`; `joined_census.py`, `joined_census.json`; `gate_growth.py`, `gate_growth.json`; `gate_decorated.py` (written,
  not run: the result does not rest on the decorated closure); `mode_bond.py` (the pruned search of the first draft, not run).
- The proof family `proofs/MODE-BOND-20261117-001A/`: `proof.md`, `check.py` and `result.json`.

**Least sure.**
- (a) The joined-path lemma in "Theorem G on a component": every link of the skeleton below level k is joined.
- (b) `growth13.py`'s joined automaton, a variant of `composite.py` restricted to joined children.
- (c) That Theorem G's window argument needs nothing from unjoined children. They are quantified with F holding every assignment.
