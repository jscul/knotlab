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
only when some knot, their common knot, already meets both; and a dead knot is a common knot that is not itself a member of
the live roster. This study asks three things. Does a dead knot in a start make it easier for a part to return and give parts
off? Is a part that returns always made of knots that waited, the only knots that stay members for more than one round? And
can the round a knot was made in be read from what that one knot holds, so that one sampled knot gives the growth factor at
its round? No claim is made about minds or living things.

## In standard terms

The same rewriting system as ticket A. A start is a hypergraph of knots over distinctions; its live roster is the hypergraph
of met sets on the live knots, which for a start with every knot live is the neighbourhood hypergraph of the meeting graph.
The first question compares starts with and without vertices that are only common knots. The second asks whether every
recurrent component contains vertices that survive a step. The third asks whether a vertex's own degree data determine the
step at which it was made, which is known to equal the size of a connected cluster of the universal cover less one
([ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md)); for a tree-like cover the count used is the boundary of a
connected subtree, the sum of its degrees less twice its size less one.

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

Not searched beyond ticket A's note. The neighbourhood hypergraph of a graph, the bipartite double cover and the boundary count
of a subtree are standard; the statements used below are observations, not results.

## Known before the freeze (disclosed)

Run by the thread on 23 November 2026 with its own roster program, on rosters without distinctions
(the workspace's private note `docs/prompts/2026-11-23_balance_pilot.md`, "Anchors"): cycles of 4 to 9 members through dead common
knots return under the two added rules; rings of 5, 7 and 9 knots return, 8 as two cycles of four, 4 and 6 do not; in rings of
5 and 7 and cycles of 4 and 6 the part that returns is the knots that waited; and in the ring of five with three loose
distinctions, under ordinary growth through round 12, every knot satisfies r = f + 2p − 3 − 2e. P1, P3 for those families,
and P6 for n = 5 are therefore expected. A timing run of the census was made with its outcomes neither printed nor stored. The
census outcomes (P2, P4, P5), the seven-knot generator's holdings (P7) and the rings with a leftover on only some knots (P6b)
are not known.

## Settled by construction (stated, not tested)

- A round reads only the live roster and, at the start, which member is the common knot of which met set. A dead knot enters
  only as a common knot.
- In a start with every knot live, each knot is both a member and the common knot of the members it meets, so the met sets are
  the neighbourhoods of the meeting graph. A cycle of n met pairs is then the whole roster of a start with every knot live
  only when n is odd (the ring of n knots), and is one of two parts of the roster of the ring of 2n knots. So P1 below follows
  from ticket A's rings wherever those are run; it is kept as a check on real knots with dead common knots.
- Under the ordinary law every member spends all it holds in one round, so no knot is a member for two rounds.
- In the ring of n knots with a leftover distinction on every knot, under the ordinary law, a knot made in round r is a stretch
  of L members of the unrolled ring with j of their leftover members, r = L + j − 1 (ROUND-FREE). Its children add one of the
  L − j missing leftovers or lengthen the stretch at either side, so its demand is L − j + 2; its parents drop one of the j
  leftovers or one of the e outermost members whose leftover is absent, so p = j + e. If the fresh count equals the demand,
  r = f + 2p − 3 − 2e with e equal to 0, 1 or 2. Since e is read from the cluster and not from the knot, what a knot holds gives
  its round to within three values and no closer. P6 below checks this; it is not a finding.

## What is supplied

As in ticket A, and in addition the census's family of starts, its weighting (each start up to isomorphism counted once), the
two ways of realising a cycle through dead knots, and the bounds. The realisation is swapped (D2 against DW); the weighting is
not swapped, and every share is stated under it.

## Runs (frozen)

R is the last round run. A run is also cut off when the structure passes the stated number of knots.

| Run | Starts | Laws | R; knots |
| --- | --- | --- | --- |
| B1 | D2(n, 3) and DW(n, 3), n = 3 to 12; Ring(n, 3), n = 3 to 16 from ticket A | the two added rules; the three; ordinary; the knot test on every start under both knot laws | 12; 6,000 |
| B2 | The census: every connected simple graph on 3 to 6 knots as the pattern of meetings (one shared distinction for each pair that meets), every loose count from 0 to 3 on each knot with at least three places for each knot and at least one live knot, each start up to isomorphism once: 86,032 starts, 55,771 with a dead knot. Starts with a knot that fails the parity knot test are set aside and counted. | ordinary; the two added rules; the three | 10; 1,500 |
| B3 | Every run of B1, B2 and ticket A's A4 in which a part returns | the same | as there |
| B4 | Ring(n, 3), n = 5, 7, 8, 9, 10, 11; Ring(n, 3) with one loose distinction removed from knot 0, and from every knot of even number, n = 5, 7, 9; Ring(n, 2), n = 5, 7 | ordinary | 12 (14 for n = 5); 6,000 |
| B5 | The seven-knot generator | ordinary | 9; 20,000 |

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate. Ticket A's gate has passed. Every start of B1 passes the parity knot test (the not-all-equal test of each start is reported). D2(n, 3) and DW(n, 3) give the same roster at every round under each law. Under the ordinary law no run has a part that gives parts off, and no knot is a member for two rounds. | any fails |
| P1 | Under the two added rules D2(n, 3) returns every two rounds giving n parts off, for every n from 4 to 12. n = 3 is reported without a prediction. | any n from 4 to 12 fails |
| P2 | In the census under the two added rules, no start of four or fewer knots with every knot live has a part that returns giving parts off, and every such start of five knots has the five-cycle as its pattern of meetings. | a counterexample |
| P3 | In every run of B3 under a law with waiting, every member of a part that returns giving parts off waited in the round at which it returns. Under laws without waiting no part returns giving parts off. | a counterexample to either |
| P4 | Some start of the census with fewer than five members has a part that returns giving parts off under the two added rules. (Outside the census D2(4, 3), with four members and four dead knots, is predicted to by P1.) | none in the census does |
| P5 | Matched pairs: for each census start of six knots with exactly one dead knot, take the start with the same meetings and loose counts except that this knot holds one loose distinction. Under the two added rules, the pairs in which only the start with the dead knot has a part that returns giving parts off outnumber the pairs in which only the other does. The shares at every size and number of dead knots are reported, each start up to isomorphism counted once. | they do not outnumber them |
| P6 | (a) In B4, every knot made in rounds 1 to R of a ring with a leftover on every knot satisfies r = f + 2p − 3 − 2e with e equal to 0, 1 or 2 counted from the knot's cluster (a check of the settled statement). (b) On Ring(n, 2) every knot of every round has p = 2 and f = 2, so holdings give no round. On the rings with some leftovers removed, among knots with equal p and f the greatest round less the least exceeds 4 somewhere by round 12. | a knot breaks the formula; or in (b) the spread never exceeds 4 |
| P7 | In B5 every knot made in round t holds at least (t + 9)/5 fresh distinctions (the record's bound); the greatest and least round among knots of equal p and f are reported without a prediction. | the bound fails |

A result that fails is reported as it is. P5 is about one weighting and one way of matching, and says nothing of any other.

## Runs and stop rule

B2 is about 260,000 runs and goes through the shared runner (`scripts/longrun.py`) as one job with a row in the long-running
index, at most 16 GB, each case a block of starts with a time limit; everything else is expected to take under ten minutes.
For each run the job records the kind of outcome (the first that applies in the order of the definitions), the first return
found with its rounds and parts, and which members waited. The study stops when B1 to B5 are done and each prediction has a
verdict. Deviations are recorded in `deviations.md` in the experiment family before the affected run. The advisor model
(Claude Fable 5.2) reviewed the design cold before this freeze (`research/RING-IN-BALANCE-20261123-001/advisor/`); the matched
pairs of P5 and the reading of P1 and P6 as checks are its points.
