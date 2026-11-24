# Can births be made one at a time, each knot reading a few steps, and still build what the rounds build? Pre-registration

Ticket `LOCAL-ROUND-20261123-001A` of epic `LOCAL-ROUND-20261123-001` (sub-goal B323; goals G5 with G18). Frozen on
2026-11-24, before the study's code is written. The code is by a helper agent that has not seen the drafter's prototype, written from this
text and [the definitions](../LOCAL-ROUND-20261123-001/definitions.md), which extend the
[shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) of `RING-IN-BALANCE-20261123-001`. The canonical K1–K3
test is unchanged.

## The question

The owner asked on 23 November 2026 whether time is "a device or pattern just like the other ones", and then whether it is
"not really like a sequencer, but more like a priority system".

- The study of the ring that returns found that the round for the whole growth can be replaced by rounds taken part by part.
  It also found that a law in which every knot reads a second time after each birth jams.
- The record's serial-repairs study had already shown, for ordinary growth, a rule that makes one birth at a time and builds
  what the rounds build in every order, by finishing the least unfinished depth first. It reads the whole structure and needs
  the first knots to be recognisable, and under waiting it does not finish what the rounds build.

This study asks what is left. Is there a law that makes one birth at a time, in which each knot reads only a bounded
holder-step distance and only what is built, that builds in every order what the complete rounds build? It asks this for the
laws with a ration fixed at birth, for the ring that returns (which needs waiting), and for ordinary growth. It registers five
laws that differ in how far a knot reads and when it may read, a family T(d) that lets the widest of them read only within
holder-step distance d, and the record's depth guard as a control.

## In standard terms

Confluence of an asynchronous graph-rewriting system against its synchronous reference: whether every maximal sequence of
single rule applications, each guarded by a local readiness condition, reaches the structure the parallel steps build. The
guards are of the kind used by a synchronizer in distributed computing (a node acts when its predecessors have finished). The
question of the least holder-step distance a guard must read is the question of the locality of the synchronizer.

## Prior work in the program

Searches, each with `--until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`:

`python3 -B scripts/track.py objects "one birth at a time from what is built, every order builds what the rounds build" --until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`
`python3 -B scripts/track.py objects "guarded serial rule, depth cohort, reads the whole structure" --until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`
`python3 -B scripts/track.py objects "a knot reads a bounded number of steps to decide its birth" --until 2026-11-23 --exclude LOCAL-ROUND-20261123-001`

- `RING-IN-BALANCE-20261123-001` — the same object: its ticket C showed that parts taking their rounds one at a time build
  what the complete rounds build, and that the birth-by-birth law, here R0, jams. This study starts from its definitions.
- `SETTING-AS-REREAD-20261123-001` — unrelated (a measurement setting read as a re-read birth, another thread's study of the
  same day).
- `SERIAL-REPAIRS-20261120-001` — the same object for ordinary growth: its guarded rule finishes the least unfinished depth
  first and reproduces the complete rounds in every order of its own moves, reading the whole structure, on starts whose
  original knots can be recognised (proved in that scope, referee pending); it also argues, without running it, that a read
  of four to five holder steps suffices once parent direction is available. This study's control is that guard with the
  originals supplied; its laws R1 to R3 are bounded-read relatives of that argument, extended to waiting.
- `TICK-BIRTHS-AND-SCARCITY-20261121-001` — a relative: the same guard on an eight-knot clock, with the originals supplied.
- `GENERATORS-20261120-001` — a relative: its fixed-map replay delivers births in other parent-respecting orders with the
  whole layer's plan supplied.
- `MEET-ORDERS-20261118-001`, `COPY-CLASS-20261118-001`, `MEET-TWIST-20261118-001` — unrelated (orders of meeting in
  betweenness structures).
- `ROUND-FREE-20261119-001` and `FRESH-DEMAND-20261120-001` — relatives: present-state laws are order-dependent; with the
  first layer's plan supplied every order agrees; demand follows from the parents' child lists alone.
- `COPYING-PARTS-20261123-001` — a relative: the laws with a ration fixed at birth, FLOOR1 among them, used here.

