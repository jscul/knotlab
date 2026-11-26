# Referee hand-off

Study `ON-DEMAND-20261126-001`: a check by the thread, computed, referee pending. Frozen in `de892a09d6` with the
advisor's review and its hand test ([question](advisor/question.md), [answer](advisor/answer.md),
[`handtest.json`](handtest.json)) before the runs; one deviation recorded before the rerun of the set with cycles.

**Claims** ([the note](README.md), [the decision](decision.md)):
1. The roster engine ([`ondemand.py`](ondemand.py)) equals the look-alike study's growth on every four-knot census start
   under both laws; the five-knot check (`verify_5_*.jsonl`) is a stress test pending.
2. Under not-all-equal, for every start that does not stall and its reader (a live start knot), the growth on the live
   knots within t + 1 steps of the map gives the reader's view through round t exactly (2,256 of 2,256 cases); within t
   steps fails only where the edge cuts a round-1 group of three or more (27 cases).
3. Every region holding those knots, and every step of admitting more, gives the same view (1,544 checks).
4. The round-1 shortage and parity's implied birth are the only reads of the whole start: 2 of 252 stalling starts have
   the short knot beyond the reader's piece; under parity all 53 differing cases are implied closures of the region.
5. A reader's view rests on a median of 28% (trees) and 34% (with cycles) of the births.
Data: `results_*.jsonl`, [`score.py`](score.py), [`score.json`](score.json), [`run.py`](run.py).

**Points to press.** Whether the region rule (blocks cut to the region, open counts unchanged) is the right on-demand
computation, or hides a read of the far side (the holders); whether "steps of the map" from one start knot is computed
as stated; whether any stratum could have failed (the trees cannot cut a group of three); the cap's effect (rounds past
the full growth's cap are not read; region growths of the rerun are capped, of the first two sets not); the 9 parity
H2 differences whose ends were not recorded; the views as "descendants of the reader" against other readings; and
whether the claim of what it does not show is worded right.
