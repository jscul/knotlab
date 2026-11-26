# The thread's later look inside the "undecided" one-round counts

> **Referee report R1, 26 November 2026** ([the report](../referee-R1/report.md)): the count 3r² + 3r + 1 is
> reproduced by an independent growth on all 128 saved member profiles. Two repairs to this note. "Not under the cap
> of three with waiting" is wrong: the script missed the waiting fields, and the square count holds there too on 19 of
> 32 sampled members (72 of 128 in all; the longest matches run from 12 to 20 steps). And the registered reading did
> not label these undecided because "the part is not wide enough": the exact square is the first stretch of the count
> and the classifier reads the last.

Study `KNOTS-WITHIN-REACH-20261125-001`, 25 November 2026, after the study closed. The result note reported the
registered labels of the roster count (power 1, all within reach, undecided) and concluded that what exists at one
round is of degree 1. The thread then read the counts behind the label "undecided", from the study's own raw records,
with no growth rerun. [The script](square_law.py) · [its output](square_law.json).

**What it found.** On four census starts, under three laws, the count of members within r steps of a member is
exactly 3r² + 3r + 1, the count of a six-regular pattern (the literature's centred hexagonal numbers, the count of a
triangular lattice), from r = 0 through as many as 20 steps:

- **The starts**: the three-knot start in which every two knots share one distinction and each holds two loose
  distinctions (census index 19, stars `[[0,1,3,4],[0,2,5,6],[1,2,7,8]]`), and three four-knot starts (indices 164,
  172 and 214).
- **The laws**: the ordinary count, and the cap of three with short knots retiring or making offshoots. Not under
  the cap of three with waiting.
- **The roster**: one part at every round, of t(t + 1)/2 + 3 members after round t (2,214 after round 66), with
  3 + t/2 + t²/2 births a round.
- **The match**: 53 sampled members' counts equal 3r² + 3r + 1 from r = 0 through at least r = 5; by run the longest
  matches are 14 to 20 steps. Where a count leaves the formula it falls below it, as it must once it reaches members
  with fewer than six members within a step.

**Why the study said "undecided".** The registered reading asks for one power, within a factor of 2, over a range of
at least a factor 8 starting no lower than 4, so through at least 32 steps. After 66 rounds the counts follow the
square law for 14 to 20 steps from the best-placed members and then fall below it (the part's farthest member is
about 50 steps away), and the run at 132 rounds passed the registered bound of 50,000 knots.
The label was right by its rule; the conclusion drawn from the labels was not.

**What followed.** A probe then read the count from every member on all 23 starts whose births grow fastest:
[the probe of the rosters that widen](roster_probe/README.md). Nine starts have this count, and four have a count
that grows as the cube of r.

**Limits.** Four starts, one length of run, up to 8 sampled members each; the other five starts with births of
degree 2 under the capped laws, and the starts with births of degree 3, were not read at one round. An exact match on
a finite range is a count, not a proof that the roster is a six-regular pattern, and nothing here is named by space.
Every knot of these runs that the study tested passed the knot test.
