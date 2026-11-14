# How common certified counting inside is

Epic `CENSUS-FORGET-20261114-001` (`FREE-TARGET-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead.
Pre-registered in 1c416df97 (objects gate passed; advisor consulted). FREE-TARGET's exact forgetting test and audit (Codex's code,
unchanged) run on the shared runner from the thread's `job.py`. The canonical K1–K3 test is unchanged. **Conditional on the gap
argument, under FREE-TARGET's referee. Referee pending.**

## Words

As in FREE-TARGET:
- **Certified to grow**: some r with every product of r per-call port relations rectangular. Then at every depth s where a bond
  exists, every bond from a top port to **any** copy at depth s, members **anywhere**, has at least 2 + ⌊s/r⌋ members. A bond exists
  wherever the first ray has one (L_any ≤ L_ray).
- **Chains**: one SELF call and no other self-holding call, so there is one copy per depth and no side copy. Then L_any = L_ray.
- **Weight**: the share of draws (A79).

## The question

Across the census, what share of the families whose first-ray bond provably grows is certified to grow with nothing chosen?

## The question in standard terms

For each of 12,772 iterated hyperedge-replacement NAE families, whether the semigroup of its per-call 8 × 8 port relations becomes
rectangular, weighted by the description weighting.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The test is exact and checked.** All 12,772 first-ray growers finished (3 minutes, 0 errors). The independent audit re-derived every certified family's relations and certifying products: 5,841 families, 0 mismatches. FREE-TARGET's 66 reproduce (43 certified, same r in all 66). No certified family is bounded over paths in EVERY-RAY's 300 sampled growers, a consistency check. No empty relation occurs. | computed | G passed |
| 2 | **Among the non-chains, certified growth is a minority, but not a small one.** Of 7,646 non-chain draws, 1,618 (21.2%) are certified. That is 1,080 of 6,989 with two or more SELF calls (15.5%; Wilson 14.6% to 16.3%) and 538 of 657 with one SELF call and other self-holding calls (81.9%). 5,962 (78.0%) are certified non-forgetting (a recurring non-rectangular product) and 66 capped. Outside EVERY-RAY's sample, the c ≥ 2 share is 15.5% (14.65% to 16.38%). | proved per family (conditional) | P1 held (8% to 25%) |
| 3 | **Together with the chains, half the first-ray growth weight.** The chains count by construction: 5,633 draws (42.4%). With the 1,618 certified non-chains, 7,251 of the 13,279 first-ray growth draws (54.6%) grow with nothing chosen, at every depth where a bond exists. That is 3.25% of all 223,261 nested draws. The rest of first-ray growth (45.4%) is undecided here, almost all of it certified non-forgetting. | proved per family (conditional); chains by construction | reported |
| 4 | **The limit-only growers never forget.** None of the 224 one-definition limit-only growers of `PROVED-RATE-20261113-001` is certified (203 non-forgetting, 21 capped). The census's growth there is not counting with nothing chosen by this test. | computed | reported |
| 5 | **r is small.** Certified families have r = 1 (128), 2 (1,431), 3 (2,512), 4 (530), 5 (1,068), 6 (116) or 7 to 12 (56), so the lower bound gains a member every one to six levels in almost all of them. | computed | reported |

## Answer

About half of the census's first-ray growth weight is growth the law makes with nothing chosen. Every bond from the top to any copy at
depth s needs a number of members rising with s, wherever they sit. Four fifths of that half is the single chains, which are counters
by construction. The other fifth is families with several ways down, every one of which forgets. Among families with two or more
self-calls only about one in six forgets, and none of the limit-only growers that started this line does. As a share of all nested
patterns under the description weighting it is 3.25%: a definite, uncommon kind. *(Conditional on the gap argument's review;
unrefereed.)*

## Reading

**Interpretation, not a theorem.**
- **Counting inside, by weight.** The law counts depth inside a nested pattern with nothing chosen in about one draw in thirty of the
  whole population. That is about half of the patterns whose first ray grows. It happens mostly where the pattern is a chain, and
  otherwise where every way down forgets.
- **Where it does not.** The undecided half is mostly certified non-forgetting: some way down keeps a correlation between its ends.
  Such families may still grow (FREE-TARGET's 21 were undecided), or be bounded at every depth along paths that change with the depth
  (EVERY-RAY's counterexample shape).

## Lag cutoffs and census-only claims

The 12,772 census families with a provably growing first ray (13,279 of 223,261 draws), a selected population: the share is over
them, or over all draws where stated. Per depth, at depths where a bond exists. No claim about families whose first ray does not grow,
or about the undecided half.

## Review

**Referee pending.** The advisor model reviewed the design cold (`advisor_review_answer.md`); its points were adopted.

## Literature and provenance

As in FREE-TARGET (rectangular powers; BRANCH-DEPTH's gap argument generalized). Ours: the census-wide count.

## Workspace assumptions

A79 used.

## Ratio

Substantive: 12,772 exact decisions. Administrative: the freeze, the job wrapper, this note.

## Corrections

None.

## Data

`experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/`: `job.py`, the run in `full/`
(`results.jsonl`), and `read_census.py`, which writes `reading.json`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the census share | **Status:** Successful (referee pending; conditional) | P1 held; gates passed; 54.6% of first-ray growth weight certified |
| Local direction — counting inside | Continue | The undecided half is mostly non-forgetting; a different argument is needed there |
| Broader exploration — G17 | Searching | Counting inside located by weight; its cause in the calls is open |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The share of patterns in which the law counts depth with nothing chosen |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A79 used.
**Basket:** `FREE-TARGET-20261114-001#2` (2/3 Payoff, 2/3 Concreteness), `FREE-TARGET-20261114-001#3` (2/3, 2/3),
`EVERY-RAY-20261113-001#3` (2/3, 2/3), `TRUE-BOND-20261113-001#2` (2/3, 3/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What makes every way down forget | 2/3 — Substantial | 3/3 — Ready | From the 12,772 verdicts, a rule in the SELF calls' port maps and the knots on the ports (for instance: no port passed down by identity on any cycle of calls) → a syntactic criterion that predicts forgetting on the census, exactly or with stated exceptions | Selected · awaiting go-ahead |
| 2 | The non-forgetting growers | 2/3 — Substantial | 2/3 — Testable | On a sample of the 5,962 certified non-forgetting non-chains, members anywhere and any target with depth-dependent paths (the referee's counterexample shape) → bounded per depth, or growth by another argument | Alternative · deferred |

1. Payoff 2: the cause of counting inside, as a rule a reader can check by eye. Concreteness 3: the verdicts and relations are on
   disk; the search is over simple features.
2. Payoff 2: the undecided half. Concreteness 2: needs a per-depth members-anywhere method.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
