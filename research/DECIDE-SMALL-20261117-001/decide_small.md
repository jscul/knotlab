# Does the toolkit decide every small-orbit pattern?

Epic `DECIDE-SMALL-20261117-001`. It takes direction #1 of `MODE-BOND-20261117-001` at the coordinator's go-ahead (2026-11-17 23:37
UTC), within John's request of 16:52 UTC to reopen the line. It serves G17, with G1, and ran on 2026-11-17 and 18. Code by the
thread. The canonical K1–K3 test is unchanged. **Referee pending.** Computed, with every test a proved theorem of an earlier study.

## The question

On KEEP-REACH's population, five proved tests decide whether the reach from level 3 stays bounded for every small-orbit pattern. Is
that a property of the tests, or of a small population built partly from four seeds?

## Answer

**On a fresh sample ten times larger, every pattern is decided.**
- **The sample.** 10,160 draws from KEEP-REACH's fair-coin sampler, with a new seed. The weighting:
  - s uniform in {1, 2, 3} automaton states, each with an output flip and two transitions, all uniform;
  - 1 to 4 placements, each a sorted triple of slots uniform among the 3(1 + s + s²).
- **What was kept.** 6,804 draws have orbits of at most four addresses and live at every depth.
- **Deduplicated before any test.** They are 627 distinct patterns (9.2%). 476 of them appear in neither KEEP-REACH's population nor
  the census.
- **The verdicts.** All 627 are decided:
  - 452 grow by forgetting (Theorem F);
  - 172 are bounded by a two-orbit bond (Theorem K);
  - 2 are bounded by orbit-and-block or stem bonds (Theorem K\*);
  - 1 grows by forgetting on the values states take (Theorem F′);
  - none needed the joined product test.

  There were no timeouts and nothing for the second tier.
- **The checks.** No contradiction in 62 full checks, where every test was run on every tenth pattern. No merge splits at depth 14.
- **Ground truth.** The census's certified search computed L₉(3, s), s = 1..4, on 50 decided patterns: the 3 decided by late tests,
  then the first in draw order. In 60 s per cell it decided 145 of the 200 cells, and every one fits its verdict's bound (0 misfits).
  The two-orbit and carrier upper bounds are tight in 29 of the cells they bound.

| Verdict (test) | All 627 patterns | 476 unseen before |
| --- | ---: | ---: |
| grows (T1, forgetting) | 452 | 323 |
| bounded (T2, two-orbit bond) | 172 | 151 |
| bounded (T4, block or stem bond) | 2 | 1 |
| grows (T3, forgetting on actual values) | 1 | 1 |
| grows (T5, joined product test) | 0 | 0 |
| undecided | 0 | 0 |

