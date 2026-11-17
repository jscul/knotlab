# How knots build an order: which distinction each new knot must share

Epic `KNOT-ORDER-20261117-001`, 17 November 2026, by Claude. Goals G1 and G16; tests A97. Referee pending. It answers Codex's
recommended question after the owner's knots-first answer, on the coordinator's go-ahead. Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `11978fa6f` at 20:14:09 UTC; the run went from 20:14:16 to 20:14:39
UTC. Proof: [proof.md](../../proofs/KNOT-ORDER-20261117-001A/KNOT-ORDER-20261117-001A-P001_growing_a_line/proof.md). Code:
[growth.py](../../experiments/KNOT-ORDER-20261117-001B/KNOT-ORDER-20261117-001B-E001_growth/growth.py). Results:
[results.json](../../artifacts/KNOT-ORDER-20261117-001B/KNOT-ORDER-20261117-001B-E001_growth/results.json).

## The answer

**Yes. A knot pattern grows an exact order one knot at a time, and its own states say where the next knot must go.** The knot is
B(a, b, c), "b lies between a and c". It excludes the two joint states in which a and c agree and b differs.

- **What a new knot must share depends on where the new distinction goes** (proved). Placed between two neighbours, the new
  distinction needs a knot with only those two. Placed beyond an end, it needs a knot holding both ends. In each case exactly one
  knot does it, so there are exactly m + 1 single knots that keep a line of m. The exhaustive check of all 34 three-place knots
  found exactly these through m = 8, all of them betweenness knots: m − 1 between neighbours and 2 beyond the ends.
- **Neighbours alone, growing outward, fail** (proved). A knot always made of the last three distinctions lets a second change of
  value through, as Codex's 0110 shows. That rule's states grow like the Fibonacci numbers, 10, 16, 26, … 1,220 at fourteen,
  instead of the line's 28. Any knot confined to a window of r places lets two changes more than r apart through.
- **The states themselves name the places** (proved, and run). With the names and the growth history erased, the disagreement
  counts give the two ends (the pair at the largest count) and the neighbours (the pairs at count 2). A rule that reads only the
  states, finds the ends and extends past one at random built an exact line at every step to fourteen.
- **No direction is stored.** Every admissible placement gives the same line up to renaming.
- **Growing outward from one end makes the start a hub.** Each knot then holds the start: B(start, end, new). The start is the
  reference value for every other, so that B(start, end, new) reads "if the end differs from the start, so does the new one".
  This is a property of that growth rule, not of the line. Growing inward, each new distinction between the two last placed,
  builds the same kind of line with every distinction in at most three knots and no hub. What every rule needs, by the straddle
  lemma, is a knot across every pair of places where the values could change twice.
- **The grown line is pairwise, and an exact ruler.** It is built from not-all-equal-class knots, so its pair counts carry all its
  information, and its count is 2|i − j|, with nothing skipped. Whatever knots generate it, its states put every distinction
  between every two on either side: each relates to all the others, as the owner says "3" does.
- **Two independent orders, statically.** On a grid, put betweenness on every triple with the middle one inside the box of the
  other two. The states are then exactly the row cuts and the column cuts: 10 on 3 × 3, 12 on 3 × 4. The count is twice the L1
  distance, and betweenness is exactly "inside the box". The base holds two independent orders, rows and columns. This is a given
  meeting pattern; no growth rule for it is claimed yet.

In the owner's terms, on knots alone: an order with nothing skipped, read and continued from the states, in which each
distinction relates to every other. Growing the order needs at each step a knot across the place where the new distinction goes.
The states tell the pattern where those places are. They do not tell it which one to choose, and the choice leaves no trace.

| Rule (one knot per step) | Line at every n? | States at n = 14 | Why |
| --- | --- | --- | --- |
| start: B(start, end, new) | yes | 28 = 2n | forced for outward growth (K3) |
| states only: ends found from the counts, a random side | yes, ends found uniquely at every step | 28 | K5 |
| spiral: new between the last two placed | yes | 28 | K4; no hub |
| neighbour: B(previous, end, new) | no, from n = 4 | 1,220 = 2·F(15) | K2: two changes slip past |
| random earlier: B(x, end, new) | no, from n = 5 | 456 | x not the start |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| R1 | 10 and 8 at n = 4 (0110, 1001); 16 and 10 at n = 5; 8 for B(0,1,2) with B(0,2,3) | held | exactly |
| G1 | start: a line, 2n | held | 6 … 28 |
| G2 | neighbour: not a line from 4, 2·F(n + 1) | held | 10, 16, 26, 42, 68, … 1,220 |
| G3 | random: not a line at 14 unless every x was the start; count in (28, 1,220) | held | 456; a line only at n = 4, where x was the start |
| G4 | states: a line, ends unique | held | every step |
| G5 | spiral: a line | held | every n |
| X1 | exactly m + 1 single knots keep a line, all betweenness: m − 1 between neighbours, 2 beyond the ends | held | 4, 5, …, 9 at m = 3 … 8; kinds read post hoc (below) |
| X2 | 3 × 3: 10; 3 × 4: 12; d = 2·L1; betweenness = boxes | held | exactly |

