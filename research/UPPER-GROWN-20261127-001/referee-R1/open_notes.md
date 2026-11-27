# A strict box made in one round

A connected start with ten three-place not-all-equal knots has no box on any of its 85,877 bonds. Its first ordinary round has 18 boxes on 201,425 bonds. For the six carriers below, deleting either birth restores the upper word 111. The grown system has two loose distinctions. Both are read.

In order, the starting supports are

```
(4,5,6)    (4,7,8)     (0,9,10)    (9,11,12)    (1,5,12)
(13,14,15) (7,10,11)   (3,14,16)   (2,13,16)    (6,8,15)
```

Number the starting knots from zero. The four loose distinctions are 0, 1, 2 and 3. Knots 2 and 4 have common old knot 3, and knots 7 and 8 have common old knot 5. These are the only qualifying parent pairs. The first birth takes 0 and 1 and makes 17. The second takes 2 and 3 and makes 18. Neither requires additional fresh distinctions. Thus the new laws are not-all-equal on (0,1,17) and (2,3,18).

| Agreement | Carrier |
| --- | --- |
| A0 | (0,9,17) |
| A1 | (2,3,16) |
| B0 | (1,5,18) |
| B1 | (7,10,13) |
| C0 | (4,6,8) |
| C1 | (11,12,14) |

Of all 524,288 assignments, 14,554 satisfy all twelve laws. Each of the eight ways to take one A, one B and one C has exactly the seven words other than 111. For each of the 72 pairs of a source knot and a reading, some fixing of the knot leaves both reading values. Each of the 18 carrier members has at least 766 allowed single changes that flip its reading.

Read P, Q and R as disagreement of each pair. The stage realizes 34 of the 37 six-reading words permitted by the eight exclusions. Both relations have the same seven upper words. Deleting the first birth separately restores 90 raw assignments with upper 111, and deleting the second restores 50. The other ten laws also individually restore it on deletion. Writing P, Q and R as agreements complements all three bits, so the missing word becomes 000. Each lower law separately restores an upper witness in the eight-law conjunction. The canonical checker passes all three contact roles for every lower triple, and all three upper roles on the actual six-reading image and on the eight-law conjunction. [Truth counts, minimal sufficient law sets and checker results](open_witness.json)

Each lower exclusion has a unique inclusion-minimal sufficient set of source laws. Their sizes in product order are 7, 3, 7, 3, 6, 3, 5 and 3. All eight sets omit at least one carrier member. Therefore the registered local search cannot find any of the eight lower bonds of this box, even if its four-knot cap is increased. This is a separate effect of the requirement that the chosen holders contain the carriers.

**Block on the claimed necessity of a closed part and the general growth interpretation.** In the [decision](../decision.md), replace “Needs a closed part of at least twelve knots inside a grown stage” and “Growth has not been seen to make one” with “One round from a connected ten-knot start makes eighteen boxes on a stage with two loose distinctions. Both births are individually essential to the displayed upper exclusion.” The 1,000-start sample used starts with three to five knots. This constructed start is outside it. “A knot with a distinction of its own that no carrier reads can satisfy its law there” holds. The stronger heading “Boxes need closedness” is false.

## Finding and replaying the example

On each of the 49 positive closed systems, split each of its 18 shared distinctions into two loose ones, preserving both original knots. The first search transported the one archived box per system to each choice of the retained copy and then exchanged at most one pair of the 19 identities. None of the 1,764 unmodified transports retained all eight lower exclusions. Among 266,364 additional exchanges with the archived missing values, one passed all eight full-stage bond tests. It came from the first row of `out/cubic_12_3.jsonl`, splitting distinction 0 at knot 1. Taking both holders of the loose distinctions out of this open system yielded the ten-knot starting supports above. [Targeted cut results](open_cuts.json)

The independent [closed-system deletion table](closed_boxes.jsonl) extends the failure of unmodified transport to all 801 closed boxes. Each of their twelve laws is essential to upper 111. After a split, the old readings leave one copy unused in its sole holder H. Take an assignment realizing 111 after deleting H from the closed source. Give the retained copy its old value, and choose the unused copy to satisfy H. Every reading keeps its value. This supplies an upper witness to all 28,836 transports (801 boxes, 18 choices of distinction and two choices of retained copy).

