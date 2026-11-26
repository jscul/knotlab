# Referee hand-off

Study `SETTLE-BOUND-20261126-001`, closed 26 November 2026: a check by the thread, not registered; computed; referee
pending. The bound and expectations were committed in ec406f0ff7 before the test runs. Read [the decision](decision.md)
and [the note](README.md).

## Claims, each computed

1. The frozen bound (settling round at most M + 5 without parents, M + 7 with them; M the larger of the largest set of
   live start knots sharing a neighbour and the largest fresh count of a round-1 birth) fails on 41 of 1,556 five-knot
   starts of a dimension and 6 of 387 of a seeded sample of 1,000 six-knot starts under not-all-equal, and on 11 of 1,078
   and 2 of 283 under parity ([`bound.py`](bound.py), `test_*.json`, `grown_*.jsonl.gz`).
2. 30 of the 41 five-knot misses and 4 of the 6 six-knot ones narrow to a single birth a round and then grow as a lone
   knot; under parity the 30 close, and the 11 parity misses are the 11 that do not narrow.
3. With each start's bound as its cut, every pair the look-alike pair rule misses includes a start that settles past
   its bound.

## Points to press

- Is M computed as stated (Lemma R's live-neighbour sets; round 1 under the same law)?
- The six-knot sample: `random.Random(20261126).sample(census(6), 1000)` over the census list in its order; check it.
- Settling uses the look-alike study's definition with its least round of 3 (its referee's note): does that change any
  verdict here?
- Is "narrows to one knot" the right description of the late starts, and does the round of the last merge bound
  their settling (the note's link)?
