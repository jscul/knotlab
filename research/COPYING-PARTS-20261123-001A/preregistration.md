# Parts that copy themselves: what they are and what they need. Pre-registration

Ticket `COPYING-PARTS-20261123-001A` of epic `COPYING-PARTS-20261123-001` (direction 1 of `RING-IN-BALANCE-20261123-001`;
goals G18 with G17), 2026-11-23. Frozen before the study's code is written. Code by a helper agent from this text, using the
engine and the [definitions](../RING-IN-BALANCE-20261123-001/definitions.md) of `RING-IN-BALANCE-20261123-001`, which are
taken over unchanged. The canonical K1–K3 test is unchanged.

## The question

The owner asked on 23 November 2026 whether the growth has "structures that output other structures that either die, or
live, or combine with other patterns", like "cells reproducing". The study of the ring that returns swapped the ration of
fresh distinctions for others and found, without anyone having predicted it, that under three rations (FLOOR0, FLOOR1 and
ONE-FEWER) a part of two knots comes back after two rounds beside a copy of itself, with no knot waiting. This study asks
what these parts are on real knots: the cycle by which one becomes two, the count of copies under each treatment of a short
knot, whether every knot made passes the knot test under both knot laws, which of the supplied rules the copying needs, and
what makes the copies stop. No claim is made about living things.

What it cannot show: under these laws parts that have come apart act alone and never become joinable again, so the copies
cannot combine with one another or read one another. That part of the owner's question is outside this study by construction.

## In standard terms

A component of a synchronous graph-rewriting system whose descendants after a fixed number of steps include two or more
components isomorphic to it. Since the components never interact, the kinds of component form a context-free substitution
system (the literature's 0L system; Lindenmayer 1968), equivalently an age-structured population with fixed offspring (Leslie
matrices), and the count of copies obeys a linear recurrence whose leading root is the growth per step. The comparison with a
cellular automaton's replicator is loose: there the copies collide, and growth is slower for that reason.

## Prior work in the program

Searches, each with `--until 2026-11-23 --exclude COPYING-PARTS-20261123-001`:

`python3 -B scripts/track.py objects "part of the live roster that copies itself, replicator" --until 2026-11-23 --exclude COPYING-PARTS-20261123-001`
`python3 -B scripts/track.py objects "floor ration, arity-floor law, one-fewer law, forbidding join" --until 2026-11-23 --exclude COPYING-PARTS-20261123-001`
`python3 -B scripts/track.py objects "number of copies by round, Fibonacci, Pell, doubling" --until 2026-11-23 --exclude COPYING-PARTS-20261123-001`

- `RING-IN-BALANCE-20261123-001` — the same object: its ticket A found these parts in a table of 70 laws on three rings and
  did not study them; its definitions, its engine and its settled statements (the roster decides the round; parts act alone
  past the start) are used here.
- `READ-ORIGIN-20261120-001` — unrelated (marks for original knots).
- `FRESH-COUNT-20261118-001` — a relative: the ordinary fresh count. `FORBIDDING-JOIN-20261120-001` — a relative: the laws
  that give a join one fewer distinction than it is asked, or only its floor, were introduced there for another purpose;
  no part that copies itself is reported there.
- `RING-FORMULA-20261118-001`, `RING-GROWTH-20261118-001` — relatives: growth rates of rings under ordinary growth, where the
  golden ratio appears as the rate of one growing part; here it would be the rate of a count of separate parts.

## Prior work outside the program

Self-reproducing automata go back to von Neumann (1966); a cellular automaton's replicator is a pattern that makes copies of
itself (HighLife's, Bell 1994), whose copies collide. Populations with fixed rules of division are the setting of Fibonacci's
rabbits, Narayana's cows and the Pell numbers, and of Lindenmayer's systems. A knot that waits for two partners while holding
one distinction is the literature's deadlock by contention for a resource (Dijkstra's dining philosophers). What this would
add is copying parts whose every piece is a knot under the canonical test, on a structure with no board. Not searched further.

## Known before the freeze (disclosed)

