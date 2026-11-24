# The ring in balance on real knots: result

Ticket `RING-IN-BALANCE-20261123-001A` (sub-goal B315; G18 with G17 and G5), 2026-11-23. Computed with an engine written from
the frozen text alone; scientific referee pending. [Pre-registration](preregistration.md) ·
[shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ·
[code and its recorded readings](../../experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/deviations.md) ·
[the thread's comparison with the pilot's programs](../RING-IN-BALANCE-20261123-001/checks/compare_pilot.py)

**The pilot's result holds on real knots. Under the two added rules a ring of an odd number of knots, five or more, comes back
to its start's roster every two rounds and the same two-knot part comes apart from it n at a time; under the three, the roster
is in balance. Every knot passes the knot test under parity and under not-all-equal. The return does not need a cap of three:
every cap from three to seven gives one, with larger parts coming apart. It does need the waiting, the release of what
cancelled joins would have taken, and the offshoots: swap any of the three and the ring stalls, jams, or returns giving nothing
off. One prediction failed: small parts of one to three knots that copy themselves appear under other laws, some of them
without waiting.**

## Verdicts

| # | Verdict | What was found |
| --- | --- | --- |
| G | Holds, with one noted difference | The engine gives the record's ordinary counts for the ring of five, the bare ring and the seven-knot generator; no part comes apart in 34 ordinary runs; the hand trace of rounds 1 and 2 and the stall under STALL come out; its round agrees with a naive second implementation on 4,051 rounds and its knot tests with brute force on 305 structures. Against the pilot's two programs, the members, parts, loose counts and met sets agree on every round of all 42 runs of A1 with one program and of 41 with the other; the one difference is Ring(3, 3) under ordinary growth at round 7, where it closes and the thread's pilot program, which has no closing exception, goes on. |
| P1 | Holds | 36 cases, odd n from 5 to 15, even rounds 2 to 12: the n knots that waited form one part, the same as the start's roster. |
| P2 | Holds | 30 cases (rounds 2 to 10; round 12 would need round 14): n + 1 parts, one the same, n of two members with two usable loose distinctions in one met set. |
| P3 | Holds as meant; fails as worded | The two-member parts of P2, 126 followed, are all the same s rounds later and have s + 2 members, s = 0 to 10. As worded the prediction also covers the parts of the first return found, which is the part of 2n members after round 1 returning at round 3 with three-member parts beside it; those are one round older and have s + 3. The reading was recorded before the run. |
| P4 | Holds | In balance from round 1 with period two through round 20: 2n members in one part, then 3n in n + 1 parts. Every part that came apart made one knot with no usable distinction and ended (45 to 135 such parts per ring). |
| P5 | Holds | Rings of 4 and 6: no return giving parts off. Rings of 8 to 16: two parts, each returning every two rounds and giving n/2 off. The ring of 3 (no prediction) grows with no return. |
| P6 | Holds (a check of an argument) | 62,280 knot tests by each of the two methods, in agreement; all 144 rounds extend. |
| P7 | Holds | The closing exception never applies; births under not-all-equal equal those under parity through round 12; 1,848 knots pass the not-all-equal test through round 6 (28,032 solver calls). |
| P8 | **Fails** | (a) Parts of one to three members that return giving parts off appear under FLOOR0, FLOOR1 and ONE-FEWER with CANCEL-OFFSHOOT and CANCEL-RETIRE, and parts of seven or nine members under RATION-4 with the same two treatments: 24 of the 180 runs that (a) covers, none of them with waiting. (b) FLOOR0 and FLOOR1 with CANCEL-WAIT have such small parts too. What the prediction was about does hold: a part of n or 2n members returns giving parts off only with CANCEL-WAIT and offshoots, under CAP-3, CAP-4, ONE-FEWER, RATION-3 and (reported) RATION-4, on all three rings. |
| P9 | Holds | A ring with two loose distinctions on every knot has the same roster after every round. Reported: with four, the ring returns giving parts off under the two added rules and settles into the same balance under the three from round 6; with five, it jams in round 2, every member short. |
| P10 | Holds | With HOLD in place of RELEASE no birth is made after round 1: the joins wait, the offshoots keep what the cancelled joins would have taken, and the roster never changes again. |
| P11 | Holds | For every cap k from 3 to 7 a part of n members with k usable loose distinctions each first appears after round k − 1 and returns every two rounds. The parts that come apart have 2, 5, 9, 14 and 20 members, which is (k − 2)(k + 1)/2. For k of 5 and more the runs reached the bound of 20,000 knots after two to four returns. |

## What the swaps show

Each added rule is a scaffold (A224). Swapped one at a time on rings of 5, 7 and 9 knots:

| Swapped | For | What happens to the ring |
| --- | --- | --- |
| The cap of three | caps of four to seven; a fixed three or four; one fewer than asked | Still returns giving parts off. The cap sets how much each ring knot holds and how large the parts are. |
| The cap of three | a cap or fixed ration of two | Returns every round giving nothing off (the bare ring). |
| The cap of three | no cap (the ordinary count) | No shortage, so no waiting: the golden-ratio eddy. |
| Waiting | the whole round stalls | Stalls in round 2. |
| Waiting | the short knot makes offshoots, or retires | Grows with no ring-sized return. |
| Releasing what cancelled joins would have taken | holding it | Jams in round 2 for good. |
| Offshoots | none | Returns giving nothing off, or jams. |
| The fillers | absent | The parts that come apart grow by one member a round instead of ending. |
| Parity | not-all-equal | The same births; every knot passes. |

So the return with parts is a result about waiting together with release and offshoots. It is not sensitive to the ration, and
it is not a property of ordinary growth, where no knot waits. No other rule that makes the parts end is known, so the fillers
were swapped only against their absence.

## The argument for every odd ring (for the referee)

The runs prove P1 and P2 only for the rings they cover. For a ring of odd n ≥ 5 under the two added rules:

1. **Round 1.** Knot i is the common knot of i − 1 and i + 1, so the joinable pairs form one cycle (n is odd) with no three
   pairwise joinable (n ≠ 3). Each knot is in two groups and holds three, so none is short: n joins J_i with parents i − 1 and
   i + 1, and n offshoots O_i. After the round the dead knot i meets J_{i−1}, J_{i+1} and O_i, a met set of three, and no three
   members are pairwise joinable across different met sets (that would need n to divide 4 or 6). So every group to come is a
   pair: a join is in four and receives min(4, 3) = 3; an offshoot is in two and receives two.
2. **Round 2.** Every join owes four and holds three, so it is short and waits, and every group contains a join, so all are
   cancelled. Each offshoot is not short and releases its two distinctions as two offshoots of its own, which are joinable to
   each other through it and to nothing else; each receives two. After the round the waiting joins are met in pairs by the dead
   ring knots, in one cycle, each holding three: the start's roster. Beside them are n parts of two members holding two each.
   No member meets a member.
3. **Round 3.** The waiting joins now do what the start did in round 1, with the dead ring knots as common knots; their met
   sets afterwards are again triples of two joins and an offshoot. So the roster of their descendants after round 3 is the same
   as the whole roster after round 1, and both are past the start.
4. **For ever.** Past the start the roster decides the round and parts act alone (pre-registration, settled statements). So
   the part of step 3 repeats steps 2 and 3 without end, giving off n two-member parts every two rounds.

For even n the joinable pairs form two cycles of n/2, and the same steps go through when n/2 ≥ 4; n/2 = 3 has three pairwise
joinable members and n/2 = 2 is degenerate, which is where the rings of 6 and 4 fail. This is an argument, not a refereed
proof.

## Not predicted

- **Parts that copy themselves.** Under FLOOR0 with any cancelling treatment, a part of two members returns after two rounds
  beside a copy of itself, so the number of such parts doubles every two rounds (5, 10, 20, 40, 80 under CANCEL-RETIRE in the
  pilot's program, which was run afterwards as a second check). Under FLOOR0 with CANCEL-OFFSHOOT the members number 10, 15,
  25, 40, 65, 105, …, five times the Fibonacci numbers, in 10, 10, 20, 30, 50, 80, … separate parts: the golden ratio again,
  this time as a count of small parts and not of one growing part (the engine and the pilot's program agree on every round
  to 10; [spot checks](../RING-IN-BALANCE-20261123-001/checks/spot_checks.txt)). In Conway's Life the literature calls a
  pattern that makes copies of itself a replicator. These came from the swap table, not from a search, and nothing more is
  known about them yet.
- **Under ONE-FEWER with CANCEL-OFFSHOOT a knot fails the knot test.** A join of three parents asked for at most once receives
  nothing; from round 4 the round-1 joins fail by both methods and the round does not extend. It is the only failure in 210
  runs, and it is where the argument says a failure can be: a birth that receives nothing.
- **Returns at odd rounds.** The part of 2n members after each odd round also returns every two rounds; it is the same clock
  read half a period later.

## Deviations and limits

- The engine's author recorded 22 readings of the frozen text before or beside the runs
  ([deviations](../../experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/deviations.md)). Two bear on
  verdicts: which parts P3 follows, and that P8 counts any part that returns, of whatever size. Both readings are reported.
- The gate's comparison with the pilot's programs was made by the thread
  ([script](../RING-IN-BALANCE-20261123-001/checks/compare_pilot.py),
  [output](../RING-IN-BALANCE-20261123-001/checks/compare_pilot.txt)); the pilot's programs are private workspace files.
- Everything is finite: rings of 3 to 16 knots, 12 to 20 rounds, at most 20,000 knots. The not-all-equal test stops at round 6.
- Evidence class: exact computation, with an argument for periodicity. The pilot's counts were known before the freeze, so P1
  to P5 test the code and the real knots; P7, P10, P11 and the swap table are new.
- Scaffolds: the complete round was not swapped here (ticket C), nor the start beyond rings (ticket B).
