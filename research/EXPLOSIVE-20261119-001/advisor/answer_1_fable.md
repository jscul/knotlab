**Assumption throughout:** I read knots as points and blocks as the links between them. If blocks can hold more than two live knots, my Betti counts below change.

**1. Is the filled map sound?**
- **Round 1: yes, and provable.** A junction is a cone over its parents. Three pair junctions leave the cycle of three blocks hollow, while one three-parent junction cones it off, which is exactly gluing a 2-cell. So the round-1 demand complex is homotopy equivalent to the filled map, by a nerve argument.
- **Beyond round 1: not proved.** You would still need that the growth class depends only on that homotopy type. Later groups of 4 to 6 are higher cells that the reading never sees.
- **Weak evidence so far.** On one-cycle starts, filling cannot be told apart from "delete one block of the cycle" or "merge the three knots". Only starts whose cycles share blocks discriminate.

**2. What should make a start explosive?**
- **Two triangles joined twice:** I count b1 = 3 unfilled, and b1 = 1, b2 = 0 after filling both triangles. Filling alone would then say dimension 1, not explosive.
- **Prediction:** the cause is neither b2 nor overlap in a point. It is a surviving cycle that runs along a block of a filled group. Each lap re-meets the group and merges it with its copies, which matches the group jumps (13, 66).
- **K4's void** (b1 = 0, b2 = 1): I guess it closes. I am unsure of both guesses.
- **Freeze it as a three-way readout:** shared-block residual cycle, b2 ≥ 1, or point overlap.

**3. Are the class definitions honest?** Not yet:
- **The difference test is too short.** Five counts always fit degree 4, so D = 4 cannot be detected and D = 3 rests on one number. Use at least D + 3 counts. Also test at lags 2 and 3, or periodic-polynomial starts land in "not polynomial".
- **Group ≥ 20 by round 20 confuses linear group growth with explosion.** The series 2, 3, 4, 5 looks linear. Define explosive on the counts and report the group series separately.
- **"Ratios rise past 3" may miss the reference.** The reference ratios run 0.97, 15, 9.7, which do not rise. The 6,000 cap also cuts that series at 4,495. Run the frozen rule on the reference shapes first, and disclose it as calibration.
- **The classes overlap and have gaps.** Add "exponential, ratio under 3" and "cap-truncated, undecided", and make all classes exclusive.

**4. Is X2 a sensible risk, and what to change?**
- **X2 may be true by counting.** First check whether a residual cycle sharing a block with a group of three fits within five places at all. If it cannot, X2 is not a risk, and you should say so.
- **If it can, stratify.** Guarantee a stated number of such starts; random sampling may never hit one, and "none explosive" would then mean little.
- **X3 is already true if the reference shapes count.** Restrict it to fresh starts.
- **X1 is too safe.** Limited to b1 = 0, it skips the cases where filling could fail. State the filled prediction for b1 ≥ 1 as well, and report how many starts fall out of reach.
- **Freeze sample sizes and seeds.**
