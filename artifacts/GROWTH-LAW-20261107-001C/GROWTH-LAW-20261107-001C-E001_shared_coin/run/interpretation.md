# Where the pinwheel's growth fails, and what it needs: interpretation

Experiment `GROWTH-LAW-20261107-001C-E001` (exploratory), run 2026-11-07 under the frozen contract on 20 workers, about 50
minutes: 126 jobs. Rows are in `rows.jsonl`, totals in `result.json`.

**The summary step.** The run's final summary step failed on tuples used as JSON keys after every job had finished and been
written to `rows.jsonl`. The traceback is in `log.txt`. The summary was rebuilt from `rows.jsonl` by the corrected `run.py
--summarize`, and no job was re-run (`log_summarize.txt`).

## Controls

- **Traces reproduce ticket B.** All 70 traces reproduce their ticket B runs exactly: outcome, tiles and moves.
- **The oracle never gets stuck.** It never dead-ended, and all 15 of its final patches embed, as a pinwheel patch must allow.
- **The stronger law passes its replay.** Under the stronger law, growth that follows a genuine pinwheel patch (T_6) reached 500
  tiles in 126 moves (97 forced, 29 choices) with no rejection.

## Trace: where growth leaves the pinwheel

- **Always at a coin.** In all 70 runs the first move after which the patch is no longer a pinwheel patch was a choice, never a
  forced move. On a pinwheel patch a forced move is the genuine continuation, so this is as it must be.
- **Early.** In bfs that move was move 2 to 26 (median 7), in random 2 to 12 (median 5), in finger 2 to 10 (median 4), and in
  forced-first growth 5 to 73 (median 18).
- **Usually one right option.** At that move exactly one option kept a pinwheel patch in 59 of 70 runs. It was 1 of 2 in 35 runs,
  1 of 3 in 15, and 1 of 4 to 1 of 10 in 9. In the other 11 runs 2 to 4 options were right.
- **Seen late, and nearby.** The patch then carried the error for 0 to 145 moves (median 14) before its run ended. Where it ended
  in a dead end (66 runs), the dead tile lay 1 to 19 tiles from the wrong move (median 3).

## Oracle: how much information growth needs

Fifteen oracle runs (bfs seeds 1 to 10, random seeds 1 to 5) each reached 1,000 tiles.

| | Per run, after the seed's 54-way choice |
| --- | --- |
| Choices | 34 to 67 (775 in all) |
| Choices with exactly one legal option | 693 of the 775 (89%) |
| Bits the oracle supplied (log₂ of the legal options) | 4.0 to 9.6 |
| Bits the choices seemed to offer (log₂ of all options) | 45.7 to 88.1 |
| Chance that coins stay inside the pinwheel to 1,000 tiles | 2^−40.6 to 2^−82.0 |

- **Where the real choices sit.** Choices with more than one legal option thinned out as the patch grew: 37 of the 82 came within
  the first 60 tiles, and only 12 after 400.
- **The seed's choice.** All 54 collars of the seed's handedness occur in pinwheel tilings, so it is always free: 5.75 bits.

## Stronger law

- **It gets stuck too.** Under the collar law plus the radius-2 atlas, all 40 runs dead-ended: bfs 20 of 20 and random 20 of 20,
  within 18 to 214 tiles. No final patch is a pinwheel patch.
- **It changes when, not whether.** 35 runs stopped at exactly the size of the collar-law run with the same seed. The other 5 bfs
  runs stopped sooner (194, 165, 122, 214 and 160 tiles, against 205, 304, 241, 230 and 241). None got further.

## Reading against the decision rule

- **Trace.** Every first illegal move is a choice. So the patch leaves the pinwheel at a coin, and usually that coin had one right
  option among two or three.
- **Oracle.** The bits of legal options grew far more slowly than those of all options: 4 to 10 against 46 to 88 by 1,000 tiles.
  So growth needs few hidden bits, and local coins cannot share them. This is the shared coin of `GROW-COIN-20261107-001`: there
  the four equator corners had to agree on one bit, and here every tile of the growing boundary must agree with a handful of
  hierarchy bits that nothing local shows.
- **Stronger law.** It does no better. It detects some deceptions a little sooner and avoids none, as Dworkin and Shieh (1995)
  predict for every aperiodic protoset of the plane.

## Nonclaims

- **Finite runs.** The sizes and runs are finite. Bits per level was not measured.
- **The oracle is a measurement.** It reads the whole patch through the embedding test, so it is not a growth law.
- **One stronger law.** Only one stronger law was tried.
