# Planted walls: selective configurations on every torus

Status: Proved

Ticket `WALLS-WITH-CHOICES-20261024-001C`, 2026-10-24.

**What it uses:**
- from `WALLS-WITH-CHOICES-20261024-001A-P001`: Theorem 1 (periodic walls decide every direction), the wall moves, and the
  Lipschitz argument of Theorem 3;
- from `DIRECTIONAL-RIGIDITY-20261023-001B-P001`: the constant frame, Lemma B (the frame flip and the half turn), and the
  placements and their kinds;
- from `DIRECTIONAL-RIGIDITY-20261023-001A-E001` (frozen, supported): the counts in Remark 4.

## Standard statement

### Setting

- **The torus and the twist.** Squares S = (i, j) with 0 ≤ i < L and 0 ≤ j < M, where L, M ≥ 3. The square of (i, j) holds the up
  and down triangles at (i, j).
  - Work in the constant frame with relative twist r = (1, 1).
  - For a placement whose frame complements place 1, that means the twist (1, 1) + (L, M) in the placement's own terms.
  - The odd classes are those with c₁ + c₂ odd; among them are (1, 0), (0, 1), (1, 2) and (2, 1).
- **The cross and W\*.** The cross is column 0 together with row 0. W\* is the staircase that goes like this:
  - it climbs column 0 from the corner (0, 0), crosses the horizontal seam and returns to the corner;
  - it then runs left along row 0, crosses the vertical seam and returns to the corner.
  - Its class is (−1, 1), and r(−1, 1) = 0, so it closes with its left value.
  - That left value, relative to the twist, is 0 on the column and on the row. At the corner it is 1 on arrival from below and 0
    on arrival from the right.

**Lemma 1 (what W\* blocks).** As a periodic wall, W\* meets its own translates by (L, 0) and by (0, M), through its runs of L
moves left and M moves up. It crosses every cylinder of a class with c₁c₂ > 0 without meeting its copies, since it moves only up
or left (the argument of Theorem 3 in `WALLS-WITH-CHOICES-20261024-001A-P001`).

**Theorem 2 (planted walls).** For every L, M ≥ 3 the following configurations exist.
- **(a) Directed walls without choices: 147, and 54 through the frame flip.**
  - The configuration: the corner's up triangle has coin 0 and its down triangle coin 0. The column's up triangles have coin 1
    and down triangles coin 0. The row's up triangles have coin 0 and down triangles coin 1. Every other triangle has coin 1 on
    the up triangle and 0 on the down triangle.
  - Its only periodic wall is W\*, taken in either direction.
- **(b) Directed walls with a free place: 155; 110, 203 and 62 through the frame flip and the half turn.** The up-bond into a
  square is open for the copy 1 + coin(up triangle), and the left-bond out of it for the copy 1 + coin(down triangle).
  - The configuration, as (up-bond, left-bond) copies: the corner (1, 1); the column (0, 1); the row (0, 0); the squares of row 1
    off the column (1, 0); everything else (0, 0).
  - Its only periodic wall is W\*.
- **(c) Walls turning both ways without a free place: 151, and 109 through the frame flip.**
  - The configuration: coin 1 everywhere except the corner's two triangles, the column's down triangles and the row's up
    triangles, which have coin 0.
  - The periodic walls are W\* and a braid W₂ of class (1, 1) with 10(L + M) − 34 states, which winds up the column and along the
    row and meets its translates by (L, 0) and (0, M).
  - Every other closed walk is a loop around one lattice vertex: six states for each copy at each vertex (i, j) with
    2 ≤ i, j and i ≤ L − 1, j ≤ M − 1, and two loops of ten states.
- **Hence**, by Theorem 1 of `WALLS-WITH-CHOICES-20261024-001A-P001`, each of these eight configurations contradicts along (1, 0)
  and (0, 1) and has assignments along (1, 2) and (2, 1). So it is selective, on every torus with L, M ≥ 3.

**Corollary 3 (which contacts are selective on every torus).** The eight bending contacts with directed walls or without a free
place (54, 62, 109, 110, 147, 151, 155, 203) are selective on every L × M torus with L, M ≥ 3. Together with
`DIRECTIONAL-RIGIDITY-20261023-001B-P001`, a three-place tiling contact of these kinds is selective on every such torus, and a
contact with stripes or straight walls on none.

