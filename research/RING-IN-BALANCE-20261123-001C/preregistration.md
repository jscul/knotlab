# With no round supplied, does the ring still return? One part at a time, one birth at a time, and priorities. Pre-registration

Ticket `RING-IN-BALANCE-20261123-001C` of epic `RING-IN-BALANCE-20261123-001` (sub-goals B319 and B320; goals G5 with G18 and
G17), 2026-11-23. Frozen before the study's code is written. Code by a helper agent from this text and
[the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md), with ticket A's engine for the complete rounds. The
canonical K1–K3 test is unchanged.

## The question

On 23 November 2026 the owner asked: "what if 'time' is a device or pattern just like the other ones? Are we able to simulate
things 'over time'? So logic is prior to time as well as space." And: "for the time thing, I feel like it's not really like a
sequencer, but more like a priority system, if that makes sense. How often updates happen given some property (maybe mass
impacts that). … Then places with nothing going on need less simulation." The ring that returns in ticket A comes back while
giving the same parts off, so it could serve as a clock. But it was found under complete rounds, which the one who runs the
growth supplies (assumption A104): every member of every part reads its situation at the same moment. This study takes that
away in two steps. First it lets the parts of the live roster move one at a time, in an order set by a priority, each part
still reading at once: does the same structure get built whatever the order, and how often does the ring return, counted in
births, under each priority? Second it makes one birth at a time, with every member reading again after every birth: does the
ring still return? The complete round is also the scaffold that ticket A's result has to survive a swap of before it can be
said of the model.

## In standard terms

The asynchronous versions of ticket A's synchronous rewriting system, at two grains: components updated one at a time
(step semantics within a component, interleaving between components), and single rule applications (full interleaving). The
questions are confluence (does every fair schedule build the same thing), and the rate of a recurrent component per rule
application under a scheduling priority. The literature's abelian networks are the systems whose result is independent of the
order of events.

## Prior work in the program

Searches, each with `--until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`:

`python3 -B scripts/track.py objects "one birth at a time, order of births, priority, serial growth without rounds" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "does a ring return in every order of births" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "a clock's returns per birth when more is attached" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`
`python3 -B scripts/track.py objects "depth of a knot, parent steps, order read from the structure" --until 2026-11-23 --exclude RING-IN-BALANCE-20261123-001`

- `ROUND-FREE-20261119-001` — the same object under the ordinary law: two present-state laws that make one join at a time
  build different things in different orders and never what the rounds build; a law that makes a knot for a cluster as soon as
  its parents exist is order-free but reads the whole map of joins. This study takes its present-state law as its
  birth-by-birth law and its order effect as a gate.
- `SERIAL-REPAIRS-20261120-001`, `TICK-BIRTHS-AND-SCARCITY-20261121-001` — the same kind of object: the guarded rule, which
  rebuilds the cohort at the least depth still holding a loose distinction and plans its complete round, and the rule that
  recomputes after every birth. Under the guarded rule one tick of an eight-knot clock cost 81 births alone and 141 or 253 with
  an attachment, at the same four depths per tick; the recomputing rule can lose a tick for good. The guarded rule's depth
  barrier does not pass a waiting knot, so it is not used here as it stands; the part-round law is its nearest relative, with
  the part in place of the depth.
- `REVIEW-LEADS-20261123-001` (ticket D) — a relative: two copies of that clock on one donor one loose distinction short; the
  order of births decides which loses its tick.
- `LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001`, `CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001`,
  `FREEDOM-CLOCKS-AND-BIRTHS-20261120-001` — relatives: clocks read as returns to the same original knot in structures that
  grow, with the reader supplied (A150). The clock here is a part of the live roster that comes back the same.
- `COPIES-AND-MEETINGS-20261120-001` — a relative (parent steps between packets).
- `FRESH-DEMAND-20261120-001` — a relative: two present-state schedules (unrestricted, joins first) on a panel of trees.
- `GROW-FACE-20261110-001` — a relative in another line: a rule that grows everywhere at once is split by an order at every
  radius and priority.