The exact twelve-knot split cannot arise within two rounds from a three- to five-knot census start. Every birth leaves at least one loose distinction and the round consumes every old loose distinction. A split has exactly two loose distinctions on different knots. Both knots must have been born in the last round, each taking two earlier distinctions. Its ten-knot predecessor has four loose distinctions. At most four of its knots could have been born in the preceding round, leaving at least six knots in a two-round start.

The unrestricted search covers all 18 splits of each of the 49 positive source systems, 882 choices in total. Relabelling each source reduces them to 371 inequivalent splits. Exactly one of the 882 choices has any boxes, and it has 18. All eighteen miss just upper 111, require all twelve laws and require both births separately. The other 881 choices have zero boxes. The exact predecessor has ten knots and no earlier ordinary predecessor. This count is under equal weighting of the 49 source classes and the 18 marked distinctions within each. [Complete split census](open_full.json) · [All upper deletions and reverse growth](open_reverse.json)

The follow-up that cut one seeded distinction per system selected 49 of these 882 choices. Its source positions, marked distinctions, pairs of holders, pre-cut boxes, cut bonds and cut boxes match on every row. Together those selected systems retain 7,634,271 lower bonds, ranging from 131,578 to 223,829, and zero boxes. On the exceptional system, the follow-up's sixth source (stored position 5), its seed selected distinction 16 held by knots 7 and 11. The positive split uses distinction 0 held by knots 0 and 1. Its finite sample result stands. Its statement that the layer is “out of ordinary growth's reach” fails on the two-birth construction. [Seeded cut matches](open_followup.json) · [Follow-up decision](../../CUT-BOXES-20261127-001/decision.md)

Splits of the 36 closed source classes without boxes, simultaneous splits, and a census of all ten-knot starts were not run here.

The cut search verifies the archived carrier numbering by recovering the literal order of its generated distinctions and replaying their eight semantic exclusions. It uses satisfiability queries on complete source laws and six ordinary agreement definitions. The direct witness check enumerates every Boolean assignment and all 4,096 subsets of the source laws. Its growth replay uses the earlier independent [ordinary rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py), previously compared with 33 archived first rounds and 199 births. The two parent pairs, their input identities and fresh demands also agree with the direct calculation above. The unrestricted carrier census on the chosen start and grown stage uses the independent [finite-state implementation](census_search.cpp) in this review. It recovers the displayed box among its eighteen. [Unrestricted carrier counts](open_full_pilot.json)

From the repository root, run the commands in order. The targeted pilot took 0.222 seconds for two splits, including its common initialization, giving an upper estimate of 98 seconds for all 882. The run took 33.2 seconds. The literal witness pilot with one deletion took 0.193 seconds and the complete check took 0.200 seconds. The unrestricted split pilot took 0.83 and 1.18 seconds per split class, giving an estimate of about 6.2 minutes for all 371 classes. The full search took 292.3 seconds. The separate upper-deletion pilot on the 18 boxes took 0.0035 seconds and the two-row seeded-match pilot took 0.0082 seconds.

```sh
ulimit -v 2000000
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
r=research/UPPER-GROWN-20261127-001/referee-R1
.venv/bin/python -B "$r/open_cuts.py" --graphs 1 --cuts 2 --one-swap --out "$r/open_cuts_pilot.json"
.venv/bin/python -B "$r/open_cuts.py" --one-swap --out "$r/open_cuts.json"
.venv/bin/python -B "$r/open_witness.py" --deletions 1 --out "$r/open_witness_pilot.json"
.venv/bin/python -B "$r/open_witness.py" --out "$r/open_witness.json"
.venv/bin/python -B "$r/open_full.py" --witness --orbits 2 --out "$r/open_full_pilot.json"
.venv/bin/python -B "$r/open_full.py" --witness --orbits 371 --out "$r/open_full.json"
.venv/bin/python -B "$r/open_reverse.py" --input "$r/open_full_pilot.json" --limit 1 --out "$r/open_reverse_pilot.json"
.venv/bin/python -B "$r/open_reverse.py" --input "$r/open_full.json" --out "$r/open_reverse.json"
.venv/bin/python -B "$r/open_followup.py" --limit 2 --out "$r/open_followup_pilot.json"
.venv/bin/python -B "$r/open_followup.py" --out "$r/open_followup.json"
```