**Remark 4 (the kind left open).** For the four bending contacts whose walls turn both ways and have a free place (111, 125, 159,
215) no uniform construction was found.
- **Why the planted wall does not work.** Their free turns make walls almost unavoidable.
  - In the frozen exhaustive record no configuration on 3 × 3 or 3 × 4 contradicts along every odd class: 0 of 3145728 and 0 of
    201326592 configuration-twists, while 2967072 and 192641088 contradict nowhere.
  - So no quiet background exists to plant W\* in.
- **How they select instead.** They are selective on every torus computed, through walls that wander enough to meet their own
  copies along some classes and not others.
- **Status.** Whether they are selective on every large torus stays open.

## Nearest known result

- **Elementary.** Planting a defect line and suppressing all others is a standard way to build examples in tiling and subshift
  theory.
- **New to the program.** The specific configurations, and the counting proof of (c).

## Proof

### Lemma 1

- **Runs.** W\* makes L consecutive moves left along row 0, and travels exactly (−L, 0) during them. So it meets W\* − (L, 0),
  that is, it meets its translate along the cylinder of class (1, 0). The same holds for the M moves up and the class (0, 1).
- **First quadrant.** W\* moves only up or left. So the Lipschitz argument of Theorem 3 in
  `WALLS-WITH-CHOICES-20261024-001A-P001` shows that W\* misses W\* + kw for every k ≠ 0 when c₁c₂ > 0, and its class (−1, 1)
  is transverse to such c. ∎

### Theorem 2(a)

**The model.** For 147 (no frame flip), every crossed triangle has its lone corner at place 0 or 2. So a wall passes through a
unit square from bottom or right to left or top.
- Each copy of a square has exactly one entry side and one exit side. Write E(S) for the copy that enters from the bottom; the
  other copy enters from the right. Write X(S) for the copy that leaves at the top; the other leaves on the left.
- With the pinned value 1 of both places, E(S) = 1 + coin(up(S)) and X(S) = coin(down(S)).
- Hence every state has at most one successor and at most one predecessor.

**The configuration.**
- The corner has E = 1 and X = 0, so its copy 1 turns from up to left and its copy 0 from left to up.
- The column squares are straight with copy 0 going up; the row squares are straight with copy 0 going left.
- Every other square is straight with copy 0 going up and copy 1 going left.
- W\* is a closed walk, carrying copy 0 on the column and the row.

**Every other state dies within L + M steps.**
- **Copy 0 going up a column i ≥ 1.**
  - It reaches row M − 1 and crosses the horizontal seam, so its copy becomes 1.
  - It enters the row square (i, 0), whose copy 1 enters from the bottom and goes up.
  - It then reaches (i, 1), whose copy 1 enters only from the right, and stops.
- **Copy 1 going left along a row j ≥ 1.**
  - It reaches the column square (0, j), whose copy 1 goes left.
  - It crosses the vertical seam, so its copy becomes 0.
  - It reaches (L − 1, j), whose copy 0 enters only from the bottom, and stops.
- **The other copies of cross squares.** The copy 1 of a column square goes left and the copy 1 of a row square goes up, so these
  are covered by the two cases above.
- **Conclusion.** No closed walk other than W\* exists. Its reverse is the same wall traversed the other way.

54 follows by Lemma B: the frame flip, then the global exchange of coins that turns the flipped relation into 54. ∎

### Theorem 2(b)

**The model.** For 155 (place 2 free, place 0 pinned with value 1), a crossed triangle again has its lone corner at place 0 or 2,
so walls move up or left.
- Entering a square from the right uses the free corner of its up triangle, and leaving at the top uses the free corner of its
  down triangle.
- Entering from the bottom needs the up-bond open for the wall's copy; leaving on the left needs the left-bond open.

**W\* has no branches.**
- On the column its copy 0 cannot leave on the left, since that bond is open for copy 1.
- At the corner, its copy 1 cannot go up, since the up-bond of (0, 1) is open for copy 0. Its copy 0 cannot leave on the left,
  since that bond is open for copy 1.
- On the row its copy 0 cannot go up, since the up-bonds of row 1 are open for copy 1.
- So each state of W\* has exactly one successor, the next one on W\*.

**The other copies have no predecessor.** These are copy 1 of every square off the cross, and copy 1 of the column and row squares.
- A predecessor from below would need an up-bond open for copy 1, after allowing for the seam. Off the cross that happens only
  into row 1, from copy 1 of a row square, which is itself such a state.
- A predecessor from the right would need a left-bond open for copy 1. The only such bonds are the column's, and crossing the
  vertical seam turns copy 1 into copy 0.
