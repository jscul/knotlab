# A probe of the rosters that widen

Sub-goal B334, 25 November 2026, after the study `KNOTS-WITHIN-REACH-20261125-001` closed and its headline was
corrected ([the first look](../README.md)). The owner asked which directions to keep hot and said to go on with this
one. **This is a probe by the thread, not a frozen study**: nothing was registered beforehand, and every number here
was seen before it was written down. It uses the study's engine unchanged, and its headline stages were grown again
with a second engine.
[The probe](probe.py) · [its driver](drive.py) · [the runs](probe_runs.jsonl.gz) · [the second engine](second_engine.py) ·
[the starts](fast_starts.json) · [the matching and the larger starts](model_check.py) · [their output](model_check.json)

> **Referee report R1, 26 November 2026** ([the report](../../referee-R1/report.md)): an independent growth
> matched all 142 runs and 958 recorded stages, and matched every one-step pair to the description on all 25 stages.
> Read this note with these changes.
> - For "the best-placed member" and "from every member" read: the greatest count at each step over the members
>   examined. Of the 958 stages, 681 read every member of the largest part, 69 a sample, and 208 sizes only. Counting
>   every member on the 69 sampled stages changes later greatest counts on 23 and no formula's range.
> - The member with the most within one step need not be the member with the most within three.
> - The probe's second computation compared totals, counts by number of neighbours and greatest counts; that cannot
>   show the one-step pairs are the same. The referee's explicit matchings do.
> - The knot test here is a sample: 200 made knots a run.
> - All four families now have proofs, in the study of widening rosters
>   ([its note](../../../WIDENING-ROSTERS-20261125-001/rosters.md)); the two denser size formulas hold from round 3.

## What the record already had (searched after the probe)

The main fact was already in the record, by another count. The study of the first knot
([FIRST-KNOT-20261118-001](../../../FIRST-KNOT-20261118-001/first_knot.md), 18 November 2026; its Proposition 4, proved,
computed for m = 3, 4, 5) shows that m knots of m + 1 places, each sharing one distinction with every other, grow
m-dimensionally under the fewest counts, where its "dimension" counts the knots made up to round t. It rests on the
study of the fresh count ([FRESH-COUNT-20261118-001](../../../FRESH-COUNT-20261118-001/fresh_count.md): the growth is
the pattern of down-closed sets of its chains of offshoots, proved). The start of three knots in the first row below
is its case m = 3, and the plainest start of the second row is its case m = 4.

**What this probe adds** is the count at one round, which those studies did not read: what exists after round t has
one degree less than their count by round, with exact counts and an exact description (below); which laws keep it;
and which of the census starts do it, among them starts that are not of that form and two denser kinds the
proposition does not cover. It adds no new dimension: the degree at one round is the start's arrangement, m − 1 for
m mutually sharing knots, and can be any number.

## What was read

- **Starts**: the 23 census starts, of three to five knots, whose births per round grow as the square or the cube of
  the round under the ordinary count (19 and 4 of them), out of the 469 starts the study's first table ran.
- **Laws**: the ordinary count; retiring with no cap; the cap of three with short knots waiting, retiring or making
  offshoots; the cap of four with retiring. Not-all-equal throughout; parity on four starts, with the same rosters.
- **The count**: after rounds 10 to 40 (or the round at which the run passes 50,000 knots), the number of members of
  the part within r witnessed steps of a member, from every member of the part, or from an even sample of at most
  2,500. Two members are one step apart when some knot shares a distinction with both. "The best-placed member" is
  the member with the greatest count at each r.

## What was found

| Starts | Laws under which the part stays whole | Members after round t | Most members within one step | Count from the best-placed member | Range it holds on |
| --- | --- | --- | --- | --- | --- |
| 9 (census 19, 164, 172, 214, 1350, 2086, 2216, 2772, 3075) | all six | t(t + 1)/2 + 3 | 6 | 3r² + 3r + 1 | r ≤ 4, 6, 8, 9, 11, 13 after rounds 15, 20, 25, 30, 35, 40 |
| 4 (census 177, 218, 3195, 3288) | the ordinary count; no cap with retiring; the cap of four | C(t + 2, 3) + 4 | 12 | (2r + 1)(5r² + 5r + 3)/3 | r ≤ 3, 4, 6, 7 after rounds 15, 20, 25, 30 |
| 8 (census 178, 179, 219, 1382, 2218, 2231, 2694, 3077) | the ordinary count; no cap with retiring | 9, 16, 28, 44, 64, 88, … from round 2 (births 4 − 2t + 2t²) | 13 | 12r² + 2 for r ≥ 1 | r ≤ 6 after round 20, r ≤ 12 after round 40 |
| 2 (census 1964, 2236) | the ordinary count; no cap with retiring | 12, 27, 59, 107, 171, 251, … from round 2 (births 27 − 24t + 8t²) | 22 | 48r² − 48r + 24 for r ≥ 2 | r ≤ 5 after round 20, r ≤ 8 after round 28 |

