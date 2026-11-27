# Agreements bind again on the registered cuts

All 49 open systems carry three agreements of agreements that pass the knot test. The two lower carriers compared in each upper agreement share exactly one raw distinction. Across the three upper agreements the raw supports are pairwise disjoint. The frozen box requires all six lower carriers to be disjoint. This within-pair overlap was already used in the earlier referee's grown-ring example. [Earlier comparison](../../RING-BOND-20261127-001/referee-R1/layer_notes.md) · [All 49 certificates](other_registered.json)

| Check | Result for the first qualifying choice on each cut |
| --- | --- |
| Eight lower bonds per choice | All 392 forbid exactly 111 and retain all seven other words. Their three carriers are disjoint within each bond. No one source knot determines a reading, and every member of every carrier can flip its reading by changing alone. |
| Exact presentation by lower bonds | In all 49 cases the eight clauses allow 37 of 64 six-reading words, exactly the 37 realized by the source. Each upper agreement remains free under some fix of every single lower bond. |
| Three upper agreements | All 49 forbid exactly 000. Their three pair projections each contain all four words. The canonical check passes in all three contact roles on this relation and on the lower clause. |
| Erasing a constraint | On the six lower readings, each of the eight single deletions restores 000. On the raw source, exactly six laws are individually necessary and jointly sufficient for the exclusion. Removing all source laws allows 27,648 assignments with upper word 000 on each cut. |
| Which loose distinctions matter | Of these 49 choices, 10 read both loose distinctions and need both cut knots, 33 read one and need one, and six read neither and need neither. |

The same comparison survived the split on 39 of the 49 systems. Identifying the two loose distinctions again preserves all lower and upper eligibility checks for those 39 choices. The other ten use the two newly distinct places in different upper carriers. Identifying them makes some lower carriers overlap within a proposed bond and changes its forbidden words. All 49 still have seven upper words before the split. At the level of the six lower readings the closed systems realize 37 words on 37 choices, 36 on two and 33 on ten. [Source, identification and knot-test controls](other_controls.json)

## Why it works

In every certificate the six necessary source knots form three separate pairs under sharing of raw distinctions. Call each pair's shared distinction its common value. Each lower reading compares two remaining places of a knot in that pair with the common value taken from the preceding pair, in a cyclic ordering of the three pairs. If a lower reading agrees, its knot sees two copies of the preceding common value. The not-all-equal law forces the current common value to differ from that preceding one. Choosing one true reading from each pair would therefore make three Boolean values differ consecutively and return to the first. This excludes 111 in each of the eight lower bonds. If all three upper comparisons disagree, each has a true member, which explains the exclusion of 000.

The 392 lower bonds each have a unique minimal set of three source laws. These three knots hold exactly the raw members of the three carriers and share no raw distinction with each other. The six sufficient upper laws can recover the entire 37-word relation on their own. Thus the choices of agreement carriers relate three otherwise separate source pairs in this construction. This witnesses upper binding under the whole-stage definition and gives no witness under a requirement for connected, essential lower holders. The full source has twelve knots. [Sufficiency and all single-deletion checks](other_controls.json)

For example, the first registered system was opened at the distinction shared by knots 0 and 1. In lexicographic order of the original pairs of holders, distinction 0 stays with knot 0 and its new copy 18 goes to knot 1. Compare the agreements on (0,1,3) and (3,5,7), on (2,8,10) and (2,14,16), and on (9,13,15) and (4,9,18). The three pairs of necessary source knots are (0,3), (4,9) and (1,10). Both cut knots belong to this set. [Example and all eight lower images](other_first.json)

## Replay

From the repository root, the following commands recover the 49 source systems from the original holder lists and the recorded cut endpoints. The search takes the first sufficient three-law construction with the stated carrier overlap for each cut. Each source truth table covers all 524,288 Boolean assignments.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
dir=research/CUT-BOXES-20261127-001/referee-R1
.venv/bin/python -B "$dir/other_upper.py" --source-triples 35 --compared-pairs 500
.venv/bin/python -B "$dir/other_upper.py" --count 1 --out "$dir/other_first.json"
.venv/bin/python -B "$dir/other_upper.py" --count 49 --out "$dir/other_registered.json"
.venv/bin/python -B "$dir/other_checks.py" --limit 1
.venv/bin/python -B "$dir/other_checks.py" --out "$dir/other_controls.json"
```

The first source prefix took 0.02 seconds. One full system took 0.15 seconds, and the 49 systems took 6.31 seconds with a peak of 33,544 KiB. The before-and-after pilot took 0.07 seconds and the full checks took about 1.1 seconds. A count of every admissible overlapping choice and a search over other upper reading functions were not run.
