# A probe of the rosters that widen

Sub-goal B334, 25 November 2026, after the study `KNOTS-WITHIN-REACH-20261125-001` closed and its headline was
corrected ([the first look](../README.md)). The owner asked which directions to keep hot and said to go on with this
one. **This is a probe by the thread, not a frozen study**: nothing was registered beforehand, and every number here
was seen before it was written down. It uses the study's engine unchanged, and its headline stages were grown again
with a second engine.
[The probe](probe.py) · [its driver](drive.py) · [the runs](probe_runs.jsonl.gz) · [the second engine](second_engine.py) ·
[the starts](fast_starts.json)

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

## How it was checked

- **A second growth engine.** Six stages (census 19 after rounds 10 and 20; 177 after 10 and 15; 218 after 10; 178
  after 20) were grown again with the round of the study of births one at a time, and the members, their meetings
  and the counts recomputed without any code of the reach study: the same knots, members, neighbour counts and
  counts at every r.
- **The knot test.** The reach study tested every knot of its runs of twelve of these starts (the nine of three and
  four knots, and census 1964, 2236 and 2694) under the ordinary count and the cap of three, to the same bounds, with
  no failing knot. The other eleven five-knot starts were not knot-tested; two of the four starts of the second row
  (census 3195 and 3288) are among them.

## Limits, said plainly

- **A probe.** No pre-registration, no independent program for the whole table, no referee. The formulas were found
  by looking at the counts.
- **Finite ranges.** An exact match through 7 or 13 steps on a part of a few thousand members is a count. It is not a
  proof that the part is a piece of an unbounded pattern, and no limit is taken.
- **No argument yet.** Why these starts and not others, and why these counts, is not argued here. The counts suggest
  one: the members after round t correspond to the ways of writing t as a sum of three (or four) non-negative
  whole numbers in order, two members being a step apart when one unit moves from one term to another. That is a
  guess read off C(t + 2, 2) and C(t + 2, 3), not a result.
- **Prior work not searched.** The record's studies of growth by round (lesson 8.2 of the guide: growth of a fixed
  dimension, and groups of three read as filled cells) may already describe these structures in other terms. What
  is read here, the count within reach at one round, is what the reach study's survey found unmeasured.
- **Nothing is named by space.** The literature's name is given once to make the count findable. No claim is made
  about physical space.
