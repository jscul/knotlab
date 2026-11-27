# Disjoint agreements on an open grown stage

An ordinary first-round birth is essential to an upper knot on disjoint carriers when a lower agreement may use four distinctions. With two four-place carriers, the eight lower clauses give exactly the six-reading relation on the grown stage. With one four-place carrier, the same eight clauses give exactly the upper relation. Both examples use three-place not-all-equal source knots throughout.

## Two four-place carriers give the full lower relation

Remove `(0,1,6)` from the earlier [twelve-knot example](../../RING-BOND-20261127-001/referee-R1/layer_notes.md). The three loose distinctions are 1, 6 and 0. Their holders have no pair eligible for a common birth. The ordinary first round therefore adds `(1,18,19)`, `(6,20,21)` and `(0,22,23)`. Read six disjoint agreements.

| A0 | A1 | B0 | B1 | C0 | C1 |
| --- | --- | --- | --- | --- | --- |
| 0,1,2,18 | 3,4,5 | 6,7,8,19 | 9,10,11 | 12,13,14 | 15,16,17 |

Choose one agreement from each of A, B and C. If all three hold, three source laws require the A and B values to differ, the B and C values to differ and the C and A values to differ. In the cases involving A0 and B0, the first of these requirements now comes from the birth `(1,18,19)`. The eight choices therefore give the same eight one-word exclusions as in the earlier closed example.

Conversely, take any allowed state of the earlier closed example. Give 18 its old value at 0 and 19 its old value at 6. Give each of the two other births a disagreeing pair of fresh values. This extends the state to the grown system, preserves all six agreements and recovers all 37 six-reading words allowed by the eight clauses. The three upper agreements `A0=A1`, `B0=B1`, `C0=C1` realize exactly `001, 010, 011, 100, 101, 110, 111`.

The lower-clause and source-law deletions answer different questions. On the six readings as free bits, deleting any one of the eight clauses admits a word with exactly its three readings true and all other readings false. This gives upper `000`. On the full grown stage, deleting the first birth restores 360 source states with upper `000`. Deleting either other birth restores zero. Deleting each of the eleven old laws restores the word. These figures count raw states, with both values of each distinction included. The stages are connected and have loose distinctions. A closed subset in a two-holder system would have no shared distinction leading out of it, so these stages contain no nonempty closed subset of knots. [All assignments, source-law deletions and canonical checks](alternative_exact.json)

## One four-place carrier suffices

After removing `(0,1,6)`, identify old distinctions 0 and 1 by giving their remaining occurrences the shared identity 0. Only distinction 6 is then loose. Its holder is the sole parent of the ordinary birth `(6,18,19)`. Use `A0=[0=2=18=19]` and keep the other five original three-place readings. Here the upper relation still follows from the eight lower clauses alone. The source also excludes `111` on `B1,C0,C1`, so 35 of the clauses’ 37 lower words occur. The source and the eight chosen clauses give the same seven upper words. The extra triple matters if unreadability is required against every lower bond that can be read on the six distinctions. The two-four-place example has exactly the original eight lower bonds on those readings. [Single-birth data](alternative_growth.json)

| Check | One four-place carrier | Two four-place carriers |
| --- | ---: | ---: |
| Source knots after the round | 12 | 14 |
| Distinctions | 19 | 24 |
| Allowed states / all assignments | 15,930 / 524,288 | 284,310 / 16,777,216 |
| Actual lower words / words allowed by eight clauses | 35 / 37 | 37 / 37 |
| Source laws whose separate deletion restores `000` | 12 / 12 | 12 / 14 |
| Restored states on deleting the selected birth | 40 | 360 |
| Fewest source-knot fixes leaving both values of a lower reading possible | 2 | 2 |
| Fewest fixes of a chosen lower knot leaving both values of an upper reading possible on the source | 5 | 6 |
| Single-carrier shortenings to two or three members giving all eight upper words | 10 / 10 | 20 / 20 |

Every raw carrier member in both examples changes its reading on a single permitted flip somewhere. The three upper roles all pass the canonical check with the six lower readings quantified away. All 32 interchanges of the incoming occurrences of the other five carriers in the one-four-place construction still give 35 lower words. [Interchanges](alternative_variants.json)

As a separate strict-cap control, split its four-place carrier into two disjoint pairs. Keep or shorten each of the other five carriers to two or three members, requiring each reading to remain unread at every source knot. There are 64 choices of seven lower readings. The complete search on them tested 13,440 triples of disjoint upper agreements and 20,160 further triples with a signed three-place agreement. Each upper reading used two or three lower readings. All 33,600 upper images were full. Sixteen of the 64 choices even kept their entire seven-reading image on deleting the birth. The unsplit positive control recovered eight essential lower clauses. This finite control covers these carrier choices on this start. [Split-carrier check](alternative_split.json)