## Prior work outside the program

- Synchronizers (Awerbuch 1985) run a synchronous algorithm on an asynchronous network by local waiting.
- Lamport's logical clocks (1978) order events without a global clock.
- Confluence by critical pairs in graph transformation (Ehrig; Plump), and abelian networks (Bond and Levine 2016), are the
  standard settings for order-independence.

Three further names, each the literature's and given from memory, not checked:
- In Awerbuch's synchronizer a node is **"safe"** when every message it sent in the current pulse has arrived. A weaned knot
  is one all of whose parents are safe in this sense.
- The stored-previous-state simulation of synchronous by asynchronous automata (Nakamura 1974; Nehaniv 2004). These laws are
  an instance, with the written birth record as the stored state.
- **Mazurkiewicz traces**, for the commutation of independent events, which is what makes the order of births in different
  broods irrelevant.

Not searched beyond ticket C's note of the earlier study. What this would add is the least holder-step distance these growth
laws must read, and a case with waiting.

## Known before the freeze (disclosed)

The drafter of the definitions wrote a scratch prototype of every law here and ran it on every start below before this
freeze. The prototype is unreviewed, is not the study's engine, and its author does not write the study's code.
- Its complete rounds give the same structure as ticket A's engine of the earlier study after every round. The test was
  exact isomorphism, knots coloured by round of birth, for all twenty start and law pairs used below, rounds 1 to 5. Fewer
  rounds where the growth ends: 4 for the lone four-place knot, 2 for the seven-knot generator under CANCEL-RETIRE. The test
  rejected three altered controls.
- Each search ran on one core, under 120 s.
- "Every order" means the breadth-first search over memo keys finished. "Sampled" means at each step a uniform choice among
  the allowed births, seeds 0 to N − 1. "x-last" means the x-last orders of definitions section 4.
- "Least n" is the least number of births of an order ending in a mismatch. It is exact when found breadth-first; otherwise
  it is marked "found".
- Knots are numbered as in `growth.py`'s `from_stars` (the earlier study's ticket C), births from the first free number.

**Starts.**
- D2(n, 3) and Ring(5, 3): as the shared definitions, lines 145–151.
- Two-knot: `[[0,1,2],[0,3,4]]`.
- Three-knot: `[[0,1,2,3],[0,1,4,5],[2,3,6,7]]` (a dead knot with two members).
- Lone four-place: `[[0,1,2,3]]`.
- The seven-knot generator: the shared definitions, lines 152–153.
- **The start-clause counterexample** (seven knots): `[[1,2,3,7,8],[1,4,9,10],[2,5,11,12],[3,6,13,14],[4,15,16],[5,17,18],[6,19,20]]`.
  Knot 0 meets knots 1–3 once each and holds two loose; knot i (1–3) meets 0 and i + 3 and holds two; knots 4–6 hold two.
- **The cycle of eight with three extra dead knots**: D2(8, 3) plus three dead knots of the same kind, between members 0 and
  4, 1 and 5, 2 and 6, each sharing two distinctions with each of its members (in the literature's words, a cycle with three
  chords):
  `[[0,1,30,31,32,33,34,56,57],[4,5,2,3,35,36,37,60,61],[8,9,6,7,38,39,40,64,65],[12,13,10,11,41,42,43],[16,17,14,15,44,45,46,58,59],[20,21,18,19,47,48,49,62,63],[24,25,22,23,50,51,52,66,67],[28,29,26,27,53,54,55],[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15],[16,17,18,19],[20,21,22,23],[24,25,26,27],[28,29,30,31],[56,57,58,59],[60,61,62,63],[64,65,66,67]]`.
  - Members 0–7 are knots 0–7; the dead knots between consecutive members are 8–15; the three extra dead knots are 16–18.
  - Members 0, 1, 2, 4, 5, 6 have nine places (six shared, three loose); members 3 and 7 have seven; every dead knot has four.
  - Every knot passes the parity knot test of ticket A's engine (both methods) on the start and after each of rounds 1 to 5.
  - Under (RATION-3, CANCEL-WAIT), ticket A's engine gives: round 1, 13 births (11 joins and the offshoots of members 3 and
    7); in round 2 all 11 joins are short; in round 3 seven are short again; in round 4 the join of members 1 and 5 waits a
    third time.

