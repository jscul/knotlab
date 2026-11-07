# Reading through plane glue

Epic `GLUE-READ-20261106-001` (program topology), 2026-11-06.

## The question

- **The approval.** The owner said "Yes, please continue." to CHAIN-TRANSFER's recommendation: read the atoms, and so the genus, through
  plane glue.
- **What to explain.** The glue line that joins an atom's twin class, and the atoms that split into twin pairs.
- **What to look for.** One rule that reads the atoms of every three-fold space.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Creation at an atom is decided by its cut.** For a closed Fano atom, whether a removal beyond one of its cuts creates at a line of it depends only on the relation the removal's side shows on that cut. An emitter's lines receive exactly when the ports may be equal. A receiver's cut line receives exactly when the other two ports are not forced equal; its intact line receives exactly when the side tells the ports apart. | proved: exhaustive over every port relation and every deeper relation (8,190 cases) | A |
| 2 | In real spaces the removal's side acts only through that relation. | computed: 47,550 of 47,550 pairs on the census | A |
| 3 | **Through atoms the cut is always free, and the touching rule holds.** Through glue the side can exclude a pattern pair or tie two ports. Where it stays free, the touching rule still holds (88,764 pairs). Every failure is at a constrained side (7,319 of 11,100). | computed: 191 spaces | B |
| 4 | **The two disturbances are local.** A joined glue line is a doubled-square line meeting two or more of the atom's ports (218 of 218). A split atom emits into a planar brace and splits by the points of its emitted line, differing only on glue lines (64 of 64). Planar lines see which point a removal passed through; atom lines do not. | computed: 191 spaces | B |
| 5 | **The two-stage twin rule reads the census.** Twins pick out the atom lines, then twins on atom lines give the atoms. It reads every Fano tree with at most four cuts per atom (proved), all 111 census spaces, and 57 of 80 random spaces. | proved (Fano trees) and computed | C |
| 6 | **The yes/no relation cannot read every space.** In 15 random spaces, two lines of different atoms are twins of the yes/no creation relation, so no rule that reads only whether creation occurs can return the atoms. In every one, the atoms meet one planar brace. | computed instances, with a one-line argument | C |
| 7 | **The far sides carry the missing distinction.** Which far side creates separates every two lines of different atoms in all 191 spaces. It varies inside atoms too, so plain twins on it fail. | computed | C |

## Answer

- **What decides creation at an atom is now known exactly.** It is the relation its cut sees from the removal's side.
  - Through atoms that relation is always free, which is the touching rule.
  - Glue can constrain it, and then the law's table applies.
- **The atoms can be read through glue in the census.** The two-stage rule reads every three-fold space of up to 26 points there.
- **Native reading of the yes/no kind stops at shared plane pieces.**
  - **Where.** When several atoms meet one planar brace, their lines can be indistinguishable to whether creation occurs.
  - **What is left.** The distinction survives only in which far side creates.

## Reading

- **A cut is an atom's whole window.**
  - The atom sees the rest of the space only through the patterns its cut allows, three ports' worth.
  - Free and not-all-equal sides look alike to a receiver.
  - An emitter needs its ports allowed equal.
- **Atoms are blind to depth; plane glue is not.**
  - Lines of a Fano atom respond only to what their cut allows.
  - Lines of a plane piece respond to where in the piece a removal entered.
  - That is why atoms split only in what they do to glue.
- **Several handles on one plane can look alike.**
  - The plane hides which handle a removal came from: whether creation occurs is the same.
  - Only how creation occurs keeps them apart: which far side completes it.
- **Doctrine.**
  - **No space is assumed.** Cuts, ports and far sides are relations among lines.
  - **The far sides.** Throughout, creation is the creation map's, against its four census far sides.

## Literature

- **Ours.**
  - The two-round rule (PENDANT-LINE A).
  - The chain profiles and free ports (CHAIN-TRANSFER A).
  - The twin rule (CHAIN-TRANSFER C).
  - The census (BRACE-TREE C).
  - Halos and claims on plane pieces (PHASE-HALO, FACE-CLAIM, STRIP-RELAY), which ticket B's split recalls.
- **Classical.**
  - Finite verification by bounding an OR over local configurations.
  - Invariance of rules under automorphisms.
- **New here.**
  - The receiving-cut law and its native table.
  - The record of what glue presents.
  - The two-stage rule.
  - The obstruction for the yes/no relation.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
  - Whether to publish today's epics to knotlab and jscul.dev.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — reading through plane glue | **Status:** Partially successful | **Proved.** The receiving-cut law. **Computed.** What glue presents, and the two disturbances. **Reads.** The two-stage rule reads the census and Fano trees. **Obstruction.** No rule using only whether creation occurs reads every space: 15 random spaces are obstructed. |
| Local direction — reading with the yes/no relation | Exhausted | **Obstructed** where several atoms meet one planar brace. Further rules of this kind cannot fix those spaces. |
| Broader exploration — reading every three-fold space | Open | **The information is there.** Which far side creates separates every cross-atom pair in all 191 spaces. **Untouched.** Non-Fano handles (census 58) are still not read. |
| Long-term goal — topology from native emergence | Capability gained, limit found | **Gained.** Native creation at an atom is fixed by one three-port relation, and the census genus is read natively. **Found.** The limit of the yes/no relation is now precise: plane glue can make handles look alike, and only the far sides keep them apart. |
| Next recommendation — reading with the far sides | **Next step:** Continue. Use the 191 exact maps, which keep which far side creates, to look for a rule that separates atoms meeting one planar brace without splitting atoms. Start from the two-stage classes, and test whether census 6's pattern, taken over a whole class, separates merged atoms. | **If yes.** One native rule would read the genus of every space computed. **If no.** Reading needs more than creation's pattern, which is a sharper limit. **Alternatives.** Derive the relation a planar brace presents from its faces (1/3); read non-Fano handles through the receiving-cut law with census 58 atoms (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The separation exists in every space, and the maps are already computed, so the test is cheap. **Main uncertainty.** Census 6 varies inside atoms, so a rule must find what stays constant inside an atom. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The 191 saved maps, then fresh larger spaces. **Stop when** a far-side rule reads every saved space and holds on fresh ones, or the far sides are shown not to determine the atoms. |