- **The first row** is the six-regular count of the first look, now on nine starts and under every law read. Its
  part has three members with one member within a step, three with three, 3t − 6 with four, and the rest with six.
- **The second row is a count that grows as the cube of r, at one round.** On four starts of four or five knots the
  members are one part; a member with the most members within a step has twelve; and the count within r steps
  is 1, 13, 55, 147, 309, 561, 923, 1415: the count of the literature's face-centred cubic packing (its centred
  cuboctahedral numbers), exactly, on a range that lengthens with the rounds. From any of the four members
  that have a single member within a step the count is C(r + 2, 3) + 1 through r = t. Under any cap of three the part breaks into four or five parts
  whose counts are 2r + 1.
- **The third and fourth rows** are parts that grow as the square of r with a denser neighbourhood. Their counts are
  exact quadratics from the first or second step on.
- **Where a count leaves its formula it falls below it**, as it must once it reaches members that have fewer members
  within a step, and the range on which it holds lengthens with the rounds in every row: about a third of the round in the first row, about a quarter in the
  second.
- **Under parity** the rosters of the four starts read (census 19, 177, 218, 178) are the same, round by round.

So, with dimension taken as the program defines it, the growth rate of the count within r steps: what exists at one
round has dimension 2 on 19 of these starts and dimension 3 on 4, under the ordinary count with nothing added, on
the ranges read. The count over the whole history has one degree more, which is the rounds.

## The matching, and larger starts

- **An exact description of the first two rows.** After round t, the members and their one-step relation are the same,
  up to renaming, as this: the ordered ways of writing t − 1 as a sum of m non-negative whole numbers, two of them a
  step apart when one unit moves from one term to another, with one further member attached to each of the m sums
  that have a single non-zero term (m = 3 in the first row, 4 in the second). An exact isomorphism search confirms it
  on all 25 stages tried: the mutually sharing starts for m = 3 (rounds 4, 8, 12, 16), m = 4 (4, 6, 8, 10) and m = 5
  (4, 6, 8), and seven census starts of the two rows after rounds 6 and 9. With the earlier proposition this gives an
  argument to write: the knots made in a round are the down-closed sets of one size in m chains, which are those
  sums; the m further members are the chains' newest offshoots; and two members share a knot exactly when one unit
  moves. It is not written as a proof here.
- **Larger starts go on the same way.** Five knots of six places, each sharing with the other four: C(t + 3, 4) + 5
  members after round t, twenty within one step, and the count 1, 21, 131, 471 through 3 steps after 16 rounds. Six
  knots of seven places: thirty within one step. So the degree at one round is m − 1, with m(m − 1) members within a
  step.

## How it was checked

- **A second growth engine, on every start.** All 23 starts were grown again under the ordinary count with the round
  of the study of births one at a time, and the members, their one-step relation and the counts recomputed with no
  code of the reach study, after rounds 10, 15 and 20: the same knots, members, neighbour counts and counts at every
  r on 69 of 69 stages (on two of them the probe had read a sample of the members, and only the knots and members
  are compared). [The check](confirm.py) · [its output](confirm_second.json)
- **The knot test, on every run.** The reach study's own routine, unchanged, on the 92 probe runs of the 23 starts
  under four laws: the start knots and a seeded sample of 200 made knots of each run, by two methods under each knot
  law. 18,820 knots tested under not-all-equal and the same under parity, none failing, none untested, the methods
  never disagreeing; no run closes under parity. [Its output](confirm_ktest.json)
- **The matching** of the first two rows with their description is exact on all 25 stages tried (above).

## Limits, said plainly

- **A probe.** No pre-registration and no referee, and both engines were run by the thread. The formulas were found
  by looking at the counts.
- **The knot test is of a sample**: the start knots and 200 made knots of each run, not every knot.
- **Finite ranges.** An exact match through 7 or 13 steps on a part of a few thousand members is a count. It is not a
  proof that the part is a piece of an unbounded pattern, and no limit is taken.
- **The argument is sketched, not written.** For the first two rows it follows the earlier proposition, and the
  matching above is exact on every stage tried. The third and fourth rows, and the census starts of the first two
  rows that are not mutually sharing knots, have no argument: why those starts, and what their denser parts are, is
  open.
- **Three is not singled out.** The second row's cube is the case m = 4 of a family; m = 5 gives the fourth power.
  The earlier study already concluded that the number is the start's arrangement and not the law's own.
- **Nothing is named by space.** The literature's name is given once to make the count findable. No claim is made
  about physical space.
