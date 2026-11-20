# Bond distances between original marks

The one-spare ring joined to a 17-knot background gives 75 exact age-one
changes between quiet and loaded histories. The loaded history has bond
distance two larger in 33 of the 120 path–path pairs and 42 of the 80
ring–path pairs. All other pairs agree, including the ten ring–ring pairs.
The 33 affected path pairs are precisely \(e_i,e_j\) with \(i=0,1,2\) and
\(j=5,\dots,15\). Nine affected pairs have both marks at least three
original knot steps from the attachment. The entire source interval still
includes the attachment in each of those nine pairs. For the largest
original index separation, \(e_0,e_{15}\) reads 37 quiet and 39 loaded.

The predecessor's 56 exact comparisons agree with the new enumeration.
All 308 predecessor lower bounds on individual arms also hold. Of the
154 previously unresolved comparisons, 75 increase and 79 agree. The
bare, one-spare and two-spare single attachments give the same 120
age-one path readings arm by arm. Each loaded table retains all 120
source path readings. Each quiet table shortens 33 by two. The cut
control admits only the quiet shared-only load in this panel. Its
\(e_2,e_5\) reading is 13 at age one,
as in the one-spare quiet history. The bare background reads 7 for
this pair at source and age one.

An independent separator calculation recovers all 210 minima in each
one-spare arm at age one and obtains all 210 at age two. Every pair in
each arm retains its age-one value at age two. In particular the
longest original index separation still reads 37 and 39 at age two.
A separate integer-flow sweep recovers 103 exact quiet and 96 exact
loaded age-two distances, with all remaining bounds containing the
separator result.

## Later reversal on the same marks

| Age | \(e_2,e_5\) quiet | \(e_2,e_5\) loaded | \(e_3,e_4\) quiet | \(e_3,e_4\) loaded |
| --- | ---: | ---: | ---: | ---: |
| 0 | 15 | 15 | 7 | 7 |
| 1 | 13 | 15 | 7 | 7 |
| 2 | 13 | 15 | 7 | 7 |
| 3 | 13 | 15 | 7 | 7 |
| 4 | 13 | 12 | 7 | 4 |

At age one the quiet \(e_2,e_5\) witness uses the original knots
\(b_3,b_5\) and the new knot they jointly produced. Their loaded
counterpart carries six fresh distinctions in place of four. At age
four the loaded \(e_3,e_4\) minimum consists of distinction IDs
3, 4, 16, 20 and 586. The same 16 newly formed knots on the inside of
that cut, together with \(b_3,b_4,b_5\), give the age-four loaded
\(e_2,e_5\) witness of size 13. The age-four quiet and loaded
presentations have 291 and 250 knots and 1,238 and 709 distinctions,
respectively.

For the longest pair \(e_0,e_{15}\), the loaded age-three value is
exactly 39. The quiet arm has a verified cut giving at most 37, so
the histories still differ. At age four the loaded value is exactly
36, while the quiet bound is 15–37. The quiet separator calculation
reached its width ceiling at both ages. The age-four difference
for this pair remains unresolved.

Along each history a complete stage preserves exactly the prior allowed
assignments on the old distinctions. Projection onto any old subset
therefore stays the same, and each prior minimal nonfree set of old
distinctions remains a bond. Bond distance between old distinctions
can only decrease or stay equal in that history. The sign reversal in
the table is a comparison of two histories at the same age.

## Two loaded rings and dose

For two one-spare rings joined four original knot steps apart, jointly
loading them increases 61 of the 120 age-one path-pair readings. The
counts are 40 at +2 and 21 at +4. At eight original knot steps the
corresponding counts are 48 and 9, totaling 57. For both starts the
interaction \(\text{both}-\text{first}-\text{second}+\text{quiet}\) is
exactly zero on all 325 original marked pairs, including the 120 path
pairs. For the longest original index separation the four arms both
read 43, 45, 45 and 47, in quiet, first, second and joint order.

At the second attachment in each double, the corresponding crossing
pair \(e_{b-2},e_{b+1}\) also reverses at age four. Here \(b\)
is the second attachment's original path index. Its reading is 13
with no second load, 15 with a second load at ages one through
three, and 12 with a second load at age four. The neighboring
pair \(e_{b-1},e_b\) reads 7 until age four and 4 then if loaded.
These readings are identical with or without a simultaneous first
load. In the longer two-ring preparation, \(e_8,e_{12}\) reads 15
through age three under all four loads. At age four it reads 12
in both second-loaded arms and 15 in both second-quiet arms.

### Later pairs spanning both attachments

All eight focused four-arm contrasts at age two are exactly zero.
At ages three and four, the table gives the certified interaction
intervals. A zero entry is exact.

| Knot steps between attachments | Marks | Age 3 | Age 4 |
| ---: | --- | ---: | ---: |
| 4 | \(e_3,e_8\) | [−1, 4] | [−1, 2] |
| 4 | \(e_3,e_7\) | 0 | 0 |
| 4 | \(e_4,e_7\) | 0 | 0 |
| 4 | \(e_2,e_9\) | [−9, 24] | [−10, 19] |
| 8 | \(e_3,e_{12}\) | [−10, 20] | [−10, 18] |
| 8 | \(e_3,e_{11}\) | [−3, 8] | [−3, 9] |
| 8 | \(e_4,e_{11}\) | 0 | 0 |
| 8 | \(e_2,e_{13}\) | [−18, 42] | [−18, 36] |