**The laws on every start** (the cutoff is "within round r", definitions section 4):

| Start · law | Cutoff | R1 | R2 | R3 | R3L | R0 | Control |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D2(4,3) · RATION-3, CANCEL-WAIT | round 1 (28 births) | differs: 67,353 keys, 1,332 mismatches; least 7 | every order matches (65,803 keys, 24.5 s) | every order matches (65,791 keys, 19.3 s) | differs: 32 mismatches; least 12 | every order ends in a mismatch or underbuilds; least 3 | every order underbuilds, ending after 20 births |
| D2(5,3) · same | round 1 | least 7; 30 of 60 sampled and 19 of 20 x-last differ | 60 of 60 sampled and 20 of 20 x-last match | as R2 | least 14; 60 of 60 sampled match | least 3 | 60 of 60 underbuild |
| Ring(5,3) · same (members meet members) | round 1 for least n; round 2 for 40 sampled | least 7; 15 of 40 sampled and 7 of 15 x-last differ | 40 of 40 sampled and 15 of 15 x-last match | as R2 | least 3; 39 of 40 differ | least 2 | 40 of 40 underbuild |
| Cycle of eight with three extra dead knots · same | round 1 | least 7 | least 13 (8,435 keys, 2.8 s); 27 of 200 sampled and 2 of 32 x-last differ | no mismatch in any order up to 18 births (318,780 keys, unfinished); 200 of 200 sampled and 32 of 32 x-last match | least 17 | least 3 | no mismatch in any order (8,206 keys); 200 of 200 underbuild |
| Two-knot · FLOOR1, CANCEL-RETIRE | round 2 / 3 every order; round 4 sampled 40 | every order matches (517 / 17,403 keys, 3.2 s); 40 of 40 | every order matches (357 / 16,435); 40 of 40 | as R2 | differs: least 3; 26 of 40 differ | least 2 | every order matches (152 / 4,247); 40 of 40 |
| Two-knot · FLOOR1, CANCEL-OFFSHOOT | round 2 every order; round 3 unfinished; round 4 sampled 40 | every order to round 2 (841); round 3: no mismatch in 95,621 keys, unfinished at 35 s; 40 of 40 | every order to round 2 (729); round 3: none in 90,554, unfinished; 40 of 40 | as R2 (92,858, unfinished) | least 3; 31 of 40 differ | least 2 | every order to round 3 matches (37,258 keys, 6.3 s); 40 of 40 |
| Three-knot · FLOOR1, CANCEL-RETIRE | round 2 / 3 every order; round 4 sampled 40 | every order matches (128 / 528); 40 of 40 | every order matches (124 / 364); 40 of 40 | as R2 | every order to round 2 matches (124); 40 of 40 | least 2 (a wrong retirement) | every order matches (79 / 159); 40 of 40 |
| Three-knot · FLOOR1, CANCEL-OFFSHOOT | round 2 / 3 every order; round 4 sampled 40 | every order matches (409 / 9,260, 1.7 s); 40 of 40 | every order matches (407 / 8,026); 40 of 40 | as R2 | differs: least 6; 13 of 40 differ | least 3 | every order matches (216 / 2,807); 40 of 40 |
| Two-knot · ORD, STALL | round 3 every order | every order matches (4,624) | every order matches (3,364) | every order matches (3,136) | not run before the freeze | least 2 | every order matches (1,350) |
| Lone four-place · ORD, STALL | round 4 (through the closing birth) every order | every order matches (84) | every order matches (84) | every order matches (84) | not run before the freeze | least 1 | every order matches (84) |
| D2(4,3) · ORD, STALL | round 2, 30 sampled | 30 of 30 | 30 of 30 | 30 of 30 | not run before the freeze | 30 of 30 differ; least 1 | 30 of 30 |
| Ring(5,3) · ORD, STALL | round 2, 30 sampled | 30 of 30 | 30 of 30 | 30 of 30 | not run before the freeze | 30 of 30 differ; least 1 | 30 of 30 |
| Start-clause counterexample · RATION-3, CANCEL-WAIT | round 1 | least 2 | least 2 | least 2 | least 2 | least 2 | underbuilds (216 keys) |

