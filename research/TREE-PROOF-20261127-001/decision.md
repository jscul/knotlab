# A proof of the pair cost, and with it the families' tree: what stands

Epic `TREE-PROOF-20261127-001`, closed 27 November 2026. A proof by the thread. **Refereed (R1): the theorem confirmed
with proof fixes; one Block** ([report](referee-R1/report.md)): the tree is not read off allowed-state distances alone;
the family parity map, from the holdings, is needed. [The proof](tree_proof.md)

## What stands

1. **The pair cost (proved, from the engine's definitions).** c_t(A, B) is the shortest chain of families from A to B
   with steps d + 2t + 2; usually d + 2t + 2, and shorter only through other families while 2t + 2 is small.
2. **Its consequences (proved).** Set costs (the cheapest crossing step), the class facts at a scale (cluster facts),
   and the tree (single linkage by d), fixed by the start; scale and round pick the level.
3. **Distance (reading).** [Corrected, Block: given the family parity map, the least distances determine the tree at
   every resolution; the allowed states alone do not, so A97 is not shown here.] No scale is needed for the tree.
4. **Computed.** 6,839 of 6,839 recorded pair costs equal the shortest chain.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the pair cost proved | **Status:** STOP (proved, referee pending) | Upper bound by rising routes, lower bound by pairing routes and no shortcut through births |
| Local direction — what growth selects | Closed for ordinary growth, given the referee | The selection is the families' tree, fixed by the start's distances |
| Long-term goal — G17 with G18 | Narrowed | The pair-cost theorem identifies a hierarchy on the named family facts; growth's selection of all next-layer places is open (R1) |

**Next step:** Research directions — the coordinator's call, after the selected-knots referee

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A referee for this proof, with the selected-knots one | 3/3 — the stop becomes a refereed theorem | 3/3 | Launch → confirmed, or the step that fails | Proposed |
| 2 | The forbidding cuts on the tree: does a cut birth with no fresh distinction change a family's distance or join lineages, putting a loop in the second layer? | 2/3 | 2/3 | tree.py under both cuts → a loop, or none | Alternative |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G18).
**Assumptions:** none added; A97 is not established by this proof (the tree needs the family map, not distances alone).
**Basket:** the postulates line's other items belong to the hearing and meeting lines.
**Scaffolds:** the presentation supplies the family parity map; the scale selects a level of its tree (A303).
**Advisor:** not consulted for the proof; it follows the earlier direct-step conjecture, corrected after its three misses.
