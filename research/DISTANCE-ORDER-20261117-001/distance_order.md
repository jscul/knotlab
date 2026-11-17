# Which distance carries a base's information, and which gives an order with nothing skipped

Epic `DISTANCE-ORDER-20261117-001`, 17 November 2026, by Claude. It follows `DISTANCE-INFO-20261117-001`, its referee and the
owner's answer on A97. Goals G1 and G16. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block, folded in on
17 November (see Referee). Pre-registration: [preregistration.md](preregistration.md), frozen in
commit `9becfe4b8` at 18:36:24 UTC; the run went from 18:36:33 to 18:38:49 UTC. Proof:
[proof.md](../../proofs/DISTANCE-ORDER-20261117-001A/DISTANCE-ORDER-20261117-001A-P001_betweenness/proof.md). Code:
[order.py and run.py](../../experiments/DISTANCE-ORDER-20261117-001B/DISTANCE-ORDER-20261117-001B-E001_order/). Results:
[results.json](../../artifacts/DISTANCE-ORDER-20261117-001B/DISTANCE-ORDER-20261117-001B-E001_order/results.json).

## The answer

**On knot trees one distance read from the allowed states does both (proved).** On the thread and the weave, read with exact
additive betweenness (A98), the count that carries the information has no betweenness at all (computed). Read only as order, it
has a local order with nothing skipped, but its nearest neighbours are the knot-neighbours plus the second neighbours of the
start's own class, not the weave's own steps (the referee's reading, computed). *Narrowed after the referee: the first answer said
"where they form cycles, the two jobs split"; that is one strict reading on two bases, not a property of cycles.*

- **The disagreement count carries everything (proved).** The disagreement count of two distinctions is the number of allowed
  states in which they take different values.
  - The table of disagreement counts determines every nonempty not-all-equal base from four distinctions on.
  - Once the number of allowed states N is also known, it determines every base built from complement-closed constraints on at most
    three places.
  - It fails at three distinctions, the smallest emergent unit: one knot and no knot share the table. Read as rates instead, 2/3
    against 1/2, they differ.
  - The reason is that "not all equal" on three distinctions is itself a sum of pairwise disagreements. Pairs see exactly three
    places: a parity knot is invisible to them.
- **It has no additive betweenness on the program's spatial bases (computed, under A98).** These are the thread, a chain of knots
  and the six-regular weave at L = 6, 9 and 12. On all of them no distinction lies between two others, nothing is built from unit
  steps, and the rates go up and down with steps apart. Read only as order (w between u and v when nearer to each than they are to
  each other; the literature's relative neighbourhood graph), the weave's start has exactly twelve neighbours with nothing between,
  at L = 6, 9 and 12: its six knot-neighbours and the six second neighbours of its own class. Every farther distinction has something
  between it and the start. A path back to the start falling one step at a time fails for 11 of 35, 26 of 80 and 47 of 143
  distinctions (the referee's computation). On the weave the rate is 2/3 one step away. Along a row it falls below 1/2 at every third distinction and
  stays above 1/2 elsewhere (at L = 12: 0.667, 0.600, 0.311, 0.589, 0.581, 0.339).
- **Steps apart and bond distance have the order but do not carry everything.** Both have an order with nothing skipped, bond
  distance up to its offset of one. Bond distance is steps apart plus one on the knot chain, on the thread at ten distinctions except its two ends, and on the weave within
  the ruler theorems' margin. But equal tables of either still allow different states, from four distinctions on (`DISTANCE-INFO-20261117-001`).
- **Order is a three-place constraint (proved).** In the disagreement count, "c lies between a and b" says exactly that no allowed
  state has a = b ≠ c, which is a three-place constraint. It is a knot where the three pairs are free. On complement-closed bases
  with no tie, strict betweenness is always a knot. Without complement closure it can follow from two-place rules: on the chain of
  implications x → y → z, which has no knot, the counts are 1, 1 and 2 (corrected the same day by the review of what the premise
  reopens).
  - Read with flips, each not-all-equal knot gives a chain of three, and on every spatial base tested that is the longest chain:
    three, or four counting the start's own flip.
  - Order costs states. A chain of m distinctions allows at most 2m of their 2^m joint values.
  - The one base whose counts make a line with nothing skipped, 2|i − j|, is the threshold line, and it has only 2n states.
- **On knot trees the two jobs meet (proved).** When the knots form no cycle, τ = −log₃ |1 − 2d/N| equals steps apart exactly. Among
  such bases, steps apart determines the knots. So there one quantity, read from the allowed states alone, is built from unit
  steps, goes outward from any start with nothing skipped, and carries the base. On the thread and the weave, τ breaks. On the weave,
  two distinctions two steps apart in the same one of its three classes read nearer (τ = 0.66) than two that share a knot (τ = 1).

| Base | P1, built from unit steps | Betweenness triples | Gap graph | Longest chain, alone / with flips / without the start's flip | τ = steps apart | τ grows with steps apart |
| --- | --- | --- | --- | --- | --- | --- |
| b4 threshold line, n = 10 (control) | yes, unit 2 | 120 | a path, one gap value | 10 / 11 / 10 | (every pair one step) | — |
| b1 thread, n = 30 | no | 0 | complete (435 of 435) | 2 / 4 / 3 | no (off by up to 2.15) | no |
| b2 knot chain, 15 knots, n = 31 | no | 0 | complete (465 of 465) | 2 / 4 / 3 | yes (to 1.8 × 10⁻¹⁵) | yes |
| b3 weave L = 6 | no | 0 | complete (630) | 2 / 4 / 3 | no | no |
| b3 weave L = 9 | no | 0 | complete (3,240) | 2 / 4 / 3 | no | no |
| b3 weave L = 12 | no | 0 | complete (10,296) | 2 / 4 / 3 | no | no |

The weave's counts are exact: N = 263,640 at L = 6, 547,003,370,634 at L = 9 and about 3.79 × 10²⁰ at L = 12. At L = 9 and 12 they
come from transfer matrices modulo five primes, joined by the Chinese remainder theorem. Steps apart passes P1 everywhere, by
definition.

**The census of every not-all-equal relation (exploratory).**
- **Betweenness.** No relation on four distinctions has any. At five, 732 of 1,023 relations have some, and at six, 87,924 of
  97,248. These are mostly bases with few states, as statement 6 leads one to expect.
- **Lines.** No relation on four to six distinctions has a gap graph that is a path.
- **Unit steps.** 92 of 1,023 relations at n = 5, and 870 of 97,248 at n = 6, pass P1 with a table that is not constant. Counting only
  tables with at least two distinct positive values, as the referee does, gives 0, 72 and 780 at n = 4, 5 and 6.
- **The chain bound** of statement 6 held everywhere.
- **τ.** τ with N gives 16, 674 and 63,355 distinct tables for 16, 1,023 and 97,248 relations. Dropping the sign of the correlation
  loses information, so τ is not a reading that carries everything, except among knot trees.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| C | b4: P1 unit 2, gap path, chain 10 / 11 / 10 | held | as predicted |
| E1 | the count fails P1 on b1, b2, b3 | held | all five bases |
| E2 | no strict betweenness on b1, b2, b3 | held | 0 triples, complete gap graphs, chain 2 |
| E3 | with flips, chain 4, or 3 without the start's flip, on b1, b2 (b3 lower confidence) | held | 4 / 3 on all five, b3 included |
| E4 | b2: τ = steps apart | held | largest difference 1.8 × 10⁻¹⁵ |
| E5 | b1: τ does not grow with steps apart | held | pairs one step apart range over τ 0.58 to 2.63 |
| E6 | b3: rate 2/3 at one step; on a row, below 1/2 exactly at every third | held | exactly 2/3; L = 6, 9, 12 all on the predicted side |
| E7 | b2, four knots: bond distance steps + 1, fails P1, no betweenness | held | as predicted |
| E8 | census: no betweenness at n = 4, some at 5 and 6; chain bound | held | 0; 732; 87,924; bound held |

9 of 9 held. The proof's check also passed: every set of states of three and four distinctions, every not-all-equal relation of
three to six distinctions, every signed complement-closed relation of four and five (225 and 16,201), and 301 knot trees.

**Not predicted.**
- **The thread's bond distance** at ten distinctions is steps apart plus one for every pair except its two ends. No bond holds
  distinctions 0 and 9; this was seen after the run.
- **The weave's τ** does not grow with steps apart at any L.

## What it means for A97

The owner's reading has two parts: distance is the only form of information, and distance is topological, with no direction and
an order in which nothing is skipped. Read with the pairwise distances tested here:

- **Without cycles of knots, the reading holds exactly (proved).** On a base whose knots form no cycle, one quantity read from the
  allowed states, τ, is steps apart. It goes outward from any start one unit at a time, and among such bases it determines the base.
- **On the thread and the weave, under A98's strict reading, the two parts come apart (computed).** The disagreement count holds all
  the information but no additive betweenness. Steps apart and bond distance hold the order but not all the information.
- **Not a property of cycles.** Under an order-only reading the weave's count has a local order, though not the weave's own (twelve
  nearest neighbours instead of six). The census has 732 and 87,924 relations with cycles of knots and strict betweenness at n = 5
  and 6, and the threshold-line control has cycles and does both. What the data show is about spatial bases with many states,
  as statement 6 says: order costs states.
- **The order is a three-place constraint.** By statement 1, "c lies between a and b" is a three-place constraint, a knot where its
  pairs are free. Statement 6 says it costs states: a long order means a nearly frozen base.

So A97 is narrowed, not overturned. It holds on knot trees. Its narrowing on bases with cycles rests on A98's strict reading, and
an order-only reading changes it on the weave. A97 stays under challenge.

## What the knot picture explained

- **Information.** The census result "the pair table determines the base" turned out to be the law's own shape. Not all equal on
  three is a sum of pairwise disagreements. That is the dual of the known fact that the law reads pair counts of knots
  (`OVERLAP-READ-20261111-001`), and it explains why pairs see exactly three places and miss parity.
- **Order.** The knot picture says where order comes from: betweenness of three is a three-place constraint, a knot wherever its
  pairs are free. On a base with no tie and closed under flipping all values, its order is its knots, read three at a time.
- **Distance.** It also says when a distance read from states is a ruler: when no cycle of knots lets two routes interfere. The
  weave's three classes are the interference. The literature's version is the additive tree distance of phylogenetics, which
  works on trees and fails with cycles.

Known mathematics, labelled:
- metric betweenness (Menger);
- the triangle facets of the cut polytope (Deza and Laurent);
- the degree-two form of "not all equal";
- pairwise independence of parity;
- line metrics as nested cuts;
- the Cavender–Farris–Neyman tree distance;
- the triangular antiferromagnet's correlations (Stephenson).

The local parts are statement 3 in this form, statement 6, and the measurements on the program's bases.

## Limitations

- Pairwise readings only, and three candidates (the disagreement count, bond distance, steps apart) with τ. A distance read from
  the states in some other way could still both carry everything and give an order on the weave.
- The weave only to L = 12. That covers about six steps, too few to see the r^(−1/2) decay; the thread is open-ended.
- The reading of "no skipping" (unit steps, betweenness, gap graph, chains, flips counted) is one formalization, recorded as an
  assumption.
- Steps apart and bond distance are only cited, not re-proved, as not carrying everything. The n = 4 collision of
  `DISTANCE-INFO-20261117-001` serves for both.

## Reproduce

```sh
.venv/bin/python -B proofs/DISTANCE-ORDER-20261117-001A/DISTANCE-ORDER-20261117-001A-P001_betweenness/check.py
.venv/bin/python -B experiments/DISTANCE-ORDER-20261117-001B/DISTANCE-ORDER-20261117-001B-E001_order/run.py
```

## Advisor

Consulted before the freeze. It:
- confirmed statements 1 to 5 by hand;
- corrected two of my predictions: the knot chain's shared distinctions are not independent, and the chain with flips is 4,
  not 3;
- advised dropping a level-skipping test that fails on bookkeeping;
- gave the five-distinction betweenness example, the four-place parity witness, the chain bound of statement 6 and the log
  transform of statement 7;
- chose the word "disagreement count".

It was not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 17 November 2026, by a background referee thread with fresh code and no Codex: confirmed with
fixes, no Block. All seven statements are correct. Statement 3(b), with its recovery of N, is proved for every n ≥ 4. Every number of
ticket B recomputes with the referee's own code, including the weave's exact counts and a SAT check of no betweenness at L = 6 and
9. The freeze preceded the results. Folded in the same day, each item logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing.** "With cycles they split" is what A98's exact additive betweenness finds on two bases, not a property of cycles.
   The census has cyclic bases with betweenness, and the threshold line is cyclic and does both. Read only as order, the weave's
   count has a local order of twelve neighbours, not the weave's six. The answer, the meaning for A97, the position rows, A97, A98,
   the notebook, the goals and the two premise pages are scoped, and the chain of knots, a knot tree, is no longer listed under
   cycles.
2. **Not a block.** Statement 7 said "four if x is also new"; it is six. Only the equal weight is used.
3. **Not a block.** "Non-constant P1" counted tables with zeros and one positive value; the referee's 72 and 780 are given beside 92
   and 870.
4. **Not a block.** Bond distance has the order only up to its offset of one.
5. **Literature added to the proof.** The second-moment reading behind statement 3 (degree-two Sherali–Adams and sum-of-squares:
   a nonnegative degree-two violation count holds exactly when its mean is zero), and the broadcast process on a tree behind
   statement 7 (Evans, Kenyon, Peres and Schulman 2000).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which distance carries the information and which the order | **Status:** Successful (refereed, confirmed with fixes) | Proof that the disagreement count determines every not-all-equal base from four distinctions; on knot trees τ is steps apart; on the thread, knot chain and weave no additive betweenness; read only as order, a local order of twelve neighbours on the weave; 9 of 9 predictions held |
| Local direction: distance that is both information and order | Promising | Holds on knot trees; on the weave it depends on the reading of order (A98); whether the weave's states can read steps apart some other way is open |
| Broader exploration: what determines a relation | Known alternatives | Pair statistics determine conjunctions of complement-closed constraints on at most three places (likely folklore); parity needs more |
| Long-term goal: G16 and G1 | G16 capability gained; G1 obstruction learned | G16: what pair counts of the allowed states determine is now proved. G1: on the weave, the count that carries the information gives no additive order, and its order-only neighbours are not the weave's own |

**Next step:** Research directions. No action is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Can the weave's allowed states read steps apart? Look for a pairwise function of the counts that equals steps apart on W(L) (for example τ within each of the three classes, or the counts of three) | 2/3, a ruler read from the states on the program's own space | 2/3, exact counts to L = 12 are in hand | Freeze candidate readings → stop at a reading, or at a proof that a named family cannot | Alternative |
| 2 | k-wise disagreement counts and k-place knots, with parity at k = 3 | 1/3, likely folklore | 3/3 | Prove the degree-k statement → stop at the proof | Alternative |
| 3 | Order against states: how long a chain a base of N states can hold, and whether the program's grown number line is near the bound | 1/3 | 2/3 | Compare chains with the bound of statement 6 on `OPEN-END-GROWTH-20261107-001`'s thread → stop at the comparison | Alternative |

**Corrections:** one Narrowing at the close, and after the referee one more Narrowing and three Not a block entries, all logged. The disagreement table was said to determine "every not-all-equal base on up to six
distinctions" (THEORY.md, Intuitions lesson 2.4, HISTORY.md and the predecessor's note). It fails at three, one knot against none,
and holds from four, now proved.

**Goals:** a G16 and G1 checkpoint (G16 capability gained, G1 obstruction learned). G16's entry is upgraded from computed to
proved. No goal changed.

**Assumptions:** A97 stays Under challenge, narrowed: it holds on knot trees; on the thread and the weave the split rests on A98.
New entry A98 records the reading of "no skipping" used here; its challenge was partly run by the referee.

**Basket:** read; nothing in it is this question.
