# Growth evidence behind the single-cut study

## Archived ordinary growth

The sampled roster matches all eight shards in their recorded order. The sample selects 1,000 of 7,075 archived starts without replacement, using seed 20261128 after excluding the ten archived pilot starts selected with seed 1. The three starts in the other saved pilot are also absent from the sample. We reused the earlier independent ordinary not-all-equal growth rule. Its original check matched the literal supports and birth records of 33 first rounds. Here it matches the round roster, distinction count, knot count and search scope of all 2,416 archived rows. The archived rows do not carry the full supports. [Sample and totals](growth_counts.json) · [Earlier literal comparison](../../NAE-LAYER-20261127-001/referee-R1/growth_notes.md#replay)

| Round | All stages | Full search | Capped search | At least 12 distinctions and 8 recorded bonds, full | At least 12 distinctions and 8 recorded bonds, capped |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 1,000 | 1,000 | 0 | 370 | 0 |
| 1 | 708 | 680 | 28 | 593 | 27 |
| 2 | 708 | 385 | 323 | 379 | 322 |
| All | 2,416 | 2,065 | 351 | 1,342 | 349 |

All archived box counts are zero. The capped search uses at most four connected holders. The published counts of 1,691 stages that pass both inventory requirements include 370 starts and 1,321 stages after a birth. These are necessary counts for a box built from the bonds each search returned. The largest full search has ten knots. All 179 stages with twelve or more knots are capped, and 178 of them pass both inventory counts. The largest capped stage has eighteen knots. In the sample, 35 starts were already closed and 257 open starts stalled before a birth. Every one of the other 708 starts grew in both rounds and remained open. [Frozen search](../../UPPER-GROWN-20261127-001/README.md) · [Population by round and search](growth_counts.json)

Independently, 462 stages have fewer than twelve distinctions, so six disjoint carriers of two or three places cannot fit. The 639 stages with exactly twelve distinctions require all six carriers to be pairs. Enumerating every eligible triple of pair agreements by the exact allowed states gives zero one-word clauses on those stages, hence zero boxes. The other 964 full-search rows and all 351 capped rows contribute archived counts. Their entire relations and the capped stages' unrestricted searches were not run here. [Independent finite enumeration](growth_relations.json)

## Closure and the rival growth laws

In a system with at most two holders per distinction, a closed set of knots contains both holders of every distinction it meets. Closure under meeting therefore makes it a union of connected components. A connected system can close only as a whole. In a funded ordinary not-all-equal round every old loose distinction is taken once and each birth supplies its own fresh distinctions. The loose count after the round is exactly the number of fresh distinctions. At least one birth is made and each has at least one fresh distinction, so the complete stage remains open. The same fresh distinctions let every earlier allowed state extend, independently at the births. This preserves a fixed relation on earlier distinctions. It still allows a relation whose carriers use a born distinction to need a birth. Ordinary parity uses a different implication test and can close, as the earlier closure study showed. [Not-all-equal growth argument](../../NAE-LAYER-20261127-001/referee-R1/growth_notes.md#why-fixed-earlier-readouts-are-preserved) · [Ordinary parity closures](../../FOUR-READINGS-20261120-001A/results.md#which-closed-structures-does-ordinary-growth-produce)

A129 and A130 keep the two-holder condition, the connected start, and the use of every old loose distinction in a funded round. A129 removes one from the ordinary grant down to the three-place minimum. A130 grants only that minimum. The whole stage closes exactly when every birth of a funded round receives zero fresh distinctions. Through round two each law closes 21 of the same 1,000 starts after a birth, with 17 closures in round one and four in round two. These are the same starts under both laws. The largest newly closed system has nine knots. Every closed system reached in this comparison has at least one knot of more than three places. This comparison reads the growth record's structure. [Fresh-count rules and bounded replay](growth_counts.json)

There is a separate test for whether either cut can reach one of the 49 reported box-positive twelve-knot systems at any positive round from a connected open two-holder start. Every knot in a final closing round has zero fresh distinctions and only takes its inputs from the preceding stage. No two final births share a distinction. Erase each nonempty set of knots with pairwise disjoint supports and keep the consumed distinctions loose at their surviving holders. A necessary predecessor is connected and its funded proposal must have the erased knots' parent sets. Matching those sets lets us rename the loose distinctions within each preceding holder to match the erased supports. In the 49 positive systems there are 8,722 candidate sets, 5,664 with a connected predecessor and 1,687 with a funded proposal. None has the required parent sets. The same check on 63 closed comparison systems with no recorded box gives 22 returning cuts under each law, including five cuts on four different twelve-knot systems. This exhausts the possible final rounds for the 49 named closed systems. Reachability beyond those systems is a separate question. [Counts and returning controls](growth_counts.json)

## Earlier open and closed witnesses

The constructed twelve-knot start has 7,570 allowed states, 37 lower words on its six disjoint agreement carriers and eight lower clauses. Its upper agreements take every word except `000`. Removing any one of the twelve source laws restores `000`.

The earlier three-knot ring with one loose distinction at each knot is still open after three ordinary rounds, with four loose distinctions. Its six lower carriers overlap only within the three upper pairs. Each of the eight lower triples misses exactly `111`, with every pair free. The actual joint image has 25 lower words and gives seven upper words, with only `000` missing. Removing either of the newest laws separately gives 12 states with `000`. An upper relation of this carrier form can occur on an open stage under ordinary growth and need a birth. A309's box requires all six lower carriers to be disjoint. The canonical knot test on the eight lower laws with six witnesses forgotten gives the same seven upper words. [Independent enumeration and deletion counts](growth_relations.json) · [Canonical test](growth_upper_check.json) · [Earlier explanation](../../RING-BOND-20261127-001/referee-R1/layer_notes.md#a-grown-ring-example-when-first-readings-can-overlap)

The current review also verifies a strict box after two births in a single ordinary round from a connected open start of ten knots. Both loose distinctions are in its disjoint carriers, and deleting either birth restores the excluded upper word. The staged comparison reports zero boxes on the start or on either single-birth control and 18 on the funded stage. The archived sample starts from three to five knots. [Literal witness](witness_states.json) · [Stage comparison](reading_identity.json)

## Wording to fix

- **Narrowing.** Replace “They occur on none of the 2,416 grown stages read” in the [single-cut study's background](../README.md) with “No disjoint-carrier box was reported on 2,416 ordinary not-all-equal stages, including 1,000 starts and 1,416 stages after a birth. Searches were full on 2,065 stages and capped at four connected holders on 351.” The broader wording in the [goals checkpoint for the grown-stage search](../../../docs/RESEARCH_GOALS.md) and the [box-form register history](../../../docs/ASSUMPTIONS.md#a309--a-box-form-for-the-step-one-layer-up-and-closed-systems-counted-once) needs the same scope.
- **Narrowing.** Replace “A connected grown stage under ordinary growth always has loose distinctions” in the [single-cut decision](../decision.md) with “After a funded ordinary not-all-equal round from a connected two-holder start, the stage has loose distinctions and no nonempty closed set of knots.” Replace “which can close a part” in its entry on rival laws with “which can close the whole connected system if every birth of the round receives zero fresh distinctions.”
- **Block.** Replace “Needs a closed part of at least twelve knots inside a grown stage” in the [grown-stage decision](../../UPPER-GROWN-20261127-001/decision.md#position-and-next-directions) with “One ordinary not-all-equal round on a constructed ten-knot start leaves two loose distinctions and realizes the disjoint-carrier form. Its upper restriction needs both births. The earlier negative count applies to the archived sample and its search limits.”

## How to rerun

These commands run from the repository root with one computation at a time. The structural checks first processed 24 sampled starts and two closed systems of each comparison class in 0.08 seconds, followed by the full check in 1.02 seconds. The finite relation checks first processed 20 twelve-distinction stages plus the two known witnesses in 0.16 seconds, followed by the complete 639-stage check and witnesses in 1.55 seconds. Peak memory was under 32 MiB.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
.venv/bin/python -B research/CUT-BOXES-20261127-001/referee-R1/growth_audit.py --limit 24 --reverse-limit 2
.venv/bin/python -B research/CUT-BOXES-20261127-001/referee-R1/growth_audit.py
.venv/bin/python -B research/CUT-BOXES-20261127-001/referee-R1/growth_relations.py --limit 20
.venv/bin/python -B research/CUT-BOXES-20261127-001/referee-R1/growth_relations.py
```

For the canonical check, read the eight lower clauses and the three upper definitions from the earlier witness. The version without witnesses and the full command both took 0.03 seconds.

```sh
export PYTHONPATH=tools
.venv/bin/python -B -m knotlab check --cnf 'P Q R' --loops Q R --contact P --json
.venv/bin/python -B -m knotlab check \
  --cnf '~A0 ~B0 ~C0; ~A0 ~B0 ~C1; ~A0 ~B1 ~C0; ~A0 ~B1 ~C1; ~A1 ~B0 ~C0; ~A1 ~B0 ~C1; ~A1 ~B1 ~C0; ~A1 ~B1 ~C1; A0 A1 P; A0 ~A1 ~P; ~A0 A1 ~P; ~A0 ~A1 P; B0 B1 Q; B0 ~B1 ~Q; ~B0 B1 ~Q; ~B0 ~B1 Q; C0 C1 R; C0 ~C1 ~R; ~C0 C1 ~R; ~C0 ~C1 R' \
  --loops Q R --contact P --witnesses A0 A1 B0 B1 C0 C1 --json
```
