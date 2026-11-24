# One birth at a time from what is built: result

Ticket `LOCAL-ROUND-20261123-001A` (sub-goal B323; goals G5 with G18), 2026-11-24. Computed with an engine written from the
frozen text by a helper that had not seen the drafter's prototype; scientific referee pending.
[Pre-registration](preregistration.md) · [definitions](../LOCAL-ROUND-20261123-001/definitions.md) ·
[shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ·
[code and its recorded readings](../../experiments/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/deviations.md) ·
[the thread's checks](../LOCAL-ROUND-20261123-001/checks/)

**Yes, with a record of who was made from whom. A knot may act as soon as every knot made alongside it has parents that have
finished giving, and it then works out, from those knots alone, what the complete round would have had it do. Births made
one at a time under that guard built what the complete rounds build in every order searched, with waiting, without it, and
under ordinary growth. On cycles through dead knots it is enough to read four steps out, whatever the cycle's size. It is
not enough when a knot has to wait more than once: each further wait reaches one step further, and a guard that checks a
fixed number of steps then fails. What makes this work is the written record of parents together with the rule that a knot
spends everything in one act; the study does not show that the round can be done without, only that nobody has to keep
it.**

## The laws, in plain words

A knot is **weaned** when none of its parents is still a member: they have finished giving. Its **brood** is every knot made
alongside it: its parents' other children, their parents' other children, and so on. Each law makes one birth at a time and
differs in what must be weaned before a knot may act.

| Law | A birth is allowed when | Reads |
| --- | --- | --- |
| R0 | (the record's birth-by-birth law) always; every knot reads the present roster | the present part |
| R1 | its parents are weaned | one step for the guard |
| R2 | its parents are weaned, and so is every knot that shares a parent with one of them | three steps for the guard |
| R3 | every knot of its parents' brood is weaned | the brood |
| T(d) | as R3, reading only knots within d holder steps | d steps |
| R3L | (the idea as first stated) its part of the present roster has no births yet | the present part |
| Control | (the record's depth guard, first knots supplied) it lies at the least unfinished depth | everything |

## Verdicts

Fourteen predictions were frozen. Eleven hold. Three hold in part, each only because a search over every order ran out of
its cap before finishing, with no mismatch found. None fails. "Sampled" means 200 orders, each a uniform choice among the
allowed births at every step; "x-last" means one order for each knot, which serves that knot last.

| # | Verdict | What was found |
| --- | --- | --- |
| Gate | Holds | The new engine's complete rounds give the same structure as the earlier study's engine after every round, for all 20 pairs of start and law (116 structures, exact isomorphism). Five altered controls are rejected. |
| P1 | Holds | On the cycle of four through dead knots with waiting, R2 and R3 build what the rounds build in every order through round 1 (65,803 and 65,791 states, 28 births). Through round 3: all sampled and x-last orders match; every order was searched without a mismatch to 20 of 112 births. |
| P2 | Holds | The same on the cycle of five and on the ring of five through round 1, in every order (about 1.05 million states each). |
| P3 | Holds | R1 fails with waiting, and the shortest failing order has exactly 7 births on all four starts. Every such failure is a knot that waited making one offshoot more than the rounds give it. |
| P4 | Holds | R3L fails on the cycle of n through dead knots at exactly 2n + 4 births (12, 14, 16 for n = 4, 5, 6). |
| P5 | Holds | With no waiting (a short knot retires, or makes offshoots), R1, R2 and R3 match in every order on the two-knot and three-knot starts, through round 3 (and through round 4 where the search finished). |
| P6 | Holds | R3L fails at 3, 3, 6 and 17 births on the four starts named, and does not fail on the three-knot start when the short knot retires. |
| P7 | Holds in part | Under ordinary growth R1, R2 and R3 match in every order on the cycle of four through round 2 (about 1.05 million states), the two-knot start through round 3 and the lone four-place knot through round 4, where the closing bit fires once in every order, at the reference's closing birth. On the ring of five through round 2 every order was searched without a mismatch to 36 of 50 births, where the registered cap of ten million states was reached (11.6 to 11.8 million states, the cap being checked at the end of a level); all sampled and x-last orders match. |
| P8 | Holds | On the start-clause counterexample every law but the control fails at 2 births, and the control underbuilds. |
| P9 | Holds in part | The control underbuilds in every order wherever a knot waits (a check), and never mismatches. With no waiting it matches in every order at every cutoff searched, except that on the ring of five under ordinary growth the search reached its cap at 36 of 50 births. |
| P10 | Holds | R0 fails on every start, at 1 to 3 births. |
| P11 | Holds | The least d at which T(d) has no mismatch is 4 on the cycles of 4, 6, 8 and 12 through dead knots, and 6 on the cycle of eight with three extra dead knots, where d = 2 to 5 all fail. Every order finished only on the cycle of four; on the cycles of 6, 8 and 12 and on the cycle with extra dead knots every order was searched to 21, 22, 7 and 20 births, with all sampled and x-last orders matching. |
| P12 | Holds (a check) | Under ordinary growth no member of any brood's roster at birth is short. |
| P13 | Open, reported | Where a roster has a group of three or more and nothing waits (the seven-knot generator), R1 matches: in every order when the short knot retires, and to 22 births with all sampled and x-last orders when it makes offshoots. |
| P14 | Holds in part | On the cycle of eight with three extra dead knots R2 fails, the shortest failing order having exactly 13 births; both named orders fail at the thirteenth. R3 shows no mismatch in any order to 25 of 44 births, where the cap was reached; all sampled and x-last orders match, and the order that defeats R2 is not allowed under R3. |

## What the result is

1. **The guard that works.** R3 never mismatched: in every order where the search finished, and in every sampled, x-last and
   partly searched order elsewhere. It does not read the round or the roster as it stands. It reads its brood as it was at
   birth and replays the round on that record.
2. **How far a knot must read.** On the cycles through dead knots four holder steps are enough at every size tried (4, 6, 8
   and 12 members), so the reading does not grow with the structure there. The thread's reading of why: four steps
   take a join to its parents, their other children, those children's other parents, and the children of those, which is
   what it takes to tell which of the knots it could join are short.
3. **Waiting is what costs.** A knot that waits reads a second time against the brood-mates that also waited, and who waited
   depends on knots one more step away. On the cycle of eight with three extra dead knots one join waits three times; R2,
   which checks three steps, fails there, and the least distance that works is 6, the brood's extent from that join. So no
   fixed distance is enough for every number of waits.
4. **Without waiting, less is needed.** Where a short knot retires or makes offshoots, and under ordinary growth, R1 already
   matched in every order that finished: it is enough that a knot's own parents have finished.
5. **Reading the present roster fails.** R0 and R3L, which read what is there now, fail within 1 to 17 births. What is there
   now mixes knots of different rounds; what a knot needs is its brood as it was made.
6. **The record's guard stops under waiting.** The depth guard matches wherever nothing waits and never builds anything
   wrong, but it gives a knot that waited nothing to do, so it stops before the rounds do.
7. **The start is not covered.** A start knot has no parents, so it reads the start as given. Where a start knot that acts
   meets one that waits, that reading is wrong, and every law fails at the second birth.

## What this does and does not show

The frozen text said this in advance, in the advisor's terms, and the result does not change it.

- **It shows** that the scheduler for the whole growth can be removed: nobody has to say "now everyone reads". Each knot can
  decide from what is built around it, given three things: every birth records its parents; a knot spends all it holds in
  one act; and a parent's death is the signal that it has finished.
- **It does not show** that the round can be done without. A brood is exactly one part's round, and the laws replay that
  round on the record. It does not show that the holders alone would do, with no record of who was made from whom. It does
  not show bounded reading where knots wait repeatedly.
- **It says nothing** for knots that hold instead of releasing, for the fillers, or for the cap of three (the two added
  rules of the ring that returns as recorded; a fixed ration of three was run in their place), for starts where a knot that
  acts meets a knot that waits, or beyond the rounds searched.

## Agreement with the drafter's prototype

The prototype was written by the drafter of the definitions and is independent of the engine.

- **Agree:** every verdict; every least number of births that the prototype had found by a finished search (7 for R1, 13 for
  R2, 12, 14, 3, 6 and 17 for R3L, 1 to 3 for R0, 2 on the start-clause counterexample); and the least distances 4 and 6.
- **Where the prototype had only sampled**, the engine's search gives smaller, exact numbers: T(2) first fails at 7 births on
  every start (the prototype had found 10 to 24), T(3) at 11 on the cycle of eight (17), and R1 at 7 through round 3 (9).
- **Counts over sampled and x-last orders differ**, since the two programs draw different orders; the shares are close.
- **Counts of states differ** in one family, the brood laws where a short knot retires (for example 400 against 517). The
  two programs seem to time a barring differently; this was not run down, and the verdicts there agree.
- **The advisor's account of the counterexample** holds, with one detail corrected by the engine's trace and by the thread's
  [hand trace](../LOCAL-ROUND-20261123-001/checks/hand_trace.md): the two joins that are misread are read as not short at the
  first reading, not the second.

## Deviations and limits

- **Time budgets were added to the caps (the thread's doing).** The pre-registration caps a search by its number of states.
  The thread's brief to the engine's author also set a time budget, so 46 of the 67 unfinished searches stopped on time
  before their cap. For P7, the one prediction where this mattered, the three searches on the ring of five were run again
  to the registered cap of ten million states (long-running check `LOCALROUND-P7-CAP`, 28 to 29 minutes each). Those are
  the numbers given above; the first runs had stopped at 35 births.
- **A prediction without a run.** P4 predicted the cycle of six, which no registered run covered. The engine's author ran it
  as an extra, recorded before the run.
- **A table and a rule disagreed.** The ring of five was listed with one cutoff for the search and another for the samples;
  every kind of order was run at both.
- **Readings recorded by the engine's author before the runs** ([deviations](../../experiments/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/deviations.md)):
  a barring is made only for a knot born by the cutoff; all barrings allowed at one moment are made together; an allowed
  birth is a set of parents, so a member's several offshoots count as one choice at a step (this sets what "a uniform choice"
  means); the all-short test is applied to every roster read.
- **Everything is finite.** Twenty pairs of start and law, to round 1 with waiting on the cycles and rings and to rounds
  2 to 4 elsewhere; of 193 registered searches over every order, 126 finished. That R3 is exact at every round rests on the
  brood argument of the definitions, which is an argument for the referee and is not proved here.
- **Evidence class:** exact computation, with a second, independent program agreeing on every verdict; one argument (the
  brood argument); a hand trace of the counterexample.
- **Scaffolds:** this ticket swapped the guard (five laws, the family T(d), a control), the ration with its treatment (three
  families) and the start. It did not swap the written record of parents, the start clause, the rule by which a waiter reads
  a second time, or the release rule. The laws and their guards are themselves supplied.
