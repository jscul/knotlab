# Referee report GRID-GROW-R1 (fresh code, no Codex)

**Verdict: G1 to G4 confirmed. One Block, on G5 ("the states name every placement") and the summaries that rest on it.**
- **What holds.**
  - The costs are right, and the referee's arguments for them apply to every Young diagram, not only those in a 4 × 4 box:
    - a new line costs exactly one knot, forced and unique;
    - a filled cell costs three, never two;
    - the totals do not depend on the order.
  - Every frozen number recomputes with the referee's own code. One size past, every reading also holds in the 5 × 5 box (251
    shapes, 629 steps) and in the 6 × 6 box (923 shapes, 2,771 steps).
  - The referee checked every minimum cover, not only the local ones. All their knots are betweenness knots.
- **The Block.** Bases with the same states can have different placements. The column of three cells and the three-cell L (the
  growth's own start) have the same states up to renaming, a line of three. Only the L has a cell to fill.
  - From the states of a straight run, the base admits a fill at every interior distinction, and each gives the cut system of a
    Young diagram. The drawing allows none of them.
  - So the states name the base's own extensions, and the given two-way drawing chooses which one is the next cell.
  - The second order first appears at the first fill, and that is where the drawing, not the states, says where to go.
  - Nothing in the study reads a placement from the states: the growth runs are handed coordinates and an order.
  - "Knots alone grow two independent orders, and the states name each next step" does not hold.
- **Narrowings.**
  - G3's "unique within L1 radius 2" is computed, not proved: the proof's premise that only a, b and c lie that close is false.
  - The ruler is the disagreement count. By `WEAVE-LAWS-20261117-001`'s rule the base is frozen, so the comparison with the weave
    mixes two readings, as in `KNOT-ORDER-20261117-001`.
  - "Two-dimensional" is the drawn grid's.

## What holds

- **Order.** The freeze, `675e4ef24`, is at 20:30:26 UTC. It holds the proof, the pre-registration and the code, whose hashes
  match the contract and are unchanged since. The run went from 20:30:26 to 20:30:40, and the epic closed at 20:32:22.
- **G1 (proved; classical).**
  - A Young diagram is isometric in the grid: a monotone path goes down then across inside it.
  - It is median-closed: of three cells, one of the two with x ≥ the median x also has y ≥ the median y, and dominates the median.
  - So box ∩ S is the geodesic interval, B on box triples allows exactly the convex sets with convex complements, and those are the
    halfspaces, the row and column cuts (Djoković; Winkler; median graphs).
  - The referee's brute force over all 2^n states agrees on all 198 shapes of at most 16 cells in the 5 × 5 box. d = 2·L1 holds on
    every one.
- **G2 (proved for every Young diagram of two or more cells; the coordinator's item 1, "forced").** Let p = (x, 0) start a new
  column, with neighbour b = (x − 1, 0). The proof is right, and one step it leaves implicit is this.
  - **Why u and v must be split by every cut.** On the two constant states p is free (one of them, with p flipped, is the new
    cut). So a knot on (u, v, p) can exclude no pattern with x_u = x_v. A single knot must kill p's wrong value on every
    non-constant cut, so u and v are on opposite sides of every cut.
  - **Which pairs those are.** In a Young diagram of w columns and h rows, they are {(0, h − 1), (w − 1, 0)} = {z, b}, plus
    {(0, 0), (w − 1, h − 1)} for a rectangle. The second does not fix b's value once row and column cuts both exist.
  - **The knot is fixed.** On (z, b, p) the targets use six of the eight patterns, so the knot excludes exactly 010 and 101: it is
    B(z, b, p).

  The census agrees: 66 of 66 new-line steps in 4 × 4, 248 of 248 in 5 × 5 and 920 of 920 in 6 × 6 have exactly one single-knot
  cover, that betweenness knot. From a single cell the cost is 0.
- **G3's lower bound (proved for every corner; the coordinator's item 1, "never two").**
  - **A knot that fixes the constants does nothing else.** A knot that kills p flipped on a constant state needs every cut to
    have u or v on p's side. Since no cell of S dominates p, its pair is one cell up and left and one down and right. That pair is
    split by both C_x and R_y, and it kills neither of their bad states: each one's bad pattern is the other one's flipped target
    pattern.
  - **No knot covers both cuts through the square.** One knot killing both the C_x and the R_y bad state would need a cell with
    x′ ≥ x and y′ ≥ y.
  - **So three are needed.** The referee rewrote both steps and finds them right. They do not depend on the box.

  The census agrees: 71 of 71 fills in 4 × 4, 379 of 379 in 5 × 5 and 1,849 of 1,849 in 6 × 6 need exactly 3 and never 2. The unit-square three cover in
  every case, and so does the four-place parity. That parity is a knot under the canonical test (`knotlab`, `is_knot: true`).
- **Every minimum cover is made of betweenness knots.** The frozen code checked only the covers within radius 2. The referee
  enumerated every minimum cover, from 1 to 40,000 distinct ones per fill. In 4 × 4, 5 × 5 and 6 × 6 every knot in every one is a
  betweenness knot.
  - A sketch of why, the referee's and not fully checked: each of the three knots kills one kind of bad state in both
    orientations. Its excluded set then holds a complementary pair, which among the 34 knots means the not-all-equal class. It is
    not the constant pair, which the constant states use.
- **G4 (proved).** Each step's base is exactly the cut system whatever knots were used, so the costs add up. Growth to 4 × 4 takes
  32 knots in both orders.
  - The busiest distinctions have 9 knots each, but there are four of them: (1, 1), (2, 1), (1, 2) and (2, 2). The note names
    three, because `run.py` printed only the top three.

## 1. "The states name every placement" (G5; the coordinator's item 2; Block)

**The claim.** G5 says: "By G1 the counts give the L1 geometry of the shape, up to its symmetries. So the outer corners, the
neighbours a, b, c and the opposite corners are all read from the states, with names and history erased." It is repeated:
- in the answer ("The states name every placement");
- in A97's new text;
- in the G1 and G16 checkpoint ("the states name each next step").

**Why it fails.** The counts give the base's L1 metric. They do not give the drawn shape.
- **Equal states, different placements.** The column {(0, 0), (0, 1), (0, 2)} and the L {(0, 0), (1, 0), (0, 1)} both have the
  states of a line of three, the same set up to renaming.
  - The column's drawn placements are two new lines.
  - The L's are two new lines and a fill at (1, 1).

  Grouped by equal states up to renaming, the 69 shapes of 4 × 4 fall into 38 classes, and the 251 of 5 × 5 into 130. In 2 and 3
  of those classes the shapes, which are not mirror images, have different numbers of placements. Each such class is a straight
  run against a run bent once at its end, the three-cell L among them.
- **The base admits fills the drawing forbids.** From the states of a straight run of n, the referee added p with the three
  knots B(a, p, b), B(c, a, p) and B(c, b, p) at each interior distinction c. Every one of the n − 2 results is, up to renaming,
  the cut system of a Young diagram (`line_fills`, checked to n = 7).
  - The drawing allows no fill on a straight run, and one on a hook.
  - So the states name the base's own one-step extensions, and the given drawing picks which of them is the next cell.
- **The two orders enter through the drawing.** Every shape that is a hook, a row and a column meeting at (0, 0), has a line of
  states. The second order first appears at the first fill, and from a line's states that fill could go at any interior
  distinction. Which one is "the corner" comes from the drawing.
- **Nothing in the study reads a placement from the states.** C3's growth runs are handed coordinates and a fixed order, and
  `step_covers` works in coordinates. Unlike `KNOT-ORDER-20261117-001`, there is no states-only rule here, and G5 is asserted
  "From G1. ∎".

**What does hold.** The new-line placement is read from the states: its two cells are the pair at the largest disagreement count,
the diameter pair. It is unique when the shape is not a rectangle; for a rectangle the two pairs are mirror images. That is the
line's own end growth.

**Why this is a Block.** It is judged against the claim under test, A97's two-dimensional positive case: "It grows one distinction
at a time, and its own states name where the next knots go." That fails exactly where the second order begins.

What survives is narrower: on a given two-way drawing, a grower told the next drawn cell pays fixed costs, and the knots it must
use are forced (a new line) or three local ones (a fill). G2 to G4 are not affected.

## 2. G3's local uniqueness is computed, not proved (Narrowing)

The proof says: "Within L1 radius 2 of p the only cells are a, b and c, so this cover is unique there." That is false. Cells such
as (x − 2, y), (x, y − 2), (x + 1, y − 1) and (x − 1, y + 1) can be in S at distance 2. One is present in 70 of the 71 fills in
4 × 4, and in 378 of the 379 in 5 × 5.
- The conclusion holds: exactly one cover within radius 2, the unit-square three, in every fill of both boxes.
- But it rests on the census, not on the proof. "Proved" should read "computed in 4 × 4 and 5 × 5".

## 3. The ruler and A97's "two-dimensional positive case" (the coordinator's item 3; Narrowing)

- **The ruler is the disagreement count,** d = 2·L1 with exact additive betweenness (A98's reading). By
  `WEAVE-LAWS-20261117-001`'s rule the base is frozen.
  - It has 2(r + c) − 2 states for r·c distinctions: 1.18 states per distinction at 4 × 4, 1.055 at 8 × 8 and 1.016 at 16 × 16.
  - So "The weave, critical, does not do this; the grid of betweenness knots does" compares two readings. This is the same point
    as `KNOT-ORDER-R1`, section 5.
- **"Two-dimensional" is the drawn grid's.**
  - The cut system of a drawn r × c arrangement is the classical cut system of a product of two paths, the product of two copies
    of `KNOT-ORDER-20261117-001`'s line.
  - The note says the pattern is given ("on a given meeting pattern"; "no law here chooses to grow two ways").
  - But A97's text and the checkpoint add "the states name every placement", which section 1 withdraws.
  - A fair line for A97: "On a drawn two-way arrangement, betweenness knots grow a base whose disagreement count is twice the drawn
    L1 distance, at fixed costs per new cell (one forced knot for a new line, three for a fill). The drawing says where each next
    cell goes. The base is nearly frozen."

## 4. The speed (the coordinator's item 4; Not a block)

- **What was frozen.** The proof, the pre-registration and the code were frozen together. The run started in the same second as
  the freeze commit and took 14 seconds.
- **Before the freeze.** The predictions came from the advisor's derivation, which the study discloses.
- **After the read-out.** The only unlabelled reading is the truncated busiest list (the "What holds" section above). "Not
  predicted" is labelled, and P4 is called bookkeeping.
- **One overstatement in the frozen readings.** The proof says the betweenness kinds of minimum covers are "checked by the census".
  The census checked only the local covers. The referee's enumeration of all minimum covers closes that.
- **Timing against `KNOT-ORDER-R1`.** The study was frozen and closed before that verdict arrived. It repeats that report's points:
  - the ruler comparison with the weave;
  - "knots alone" (here stronger, since no states-only rule exists);
  - "pairwise".

## 5. Words (the coordinator's item 5; Not a block)

- **"Pairwise."** "A pairwise base made of betweenness knots" and "the compact form of three pairwise ones" use the word that the
  glossary keeps for "defined by its two-place parts", which no knot is. The same point is in `KNOT-ORDER-R1`, section 6.
- **Words from two dimensions.**
  - The drawing's own words are fair for the drawing when marked as drawn: cell, row, column, corner, unit square, arms, Young
    diagram (the literature's).
  - The note also gives them to the base. "The cut system's own law on a unit square is a four-place parity", "a filled corner"
    and "reaching far … the far corner" describe the knots and their states.
  - Mark the drawing as drawn, give the classical names once, and say what the base itself has: a four-place parity on four
    distinctions, two of them each between the other two.

## Fixes for the thread (listed for the owner, not folded in)

1. **Withdraw G5 as stated.**
   - In its place: the states give the base's L1 metric and the new-line pair (the diameter pair). The fill placements come from
     the given drawing: shapes with equal states can have different placements, and a straight run's states admit a fill at every
     interior distinction.
   - Correct the answer, A97's text and the G1 and G16 checkpoint to drop "the states name every placement / each next step".

   **Block.** It is on that claim; G1 to G4 stand.
2. **G3.** Remove "within radius 2 the only cells are a, b and c", and mark local uniqueness as computed in 4 × 4 and 5 × 5.
   **Narrowing.**
3. **A97 and the weave comparison.** Name the ruler (A98's reading). Say that by `WEAVE-LAWS-20261117-001`'s rule the base is
   frozen. Say "drawn" before "two-dimensional". **Narrowing.**
4. **Small fixes.**
   - The busiest cells are four, (2, 2) included.
   - The kind check extends to all minimum covers.
   - "Pairwise" and the drawing's words.

   **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, the proof, `gridgrow.py`, `run.py`, the contract, the results, the note and the shared-doc
    additions;
  - checked G1 to G4 by hand for every Young diagram;
  - wrote its own shapes, cut systems, brute-force base check, step analysis (every minimum cover, local covers and the cells near
    p), the equal-states classes, the fills of a straight run, the growth totals, and the knot test of the parity.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`census_6x6.json`:** the same step census in the 6 × 6 box (`referee_grid.census(6, 6)`, about nine minutes), run after the
  first commit of this report. It confirms every count.
- **`referee_grid.py` and `.json`:**
  - 1, G1 by brute force (198 shapes);
  - 2, the step census in 4 × 4 and 5 × 5 (6 × 6 with `--six`);
  - 3, G5: the column against the L, the equal-states classes and a straight run's fills;
  - 4, growth totals;
  - 5, the parity under `knotlab` and states per distinction.

Reproduce, from `research/GRID-GROW-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_grid.py > referee_grid.json
```
