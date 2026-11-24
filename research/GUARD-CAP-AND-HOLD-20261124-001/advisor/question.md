You are the design advisor for two small pre-registered computational studies in a research program on "knot growth". Review both designs COLD, before they are frozen. You have no tools; everything is below. Do hand work where it helps and say that it is hand work. Be adversarial: I would rather learn that a prediction is wrong or a definition unusable now.

Background. Growth proceeds in complete rounds (shared definitions, item 5 below). An earlier study (its definitions are item 4) made births one at a time under guards read from a written record of parents: a knot is "weaned" when none of its parents is still a member; its "brood" is the closure under taking all children of each parent; the guard R3 allows a birth when the brood of its parents is all-weaned and plans it by replaying the round on the brood's roster at birth. R3 matched the complete rounds in every order searched under (RATION-3, CANCEL-WAIT, RELEASE), (FLOOR1, CANCEL-RETIRE or CANCEL-OFFSHOOT, RELEASE) and (ORD, STALL). The owner now asks for two follow-ups.

Word rules of the program: one word for each meaning; no words from a space of two or three dimensions for the program's own objects; a new word must not reuse a stem the record uses otherwise or have a settled outside meaning the program might cite in another sense.

## STUDY ONE (items 1 and 2): the guard under the cap of three, with the fillers, and under holding

Answer under these numbers, in short lines:
1.1 Is the reading of CAP-3's demand D among one reading's births right (definitions section 1)? Check it against the shared definitions' step 6, including under the waiters' recursion and at the start. Is anything else needed for CAP-3 that the earlier definitions did not need?
1.2 FILLERS: is "holdings at birth = places less parents less places barred at birth" right, and is the match rule sound? Under FILLERS the usable count is min(f, D): is D available to a serial law at the moment of a birth?
1.3 HOLD: is the reading in section 3 the minimal honest extension? Is the stopping rule "at rest" right (can a part be read again for ever without being at rest)? Check my hand claim behind P6 on D2(4,3) under (RATION-3, CANCEL-WAIT, HOLD): round 1 makes 4 joins and 4 offshoots; in round 2 the joins are short and wait, each offshoot (holding 3, asked for two joins, both cancelled) keeps 2 and makes 1 offshoot c; under the complete rounds c makes 3 offshoots in round 3; under R1, R2, R3 as frozen c is never weaned because its parent holds for ever, so the laws underbuild through round 2. Is that right? Where would a MISMATCH (a birth the rounds never make) appear under holding, if anywhere?
1.4 Predictions P1 to P9: which are true by construction, which cannot be decided by the registered runs, which do you expect to fail? In particular P2 (R1 fails at exactly 7 births under the cap, as under a fixed three) and P3 (R2 fails at exactly 13 births on the cycle of eight with three extra dead knots under the cap): under CAP-3 an offshoot receives 2 where a fixed ration gives 3; does that change either count?
1.5 The owner asked: "run its guard under the cap of three as recorded for the ring that returns, and with knots that hold instead of releasing. Stop at a match in every order searched, or at the first mismatch." Is anything he asked for missing, and is it honest to stop at an early stop (underbuild) under holding without registering a repaired guard? If a one-line repair is natural, state it precisely enough to register as a second law with an open prediction.
1.6 Words: holder; the roster of those that still hold; at rest.

## STUDY TWO (item 3): can a knot tell its parents from its children by what is built around it?

2.1 Is "what is looked at within d holder steps" a complete and usable definition (boundary places, marks)? Is "confusable pair" the right formalisation of the owner's "pairs of knots that agree on everything within d holder steps but differ in who their parents are"? Should the test be per chosen place (as drafted) or per knot (the whole set of parent places)?
2.2 Is the certification sound both ways? Any trap in comparing looks across structures of one law but different starts or rounds?
2.3 Hand work wanted: under (FLOOR1, CANCEL-OFFSHOOT, RELEASE) from the two-knot start [[0,1,2],[0,3,4]], and under (RATION-3, CANCEL-WAIT, RELEASE) on D2(4,3), can you exhibit a confusable pair at distance 2 or 3 deep inside the structure, or argue that a local rule recovers the parents (for example from the cycle of four holder steps made by two parents, their common knot and their join, where the common knot and the join sit across from each other)? State your expectation for P2 and P3.
2.4 The populations: are P1 and P2 the right ones for the owner's "structures already built"? Does the stop rule's reading of "a pair no bounded reading tells apart" hold up? What would make the result an artifact?
2.5 Predictions: true by construction, undecidable, expected to fail?
2.6 Words: "look" (what is looked at within d), "agree", "confusable pair", "parent place / child place / start place", "a rule recovers the parents".


# (1) STUDY ONE: DRAFT DEFINITIONS

# The guard under the cap of three and under holding: definitions

