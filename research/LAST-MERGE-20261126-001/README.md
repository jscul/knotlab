# The last merge as the settling round of a local reader's view

Epic `LAST-MERGE-20261126-001`, at the coordinator's go-ahead on the selected direction of
[`SETTLE-BOUND-20261126-001`](../SETTLE-BOUND-20261126-001/decision.md). A check by the thread, not a registered
study; computed; referee pending. "Seen before the freeze" and "Frozen" were committed, after the advisor's review
([question](advisor_question.md), [answer](advisor_answer.md)), before the held-out sample below was read; the sample
was grown meanwhile and not opened.

## Seen before the freeze

On the 47 starts that settled past the largest-block bound (41 of five knots, 6 of a sampled thousand of six, under
not-all-equal), the settling round K is exactly T + 3 without parents and T + 5 with them, where T is the first round of
the final trough of the total count; 34 of them first narrow to a single birth a round. On every start of
SETTLE-BOUND's four runs, K ≤ max(M + 5, T + 3) and K ≤ max(M + 7, T + 5); T + 3 alone does not bound K (K − T reaches
11). A crude proxy for the size of the start's map of joins (live members plus leftover distinctions after round 1's
joins) does not give T: T minus it ranges from −7 to +1 on the 47. So no static prediction of T is frozen here.

## Frozen

**T** is the least t with c_s ≤ c_(s+1) for every s from t to the last round read before it, where c_s is the total
births of round s (the advisor's definition; plateaus are not falls). A start of dimension D is **checkable** when
K ≤ 24 − D, so that at least D + 1 rounds test its fitted polynomials; others are counted as censored, not as passes.

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