Beyond the table, sampled, with R1, R2 and R3 only:
- D2(4,3) under (RATION-3, CANCEL-WAIT) through round 3: R2 and R3 match in 40 of 40 orders; R1 differs in 20 of 40 (least
  9 found).
- Ring(5,3) and the seven-knot generator under (FLOOR1, CANCEL-RETIRE) and (FLOOR1, CANCEL-OFFSHOOT) through round 3: all
  three laws match in 40 of 40 orders on each start and treatment.

The least differing orders:
- **R1 on D2(4,3):** `(0,) (0,1) (0,3) (1,) (1,2)`, then two offshoots of knot 9, the join of members 0 and 1.
  - Its brood-mates' waits are not yet visible, because members 2 and 3 are still members. So it makes two offshoots where
    the rounds give one.
  - The same mechanism holds on D2(5,3) and on Ring(5,3). On the cycle of eight with three extra dead knots the order is the five
    joins with member 0 or member 1 as a parent, `(0,1) (0,4) (0,7) (1,2) (1,5)`, then two offshoots of knot 19, the join
    of members 0 and 1.
- **R3L on D2(n,3):** the start's 2n births, three offshoots of one start offshoot, then a join of a waiting join with
  another start offshoot. With that offshoot dead, the present part of the waiting joins and the other offshoots looks
  untouched, and two of the joins no longer read as short.
- **R3L on the two-knot start:** knot 1's two offshoots, then knot 0 joins one of them through the dead knot 1.
- **R3L on the three-knot start, CANCEL-OFFSHOOT:** `(2,) (1,2) (1,)`, the two offshoots of knot 5, then `(3,4)`. Under
  CANCEL-RETIRE the short join is barred when its brood is first read, so no later present part can contain it.
- **Every brood law on the start-clause counterexample:** two offshoots of knot 0.
  - In round 1 knot 0 waits (three groups, two holdings). In round 2 of the complete rounds the dead knots 1–3 meet it and
    their joins, and it makes one four-parent join and one offshoot.
  - The start clause reads it alone and gives two offshoots. The brood of the joins of knots 1–3 is also read without it
    (definitions section 2.2).
- **R2 on the cycle of eight with three extra dead knots.**
  - The least order found breadth-first is every start birth except member 7's offshoot, then the join of knots 22 and 23
    (the joins of members 1 and 2, and of members 1 and 5).
  - The advisor's order is every start birth except member 3's offshoot, then the join of the joins of members 0 and 1, and
    of members 1 and 5. It is the image of the first under the relabelling i ↦ 2 − i (mod 8) of the members, which maps the
    start to itself. Run directly, it also mismatches at birth 13.
  - The mechanism, in the advisor's account (followed by hand by the thread; not traced in the prototype): in its order the joins of members 2 and 3 and of
    members 3 and 4 are not weaned, because member 3 is still a member. They read as not short in their second reading. R2's
    guard does not reach them, so the join of members 0 and 1 reads its third roster as only the joins (0,1), (1,5) and
    (5,6).

**The family T(d)** under (RATION-3, CANCEL-WAIT), through round 1:

| Start | d = 2 | d = 3 | d = 4 | d = 5 | d = 6 to 10 |
| --- | --- | --- | --- | --- | --- |
| D2(4,3) | least 7 | least 10 | 30 of 30 sampled and 16 of 16 x-last match; every order: no mismatch in 65,416 keys, unfinished at 110 s | 30 of 30 match | 30 of 30 match, each d |
| D2(6,3) | 30 of 30 differ; least 11 found | least 11 | 30 of 30 and 24 of 24 x-last match | 30 of 30 | 30 of 30, each d |
| D2(8,3) | 30 of 30 differ; least 14 found | 30 of 30 differ; least 17 found | 30 of 30 and 32 of 32 x-last match | 30 of 30 | 30 of 30, each d |
| D2(12,3) | 12 of 12 differ; least 24 found | 12 of 12 differ; least 25 found | 12 of 12 and 48 of 48 x-last match | 12 of 12 | 12 of 12, each d |
| Cycle of eight with three extra dead knots | 30 of 30 differ; least 10 found | 30 of 30 differ; least 14 found | least 14 | least 14; 32 of 32 x-last differ | 30 of 30 match each d; at d = 6, 32 of 32 x-last match |

