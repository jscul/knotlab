# One layer up, made by growth? What stands


> **Referee R1: refuted, one Block** ([report](referee-R1/report.md)). Every frozen count reproduces: 1, 2, 5, 19 and 85
> classes; boxes on 49 of the 85 twelve-knot classes and on none smaller (801 boxes, each with every law needed); none on
> the 2,416 sampled stages, also under an unrestricted search of the 351 large ones. **Block:** closure is not needed, and
> ordinary growth makes the step. A connected ten-knot start grows two ordinary births in one round. The grown stage then
> has 18 boxes on six disjoint three-place carriers, and every one of its twelve laws is needed, both births included.
> Replayed by the thread with the study's own engine (`post/grown_replay.py`: the same stage, 14,554 states, seven
> upper words, every law needed). The argument "boxes need closedness" holds only for a loose distinction that no carrier
> reads; here the carriers read both births' fresh distinctions. A different upper reading (four clauses: both A
> agreements, either B, either C) gives a step on a closed ten-knot system, and on a sampled stage (census start 420,
> round 2) with all six birth laws needed. **Narrowings:** the class weighting (labelled systems give 368 of 661); the
> opportunity count (1,693 by full-stage bonds); B4 checked on all 801; the product form guarantees at least one upper
> exclusion, not exactly one; "modulo two" in the definition. The start was built, not sampled, and selection of readings
> by growth is open: both symmetries of the start exchange the 18 boxes in pairs.

`UPPER-GROWN-20261127-001`. Frozen in commit b35af0be04. Results are in `out/`; the post-hoc replay is in `post/`.
Referee pending.

A **box** is six agreements on disjoint carriers whose eight triples are clauses of one product pattern. Its three
agreements of agreements then miss one word (`README.md`, "Definitions"). This is the step one layer up that
`RING-BOND-20261127-001`'s referee found.

## Answers in parts

**Where boxes live: closed systems of twelve knots, often.** A connected system of three-place knots that holds every
distinction twice is a connected cubic graph: knots are its points, distinctions its links. Every such graph with 4 to
12 points was read (1, 2, 5, 19 and 85, the known counts), each once.

| Points (knots) | Graphs | Graphs with a box | Boxes |
| --- | --- | --- | --- |
| 4, 6, 8 | 1, 2, 5 | 0 | 0 |
| 10 | 19 | 0 | 0 |
| 12 | 85 | **49** | 801 |

- B1, B2 and B3 held. 49 of the 85 twelve-knot systems carry a box, counting each isomorphism class once; the
  witness's carries 90.
- B4 held: every box read (681 of the 801; at most 50 were read per graph) has an upper image missing exactly one
  word.
- Beyond the prediction, all 12 knots are needed for each of those 681 upper words.
- A replay by full enumeration, with no solver (`post/replay_box.py`), agrees on one box of each of the 49 graphs: one
  word missing, all twelve knots needed.

So the step one layer up is not one chosen example. [R1: the frozen box occurs on 49 of the 85 simple connected closed twelve-knot classes and none of the 27 smaller classes, weighting each class equally; a different upper reading already works at ten.]

**Made by growth: not found** [R1, Block: found by the referee on a built ten-knot start after one ordinary round, both births needed].
- G1 and G2 held. 1,000 held-out census starts were read at rounds 0 to 2: 2,416 stages in all, 2,065 by the full
  search and 351 by the local search (holders ≤ 4). They have no box, so no box needs a birth.
- There were 1,691 stages with at least 12 distinctions and at least 8 bonds, where a box could have appeared.
- The grown ring has none through round 4 (explored).

The reason is partly proved. Growth never changes what the distinctions present before a round allow, so a box that
needs a birth must read born distinctions. In the boxes found, every knot is needed and every distinction is held twice
within them. A grown stage keeps loose distinctions, and its born part has no closed twelve-knot part in the rounds read.

## On the owner's rungs

- **Repetition:** met (`RING-BOND-20261127-001`).
- **The tower's next step:** reached on 49 of the 85 closed twelve-knot systems (computed, replayed): a relation that
  passes the knot test, made of relations that pass it, with every knot needed. Growth has not been seen to make one.
- **The tower's every step and recursion:** not shown.

## Intuition (a link, not evidence)

**Boxes need closedness** [R1, Block: false; the argument covers only loose distinctions no carrier reads]. A knot with a distinction of its own that no carrier reads can satisfy its law there, so its
law is never needed. That is the same argument that makes growth keep the earlier projection. In a box with every knot
needed, every private distinction must be read. Closed systems have none, so all their knots can be needed. Cheapest
test: on open systems built by removing one link from the 49 graphs, count the boxes that survive.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: one layer up, made by growth | **Status:** STOP (B1–B4, G1 and G2 held) | Common in closed twelve-knot systems (49 of 85), absent below twelve, and absent from 2,416 grown stages read |
| Local direction: a second layer made by growth | Open | [R1, Block: ordinary growth makes 18 boxes in one round on a built ten-knot start, every law needed; the 1,000 sampled starts make none through round 2.] ~~Needs a closed part of at least twelve knots inside a grown stage~~ |
| Long-term goal: G17 with G18 | Advanced | The step one layer up is generic in closed systems at twelve knots, not one built example |

**Next step:** Continue with direction 1 (the coordinator's call; the law between parity and not-all-equal waits for the
owner).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Closed parts inside grown stages: grow sampled starts more rounds, find closed connected parts of twelve or more knots, and test them for boxes | 3/3 | 2/3 | Count closed parts by round on 200 starts to round 6 → a box needing a birth, or no closed part | Proposed |
| 2 | A third layer: boxes of boxes on larger closed systems (14 to 18 knots, sampled) | 3/3 | 1/3 | Search upper clauses for a product pattern among upper readings on the 49 graphs' doubles → one, or a size bound | Proposed |
| 3 | Which twelve-knot systems carry boxes (49 of 85): a structural rule | 2/3 | 3/3 | Compare girth, connectivity and matchings of the 49 against the 36 → a rule, or none | Proposed |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** one scaffold entry added (the box form; each isomorphism class once).
**Scaffolds:**
- The box form and carrier rules, inherited from A308 and not swapped here.
- The holder cap on the 351 large stages.
- Counting each closed system once, a complete count, so no sampling weighting enters.

The closed-system result is about the model under the box form. The growth result is about stages through round 2.
**Advisor:** not consulted (usage limit at the freeze); the referee stands in alone.