Epic `GUARD-CAP-AND-HOLD-20261124-001` (direction 4 of `LOCAL-ROUND-20261123-001`; goals G5 with G18). Frozen with the
pre-registration of ticket A, before any of the study's code is written. It extends
[the definitions of the one-birth-at-a-time study](../LOCAL-ROUND-20261123-001/definitions.md) ("LR" below, cited by
section) and [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("the shared definitions", cited by
line), and changes nothing in either for the laws they already cover. Every word keeps its meaning there: member, short,
waits, retires, part, weaned, brood, all-weaned, all-short, status, acting roster, waiters' roster, a barring, allows,
cutoff, matches through round r, underbuilds, x-last order. Three are new: **holder**, **the roster of those that still hold** and
**at rest** (section 3).

## 1. The cap of three in a plan

LR section 2.1, step 4, gains one line:

- **CAP-3**: f = min(max(D, 3 − p, 1), 3), with D read exactly as LR reads it for ORD: the number of groups containing the
  birth in a roster whose members are the births planned in the same reading, each with holding 1, and whose met sets are,
  for each member of that reading's roster, the births it is a parent of, when there are at least two.
- **Why only the births of that reading** (an argument for the referee). The shared definitions' demand (lines 55–58) also
  keeps the old members that still hold something. Past the start, under RELEASE, the only such members are waiters; a
  waiter meets only its parents and a new knot meets only its parents, which are other knots, so no knot meets both and
  no group holds both. The gate checks every fresh count against the reference.
- The laws: **the two added rules** are (CAP-3, CANCEL-WAIT, RELEASE), as recorded for the ring that returns (shared
  definitions line 70).

## 2. The fillers

The extra FILLERS (shared definitions line 67): of a new knot's f fresh distinctions, min(f, D) are usable and the rest are
barred at birth. **The three added rules** are the two with FILLERS.

- **Holdings at birth under FILLERS.** h₀(x) is the number of places x received at birth that were usable then: its places,
  less its parents, less its places that were barred at birth. Under (CAP-3, CANCEL-WAIT, RELEASE, FILLERS) nothing but
  the fillers bars a distinction, and a barred distinction is never taken, so "barred at birth" is read from the structure
  as x's loose barred places. For a start knot h₀ is as in LR.
- **A birth under FILLERS** is allowed with its fresh count f and its number of usable fresh distinctions min(f, D), both
  read from the plan. It **matches** (LR section 4) when the reference has a knot, not yet an image, with the same images
  of parents, the same f and the same number of places barred at birth.
- No barring (LR section 2.4, step 4) is made under this law: nothing retires.

## 3. Holding

HOLD (shared definitions lines 51–54): a member that is not short, after paying its kept groups, keeps the distinctions its
cancelled groups would have taken and makes offshoots only from the rest. The plan of LR section 2.1 is read under HOLD as
follows; everything not mentioned is unchanged.

1. **Step 3 under HOLD.** A member that is not short has as many planned offshoots as its holding less all its groups,
   kept and cancelled. It keeps one usable distinction for each of its cancelled groups. If it keeps at least one it is a
   **holder** in this reading: it has acted, and it is still a member.
2. **Step 5 under HOLD, for every cancelling treatment.** The **roster of those that still hold** of a roster has as members
   its waiters, with holdings unchanged, and its holders, each with what it kept. Its met sets are the roster's met sets
   intersected with those members, kept when they have at least two. It takes the place of the waiters' roster: each of
   its parts is read a second time by steps 1 to 5, and so on.
   - A reading of a part that plans no birth and no retirement leaves the part as it was, so reading it again gives the
     same. Such a part is **at rest**: its members make no births for ever, and the recursion stops there. An all-short
     part is the case in which every member is short; under holding a part can also be at rest with some members
     waiting and the others holding.
   - Under CANCEL-RETIRE and CANCEL-OFFSHOOT a short member retires or spends everything, so only holders are carried on.
3. **Planned births of a member** are the births of every reading in which it acts that have it among their parents. A
   holder can act in several readings.
4. **The reading is a reading** (a scaffold, stated before the runs). Under the complete rounds a holder is a member of
   the live roster beside the new knots. It meets its own children, so a child of one of its children can be joinable
   with it through that child. The rule above reads a holder again only against the others of its own brood that still
   hold, and so leaves any such group out.
5. **Weaned is unchanged**: a knot is weaned when none of its parents is a member of the present roster. Under HOLD a
   parent that has made a birth may still be a member, and may stay one for ever. The guards R1, R2 and R3 are run with
   this meaning, as frozen. Nothing is repaired in this study.

## 4. What is supplied by hand (scaffolds)

Everything LR lists in its section 5 (the parent relation, A242; the start clause and the rule for a second reading, A243;
the guards; the comparison), and here: the reading of the demand among one reading's births; the reading of holdings at
birth under the fillers; the rule that a holder reads again with those of its brood that still hold; and the choice to
leave "weaned" as it is under holding.


# (2) STUDY ONE: DRAFT PRE-REGISTRATION

# Does the guard of births made one at a time hold under the cap of three, and when knots hold? Pre-registration

Ticket `GUARD-CAP-AND-HOLD-20261124-001A` of epic `GUARD-CAP-AND-HOLD-20261124-001` (direction 4 of
`LOCAL-ROUND-20261123-001`; goals G5 with G18). Frozen on 2026-11-24, before the study's code is written. The code is the
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
holding in brackets:

| Start | (CAP-3, CANCEL-WAIT, RELEASE) | the same with FILLERS | (CAP-3, CANCEL-WAIT, HOLD) | (RATION-3, CANCEL-WAIT, HOLD) | (FLOOR1, CANCEL-RETIRE, HOLD) | (FLOOR1, CANCEL-OFFSHOOT, HOLD) |
| --- | --- | --- | --- | --- | --- | --- |
| D2(4, 3) | 8, 8 (4 short), 20, 24 (4), 40, 48 (4) | 8, 8 (4), 12, 8 (4), 12, 8 (4) | 8, then jammed at round 2 (4 short, 4 holding) | 8, 4 (4; 4), 12 (4; 4), 12 (8; 12), 28 (20), jammed at round 6 | 8, jammed at round 2 | 8, 4 (4; 4), 16, 24, 24 (8; 16), 64 |
| Ring(5, 3) | 10, 10 (5), 25, 30 (5), 50, 60 (5) | 10, 10 (5), 15, 10 (5), 15, 10 (5) | 10, jammed at round 2 | 10, 5, 15, 15, 35, jammed at round 6 | 10, jammed at round 2 | 10, 5, 20, 30, 30, 80 |
| The cycle of eight with three extra dead knots | 13, 4 (11), 16 (7), 32 (3), 47 (6), 71 | 13, 4 (11), 12 (7), 24 (3), 29 (6), 31 | 13, jammed at round 2 | 13, 2, 6, 6, 14, jammed at round 6 | 13, jammed at round 2 | 13, 11, 26, 39, 39, 104 |
| The two-knot start | 4, 6, 8, 10 (no knot short) | 4, 2, stopped | as with RELEASE | not run | 4, 6, 4 (2; 4), 12, 20, 20 (4; 8) | 4, 6, 6 (2; 4), 16, 26, 30 (6; 12) |
| The three-knot start | 3, 4, 5, 6 (no knot short) | 3, 2, 1, stopped | as with RELEASE | not run | 3, 2 (1; 2), 6, 10, 10 (2; 4) | 3, 3 (1; 2), 8, 13, 15 (3; 6) |

- In none of these runs, through round 8, does a join have parents made in two different rounds.
- A parent with children made in two different rounds first appears at round 3 or 4 on the two small starts and at round 6
  on the cycles and the ring, under FLOOR1 with holding.
- Every knot of every one of these structures passes the parity knot test of the reference engine after its last round.
- Hand work by the thread, not run: the trace behind P2 below (the same seven births as under a fixed ration of three), and
  the trace behind P6 (on D2(4, 3) under (RATION-3, CANCEL-WAIT, HOLD) each round-1 offshoot is asked for two joins, both
  cancelled, keeps two distinctions, makes one offshoot and is then asked for the same two joins in every later reading).

## Settled by construction (stated, not tested)

- **The demand among one reading's births** (definitions, section 1): an argument, checked by the gate.
- **Under the cap the guards read what they read before.** A plan's fresh counts depend only on the births of the same
  reading, which lie in the same brood. So the brood argument of the earlier study carries over to the cap with RELEASE,
  and R3 there is a check of that argument.
- **Under holding the brood argument fails**, and the definitions say where: a parent can give in more than one reading, so
  the children of one parent are not all born in one round, and a holder stays a member beside its own children.
- **A check, true by construction:** where the reference jams in round 2 with no birth (the cap with holding on the ring
  starts), every law that plans from the brood reaches the same end.

## What is supplied

Everything the earlier study supplied (assumptions A242 and A243, with A104 and A224), and here the four readings listed in
the definitions, section 4. This ticket swaps the ration (the cap of three for a fixed three), adds the fillers, and swaps
the release rule for holding under four laws. The guard, the record of parents and the start clause are not changed.

## What a result would and would not show

- **A match under the cap** would show that the earlier result holds for the ring that returns as recorded, to the rounds
  searched: the gap named in that study's report would be closed.
- **A mismatch or an early stop under holding** would show that "its parents have finished giving" is the wrong test when a
  parent can give more than once. It would not show that no guard works there: nothing is repaired in this study.
- As before, nothing here shows that the round can be done without, or that the record of parents can be.

## Runs (frozen)

Parity. Orders, the match, the cutoff and the gate are those of the earlier study's definitions, section 4. Caps: two million
states for a search over every order, with no time budget; a search that reaches its cap is reported as unfinished with the
number of births to which every order was searched.

1. **The gate.** The engine's own complete rounds under each law below against the reference engine, structure by
   structure, rounds 1 to 6 (or to the round the growth ends), with fresh counts, usable and barred counts and holders
   compared. Three altered controls must be rejected: RELEASE for HOLD, a fixed three for the cap, the fillers left out.
2. **The cap.** Laws (CAP-3, CANCEL-WAIT, RELEASE) and the same with FILLERS. Starts D2(4, 3), D2(5, 3), Ring(5, 3), the
   cycle of eight with three extra dead knots, the two-knot and three-knot starts. Guards R1, R2, R3 and the control.
   Cutoff round 1: every order, 200 sampled orders, every x-last order. Cutoff round 3: 200 sampled and every x-last
   order, and every order to the cap.
3. **The distance under the cap.** T(d) for d = 2 to 6 on D2(4, 3) and D2(6, 3) under (CAP-3, CANCEL-WAIT, RELEASE), cutoff
   round 1, the three kinds of order.
4. **Holding.** Laws (CAP-3, CANCEL-WAIT, HOLD), (RATION-3, CANCEL-WAIT, HOLD), (FLOOR1, CANCEL-RETIRE, HOLD) and
   (FLOOR1, CANCEL-OFFSHOOT, HOLD). Starts D2(4, 3), Ring(5, 3), the two-knot and three-knot starts. Guards R1, R2, R3 and
   the control. Cutoffs round 1, round 2 and round 3: every order to the cap, 200 sampled orders, every x-last order.
5. **The knot test.** No law here makes a knot the complete rounds do not, unless it mismatches. Every knot of the
   reference structure after its last compared round is tested for every start and law, under parity by both methods and,
   for structures of up to 600 knots, under not-all-equal with the births compared with parity's. A knot made at a mismatch
   is tested in the structure in which it was made.
6. **Reported in every run:** counts of orders that match, mismatch and underbuild; the least number of births to a
   mismatch, exact or found; for an order that underbuilds, the first reference knot never made and why its birth was not
   allowed; every roster read with a group of three or more.

## Predictions (frozen)

All are hand predictions that were not run, marked (b), except where marked a check or (c), open.

| # | Prediction | Fails when |
| --- | --- | --- |
| Gate | The engine's complete rounds equal the reference's under every law of the runs, and the three altered controls are rejected. | any fails |
| P1 (b; a check of the brood argument) | Under (CAP-3, CANCEL-WAIT, RELEASE), R3 builds what the complete rounds build on every start: in every order through round 1 where the search finishes, and in every sampled and x-last order through round 3. | an order mismatches or underbuilds |
| P2 (b) | Under the same law R1 differs on D2(4, 3), D2(5, 3) and Ring(5, 3) with a least differing order of exactly 7 births, a waiter's surplus offshoot, as under a fixed ration of three. On the two small starts, where no knot is short, R1 matches. | the least is not 7, or R1 differs on a small start |
| P3 (b) | Under the same law R2 matches on D2(4, 3), D2(5, 3) and Ring(5, 3) through round 1 and differs on the cycle of eight with three extra dead knots, with a least differing order of exactly 13 births. | R2 differs on the first three, matches on the fourth, or the least is not 13 |
| P4 (b) | The least d at which T(d) has no mismatch under the cap is 4 on D2(4, 3) and on D2(6, 3). | it is not 4 |
| P5 (b) | With FILLERS added, R3 builds what the complete rounds build on every start, through the same cutoffs. | an order mismatches or underbuilds |
| P6 (b) | Holding, where a holder has a child: on D2(4, 3) and Ring(5, 3) under (RATION-3, CANCEL-WAIT, HOLD), R1, R2 and R3 match through round 1 and underbuild through round 2. The first reference knots never made are the offshoots of the children of the round-1 offshoots; they are never allowed because their parents' parent holds for ever and so they are never weaned. | a law matches through round 2 there, or mismatches before it underbuilds |
| P7 (a check) | Under (CAP-3, CANCEL-WAIT, HOLD) and (FLOOR1, CANCEL-RETIRE, HOLD) on D2(4, 3) and Ring(5, 3), where the reference jams in round 2 with no birth, R1, R2 and R3 match at every cutoff. | a law differs |
| P8 (c) | Holding on the two small starts under FLOOR1, and under (FLOOR1, CANCEL-OFFSHOOT, HOLD) on the cycle and the ring: whether each guard matches, mismatches or underbuilds at each cutoff, and at which birth. Reported. | not applicable |
| P9 (c) | The control under every law here. Reported. | not applicable |

A result that fails is reported as it is.

## Runs and stop rule

- **One engine.** The earlier study's engine, extended by its author from this text. There is no second program here; the
  check on it is the gate against the reference and the earlier study's unit tests, which must still pass.
- **Stop**, in the owner's words: at a match in every order searched, or at the first mismatch. Read for each law family:
  the cap stops at R3's verdict under P1 and P5; holding stops at the first mismatch or early stop of R3 under each of the
  four laws, or at a match through round 3. The study stops when every registered run is done and every prediction has a
  verdict.
- **Resources.** Each search under ten minutes and 8 GB on one process where it can be; a search expected to take longer
  goes through a background unit with a memory cap and a row in the long-running index. No time budget replaces a cap.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor** (Claude Fable 5.2, no tools) reviews this text cold before the freeze.


# (3) STUDY TWO: DRAFT PRE-REGISTRATION

# Can a knot tell its parents from its children by what is built around it? Pre-registration

Ticket `PARENTS-FROM-HOLDERS-20261124-001A` of epic `PARENTS-FROM-HOLDERS-20261124-001` (the first step of sub-goal B325
only; goals G5 with G18). Frozen on 2026-11-24, before the study's code is written. The code is written by a helper agent
from this text alone. It uses [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("the shared
definitions", cited by line) and the words of
[the one-birth-at-a-time study](../LOCAL-ROUND-20261123-001/definitions.md) ("LR"). The canonical K1–K3 test is unchanged.

## The question

Births made one at a time can build what the complete rounds build, if each birth records its parents (assumption A242).
The two holders of a shared distinction do not say which of them is the parent. The owner asked on 24 November 2026 for
the first step of the open question only: "on the structures already built, search for pairs of knots that agree on
everything within d holder steps but differ in who their parents are, for d from 1 to 6. Stop at a rule that recovers the
parents on every structure reached, or at a pair no bounded reading tells apart."

No law is proposed and nothing is grown by a new rule. This is a search on structures that the recorded laws build.

## In standard terms

Whether an orientation of the links of a network can be recovered by a local rule: for each link at a node, is it
determined, by the unlabelled neighbourhood of radius d around the node, whether the link goes to a predecessor or to a
successor? In the literature's words this is local symmetry breaking in a network without identifiers; two nodes with
isomorphic radius-d neighbourhoods cannot be told apart by any rule of that radius (the literature's views and covering
arguments, Angluin 1980; cited from memory, not checked).

## Definitions

- **Structure, place, loose, usable, barred, shared, start knot, holder step, holder-step distance**: as the shared
  definitions and LR section 1.1. Every distinction in the structures used here has one or two holders.
- **The record of parents** is written by each birth (LR section 1.1). It is what the search is checked against, and it
  is not part of what is looked at.
- **The kind of a shared place.** Let a be a place of knot x that is shared with knot y. It is a **parent place** of x when y is a
  parent of x (x took a from y), a **child place** of x when y is a child of x (y took a from x), and a **start place** when
  x and y are both start knots. These three are the kinds.
- **What is looked at within d holder steps of x**, with the place a chosen: the knots at holder-step distance at most d
  from x; for each of them its places, each marked as loose and usable, loose and barred, or shared; which places of
  these knots are one and the same distinction; for a shared place whose other holder is farther than d, only that it is
  shared; which knot is x; which place is a. No names, no rounds and no record of parents.
- Two such looks **agree** when a one-to-one renaming of knots and of distinctions carries one onto the other: x to x, the
  chosen place to the chosen place, every mark kept.
- **A confusable pair at distance d** is two chosen places of different kinds, on one knot, on two knots of one structure,
  or on knots of two structures of the population, whose looks within d agree.
- **A rule of distance d recovers the parents** on a population when the population has no confusable pair at distance d.
  The table from looks to kinds is then well defined on it. Where a rule exists the result also states the simplest
  description found that gives the same table, and says that the description is the thread's.
- **Two coarser looks**, as swaps: without the usable-or-barred mark (loose is loose); and with knots only as live or dead
  and their numbers of places (no record of which loose places are barred).

## Prior work in the program

Searches, each with `--until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`:

`python3 -B scripts/track.py objects "which holder of a shared distinction is the parent, read from the structure within a bounded distance" --until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`

`python3 -B scripts/track.py objects "two knots alike within d holder steps, isomorphic neighbourhoods, automorphism" --until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`

`python3 -B scripts/track.py objects "recognise the original knots from holdings, depth to the first knots, direction of descent" --until 2026-11-24 --exclude PARENTS-FROM-HOLDERS-20261124-001`

- `LOCAL-ROUND-20261123-001` — the source of the question: its guards read a written record of parents, and its report
  names doing without that record as the open direction; its structures are the first population here.
- `ONE-PARENT-REREAD-20261123-001`, `SETTING-AS-REREAD-20261123-001`, `THIRD-HOLDER-20261123-001` — unrelated (births that
  take a distinction that is already shared; a different question about holders).
- `KEEP-READ-20261118-001`, `COPY-READ-20261118-001` — relatives in method only: local pictures of knots compared, under
  another growth and for another question.
- `SERIAL-REPAIRS-20261120-001` — a relative: its guard recovers the order of births from depth to the first knots,
  looking at the whole structure, on starts whose first knots can be recognised; it argues, without running it, that four
  to five holder steps suffice once the direction of each parent step is available. This study asks whether that
  direction is available locally.
- `DIRECT-REACH-20261115-001`, `LOOSE-NAMES-AND-SPENT-JOINS-20261120-001` — unrelated (reach along a chain of bonds; named
  births under ordinary growth).
- `READ-ORIGIN-20261120-001` — a relative: whether the first knots can be recognised from holdings.

## Prior work outside the program

Angluin's work on local and global properties of networks of processors (1980) and the theory of views (Yamashita and
Kameda) say that nodes with the same view cannot be distinguished by a deterministic local rule; orienting an anonymous
network is a standard problem there. Cited from memory and not checked; not searched further. What this would add is the
answer for the structures these growth laws build, where the frontier and the start break symmetry at some distance.

## Known before the freeze (disclosed)

Nothing was run for this study. Known from the record: the structures of the first population and their records of
parents (the one-birth-at-a-time study and its reference engine). Hand reasoning by the thread, not run:

- At distance 1 confusable pairs are expected everywhere: a knot sees only its neighbours' places and marks.
- Far from the start and from the live roster, growth under a fixed ration is regular (every offshoot receives the same,
  every join the same), so a look that reaches neither may be the same from a parent's side and from a child's side. The
  thread could not settle by hand whether the short cycles that joins make (two parents, their common knot and their
  join) tell the two sides apart.
- On a small structure a look of a few steps reaches the start or the live roster, which are not alike, so a rule may
  exist there for a reason that does not carry to larger structures.

## Settled by construction (stated, not tested)

- If two looks within d agree, no rule that uses only what is within d can give them different kinds. So a confusable
  pair at distance d is a proof that no rule of distance d recovers the parents on a population holding that pair.
- A confusable pair at distance d is also one at every smaller distance.
- Agreement is certified both ways: a confusable pair is reported only with an explicit renaming that is checked place by
  place; "no confusable pair" is reported only when every two looks of different kinds are told apart by a quantity that
  any renaming must keep, or by an exhaustive search for a renaming that finds none.

## What is supplied

The laws that built the structures (assumptions A104, A224), the starts, and here: what counts as "everything within d
holder steps" (the look defined above, with two coarser swaps); the populations and their bounds; the reading of "a pair no
bounded reading tells apart" in the stop rule. The record of parents (A242) is used only as the answer the search is
checked against.

## What a result would and would not show

- **A rule at some distance** would show that on the structures searched the record of parents could be replaced by a look
  of that distance. It would not show that the same rule works on larger structures or under other laws, unless it comes
  with an argument.
- **A confusable pair at distance 6 whose least separating distance grows with the structure** would show that no fixed
  distance up to 6 is enough on these structures, and would be evidence that none is. A pair of places exchanged by a
  renaming of a whole structure would be a pair that no look tells apart on that structure at all.
- Neither shows anything about a law that would write less than the full record, for example only the round of birth.

## Populations

- **P1, the structures already built.** For each of the twenty pairs of start and law of the one-birth-at-a-time study
  (its `gate.json`), the reference structure after each complete round up to the last round it compared. And, for the law
  R3 at each cutoff, the structure after every birth of each of the first 20 sampled orders (seeds 0 to 19), built with
  that study's engine.
- **P2, the same grown further.** The same twenty pairs grown by the reference engine to the first round after which the
  structure has more than 2,000 knots, or to 12 rounds, whichever comes first; the structure after each round. Every knot
  of each final structure is tested under parity by both methods of the reference engine, and under not-all-equal where
  the structure has at most 600 knots.
- Pairs are searched within each structure and across all structures of one law (structures under different laws are
  not compared with one another).

## Runs (frozen)

1. **Checks of the code before any run.** (a) On 200 drawn small structures (at most 8 knots within the look), agreement by
   the code equals agreement by trying every renaming. (b) A planted pair: two copies of one structure joined so that a
   renaming exchanges a parent place with a child place is found at every distance. (c) A planted difference: one barred mark
   changed four steps from x is not seen at distances 1 to 3 and is seen from distance 4.
2. **P1**, distances 1 to 6, the full look and the two coarser looks: the number of chosen places of each kind, the number
   of classes of looks, the number of classes holding places of two kinds, and for each law the least distance with no
   confusable pair, if any.
3. **P2**, the same, by round of the structure.
4. **For each law and each distance with a confusable pair in P2:** one pair written out (the two knots, their rounds of
   birth, their distances to the start and to the nearest member, the renaming), and the least distance at which that pair
   is told apart, up to 10.
5. **Whole-structure renamings.** For each final structure of P2 with at most 2,000 knots: whether some renaming of the
   whole structure onto itself carries a parent place to a child place.
6. **Where a rule exists** at some distance on P1 and P2 for a law: the table of looks, and the simplest description of it
   that the code's author can state and check against every place.

## Predictions (frozen)

Hand predictions that were not run are marked (b); open questions reported without a prediction are marked (c).

| # | Prediction | Fails when |
| --- | --- | --- |
| Checks | The three checks of the code hold. | any fails |
| P1 (b) | At distance 1 there is a confusable pair under every law, in P1 and in P2. | some law has none |
| P2 (b) | In P2, under the laws with a ration fixed at birth (a fixed three with waiting; just enough for three places, the short knot retiring or making offshoots), there is a confusable pair at every distance from 1 to 6: no rule of distance up to 6 recovers the parents there. | some such law has a distance from 1 to 6 with no confusable pair on its P2 structures |
| P3 (b) | For the pair written out at distance 6 under each such law, both knots lie more than 6 holder steps from the start and from every member. | a pair at distance 6 reaches the start or a member |
| P4 (c) | On P1 alone: the least distance with no confusable pair for each law, if there is one. Reported. | not applicable |
| P5 (c) | Under ordinary growth, where what a knot receives follows the demand: whether a rule exists at some distance up to 6 on P2. Reported. | not applicable |
| P6 (c) | The two coarser looks: whether they change any least distance. Reported. | not applicable |
| P7 (c) | Whether any whole structure has a renaming that carries a parent place to a child place. Reported. | not applicable |

A result that fails is reported as it is.

## Runs and stop rule

- **Stop**, in the owner's words: at a rule that recovers the parents on every structure reached, or at a pair no bounded
  reading tells apart. Read here: the study stops when, for each law, either some distance from 1 to 6 has no confusable
  pair on P1 and P2 (the rule is then stated), or a confusable pair at distance 6 is written out with the least distance
  that tells it apart and with how that distance changes with the round of the structure. A pair exchanged by a renaming
  of a whole structure settles the second for that structure.
- **Resources.** Each run under ten minutes and 8 GB on one process where it can be; anything longer in a background unit
  with a memory cap and a row in the long-running index. No time budget replaces a stated bound.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor** (Claude Fable 5.2, no tools) reviews this text cold before the freeze.


# (4) THE EARLIER STUDY'S DEFINITIONS (frozen; cited as LR by section)

# One birth at a time from what is built: definitions

Epic `LOCAL-ROUND-20261123-001` (sub-goal B323; goals G5 with G18). Frozen on 2026-11-24 with the pre-registration of
ticket A, before any of the study's code is written. It extends [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md)
of `RING-IN-BALANCE-20261123-001` and changes nothing in them. "The definitions" below means that file, cited by line. Words
are the glossary's and the definitions'.

- **Member, met set, common knot, joinable, part, short, waits, retires, live, dead, usable, barred, start** keep exactly
  their meaning there.
- **Member, short, waits and retires** are also used of the start roster, of a brood's roster at birth and of the waiters'
  roster, each with holdings h₀. They mean there what the definitions mean of the live roster with holdings h. A **part** of
  any of these rosters is a connected component of its joinable relation (definitions line 27).
- A roster is always named by its kind: the start roster, a brood's roster at birth, the waiters' roster, the present roster
  (the definitions' live roster as it now is), the reference's roster.
- "Jams" keeps only the definitions' sense (lines 84–85, 125).
- New here, each defined where it first appears: **weaned**, **brood**, **all-weaned**, **all-short**, **status**, a member's
  **acting roster**, **waiters' roster**, a **barring**, **allows**, **cutoff**, **matches through round r**,
  **underbuilds**, the **extent** of a brood from a knot, **x-last order**, **untouched**.

The text was drafted by the helper agent that surveyed the record and wrote a scratch prototype of these laws. The prototype
is not the study's engine. What it showed is disclosed in the pre-registration, under "Known before the freeze".

## 1. What is read from the structure

### 1.1 Parents, children, places, holder-step distance

- **Parents.** Every birth writes, with the new knot, the set of knots it took a distinction from: its **parents**
  (definitions steps 4–5: a join's parents are its group, an offshoot's its one member). The **children** of a knot are the
  knots that have it among their parents. A start knot has no parents and is the child of none.
  - The parent relation is not a reading of the holders: a shared distinction has two holders and no order (definitions
    lines 11–13, 76). It is written by the birth, as the record's birth-by-birth law already reads it (definitions line 111).
    See section 5.
- **Places, loose, usable, barred, h(u), k(u), member, live, dead**: as the definitions, lines 11–24.
- **Holdings at birth.** For a knot x with parents, **h₀(x)** is its number of places less its number of parents. Each
  parent gave one distinction; the others x received at birth, whatever they are now: loose, barred, or shared with a child.
  For a start knot, h₀(x) is its number of places not shared with another start knot.
- **Holder-step distance.** One holder step crosses a shared distinction from one holder to the other
  ([SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/local_rule.md) line 7). The **holder-step distance** between two knots is
  the least number of holder steps between them.
- A rule **reads to holder-step distance d** from a knot when its decision is the same for any two structures that agree on
  every knot within holder-step distance d of it. Agreeing means: their places, which of those are loose, usable or
  barred, and their parent sets and children, together with the closing bit of section 2.4.

### 1.2 The start roster (what plays the part of parents for start knots)

The **start roster** has as members the start knots with h₀ ≥ 1, each with holding h₀. Its met sets are, for each start
knot, the set of start members it meets, when it has at least two. Any start knot may be a common knot here, a member
included, as in definitions step 1. It is the roster the first complete round reads; it never changes.

### 1.3 Weaned

A knot is **weaned** when none of its parents is a member of the present roster: its parents have finished giving. Every
start knot is weaned.

### 1.4 The brood

- The **brood** of a knot x with parents is the smallest set B containing x such that, for every knot in B and every parent
  of it, all children of that parent are in B. The **parents of the brood** are the parents of its knots. Knots of B that
  have since made births, retired or died stay in B.
- **A brood's roster at birth** has as members the knots of B with h₀ ≥ 1, each with holding h₀. Its met sets are, for each
  parent p of the brood, the members that are children of p, when there are at least two.
- A brood is **all-weaned** when every knot in it is weaned.
- **Why this set** (an argument for the referee, not a definition).
  - Under RELEASE a member that makes any birth spends every usable distinction in the one roster in which it acts. So all
    children of a parent are born in one complete round.
  - Past the start, a knot meets only its parents and its children, and a waiter meets only its parents. So a waiter is
    joinable only with brood-mates that still wait.
  - Hence an all-weaned brood's roster at birth is exactly the part the complete rounds read in the round after its births, with
    the holdings it had then. Its waiters' rosters (section 2.1, step 5) are the parts the complete rounds read in the
    rounds after that.

## 2. Plans, and how a birth is made

### 2.1 The plan of a roster

A **roster** here is a set of members, a holding for each, and a family of met sets. Its **plan** is read as follows.

1. **Groups and owing.** As definitions steps 1–2 (lines 36–40), with the roster's holdings.
2. **Treatment.**
   - STALL: if a member is short, the plan **stalls** and has no births.
   - CANCEL-OFFSHOOT: a short member's births are one offshoot from each of its holdings.
   - CANCEL-RETIRE: a short member **retires** in this plan.
   - CANCEL-WAIT: a short member **waits** in this plan.
3. **Births of the plan.** Every group containing a short member is cancelled. Each kept group is one planned join. Each
   member that is not short has as many planned offshoots as its holding less its kept groups (RELEASE).
4. **Fresh count of a planned birth with p parents.**
   - FLOOR1 and RATION-3: as definitions step 7, line 62.
   - ORD: f = max(D, 3 − p, 1). D is the number of groups containing the birth in a roster whose members are the plan's
     births, each with holding 1, and whose met sets are, for each member of the plan's roster, the births it is a parent
     of, when there are at least two. Under STALL no member keeps anything, so no old member enters this roster, and D is
     the birth's owing in the next roster.
   - The closing exception is not applied here (section 2.4).
5. **Waiters' recursion** (CANCEL-WAIT only).
   - The **waiters' roster** of a roster has as members its waiters, with holdings unchanged. Its met sets are the roster's
     met sets intersected with the waiters, kept when they have at least two.
   - Each part of the waiters' roster is read a second time by steps 1 to 5, and its own waiters' roster after that.
   - A part of any roster all of whose members are short is **all-short**: its members wait for ever and make no births. The
     recursion stops there.
   - A member's **acting roster** is the first roster of this sequence in which it is not short.
   - A waiter reads a second time against the waiters of its roster only, never against new knots. Past the start this is
     what the complete rounds read, by section 1.4.
6. **Status.** A member's **planned births** are the births of its acting roster that have it among their parents, with
   multiplicity. Its **status** is one of:
   - "acts", with those births;
   - "retires";
   - "its plan stalls";
   - "is in an all-short part".

### 2.2 Which roster a member reads

- **Start clause.** A start knot reads the start roster (section 1.2), at every moment. The start clause is exact only when
  no start knot that acts meets a start knot that waits.
  - On the start-clause counterexample of the pre-registration two readings are wrong. The waiter (knot 0) reads a waiters' roster of
    itself alone. And the brood's roster at birth of the children of knots 1–3 omits knot 0, which the complete rounds put
    in their part in round 2.
  - Ring(5, 3) satisfies the condition: no start knot is short there.
- Every other member reads its brood's roster at birth (section 1.4).

### 2.3 Births already made

- A planned join with parents G is **made** when some knot has exactly the parents G.
- A member's planned offshoots are made, up to their number, by its children that have it as their only parent.
- The **remaining births** of a plan are, for each planned join and for each member's planned offshoots, those planned less
  those made. When more births of one kind have been made than the plan now gives, none of that kind remains. Where the plan
  read is the complete rounds' own (R2 and R3, and T(d) for d at least the brood's extent), this happens only after a
  mismatch (section 4).

### 2.4 Making a birth, retiring, stalling, the closing bit

1. A law **allows** a birth: a parent set B, each of whose knots holds a usable loose distinction, with the fresh count f of
   the plan it is read from.
2. The new knot takes one usable loose distinction from each knot of B; which one makes no difference up to renaming
   (definitions lines 76–77). It receives f fresh distinctions, all usable (FILLERS is not used here). Its parents are B.
3. **The closing bit** (parity, every ration). If, after taking, no loose distinction is left in the structure (usable or
   barred), the new knot receives none.
   - It is read on the present structure. This is a reading: the definitions' exception (lines 63–66) concerns a round's
     only birth.
   - That the two agree on these laws is argued, not proved here. Every non-closing birth receives at least one fresh
     distinction, and a barred distinction stays loose, so a part never runs out of loose distinctions except at a closing
     birth.
   - Every run counts each firing and whether the reference knot matched to that birth received none.
4. **Retiring.** When a member's status is "retires" and the law allows it (with the same guard as its births), all its usable
   loose distinctions are barred.
   - This is a **barring**. It is not a birth and not a move, since it adds no knot (glossary, "Move").
   - It is made as soon as it is allowed, before the next birth.
5. **Stall.** Under STALL the stall is read from the start roster only: if the start roster's plan stalls, no birth is
   allowed anywhere, and the growth has stalled.
   - This is enough under (ORD, STALL). There a new knot receives f ≥ D, its owing in the next roster (step 4 of section
     2.1). So no member of any later roster is short.
   - A brood's roster at birth whose plan stalls would allow nothing; under ORD this cannot occur. The pre-registration's
     P12 is a check of this, true by construction.

**Orders.** An order of a law is a sequence of allowed births, each allowed at its moment, with every allowed barring
made before the next birth. No fairness, priority or weighting is assumed. The kinds of order the study searches are in
section 4.

## 3. The laws

**R0 · the record's birth-by-birth law.** As the definitions, lines 108–126: common knots ANY, order UNIFORM, and
BY-GENERATION as recorded. It is defined there only for RATION-3 or PRESENT-ORD, with WAIT or FIRST-COME. **Added here**, for
this study only:
- FLOOR1 gives f by p, as RATION-3 does in step 4.
- Under CANCEL-RETIRE a member read short retires at once (a barring).
- Under CANCEL-OFFSHOOT a member read short has an offshoot move from each usable loose distinction and no join move.
- Under ORD the law is PRESENT-ORD with FIRST-COME, as the record ran ROUND-FREE's law
  ([ticket C's readings](../../experiments/RING-IN-BALANCE-20261123-001C/RING-IN-BALANCE-20261123-001C-E001_no_round/deviations.md),
  item 18).

It reads the present roster: its parts, the open test and each member's present holdings.

**R1 · the birth's parents are weaned.**
1. Each member reads its status by sections 2.1–2.2 from the structure as it stands. A brood that is not all-weaned is read with
   the children its parents have so far.
2. A remaining birth B is allowed when every knot of B is weaned.
3. A barring of x is allowed when x is weaned.

The guard reads to holder-step distance 1. How far the reading of a status must go is what T(d) measures.

**R2 · the parents' brood-mates are weaned too.** As R1, but a remaining birth B, or a barring of x, is allowed when
every knot of B (or x) is weaned, and so is every knot sharing a parent with it, that is, every child of each of its parents.
The guard reads to holder-step distance 3.

**R3 · the brood is all-weaned.** As R1, but a remaining birth B, or a barring, is allowed when the brood containing the
knots of B (or the knot barred) is all-weaned. All knots of a remaining birth lie in one brood, since joinable knots share a parent. A birth of start
knots is always allowed, since the start roster has no parents. R3 reads all of the brood. On D2(n, 3) the brood of the
start's births has 2n knots, and its extent from any of them is about n holder steps.

**T(d) · R3's reading within holder-step distance d** (d = 2 to 10). For a proposed birth with parent set B, let W be the
knots within holder-step distance d of some knot of B. Only knots of W are read. A knot of W whose parents or children lie
outside W is read without them: they give it no met set, no member and no guard. The one exception is h₀, which a knot of W
carries itself (its places and the number of its parents), so h₀ is read exactly even at the boundary.
1. **The brood within d** of B is the smallest set containing B such that, for every knot in it and every parent p of it
   that lies in W, every child of p in W is in the set.
2. **Its roster at birth** has as members the knots of the brood within d with h₀ ≥ 1, holdings h₀. Its met sets are, for
   each parent p in W of a knot of the brood within d, the members that are children of p, when there are at least two.
   - If every knot of B is a start knot, read instead the start roster within W: its members in W, and, for each start knot
     in W, the start members in W that it meets, when at least two.
   - A B that mixes start knots and other knots is never allowed.
3. **The plan** of that roster is read by section 2.1, with the waiters' recursion. Made births are subtracted by section
   2.3; the children of B's knots are one holder step from B, so they lie in W.
4. **Allowing.** B is allowed when it is a remaining birth of that plan, with the plan's fresh count, and every knot of the
   brood within d is weaned as read in W (none of its parents in W is a member).
   - A barring of x is allowed when x's status in the reading around x alone is "retires", under the same guard.
5. **Candidates.** The candidates are every member alone, and every remaining join of the reading around one of its
   members. Each candidate is tested in the reading around its own parent set.

The **extent** of a brood from a knot of it is the greatest holder-step distance from that knot to a knot of the brood or a
parent of the brood. When W contains a brood and all its parents, as it does when d is at least the brood's extent from
every knot of B, T(d) reads that brood as R3 does.

**R3L · the present part** (the working idea as literally stated). Read the present roster (definitions step 1, ANY) and its
parts.
1. A part in which no member has a child and every member is weaned is **untouched**. Its plan is the plan of the part
   with present holdings h(u) and present met sets. Its remaining births and barrings are allowed.
2. In a part in which some member has a child, each member reads its status by section 2.2 (the start roster, or its brood's
   roster at birth). Its remaining births and barrings are allowed with no guard.
3. Any other part allows nothing.

R3L reads the whole present part.

**Control · the depth guard, originals supplied.** This is the record's guard, with this study's round in place of the
ordinary operator: [SERIAL-REPAIRS](../SERIAL-REPAIRS-20261120-001/present_proof.md) lines 41–43;
[cohort.py](../../experiments/SERIAL-REPAIRS-20261120-001A/SERIAL-REPAIRS-20261120-001A-E001_repairs/cohort.py) lines 28–81.
The originals are supplied as in
[the clock study's replay.py](../../experiments/TICK-BIRTHS-AND-SCARCITY-20261121-001B/TICK-BIRTHS-AND-SCARCITY-20261121-001B-E001_serial/replay.py)
lines 66–116.
1. The originals are the start knots. The **depth** of a knot is its holder-step distance to the nearest start knot.
2. Let k be the least depth of a member. The **layer** is every knot of depth k, members or not.
3. Holdings: at k = 0, the start holdings; otherwise each layer knot's places not shared with a knot of depth k − 1.
4. The layer's roster has as members the layer knots with holding at least 1. Its met sets are the start roster's at
   k = 0; otherwise, for each knot of depth k − 1, the layer's members it meets, when at least two.
5. The plan is section 2.1, steps 1–4, **without** the waiters' recursion: a waiter is given nothing to do.
6. The layer's children are the knots of depth k + 1, each with its neighbours of depth k as parents. Subtract them (section
   2.3), allow the remaining births, and make barrings as section 2.4.

The control reads the whole structure.

## 4. The comparison

- **Reference.** The reference is ticket A's engine of the earlier study
  ([engine.py](../../experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py),
  `round_step`). It is run on the same start under the same law through a last round R. Each reference knot has a round of
  birth.
- **Gate.** Before any search, the new engine's own complete rounds are checked against the reference structure by
  structure. The test is exact isomorphism of the incidence structure of knots and distinctions after each round, rounds 1
  to R, knots coloured by round of birth and distinctions by barred or not, for every start and law. A failure stops the
  searches until it is resolved and recorded.
- **The last round R** is the least round such that every knot born by round r (the cutoff below), in the reference's roster
  after round R, is either no member or a member of a part all of whose members are short. Under CANCEL-WAIT such a part
  makes no birth in any later round. The reference's growth may also have stopped, stalled or jammed by then.
- **Match.** A run keeps a map m from its knots to reference knots, the identity on start knots.
  - A birth c with parents B and f fresh distinctions **matches** when the reference has a knot c′, not yet an image of m,
    whose parent set is m(B) and whose fresh count (places less parents) is f. Then m(c) is the least-numbered such c′.
  - A barring of x matches when m(x) holds barred distinctions in the reference and has no children there.
  - Anything else is a **mismatch**.
- **Cutoff.** A birth is **within round r** when the image of each of its parents was born by round r. In the comparison only
  births within round r are allowed.
  - For R1, R2, R3 and T(d) the cutoff removes no interleaving that matters. A birth within round r is read from a brood of
    knots born by round r and from their parents, and no birth outside the cutoff enters such a brood.
  - For R0 and R3L, which read the present roster, births outside the cutoff could change what they read. So the cutoff
    removes interleavings, and their least differing orders and any match through round r are relative to the cutoff.
  - A mismatch at a birth whose parent was born after round r is not tested.
- **Outcomes of a run.**
  - A run **matches through round r** when it has no mismatch, allows no birth within round r, every reference knot whose
    parents are all images of m and born by round r is itself an image, and every image of m born by round r that retires
    in the reference is barred in the run.
  - A run **underbuilds** when it allows no birth within round r while one of those reference knots is not an image, or one
    of those retirements is not made.
- A law **builds what the complete rounds build through round r** on a start when every maximal order of it within round r
  matches through round r. When births are made is not compared, only what is built.
- **Memo key.** The set of images of m, together with the set of images of barred knots.
  - It is valid while every birth and barring so far has matched. Then two states with equal keys are the same structure up
    to renaming of distinctions: each image fixes a knot's parents, its fresh count and whether it is barred, and which loose
    distinction of a parent a child took is exchangeable. Every law here is invariant under renaming, so it allows the same
    births in both states.
  - Equal structures can have unequal keys (which of two exchangeable offshoots has the matched children); that only
    enlarges the search.
  - A state's number of births is the size of its key less the start knots. So a breadth-first search over keys finds the
    least number of births to a mismatch exactly. A depth-first search stopped after a set time does not: on the
    start-clause counterexample it reported 9 where the least is 2.
- **Orders searched.** Three kinds, none of them a weighting:
  - **every order**: breadth-first over memo keys, up to a cap on keys, reported as finished or not, with the number of births
    to which every order was searched;
  - **sampled**: at each step a uniform choice among the allowed births within the cutoff, seeds 0 to 199;
  - **x-last**: for each knot x that exists by round 1 of the reference, an order that never makes a birth with x (through
    m) among its parents while any other birth within the cutoff is allowed. Among the others it chooses uniformly, seed 0.
  - Shares are reported under the uniform choice only.
- **Reported in every run:** each firing of the closing bit and whether the matched reference knot received none, and
  whether any roster read has a group of three or more.

## 5. What is supplied by hand (scaffolds)

- **The parent relation.** Which holder of a shared distinction is the parent is written by the birth, not read from the
  holders. Holdings at birth, weaned, brood and every made-birth test depend on it.
  - Recovering it instead from depth to supplied or recognised originals reads the whole structure.
  - Depth orients every parent–child meeting here, but it is not the round under waiting. In the scratch runs 196 of 544
    knots of D2(4, 3) through round 7 have depth unequal to their round.
- **The start clause.** Start knots read the start roster for ever, and start waiters read a second time against start knots
  only. It is exact only when no start knot that acts meets a start knot that waits; on the start-clause counterexample it is wrong
  twice (section 2.2).
- **The waiters' recursion** (section 2.1, step 5): how a waiter reads a second time, against which roster, and the
  all-short test.
- **The barring** under CANCEL-RETIRE: an act that is not a birth, made as soon as allowed.
- **The closing bit**, read on the present structure, and under STALL the read of the start roster only.
- **The guards**: weaned; brood-mates weaned; the brood all-weaned; T(d)'s reading within d and its rule at the boundary; R3L's untouched test.
- **R0's extension** to FLOOR1, CANCEL-RETIRE, CANCEL-OFFSHOOT and ORD.
- **The control's supplied originals.**
- **The comparison**: ticket A's engine as the reference, the cutoff r, the last round R, the rule for a match and its
  least-numbered choice, and the three kinds of order (none a weighting; shares under the uniform choice only).
- **The starts, cutoffs and caps**, and the scratch prototype that produced the disclosed results, which is unreviewed and is not
  the study's engine.


# (5) THE SHARED DEFINITIONS (frozen; line numbers as cited)

   1  # A ring in balance: definitions shared by the three studies
   2  
   3  Epic `RING-IN-BALANCE-20261123-001`, 2026-11-23. Frozen with the three pre-registrations, before any of the study's code is
   4  written. Tickets A, B and C cite this file and add only what is their own. The canonical K1–K3 test is unchanged. Words are the
   5  glossary's (Intuitions guide). The growth records' "junction" is a knot and their "growing end" is the live roster. Their
   6  "witness" is here a **common knot**, their "witnessed set" a **met set** and their "adjacent" **joinable**, because the glossary
   7  keeps witness for a helper variable and graph theory uses adjacent for what the program calls meeting.
   8  
   9  ## Structure
  10  
  11  - A **structure** is a finite set of knots, each holding a set of distinctions, its **places**. A distinction has one or two
  12    **holders**. It is **loose** with one holder and **shared** with two. Every knot of a start has at least three places, and so
  13    has every new knot except one that receives no fresh distinction (below).
  14  - Two knots **meet** when they share a distinction. A knot is **live** while it holds a loose distinction and **dead** otherwise.
  15  - A **start** is a structure given before any birth, written as its list of knots, each a list of distinction numbers (the
  16    records' stars).
  17  - A loose distinction is **usable** unless the law has **barred** it: a barred distinction stays loose and is never taken by any
  18    birth. (The Intuitions guide and the site call a barred distinction "never used".)
  19  
  20  ## The live roster
  21  
  22  - The **members** of the live roster are the knots holding at least one usable loose distinction. Write h(u) for the number of
  23    usable loose distinctions member u holds and k(u) for the number of barred ones. A knot holding only barred distinctions is
  24    live and is not a member.
  25  - A **met set** is the set of members that one knot of the structure meets, when it has at least two members. That knot is a
  26    **common knot** of those members; it may be dead or itself a member. Two knots with the same met set count once.
  27  - Two members are **joinable** when some met set contains both. A **part** of the live roster is a connected component of the
  28    relation joinable. The roster is **past its start** when no member meets a member (the records' positive age).
  29  - Two rosters, or two parts, are **the same** when a one-to-one renaming of members carries h, k and the family of
  30    inclusion-maximal met sets of one onto the other.
  31  
  32  ## One complete round
  33  
  34  A **law** is a knot law (parity or not-all-equal), a ration, a treatment and optional extras. One round, on real knots:
  35  
  36  1. **Groups.** First take every inclusion-maximal set of at least three pairwise joinable members that is contained in no
  37     single met set. Then take every joinable pair that is contained in none of the sets just taken. These are the groups
  38     ([ORDINARY-DYNAMICS-20261120-001](../ORDINARY-DYNAMICS-20261120-001/end_operator.md), "The operator on the present end", step 1).
  39  2. **Owing.** Member u owes one usable loose distinction to each group containing it. It is **short** when it owes more than
  40     h(u). Shortness is read once, here, for the whole round.
  41  3. **Treatment of a short member.**
  42     - STALL: if any member is short, no birth is made and the growth has stalled.
  43     - CANCEL-OFFSHOOT: every group containing a short member is cancelled; the short member makes an offshoot from each of its
  44       usable loose distinctions.
  45     - CANCEL-WAIT: every group containing a short member is cancelled; the short member **waits**: it makes nothing and keeps
  46       everything it holds.
  47     - CANCEL-RETIRE: every group containing a short member is cancelled; the short member **retires**: it makes nothing now or
  48       later, and its loose distinctions are barred.
  49  4. **Joins.** Each group that is kept makes one new knot, a **join**, whose parents are its members; it takes one usable loose
  50     distinction from each.
  51  5. **Offshoots and the release rule.** A member that is not short, after paying its kept groups, makes one new knot of one
  52     parent, an **offshoot**, from each usable loose distinction it has left. RELEASE (the default): this includes the
  53     distinctions that its cancelled groups would have taken. HOLD: it keeps those and makes offshoots only from the rest. With
  54     the extra NO-OFFSHOOT it makes no offshoot, and the distinctions an offshoot would have taken are barred.
  55  6. **Demand.** Count every new knot as a member holding one usable loose distinction, whatever it will receive, and keep every
  56     old member that still holds a usable loose distinction after steps 3 to 5 (one that waits; under HOLD, one that keeps what
  57     its cancelled groups would have taken) with what it holds. Form the groups of that roster as in step 1. The **demand** D of
  58     a new knot is the number of those groups that contain it.
  59  7. **Fresh distinctions (the ration).** A new knot with p parents and demand D receives f fresh distinctions, each loose and held
  60     by it alone. With q = max(D, 3 − p, 1), the ordinary count:
  61     - ORD: f = q. CAP-k: f = min(q, k). RATION-k: f = max(k, 3 − p).
  62     - ONE-FEWER: f = min(q, max(3 − p, 0, q − 1)). FLOOR0: f = max(3 − p, 0). FLOOR1: f = max(3 − p, 1).
  63     - **Closing exception** (parity only, every ration): a new knot that takes every loose distinction of the structure receives
  64       none; it may then have fewer than three places. It is then the round's only birth, nothing is barred and no old member
  65       keeps anything. Under not-all-equal there is no exception
  66       ([NAE-GROWTH-20261119-001](../NAE-GROWTH-20261119-001/nae_growth.md): the growth reads the knot law in this one place).
  67  8. **Extra FILLERS.** Of a new knot's f fresh distinctions, min(f, D) are usable and the rest are barred.
  68  
  69  The records' ordinary growth, the cheapest growth of lesson 8.1, is the law (ORD, STALL). **The two added rules** are the law
  70  (CAP-3, CANCEL-WAIT with RELEASE). **The three added rules** are (CAP-3, CANCEL-WAIT with RELEASE, FILLERS). They were added by
  71  hand (assumption A224, a scaffold); RELEASE is part of what was added. The pilot's program counted a short member by all its
  72  loose distinctions; the two readings agree, because a member holding a barred distinction owes exactly its usable count in
  73  the one round it acts. One barred distinction anywhere switches the closing exception off everywhere, since the exception needs
  74  a birth that takes every loose distinction there is.
  75  
  76  A distinction taken by a new knot becomes shared between its old holder and the new knot. Which of a member's usable loose
  77  distinctions goes to which birth makes no difference up to renaming.
  78  
  79  ## Kinds of outcome under complete rounds
  80  
  81  A run is one start grown under one law through a stated number of rounds, or until a stated number of knots. After each round:
  82  
  83  - The growth has **stopped** when the roster has no member, **stalled** (STALL only) when a member is short, and **jammed** when
  84    the roster has members and the round makes no birth.
  85  - A part Y of the roster after round s, past its start, **returns** at round t > s when the members after round t that descend
  86    from Y (through parents; a waiting member descends from itself) include a part that is the same as Y. The other parts those
  87    descendants form have **come apart** from Y, and Y **gives parts off** when there is at least one. Returns are searched with
  88    the least s first and then the least t, and t − s is the period.
  89  - The roster is **in balance** from round s with period T when at least one birth is made in every round and the whole roster
  90    after round t + T is the same as the whole roster after round t for every t ≥ s in the run. The structure still grows.
  91  - A part has **ended** when none of the knots descending from it is a member. It may still hold barred distinctions.
  92  - For a census a run is given one kind, the first that applies: stalled; jammed; stopped; a part returns giving parts off; a
  93    part returns giving none off; grows to the bound with no return found.
  94  
  95  ## One part at a time, and one birth at a time
  96  
  97  - **Part-round law.** A move is one complete round of one part: steps 1 to 8 applied to the members of that part alone, the
  98    other parts left as they are (the closing exception as stated: only for a birth that takes every loose distinction of the
  99    whole structure). The **own time** of a start knot is 0; a new knot's is one more than its parents'; and a member that
 100    waits through a move of its part gains one. So a member's own time is the number of moves its line of descent has taken
 101    part in. A **priority** chooses the part that moves next among the parts that would make a birth:
 102    - ALL-IN-TURN: every part once, then again; this is the complete round.
 103    - UNIFORM: each part with equal chance.
 104    - BY-MEMBERS: each part with chance in proportion to its number of members.
 105    - LARGEST: a part with the most members; SMALLEST: one with the fewest; ties uniform.
 106    - MOST-LOOSE: a part whose members hold the most usable loose distinctions in all; ties uniform.
 107    - LEAST-TIME: a part whose members have the least own time; ties uniform. This priority reads the history, not the structure.
 108  - **Birth-by-birth law** (the present-state reading of [ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md), with
 109    waiting). A move is one birth, and everything is read again after every move.
 110    1. Form the groups of the present roster as in step 1, with every knot allowed as a common knot (ANY) or only dead knots
 111       (DEAD). A group is **open** when no knot already made has all of its members among its parents.
 112    2. A member is short when it is in more open groups than h(u); a short member makes nothing. Under FIRST-COME, used only to
 113       check the engine against the record, no member counts as short.
 114    3. Every open group with no short member is a join move. A member that is not short and holds more usable loose distinctions
 115       than the number of open groups without a short member that contain it has an offshoot move. (Under FIRST-COME: every open
 116       group is a join move, and a member has an offshoot move when h(u) exceeds the number of open groups containing it.)
 117    4. The new knot receives max(3, 3 − p) fresh distinctions (RATION-3), or max(d, 3 − p, 1) (PRESENT-ORD), where d is the number
 118       of open groups containing it immediately after its birth, the new knot counted as a member before it receives anything.
 119       Closing exception, parity only: a move that takes every loose distinction of the structure, with d = 0 where d is read,
 120       receives none.
 121    5. Start knots have **generation** 0 and a new knot has generation one more than the greatest generation of its parents; a
 122       move's generation is the greatest generation of its parents. The next move is chosen uniformly among all moves (UNIFORM)
 123       or among the moves of least generation (BY-GENERATION), with joins first, offshoots first, or uniformly among those. The
 124       generation is the simulator's record of who was made from whom; it is not read from the structure.
 125    - A birth-by-birth run has **jammed at generation g** when no move of generation g or less is available and some member of
 126      generation g or less is short.
 127  
 128  ## The knot test
 129  
 130  - **Parity.** Each knot is the rule that its places have even parity. A knot with place set S passes K1–K3 in the whole
 131    structure when the allowed states of the structure, restricted to S, are exactly the even assignments of S. Two methods are
 132    run and must agree on every knot. Ranks: with H the matrix over the field of two elements with one row for each knot, the
 133    rank of H less the rank of H with the columns of S removed is one (the records' test, ORDINARY-DYNAMICS, `rulers.py`). Cut:
 134    in the graph with one vertex for each knot and one for the outside, an edge between the two holders of each shared
 135    distinction and an edge to the outside for each loose one, deleting the knot leaves the rest connected (the knot is not a cut
 136    vertex; the allowed states are the graph's cycle space).
 137  - **Not-all-equal.** Each knot is the rule that its places are not all equal. A knot passes when the assignments of S that
 138    extend to an allowed state of the whole structure are exactly the assignments that are not constant, decided by a SAT solver
 139    for each of the 2^|S| assignments (the records' test, ORDINARY-DYNAMICS, `source_cert.py`).
 140  - **Extension.** A round, or a move, extends when every allowed state of the structure before it is the restriction of an
 141    allowed state after it.
 142  
 143  ## Named starts
 144  
 145  - **Ring(n, a).** Knots 0 to n − 1. Knot i shares one distinction with knot i + 1 (mod n) and holds a loose distinctions.
 146    Ring(5, 3) is the start of the golden-ratio eddy.
 147  - **Cycle through dead knots, doubled, D2(n, a).** Members 0 to n − 1, each holding a loose distinctions, and dead knots
 148    w_0 to w_{n−1}; w_i shares two distinctions with member i and two with member i + 1 (mod n), so w_i has four places and its
 149    met set is {i, i + 1}.
 150  - **Cycle through dead knots that meet one another, DW(n, a).** As D2 with single meetings: w_i shares one distinction with
 151    member i, one with member i + 1, one with w_{i−1} and one with w_{i+1}.
 152  - **The seven-knot generator.** Stars [0,1,2,9,10,11], [0,1,3], [4,5,12,13,14], [6,7,15,16,17], [2,3,4,6,18,19,20], [7,8,21,22],
 153    [5,8,23,24] ([GENERATORS-20261120-001](../GENERATORS-20261120-001/source.md)).
 154  
 155  ## What is supplied by hand
 156  
 157  The complete round (assumption A104); every ration other than ORD, every treatment other than STALL, the release rule and both
 158  extras (A224); the part-round law, the birth-by-birth laws and every priority; the starts; the reading of a part as a thing (as
 159  in A125); the bounds on rounds, moves and knots; and each weighting named where a share is given. Each study says which of
 160  these it swaps.