- The least d with no mismatch found is 4 on every D2 start, and 6 on the cycle of eight with three extra dead knots.
- After round 1 of the cycle of eight with three extra dead knots, the round-1 brood's extent (definitions, section 3) from the join
  of members 1 and 5, the knot that waits three times, is 6 holder steps. Its greatest extent from any of its knots is 8.

**Groups of three or more** (for P13), in the rounds read by the reference through round 6:
- under (FLOOR1, CANCEL-RETIRE) and (FLOOR1, CANCEL-OFFSHOOT): none on the two-knot and three-knot starts or on Ring(5,3);
  one group of three in round 2 on the seven-knot generator;
- under (RATION-3, CANCEL-WAIT): from round 4 on D2, Ring(5,3) and the cycle of eight with three extra dead knots (in the parts that
  come apart), and a group of four in round 2 on the start-clause counterexample;
- under (ORD, STALL): from round 3.

Not searched for every order: D2(5,3), Ring(5,3) and D2(n,3) for n ≥ 6 through round 1 (about 10⁶ keys or more), and
anything past round 1 on D2 or Ring under CANCEL-WAIT.

## Settled by construction (stated, not tested)

- **The brood argument.** Under RELEASE a member that makes any birth spends every usable distinction in the one roster in
  which it acts, so all children of a parent are born in one complete round. Past the start a knot meets only its parents
  and its children. Hence an all-weaned brood's roster at birth is the part the complete rounds read in the round after its births
  (definitions, section 1.4). This is an argument for the referee.
- **The memo key** is valid while every birth and barring has matched (definitions, section 4).
- **Checks, true by construction** (run and reported, but they cannot fail unless the code departs from the definitions):
  - P12: under (ORD, STALL) a new knot receives at least its owing in the next roster.
  - The control underbuilds under waiting: a waiter is given nothing to do (P9, first half).
  - R3 on a start past its start: an all-weaned brood's plan is the complete rounds' plan, by the brood argument, issued in some
    order. R3's parts of P1, P2 and P14 on D2 and on the cycle of eight with three extra dead knots are checks of this; on Ring(5,3)
    they also depend on the start clause.
  - All brood laws share the start clause, so they differ alike on the start-clause counterexample (P8).

## What is supplied

Listed in the definitions, section 5:
- the parent relation written by each birth;
- the start clause;
- the waiters' recursion and its all-short test;
- the barring;
- the closing bit read on the present structure;
- the guards, with T(d)'s reading within d;
- the control's supplied originals;
- the comparison, with ticket A's engine as reference, its cutoff, and the three kinds of order;
- the starts.

This ticket swaps the guard (five laws, the family T(d) and a control), the ration and treatment (three families), and the
start. It does not swap the parent relation: a law that reads only holders, with no record of who was made from whom, is
outside it.

## What a pass would and would not show

The parent relation, with RELEASE, carries the round. All children of a parent are born in one round, so a brood is exactly
one part's round, and h₀ rebuilds a roster that never coexists in a serial run. The plan is the complete round replayed on
that record.

- **A pass shows** that the global scheduler can be removed, given a written birth record, spending in a single act, and
  death as the signal of completion.
- **It does not show** that the round is dispensable, that holders alone suffice, or that reading is bounded under repeated
  waits.