The four-step preparation's age-four \(e_3,e_7\) values are
17, 14, 17 and 14 in quiet, first, second and joint order.
Its \(e_3,e_8\) values lie in [22, 23], [19, 20], [19, 20] and
[17, 17], respectively. The two single loads and the joint load
therefore each shorten this bond distance relative to quiet. The
interaction interval includes zero. The computation used a width
ceiling of 14, two million separator transitions per query, up to
14 seconds per frame for the separator calculation, and at most
1,500 integer relaxations per fallback query. Each shorter
upper witness formed from previously checked local pieces was
rechecked against the entire stage. Later additivity beyond the
14 exact zero contrasts remains open.

### Load count on a fixed preparation

On the fixed doubled-ring source, all 64 allowed assignments are
represented once, with 17 distinct sets of active source knots.
At age one the growth roster and the incidence of fresh distinctions
are determined by that set. This follows from the whole-parent guard
and the fixed order for realizing a chosen roster. Each arm is weighted
by its number of physical assignments when forming a mean.

| Loaded distinctions | Assignments | \(e_2,e_5\) range | \(e_2,e_5\) mean |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 13 | 13 |
| 2 | 5 | 13–14 | 69/5 |
| 4 | 10 | 14–15 | 144/10 |
| 5 | 32 | 15 | 15 |
| 6 | 10 | 14–15 | 148/10 |
| 8 | 5 | 15 | 15 |
| 10 | 1 | 15 | 15 |

The age-one answer depends on which distinctions carry the load, even
at the same count. The seam pair \(e_3,e_4\) stays at 9 across all 64
assignments on the doubled source.

## Exact calculations and checks

Each wired distinction receives one unit of cut cost. The auxiliary
exterior supplies a second endpoint for a distinction with only one
holder. The symmetric difference of the supports on one side of a cut
gives exactly its crossing distinctions. Every forced parity on the
allowed linear relation is a sum of those supports. A nonempty support
is minimal precisely when both sides of its cut are connected. A
disconnected side would give a proper nonempty subcut. If both sides
are connected, any cut using only the same crossing distinctions must
keep each entire side together. The reported bond distance is the
minimum cut cost for the two marks, minus one.

For the source and the first layer, the producer enumerates each
connected subset of original knots using their original meetings and
the possible connections through binary children. The inside is the
side excluding the auxiliary exterior. For any such subset, start with
all children outside. The cut then consists of the crossing original
meetings and one distinction for each original loose incidence at an
inside original knot. The implementation verifies from the literal
stage that every original knot has a loose distinction at source and
every new knot has at most two different original parents and at least
one fresh distinction. Every original loose distinction supplies a
child in that layer.

An inside child with at most one inside parent can be put outside
without increasing the cut cost or harming connectivity. For a child
with two inside parents, putting it inside changes the cost by its
fresh count minus two. Take all nonpositive such choices, then join
the remaining components with the cheapest available positive choices
using the minimum spanning tree algorithm on those components. The
outside remains connected by way of the fresh distinctions because
every outside original knot has a child outside. This computes the
minimum for the fixed original subset. The Python checker rebuilds
each reported minimum from the literal holdings, checks both connected
sides, and verifies the crossing list independently by symmetric
difference of supports. The solver also agrees with direct enumeration
of allowed assignments and then minimal nonfree projections on two
small controls with different fresh counts.

For later ages, branch over the side assignments that separate both
marked pairs of holders. An ordinary cut with those holders pinned
gives a certified integer lower bound via a feasible flow of equal
value. If a minimizing side is disconnected, each component must
contain one of its pins. A component missing a pin could switch sides
and reduce the strictly positive cost. A connected solution must
therefore take some unpinned boundary knot onto the same side as that
component, to connect its pin to a pin in another component. Branch
on the first boundary choice in an arbitrary fixed order, pinning
each preceding choice to the opposite side. This partitions all feasible
connected completions and the matching flow check proves each
subproblem lower bound. A connected cut gives an upper witness. At
the per-pair cap the least remaining subproblem bound remains a lower
bound, and overlapping intervals do not establish equality. The
later solver additionally agrees with direct projection enumeration
on all 28 pairs in a separate small control.

The age-two solver uses the predecessor's connected-cut separator
recurrence. Its states retain the side colors and connectivity on a
separator, together with any component that has lost contact with that
separator. When a marked distinction is read, its endpoints must have
opposite colors. Once checked, the requirement can be erased from the
state. Subproblems that enforce the same local set of marks can be
reused across queries. The age-two tested widths are 10 quiet and 5
loaded. The ceiling for each frame is the maximum size of an earlier
verified bond that lifts to that frame, so imposing it cannot remove a
minimum for any included pair.

The receipt contains literal knot and distinction IDs for both age-one
and later witnesses. To replay, run the following from the repository
root.

```sh
.venv/bin/python -B experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_distances.py
.venv/bin/python -B experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_age_two.py
.venv/bin/python -B experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_age_two.py --later-endpoints
.venv/bin/python -B experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_later.py --full-age-two --max-age 2 --flows-per-pair 180 --out artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_age_two_flow.json
.venv/bin/python -B experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_later.py --cases J1 B J0 J2 C1 T4 T8
.venv/bin/python -B experiments/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_interaction.py --cases T4 T8
```

[Source and age-one exact receipt](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_first.json) ·
[All 210 one-spare age-two pairs](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_age_two_partitions.json) ·
[Longest one-spare pair at later ages](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_later_endpoints.json) ·
[Independent age-two interval audit](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_age_two_flow.json) ·
[Named pairs at ages two through four](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_later.json) ·
[Later four-arm bond interactions](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_interaction.json)