So on small orbits, under this weighting, the reach from level 3 is decided by a short list of proved tests. It is bounded when two
bounded pieces at the ends hold a bond at every distance, and it grows when some part of what joins the ends forgets. The rare cases
are rare indeed: 3 of 627 needed more than forgetting or a two-orbit bond. This is evidence, not a proof that the toolkit is
complete. A pattern none of the tests decides would be a new way for the top to be held or to forget, and none appeared.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | All 627 distinct small-orbit patterns of a fresh 10,160-draw sample are decided by the five tests | computed (each test proved; the order and caps are the design's) |
| 2 | 476 of the 627 are new to the program; their verdicts split 323 / 151 / 1 / 1 / 0 | computed |
| 3 | No contradiction between tests (62 full checks); dedup stable from depth 12 to 14 | computed |
| 4 | Ground truth: 145 certified readings of L₉ on 50 patterns all fit their verdicts (0 misfits; upper bounds tight in 29 cells) | computed, certified (LRAT) |

## Predictions

Frozen in [predictions.md](predictions.md), commit dcc5a3319, before any draw of the new seed.
- **P1 holds.** Every distinct pattern is decided, by the first tier alone. The prediction gave 40%, the advisor 30–35%.
- **P2 fails, narrowly.** Distinct patterns are 9.2% of the kept descriptions, against 10–30% predicted (the advisor: 10–25%). The
  fraction keeps falling as the sample grows, as the advisor said.
- **P3 holds.** T1 decides 72% (50–80% predicted).
- **P4 holds.** The late tests decide 3 of 627, 0.5% (at most 2% predicted).
- **P5 holds.** No contradiction.
- **P6 holds.** No merge splits.
- **P7 holds.** All 145 decided readings fit (55 cells undecided within 60 s, not counted).

## Lessons

- Most of the program's earlier counts of "patterns" were of descriptions. Ten thousand draws give only 627 distinct patterns, and
  the dedup pays for itself many times over.
- When a short list of tests decides a large fresh sample, the open question moves to a proof of completeness. More sampling adds
  little.

## Advisor

Used once, on the design before the freeze (`advisor/design_answer.md`):
- run every draw rather than stop at the first undecided pattern;
- the full-test consistency subsample, the second tier, the ground-truth check and the depth-14 recheck;
- revised predictions for P1, P2 and P3, which the data bear out better than the first draft's (P2 failed both).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt (completeness on a fresh sample) | **Status:** Successful | All 627 decided; no new phenomenon |
| Local direction (small orbits) | Known alternatives | Sampling is exhausted as evidence; what is left is a proof of completeness, or rates |
| Broader exploration (G17's addressed line) | Continue | Orbits that grow past four addresses (B188), where none of the tools applies |
| Long-term goal (G17, with G1) | Capability gained | Bounded or growing reach is now decided for every small-orbit pattern seen, 1,000 and more |

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A83 used; none added.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A completeness proof for small orbits | 3/3 — Major | 2/3 — Testable | Show that for small orbits, either some composite chain to every far level forgets on actual values (growth), or a bounded two-end piece holds a bond at every distance: a dichotomy on the finite automaton of pair states (Theorem D's pumping applied to the carrier family) → a decision procedure, or a pattern the dichotomy misses | Selected · awaiting go-ahead |
| 2 | Orbits that grow past four addresses (B188) | 2/3 — Substantial | 1/3 — Stated | As filed: 3,356 of the 10,160 draws (33%) have growing orbits, where only descents give upper bounds | Alternative · deferred |
| 3 | Exact growth rates (B186) | 2/3 — Substantial | 2/3 — Testable | As filed | Alternative · deferred |

The reasons for each rating:
1. **A completeness proof.** Payoff 3: a decision procedure for bounded reach on small orbits would close the line's main question,
   with the two-end form of C* as a theorem for them. Concreteness 2: every ingredient exists, namely finite pair states, Theorem
   D's pumping, the carriers and the forgetting tests, and over 1,000 decided patterns guide it. The step that may fail is showing that a
   bounded bond can always be read in a bounded two-end piece.
2. **Growing orbits.** As filed. A third of the draws are there.
3. **Rates.** As filed.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.

**Route assessed, then parked (2026-11-18, after the coordinator's go-ahead).** With the advisor
(`advisor/completeness_route_question.md`, `advisor/completeness_route_answer.md`), #1 has a route. A subtree's summary is the family
of realised subsets of its interface states, tracked with and without its level-k and far members. It composes at blocks and branch
points, and it handles any number of crossings, so "L ≤ c" is decidable for each c.
- **Where totality stalls.** Deciding boundedness in s is a limitedness question for a weighted tree automaton. It is decidable by
  min-plus matrix powers only when the far members hang below one long spine. The normal form does not give that, since members near
  the bottom band ride on further spines synchronised with s.
- **What totality would need.** Either the theory of regular cost functions (Colcombet–Löding), through evidence admission, or a long
  Hashiguchi-style proof.
- **The decision.** #1 stays open in the basket, and the study moved to #2 (growing orbits, B188), as the go-ahead allowed for a
  route that is not clear.

## Hand-off to the referee

**Files.**
- This folder: the note, the design, the predictions, and the advisor's Q/A.
- `decide.py` and its outputs: `draws.jsonl`, `patterns.jsonl`, `undecided.json` and `summary.json`.
- `overlap.json`, and `ground_truth.py` with `ground_truth.json`.
- The ground truth's 22,183 LRAT certificates, packed and verified: `artifacts/DECIDE-SMALL-20261117-001/certificates/`.

**Least sure.**
- (a) The test order with early exit. Only one test decides a pattern, except in the full-check subsample.
- (b) T4's combination of carriers over tiers, copied from CARRIER's check.
- (c) The dedup by clause set at depth 12. It is rechecked at 14 for every merge, but not proved.
