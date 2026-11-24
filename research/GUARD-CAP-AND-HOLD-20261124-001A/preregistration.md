# Does the guard of births made one at a time hold under the cap of three, and when knots hold? Pre-registration

Ticket `GUARD-CAP-AND-HOLD-20261124-001A` of epic `GUARD-CAP-AND-HOLD-20261124-001` (direction 4 of
`LOCAL-ROUND-20261123-001`; goals G5 with G18). Frozen on 2026-11-24, after the advisor's cold review and before the study's code is written. The code is the
engine of the one-birth-at-a-time study, extended by its author from this text and
[the definitions](../GUARD-CAP-AND-HOLD-20261124-001/definitions.md), which extend
[that study's definitions](../LOCAL-ROUND-20261123-001/definitions.md) and
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md). The canonical K1–K3 test is unchanged.

## The question

The one-birth-at-a-time study found a guard under which births made one at a time build what the complete rounds build:
a birth is allowed when every knot of its parents' brood is weaned. It ran a fixed ration of three in place of the cap of
three recorded for the ring that returns, and it did not run knots that hold what their cancelled joins would have taken.
The owner asked on 24 November 2026 for both: "run its guard under the cap of three as recorded for the ring that
returns, and with knots that hold instead of releasing. Stop at a match in every order searched, or at the first
mismatch. Leave the start where a knot that acts meets one that waits for later."

## In standard terms