- **It says nothing** for HOLD, FILLERS or CAP-3 (the record's actual two added rules), for starts where a knot that acts
  meets a knot that waits, or past the round cutoff.

## Runs (frozen)

1. **The gate** (definitions, section 4): the engine's complete rounds against ticket A's engine, structure by structure, for
   every start and law below, rounds 1 to R, before any search.
2. **Starts, laws and cutoffs.**
   - Every row of the first table under "Known before the freeze", with every law R0, R1, R2, R3, R3L and the control, at
     the cutoff given there. R3L under (ORD, STALL) is reported without a prediction.
   - T(d) for d = 2 to 10, on D2(n, 3) for n = 4, 6, 8, 12 and on the cycle of eight with three extra dead knots, through round 1
     under (RATION-3, CANCEL-WAIT).
3. **Orders**, for every start, law and cutoff:
   - every order, breadth-first over memo keys, reported as finished or not, with the number of births to which every order
     was searched. The cap on keys is ten million for the rows of the first table and one million for T(d) and for item 4. A
     search may stop once the level of its first mismatch is complete; the least number of births to a mismatch is then
     exact;
   - 200 sampled orders (seeds 0 to 199);
   - every x-last order.
4. **Beyond the first table.**
   - R1, R2 and R3 on D2(4, 3) under (RATION-3, CANCEL-WAIT) through round 3. The returned ring's joins there are new knots
     that wait once; no knot waits twice.
   - R1, R2 and R3 under (FLOOR1, CANCEL-RETIRE) and (FLOOR1, CANCEL-OFFSHOOT) on Ring(5, 3) and on the seven-knot generator
     through round 3 (for P13).
   - Both with the orders of item 3.
5. **Reported in every run:**
   - counts of runs that match, mismatch and underbuild;
   - the least differing order, exact when the breadth-first search finished, otherwise the least found, so marked;
   - every firing of the closing bit, and whether the matched reference knot received none;
   - whether any roster read (the start roster, a brood's roster at birth, a waiters' roster) has a group of three or more;
   - for T(d), the least d with no mismatch on each start, for each kind of order.

## Predictions (frozen)

Marked (a) already seen in the drafter's scratch runs, (b) a hand prediction that was not run, (c) open, reported without a
prediction. A **check** is true by construction (see "Settled by construction").

- **P1 (a; R3's part a check)** R2 and R3 build what the complete rounds build through round 1 on D2(4,3) under
  (RATION-3, CANCEL-WAIT). (b) The same through round 3, in the sampled and x-last orders. *Fails when* an order differs.
- **P2 (a for sampled and x-last orders; b for every order)** R2 and R3 build what the complete rounds build through
  round 1 on D2(5,3) and Ring(5,3). *Fails when* an order differs.
- **P3 (a)** R1 differs on D2(4,3), D2(5,3), Ring(5,3) and the cycle of eight with three extra dead knots, with least differing order 7
  births: a waiter makes a second offshoot where the rounds give one. *Fails when* the least is not 7, or the first mismatch
  is not a waiter's surplus offshoot.
- **P4 (a for n = 4, 5; b for n = 6)** R3L differs on D2(n,3), with least differing order 2n + 4 births (16 at n = 6),
  relative to the cutoff. *Fails when* a shorter or longer least order is found.
- **P5 (a; b for the two-knot start under CANCEL-OFFSHOOT through round 3)** R1, R2 and R3 build what the rounds build:
  - through round 3 on the two-knot and three-knot starts under (FLOOR1, CANCEL-RETIRE), and on the three-knot start under
    (FLOOR1, CANCEL-OFFSHOOT);
  - through round 2 on the two-knot start under (FLOOR1, CANCEL-OFFSHOOT), and through round 3 there.
  *Fails when* an order differs.
- **P6 (a)** R3L differs at the least orders disclosed, each relative to the cutoff:
  - 3 births on the two-knot start under both treatments;
  - 3 births on Ring(5,3);
  - 6 births on the three-knot start under CANCEL-OFFSHOOT;
  - 17 births on the cycle of eight with three extra dead knots;
  - but not on the three-knot start under CANCEL-RETIRE through round 2.
  *Fails when* any of these differs.
- **P7 (b; a on the two small starts)** Under (ORD, STALL), R1, R2 and R3 build what the rounds build in every order:
  - on D2(4,3) and Ring(5,3) through round 2;
  - on the two-knot start through round 3 and on the lone four-place knot through round 4, where the closing bit
    fires exactly at the reference's closing birth.
  *Fails when* an order differs, or the closing bit fires where the reference's does not, or not where it does.
- **P8 (a; partly a check)** R1, R2, R3, R3L and R0 differ on the start-clause counterexample at 2 births; the control underbuilds there. *Fails when* one of them matches, or the control mismatches.
- **P9 (first half a check; second half a)** The control underbuilds under CANCEL-WAIT on every registered start with a
  waiter. It builds what the rounds build under (FLOOR1, CANCEL-RETIRE), (FLOOR1, CANCEL-OFFSHOOT) and (ORD, STALL) at every
  cutoff searched. *Fails when* the second half fails.
- **P10 (a)** R0 differs on every start of the first table, at 1 to 3 births, relative to the cutoff. *Fails when* some
  start matches.
- **P11 (b, the advisor's estimate; a in sampled and x-last orders)** Through round 1 under (RATION-3, CANCEL-WAIT):
  - the least d for which T(d) has no mismatch is 4 on D2(n, 3) for n = 4, 6, 8 and 12;
  - on the cycle of eight with three extra dead knots, no d up to 10 smaller than the brood's extent suffices for the knot that waits
    three times. Known before: the prototype finds the least d to be 6, the brood's extent from that knot (the join of
    members 1 and 5).
  *Fails when* the least d on a D2 start is not 4, or some d below 6 has no mismatch on the cycle of eight with three extra dead knots.
- **P12 (a check)** Under (ORD, STALL) no member of any brood's roster at birth is short. *Fails when* one is.
- **P13 (c)** Whether R1 is exact under CANCEL-RETIRE or CANCEL-OFFSHOOT where a roster read has a group of three or more.
  There, owing can fall as a brood fills in, so R1 could read a brood-mate as short too early. Reported: whether any roster
  read in any run has such a group, and R1's verdict there. Known before: among the registered starts under FLOOR1 only the
  seven-knot generator has one (round 2), and R1 matched there in 40 sampled orders through round 3.
- **P14 (a; R3's part a check)** On the cycle of eight with three extra dead knots under (RATION-3, CANCEL-WAIT), R2 differs
  within round 1, at 13 births (the advisor's order, and its image under the relabelling above), and R3 builds what the rounds
  build through round 1.
  *Fails when* R2 matches in every order, its least differing order is not 13 births, or R3 differs.

Left open, with no run: whether a start clause exists that passes the start-clause counterexample within a bounded
holder-step distance. It would have to repair both wrong readings (definitions, section 2.2).

A result that fails is reported as it is. A law that builds what the rounds build in every order searched has done so to the
stated round only. No statement about every round is made without an argument, which the result note would mark as such.

## Runs and stop rule

- **One engine** is written for this study from the frozen text. Its complete rounds pass the gate against ticket A's engine
  (definitions, section 4) before any search.
- **Disagreements.** If the engine and the disclosed prototype disagree on a verdict or a least differing order, the
  disagreeing order is replayed birth by birth. Each birth is listed with its parents, its fresh count, and the reference knot
  it matches or fails to match. The listing decides, and the disagreement is reported as a finding.
- **Resources.** Each search is expected to take under ten minutes and 8 GB on one process. Anything longer goes through the
  shared runner with a row in the long-running index.
- **Stop.** The study stops when every registered run is done and every prediction has a verdict.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.
- **The advisor.** The advisor model (Claude Fable 5.2, no tools) reviewed the first draft cold before this freeze, and then
  the words chosen after its review (`research/LOCAL-ROUND-20261123-001/advisor/`). From its review: the test for a part
  that waits for ever, the scope of the start clause, the reference taken from ticket A's engine, the family T(d) in place of
  an undefined prediction, the cycle of eight with three extra dead knots (its counterexample to R2, found by hand), the
  x-last orders, the predictions marked as checks, and the section on what a pass would show. The drafter then ran the
  prototype on the new start and on T(d); what it found is disclosed above, including where it differs from the advisor's
  estimate (a least d of 6, not 10, on the new start).
