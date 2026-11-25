# How little has to be written for a knot to find its parents? Result

Ticket `LEAST-RECORD-20261124-001A` (sub-goal B325 after its first step; goals G5 with G18), 2026-11-25. Computed with the
earlier search's program, extended by its author from the frozen text; scientific referee pending.
[Pre-registration](preregistration.md) ·
[code and its recorded readings](../../experiments/LEAST-RECORD-20261124-001A/LEAST-RECORD-20261124-001A-E001_least_record/deviations.md) ·
[the thread's own check](../LEAST-RECORD-20261124-001/checks/thread_checks.txt)

**Three values are enough. If every new knot writes one of three values, one step on from its parents' value, any knot
can tell its parents from its children by comparing values with the knots it meets, looking one step and no further. This
held on every structure reached, half-built ones included, under all four laws, and under holding on the structures tried.
No stamp of two values that was tried does the same under every law. The one place it fails is the start built so that a
start knot waits while a knot it meets acts; there five values are enough. The stamp is written by hand, and it is itself
the order of descent cut down to three values: the result says how small the record can be, not that the growth supplies
it.**

## What was done

A **stamp** is one value written on each knot. Ten stamps were tried, from two values to the full generation, each added
to what a knot sees within d holder steps, and the earlier search was rerun: are there still two places, one leading to a
parent and one not, that look alike? A knot's **generation** is 0 for a start knot and one more than its parents' for a
new knot.

## Verdicts

| # | Verdict | What was found |
| --- | --- | --- |
| Checks | Hold | The earlier checks still pass with no stamp; a stamp that is the same everywhere changes nothing; a hand-built structure of five knots comes out as stated; a stamp changed four steps away is unseen at distances 1 to 3 and seen from 4, 60 times of 60. |
| P1 | Holds | Wherever no start knot waits in a round in which a start knot it meets acts, every birth's parents have equal generations: none of 34,243 births is an exception. With the generation counted in threes shown, the rule "the other holder is a parent exactly when its stamp is one less" gives every place of both populations under all four laws (for example 807,124 of 807,124 under a fixed three with waiting). |
| P2 | Holds | That condition fails on one registered start only, the one built to break it. There a round-2 knot has parents of generations 0, 1, 1 and 1, and the rule reads its place to the start knot wrong from both sides. |
| P3 | Holds (a check) | The full generation gives every place everywhere. |
| P4 | Holds (a check) | "Has no usable loose place" changes nothing: every look already shows it. |
| P5 | Holds | "Has made a birth" leaves a start knot and a new offshoot hanging off the same knot exactly alike, at every distance, and changes nothing on the complete rounds of the proved case. |
| P6 | Holds | The generation counted in twos leaves look-alike pairs at every distance in the finished structure of 16 knots, and at distances 1 to 5 at round 12 where a short knot makes offshoots. |
| P7 | Reported | The table below. |
| P8 | Reported: none | No stamp of two values in the table recovers the parents under every law. Two do under one law only. |
| P9 | **Fails** | Under holding every birth's parents still had equal generations, in all 16 runs through six rounds, and the three-valued rule gave every place. The advisor had leaned the other way. |

## The table of costs

The least distance at which a rule recovers every parent, on both populations together, where the condition of P1 holds.
"None" means look-alike pairs remain, or the only distances without them are ones where every look reaches a start knot or
a member, which is not counted.

| Stamp | Values | Who writes it | Short knot makes offshoots | Short knot retires | Fixed three, waiting | Ordinary growth |
| --- | --- | --- | --- | --- | --- | --- |
| Nothing | 1 | — | none | none | none | none |
| Has no usable loose place | 2 | nobody: it is visible | none | none | none | none |
| Has made a birth | 2 | the birth, on an old knot | none | none | none | none |
| Has two or more parents | 2 | the new knot, from its own birth | none | none | none | none |
| Is a start knot | 2 | comes with the start | none | 2 | none | none |
| Generation counted in twos | 2 | the new knot, from its parents' stamps | none | 2 | none | none |
| **Generation counted in threes** | **3** | **the new knot, from its parents' stamps** | **1** | **1** | **1** | **1** |
| Has made a birth, and is a start knot | 4 | both | none | 2 | none | none |
| The number of its parents | grows with the law | the new knot, from its own birth | 2 | 2 | none | none |
| The full generation | grows with the growth | the new knot, from its parents' stamps | 1 | 1 | 1 | 1 |

- **The three-valued stamp is the only small one that works everywhere**, and it works at the least distance there is. The
  places it was checked on are not all near the start or the live roster: between 38,910 and 95,112 of them, by law, see
  neither.
- **A new knot can write it knowing only its parents' stamps.** No old knot is rewritten and nothing about the start has
  to be known beyond "a start knot is 0".
- **The number of a knot's parents** is enough at two steps on structures built by complete rounds under the two laws with
  "just enough for three places", but not on every half-built structure, and not under the other two laws.
- **Smallest failures.** With nothing written, or with any of the first three two-valued stamps: two knots, a knot and
  its first offshoot (or three, with a second start knot). With the generation counted in twos: the finished structure of
  16 knots.

## Where it fails, and what works there

On the start built so that a start knot waits while the knots it meets act, that start knot later joins knots one
generation younger. The join's parents have generations 0 and 1, its own is 2, and "one less, counted in threes" reads its
place to the start knot as leading to a child. The greatest difference between a child's generation and a parent's is 2
there, so counting in fives works, with the rule "a parent is one or two less". In general a count modulo one more than
twice the greatest such difference works at one step.

## What this does and does not show

- **It shows how small the record can be.** The earlier study needed, for each shared place, which holder was the parent.
  One of three values per knot carries the same, wherever the knots that join were made together.
- **It does not show that the growth supplies the stamp.** Someone writes it. And the stamp is not something other than
  the order of births: it is that order, cut down to three values.
- **It does not show that two values cannot work.** The five two-valued stamps tried do not. A cleverer one, read over a
  longer distance, is not ruled out.
- **By construction, not run:** a guard that recovers the parents exactly can stand in for the written record in the
  one-birth-at-a-time laws and decide the same. That was not run as its own test.

## Deviations and limits

- **A count that added nothing (the thread's and the advisor's design).** The second guard count, for looks holding no
  place between two start knots, always equals the first: a look with no start knot cannot hold such a place. The engine's
  author reported a variant beside it.
- **One law under holding could not count.** Under a fixed three with waiting and holding, every look reaches a start knot
  or a member at every distance, so no rule there is counted, although the full generation's rule is right on every place.
- **P9 was a lean, not a prediction with an argument.** On other starts or longer runs under holding, parents of unequal
  generations may still occur; none did here.
- **The 28 readings** of the engine's author are recorded with the code. The condition is read as: a start knot waits in a
  round in which a start knot it meets is a parent of a birth.
- **Six processes took 10 to 25 minutes**, within their memory caps (long-running row `LEASTREC-RUNS`).
- **Everything is finite:** the structures of the earlier search (twenty starts and laws, to about 2,000 knots or twelve
  rounds, and the half-built structures of twenty sampled orders), and sixteen runs under holding to six rounds.
- **Evidence class:** exact computation; an argument for why parents have equal generations (a proof sketch by the
  advisor, in the pre-registration); the thread's own check of the rule on ten grown structures.
- **Scaffolds:** every stamp is supplied, and so is who writes it. Ten were tried; the result is the table.
