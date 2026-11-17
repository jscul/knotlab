# Does a relation that never forgets keep the reach bounded?

Epic `KEEP-REACH-20261117-001`. It takes backlog B187 with B186, at John's go-ahead on 2026-11-17 16:52 UTC, relayed by the
coordinator: "let's see if we can uncover anything here". It serves G17, with G1, and ran on 2026-11-17. Proof note:
[proof.md](../../proofs/KEEP-REACH-20261117-001A/KEEP-REACH-20261117-001A-P001_two_orbit/proof.md). Code by the thread. The canonical
K1–K3 test is unchanged. **Refereed** (KEEP-REACH-R1, [report](referee-R1/report.md), commits 2275fed41 and e6e24ed66): **confirmed with
fixes**, no Block; Theorems K and F′ and Lemma E hold, and the three least-sure points check out; the summaries of what is shown about
the 25 are narrowed below. The referee did not recompute the 2,380 / 39 classification counts. *Narrowed after CARRIER's referee
(CARRIER-R1, 2026-11-17): those counts are of descriptions, and several descriptions give the same pattern. The 2,380 are 583
distinct patterns (244 that forget), the 39 are 16 (6, 5 and 5), the 25 are 10, and the census's 786 descriptions are 181 (139
that forget, 42 that never do).* **Stress test done** (depth 13, below).

## The question

On the census, where the maps' orbits stay small, forgetting decided bounded or growing reach in 782 of 786 descriptions. A pattern
that forgets loses, within r levels, what enters a stretch, and so grows. Four never forget, and nothing showed whether they were
bounded. Two questions follow:
- Do those four keep the top bound?
- Is "never forgets" the same as "bounded" in general? This is the knot intuition's question: does a strand pair whose relation never
  untangles hold the top to every depth?

## Answer

**On the census, yes: all four are bounded at every depth, so forgetting decides all 786.** In fresh patterns, the simple rule
fails. What keeps the top bound is narrower than "never forgets": a bond inside two orbits that survives from the top level at every
distance. Three new results say how far that holds.

- **Theorem K (proved).** The exact pair projection of two orbits, one at the top level and one s levels down, can hold a bond of any size
  meeting both. When it does at every s, that size bounds the reach at every depth. This settles the four: they are bounded at 4, 4,
  5 and 6.
- **Theorem F′ (proved).** It is enough to forget on the values states actually take, measured by actual pair projections from the top level
  down. Then the reach grows at every depth, as with Theorem F.
