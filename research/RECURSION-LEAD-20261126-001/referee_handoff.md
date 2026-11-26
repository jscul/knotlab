# Referee hand-off

Study `RECURSION-LEAD-20261126-001`: a check by the thread, computed, referee pending. Frozen in `1bae2cbd80` with the
advisor's review ([question](advisor/question.md), [answer](advisor/answer.md)) before the runs.

**Claims** ([the note](README.md), [the decision](decision.md)): (1) growing a start one round under parity and
exchanging it (`recur.py`, the second-check study's exchange recomputed by shortest cycles; checked equal on 28 stages)
returns the start only with loose values pinned: rings of 5 and 7 to 10 knots, and census entry 165; (2) no recorded law
pins a loose value (every birth has three or more places unless implied: `rival_growth.py`, `cut`); (3) no free exchange
returns or cycles (12 lawful, each stops within two steps); (4) beside it, no start keeps more than one whole-held fact
under two readings of a small change at rounds 1 to 3 (`tower2.py`). Data: `recur_*.jsonl`, `tower_*.jsonl`,
[`score.py`](score.py), [`score.json`](score.json).

**Points to press.** Whether the fast exchange equals the record's everywhere it is used; whether `same` (labelled
multigraphs with loose counts) is strict enough; whether "the pinning is never made by growth" is right under every arm
and under implied births; the UPTO5 reading's enumeration of cycles; and whether "not recursion" is worded right on the
owner's rungs.
