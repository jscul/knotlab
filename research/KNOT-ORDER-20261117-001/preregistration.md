# How knots build an order: which distinction each new knot must share. Pre-registration

Epic `KNOT-ORDER-20261117-001`, 17 November 2026, by Claude. The owner answered knots first ("The knots are themselves the
smallest form of spatial topology"; "3" relates "to all other numbers, not just neighbors"). Codex recommended this question and
the coordinator gave the go-ahead. Goals G1 and G16; tests A97. It builds on `OPEN-END-GROWTH-20261107-001` (knots grow a chain at
open ends) and `DISTANCE-ORDER-20261117-001` (betweenness in the disagreement count is a three-place constraint). Frozen before any
read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

Can a growing knot pattern itself identify and retain the shared distinction that keeps its order consistent?

Codex's four-distinction example (`DISTANCE-ORDER-20261117-001`, "Local and global betweenness"; rechecked here):
- B(a, b, c) and B(b, c, d) each pass the knot test, yet together they allow 0110: 10 states, where a consistent order allows 8;
- B(a, b, c) with B(a, c, d) allows exactly the 8.

## Ticket A: the proof (written before this freeze)

`proofs/KNOT-ORDER-20261117-001A/KNOT-ORDER-20261117-001A-P001_growing_a_line/proof.md`, checked by its `check.py`.
- **K1.** To exclude a state with two changes, a constraint must straddle them.
- **K2.** Knots in windows of r places cannot make a line.
- **K3.** Growing at an end in a fixed order needs a knot holding both ends and the new distinction. With one knot per step it is
  B(start, end, new), which makes the start a hub.
- **K4.** Inserting a distinction between two neighbours needs only those neighbours. A single betweenness knot keeps a line at
  exactly m + 1 placements, and inward growth has no hub.
- **K5.** The states, with names and history erased, name every placement. Up to renaming, all placements give the same line, and
  no direction is stored.
- **K6.** The line is pairwise and an exact ruler. The base implies betweenness on every triple, whatever knots generate it.
- **K7.** Betweenness knots on every box triple of a grid allow exactly its row and column cuts. Their count is 2·L1, and they
  hold two independent orders.

## Ticket B: computations

- **R1.** Codex's counts at n = 4 and 5: consecutive triples, all triples, and B(0,1,2) with B(0,2,3).
- **R2.** Growth from the single knot B(0, 1, 2) to n = 14, one knot per step, under five rules:
  - *start:* B(start, end, new);
  - *neighbour:* B(previous, end, new);
  - *random:* B(x, end, new), with x uniform among the earlier distinctions;
  - *states:* find the ends from the states alone, pick a side at random, add B(far end, near end, new);
  - *spiral:* the new distinction between the last two placed.

  For each n: the number of states, whether the base is the line along the rule's order, and, for the states rule, whether the ends
  were found uniquely.
- **R3.** From the line on m = 3..8 distinctions: every one of the 34 three-place knots, on every triple containing the new
  distinction. The read-out is the number of distinct constraints that keep the base a line, with their kinds.
- **R4.** The static two-way test: box-triple betweenness on the 3 × 3 and 3 × 4 grids. The read-out is the number of states,
  whether d = 2·L1, and whether betweenness equals the boxes.

## Predictions (frozen; checked with the advisor)

| # | Prediction | Fails when |
| --- | --- | --- |
| R1 | 10 and 8 states at n = 4, the two extras 0110 and 1001; 16 and 10 at n = 5; 8 for B(0,1,2) with B(0,2,3) | otherwise |
| G1 | start: a line at every n, 2n states (28 at 14) | otherwise |
| G2 | neighbour: not a line from n = 4, with 2·F(n + 1) states (10, 16, 26, 42, …, 1220 at 14) | otherwise |
| G3 | random: not a line at n = 14 unless every chosen x was the start, with states strictly between 28 and 1220 | a line with some x not the start, or a count outside |
| G4 | states: a line at every n (28 at 14), the ends found uniquely at every step | any failure |
| G5 | spiral: a line at every n, 28 at 14 | otherwise |
| X1 | exactly m + 1 distinct single knots keep a line at each m = 3..8, all betweenness knots: m − 1 with the new distinction in the middle between two neighbours, and 2 beyond the ends | another count or kind |
| X2 | 3 × 3: 10 states; 3 × 4: 12; d = 2·L1 and betweenness = boxes on both | otherwise |

**What would count against the reading.**
- An exhaustive count other than m + 1.
- The spiral or the states rule failing.
- A rule that leaves some (p, q) unstraddled and still gives a line, which would contradict K1.

**The headline, stated before running.** A line grows by one betweenness knot per step.
- Placing the new distinction between two neighbours needs only those neighbours.
- Placing it beyond an end needs both ends, and the states themselves identify them.
- Purely local outward growth fails at four distinctions.
- No direction is stored: up to renaming, every admissible placement gives the same line.
- The grown line is pairwise, and its disagreement count is an exact ruler. In the owner's terms, a distance that carries all the
  information and steps outward with nothing skipped, built from knots alone, in one dimension.
- Statically, betweenness knots on every box of a grid hold two independent orders.

What is classical, and what is not:
- **Classical:** betweenness axioms; the order determined up to reversal (Huntington and Kline; Fishburn); cut systems of paths
  and grids (Buneman; median graphs).
- **Hard in general:** deciding an arbitrary betweenness system is NP-complete (Opatrný). Growth here is easy because each step is
  exact.
- **Local:** the growth-rule analysis, the hub statement, and the reading in the program's terms.

## Prior work in the program

`python3 -B scripts/track.py objects "growing a chain of knots order betweenness open ends" --until 2026-11-17 --exclude KNOT-ORDER-20261117-001`

- `OPEN-END-GROWTH-20261107-001`: growth at knots holding two open ends grows the two-way thread, a ruler in bond distance. This
  study reads the order in the disagreement count instead.
- `DISTANCE-ORDER-20261117-001` and the review's "Local and global betweenness": the predecessor and Codex's example.
- `LOGIC-AXIS-20261107-001`: the logical number line in bond distance.
- `DISTANCE-DIM-20261117-001`: orders of implications read back from their states.
- `ENDLESS-BLOCK-20261112-001`: a relative (stitched harmony copies locking along open and closed chains of knots; no order reading).

## Runs and stop rule

One script, `growth.py`, one process, expected under ten minutes. The study stops after its read-out, followed by A97 status, the
decision note, the referee hand-off and the report.

The advisor was consulted before this freeze. It:
- corrected the draft's claim that every step must reach the start: inserting between neighbours needs only the neighbours, which
  gives m + 1 placements, not 2;
- gave the straddle lemma in general form, the spiral rule, the neighbour rule's Fibonacci count, the gauge reading of the hub,
  and the two-way grid statement.