From ticket A of the earlier study and the thread's check with the pilot's program, on the ring of five under FLOOR0: the
two-knot parts number 5, 0, 10, 0, 20, 0, 40, 0, 80 after rounds 2 to 10 when the short knot retires; 5, 5, 10, 15, 25, 40,
65, 105, 170 when it makes offshoots; and 5, 0, 10, 0, 25, 0, 60, 0, 145 when it waits. Through round 6 every knot passed the
parity knot test under FLOOR0 and FLOOR1 with each treatment and under ONE-FEWER with retiring and waiting; under ONE-FEWER
with offshoots the round-1 joins failed from round 4. The thread and then the advisor worked the cycle by hand before the
freeze: P1 to P4, P7 and P10 are expected from that work, P8 and P9 are the advisor's hand predictions, and P5's not-all-equal
test and P6 beyond round 6 are open. Nothing was run on the two small starts, under not-all-equal, with any swap, or on the
census.

## Settled by construction (stated, not tested)

- A **two-knot part** is a part, past its start, of two members that hold two usable loose distinctions each and nothing
  barred, lying in one met set. Under FLOOR0, FLOOR1 and ONE-FEWER its round makes a join j of both members, which receives
  one fresh distinction while two groups will ask it for one, and one offshoot of each member, which receives two. In the next
  round j is short and both groups are cancelled; each offshoot releases its two distinctions as two offshoots that are
  joinable through it and through nothing else: two two-knot parts. What j does is the treatment: it retires; or it makes one
  offshoot, which is a part of one member and makes a two-knot part one round later; or it waits one round, is then asked
  for nothing, and does the same a round later. This is an argument from the definitions; the runs check it.
- On the two small starts below no join has more than two parents and no new knot is asked for by more than two groups, so the
  three rations give the same counts there, every birth receives a fresh distinction, and the closing exception cannot apply.
- A birth that receives a fresh distinction passes the parity knot test when it is made. It can fail later: a join of three
  parents receives none under FLOOR0, and none under ONE-FEWER when at most one group will ask it, and such a birth can close
  off the piece of the structure below an earlier knot, which then fails. That is what the earlier study saw under ONE-FEWER
  with offshoots.

## What is supplied

Everything the earlier study supplied (assumptions A104, A224, A237), and here in particular the three rations, the three
treatments, the release rule, the starts, and the reading of a part as a thing. This ticket swaps the ration, the treatment,
the release rule, the offshoots and the fillers, and runs a census of starts.

## Definitions added

- A part **copies itself** when it returns (as defined) and at least one of the parts that came apart from it is the same as
  it.
- N(t) is the number of two-knot parts after round t, counted from round 0.
- **The two-knot start** is two three-place knots sharing one distinction, stars [0, 1, 2] and [0, 3, 4]. **The three-knot
  start** is a dead knot [0, 1, 2, 3] with two knots [0, 1, 4, 5] and [2, 3, 6, 7], each sharing two distinctions with it;
  its roster is a two-knot part at round 0.
- A run that passes the bound on knots is read through its last complete round.

## Runs (frozen)

Parity unless stated; RELEASE unless stated. A run is cut off at 20,000 knots.

