# The settling cut after the last fall in births

(First titled "The last merge as the settling round of a local reader's view"; renamed at the referee's request.)

Epic `LAST-MERGE-20261126-001`, at the coordinator's go-ahead on the selected direction of
[`SETTLE-BOUND-20261126-001`](../SETTLE-BOUND-20261126-001/decision.md). A check by the thread, not a registered
study; computed; refereed (R1: confirmed with fixes, no Block; folded in below). "Seen before the freeze" and "Frozen" were committed, after the advisor's review
([question](advisor_question.md), [answer](advisor_answer.md)), before the held-out sample below was read; the sample
was grown meanwhile and not opened.

## Prior work in the program

Added after the referee (R1, item 6). The look-alike study's reader comparison
([`LOOK-ALIKE-20261126-001`](../LOOK-ALIKE-20261126-001/README.md#phase-2-the-held-out-test)) had already given the same
offsets, three and five rounds, for the seven five-knot starts that settled past its fixed cutoff after a burst; the
settling-bound referee ([report](../SETTLE-BOUND-20261126-001/referee-R1/report.md), item 5) added the count of 794 of
815 earlier not-all-equal starts with a strict fall; this study's freeze (commit `4efff45d0a`, note and sampler) records
the 47 fitting cases before that report was committed. The scoring wrapper first appears with the results (commit
`4707b8880b`); no separate registration or deviations file accompanies this check.

## Seen before the freeze

On the 47 starts that settled past the largest-block bound (41 of five knots, 6 of a sampled thousand of six, under
not-all-equal), the settling round K is exactly T + 3 without parents and T + 5 with them, where T is the first round of
the final trough of the total count; 34 of them first narrow to a single birth a round. On all 3,304
dimension-labelled start–law records of SETTLE-BOUND's four runs, through their last saved round (of 8,314 records; the
referee's denominator), K ≤ max(M + 5, T + 3) and K ≤ max(M + 7, T + 5); T + 3 alone does not bound K (K − T reaches
11). A crude proxy for the size of the start's map of joins (live members plus leftover distinctions after round 1's
joins) does not give T: T minus it ranges from −7 to +1 on the 47. So no static prediction of T is frozen here.

## Frozen

**T** is the least t with c_s ≤ c_(s+1) for every s from t to the last round read before it, where c_s is the total
births of round s (the advisor's definition; plateaus are not falls). A start of dimension D is **checkable** when
K ≤ 24 − D, so that at least D + 1 rounds test its fitted polynomials; others are counted as censored, not as passes.
[Added after the referee: the scorer also required 24 saved birth rounds, and the dimension labels 1 to 4 come from the
completed run; the same 18 starts per law were censored only by the 30,000-knot cap, and grown past it they meet the
combined bound and none is late.]

On a fresh sample of 2,000 six-knot census starts, disjoint from SETTLE-BOUND's thousand
(`random.Random(20261127).sample` over the rest of the census list; [`sample.py`](sample.py)), grown to round 24 under
not-all-equal and under parity:

1. **The point law.** Every checkable start of a dimension with K > M + 5 has K = T + 3 exactly, and every one with
   K > M + 7 in the reading with parents has K = T + 5 exactly.
2. **The combined bound.** Every checkable start of a dimension has K ≤ max(M + 5, T + 3), and K ≤ max(M + 7, T + 5)
   with parents.
3. **Tightness reported, not predicted:** the share of starts where K equals the bound, and the slack's distribution.

**Stop.** One checkable start that breaks 1 or 2, under either knot law; or none. The two laws share their starts and are
not independent trials. About one start in fifty was late in SETTLE-BOUND's runs, so the point law is expected to be
tested on some tens of starts.

## What was found

> **Referee R1, confirmed with fixes, no Block, folded in** ([report](referee-R1/report.md)). Narrowed: the offsets
> three and five are the settling cuts of the late starts only: a start that is not late (census entry 363: 11, 14, 15,
> 14, 14, 16, 19, 22, … births, last strict fall at round 4) has its cuts at 8 and 10, its two largest-block cutoffs, so
> "the view settles within three rounds of the last fall" fails unrestricted; on the alternative reading of "becomes
> polynomial" as the first round that agrees, the within-three (five) wording holds for all 244 and 55 checkable records
> with a strict fall, a reading outside the frozen prediction. The 18 late outcomes are 16 distinct starts (both parity
> cases repeat not-all-equal ones); an earlier parity census had grown 1,993 of the 2,000 sampled starts through ten
> rounds, including all 16, so the sample was held out from fitting this law but not unseen by the program. The point
> law implies the combined bound, so the bound is not a second test. Requiring each start to pass K1–K3 as a whole
> leaves 549 checkable parity starts, all passing. The sentences below are corrected where marked.

The fresh sample was grown under both knot laws ([`grown_fresh_nae.jsonl.gz`](grown_fresh_nae.jsonl.gz),
[`grown_fresh_parity.jsonl.gz`](grown_fresh_parity.jsonl.gz)) and tested by [`merge_test.py`](merge_test.py)
([`test_nae.json`](test_nae.json), [`test_parity.json`](test_parity.json)).

| knot law | starts of a dimension | censored | checkable | late (K > M + 5) | point law K = T + 3 (T + 5 with parents) | combined bound broken |
|---|---|---|---|---|---|---|
| not-all-equal | 769 | 18 | 751 | 16 | 16 of 16 (16 of 16) | 0 |
| parity | 571 | 18 | 553 | 2 | 2 of 2 (2 of 2) | 0 |

The rest: 1,223 stall under both laws; 198 close under parity; 8 unread.

**Both frozen predictions held: the stop is "none".** Every held-out start that settles past the largest-block bound
settles exactly three rounds after the last fall in its count of births (five with parents), and every checkable start
settles within the combined bound. [Corrected after the referee:] The point law implies the combined bound; only 16
not-all-equal and two parity outcomes in each reading could break that bound.

**How much this says (the advisor's caution).** The combined bound is weak: T and K are read from the same counts, and
K equals the bound in only 44 of 751 starts (6%) without parents, 8 of 553 under parity; the most frequent slack is 4
without parents (352 of 751 and 347 of 553) and 5 with them (159 of 751 and 158 of 553) [corrected after the referee
from "usually 4"]. The sharper result is the point law, now held on 16 distinct late starts, 18 start–law outcomes (and
on all 47 earlier ones) [corrected from "18 held-out late starts"]; the settling-bound
referee also found the offsets 3 and 5 in 794 of the 815 earlier starts with any strict fall. What it says [corrected after the referee]: on the 16 distinct checkable late starts, the interpolation cuts are three
and five rounds after the last strict fall, and the final polynomial sequences begin two and four rounds after that
fall; for starts that are not late the cut can come later (census entry 363). What it does
not say: when the last fall comes, which still has to be read from the counts; no prediction of it from the start was
frozen.
