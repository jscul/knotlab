# Why does a growth begin with the smallest knot?

Epic `FIRST-KNOT-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead for `FRESH-COUNT-20261118-001`'s
direction 2 (sub-goal B201). Goals G2 and G1; challenges A105. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `3d0efe6f6` at 20:18 UTC; the census ran at 20:19 UTC
  through the shared runner (`FIRST-KNOT-B1`, `runs/first-knot`, 313 cases on 7 workers, all ok, finished 20:21 UTC).
- Proofs: [proof.md](../../proofs/FIRST-KNOT-20261118-001A/FIRST-KNOT-20261118-001A-P001_two_knots/proof.md).
- Code: [startlib.py, job.py, merge.py, checks.py](../../experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/),
  using `FRESH-COUNT-20261118-001B`'s `freelib.py`.
- Results: [results.json](../../artifacts/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/results.json).

## The answer

**In the owner's terms.**
- **No: nothing in the parity law or the joining rule prefers the smallest first knot.** The law accepts parity knots of every size.
  The rule never sees a knot's size at all, only how many of its distinctions are still open (proved).
- **The coordinator's test.** A three-place and a four-place first knot, apart or touching at one distinction, cannot grow under any
  single count: each would need its own number, so the growth stalls within four rounds, and neither wins (proved; every count from 2
  to 8 checked). They do grow together when they share two distinctions, because then one has one open distinction and the other two.
- **What fixes the three of a lone knot.** The foundation defines first emergence as two loops joined by one contact: a relation on
  three distinctions, whose parity form is the three-place knot. With one count, a growth from that knot alone is three-dimensional.
  The three is the foundation's definition, not a consequence of the law (a reading, recorded in A105).
- **Touching lowers the dimension.** Two touching knots of a places each lose one open distinction, so with one count they grow
  (a − 1)-dimensionally: two touching smallest knots grow two-dimensionally (proved).
- **The cheapest growth makes every touching pair two-dimensional, but that two is written into it.** Taking as few fresh
  distinctions as possible, a lone knot of any size closes into its 2^a pattern and stops, while two knots touching at one
  distinction, of any sizes, grow two copies of a two-way counting pattern forever (proved; every pair of sizes three to six checked
  exactly). The two is the rule's own floor of three distinctions per knot, less the one distinction a hanging knot borrows: with a
  floor of two or of four the growth changes (the control).
- **And the fewest counts single out no number either.** The census's one failed prediction found three knots of four places, each
  touching the other two, growing three-dimensionally under the fewest counts. In general m knots of m + 1 places, each touching
  every other, grow m-dimensionally (proved after the read-out, computed for m = 3, 4, 5). Two touching knots give two because there
  are two of them in that arrangement, not because the rule prefers two.
- **The growth belongs to the presentation, not to the relation.** The same four-place parity relation grows four-dimensionally as
  one knot and two-dimensionally as two smallest knots through a hidden distinction, or as two knots on the same distinctions with
  the same allowed states (proved). So "the size of the first knot" is not even defined for a growth until its knots are chosen.

| Start | One count | Fewest counts | Evidence |
| --- | --- | --- | --- |
| one knot of a places | runs only at c = a: a-fold counting pattern | closes into the 2^a pattern | `FRESH-COUNT-20261118-001` |
| two knots of a and b places, apart | runs only at c = a = b | both close | proved (Theorems 2, 3); computed Q1, Q2 |
| two knots touching at one distinction | runs only at c = a − 1 = b − 1 | two two-way patterns forever, any sizes | proved; computed Q1, Q2 |
| a three-place and a four-place knot | apart or touching once: no count; sharing two: c = 2 | apart: close; touching: two-dimensional | proved; computed |
| the four-place relation: one knot / two smallest knots | c = 4 / c = 2 | closes / two-dimensional forever | proved (Corollary 2.1); computed |
| chains, rings, stars of knots (outside Lemma 1) | outside the theorem: some run (rings of 3s at counts 2 to 5), some stall | close, or grow one-, two- or three-dimensionally (the ring of three four-place knots: three) | computed Q4 |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | five gate checks | held | 5 of 5 |
| Q1 | one count: survival, stall round and junctions per round from the open counts alone | held | all 226 cells in Lemma 1's scope (30 two-knot starts at counts 2 to 8, 4 small starts at counts 2 to 5); 16 cells outside the scope missed the prediction, as allowed, reported in the results |
| Q2 | fewest counts on two knots: apart close; touching at one distinction, two copies of ℕ² with the exact per-round counts and one relay per piece of three or more open distinctions | held | all 10 pairs of sizes, exactly, 30 rounds; every relay equal to the touching distinction |
| Q4 | small starts and two-distinction touches under the fewest counts: closed exactly when every demand-0 junction was implied; otherwise constant differences over the last ten rounds | **failed** | the closure clause was stated wrongly: six starts grow without ever having a demand-0 junction (their chains start at once), so "every" held vacuously; and the ring of three four-place knots grows three-dimensionally (differences rising 21 to 30), against "at most quadratic" |
| Q5 | floor control: floor 2 constant, floor 4 growing differences | held | all 8 cases |

Four of five held; Q4 failed, both parts on the record. Its second failure is the study's most interesting finding (Proposition 4,
added after the read-out).

## Why it holds

- **Pieces.** When no two first knots share a neighbour (apart, or touching each other), their descendants never become candidates
  for a common join: every later junction's neighbours lie in its own knot's piece. So each first knot grows alone, as a seed on its
  open distinctions; a shared distinction is never loose again and plays no part (Lemma 1).
- **One count.** A seed on ℓ open distinctions runs under one count only at c = ℓ (`FRESH-COUNT-20261118-001`, Theorem 2), except
  that one open distinction fits every count (its lone offshoot becomes a seed of c) and none needs nothing. So the pieces agree only
  if their open counts do (Theorem 2).
- **Fewest.** A touching knot's piece cannot close: its last junction's parity is not forced, because the touching distinction ties
  it to the other piece, so the rule must give it one fresh distinction, which copies the touching distinction (a relay), and a
  junction hanging from one distinction needs two more to be a knot. Those two open chains side by side never end (Theorem 3).

## Known results, and what this adds

Known, cited once: the predecessor's Birkhoff picture and the cube condition; the rank of a graph's GF(2) incidence matrix is the
number of vertices less the number of components (the implied-parity test, Lemma 3); vertex splitting and Whitney's 2-isomorphism
(the same cycle space from different graphs: Corollary 2.1). What this adds: the joining rule reads open distinctions, never sizes;
the exact one-count and fewest-count behaviour of every pair of first knots; and the answer that the three of a lone knot is the
foundation's, not the law's.

## Limitations

- Lemma 1's scope is starts whose knots share no neighbour. Chains, rings and stars of knots were computed, not proved.
- One joining rule (A104); serial growth is the basket's next direction.
- The reading that first emergence is a three-place knot rests on the foundation's definition (A2), which no computation here tests.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It found the first form of Theorem 2 false beyond one shared distinction
(the condition is on open counts: 0, 1 or c), gave the stall-round table, repaired Theorem 3's proof and added the relay and the
exact per-round counts, said the fewest counts' two is their floor and proposed the floor control, and strengthened the presentation
point. It found no reason inside the growth that prefers the three-place knot.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: does the law or the rule prefer the smallest first knot? | **Status:** Successful (a proved no) | The rule reads open distinctions, never sizes; a three-place and a four-place first knot cannot grow together under one count, and neither wins; the fewest counts give whatever dimension the start's arrangement holds |
| Local direction: what a growth's start decides | Continue, narrowed | The start's arrangement, not its knots' sizes, sets the dimension: two touching knots give two, m mutually touching knots of m + 1 places give m |
| Broader exploration: where dimension comes from | Known alternatives | Betweenness: a cap, a price, the start or one free step; parity: the start's open distinctions and arrangement, or a cap |
| Long-term goal: G2 Dimension three (with G1) | Obstruction learned | Three is not the law's own: it is the foundation's first emergence (two loops, one contact) or a start's arrangement |

The attempt leaves open a growth rule whose dimension belongs to the relation rather than to the chosen knots, and starts outside
Lemma 1 (chains, rings, stars), which were computed only.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Serial growth read from distances (`FRESH-COUNT-20261118-001#1`) | 2/3 — tests A104 | 2/3 — moves and reader exist | compare its descent orders with the complete round's on seeds of three to five → stop at a proof they agree, or a seed where they differ | Selected · awaiting go-ahead |
| 2 | A growth whose dimension belongs to the relation: read the allowed states with hidden distinctions forgotten, and grow from a canonical presentation | 3/3 — would make "dimension" a property of the base | 1/3 — no canonical presentation is known (a four-place knot splits three ways) | define one canonical presentation and test it on the four-place relation's three presentations → stop at one that grows alike, or a proof none can | Alternative · deferred (sub-goal) |
| 3 | The fewest counts on every small arrangement of touching knots | 2/3 — maps which arrangements give which dimension | 3/3 — Lemma 1, Theorem 3 and Proposition 4 cover the parts | census of all arrangements of up to five knots of three to five places → stop at a rule that predicts every dimension, or a counterexample | Alternative · deferred |

