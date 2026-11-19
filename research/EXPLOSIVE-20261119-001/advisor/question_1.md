# Question for the advisor (EXPLOSIVE-20261119-001, before the freeze)

You have no tools. Answer only from this text, say where you are unsure, and keep it short.

**Setting.** As in the dead-knot study you checked. Outside the class, (S3) fails: a round-1 group of three exists. That is exactly
a cycle of three blocks: three live knots pairwise in three different blocks, none holding all three. A group of three makes one
round-1 junction with three parents, in place of the three pair junctions. BREAK-EDDIES found an "explosive" kind: counts leap
(80, 32, 31, 465, 4,495, 31,465) and the largest group jumps (13, 66) or falls back (24, 2, 3, 4, 5). Its known shapes are two
triangles joined twice and the three-regular six-knot graph, with knots of six or seven places, plus an eight-knot start, G-121.

**Exploration (disclosed).**
- Of the touch census (at most five knots, at most five places), 389 starts don't stall, satisfy (S4), and hold exactly one cycle
  of three blocks. All close, or grow polynomially in dimension 1, 2 or 3. The largest group in rounds 1–20 is 3 to 6.
- **The filled reading.** Glue a 2-cell on each cycle of three blocks. Read rays from the true round-1 demand, where a group of
  three counts once, and take the tree rule: the most rays in a piece, a finished piece counting 2 when there are two or more
  pieces. This gives each of the 389 starts' measured class exactly.
- The census's 82 starts with 3 or 6 such cycles all have filled b1 = 0 (over GF(2)), and all close or grow polynomially. 8 of them
  reached the junction cap with dimensions 2 to 4 measured.

**Plan, to freeze.**
- **Populations:**
  - fresh random starts of 6–12 knots within five places (dead knots allowed);
  - 6–10 knots within seven places;
  - each kept if it doesn't stall, satisfies (S4) and holds at least one cycle of three blocks;
  - plus the census and BREAK-EDDIES's reference shapes.
- **Each start** is grown to round 20 or 6,000 junctions, recording the largest group per round. It is classed as:
  - polynomial of dimension D if the D-th differences of the last five counts vanish;
  - "not polynomial in reach" otherwise;
  - "explosive" if the largest group reaches 20, or the last three ratios rise past 3.
- **Predictions:**
  - X1: the filled reading equals the measured class on every in-reach start with filled b1 = 0, one cycle or several.
  - X2 (risky): within five places, no start is explosive.
  - X3: within seven places, at least one start is explosive.
  - Readout: the filled Betti numbers b1 and b2 of the explosive starts, and the smallest explosive start's largest group per round.

**Questions.**
1. Is the filled map a sound object? Why would a group of three behave like a filled 2-cell, i.e. kill that cycle for the growth?
   Is there a short argument I could prove? It seems to say a group of three does not unroll.
2. If filling is right, what should make a start explosive: a filled map with b1 ≥ 1, b2 ≥ 1 (an enclosed void, such as the four
   triangles of K4's blocks), or groups that overlap in a point? Predict which, for two triangles joined twice.
3. Are my class definitions honest? In particular, "explosive" by group ≥ 20, and polynomial by differences over 20 rounds.
4. Is X2 a sensible risk, and what would you change before freezing?
