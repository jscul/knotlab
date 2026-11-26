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

## What was found

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
settles within the combined bound.

**How much this says (the advisor's caution).** The combined bound is weak: T and K are read from the same counts, and
K equals the bound in only 44 of 751 starts (6%) without parents, 8 of 553 under parity; the slack is usually 4. The
sharper result is the point law, now held on 18 held-out late starts (and on all 47 earlier ones); the settling-bound
referee also found the offsets 3 and 5 in 794 of the 815 earlier starts with any strict fall. What it says: once a
growth stops narrowing, a local reader's view becomes polynomial within three rounds (five with parents). What it does
not say: when the last fall comes, which still has to be read from the counts; no prediction of it from the start was
frozen.