- **#1.** As in `FRESH-COUNT-20261118-001`; the coordinator asked to keep it next.
- **#2.** Payoff 3/3: G2 asks whether native logic builds three dimensions; if the dimension is a property of the presentation, the
  question needs a presentation first, and a canonical one would answer it for bases. Concreteness 1/3: no canonical presentation is
  known; Whitney's theory says which graphs share a cycle space, not which one is native. Filed as a sub-goal.
- **#3.** Payoff 2/3, concreteness 3/3: the pieces lemma and the two propositions give the method; the census found the ring of three
  four-place knots by accident.

**Corrections:** none to published claims. `FRESH-COUNT-20261118-001`'s statement that the fewest counts "keep the chains they are
handed, any number" stands; this study adds natural starts that hand over three, four and five.

**Goals:** G2 checkpoint (obstruction learned: three is not the law's own); G1 checkpoint (the same); no goal changed.

**Assumptions:** A105 returns to Assumed, its reason restated: the law prefers no size, so the premise rests on the foundation's
first emergence (A2), and the dimension also depends on the start's arrangement and presentation. No new entry.

**Basket:** B196, `FRESH-COUNT-20261118-001#1` (serial growth), the new sub-goal (#2 here); none taken, #1 awaits go-ahead.

## Final report as sent (2026-11-18 20:30 UTC)

**Outcome:** No. Nothing in the parity law or the joining rule prefers the smallest first knot (proved; a frozen census of 313 runs, with 4 of 5 predictions held). Closed, referee pending.

- **The coordinator's test.** A three-place and a four-place first knot, apart or touching at one distinction, cannot grow under any single count. Each would need its own number, the growth stalls within four rounds, and neither wins.
- **Why.** The rule never sees a knot's size, only how many of its distinctions are still open.
- **Where the three comes from.** The three of a lone growing knot is the foundation's definition of first emergence (two loops joined by one contact, three distinctions), not a consequence of the law.
- **Touching lowers the dimension.** With one count, two touching knots of a places grow (a − 1)-dimensionally.
- **The cheapest growth does not pick a number either.** Two touching knots of any sizes grow two-dimensionally, through a relay of the touching distinction. The one failed prediction found that three knots of four places, each touching the other two, grow three-dimensionally. In general, m such knots of m + 1 places grow m-dimensionally (proved after the read-out, computed for m = 3, 4, 5). So the number comes from the start's arrangement.
- **The growth belongs to the presentation.** The same four-place relation grows four- or two-dimensionally depending on which knots present it.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: does the law or the rule prefer the smallest first knot? | **Status:** Successful (a proved no) | The rule reads open distinctions, never sizes; three- and four-place first knots can't grow together under one count; the cheapest growth gives whatever the start's arrangement holds |
| Local direction: what a growth's start decides | Continue, narrowed | The arrangement, not the knots' sizes, sets the dimension |
| Broader exploration: where dimension comes from | Known alternatives | Betweenness: a cap, a price, the start or one free step; parity: the start's open distinctions and arrangement, or a cap |
| Long-term goal: G2 Dimension three (with G1) | Obstruction learned | Three is not the law's own: it is the foundation's first emergence or a start's arrangement |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Serial growth read from distances (`FRESH-COUNT-20261118-001#1`) | 2/3 — tests A104 | 2/3 — moves and reader exist | compare its descent orders with the complete round's on seeds of three to five → stop at a proof they agree, or a seed where they differ | Selected · awaiting go-ahead |
| 2 | A growth whose dimension belongs to the relation (a canonical presentation read from the states) | 3/3 — would make dimension a property of the base | 1/3 — no canonical presentation known | test one candidate on the four-place relation's three presentations → stop at one that grows alike, or a proof none can | Alternative · deferred (sub-goal) |
| 3 | The cheapest growth on every small arrangement of touching knots | 2/3 — maps arrangement to dimension | 3/3 | census of arrangements of up to five knots of three to five places → stop at a rule predicting every dimension, or a counterexample | Alternative · deferred |

**Corrections:** none. **Goals:** G2 and G1 checkpoints (obstruction learned); no goal changed. **Assumptions:** A105 returns to Assumed, now resting on the foundation's first emergence (A2); no new entry. **Basket:** B196, `FRESH-COUNT-20261118-001#1`, the new sub-goal; none taken, #1 awaits go-ahead. **Advisor:** Fable 5.2 before the freeze. It found my first "different sizes never grow together" too strong (the condition is on open counts, so a three and a four sharing two distinctions do grow), repaired a proof, and proposed the floor control. Its "nothing three-dimensional ever" was refuted by the census.

Referee hand-off: the prior-work line is in the pre-registration (objects-gate passes). The decision note is `research/FIRST-KNOT-20261118-001/first_knot.md`.