8 of 8 held.

**X1's kinds, read post hoc.** The run's flag for a knot's kind compared one stored representation literally. A knot with a
reordered place list and its excluded pair written in that order showed as "not betweenness". So the flags were unusable.
Reading each stored constraint's excluded pair and its odd place gives exactly the predicted kinds at every m:
- m − 1 knots with the new distinction in the middle between neighbours k and k + 1;
- B(0, m − 1, new) beyond one end;
- B(m − 1, 0, new) beyond the other end.

The count, m + 1, was computed as frozen.

## What it means for A97

On knots alone, in one dimension, the owner's reading holds exactly: a distance that carries all the information, the
disagreement count of a pairwise base, orders it with nothing skipped, and every distinction relates to every other. What it costs
is states. The line has only 2n of them (`DISTANCE-ORDER-20261117-001`, statement 6: order costs states). The weave, the critical
two-way pattern, does not do both (`WEAVE-LAWS-20261117-001`). A line of knots does.

A97 stays under challenge. It now has a positive case built from knots: the grown line, and statically the box-betweenness grid.

## What the knot picture explained

- **Codex's four-distinction failure.** Knots that each pass the knot test can still let the order turn back. To stop a second
  change, a knot must straddle it.
- **Why the start mattered in the first draft.** Outward growth from one end must keep a knot across the whole line, so it keeps
  returning to the start. Inward growth straddles each new place with its two neighbours.
- **The pattern can continue itself.** Its states name the ends and the neighbours, so it can find its own next placements. That is
  "retain the shared distinction" in the strongest form available: the states carry it, with no names and no history.

Known mathematics, labelled:
- betweenness and orders up to reversal (Huntington and Kline; Fishburn);
- cut systems of paths and grids (Buneman; median graphs);
- the NP-completeness of general betweenness (Opatrný). Our steps are easy because each is exact.

Local: the growth-rule analysis, the hub statement, and the reading in the program's terms.

## Limitations

- One dimension for growth. The two-way grid is static, and no growth rule for it is claimed.
- Only betweenness knots are grown. The exhaustive check covers all 34 three-place kinds for a single added knot, up to m = 8.
- Hidden distinctions are not allowed. With hidden copies, a local chain can carry a reference value and make local growth
  trivially consistent (the advisor's caveat on K2).
- The line's 2n states make it nearly frozen. An order with nothing skipped is bought with states.

## Reproduce

```sh
python3 -B proofs/KNOT-ORDER-20261117-001A/KNOT-ORDER-20261117-001A-P001_growing_a_line/check.py
python3 -B experiments/KNOT-ORDER-20261117-001B/KNOT-ORDER-20261117-001B-E001_growth/growth.py
```

## Advisor

Consulted before the freeze. It:
- corrected the draft's claim that every step must reach the start: inserting between neighbours needs only the neighbours, so
  there are m + 1 placements;
- gave the straddle lemma in general form, the spiral rule and the Fibonacci count;
- gave the gauge reading of the hub and the two-way grid statement.

Not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: how knots build an order | **Status:** Successful (referee pending) | The straddle lemma; m + 1 placements; the states name them; the grown line is pairwise and an exact ruler; 8 of 8 held |
| Local direction: an order built and continued by knots alone | Promising | Exact in one dimension; two independent orders exist statically on a grid |
| Broader exploration: dimension built by knots | Unexplored | Growth for the grid, and whether a law can choose to grow two ways |
| Long-term goal: G1 and G16 | Capability gained | Knots alone build an order with nothing skipped and read its next placements from their states |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Grow the two-way grid with knots: which knots must each new distinction share, and can the states name the placements? | 3/3, two independent orders grown by knots | 2/3: the straddle lemma generalises to cuts of a grid | Freeze the single-knot (or fewest-knot) extensions of a grid's cut system → stop at the rule or at an obstruction | Alternative |
| 2 | A law that chooses: a uniform rule reading only the states that grows a line, or a grid, without being told which | 3/3 | 1/3 | Look for a local rule on the states whose growth is forced → stop at a rule or an obstruction | Alternative |
| 3 | The price: how few states an order with nothing skipped can have, and lines with hidden distinctions | 1/3 | 3/3 | Census of small bases → stop at the bound | Alternative |

**Corrections:** none.

**Goals:** a G1 and G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 stays Under challenge, with a positive case built from knots; no new entry.

**Basket:** read; B195 (outlines) is left to its owner.
