# Does a pattern the growth makes count the ticks of a made clock? Result

Ticket `TIME-AS-FOLD-20261125-001A` (sub-goal B329; assumptions A223, A228 and A229; goals G5 with G15 and G18),
2026-11-25. Computed by an engine written from the frozen texts by a helper that had not seen the drafter's prototype;
the main run's verdicts recounted by the thread from the raw records. Evidence class of everything here: **computed,
bounded, referee pending.**
[Pre-registration](preregistration.md) · [claim](../TIME-AS-FOLD-20261125-001/claim.md) ·
[definitions](../TIME-AS-FOLD-20261125-001/definitions.md) ·
[the run's summary](../../artifacts/TIME-AS-FOLD-20261125-001A/TIME-AS-FOLD-20261125-001A-E001_count_of_returns/summary.md) ·
[the readings taken](../../experiments/TIME-AS-FOLD-20261125-001A/TIME-AS-FOLD-20261125-001A-E001_count_of_returns/deviations.md)

**No made count of returns was found. In 88,299 tests of a made clock and a second part, under every law run, the
claim that the second part makes a fixed number of its own knots for each tick and stops when the clock is barred
fails, each test decided. The weaker reading, that the second part's course differs when the clock is barred after
each of three returns, holds in 78 tests, all under rules that take from a recorded ancestor and choose by name, and
every such case is lost under some renumbering of its start. Under the two cheapest laws that let parts meet, no clock
gives parts off at four ticks at all. So the study reaches neither arm of its stop: no made part follows another's
returns at a fixed ratio, and no reason is shown that no law of this kind can hold both.**

The words. A **made clock** Y is a part the growth makes that returns: its roster is the same again after a fixed
number of rounds, each return a **tick**. The **second part** X is another part the growth makes, wholly apart from Y
when chosen. **C** is the claim of a count: over four periods X makes the same number of own knots in each, and with Y
barred after a tick X makes no further own knot after a short lag, through a meeting made by births, every knot
passing, under every registered numbering. **C-iii** is reading with no count: X's course differs within two periods
when Y is barred, at each of three returns. The laws are named as in the study of parts that meet again: COPY-LAW(t)
is that study's name for a ration and a treatment, not a law of copying; RING-LAW is the cap of three with short
knots waiting; MET lets a birth take a distinction held by a knot its parent meets; STEPS-k lets an offshoot take one
held by a recorded ancestor k parent steps above its parent; OLDEST, NEWEST, IN-TURN and BY-COUNT choose among
candidates by name. A period is always measured in rounds, which are supplied.

## Verdicts

| # | Kind | Verdict | What was found |
| --- | --- | --- | --- |
| P0 | gates | Holds | 3,346 of 3,346 runs equal, knot for knot, to the engine of the study of parts that meet again; the ring study's 227 starts with a tick that gives parts off reproduced exactly from 86,032 enumerated; 1,134 earlier runs matched over 9,862 rounds; 25 of 25 renamed parts accepted and 50 of 50 altered ones rejected. |
| P1 | check of an argument | Holds | With no taking rule no second part's course differs with the clock barred (1,083 tests under not-all-equal). |
| P2 | check of an argument | Holds | Under the laws of the count argument no series has more ticks that give parts off than start knots acting (288 runs in each of two groups). |
| P3 | seen in scratch | Holds | Under the two primary laws, on twelve named starts, no clock gives parts off at four ticks. With the fresh count taken by parents in place of distinct inputs, 10 runs have one. |
| P4 | seen in scratch | Holds | Under MET with the cap of three the start's roster never returns on the eight ring starts (192 runs). |
| P5 | by argument, and seen | Holds | C holds in none of 952 tests under the primary laws; where short knots make offshoots under not-all-equal, 473 of 473 tests are ruled out by the treatment, as argued. |
| P6 | seen in scratch | Holds | Under the primary laws C-iii holds only on the two-knot start, under STEPS-1 with COPY-LAW and offshoots, with OLDEST or IN-TURN: in 80 of the 240 numberings of that start, exactly those in which the start's shared distinction is the least-named place of the knot listed second. |
| P7 | by argument, and seen | Holds | Under STEPS-k the ring's own births are untouched for 2k rounds and the start's roster does not return after them (448 runs, 4 stopped by the guard); with k = 1 it never returns. The k is the law's. |
| P8 | seen in scratch | Holds | With no taking rule all 227 starts have a clock giving parts off at four ticks (454 of 454 runs); under MET none has (0 of 1,816). |
| P9 | seen in scratch | Holds | Each of seven structural statements about which rule keeps such a clock under which ration. |
| P10 | seen in scratch | Holds | The test with the second part barred, on the two-knot case, as registered. |
| P11 | by hand | **Fails** | The knot test: 28,352,211 verdicts on 28,590 runs, the two methods never disagreeing. Predicted: only the two parity joins of twelve parents under MET with NEWEST fail. Found: those two and 23 more, in 19 other runs, every one a join under parity with 4 to 38 parents; none is in the run of a C-iii case. |
| P12 | no prediction | Reported | The least law of the second arm that keeps a clock giving parts off at four ticks while a second part's course differs at each of three returns is STEPS-2 for offshoots of joins, on the two-knot start, in 112 of 240 numberings. |
| P13 | conditional | Not run | Its condition, a case of C under every registered numbering, is not met. |
| P14 | check | Holds | Masked runs are used only for the second part's trace. |
| P15 | seen in scratch | Holds | Under STEPS-2 with offshoots the C-iii cases are three-member parts of period 3 rounds that each return only while the other is there: 50 tests on 36 cases, every case lost under at least one registered shift of its start (between 16 of 32 and 106 of 168 pass). |
| P16 | seen in scratch, one clause by hand | Holds | Under STEPS-2 for offshoots of joins on the two-knot start, the second part's own knots per period are 7, 15, 32, 74 (not equal, so C fails) and the clock is unchanged with the second part barred. |

## Per law, in the registered form

- **C**: "none, every test decided" for every law run (88,299 tests, none undecided, none held).
- **C-iii**: found in 8 tests under the first primary law (STEPS-1 with COPY-LAW), in 20 under STEPS-2 for offshoots
  of joins and in 50 under STEPS-2, all under COPY-LAW. Under STEPS-2 with that ration 148 further tests are
  undecided: the masked run does not reproduce the difference, so "through a meeting" is not decided there. Every
  other rule: "none, every test decided".
- Recounted by the thread from the raw records of the main run: 88,299 tests; C fails in all; C-iii holds in 78 (8,
  20 and 50, as above) and is undecided in 148.

## What this shows and does not show

- **No count.** Where a second part's course does depend on the clock, either the treatment rules a count out or the
  second part's own knots grow from period to period, so there is no fixed number per tick. Nothing here is a
  counting pattern.
- **Reading at each return, only under supplied names.** Every C-iii case uses a rule that chooses by name, and none
  survives every registered numbering of its start: 80 of 240, 112 of 240, and between 36% and 63% of the
  registered shifts for the others, each numbering counted once. They are cases under a supplied numbering.
- **The cheapest laws for meeting make no clock that gives parts off.** Under the first this is argued for every
  start, given the supplied rule that a birth's fresh distinctions are counted by its distinct inputs; under the
  second it is seen only.
- **It is not a reason that no law can.** With MET's join clause alone the ring still returns and parts meet; no count
  was found there either, and that is a census result, not an argument.
- **Supplied**: the laws, the starts, the choice of take, the rounds in which every period is measured, the bars, the
  masks, and the study's own check that a return has happened. **Made by births**: the clocks, the second parts and
  their meetings.
- **Bounded**: twelve named starts and the 227 census starts, 18 rounds, the family of rules of the data file.
- **Not run**: 5,116 of the main run's 10,116 runs (1,309 with the fresh count by parents, 3,011 with demand taken
  before the takes, 486 and 310 of two further groups); the registered sizes understated the cost, and the run was cut
  to the first 5,000 in the registered order by a rule recorded before it. The knot test was not run on the runs of
  the numbering and swap runs, and on the comparison runs only for a seeded sample of 100 (2,383 runs, no failing
  knot). The run of the 200 further numberings and the conditional last run did not have their conditions met. None
  of these is a negative.

## Differences from what was disclosed, and readings

- **One column of the prototype's census** (runs with a series giving parts off at two or more ticks) is higher here
  in 8 of 82 cells, all for rules the prototype implemented itself; the two columns the predictions use agree in every
  cell. Not resolved; no verdict rests on it.
- **The main run finds three starts more** than the prototype with C-iii under STEPS-2 and BY-COUNT; all 44 of the
  prototype's cases are among the run's.
- **One reading changes a count and no verdict**: testing one clock of each form, as the main run registers, 110 of
  3,488 numbering verdicts differ from the prototype's; testing every clock gives all 3,488 equal. Both are in the
  outputs.
- **Four statements of the frozen texts** were found ambiguous or in conflict by the engine's author and are recorded
  with the reading taken: which clocks a numbering test must try; a second pass that can never be triggered once C
  fails everywhere; "a clock giving parts off at four ticks"; and the column "bound exceeded".
- **Readings recorded by the engine's author: 46**, each before the run it affects.
- **Evidence class**: computed by an engine written from the frozen texts, with its gates against two earlier
  engines; one recount by the thread from the raw records; no second program. Scientific referee pending.
