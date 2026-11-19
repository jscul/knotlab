# What distances carry of what the law builds: the line from GROWN-PAIR to HUNT-SHORTEN

19 November 2026, by Claude, at the coordinator's request. A summary of nine epics; it adds no evidence. Each claim links to the
record it comes from. HUNT-SHORTEN is **referee pending**; the other eight are refereed.

## In plain words

- **Pair distances alone lose information.** The law, cheapest counts in complete rounds, builds pairs of different arrangements
  with the same distance between every two distinctions but different allowed states.
  - It does so when start knots share two distinctions (GROWN-PAIR).
  - It does so when junctions meet once, once the starts are large enough to hold such a pair already (GROW-SMALL).
  - The census's own starts, five knots at most, are just too small to show this (MEET-ONCE, narrowed).
- **Adding three-way distances recovers what was lost.** The three-way distance is the smallest bond holding three given
  distinctions. With it added, every such pair found comes apart (THREE-WAY, TRIPLE-GROWN). What stays hidden is only which
  junction holds what, which no reading of the allowed states can show.
- **What the law reads, and the clean form of your premise.** One round of the law reads only the growing end: which junctions hold
  a loose distinction, how many, and which sets of them one junction meets. Distance plus the growing end carried everything one
  round further in every case where the hypothesis applies, 69,978 of them, but that is not proved. A junction joined by hand
  across two matched junctions does break it; the law's own joins, so far, never do.

## Proved (refereed)

| Result | Epic |
| --- | --- |
| Complete rounds from a connected start keep backed pairs (two junctions met by a live junction also meet an older, closed one) and keep live junctions apart, at every size; removing the live junctions gives the previous stage exactly; older distances never grow | PARENT-RULE, Theorems 1 to 3 |
| So the law never builds UNIQUE-TABLE's six static rivals, in any round, at any size | PARENT-RULE |
| One round reads only the growing end (Lemma A); with the equations in place of the distances, a matching that keeps the growing end carries every later round (Claim B\*) | EXTEND-ROUND |

## Computed, with its bound

| Finding | Bound | Epic |
| --- | --- | --- |
| 152 reached groups with one table and other states, all from starts whose knots share two; they persist two rounds | census stages ≤ 14 junctions | GROWN-PAIR |
| Where junctions meet once, no such pair; all 102 collisions keep the states, already at distance 8 | census stages 15 to 40 (50 by the referee); census starts only | MEET-ONCE |
| Backed pairs do not keep the states: 242 static meet-once pairs, backed on both sides, share a table with other states | all legal meet-once arrangements ≤ 7 junctions (503,039) | PARENT-RULE |
| From those 503,039 starts the law makes 87 meet-once pairs with one table and other states: 86 carried from colliding starts (persisting), 1 created (parting next round) | 1 and 2 rounds | GROW-SMALL |
| Pair plus three-way readings separate every collision found: 11 + 152 + 22 + 1,034 + 87 pairs | the collisions found | THREE-WAY, TRIPLE-GROWN |
| The created pair: matching the tables swaps a start knot with a new junction and moves one join distinction across the growing end; no matching keeps its loose distinctions, while some does in every carried pair | 1 created, 86 carried | CREATED-PAIR |
| Distance plus the growing end extends one round: 36,060 of 36,060 (carried pairs) and 33,918 of 33,918 (census self-pairs); joins made by hand break it 14,792 times in 41,268, offshoots never | ≤ 14 junctions, one round | EXTEND-ROUND, HUNT-SHORTEN |

## Known mathematics, and what our reading adds

The allowed states form the cut space of the junction graph, and a bond is a cocircuit. Two arrangements have the same states
exactly when the graphs' cycle matroids agree (Whitney's 2-isomorphism theorem). Weight enumerators are a classical invariant of a
binary code. The four junctions that pairwise meet, whose table has a symmetry its states lack, are an exception in Whitney's
edge-isomorphism theorem.

What this line adds:
- which of these ambiguities the growth law actually produces, and from which starts;
- that three-way bond sizes resolve every one found;
- the exact reading of a round;
- a computed, bounded form of "distance plus the growing end carries what grows", and the hand-made join that breaks distance
  alone.

## Corrections made along the line (all logged in `docs/CORRECTIONS.md`)

| Epic | Correction | Verdict |
| --- | --- | --- |
| GROWN-PAIR | Meet-once headline given its size; superseded tally marked; 151 groups with two state groups and 1 with three | Not a block |
| THREE-WAY | Stages left alike 77, not 74; the reading worded as a bond | Not a block |
| MEET-ONCE | 20 groups without closed stages, not 19; law-like sentences given their size | Not a block |
| MEET-ONCE, PARENT-RULE | "A property of what the law reaches" and "the protection lies in the law's exact joins" hold for the census's starts only (found by GROW-SMALL) | **Narrowing** |
| PARENT-RULE | 181 of 1,099 tables with a symmetry the states lack, not 178; "in any round from a connected start" | Not a block |
| TRIPLE-GROWN | Counts of readings separate every pair, not 1,000 and 73; ranks quoted wrongly | Not a block |
| CREATED-PAIR | Carried pairs' differences are not always two junctions from the growing end | Not a block |
| EXTEND-ROUND | The stall test counts groups; Claim B\* is about the span of the equations | Not a block |

## Open questions, graded

| # | Question | Payoff | Concreteness |
| --- | --- | --- | --- |
| 1 | Prove Claim B: why does keeping the growing end stop a bridging join from breaking the distances? | 3/3 | 2/3 |
| 2 | Are pair plus three-way readings complete beyond the collisions found (a pair agreeing on both, with other states)? | 2/3 | 2/3 |
| 3 | How often does the law create such a pair from larger starts and over more rounds? | 2/3 | 2/3 |
| 4 | Does the extension keep holding over rounds 2 to 4? | 2/3 | 2/3 |
| 5 | The same questions under Codex's serial mixed law | 2/3 | 2/3 |
