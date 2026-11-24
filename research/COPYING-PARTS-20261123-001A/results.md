# Parts that copy themselves: result

Ticket `COPYING-PARTS-20261123-001A` (direction 1 of `RING-IN-BALANCE-20261123-001`; G18 with G17), 2026-11-23. Computed with
the earlier study's engine, unchanged; scientific referee pending. [Pre-registration](preregistration.md) ·
[definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ·
[code and its recorded readings](../../experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies/deviations.md) ·
[the thread's side checks](../COPYING-PARTS-20261123-001/checks/)

**The parts that copy themselves are real, simple and common. Under three rations that give a new knot just enough for three
places, with a short knot's joins cancelled, a part of two knots becomes two such parts every two rounds. How fast the copies
multiply is set by what the short knot does: by the square root of two a round if it retires, by the golden ratio if it makes
an offshoot, and by the square root of one plus the square root of two if it waits. Every knot made passes the knot test under
both knot laws on the small starts. Under the ration that always gives a fresh distinction, a part copies itself in 85 to 97
of every hundred starts of up to five knots, and no knot fails. One hand prediction failed: when knots hold instead of
releasing, and the short knot waits, nothing copies and the growth jams.**

## Verdicts

| # | Verdict | What was found |
| --- | --- | --- |
| Gate | Holds | The earlier study's counts on the ring of five come out, and the trace of one two-knot part through two rounds matches the hand argument under each treatment and each ration. |
| P1 | Holds | Retiring: every one of 6,648 two-knot parts followed returns after two rounds with exactly one part coming apart, the same as it; N(t + 2) = 2 N(t) on all three starts to the bound (2,048 parts by round 21). |
| P2 | Holds | Offshoots: N(t + 2) = 2 N(t) + N(t − 1) at every round in range on all three starts. From one two-knot part: 1, 0, 2, 1, 4, 4, 9, 12, 22, 33, 56, 88, 145, 232, 378, 609, 988, 1,596, 2,585. On the ring of five the counts are five times the Fibonacci numbers. |
| P3 | Holds | Waiting: N(t + 2) = 2 N(t) + N(t − 2). From one two-knot part, at even rounds: 1, 2, 5, 12, 29, 70, 169, 408, 985, 2,378, the Pell numbers. |
| P4 | Holds (checks of arguments) | On the two small starts the three rations give identical runs; all 20,697 births receive a fresh distinction; 57,171 knot verdicts pass by both parity methods; every round extends. |
| P5 | Holds | Under not-all-equal the births equal parity's, and 19,113 knot verdicts pass (155,208 solver calls), through round 9 or 10. |
| P6 | Holds | On the ring of five through round 12: under FLOOR0 and FLOOR1 every knot passes with each treatment; under ONE-FEWER every knot passes with retiring and waiting, and with offshoots the five round-1 joins fail from round 4, the one round in which births without a fresh distinction are made (five joins of three parents). |
| P7 | Holds | No part copies itself under ORD, CAP-2, CAP-3 or RATION-2 with any treatment (those twelve laws give one and the same run on the small starts), nor without offshoots. |
| P8 | Holds | Under a fixed ration of three a part of five members, all holding three, one of them in two met sets of three, returns after one round beside a copy of itself, with each treatment and on both small starts. |
| P9 | Holds for two treatments; **fails for the third** | With knots holding instead of releasing, the two-knot part still copies itself with retiring and with offshoots, and both predicted recurrences hold from round 4 to 16. With waiting nothing copies and the run jams by round 6 or 7; the predicted recurrence holds only as 0 = 0. |
| P10 | Holds | With the fillers rule added every run on the small starts has stopped by round 3. |

## The cycle (an argument, checked)

A two-knot part is two members holding two usable loose distinctions each, joinable through one knot. Under FLOOR0, FLOOR1 and
ONE-FEWER:

1. **Round one.** The two join: the join receives one fresh distinction (enough for three places). Each also makes an offshoot,
   which receives two. Two groups will ask the join for a distinction, and it holds one.
2. **Round two.** The join is short, so both groups are cancelled. Each offshoot releases its two distinctions as two
   offshoots, joinable through it and through nothing else: two two-knot parts.
3. **The short join.** If it retires, that is all: one part has become two, and N doubles every two rounds. If it makes an
   offshoot, that offshoot is alone and makes one more two-knot part a round later: N(t + 2) = 2 N(t) + N(t − 1), whose growth
   is the golden ratio a round. If it waits, it is asked for nothing in the next round, makes its offshoot then, and the extra
   part comes two rounds later: N(t + 2) = 2 N(t) + N(t − 2), whose growth is 1 + √2 every two rounds.

Parts that have come apart act alone, so these recurrences hold at every round; that is an argument for the referee. The runs
confirm them to the bound of 20,000 knots, and the pilot's program, which has no distinctions in it, gives the same counts on
all nine combinations of start and treatment ([side check](../COPYING-PARTS-20261123-001/checks/pilot_counts.txt)).

## What the copying needs, and what stops it

| Changed | Result |
| --- | --- |
| The ration: the ordinary count, a cap of two or three, a fixed two | No copying: the join receives what it is asked and is never short; each two-knot part becomes one chain gaining a member a round. |
| The ration: a fixed three | A different, larger copier: a part of five members that copies itself every round. |
| The ration: a fixed four (on the ring) | Parts of seven and of nine members that turn into one another: a seven becomes two nines, and they become six sevens. |
| Offshoots removed | Nothing copies; the growth stops in a round or two. |
| The fillers rule added | Everything stops by round 3. |
| Holding instead of releasing | Copying goes on with retiring (N(n) = 2 N(n − 3) + 2 N(n − 4)) and with offshoots (3 N(n − 3) + 2 N(n − 4)); with waiting it jams. |
| Parity for not-all-equal | The same births; every knot passes. |

So the copying needs a join that receives less than it is asked while offshoots receive more than they are asked, and a
treatment that cancels the join's groups. It does not need waiting, and it does not need the release rule.

## How common it is (reported; lower bounds)

Every start of up to five knots with single meetings, each once up to isomorphism, 3,344 passing the knot test, ten rounds:

| Ration | Short knot | Starts with a part that copies itself | Starts with a knot that fails the knot test |
| --- | --- | --- | --- |
| FLOOR1 | retires | 3,126 (93%) | 0 |
| FLOOR1 | makes offshoots | 3,229 (97%) | 0 |
| FLOOR1 | waits | 2,851 (85%) | 0 |
| FLOOR0 | retires | 2,926 (88%) | 723 |
| FLOOR0 | makes offshoots | 3,254 (97%) | 723 |
| FLOOR0 | waits | 2,776 (83%) | 371 |

The shares are under that one weighting. In every copying run the smallest copier is a two-knot part. Under FLOOR0 every
failing knot fails in a round in which a join of three parents receives nothing; under FLOOR1, where every birth receives a
fresh distinction, none fails. The pilot's program finds a two-knot part by round 8 in 3,141, 3,244 and 2,866 of all 3,376
starts under FLOOR1, the same counts once the 32 starts the engine sets aside are allowed for
([side check](../COPYING-PARTS-20261123-001/checks/census_side_check.txt)).

## What this is, and is not

- **It is a population, not a machine.** The copies never meet again, so their number follows a fixed rule of descent: the
  literature's Fibonacci rabbits and Pell numbers, or a Lindenmayer system without context. A cellular automaton's replicator
  is a different thing: its copies collide.
- **Nothing here combines or reads.** That part of the owner's question is closed off by these laws themselves.
- **It is not ordinary growth.** Every ration and treatment here was added by hand (A224). FLOOR1 is the simplest of them: a
  new knot receives enough for three places and never nothing, and it reads nothing of the round to come.
- **The other phase copies too.** The part of three members between two two-knot parts returns every two rounds beside a copy
  of itself; it is the same population seen a round later.

## Deviations and limits

- **P9** was a hand prediction by the advisor. Its recurrences for retiring and offshoots hold. For waiting it missed that a
  knot that holds stays a member and stays joinable with the offshoots of its own offshoot, so no two-knot part forms.
- **NO-OFFSHOOT with a short knot that makes offshoots.** The engine refuses that pair. The code's author ran it both ways (left
  out, and forced past the engine's check without changing the round); P7 holds either way.
- Readings recorded before the runs are in the
  [deviations](../../experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies/deviations.md); the round
  that passes the bound on knots was read both ways, with the same verdicts.
- Everything is finite: three named starts to 20,000 knots, starts of up to five knots for ten rounds. The not-all-equal test
  stops at round 9 or 10 on the small starts and was not run on the census.
- Evidence class: exact computation with one engine, an argument for the recurrences, and side checks by the thread with the
  pilot's program on the counts.
- Scaffolds: this ticket swapped the ration, the treatment, the release rule, the offshoots, the fillers, the knot law and the
  start. The complete round was not swapped.