The same question as the earlier study: whether an asynchronous rule guarded by a local readiness condition reaches what the
synchronous rule builds (in the literature's words, a synchronizer). Two changes to the synchronous rule are tried. Under
the cap, what a new node receives depends on a lookahead among the nodes made with it. Under holding, a node may act in
several steps, so "a node's predecessors have finished" is no longer settled in one step.

## Prior work in the program

Searches, each with `--until 2026-11-24 --exclude GUARD-CAP-AND-HOLD-20261124-001`:

`python3 -B scripts/track.py objects "one birth at a time under the cap of three, the ring that returns, guard on a written record of parents" --until 2026-11-24 --exclude GUARD-CAP-AND-HOLD-20261124-001`

`python3 -B scripts/track.py objects "knots that hold instead of releasing, a parent that gives in two rounds, weaned" --until 2026-11-24 --exclude GUARD-CAP-AND-HOLD-20261124-001`

`python3 -B scripts/track.py objects "fillers rule, barred fresh distinctions, holdings at birth" --until 2026-11-24 --exclude GUARD-CAP-AND-HOLD-20261124-001`

- `LOCAL-ROUND-20261123-001` — the same object: its guards, its comparison and its engine are used here; it left the cap of
  three, the fillers and holding out, and said so.
- `RING-IN-BALANCE-20261123-001` — the same object on the side of the complete rounds: the two and the three added rules,
  the ring that returns, and the finding that with holding the ring jams. Its engine is the reference.
- `TICK-BIRTHS-AND-SCARCITY-20261121-001` — a relative: a guarded serial rule on an eight-knot clock under ordinary growth.
- `GENERATORS-20261120-001` — unrelated (recurring products and a partner-specific meeting under ordinary growth).
- `COPYING-PARTS-20261123-001` — a relative: the swaps of the release rule and of the fillers on the parts that copy
  themselves, under complete rounds.
- `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` — unrelated (a short knot that takes a shared distinction).
- `LOOSE-NAMES-AND-SPENT-JOINS-20261120-001` — unrelated (named births under ordinary growth).

## Prior work outside the program

As the earlier study: synchronizers (Awerbuch 1985) and the stored-previous-state simulation of synchronous by asynchronous
automata (Nakamura 1974; Nehaniv 2004), cited from memory there and not searched further here. What this would add is whether
the same local guard survives a lookahead in what a new knot receives, and a node that acts in several steps.

## Known before the freeze (disclosed)

No prototype of the laws was written. The thread ran the reference engine alone (the complete rounds; nothing serial) on the
registered starts for eight rounds, to choose starts and cutoffs. Births by round, with the number short and the number
staying in brackets. A first version of this table took a round with no birth for an end; under retiring it is not one
(the advisor caught this by hand), and the table below is the corrected run:

| Start | (CAP-3, CANCEL-WAIT, RELEASE) | the same with FILLERS | (CAP-3, CANCEL-WAIT, HOLD) | (RATION-3, CANCEL-WAIT, HOLD) | (FLOOR1, CANCEL-RETIRE, HOLD) | (FLOOR1, CANCEL-OFFSHOOT, HOLD) |
| --- | --- | --- | --- | --- | --- | --- |
| D2(4, 3) | 8, 8 (4 short), 20, 24 (4), 40, 48 (4) | 8, 8 (4), 12, 8 (4), 12, 8 (4) | 8, then nothing more: ended at round 2 (4 short, 4 staying) | 8, 4 (4; 4), 12 (4; 4), 12 (8; 12), 28 (20), ended at round 6 | 8, 0 (4 retire; 4 stay), 8, 12, 8 (4; 8), 24 | 8, 4 (4; 4), 16, 24, 24 (8; 16), 64 |
| Ring(5, 3) | 10, 10 (5), 25, 30 (5), 50, 60 (5) | 10, 10 (5), 15, 10 (5), 15, 10 (5) | 10, ended at round 2 | 10, 5, 15, 15, 35, ended at round 6 | 10, 0, 10, 15, 10, 30 | 10, 5, 20, 30, 30, 80 |
| The cycle of eight with three extra dead knots | 13, 4 (11), 16 (7), 32 (3), 47 (6), 71 | 13, 4 (11), 12 (7), 24 (3), 29 (6), 31 | 13, ended at round 2 | 13, 2, 6, 6, 14, ended at round 6 | 13, 0, 4, 6, 4, 12 | 13, 11, 26, 39, 39, 104 |
| The two-knot start | 4, 6, 8, 10 (no knot short) | 4, 2, stopped | as with RELEASE | not run | 4, 6, 4 (2; 4), 12, 20, 20 (4; 8) | 4, 6, 6 (2; 4), 16, 26, 30 (6; 12) |
| The three-knot start | 3, 4, 5, 6 (no knot short) | 3, 2, 1, stopped | as with RELEASE | not run | 3, 2 (1; 2), 6, 10, 10 (2; 4) | 3, 3 (1; 2), 8, 13, 15 (3; 6) |

- In none of these runs, through round 8, does a join have parents made in two different rounds.
- A parent with children made in two different rounds first appears at round 3 or 4 on the two small starts and at round 6
  on the cycles and the ring, under FLOOR1 with holding.
- Every knot of every one of these structures passes the parity knot test of the reference engine after its last round.
- Hand work by the thread, not run: the trace behind P2 below (the same seven births as under a fixed ration of three), and
  the trace behind P6 (on D2(4, 3) under (RATION-3, CANCEL-WAIT, HOLD) each round-1 offshoot is asked for two joins, both
  cancelled, keeps two distinctions and makes one offshoot; in this study's reading it is then asked for the same two
  joins in every further reading).
- Hand work by the advisor, not run: it reproduced four rows of the table; it confirmed P2's seven births under the cap; it
  showed that under the complete rounds the staying offshoot is asked for five joins in round 4, through its own child,
  which this study's reading leaves out; and it traced the two places where a birth the rounds never make appears (P7
  and P9 below).

## Settled by construction (stated, not tested)

- **The demand among one reading's births** (definitions, section 1): an argument, checked by the gate.
- **Under the cap the guards read what they read before.** A plan's fresh counts depend only on the births of the same
  reading, which lie in the same brood. So the brood argument of the earlier study carries over to the cap with RELEASE,
  and R3 there is a check of that argument.
- **Under holding the brood argument fails**, and the definitions say where: a parent can give in more than one reading, so
  the children of one parent are not all born in one round, and a knot that stays is a member beside its own children.
- **A check, true by construction:** where the reference ends in round 2 with every join waiting and every offshoot
  staying (the cap with holding on the cycles and the ring), every law that plans from the brood reaches the same end.
- **Under holding, R1, R2 and R3 stop early by the definition of weaned**, wherever a stayer has a child: the child's
  parent never stops being a member. P6 is a check of this, and what it hides is tested by the repaired guard R3′.

## What is supplied

Everything the earlier study supplied (assumptions A242 and A243, with A104 and A224), and here the four readings listed in
the definitions, section 4. This ticket swaps the ration (the cap of three for a fixed three), adds the fillers, and swaps
the release rule for holding under four laws. The guard, the record of parents and the start clause are not changed.

## What a result would and would not show

