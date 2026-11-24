You are asked to review, cold, the design of a three-part study before it is frozen. You have no tools; answer from this text alone. Be a critical colleague: find what is wrong, ambiguous, untestable, trivially true, or confounded. Do not praise. Where you think a definition will produce a different behaviour than the author expects, work the smallest case by hand and say so.

Context in one paragraph. A research program grows structures of "knots" (parity constraints, or not-all-equal constraints, each on a set of binary "distinctions"; a distinction is held by one or two knots). The established growth law ("ordinary growth", defined below as the law (ORD, STALL)) proceeds in complete synchronous rounds. A pilot found that with two rules added by hand (a cap of three on fresh distinctions; a knot that cannot pay waits instead of stalling the round) a ring of an odd number of knots returns to its starting live roster every two rounds while giving off the same finite parts, and with a third added rule those parts end. The study below (tickets A, B, C) is meant to (A) replicate this with independent code on real knots, run the canonical knot test on every knot, test not-all-equal, and swap each added rule; (B) ask what "references" contribute: dead knots as witnesses, knots that wait, and whether a knot's holdings give the round it was made in; (C) remove the complete rounds: one birth at a time under serial laws and priorities. The owner's standing rules: every scaffold (anything added by hand) must be named and swapped before a result is claimed about the model; never say typical or rare without naming the weighting; frozen predictions must be falsifiable; negative results are kept.

Please answer these questions, numbered:
1. Definitions file: is any definition ambiguous or internally inconsistent? In particular (a) the group rule; (b) the treatment CANCEL-WAIT together with the demand lookahead of step 6 (a waiting member is kept "with what it holds" while every new knot counts as holding one); (c) FILLERS; (d) "returns", "gives parts off", "in balance"; (e) the serial law (open groups, short, moves, the two witness rules, the rations, the priorities, "settled", "build the same to depth D", "returns k times").
2. "Settled by construction" claims in A, B and C: is each actually true as stated? Especially: "Parts act alone at positive age … hence if a part at positive age returns after T rounds giving parts off, it returns every T rounds without end"; "A knot's verdict under parity is fixed at its birth round whenever every later birth receives a fresh distinction"; the derivation r = f + 2p − 3 − 2e in B; "The cohort law builds what the complete rounds build" in C.
3. Predictions: which are trivially true given the definitions, which are not falsifiable as worded, and which are likely false? For C's P3 and P4 work the cycle of five through dead knots (D2(5,3)) by hand under the serial law L2 (RATION-3, DEAD) with the DEPTH priority, offshoots first and joins first, and say whether you agree that offshoots-first reproduces the complete rounds under (RATION-3, CANCEL-WAIT) and joins-first cannot.
4. Confounds and missing controls: what would make a positive result an artefact of the code or of a definition (for example of the isomorphism test, of the lineage rule in "returns", or of the bounds on rounds and knots)? What single extra control would you add to each ticket?
5. Is anything here likely to be already known under another name (beyond what the "Prior work outside the program" sections cite)? Name it.
6. Words. The study uses: member, part, witness, witnessed set, adjacent, short, waits, ends, join, offshoot, ration, treatment, usable, never used, returns, gives parts off, comes apart, in balance, settled, ring part, cohort law, serial law, move, depth, priority. The program's rules: one word per meaning; no words taken from two- or three-dimensional space for its own objects (ring and cycle are the records' established words here). Flag any word that is used in two senses in the text, or that collides with a standard technical meaning in a way that would mislead.

=== FILE: definitions.md ===
# A ring in balance: definitions shared by the three studies

Epic `RING-IN-BALANCE-20261123-001`, 2026-11-23. Frozen with the three pre-registrations, before any of the study's code is
written. Tickets A, B and C cite this file and add only what is their own. The canonical K1–K3 test is unchanged. Words are the
glossary's (Intuitions guide); the growth records' "junction" is a knot, their "growing end" is the live roster, and their
"witness" is kept here as the records' word for a knot that meets two or more members of the live roster.

## Structure

- A **structure** is a finite set of knots, each holding a set of distinctions, its **places**. A knot has at least three places.
  A distinction has one or two **holders**. It is **loose** with one holder and **shared** with two.