- `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` (frozen the same day by another thread) — another treatment of a short knot: it
  pays with a shared distinction. Not used here.

## Prior work outside the program

- Order-independence. Chip-firing and the abelian sandpile build the same final configuration whatever the firing order
  (Dhar 1990; Björner, Lovász and Shor 1991). Bond and Levine, "Abelian networks I" (2016), give two axioms on automata that
  guarantee it; Chan and Levine, "Abelian networks IV" (2022), treat networks that never halt, where the order changes the
  trajectory but features such as the least period are defined without an update order. In graph transformation the question
  is local confluence by critical pairs (Ehrig; Plump); in Petri nets, step against interleaving semantics. Read from search
  summaries and from memory, not in full. Whether the growth laws here satisfy any of those conditions is not known;
  ROUND-FREE's order effect shows the ordinary present-state law does not behave so.
- Order without a global clock: Lamport, "Time, clocks, and the ordering of events in a distributed system" (1978).
- Event-driven simulation keeps the next changes in a queue by priority and spends nothing on quiet regions; for Conway's
  Life, Gosper's hashlife (1984).

## Known before the freeze (disclosed)

No law of this study has been run. Worked by hand before the freeze, by the advisor and then by the thread: on the cycle of
five through dead knots under the birth-by-birth law, generation 0 makes its ten births in any order; at generation 1 each
join is in four open groups holding three and is short, each offshoot makes two offshoots and is then in two open groups
holding one, so it is short as well, and nothing of generation 1 moves again. P1 is that trace. P4 to P6 are expectations from
arithmetic on ticket A's disclosed counts.

## Settled by construction (stated, not tested)

- **Under the part-round law the order of the parts does not matter to what is built.** Past the start a part acts alone
  (ticket A, settled statements), so a part's line of descent is the same in every order, each knot's own time is its round
  under complete rounds, and once every part that would make a birth has own time at least R, the knots of own time at most R
  form the structure the complete rounds build in R rounds. ALL-IN-TURN is the complete round. P2 below checks this on real
  knots; it is not a finding.
- What the priority does change is how many births of other parts fall between two returns of one part.
- Under RATION-3 every new knot receives three fresh distinctions, so every move of the birth-by-birth law extends.
- Under the DEAD rule a start with no dead knot has no join at its first moves.

## What is supplied

The part-round law and its seven priorities; the birth-by-birth law, its two rules for common knots and its orders; the seeds
and, for every share or mean over seeds, the priority's own weighting; the bounds. Ticket A's complete round is what this
ticket swaps. Left out, and said so here: the record's eight-knot clock and its attachments, whose tick is read by a supplied
reader through that study's guarded rule (two more scaffolds); not-all-equal; the fillers under the birth-by-birth law, since
they read a next round; and any law in which the members of one part read at different moments other than the birth-by-birth
law.

## Runs (frozen)

All under parity.

