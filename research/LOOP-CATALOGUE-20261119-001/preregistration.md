# Which loops of knots feed themselves? Pre-registration

Epic `LOOP-CATALOGUE-20261119-001` (the coordinator's go-ahead, taking `SCALE-SHARE-20261119-001#1`; goal G17), 2026-11-19.
Written after a pilot (disclosed below) and the advisor's answer, before the frozen run. The canonical K1–K3 test is unchanged.
The owner's idea behind it, in his words, is recorded as A109 and in THEORY.md: "loops of logic, then like eddies in a river that
are shared across the universe essentially there are 'core-libs' kind of processing". It is his direction, not a result.

## Words

- **Growth** and the **cluster rule** are as in `CLUSTER-ALL-20261119-001`: the cheapest parity growth under the complete-round
  policy (A104). The **candidate map** joins the live knots sharing a distinction with one knot. Its **blocks** are:
  - simplices, merged when they share two knots;
  - first-round groups of three or more, **hyperedges**, taken all or nothing.

  A **live** knot still holds an open distinction.
- A **loop** is a cycle of the block graph, whose points are knots and blocks. Going once round a loop has a **round-weight** W(y),
  the sum over the ways round of y to the number of knots taken (the advisor's form). It is computed by `loopweight.py` from the
  rule's own entry series.
- A start **feeds itself** (an **eddy**) when its growth is exponential. A loop is **bare** when W is one power of y: there is one
  way round, and the count stays constant.
- A **minimal eddy** is a start that feeds itself, where removing any one spare, or any one knot, leaves nothing that does. Its
  **interface** is what joining something to one of its knots does to its rate.

## The questions

1. Which cycles of knots feed themselves, and why do large growers' many cycles not?
2. What is the catalogue of distinct self-feeding loops up to a stated size? Each entry is given with its ratio as a root of its
   equation, whether it is the same under not-all-equal, and its interface (a spare, a hanging knot, a chain, a second loop).
3. Is the catalogue finite, a few families or unbounded, and does a small generating set compose it?

## The eddy rule (frozen, `eddy.py`)

A start feeds itself when some piece of its block graph has a loop and is not bare, and the piece holds none of the cluster rule's
two known breaks. The breaks are a merged block with a missing pair (the overlapping sunflowers), and two hyperedges meeting at a
knot (the referee's second break). A piece with a loop that holds a break is **unreliable**; growth decides it.

## What is argued before the run (the advisor's statement, to be written out in the note)

**In the cover model.** A piece with no loop has finitely many clusters. Its growth closes, or comes from the floor's endless
chains: polynomial. With one loop the count is P + Q / (1 − W), with rate 1/y* where W(y*) = 1. The count is constant when W is a
single power of y. With two independent loops of blocks the unrolled map branches, the count is algebraic, and it grows like
C ρ^t t^(−5/2) (`RING-PAIR-20261119-001`).

**The parts of W:**
- each knot on the loop gives y;
- each block passed gives a transit:
  - a simplex of k knots, (1 + y)^(k − 2);
  - a hyperedge of h knots, y^(h − 2);
  - two simplices sharing c knots, ((1 + y)^c − 1)(1 + y)^(others);
- each side entry gives a factor (1 + U), with U = y Π(1 + U′) over what hangs from it:
  - a spare: U = y;
  - a lone hanging knot: y;
  - a hanging knot with s spares: y(1 + y)^s;
  - a hanging path of two knots: (1 + y)(1 + y/(1 − y)) = (1 + y)/(1 − y). The far knot, at bare size, has two open places
    and one first-round join, so the floor gives it an endless chain. The advisor's finite-path form (1 + y)^2 assumed no chain;
    the smoke run showed the chain (disclosed).
  - an endless chain: y/(1 − y) as U.

**So the rates are generated** by finitely many pieces (a loop step, the transits, the entries, and the joint between two loops)
under multiplication and substitution. They are infinitely many: y^L (1 + y) = 1 already gives one rate per loop length, falling
to 1.

## Pilot (disclosed)

- **The census.** On all 26,441 starts, the rule picks exactly the 13 rings (all rings of five with spares). The 3 bare rings grow
  by 5 a round.
- **Random starts.** About a million random arrangements of 6 to 12 knots were sampled (sampler.py; pilot seeds 10^6 n + k,
  frozen seeds 10^7 n + k, so the two never meet), and about 13,600 of them were grown.
  - All 64 rule-eddies are exponential.
  - None of the grown non-eddies is exponential.
  - None of the 46 pieces with two hyperedges meeting at a knot is exponential.
  - Loops through a single hyperedge are real eddies, and there the rule's series equals the growth.
- **Why growers' cycles do not feed.** In growers only 16 to 27% of knots are live. A loop needs live knots where it joins; its
  common neighbours may be full. Growers average 3.9 to 19.5 chordless cycles of knots, of which 0.5 to 1.4% are all-live.
- **The theta.** The six-knot theta (the ring 0-1-2-3-4, plus knot 5 touching 0 and 3) holds the overlapping-sunflower break. The
  rule gives y^5 (2 + y) = 1, a rate of 1.2298. The growth departs from the rule at round 3 (13 against 12) and grows faster. So
  the theta is decided by growth.
- **Minimal eddies.** The search covered every connected simple knot graph to eight knots (networkx's atlas to seven, and the
  11,117 eight-point graphs by augmentation), at bare sizes plus at most two spares. Where the rule is reliable it found five, which
  form `catalogue.json`:
  - the ring of five with a spare: y^5 (1 + y);
  - the ring of five with a lone knot hung on it: y^5 (1 + y);
  - the ring of seven with a spare: y^7 (1 + y);
  - the ring of seven with a lone knot hung on it: y^7 (1 + y);
  - the ring of eight with a spare: one loop of four, y^4 (1 + y).

  The rule could not decide the rest of the starts the search met: a loop holding a known break, or a start outside its scope
  with a loop (`undecided.json`). Part U grows all of them, and `merge.py` reads off which are minimal eddies by growth.
- **Smoke run** (disclosed). The interfaces of the ring of five with a spare:
  - a spare or a lone knot at a loop knot multiplies W by (1 + y);
  - a lone knot with a spare by 1 + y + y^2;
  - a hanging path of two by (1 + y)/(1 − y), not the advisor's (1 + y)^2.

  Also: the ring of nine with a spare has W = y^9 (1 + y), and the ring of eight with a lone knot at knot 1 has rate 1.3247.

## Prior work in the program

`python3 -B scripts/track.py objects "self-feeding loops of knots exponential growth ring catalogue round weight" --until 2026-11-19 --exclude LOOP-CATALOGUE-20261119-001`
`python3 -B scripts/track.py objects "which cycles of the candidate map give exponential growth why random arrangements rarely grow exponentially" --until 2026-11-19 --exclude LOOP-CATALOGUE-20261119-001`

- `RING-FORMULA-20261118-001`, `RING-GROWTH-20261118-001` (one ring's formula, proved), `JOIN-GROWTH-20261118-001` (the menus
  F_s and the product law), `RING-PAIR-20261119-001` (the cover model, two loops algebraic): the same object, one loop or one join
  at a time. This study states W for every one-loop piece and searches all small starts.
- `CLUSTER-ALL-20261119-001` (the rule used, its two breaks), `SCALE-SHARE-20261119-001` (rings rare at scale; its #1 is this
  study's question 1): the same population.
- `RING-READ-20261118-001`: unrelated object (reading a ring back from distances), the same words.
- `NAE-GROWTH-20261119-001`: the not-all-equal check (C1) rests on its theorem.
- `TRUE-RATE-20261113-001`: unrelated object (least-bond rates of nested rules), the same words ("rate").

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| E1 | Part E and S: every rule-eddy is exponential; where the rule is exact (no known break), its counts equal the rule's series at every grown round | any is not exponential, or an exact one differs |
| E2 | Part E and S: no start the rule calls not an eddy (in scope, no break on a loop) is exponential | any is |
| E3 | Part E and S: no piece whose loop holds two hyperedges meeting at a knot is exponential (the cluster rule's false rings) | any is |
| E4 | (descriptive, thresholds set from the pilot) at every n ≥ 6, growers' live share is below 0.3, all-live chordless cycles are below 2% of their cycles, and growers with a loop are below 0.1% | any fails |
| C1 | Every catalogue entry is exponential under parity; where the rule is exact, its counts equal the rule's series; under not-all-equal its counts equal parity's for 12 rounds | any fails |
| C2 | For every exact one-loop start of parts C, I and R, the rule's rate (Berlekamp–Massey) equals the root of W = 1 (loopweight) to 10^(−5) | any differs |
| C3 | Every exact one-loop minimal eddy has W(1) = 2: exactly two ways round | any has more |
| C4 | No catalogue entry up to eight knots is algebraic (two loops); the first two-loop minimal eddy needs nine knots or more (the advisor) | one is |
| U1 | Part U: no start whose loop holds two hyperedges meeting at a knot is exponential; readouts: how many undecided starts are exponential, and which of them are minimal eddies by growth | one with meeting hyperedges is exponential |
| I1 | Every exact interface start grows equal to its rule series (no false rings) | any differs |
| I2 | At a loop knot of a one-loop entry, W changes by exactly: a spare (1 + y) when the knot then has three or more open places; a lone knot (1 + y); a lone knot with a spare 1 + y(1 + y); a hanging path of two (1 + y)/(1 − y) | any differs |
| I3 | Every interface raises the rate, and joining the ring of five with a spare makes the count algebraic (no recurrence of order 30 or less in 120 terms) | any lowers it, or a ring join is rational |
| R1 | Rings with one spare: W = y^n (1 + y) for odd n = 9, 11, 13 and y^(n/2) (1 + y) for even n = 8, 10, 12; bare rings of 8 to 13 make n junctions a round | any differs |
| R2 | The ring of eight with a spare at knot 0 and a lone knot hung at knot 0 has rate root of y^4 (1 + y) = 1; with the lone knot hung at knot 1, y^4 (1 + y)^2 = 1 (the two loops take their entries separately) | either differs |

## Runs and stop rule

`job.py` through the shared runner (six workers; about an hour, registered), with `checks.py` as gates (G1–G6 pass). Parts E and S
grow only the starts named in job.py; `merge.py` scores. Stop at the read-out.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. Its points, and how each was used:
- **The theta's equation.** It corrected my y^5 (1 + 2y) to y^5 (2 + y); its rate matches the rule's 1.2298. Since then the theta
  was found to be a break shape, decided by growth.
- **The general law.** It stated W as loop points × transits × entries, and the theorem by transfer (c = 0, 1, ≥ 2). Both are
  used above.
- **The chain's factor.** It gave (1 − y)^(−2) for an endless chain hanging at a loop knot and a finite-path product. Under bare
  sizes the far knot of a hanging path carries the floor's endless chain, so I2 uses (1 + y)/(1 − y) for a path of two (from the
  smoke run, disclosed).
- **The even ring.** It gave the placement check (R2).
- **The unit.** It said to catalogue round-weights, not starts. The note lists both: W for the rate, the starts that realize it.
- **Minimal eddies.** It predicted W(1) = 2 (C3), "a shared set of three or more is never minimal", and no algebraic entry to eight
  knots (C4).
- **What I did not adopt.** I did not test its mechanism for the meeting hyperedges, that a loop knot needs an open distinction
  left after round 1. It is recorded as a direction.