- A chain of such states would have to start somewhere, and no state outside this set leads into it. So none of them lies on a
  closed walk.

**Copy 0 off the cross.**
- It moves up or left within rows 1 to M − 1 and columns 1 to L − 1.
- Leaving row M − 1 at the top crosses the seam into copy 1 at a row square. That square's up-bond is open only for copy 0, so the
  wall stops there.
- Leaving column 1 on the left enters the column square in copy 0, that is, onto W\*. There it stays, since W\* has no branches.
- So no closed walk passes through these states either.

**Conclusion.** The only closed walk is W\*. The other three contacts follow by Lemma B. ∎

### Theorem 2(c)

**The model.** For 151 every lone corner is pinned with value 1. The copy 1 + coin turns left at a triangle and the other copy turns
right. Every state therefore has exactly one successor, so the closed walks partition all 12LM states.

**The count.**
- The listed closed walks have these sizes:
  - W\* and its reverse: 2(L + M) states each;
  - W₂ and its reverse: 10(L + M) − 34 each;
  - the two loops of ten states;
  - 2(L − 2)(M − 2) loops of six states.
- Their sizes add up to 4(L + M) + 20(L + M) − 68 + 20 + 12(L − 2)(M − 2) = 12LM.
- So once they are shown to be closed walks, they are all the closed walks.

**The loops of six states.** Around a vertex (i, j) with 2 ≤ i ≤ L − 1 and 2 ≤ j ≤ M − 1, all six triangles are off the cross
and within one fundamental domain, so their coins are 1. There copy 0 turns left six times and copy 1 turns right six times.

**W₂, the loops of ten states, and W\*.**
- **Locality.** The planted coins depend only on whether a square is the corner, on the column, on the row, or elsewhere. Moves are
  local. So a wall's step from a square depends only on the coins of the squares next to it.
  - Along the column, rows 2 to M − 2 all have the same neighbourhood, and likewise columns 2 to L − 2 along the row. W₂'s braid
    repeats there with period one row and one column respectively.
  - The neighbourhood of radius two around the corner, including both seams, is the same on every torus with L, M ≥ 5.
- **Verification.** `check.py` verifies all three walls on every torus with 3 ≤ L, M ≤ 9. That covers every local situation,
  including the corner neighbourhood for L, M ≥ 5 and the small tori directly. With the count, this proves the list for all
  L, M ≥ 3.

**W₂'s collisions.** W₂ meets its translates by (0, M) and by (L, 0). On the 6 × 6 torus, for instance, it visits both (1, 1)
and (1, 7), and both (−1, 5) and (5, 5). The check confirms the resulting verdicts on every torus up to 9 × 9.

**Conclusion.**
- By Theorem 1, the classes (1, 0) and (0, 1) contradict: neither W\* nor W₂ is simple there, and loops cross nothing.
- The classes (1, 2) and (2, 1) have assignments through W\* (Lemma 1).
- 109 follows by Lemma B. ∎

### Corollary 3

It combines Theorem 2 with `DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Theorems 2 and 3. ∎

## Checks

`check.py` uses the standard library only. Every result below was obtained:
- **The eight planted configurations** (147, 54, 155, 110, 203, 62, 151, 109) on all 49 tori with 3 ≤ L, M ≤ 9. For each one:
  - every strongly connected part of the wall graph is a single cycle;
  - the winding walls are exactly the listed ones;
  - for 151 and 109 the listed loops and walls account for all 12LM states;
  - by Theorem 1 the configuration contradicts along (1, 0) and (0, 1) and has assignments along (1, 2) and (2, 1).
- **Direct certificates.** On 3 × 3, 3 × 4 and 4 × 4 the own solver certifies the same four verdicts for all eight.
- **Remark 4.** In the frozen exhaustive rows, none of the 3145728 (3 × 3) and 201326592 (3 × 4) configuration-twists of 111, 125,
  159 and 215 contradicts along every odd class; 2967072 and 192641088 contradict along none.
- **Controls.**
  - Without the blocking of the column's left exits, the configuration for 155 has another winding wall and is not selective on
    3 × 3.
  - In the fitting twist no class is odd.

## What this does not show

- Selectivity on every large torus for 111, 125, 159 and 215 (Remark 4).
- The general case of (c) rests on the locality argument and the verification on every torus up to 9 × 9. It is not a
  closed-form description of W₂'s states.
- Anything about other triangulations, or about space or physics.