- **A match under the cap** would show that the earlier result holds for the ring that returns as recorded, to the rounds
  searched: the gap named in that study's report would be closed.
- **An early stop under holding** follows from the definition of weaned and shows only that "its parents are no longer
  members" is the wrong test when a parent can stay. **A mismatch under the repaired guard** would show more: that a brood
  is no longer one round's roster when a parent gives in two rounds, or stays beside its children's children. Neither
  shows that no guard works under holding.
- **The cap with holding**, the owner's literal case, tests little on these starts (definitions, section 5), and the result
  will say so.
- As before, nothing here shows that the round can be done without, or that the record of parents can be.

## Runs (frozen)

Parity. Orders, the match, the cutoff and the gate are those of the earlier study's definitions, section 4, with the two
changes of this study's definitions, section 3, items 6 and 7. Caps: two million states for a search over every order, with
no time budget; a search that reaches its cap is reported as unfinished with the number of births to which every order was
searched.

1. **The gate.** The engine's own complete rounds, computed through the plan, under each law below against the reference
   engine, structure by structure, rounds 1 to 6 (or to the round the growth ends), with fresh counts, the demand D of
   every birth, usable and barred counts and stayers compared. Three altered controls must be rejected: RELEASE for HOLD
   (on D2(4, 3) under a fixed ration of three with waiting, where knots are short), a fixed three for the cap, and the
   fillers left out. The start clause's condition is asserted for every start and law.
