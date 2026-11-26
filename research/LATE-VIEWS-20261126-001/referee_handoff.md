# Referee hand-off

Study `LATE-VIEWS-20261126-001`: a check by the thread, computed; refereed (R1, confirmed with fixes, no Block; [report](referee-R1/report.md)), with the denominators below as corrected in [the note](README.md). Frozen and pre-registered in
`f97fd78ae5`, with the advisor's review ([question](advisor_question_freeze.md), [answer](advisor_answer_freeze.md)),
before any grown file of the held-out sets was opened; the sets were grown meanwhile.

**Claims** ([the note](README.md), [the decision](decision.md)):
1. A predictor ([`late.py`](late.py)) reads a local reader's view (per round, the multiset of births by parents and
   fresh distinctions, `sig0`, and with the parents' kinds, `sig1`) off a start's finite map without growing it: valid
   sets of the core, endless chains as binomial tails, repeated blocks as distinct maximal sets, round-1 groups of three
   or more as cells, and the relay of a finite piece.
2. Its predictions, hashed in [`predictions.jsonl.gz`](predictions.jsonl.gz) (sha256 of the uncompressed content in the
   note), agree in every round with the grown views for 705 of 706 accepted starts of a uniform seeded sample of 2,000
   six-knot census starts, 159 of 199 of a stratified supplement, 15 of 16 starts built by hand, 70 of 70 seven-knot
   starts of a second weighting, and 100 of 100 grown to round 40, under both knot laws ([`score.py`](score.py),
   [`score.json`](score.json)).
3. The settling round predicted from the start equals the grown one wherever the views agree (P2); the three negative
   controls fail (P4); every start read as stalling stalls in round 1.
4. The cell reading fails where two cells share a knot (39 of 39), and in 3 starts where a block meets a cell of four.
5. Post hoc, not a test: a graded-order reading fixes 40 of the 42 misses ([`posthoc.py`](posthoc.py),
   [`posthoc.json`](posthoc.json)).
6. Fitting data (seen before the freeze): every accepted census start of up to five knots agrees ([`fitting/`](fitting)).

Evidence class: computed. The proved identification (`DOUBLE-IDENT-20261119-001A` and its predecessors) covers only
39 of the 706.

**Points to press.**
- Whether the predictor is the growth in another form: it imports nothing of the growth engine except, for the
  stratum label only, `DOUBLE-IDENT`'s classifier; round-1 groups are computed in `late.round1` (equal to the engine's
  on all 86,036 census starts of one to six knots). Check whether any part of the prediction reads the engine.
- The pre-registration: that `predictions.jsonl.gz` in `f97fd78ae5` matches its stated hash and is what `score.py` read,
  and that the samples are seeded and disjoint as stated ([`sample.py`](sample.py), [`strata.py`](strata.py),
  [`sample_grow.py`](sample_grow.py), [`horizon.jsonl`](horizon.jsonl)).
- Whether P2 is a second test or a consequence of P1 (the note says a consequence), and whether the controls could have
  failed to fail.
- The strata: the stratified supplement was drawn after the five-knot fitting; whether "every other stratum agrees"
  holds with the strata as drawn, and whether any agreeing stratum is too small to say so.
- "A local reader's whole view ... read off the start's finite map": a headline from 705 of 706; check its wording
  against coverage (41 of 747 non-stalling uniform starts have a piece with a cycle and are not predicted).
