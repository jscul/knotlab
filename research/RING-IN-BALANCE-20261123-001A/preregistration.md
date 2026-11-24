# Does a ring of knots return and give parts off, on real knots? Pre-registration

Ticket `RING-IN-BALANCE-20261123-001A` of epic `RING-IN-BALANCE-20261123-001` (sub-goal B315; goals G18 with G17 and G5),
2026-11-23. Frozen before the study's code is written. Code by a helper agent from this text and
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) alone, without reading the pilot's programs; the
thread compares its output with the pilot's afterwards. The canonical K1–K3 test is unchanged.

## The question

An exploratory pilot of 23 November 2026 found that under two rules added by hand to the cheapest growth, a ring of an odd
number of knots comes back to its start every two rounds while the same finite parts come apart from it, and that a third added
rule makes those parts end ([Intuitions lesson 8.7](https://prespatial.org/intuitions/generators-and-folds-of-emergence), "Balance"). Ordinary growth cannot do this: its parts never come apart, and only finitely many lasting packets of any fixed
width can be released. The pilot ran on rosters with no distinctions in them, was not pre-registered and was not refereed. This
study repeats it with independent code on real knots, and asks what the pilot left open: whether every knot made under the
changed laws passes the knot test in the whole structure, whether not-all-equal behaves the same, and what happens when each
added rule is swapped for another. It matters to G18 because it would be the first growth law of the program under which a
fixed finite thing is made again and again, and the first whose roster is in balance.

## In standard terms

A synchronous graph-rewriting system on hypergraphs (knots are hyperedges over distinctions, each distinction in at most two
knots) with a resource cap and a blocking rule. On the pairs of the live roster one round is the line-graph operator, with a
clique rule for three or more and pendant vertices for offshoots. The object is a periodic configuration that produces a fixed
finite pattern each period: an oscillator with output, the cellular-automaton literature's gun. The population is cycles of n
hyperedges with a fixed number of pendant vertices each. The quantities are the period, the pattern produced, and whether each
hyperedge is a minimal dependency of the cycle space (parity) or of the not-all-equal constraint system.

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
- The pilot itself is outside the index: a private note of the workspace, `docs/prompts/2026-11-23_balance_pilot.md`.

## Prior work outside the program

- Conway's Life has guns: Gosper's glider gun (1970) returns every 30 steps and makes one glider. A pattern whose output
  itself keeps growing, so that the whole grows as the square of the time, is the literature's breeder. That is on a board
  with a clock. The study asks for the same on a structure that makes its own places.
- The line-graph operator: the only connected graphs equal to their own line graph are the cycles (van Rooij and Wilf, 1965),
  which here is the ring with two loose distinctions on every knot; repeated line graphs and clique graphs are surveyed in
  Prisner, *Graph Dynamics* (1995). What this adds is the ration and the waiting rule, under which a cycle returns with output.
- Growth by graph rewriting with a cap can replicate: the Wolfram Demonstrations Project's "Self-Replicating Graphs" describes
  a rule with a degree cap of four under which one edge grows to twelve vertices and then breaks into four edges that repeat.
  Graph-rewriting automata that reproduce are studied by Tomita, Kurokawa and Murata (Artificial Life 13, 2007). Read from
  search summaries only, not in full.
- Not found: a rewriting rule on parity or not-all-equal constraint systems with a ration and a waiting rule, or any statement
  that the pieces produced are minimal dependencies. Searched 23 November 2026 with the phrases "graph rewriting oscillator
  emitting copies", "glider gun analogue graph grammar" and "self-replicating structure resource limit"; no claim of novelty
  is made beyond the program's own records.

## Known before the freeze (disclosed)

The pilot's two programs (the helper's `roster.py` and the thread's `own_check.py`) and the public site's port were run before
this freeze. They give, on rosters without distinctions or on the ring's stars: the return every two rounds for cycles of 4 to
12 members; members and parts 5/1, 10/1, 15/6, 25/6, 35/11, 50/11, 65/16 for the ring of five under the two added rules and
5/1, 10/1, 15/6, 10/1, 15/6 under the three; no return for rings of four and six knots; a return for the ring of eight as two
cycles of four; and a search of 56 laws on 2,400 starts in which a part returned giving parts off under three laws, all with
waiting. The advisor's hand work before the freeze predicts a return under a cap of four from round 3, which nobody has run.
P1 to P5 and the pilot's part of P8 are therefore expected to hold and test the independent code and the real knots. P7 for
not-all-equal, the caps of four and more in P8 and P11, P9, P10 and the knot test under the swapped laws were not computed by
anyone before this freeze.

## Settled by construction (stated, not tested)

- **The roster is enough.** Past its start, a round reads only h, k and the inclusion-maximal met sets of the roster, so two
  rosters that are the same have the same next round up to renaming.
- **Parts act alone past the start** (under RELEASE). The groups, the owing, the births, the demand and the fresh counts of a part then depend
  only on that part, except for the closing exception, which needs the round's sole birth. A new knot meets only its parents,
  and every parent that made a birth has spent every usable distinction, so the next roster is again past its start and the
  descendants of two parts are never joinable. Hence if a part returns after T rounds giving parts off, it returns every T
  rounds without end, and gives off the same parts each time.
- **Under parity a set of loose distinctions is constrained only when it is all of them** (the sum of every knot's rule;
  ORDINARY-DYNAMICS, step 4), in a connected structure.
- **So under parity every new knot that receives a fresh distinction passes the knot test, and keeps passing.** Its rule is
  then the only constraint on its places, and a later rule with a place of its own removes no allowed state. P6 below is this
  statement; its runs check the argument and the code, and the knot test can fail only where a birth receives nothing (FLOOR0,
  the closing exception).
- Under the ordinary law no part comes apart or returns giving parts off
  ([GENERATORS, components](../GENERATORS-20261120-001/components.md)); the engine is checked against this.

## What is supplied

The complete round (A104), the added rules and every other ration and treatment (A224), the rings, the bounds, and the reading
of a part as a thing. This ticket swaps the ration, the treatment, the release rule and the fillers (against their absence, no
other rule that makes parts end being known). The complete round is swapped in ticket C and the start in ticket B.

## Runs (frozen)

All under parity unless stated, with the release rule RELEASE unless stated. R is the last round run. A run is also cut off
when the structure passes 6,000 knots (20,000 in A7).

| Run | Starts | Laws | R |
| --- | --- | --- | --- |
| A1 | Ring(n, 3), n = 3 to 16 | the two added rules; the three added rules; ordinary | 12; 20; 8 |
| A2 | Ring(n, 3), n = 5, 7, 9, 11, 13, 15 | the two and the three added rules: knot test and extension test for every knot at every round | 12 |
| A3 | Ring(5, 3), Ring(7, 3) | the two and the three added rules under not-all-equal: births compared with parity at every round; the not-all-equal test for every knot | 12 for births; 6 for the test |
| A4 | Ring(n, 3), n = 5, 7, 9 | 70 laws: rations ORD, ONE-FEWER, FLOOR0, FLOOR1, RATION-2, RATION-3, RATION-4, CAP-2, CAP-3, CAP-4, each with STALL, CANCEL-OFFSHOOT, CANCEL-WAIT, CANCEL-RETIRE, and with STALL, CANCEL-WAIT, CANCEL-RETIRE under NO-OFFSHOOT; knot test and extension test through round 6 | 16 |
| A5 | Ring(n, a), n = 5, 7, a = 2, 4, 5 | the two and the three added rules | 12; 20 |
| A6 | Ring(n, 3), n = 5, 7, 9 | (CAP-3, CANCEL-WAIT with HOLD) | 12 |
| A7 | Ring(5, 3), Ring(7, 3) | (CAP-k, CANCEL-WAIT), k = 3 to 7 | 2k + 8 |

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate. Under the ordinary law the engine gives births 10, 15, 25, 40, 65, 105 for Ring(5, 3), five births every round for Ring(5, 2), and births 8, 12, 19, 32, 56 with 25, 42, 75, 140, 269 fresh distinctions in rounds 1 to 5 for the seven-knot generator (GENERATORS, source note); no part comes apart in any ordinary run; under the two added rules Ring(5, 3) makes five joins and five offshoots in round 1 and ten offshoots and no join in round 2; on every run of A1 its members, parts and loose counts each round equal those of the pilot's two programs; the two parity methods agree on a structure with a planted failing knot; and with STALL in place of CANCEL-WAIT the ring of five stalls in round 2. | any fails |
| P1 | Under the two added rules, for every odd n from 5 to 15 and every even round t from 2 to 12: the roster is past its start; the n knots that waited in round t form one part; that part has n members with three usable loose distinctions each and n met pairs in one cycle, the same as the start's roster. | any n and t fails |
| P2 | For the same n and t, the members after round t + 2 that descend from that part form n + 1 parts: one the same as it, and n each of two members with two usable loose distinctions in one met set. | any fails |
| P3 | Under the two added rules every part that has come apart is the same, s rounds later, as every other at the same s, and has s + 2 members, for s from 0 to 10 and n = 5, 7, 9. | two such parts differ at one s, or a count differs |
| P4 | Under the three added rules, for every odd n from 5 to 15 the roster is in balance from round 1 with period two through round 20, with 2n members in one part after odd rounds and 3n members in n + 1 parts after even rounds; each part that has come apart makes exactly one further knot, which has no usable distinction, and has then ended. | any fails |
| P5 | Under the two added rules through round 12: Ring(4, 3) and Ring(6, 3) have no part that returns giving parts off; Ring(n, 3) for n = 8, 10, 12, 14, 16 has two parts after round 2 that each return every two rounds giving n/2 parts off. Ring(3, 3) is reported without a prediction. | any fails |
| P6 | In A2 every knot passes the parity knot test at every round by both methods, the methods agree on every knot, and every round extends (a check of the settled statement above). | a knot fails, the methods disagree, or a round does not extend |
| P7 | In A3 the closing exception never applies, the births under not-all-equal equal those under parity at every round, and every knot passes the not-all-equal test. | any fails |
| P8 | In A4, on each of the three rings: (a) no law with STALL, CANCEL-OFFSHOOT or CANCEL-RETIRE, and no law with NO-OFFSHOOT, has a part that returns giving parts off; (b) with CANCEL-WAIT and offshoots, the rations CAP-3, ONE-FEWER, RATION-3 and CAP-4 have one, and ORD, FLOOR0, FLOOR1, RATION-2 and CAP-2 do not; RATION-4 is reported without a prediction. The knot and extension tests under each law are reported without a prediction. | any stated case comes out otherwise |
| P9 | In A5, under both laws Ring(n, 2) has the same roster after every round from round 1 on: one part of n members with two usable loose distinctions each. Ring(n, 4) and Ring(n, 5) are reported without a prediction. | Ring(n, 2) does anything else |
| P10 | In A6, with HOLD in place of RELEASE, no part returns giving parts off: the knots that waited in round 2 are short again in round 3 and in every later round of the run. | a part returns giving parts off, or those knots act |
| P11 | In A7, for every k from 3 to 7 and both rings, some part of n members with k usable loose distinctions each returns every two rounds giving parts off. | some k has no such part within its rounds |

A result that fails is reported as it is. An argument that P1 and P2 hold for every odd n from 5 up will be written out in the
result note and marked as an argument for the referee; the runs prove them only for the n they cover, by the settled
statements.

## Runs and stop rule

One Python engine on real knots (`engine.py`, in this ticket's experiment family), with the rosters, their sameness test by
graph isomorphism, the line of descent of every member, the two parity tests by exact arithmetic over the field of two
elements and by graph connectivity, and the not-all-equal test by a SAT solver. Each run is expected to take under ten minutes
and 4 GB on one process; anything longer goes through the shared runner with a row in the long-running index. The study stops
when runs A1 to A7 are done and each prediction has a verdict. Deviations are recorded in `deviations.md` in the experiment
family before the affected run. The advisor model (Claude Fable 5.2) reviewed the three designs cold before this freeze
(`research/RING-IN-BALANCE-20261123-001/advisor/`); its findings on the cap of four, the release rule, the inert extra that was
dropped, and the words are folded in here.
