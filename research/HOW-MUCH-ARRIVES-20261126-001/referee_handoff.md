# Referee hand-off

Study `HOW-MUCH-ARRIVES-20261126-001`, closed 26 November 2026 by the thread: a check, not registered; computed;
referee pending. Read [the decision](decision.md) and [the note](README.md) (design frozen before the full run, the
advisor's review, expectations, results, a correction made before this hand-off).

## Claims, each computed

1. **Local readings forget the start.** In the readings without names (sig0: a birth's kind, number of parents, fresh
   distinctions, places; sig1: sig0 with its parents' sig0), two touching knots and three knots in a row grown under the
   ordinary count differ in no birth from round 4 to round 32 ([`control.py`](control.py), [`control.json`](control.json)).
2. **Seven changes at the start show only as a fixed count.** For the marks and moves on two touching knots and the
   middle mark and two end-to-end moves on three knots in a row, the sig0 and sig1 damage (multiset difference both ways
   of a round's births) is exactly 4, 5 or 1 every round from about round 5 to round 32 ([`longer.py`](longer.py)).
3. **By descent, one whole line.** A mark at one of two touching knots re-makes every birth, by name, of the shell
   nearer it (holder steps, structure after the round) and none of the shell one step further: 62 of 62 and 0 of 66 at
   round 32; at the middle knot of three in a row, 63 of 65 and 0 of 68 ([`control.json`](control.json)).
4. **Everything else holds or takes over** (verdicts over the whole series, rules in the note): the tables in
   [`tables.md`](tables.md) from [`runs.jsonl.gz`](runs.jsonl.gz) by [`tally.py`](tally.py); 366 jobs, none lost.
5. **A pulse never dies out** (0 of 155), and the reason read in one case: a join is paid one more fresh distinction in
   advance for a join with the struck offshoot.
6. **Pairs:** 4 of 30 pairs of made marks give less damage than either alone (sig1).
7. **Setting B:** under the ordinary count no change shows in a joined pattern's own births; under the record's one
   fewer with waiting, two of seven far marks show at every d = 1..8, at round d + 5, share 1.00; under the cap of
   three the far site with two against three shows at round 2d + 1, first-round share 0.12 to 0.24 rising with d.
8. **Parity** gives the same output as not-all-equal in all 161 jobs run under both.

## Points to press

- Claim 1 is the control that narrowed the study. Is it general (other pairs of dimension-two starts; rings of one rate)?
  Does it make every "weakens" verdict of the design a reading of the round's count?
- The growth engine is the shared one (`experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/.../eng.py`), imported unchanged.
  Regrow at least the two-touching and chain3 cases with code of your own from lesson 8.1's law and compare.
- The naming by descent (bench naming): could a renaming artefact make claim 3's 0 of 66 or 62 of 62?
- The verdict rules were written before the run; the damage was changed from one way to both ways after one case was
  seen in testing (disclosed). Did that change any verdict?
- The pulse's strike rule bars the loose distinctions of the knots made in round s + 1 that hold the added
  distinction. Is that the intended "struck after one round", and does claim 5's reason hold beyond the case read?
- Setting B imports the starts and laws of `SHORT-AGAIN-20261126-001` and `SWITCH-RECEIVERS-20261126-001`; check the
  B2 receiver and senders are the ones those studies named.