| Run | What | Size |
| --- | --- | --- |
| C0 | Gate (below). | small |
| C1 | Part-round law with the two added rules and with the three, on D2(4, 3), D2(5, 3) and Ring(5, 3), under each of the seven priorities; seeds 0 to 19 for the priorities with a random choice, one run for the others. A run goes on until the part that returns has returned 12 times, 4,000 moves, or 20,000 knots. Recorded at each return: the moves and the births since the return before; at the end: the least own time R among the parts that would still make a birth, and whether the knots of own time at most R are the same structure as the complete rounds build in R rounds. | 726 runs |
| C2 | Birth-by-birth law (RATION-3, waiting), under ANY and under DEAD, on D2(4, 3), D2(5, 3), DW(5, 3), D2(6, 3), Ring(5, 3) and Ring(7, 3): BY-GENERATION with each of its three tie rules and UNIFORM, seeds 0 to 99, each run to 600 moves or 4,000 knots. Recorded: the moves made at each generation, every join made, whether and where the run jams, and whether a part that is the same as the start's roster, past its start and made of knots not in the start, ever appears. | 4,800 runs |
| C3 | Every order: on D2(4, 3) under the birth-by-birth law with DEAD and BY-GENERATION, a search over all orders of the moves of generations 0 and 1, by distinct structures up to renaming. | one search |

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate. (a) The part-round law under ALL-IN-TURN gives, move for move, the births of ticket A's complete rounds on Ring(5, 3) and D2(5, 3) under the two and the three added rules through round 8. (b) Under the ordinary present-state law of ROUND-FREE (PRESENT-ORD, FIRST-COME, ANY, UNIFORM), 40 seeds to 300 moves: two three-place knots sharing one distinction stop in some seeds and reach 300 moves in others, and a lone four-place knot reaches 300 moves in at least 30. (c) The sameness test for structures accepts a renamed copy and rejects a copy with one distinction moved. | any fails |
| P1 | Birth-by-birth, BY-GENERATION, every tie rule, ANY and DEAD, on D2(4, 3), D2(5, 3), DW(5, 3) and D2(6, 3): every seed jams at generation 1 after exactly 2n moves of generation 1, all of them offshoots, with no join of generation 1 ever made; and the search of C3 finds no order of generations 0 and 1 that ends otherwise. So the ring does not return. | a seed or an order makes a join of generation 1, or does not jam |
| P2 | In every run of C1 the knots of own time at most R are the same structure as the complete rounds build in R rounds, and each knot's own time is its round there (a check of the settled statement). | any run differs |
| P3 | In every run of C1 the part that returns has returned 12 times before the bounds, except where the bound of 20,000 knots is met first, which is reported. | a run stops returning for another reason |
| P4 | Under the two added rules with UNIFORM, BY-MEMBERS, ALL-IN-TURN or LEAST-TIME, the births between consecutive returns grow: their mean over returns 7 to 12 (and over seeds) is more than 1.5 times their mean over returns 2 to 6, on each start. | the ratio is 1.5 or less |
| P5 | Under the two added rules with LARGEST or MOST-LOOSE, the parts that have come apart never move, and the births between consecutive returns are exactly 4n at every return (n the number of members of the part that returns). | a part that came apart moves, or a count differs |
| P6 | Under the three added rules, under every priority, the births between consecutive returns do not grow: their mean over returns 7 to 12 is at most 1.2 times their mean over returns 2 to 6, on each start. | the ratio exceeds 1.2 |
| R | Reported without a prediction: SMALLEST under both laws; UNIFORM under the birth-by-birth law (how many seeds make a join of generation 1, jam, or show a copy of the start's roster); the rings under the birth-by-birth law. | not applicable |

A result that fails is reported as it is. Every mean is a mean over seeds under the named priority's weighting. P4 to P6 are
about births counted by the one who runs the growth; nothing in the growth counts them.

## Runs and stop rule

C1 and C2 are expected to take under ten minutes each on a few processes; if either is longer it goes through the shared
runner (`scripts/longrun.py`) with a row in the long-running index, at most 16 GB. Sameness of structures is decided by a
colour-refinement hash of the incidence graph of knots and distinctions, with rounds as colours, confirmed by an exact
isomorphism test whenever a run is counted as the same. The study stops when C0 to C3 are done and each prediction has a
verdict. That meets the ticket's stop in one of its two forms: priorities read from the present roster under which what is
built does not depend on the order, with the ring's returns per birth depending on the priority and on whether the parts that
came apart end; or the report that the registered laws fail. Whether the members of one part can read at different moments is
left open by this design unless P1 fails. Deviations are recorded in `deviations.md` in the experiment family before the
affected run. The advisor model (Claude Fable 5.2) reviewed the first design cold before this freeze
(`research/RING-IN-BALANCE-20261123-001/advisor/`) and found by hand that its birth-by-birth law jams; this design is the
answer to that review, and its part-round law was not reviewed.