- Two knots **meet** when they share a distinction. A knot is **live** while it holds a loose distinction and **dead** otherwise.
- A **start** is a structure given before any birth. It is written as its list of knots, each a list of distinction numbers
  (the records' stars). Start knots have **depth** 0; a new knot has depth one more than the greatest depth of its parents.
- Under a law with never-used fillers, and after a knot ends, a loose distinction can be **never used**. Every other loose
  distinction is **usable**.

## The live roster

- The **members** of the live roster are the knots holding at least one usable loose distinction. Write h(u) for the number of
  usable loose distinctions member u holds and k(u) for the number it holds that are never used.
- A **witnessed set** is the set of members that one knot of the structure meets, when it has at least two members. That knot
  is its **witness**; it may be dead or itself a member.
- Two members are **adjacent** when some witnessed set contains both. A **part** of the live roster is a connected component
  of adjacency. The roster is **at positive age** when no member meets a member.
- Two rosters, or two parts, are **the same** when a one-to-one renaming of members carries h, k and the family of
  inclusion-maximal witnessed sets of one onto the other.

## One complete round

A **law** is a knot law (parity or not-all-equal), a ration, a treatment and optional extras. One round, on real knots:

1. **Groups.** Take every inclusion-maximal set of at least three pairwise adjacent members that is contained in no single
   witnessed set, and every adjacent pair contained in none of those sets. These are the groups
   ([ORDINARY-DYNAMICS-20261120-001](../ORDINARY-DYNAMICS-20261120-001/end_operator.md), "The operator on the present end", step 1).
2. **Owing.** Member u owes one usable loose distinction to each group containing it. It is **short** when it owes more than
   h(u).
3. **Treatment of a short member.**
   - STALL: if any member is short, no birth is made and the growth has stalled.
   - CANCEL-BUD: every group containing a short member is cancelled; the short member makes an offshoot from each of its usable
     loose distinctions.
   - CANCEL-WAIT: every group containing a short member is cancelled; the short member **waits**: it makes nothing and keeps
     everything it holds.
   - CANCEL-END: every group containing a short member is cancelled; the short member **ends**: it makes nothing now or later,
     and its loose distinctions become never used.
4. **Joins.** Each group that is kept makes one new knot, a **join**, whose parents are its members; it takes one usable loose
   distinction from each.
5. **Offshoots.** A member that is not short, after paying its kept groups, makes one new knot of one parent, an **offshoot**,
   from each usable loose distinction it has left; this includes distinctions that cancelled groups would have taken. With the
   extra NO-BUD it makes none, and those distinctions become never used.
6. **Demand.** Count every new knot as a member holding one usable loose distinction, and keep the waiting members with what
   they hold. Form the groups of that roster as in step 1. The **demand** D of a new knot is the number of those groups that
   contain it.
7. **Fresh distinctions (the ration).** A new knot with p parents and demand D receives f fresh distinctions, each loose and held
   by it alone. With q = max(D, 3 − p, 1), the ordinary count:
   - ORD: f = q. CAP-k: f = min(q, k). RATION-k: f = max(k, 3 − p).
   - ONE-FEWER: f = min(q, max(3 − p, 0, q − 1)). FLOOR0: f = max(3 − p, 0). FLOOR1: f = max(3 − p, 1).
   - **Closing exception** (parity only, every ration): when the round makes exactly one new knot, no member waits and no
     distinction of the structure is never used, that knot receives none. Under not-all-equal there is no exception
     ([NAE-GROWTH-20261119-001](../NAE-GROWTH-20261119-001/nae_growth.md): the growth reads the knot law in this one place).
8. **Extras.**
   - FILLERS (never-used fillers): of a new knot's f fresh distinctions, min(f, D) are usable and the rest are never used.
   - PART-CLOSE: the closing exception read part by part: a new knot that is the only new knot made by its part of the roster, in
     a round in which no member of that part waits or ends, receives none.

The records' ordinary growth, the cheapest growth of lesson 8.1, is the law (ORD, STALL). **The two added rules** are the law
(CAP-3, CANCEL-WAIT). **The three added rules** are (CAP-3, CANCEL-WAIT, FILLERS). They were added by hand (assumption A224, a
scaffold). The pilot's program counted a short member by all its loose distinctions; the two readings agree, because a member
with a never-used distinction owes exactly its usable count in the one round it acts.

A distinction taken by a new knot becomes shared between its old holder and the new knot. Which of a member's usable loose
distinctions goes to which birth makes no difference up to renaming.

## One birth at a time

A **serial law** is a knot law, a ration that reads no next round, a witness rule and a priority. A **move** is one birth.

1. **Witness rule.** ANY: every knot can be a witness, as in a round. DEAD: only a dead knot can be a witness.
2. **Open groups.** Form the groups of the present roster as in step 1 of the round, with the witnessed sets the witness rule
   allows. A group is **open** when no knot already made has all of its members among its parents.
3. **Short.** A member is short when it is in more open groups than h(u). A short member makes nothing (it waits). Under the
   extra FIRST-COME, used only as a gate against the record, no member counts as short: every open group is a join move, and
   a member has an offshoot move when h(u) exceeds the number of open groups containing it.
4. **Moves.** Every open group with no short member is a join move. A member that is not short and holds more usable loose
   distinctions than the number of open groups without a short member that contain it has one offshoot move. The **depth** of
   a move is the greatest depth of its parents.
5. **Ration.** RATION-3: the new knot receives max(3, 3 − p) fresh distinctions. PRESENT-ORD: it receives max(d, 3 − p, 1),
   where d is the number of open groups containing it immediately after its birth, the new knot counted as a member before it
   receives anything (the present-state reading of [ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md)).
   PRESENT-CAP-3: min(max(d, 3 − p, 1), 3) with the same d. Closing exception, parity only: a move that takes every loose
   distinction of the structure, with d = 0 where d is read, receives none.
6. **Priority.** The next move is chosen among the moves available:
   - UNIFORM: each with equal chance.
   - DEPTH: least depth first. Its three tie rules: uniform; joins first; offshoots first (then uniform).
   - OLDEST: the move whose most recently made parent was made earliest; ties uniform. The order of making is the simulator's
     record, not the structure's.
   - FEWEST-PLACES: the move with the parent holding the fewest places; ties uniform.
   - MOST-LOOSE: the move with the parent holding the most usable loose distinctions; ties uniform.
   - LOOSE-WEIGHTED: each with chance in proportion to the usable loose distinctions its parents hold in all.
   Every random choice comes from a numbered seed; a share of seeds is a share under that priority's own weighting and under
   no other.
- The **cohort law** is the complete round made serial: the births of one round are made one at a time in a uniformly random
  order and receive their fresh distinctions when the round's last birth is made. It is the control.
- The knots of depth at most D are **settled** when every knot of depth less than D has no usable loose distinction. Two runs
  **build the same to depth D** when both are settled to D and their knots of depth at most D form the same structure up to
  renaming of knots and distinctions.

## Kinds of outcome

For a run of a start under a law through a stated number of rounds:

- It **stops** at round r when the roster after round r has no member. It **stalls** at round r under STALL when a member is short.
- A part Y of the roster after round s, at positive age, **returns** at round t > s when the members after round t that descend
  from Y (through parents, a waiting member descending from itself) include a part that is the same as Y. It **gives parts off**
  when those descendants form two or more parts. T = t − s is the period found.
- The roster is **in balance** from round s with period T when the whole roster after round t + T is the same as the whole
  roster after round t for every t ≥ s in the run.
- Otherwise the run **grows** to its bound with no return found.
- In a serial run a **ring part** is a part at positive age that is the same as the start's roster. The run **returns k times**
  when ring parts P_1, …, P_k appear at successive moments, pairwise without a common member, each member of P_{i+1}
  descending from members of P_i and P_1 from the start's members.

## The knot test

- **Parity.** Each knot is the rule that its places have even parity. A knot with place set S passes K1–K3 in the whole
  structure when the allowed states of the structure, restricted to S, are exactly the even assignments of S. Two methods are
  run and must agree on every knot. Ranks: with H the matrix over the field of two elements with one row for each knot, the
  rank of H less the rank of H with the columns of S removed is one (the records' test, ORDINARY-DYNAMICS, `rulers.py`). Cut:
  in the graph with one vertex for each knot and one for the outside, an edge between the two holders of each shared
  distinction and an edge to the outside for each loose one, deleting the knot leaves the rest connected.
- **Not-all-equal.** Each knot is the rule that its places are not all equal. A knot passes when the assignments of S that
  extend to an allowed state of the whole structure are exactly the assignments that are not constant, decided by a SAT solver
  for each of the 2^|S| assignments (the records' test, ORDINARY-DYNAMICS, `source_cert.py`).
- **Extension.** A round, or a move, extends when every allowed state of the structure before it is the restriction of an
  allowed state after it.

## Named starts

- **Ring(n, a).** Knots 0 to n − 1. Knot i shares one distinction with knot i + 1 (mod n) and holds a loose distinctions.
  Ring(5, 3) is the start of the golden-ratio eddy.
- **Cycle through dead knots, doubled, D2(n, a).** Members 0 to n − 1, each holding a loose distinctions, and dead knots
  w_0 to w_{n−1}; w_i shares two distinctions with member i and two with member i + 1 (mod n), so w_i has four places and its
  witnessed set is {i, i + 1}.
- **Cycle through dead knots in a ring of their own, DW(n, a).** As D2 with single meetings: w_i shares one distinction with
  member i, one with member i + 1, one with w_{i−1} and one with w_{i+1}.
- **The seven-knot generator.** Stars [0,1,2,9,10,11], [0,1,3], [4,5,12,13,14], [6,7,15,16,17], [2,3,4,6,18,19,20], [7,8,21,22],
  [5,8,23,24] ([GENERATORS-20261120-001](../GENERATORS-20261120-001/source.md)).

## What is supplied by hand

The complete round (assumption A104); every ration other than ORD, every treatment other than STALL and both extras (A224); the
serial laws, their witness rules and their priorities; the starts; the reading of a part as a thing (as in A125); the bounds on
rounds, moves and knots; and each weighting named where a share is given. Each study says which of these it swaps.

=== FILE: ticket A pre-registration ===
# Does a ring of knots return and give parts off, on real knots? Pre-registration

Ticket `RING-IN-BALANCE-20261123-001A` of epic `RING-IN-BALANCE-20261123-001` (sub-goal B315; goals G18 with G17 and G5),
2026-11-23. Frozen before the study's code is written. Code by a helper agent from this text and
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) alone, without reading the pilot's programs; the
thread compares its output with the pilot's afterwards. The canonical K1–K3 test is unchanged.

## The question

An exploratory pilot of 23 November 2026 found that under two rules added by hand to the cheapest growth, a ring of an odd
number of knots comes back to its start every two rounds while the same finite parts come apart from it, and that a third added
rule makes those parts end ([Intuitions lesson 8.7](../../publication/knotlab/INTUITIONS.md#87-generators-and-folds-of-emergence),
"Balance"). Ordinary growth cannot do this: its parts never come apart, and only finitely many lasting packets of any fixed
width can be released. The pilot ran on rosters with no distinctions in them, was not pre-registered and was not refereed. This
study repeats it with independent code on real knots, and asks what the pilot left open: whether every knot made under the
changed laws passes the knot test in the whole structure, whether not-all-equal behaves the same, and what happens when each of
the three added rules is swapped for another. It matters to G18 because it would be the first growth law of the program under
which a fixed finite thing is made again and again, and the first in balance.

## In standard terms

A synchronous graph-rewriting system on hypergraphs (knots are hyperedges over distinctions, each distinction in at most two
knots) with a resource cap and a blocking rule. The object is a periodic configuration that emits a fixed finite pattern each
period: an oscillator with output, the cellular automaton literature's gun. The population is rings (cycles) of n hyperedges
with a fixed number of pendant vertices each. The quantities are the period, the emitted pattern, and whether each hyperedge
is a minimal dependency of the cycle space (parity) or of the not-all-equal constraint system.

## Prior work in the program

Searches, each with `--until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`:

`python3 -B scripts/track.py objects "ring of knots that returns to its start while parts come apart" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "oscillator emitting a fixed finite pattern, glider gun, growth with a cap on fresh distinctions" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "ring of five knots three loose distinctions golden-ratio eddy" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "knot test at every birth under a changed growth law" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`

- `JOIN-GROWTH-20261118-001` — a relative: rings with trees joined to them under ordinary growth, and their return equation
  for the rate. "Return" there is a lap of the unrolled ring, not a roster coming back. Same starts, other law.
- `FREE-READ-20261118-001`, `CUMULANT-DIST-20261118-001` — unrelated (distances read from states).
- `ROUND-FREE-20261119-001` — a relative: ordinary growth without rounds. Taken up in ticket C.
- `ORDINARY-DYNAMICS-20261120-001` — the same object under the ordinary law: the round as a map on the live roster. This study
  takes its definition of a round word for word and changes the ration and the treatment of a short knot.
- `KNOT-CAP-20261117-001` — a relative: caps on knots per distinction in growth by betweenness, a different growth rule; its
  caps stop growth or leave it, and none returns.
- `IDLE-PHASE-AND-TREE-CLOSURE-20261121-001` — a relative: a cap on a start's extra loose distinctions under ordinary growth,
  and which trees then close. A cap on starts, not on births.
- `FRESH-DEMAND-20261120-001` — a relative: two present-state schedules; taken up in ticket C.
- `RING-CORES-20261119-001` — same population under the ordinary law: the ring of five with a leftover distinction on every
  knot grows by the golden ratio (proved). This study's control.
- `DROPPED-JUNCTION-20261119-001`, `LOOP-CATALOGUE-20261119-001` — relatives: which loops feed themselves under ordinary
  growth. Not used.
- `REVIEW-LEADS-20261123-001` (ticket D) — a relative: two copies of a ring clock on one donor one loose distinction short,
  one birth at a time. Scarcity there is in the start; here it is in the law. Taken up in ticket C.
- `INFLUENCE-CONE-20261120-001`, `GENERATORS-20261120-001`,
  `UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001` — relatives. GENERATORS is the direct predecessor: generators under
  ordinary growth, whose packets grow and whose parts never come apart
  ([components](../GENERATORS-20261120-001/components.md)); `COPIES-AND-MEETINGS-20261120-001` bounds its lasting packets.
- `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` (frozen the same day by another thread) — another treatment of a short knot: it
  pays with a shared distinction. Not among this study's treatments; a candidate for a later swap.
- The pilot itself is outside the index: [note](../../docs/prompts/2026-11-23_balance_pilot.md) (private).

## Prior work outside the program

- Conway's Life has guns: Gosper's glider gun (1970) returns every 30 steps and emits one glider. That is on a board with a
  clock. The study asks for the same on a structure that makes its own places.
- Growth by graph rewriting with a cap can replicate: the Wolfram Demonstrations Project's "Self-Replicating Graphs" describes
  a rule with a degree cap of four under which one edge grows to twelve vertices and then breaks into four edges that repeat.
  Graph-rewriting automata that reproduce are studied by Tomita, Kurokawa and Murata (Artificial Life 13, 2007). Read from
  search summaries only, not in full.
- Not found: a rewriting rule on parity or not-all-equal constraint systems with a ration and a waiting rule, or any statement
  that the emitted pieces are minimal dependencies. Searched 23 November 2026 with the phrases "graph rewriting oscillator
  emitting copies", "glider gun analogue graph grammar" and "self-replicating structure resource limit"; no claim of novelty
  is made beyond the program's own records.

## Known before the freeze (disclosed)

The pilot's two programs (the helper's `roster.py` and the thread's `own_check.py`) and the public site's port were run before
this freeze. They give, on rosters without distinctions or on the ring's stars: the return every two rounds for cycles of 4 to
12 members; live knots and parts 5/1, 10/1, 15/6, 25/6, 35/11, 50/11, 65/16 for the ring of five under the two added rules
and 5/1, 10/1, 15/6, 10/1, 15/6 under the three; no return for rings of four and six knots; a return for the ring of eight as
two cycles of four; and the search of 56 laws on 2,400 starts. Predictions P1 to P5 and P8 are therefore expected to hold and
test the independent code and the real knots. P6, P7, P9 and P10 were not computed by anyone before this freeze.

## Settled by construction (stated, not tested)

- **Parts act alone at positive age.** When no member meets a member, the groups, the owing, the births, the demand and the
  fresh counts of a part depend only on that part, except for the closing exception, which needs the round's sole birth. A
  new knot meets only its parents, and after a round every parent that made a birth has spent every usable distinction, so the
  next roster is again at positive age and the descendants of two parts are never adjacent. Hence if a part at positive age
  returns after T rounds giving parts off, it returns every T rounds without end, and gives off the same parts each time.
- **A knot's verdict under parity is fixed at its birth round** whenever every later birth receives a fresh distinction: a
  rule with a place that no other rule holds removes no allowed state of the earlier structure.
- **Under parity a set of loose distinctions is constrained only when it is all of them** (the sum of every knot's rule;
  ORDINARY-DYNAMICS, step 4). So the closing exception is the only case in which a birth's rule is already implied.
- Under the ordinary law no part comes apart or returns giving parts off
  ([GENERATORS, components](../GENERATORS-20261120-001/components.md)); the engine is checked against this, not this against
  the engine.

## What is supplied

The complete round (A104), the three added rules and every other ration, treatment and extra (A224), the rings, the bounds,
and the reading of a part as a thing. This ticket swaps the three added rules. The complete round is swapped in ticket C and
the start in ticket B.

## Runs (frozen)

All under parity unless stated. R is the last round run. A run also stops when the structure passes 6,000 knots.

| Run | Starts | Laws | R |
| --- | --- | --- | --- |
| A1 | Ring(n, 3), n = 3 to 16 | the two added rules; the three added rules; ordinary | 12; 20; 8 |
| A2 | Ring(n, 3), n = 5, 7, 9, 11, 13, 15 | the two and the three added rules: knot test and extension test for every knot at every round | 12 |
| A3 | Ring(5, 3), Ring(7, 3) | the two and the three added rules under not-all-equal: births compared with parity at every round; the not-all-equal criterion for every knot | 12 for births; 6 for the criterion |
| A4 | Ring(n, 3), n = 5, 7, 9 | 70 laws: rations ORD, ONE-FEWER, FLOOR0, FLOOR1, RATION-2, RATION-3, RATION-4, CAP-2, CAP-3, CAP-4, each with STALL, CANCEL-BUD, CANCEL-WAIT, CANCEL-END, and with STALL, CANCEL-WAIT, CANCEL-END under NO-BUD; knot test through round 6 | 16 |
| A5 | Ring(n, a), n = 5, 7, a = 2, 4, 5 | the two and the three added rules | 12; 20 |
| A6 | Ring(n, 3), n = 5, 7, 9 | (CAP-3, CANCEL-WAIT, PART-CLOSE) | 20 |

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate. Under the ordinary law the engine gives births 10, 15, 25, 40, 65, 105 for Ring(5, 3), five births every round for Ring(5, 2), and births 8, 12, 19, 32, 56 with 25, 42, 75, 140, 269 fresh distinctions in rounds 1 to 5 for the seven-knot generator (GENERATORS, source note); no part comes apart in any ordinary run; on every run of A1 its members, parts and loose counts each round equal those of the pilot's two programs (under the three added rules counting as members only knots with a usable distinction); the two parity methods agree on a structure with a planted failing knot; and with CAP-4 in place of CAP-3 the ring of five grows as under the ordinary law. | any fails |
| P1 | Under the two added rules, for every odd n from 5 to 15 and every even round t from 2 to 12: the roster is at positive age; the n knots that waited in round t form one part; that part has n members with three loose distinctions each and n witnessed pairs in one cycle, the same as the start's roster. | any n and t fails |
| P2 | For the same n and t, the members after round t + 2 that descend from that part form n + 1 parts: one the same as it, and n each of two members with two loose distinctions in one witnessed set. | any fails |
| P3 | Under the two added rules every part given off is the same, s rounds after it came apart, as every other at the same s, and has s + 2 members, for s from 0 to 10 and n = 5, 7, 9. | two parts of one age differ, or a count differs |
| P4 | Under the three added rules, for every odd n from 5 to 15 the roster is in balance from round 1 with period two through round 20, with 2n members in one part after odd rounds and 3n members in n + 1 parts after even rounds; each part given off makes exactly one further knot, which has no usable distinction. | any fails |
| P5 | Under the two added rules through round 12: Ring(4, 3) and Ring(6, 3) have no part that returns giving parts off; Ring(n, 3) for n = 8, 10, 12, 14, 16 has two parts after round 2 that each return every two rounds giving n/2 parts off. Ring(3, 3) is reported without a prediction. | any fails |
| P6 | In A2 every knot passes the parity knot test at every round by both methods, the methods agree on every knot, and every round extends. | a knot fails, the methods disagree, or a round does not extend |
| P7 | In A3 the closing exception never applies, the births under not-all-equal equal those under parity at every round, and every knot passes the not-all-equal criterion. | any fails |
| P8 | In A4 a part returns giving parts off under exactly three of the 70 laws on each of the three rings: CANCEL-WAIT with offshoots under CAP-3, ONE-FEWER and RATION-3. The knot test under each law is reported without a prediction. | a fourth law does, or one of the three does not |
| P9 | In A5, Ring(n, 2) returns every round as one part giving nothing off under both laws. Ring(n, 4) and Ring(n, 5) are reported without a prediction. | Ring(n, 2) does anything else |
| P10 | A6 is reported without a prediction: whether parts end under PART-CLOSE, and whether its births pass the knot test and extend. | not applicable |

A result that fails is reported as it is. An argument that P1 and P2 hold for every odd n from 5 up will be written out in the
result note and marked as an argument for the referee; the runs prove them only for the n they cover, by the first statement
under "Settled by construction".

## Runs and stop rule

One Python engine on real knots (`engine.py`, in this ticket's experiment family), with the rosters, their sameness test by
graph isomorphism, the lineage of every member, the two parity tests by exact arithmetic over the field of two elements and
graph connectivity, and the not-all-equal criterion by a SAT solver. Each run is expected to take under ten minutes and 4 GB
on one process; anything longer goes through the shared runner with a row in the long-running index. The study stops when
runs A1 to A6 are done and each prediction has a verdict. Deviations are recorded in `deviations.md` in the experiment family
before the affected run.

=== FILE: ticket B pre-registration ===
# What a reference is: dead knots, knots that wait, and the round read from one knot. Pre-registration

Ticket `RING-IN-BALANCE-20261123-001B` of epic `RING-IN-BALANCE-20261123-001` (sub-goal B318; goals G18 with G17 and G15),
2026-11-23. Frozen before the study's code is written. Code by a helper agent from this text and
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md), using ticket A's engine once its gate has passed. The
canonical K1–K3 test is unchanged.

## The question

On 23 November 2026 the owner asked: "What if some emergent patterns need anchor points, or like a reference. This would be
like consciousness in intelligence, and maybe just references in things like DNA? I think a structure like this would just
make it easier to join things, but I'm not sure. Or like a certain point of the Fibonacci sequence can be sampled to determine
growth rate at a particular point." In the program's terms the record already has two kinds of reference. Two knots can join
only when some knot, their witness, already meets both; and a dead knot is a witness that is not itself a member of the live
roster. This study asks three things. Does allowing dead knots in a start make it easier for a part to return and give parts
off? Is a part that returns always made of knots that waited, the only knots that stay members for more than one round? And
can the round a knot was made in be read from what that one knot holds, so that one sampled knot gives the growth factor at
its round? No claim is made about minds or living things.

## In standard terms

The same rewriting system as ticket A. A start is a hypergraph of knots over distinctions; its live roster is the hypergraph
of witnessed sets on the live knots, which for a start with every knot live is the neighbourhood hypergraph of the meeting
graph. The first question compares starts with and without vertices of the second kind (pure witnesses). The second asks
whether every recurrent component contains vertices that survive a step. The third asks whether a vertex's own degree data
determine its depth in the growth, where the depth is known to equal the size of a connected cluster of the universal cover
less one ([ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md)).

## Prior work in the program

Searches, each with `--until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`:

`python3 -B scripts/track.py objects "smallest start that returns, with and without dead knots" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "census of small starts with loose counts under ordinary growth" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "round a knot was made in read from its holdings" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "dead knot witness joins through" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`

- `DEAD-CAP-20261119-001`, `CAP-CHAINS-20261119-001` — the same object under the ordinary law: what dead knots change. A dead
  knot lifts the bound of two chains at five places, and the fastest growth found is built around two of them. This study asks
  the same of returning under the added rules.
- `GROWN-PAIR-20261119-001`, `RING-READ-20261118-001` — unrelated (structures read back from bond distances).
- `LEVEL-RETURN-20261113-001` — unrelated: "returning" there is a property of addressed patterns in the limit-only line.
- `DOUBLE-IDENT-20261119-001` — a relative: the identification of ordinary growth with clusters, for knots that meet twice.
  The doubled cycles of this study are starts of that kind.
- `GROWTH-STATISTICS-20261121-001`, `READ-ORIGIN-20261120-001`, `FIRST-KNOT-20261118-001` — relatives: censuses and panels of
  small starts under ordinary growth. Same kind of population, other law and other question; this study's census is exhaustive
  over meeting graphs of up to six knots, where those sampled trees or took first knots.
- `OVERLAP-READ-20261111-001`, `BOARD-DIST-20261110-001` — unrelated.
- `SERIAL-REPAIRS-20261120-001` — a relative (counts fixed at birth under one birth at a time); taken up in ticket C.
- `LIMIT-STATE-20261112-001`, `WITNESS-COUNT-20261112-001` — unrelated: "witness" and "dead" there belong to the limit-only
  line.
- `ROUND-FREE-20261119-001` — the same object for the third question: a knot's round is its cluster's size less one (proved).
  This study asks whether the knot's own holdings give that size.
- `RING-CORES-20261119-001` — the rings with a leftover distinction on every knot and their exact counts (proved); the third
  question's population.
- `GENERATORS-20261120-001` — no start of up to seven knots that are all live is a generator in the proved class, and the
  smallest generator has one dead knot ([source note](../GENERATORS-20261120-001/source.md)); `COPIES-AND-MEETINGS-20261120-001`
  — on that generator a knot made in round t holds at least (t + 9)/5 fresh distinctions.

## Prior work outside the program

Not searched beyond ticket A's note. The neighbourhood hypergraph of a graph and the bipartite double cover are standard; the
statement used below, that a start with every knot live has the neighbourhood hypergraph of its meeting graph as its family
of witnessed sets, is an observation, not a result.

## Known before the freeze (disclosed)

Run by the thread on 23 November 2026 with its own roster program, on rosters without distinctions
([private note](../../docs/prompts/2026-11-23_balance_pilot.md), "Anchors"): cycles of 4 to 9 members through dead witnesses
return under the two added rules; rings of 5, 7 and 9 knots return, 8 as two cycles of four, 4 and 6 do not; in rings of 5 and
7 and cycles of 4 and 6 the part that returns is the knots that waited; and in the ring of five with three loose distinctions,
under ordinary growth through round 12, every knot satisfies r = f + 2p − 3 − 2e. P1, P3 for those families, and P6 for n = 5
are therefore expected. A timing run of the census was made with its outcomes neither printed nor stored. The census outcomes
(P2, P4, P5), the seven-knot generator's holdings (P7) and the rings with a leftover on only some knots (P6b) are not known.

## Settled by construction (stated, not tested)

- A round reads only the live roster and, at source age, which member is the witness of which set. A dead knot enters only as
  a witness.
- In a start with every knot live, each knot is both a member and the witness of the members it meets, so the witnessed sets
  are the neighbourhoods of the meeting graph. A cycle of n witnessed pairs is then the whole roster of a start with every knot
  live only when n is odd (the ring of n knots), and is one of two parts of the roster of the ring of 2n knots.
- Under the ordinary law every member spends all it holds in one round, so no knot is a member for two rounds.
- In the ring of n knots with a leftover distinction on every knot, under the ordinary law, a knot made in round r is a run of
  L members of the unrolled ring with j of their leftover members, r = L + j − 1 (ROUND-FREE). Its children add one of the
  L − j missing leftovers or extend one of two ends, so its demand is L − j + 2; its parents drop one of the j leftovers or one
  of the e ends whose leftover is absent, so p = j + e. If the fresh count equals the demand, r = f + 2p − 3 − 2e with e equal
  to 0, 1 or 2. This is an argument from proved statements; the runs check it.

## What is supplied

As in ticket A, and in addition the census's family of starts, its weighting (each start up to isomorphism counted once), the
two ways of realising a cycle through dead knots, and the bounds. The realisation is swapped (D2 against DW); the weighting is
not swapped, and every share is stated under it.

## Runs (frozen)

R is the last round run. A run also stops when the structure passes the stated number of knots.

| Run | Starts | Laws | R; knots |
| --- | --- | --- | --- |
| B1 | D2(n, 3) and DW(n, 3), n = 3 to 12; Ring(n, 3), n = 3 to 16 from ticket A | the two added rules; the three; ordinary; the knot test on every start | 12; 6,000 |
| B2 | The census: every connected simple graph on 3 to 6 knots as the pattern of meetings (one shared distinction for each pair that meets), every loose count from 0 to 3 on each knot with at least three places for each knot and at least one live knot, each start up to isomorphism once: 86,032 starts, 55,771 with a dead knot. Starts with a knot that fails the parity knot test are set aside and counted. | ordinary; the two added rules; the three | 10; 1,500 |
| B3 | Every run of B1, B2 and ticket A's A4 in which a part returns | the same | as there |
| B4 | Ring(n, 3), n = 5, 7, 8, 9, 10, 11; Ring(n, 3) with the leftover removed from one knot and from every second knot, n = 5, 7, 9; Ring(n, 2) | ordinary | 12 (14 for n = 5); 6,000 |
| B5 | The seven-knot generator | ordinary | 9; 20,000 |

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate. Ticket A's gate has passed. Every start of B1 passes the parity knot test. D2(n, 3) and DW(n, 3) give the same roster at every round under each law. Under the ordinary law no run has a part that gives parts off, and no knot is a member for two rounds. | any fails |
| P1 | Under the two added rules D2(n, 3) returns every two rounds giving n parts off, for every n from 4 to 12. n = 3 is reported without a prediction. | any n from 4 to 12 fails |
| P2 | In the census under the two added rules, no start of four or fewer knots with every knot live has a part that returns giving parts off, and the only such starts of five knots contain the ring of five. | a counterexample |
| P3 | In every run of B3 under a law with waiting, every member of a part that returns giving parts off, at the round it returns, waited in that round. Under laws without waiting no part returns giving parts off. | a counterexample to either |
| P4 | With dead knots allowed, some start of the census with fewer than five members has a part that returns giving parts off under the two added rules. | none does |
| P5 | In the census at six knots under the two added rules, the share of starts with a part that returns giving parts off is larger among starts with a dead knot than among starts with every knot live (each start up to isomorphism counted once). The shares at every size and number of dead knots are reported. | it is not larger |
| P6 | In B4, every knot made in rounds 1 to R of a ring with a leftover on every knot satisfies r = f + 2p − 3 − 2e with e equal to 0, 1 or 2, where e is counted from the knot's cluster. (b) On Ring(n, 2) every knot of every round holds the same, so holdings give no round; on the rings with some leftovers removed the spread of r among knots with equal p and f is reported and predicted to grow with R. | a knot breaks the formula; or in (b) the spread is bounded by 4 at R = 12 |
| P7 | In B5 every knot made in round t holds at least (t + 9)/5 fresh distinctions (the record's bound), and the largest and smallest round among knots of equal p and f are reported without a prediction. | the bound fails |

A result that fails is reported as it is. P5 is about one weighting and says nothing of any other.

## Runs and stop rule

B2 is about 260,000 runs and goes through the shared runner (`scripts/longrun.py`) as one job with a row in the long-running
index, at most 16 GB, each case a block of starts with a time limit; everything else is expected to take under ten minutes.
For each run the job records the kind of outcome, the first return found with its rounds and parts, and which members waited.
The study stops when B1 to B5 are done and each prediction has a verdict. Deviations are recorded in `deviations.md` in the
experiment family before the affected run.

=== FILE: ticket C pre-registration ===
# With no round supplied, does the ring still return? One birth at a time, orders and priorities. Pre-registration

Ticket `RING-IN-BALANCE-20261123-001C` of epic `RING-IN-BALANCE-20261123-001` (sub-goals B319 and B320; goals G5 with G18 and
G17), 2026-11-23. Frozen before the study's code is written. Code by a helper agent from this text and
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md), with ticket A's engine for the complete rounds. The
canonical K1–K3 test is unchanged.

## The question

On 23 November 2026 the owner asked: "what if 'time' is a device or pattern just like the other ones? Are we able to simulate
things 'over time'? So logic is prior to time as well as space." And: "for the time thing, I feel like it's not really like a
sequencer, but more like a priority system, if that makes sense. How often updates happen given some property (maybe mass
impacts that). … Then places with nothing going on need less simulation." The ring that returns in ticket A is the first
pattern of the growth studies that comes back while giving the same parts off, so it could serve as a clock. But it was found
under complete rounds, which the one who runs the growth supplies (assumption A104). This study takes the rounds away. It
makes one birth at a time under laws that read nothing of a next round, and asks: does the ring still return in every order?
If not, is there a priority read from the structure alone under which it does, whatever way ties are broken? And measured in
births, does the ring return more slowly as the parts it has given off pile up? The complete round is also the scaffold that
ticket A's result has to survive a swap of before it can be said of the model.

## In standard terms

The asynchronous (sequential) version of ticket A's synchronous rewriting system. The questions are confluence (does every
fair sequence of rule applications build the same thing), whether a scheduling priority computable from the structure (here
the depth of a vertex in the derivation order) restores the synchronous result, and the rate of a recurrent component per
rule application as other components grow. The literature's abelian networks are the systems whose result is independent of
the order of events; for networks that never halt, features such as the least period are known to be definable without an
update order.

## Prior work in the program

Searches, each with `--until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`:

`python3 -B scripts/track.py objects "one birth at a time, order of births, priority, serial growth without rounds" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "does a ring return in every order of births" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "a clock's returns per birth when more is attached" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "depth of a knot, parent steps, order read from the structure" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`

- `ROUND-FREE-20261119-001` — the same object under the ordinary law: two present-state laws that make one join at a time
  build different things in different orders and never what the rounds build; a law that makes a knot for a cluster as soon as
  its parents exist is order-free but reads the whole map of joins. This study takes its present-state law as the base of its
  serial laws and its order effect as a gate.
- `SERIAL-REPAIRS-20261120-001`, `TICK-BIRTHS-AND-SCARCITY-20261121-001` — the same kind of object: the guarded rule, which
  rebuilds the cohort at the least depth still holding a loose distinction and plans its complete round, and the rule that
  recomputes after every birth. Under the guarded rule one tick of an eight-knot clock cost 81 births alone and 141 or 253 with
  an attachment, at the same four depths per tick; the recomputing rule can lose a tick for good. The guarded rule's depth
  barrier does not pass a waiting knot, so it is not used here as it stands; this study's depth priority is its nearest
  relative.
- `REVIEW-LEADS-20261123-001` (ticket D) — a relative: two copies of that clock on one donor one loose distinction short; the
  order of births decides which loses its tick.
- `LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001`, `CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001`,
  `FREEDOM-CLOCKS-AND-BIRTHS-20261120-001` — relatives: clocks read as returns to the same original knot in structures that
  grow, with the reader supplied (A150). The clock here is a part of the live roster that comes back the same.
- `COPIES-AND-MEETINGS-20261120-001` — a relative (depth as parent steps between packets).
- `FRESH-DEMAND-20261120-001` — a relative: two present-state schedules (unrestricted, joins first) on a panel of trees.
- `GROW-FACE-20261110-001` — a relative in another line: a rule that grows everywhere at once is split by an order at every
  radius and priority.
- `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` (frozen the same day by another thread) — another treatment of a short knot: it
  pays with a shared distinction. Not used here.

## Prior work outside the program

- Order-independence. Chip-firing and the abelian sandpile build the same final configuration whatever the firing order
  (Dhar 1990; Björner, Lovász and Shor 1991). Bond and Levine, "Abelian networks I" (2016), give two axioms on automata that
  guarantee it; Chan and Levine, "Abelian networks IV" (2022), treat networks that never halt, where the order changes the
  trajectory but features such as the least period are defined without an update order. Read from search summaries, not in
  full. Whether the growth laws here satisfy those axioms is not known; ROUND-FREE's order effect shows the ordinary
  present-state law does not behave so.
- Order without a global clock: Lamport, "Time, clocks, and the ordering of events in a distributed system" (1978); a
  synchronous algorithm run on an asynchronous network by local waiting is the literature's synchronizer (Awerbuch 1985).
  The depth priority below is a scheduler of that kind.
- Event-driven simulation keeps the next changes in a queue by priority and spends nothing on quiet regions; for Conway's
  Life, Gosper's hashlife (1984).

## Known before the freeze (disclosed)

No serial law of this study has been run. Known from the pilot's abstract program: under complete rounds, cycles through dead
witnesses return under (RATION-3, CANCEL-WAIT), with 10, 20, 40, 70, 115 members after rounds 1 to 5 for the cycle of five.
The thread worked two cases by hand before the freeze and expects P3 and P4 from them; the hand work also showed that a ring
at source age may return under a depth priority by a different route than the rounds, so the rings carry no prediction there.

## Settled by construction (stated, not tested)

- The cohort law builds what the complete rounds build.
- Under RATION-3 every new knot receives three fresh distinctions, so every move extends and the closing exception cannot
  apply while another loose distinction exists.
- Under the DEAD witness rule a start with no dead knot has no join at its first moves.

## What is supplied

The serial laws, their two witness rules and their eight priorities; the seeds and, for every share of seeds, the priority's
own weighting; the bounds. Ticket A's complete round is what this ticket swaps. Left out, and said so here: the record's
eight-knot clock and its attachments, whose tick is read by a supplied reader through that study's guarded rule (two more
scaffolds); not-all-equal beyond the check that the closing exception never applies; and the never-used fillers, which read a
next round.

## Runs (frozen)

Serial laws, all parity: L1 = (RATION-3, ANY), L2 = (RATION-3, DEAD), L3 = (PRESENT-CAP-3, ANY), L4 = (PRESENT-CAP-3, DEAD), each
with waiting as defined. Starts: Ring(5, 3), Ring(7, 3), D2(4, 3), D2(5, 3), DW(5, 3), D2(6, 3). The reference for L1 and L2 is
the complete rounds under (RATION-3, CANCEL-WAIT); for L3 and L4 under (CAP-3, CANCEL-WAIT).

| Run | What | Size |
| --- | --- | --- |
| C0 | Gates (below) | small |
| C1 | Every start × every law × the eight priorities × seeds 0 to 99. A run ends when its knots are settled to depth 3, at 800 moves, or at 4,000 knots. Recorded: the structures settled to depths 1, 2 and 3 and whether each is the same as the reference's; each return with the number of moves before it; the moves made; the reason for ending. | 19,200 runs |
| C2 | D2(5, 3) and DW(5, 3) under L2 with DEPTH, offshoots first, seeds 0 to 9, until five returns or 6,000 moves: the moves between consecutive returns. The same count for the complete rounds of ticket A under the two and the three added rules. | 20 runs |
| C3 | The parity knot test for every knot, and the extension test at every move, on seeds 0 to 4 of D2(5, 3) under L1 and L2 with DEPTH, offshoots first, to depth 3. | 10 runs |

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate. (a) The cohort law builds the same to depth 3 as the complete rounds on D2(5, 3) under (RATION-3, CANCEL-WAIT) and (CAP-3, CANCEL-WAIT), 20 seeds each. (b) Under the ordinary present-state law of ROUND-FREE (PRESENT-ORD, FIRST-COME, ANY, UNIFORM), 40 seeds to 300 moves: two three-place knots sharing one distinction stop in some seeds and reach 300 moves in others, and a lone four-place knot reaches 300 moves in at least 30. (c) The sameness test accepts a renamed copy and rejects a copy with one distinction moved. | any fails |
| P1 | Under UNIFORM, on every start and every law, at most 5 of the 100 seeds build the same to depth 2 as the reference. | more than 5 on some start and law |
| P2 | Under UNIFORM, on every start and every law, at most 5 of the 100 seeds return even once. | more than 5 on some start and law |
| P3 | Under DEPTH with offshoots first, on D2(4, 3), D2(5, 3), DW(5, 3) and D2(6, 3) under L1 and under L2, all 100 seeds build the same to depth 3 as the reference, and all return at least twice. | any seed differs or returns fewer than twice |
| P4 | Under DEPTH with joins first, on those four starts under L1 and L2, no seed builds the same to depth 3 as the reference. Under DEPTH with uniform ties at least one seed in 100 differs on each. | a seed agrees under joins first; or none differs under uniform ties |
| P5 | Under L3 and L4 on those four starts, with DEPTH and offshoots first, at most 5 of the 100 seeds return even once: a fresh count read from the present depends on the order. | more than 5 return |
| P6 | In C2 under the serial law the moves between consecutive returns increase from each return to the next. Under the complete rounds they increase without end under the two added rules and are constant from the second period under the three. | any fails |
| P7 | In C3 every knot passes the parity knot test and every move extends; the closing exception never applies in any run of C1. | any fails |
| R | Reported without a prediction: the rings at source age under every priority other than UNIFORM; OLDEST, FEWEST-PLACES, MOST-LOOSE and LOOSE-WEIGHTED on every start and law (shares of seeds that build the same as the reference to depths 2 and 3, returns, and moves per return where there are returns). | not applicable |

A result that fails is reported as it is. Every share is a share of seeds under the named priority's weighting. A positive
P3 is a statement about 100 sampled ways of breaking ties, not about all of them; if it holds, the result note gives the
argument for all, marked as an argument for the referee.

## Runs and stop rule

The serial engine keeps the live roster by parts and recomputes the moves of a part only when it changes. C1 goes through the
shared runner (`scripts/longrun.py`) as one job with a row in the long-running index, at most 16 GB, each case one start and
law with its 800 runs and a time limit; the rest is expected to take under ten minutes. Sameness to a depth is decided by a
colour-refinement hash of the incidence graph of knots and distinctions with depths as colours, confirmed by an exact
isomorphism test whenever a run is counted as the same as the reference. The study stops when C0 to C3 are done and each
prediction has a verdict, which is the ticket's stop: either a priority read from the structure under which the result does not
depend on the sampled ties and the ring returns more slowly in births as its parts pile up (P3 with P6), or the report that
no registered law and priority gives it. Deviations are recorded in `deviations.md` in the experiment family before the
affected run.