2. **The cap.** Laws (CAP-3, CANCEL-WAIT, RELEASE) and the same with FILLERS. Starts D2(4, 3), D2(5, 3), Ring(5, 3), the
   cycle of eight with three extra dead knots (its stars are in the earlier study's pre-registration), the two-knot and
   three-knot starts. Guards R1, R2, R3 and the control. Cutoff round 1: every order, 200 sampled orders, every x-last
   order. Cutoff round 3: 200 sampled and every x-last order, and every order to the cap.
3. **The distance under the cap.** T(d) for d = 2 to 6 on D2(4, 3) and D2(6, 3) under (CAP-3, CANCEL-WAIT, RELEASE), cutoff
   round 1, the three kinds of order.
4. **Holding.** Laws (CAP-3, CANCEL-WAIT, HOLD), (RATION-3, CANCEL-WAIT, HOLD), (FLOOR1, CANCEL-RETIRE, HOLD) and
   (FLOOR1, CANCEL-OFFSHOOT, HOLD). Starts D2(4, 3), Ring(5, 3), the two-knot and three-knot starts. Guards R1, R2, R3, the
   repaired guard R3′ and the control. Cutoffs round 1, 2 and 3, and round 4 on the two small starts: every order to the
   cap, 200 sampled orders, every x-last order.
5. **The knot test.** No law here makes a knot the complete rounds do not, unless it mismatches. Every knot of the
   reference structure after its last compared round is tested for every start and law, under parity by both methods and,
   for structures of up to 600 knots, under not-all-equal with the births compared with parity's. A knot made at a mismatch
   is tested in the structure in which it was made.
6. **Reported in every run:** counts of orders that match, mismatch and underbuild; the least number of births to a
   mismatch, exact or found; for an order that underbuilds, the first reference knot never made and why its birth was not
   allowed; every roster used that has a group of three or more.

## Predictions (frozen)

Hand predictions that were not run are marked (b), with whose hand; a check is true by construction; (c) is open.

| # | Prediction | Fails when |
| --- | --- | --- |
| Gate | The engine's complete rounds equal the reference's under every law of the runs, D included, and the three altered controls are rejected. | any fails |
| P1 (b, the thread's; near a check of the brood argument) | Under (CAP-3, CANCEL-WAIT, RELEASE), R3 builds what the complete rounds build on every start: in every order through round 1 where the search finishes, and in every sampled and x-last order through round 3. | an order mismatches or underbuilds |
| P2 (b, the thread's, confirmed by the advisor's hand) | Under the same law R1 differs on D2(4, 3), D2(5, 3) and Ring(5, 3) with a least differing order of exactly 7 births, a waiter's surplus offshoot, as under a fixed ration of three. On the two small starts, where no knot is short, R1 matches. | the least is not 7, or R1 differs on a small start |
| P3 (b for the verdicts; c for the number) | Under the same law R2 matches on D2(4, 3), D2(5, 3) and Ring(5, 3) through round 1, and differs on the cycle of eight with three extra dead knots. Its least number of births there is reported; under a fixed three it was 13, and that number is not derived for the cap. | R2 differs on the first three, or matches on the fourth |
| P4 (b, the thread's) | The least d at which T(d) has no mismatch under the cap is 4 on D2(6, 3). On D2(4, 3) four steps reach everything, so its 4 is a check. | it is not 4 on D2(6, 3) |
| P5 (b, the thread's) | With FILLERS added, R3 builds what the complete rounds build on every start, through the same cutoffs. | an order mismatches or underbuilds |
| P6 (a check, by the definition of weaned) | Holding, where a stayer has a child: on D2(4, 3) and Ring(5, 3) under (RATION-3, CANCEL-WAIT, HOLD), R1, R2 and R3 match through round 1 and underbuild through round 2. The first reference knots never made are the offshoots of the children of the round-1 offshoots; they are never allowed because their parents' parent stays for ever. | a law matches through round 2 there, or mismatches before it underbuilds |
| P7 (b, the advisor's) | The repaired guard under the same law: R3′ matches through round 2 and mismatches through round 3, with a least differing order of exactly 13 births on D2(4, 3) and 15 on Ring(5, 3): the eight (or ten) births of the start, one child of a staying offshoot, its three offshoots, and then one offshoot of one of those, which the complete rounds never make because that knot keeps a distinction for its cancelled join with the stayer. | R3′ matches through round 3, or the least is not 13 and 15 |
| P8 (a check) | Under (CAP-3, CANCEL-WAIT, HOLD) on D2(4, 3) and Ring(5, 3), where the reference ends in round 2, R1, R2, R3 and R3′ match at every cutoff. On the two small starts no knot is short under the cap, so the runs equal those with RELEASE. | a law differs |
| P9 (b, the advisor's) | On the two-knot start under (FLOOR1, CANCEL-RETIRE, HOLD) and (FLOOR1, CANCEL-OFFSHOOT, HOLD): R1, R2 and R3 match through rounds 1 and 2 and underbuild through round 3. Through round 4 the brood of a stayer's children of two different rounds plans a join of two of them, which the complete rounds never make; R3′ mismatches there. | R3 matches through round 3; or R3′ matches through round 4 |
| P10 (b, the advisor's) | On D2(4, 3) under (FLOOR1, CANCEL-OFFSHOOT, HOLD): R3 and R3′ match through round 3 (a parent with children of two rounds first appears later). | either differs through round 3 |
| P11 (c) | Everything else under holding: the three-knot start; D2(4, 3) and Ring(5, 3) under (FLOOR1, CANCEL-RETIRE, HOLD); Ring(5, 3) under (FLOOR1, CANCEL-OFFSHOOT, HOLD); R1 and R2 wherever R3 is predicted. Reported. | not applicable |
| P12 (c) | The control under every law here. Reported. | not applicable |

A result that fails is reported as it is.

## Runs and stop rule

- **One engine.** The earlier study's engine, extended by its author from this text. There is no second program here; the
  checks on it are the gate against the reference, with D compared, and the earlier study's unit tests, which must still
  pass.
- **Stop**, in the owner's words: at a match in every order searched, or at the first mismatch. Read for each law family:
  the cap stops at R3's verdict under P1 and P5. Holding stops, for each of the four laws, at the first mismatch of R3 or
  of R3′, or at a match through the last cutoff. An early stop of R3 under holding follows from the definition of weaned
  (P6) and is not counted as the mismatch asked for; that is why the repaired guard is run. The study stops when every
  registered run is done and every prediction has a verdict.
- **Resources.** Each search under ten minutes and 8 GB on one process where it can be; a search expected to take longer
  goes through a background unit with a memory cap and a row in the long-running index. No time budget replaces a cap.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor** (Claude Fable 5.2, no tools) reviewed this text cold before the freeze
  (`../GUARD-CAP-AND-HOLD-20261124-001/advisor/`). It reproduced four rows of the disclosed table by hand and corrected a
  fifth (a round with no birth is not an end when knots retire). It showed that the early stop under holding is true by
  the definition of weaned and hides the real fault, and proposed the repaired guard with a hand prediction (P7). It found
  that under the complete rounds a staying knot is asked for joins through its own child, which this study's reading
  leaves out; that the cap with holding tests little on these starts; and that "holder" was already the record's word, so
  the knot that stays is a "stayer" here.