| Run | Starts | Laws | Rounds |
| --- | --- | --- | --- |
| 1 | The two small starts and Ring(5, 3) | FLOOR0, FLOOR1, ONE-FEWER, each with CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT: N(t) after every round; every return of a two-knot part with the parts that came apart | 24 |
| 2 | The two small starts | the same nine laws: parity knot test by both methods and extension test for every knot at every round; under not-all-equal the births compared with parity and the not-all-equal test for every knot | 12; the not-all-equal test to round 10 or 600 knots |
| 3 | Ring(5, 3) | the same nine laws: parity knot test by both methods and extension test for every knot at every round, with the fresh count of every birth | 12 |
| 4 | The two small starts | the rations ORD, CAP-2, CAP-3, RATION-2 and RATION-3 with the three treatments; each of the nine laws with NO-OFFSHOOT, with FILLERS and with HOLD | 16 |
| 5 | Every start of up to five knots of the earlier study's census (3,376 starts, each once up to isomorphism), those passing the knot test | FLOOR0 and FLOOR1, each with the three treatments: whether a part copies itself, and whether any knot fails the parity knot test | 10; 1,500 knots |
| 6 | Ring(5, 3) | (RATION-4, CANCEL-OFFSHOOT), (RATION-4, CANCEL-RETIRE): the parts of seven and nine members that return, described | 12 |

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| Gate | With the earlier study's engine, unchanged: the counts disclosed above for the ring of five come out, and the trace of one two-knot part through two rounds under each treatment matches the settled statement (births, parents, demand, fresh, short). | any fails |
| P1 | Under (FLOOR0, CANCEL-RETIRE), on each of the three starts: every two-knot part returns after two rounds and exactly one part comes apart from it, the same as it; N(t + 2) = 2 N(t) for every t from the round the first two-knot part appears. | a part does otherwise, or a count differs |
| P2 | Under (FLOOR0, CANCEL-OFFSHOOT), on each start, N(t + 2) = 2 N(t) + N(t − 1) for every t at least one round after the first two-knot part appears. | any count differs |
| P3 | Under (FLOOR0, CANCEL-WAIT), on each start, N(t + 2) = 2 N(t) + N(t − 2) for every t at least two rounds after the first two-knot part appears. | any count differs |
| P4 | On the two small starts FLOOR1 and ONE-FEWER give the same roster as FLOOR0 at every round under each treatment, every birth receives a fresh distinction, every knot passes the parity knot test by both methods, every round extends and the closing exception never applies (checks of the settled statements). | any fails |
| P5 | On the two small starts, under the nine laws, the births under not-all-equal equal those under parity and every knot passes the not-all-equal test. | any knot fails |
| P6 | On Ring(5, 3) through round 12: under FLOOR0 and under FLOOR1 every knot passes the parity knot test at every round with each treatment; under ONE-FEWER every knot passes with retiring and with waiting, and with offshoots the round-1 joins fail from round 4. Every knot that fails does so in the round in which a birth without a fresh distinction is made. | any stated case comes out otherwise |
| P7 | In run 4, no part copies itself on either small start through round 16 under ORD, CAP-2, CAP-3 or RATION-2 with any treatment, or under NO-OFFSHOOT. | some part copies itself there |
| P8 | In run 4, under RATION-3 with each treatment, on each small start a part of five members, all holding three, with one member in two met sets of three, returns after one round beside a copy of itself. | no such part copies itself |
| P9 | In run 4, under HOLD with FLOOR0 the two-knot part still copies itself, and for every n late enough N(n) = 2 N(n − 3) + 2 N(n − 4) with retiring, N(n) = 3 N(n − 3) + 2 N(n − 4) with offshoots, and N(n) = 2 N(n − 3) with waiting. | a recurrence fails from round 8 on |
| P10 | With FILLERS added to each of the nine laws, every run on the two small starts has stopped by round 4. | a run has a member after round 4 |
| Reported | Without a prediction: in run 5, how many starts come to contain a part that copies itself and how many come to have a knot that fails the parity knot test, by ration, treatment and number of dead knots, each start counted once (lower bounds, given the bounds on rounds and knots); run 6's parts. | not applicable |

A result that fails is reported as it is. The recurrences of P1 to P3 grow by the square root of two, by the golden ratio and
by the square root of one plus the square root of two a round; if they hold, the result note gives the argument for every
round, marked as an argument for the referee.

## Runs and stop rule

All runs use `engine.py` of `RING-IN-BALANCE-20261123-001A` by import, unchanged. Each run is expected to take under ten
minutes and 4 GB on one process; run 5 (about 20,000 runs) may use eight processes, and goes through the shared runner with a
row in the long-running index only if it would take longer than ten minutes. The study stops when runs 1 to 6 are done and
each prediction has a verdict. Deviations are recorded in `deviations.md` in the experiment family before the affected run.
The advisor model (Claude Fable 5.2) reviewed the first draft cold before this freeze
(`research/COPYING-PARTS-20261123-001/advisor/`): it confirmed the cycle and the three recurrences by hand, found that a fixed
ration of three would make a draft prediction fail (now P8), that "every birth receives a fresh distinction" is false for a
join of three parents under two of the rations (now the third settled statement and P6), and predicted the counts under HOLD
(now P9).