**Scope of the proposed correction.** In the decision's position table, replace “Needs a closed part of at least twelve knots inside a grown stage” with “Test the frozen two- and three-place carriers on open grown stages. Allowing a fourth member gives a birth-essential upper knot on a connected stage with loose distinctions.” Both starts and all six readings were chosen. The growth law deterministically supplies the reported births. The 1,000-start frequency and the frozen two- or three-member search are separate questions.

## Eight lower clauses can bind without product signs

Consider six lower readings in three pairs. If an upper pair agreement must remain unread at each single lower knot, an eligible lower knot contains at most one member of each pair. With exactly these six readings available, every eligible ternary lower clause therefore uses one A, one B and one C. Fix an upper word. The eight lower words below it correspond to the two possible orientations of each pair. Selecting one member of each pair gives every orientation exactly once. Each single-clause lower knot can thus exclude exactly one of the eight words below the chosen upper word. At most eight different triples are available. To exclude the upper word, all eight are needed, and their eight forbidden orientations must be distinct. This proves necessity of coverage, with no requirement that a reading have the same sign in every clause. The argument assumes six readings, three pair comparisons, one forbidden word per eligible first triple and no additional lower distinctions.

For a concrete alternative on six lower bits, index the eight triples `(Ai,Bj,Ck)` by `ijk` in order `000` through `111`. Forbid `000, 110, 101, 011, 111, 001, 010, 100`, respectively. Exactly 22 six-bit words occur. Every specified triple has just its stated exclusion and all other triples are full. The three upper agreements have image `000, 011, 100, 101, 110`. All three pairs of upper readings take all four values. Each of the eight lower exclusions is needed for the missing upper word `111`, and every upper reading remains unread at each lower knot. No fixed forbidden value at `A0` fits both of its first two clauses. These are relations of the six lower bits. Realizing these signed clauses as agreements of disjoint carriers in an ordinary not-all-equal source remains open for this example. [Explicit deletion witnesses, clauses and canonical checks](alternative_cover.json)

Fix `111` as the upper word to exclude. With the lower pairs then agreeing, the eight forbidden triples have to permute the eight orientations. Of all 40,320 labelled permutations, 1,960 give precisely the specified one-word exclusions on their eight lower triples. Of those, 1,216 have full upper pair projections. Eight use fixed signs and 1,208 use nonproduct signs. All 1,208 pass unreadability at their eight lower triples. Respectively 992, 192 and 24 miss one, two and three upper words. In 48 of them every other triple on the six readings is full. The counts weight labelled permutations once each. They measure the abstract search space of signs, with no weighting of source stages.

## Reproduction

Run these commands from the repository root. Each command uses one process. Each prefix uses the same configuration as its complete calculation. The direct reading of the allowed states and all upper- and lower-clause tests were written for this review. The growth implementation comes from the [earlier independent ordinary-growth rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py). The check compares every birth's parents, input, demand and fresh distinctions with the single-parent construction above. It also compares the bit-column state count against a literal evaluation of every assignment in each stated prefix.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
work=research/UPPER-GROWN-20261127-001/referee-R1
.venv/bin/python -B "$work/alternative_growth.py" --prefix 8192
.venv/bin/python -B "$work/alternative_growth.py" > "$work/alternative_growth.json"
.venv/bin/python -B "$work/alternative_growth.py" --exact --prefix 32768
.venv/bin/python -B "$work/alternative_growth.py" --exact > "$work/alternative_exact.json"
.venv/bin/python -B "$work/alternative_variants.py" --limit 1
.venv/bin/python -B "$work/alternative_variants.py" > "$work/alternative_variants.json"
.venv/bin/python -B "$work/alternative_split.py" --limit 1
.venv/bin/python -B "$work/alternative_split.py" > "$work/alternative_split.json"
.venv/bin/python -B "$work/alternative_cover.py" --limit 120
.venv/bin/python -B "$work/alternative_cover.py" > "$work/alternative_cover.json"
```

The two source prefixes took 0.11 and 0.13 seconds. Their full checks took 0.07 and 2.53 seconds, with peak memory below 251 MiB. The one-configuration interchange and split pilots took 0.04 and 0.15 seconds. The complete checks took 0.14 and 0.73 seconds. The 120-permutation pilot took 0.05 seconds and the full sign count took 0.17 seconds.