- **Lemma E (proved; the advisor's idea).** A dependence between two orbits gives a two-orbit bond when it is exposed: each side of
  some missing pair is the only state with its values on a free set of addresses.

The fresh sample and the mutations test the converse. Of 2,380 small-orbit descriptions that live at every depth (583 distinct
patterns), 1,081 forget and grow (244 patterns), and 1,260 never forget and hold a two-orbit bond at every distance, so they are
bounded. **39 descriptions (16 patterns) never forget on all values, yet lack a
two-orbit bond from the top at some distance.** They fall into three kinds:

| Kind | Descriptions (patterns) | What happens |
| --- | ---: | --- |
| Forget on actual values | 14 (6) | The "never forgets" came from values no state takes. Theorem F′ proves growth |
| Top pair projections become products | 13 (5) | From level 3 every two-orbit pair projection is independent from s = 5 on, while deeper pair projections never forget |
| Unexposed dependence | 12 (5) | From level 3 the pair projections stay dependent at every s, but every missing pair has an unexposed side, so no two-orbit bond forms |

The second kind gives a sharp contrast. Mutant 8db5da810c00-73 differs from its bounded parent by one slot of one placement. The
certified least bonds at depth 11 are:
- **parent:** 3, 4, 5, 5, 5, 5;
- **mutant:** 3, 4, 5, 5, 6, 6.

So the mutant has passed the parent's bound, although something in it never forgets, even on actual values. **Stress test
(2026-11-17, LONG_RUNNING `KEEP-REACH-A2`):** at depth 13, with 900 s per s, the mutant reads 3, 4, 5, 5, 6, 6 for s = 1..6, the same as
at depth 11 and now four levels above the bottom at s = 6; s = 7 and 8 are undecided. The depth-11 readings were rerun after the referee
with their certificates recorded (`exact_third_8db5da810c00-73_N11.json`, `exact_third_census_8db5da810c00_N11.json`); the depth-13
file was written by the first version of the wrapper and does not record them.

**So "never forgets on all assignments" does not keep the top bound** (the 14, proved). For the 25 that never forget even on actual
values, boundedness is open: the mutant has passed its parent's bound at depth 11 but is not shown unbounded, and the 12 with an unexposed dependence
are undecided past s = 2. *(Narrowed after the referee: it read "'never forgets' does not keep the top bound", and the two kinds were
said not to hold the top's bond.)* What the data supports throughout is
**Conjecture C′**: the reach from level k is bounded exactly when a two-orbit bond from level k survives at every distance. It is
proved in one direction (K). The other direction is proved where actual-value forgetting holds (F′), and it agrees with everything
computed. It stays open on the 25 descriptions (10 patterns) of the last two kinds.

In the program's words, a relation that never forgets is a tangle. What is proved to hold the top is narrower than a tangle
somewhere: a tangle that starts at the top and is exposed on both of its strands. Whether that is the only thing that holds it is
Conjecture C′.

| # | Conclusion | Kind |
| --- | --- | --- |
| 1 | Theorem K: two-orbit bonds of any size from exact pair projections bound the reach at every depth | proved (the refereed every-depth routine, a new property read) |
| 2 | The four census patterns are bounded at every depth (4, 4, 5, 6); forgetting decides all 786 | computed at every depth tier |
| 3 | Theorem F′: forgetting on actual pair projections from the top level forces growth | proved (the splicing lemma with a weaker hypothesis) |
| 4 | Lemma E: an exposed dependence gives a two-orbit bond | proved |
| 5 | Among 2,380 fresh and mutated descriptions (583 patterns), 39 (16 patterns) never forget on all values yet lack a two-orbit bond: 14, 13 and 12 of the three kinds (6, 5 and 5 patterns) | computed (not recomputed by the referee, who checked the 13 and 12 by SAT) |
| 6 | Mutant 8db5da810c00-73: L₁₁ = 3, 4, 5, 5, 6, 6 against its parent's 3, 4, 5, 5, 5, 5 | computed, certified (census search, N = 11); depth 13 pending |
| 7 | Conjecture C′, consistent with every pattern decided; open on 25 | stated |

## Predictions

Frozen in [predictions.md](predictions.md), committed in 54a0010bc at 17:02 UTC, before the runs. What had been seen was disclosed
there: the exploratory look at the four and the gates.
- **P1 holds.** All four have a two-orbit bond at every s and every depth tier, at 4, 4, 5 and 6.
- **P2 fails.** It predicted zero third-class patterns; there are 39 descriptions, 16 distinct patterns (2 in the fresh sample, 37
  among the mutations). The sample reached
  its power floor of 40 never-forgetting patterns after 1,016 draws.

## Lessons

- Forgetting must be read on the values states take. On all assignments, "never forgets" can come from values that never occur.
- A global property of a pattern, such as never forgetting somewhere, can say nothing about the top. Measure from where the reach
  starts.
- A dependence is not a bond. It can stay unexposed behind one side's own constraint, and exposure is what turns it into one.

## Advisor

Used once, on the design before the freeze (`advisor_design_answer.md`). It made five contributions:
- it showed with a three-variable example that Conjecture C fails in general;
- it showed that parts outside a window can cut a relation to a rectangle;
- it proposed the exposure lemma, adopted as Lemma E;
- it said to read forgetting on actual values (F′);
- it asked for a power floor and the mutations, which found the third class.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt (never forgetting and bounded reach) | **Status:** Successful | Census decided; the converse refuted as stated; C′ formulated |
| Local direction (bonds and dependence between two orbits) | Continue | 25 patterns test C′ directly |
| Broader exploration (G17's nested and addressed lines) | Known alternatives | Joins the nested line's dichotomy and Theorem I |
| Long-term goal (G17, Typical and rare meeting patterns, with G1) | Capability gained | Bounded reach now has a proved sufficient carrier and a sharp conjecture |

**Corrections:** none. **Goals:** a G17 checkpoint (with G1), capability gained. **Assumptions:** A83 used; none added.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Conjecture C′ on the 25 | 2/3 — Substantial | 2/3 — Testable | Prove growth for the 13 by a forgetting bound that counts only windows reachable from the top's orbits; read the 12 with an unexposed dependence at depth 11–13 with a longer search → a proof, or the first pattern with no two-orbit bond yet a bounded reach | Selected · awaiting go-ahead |
| 2 | Exact reach by least-mark costs (B186) | 2/3 — Substantial | 2/3 — Testable | As filed: min-plus over signature families with free parts → exact L(s) where orbits stay small | Alternative · deferred |
| 3 | Lower bounds when orbits grow (B188) | 2/3 — Substantial | 1/3 — Stated | As filed | Alternative · deferred |

The reasons for each rating:
1. **Conjecture C′.** Payoff 2: it would make "a two-orbit bond from the top that never untangles" the exact carrier of bounded reach,
   a characterisation in the program's own terms. Concreteness 2: the 13 have top pair projections that become products. A forgetting bound
   restricted to windows reachable from the top's orbits may prove their growth, and the 12 are a concrete test set. The uncertainty
   is the unexposed kind.
2. **Least-mark costs.** As filed; it would also decide the 25 exactly.
3. **Growing orbits.** As filed.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead.

## Hand-off to the referee

**Files.**
- This folder: the note, predictions, advisor Q/A, `two_orbit.py`, `classify.py`, `gate_two_orbit.py`, `run_census.py`,
  `run_sample.py`, `analyze_third.py`, `exact_third.py` and the outputs (`census_keep.json`, `sample_keep.jsonl`,
  `mutants_keep.jsonl`, `third_class.json`, `exact_third_*.json`).
- The proof family `proofs/KEEP-REACH-20261117-001A/`: `proof.md`, `check.py` and `result.json`.

**Status.** Proved: Theorems K and F′ and Lemma E. Computed: the census classification, the sample, the mutations, the third class,
and the exact readings.

**Least sure.**
- (a) `two_orbit.py`'s copy of the refereed routine, with its property swapped; checked against Theorem W and brute force.
- (b) `analyze_third.py`'s actual-value forgetting, which uses level states only to level 16 and r up to 10.
- (c) The "unexposed" verdict (labelled "hidden" in `third_class.json`), which checks exposure on the pair projections' projections at s = 13..16 only.
