# Referee hand-off

Study `LAST-MERGE-20261126-001`: a check by the thread, computed, referee pending. Frozen in 4efff45d0a with the advisor's
review before the held-out sample was read. Claims: on a fresh seeded sample of 2,000 six-knot census starts (disjoint
from SETTLE-BOUND's thousand; [`sample.py`](sample.py)), under not-all-equal and parity to round 24, (1) every checkable
start of a dimension that settles past M + 5 settles at exactly T + 3, and past M + 7 with parents at T + 5 (16 and 2
starts), T the least round from which the count of births never falls; (2) every checkable start settles within
max(M + 5, T + 3) and max(M + 7, T + 5). Data: `grown_fresh_*.jsonl.gz`, `test_*.json`, [`merge_test.py`](merge_test.py).

Points to press: that the sample is disjoint and seeded as stated; censoring (K > 24 − D or a run shorter than 24) and
whether it hides a break; whether the point law could fail at all given how T and K are read (the advisor's caution);
SETTLE-BOUND's referee notes on negative fitted counts and the settling definition.
