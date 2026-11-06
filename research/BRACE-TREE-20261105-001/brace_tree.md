# A native reading of the brace tree

Epic `BRACE-TREE-20261105-001` (program topology), 2026-11-05.

## The question

- **The approval.** The owner said "Yes, let's continue." to NATIVE-GENUS-20261104-001's recommendation.
- **What it asked.**
  - Test whether blocks of mutual creation, one-way creation and silence recover a three-fold space's tight-cut decomposition: its Fano
    atoms, the direction of each cut, and its doubled squares, including where atoms touch.
  - Try to prove the block lemma for Fano atoms.
- **A correction made before any test.** NATIVE-GENUS proposed the fewest blocks covering a piece. Its own data rule that out: two
  atoms hanging from one atom are covered by two blocks, for genus 3. So the epic first mapped how creation depends on the tree,
  then fixed a reconstruction from that map and tested it on fresh spaces.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Atoms are blocks.** The Fano plane's creation map is complete. A Fano atom attached at a line creates among its own lines exactly as the Fano plane does. | proved (screening lemma); exact checks | A |
| 2 | Atoms attached at a point form one block too. | computed, every design | A |
| 3 | **Cuts are read in their direction.** A receiver's cut lines and the emitter's lines are mutual; its intact lines create one way at the emitter's. | computed: 676 pairs; 50 + 163 cuts | A, B, C |
| 4 | **The dictionary.** Where only atoms join two atom lines, their relation is fixed by the tree. Rules: same atom mutual; downstream cut line mutual, intact line one-way; siblings mutual; co-receivers' intact lines silent. Through plane glue it can depend on more, so the prediction "every place" is refuted. | computed: 10,074 pairs (B), 32,016 fresh pairs (C), no exception | B, C |
| 5 | **Glue is silent** when no handle lies between: 306 + 1,354 pairs. Across a handle it can create: a non-Fano one (B), or a Fano atom (C, one class). B's stated glue rule is refuted. | computed | B, C |
| 6 | **The source rule counts the genus.** Kept blocks (those with a line blind to everything the others are blind to) equal the Heawood braces, and the genus, on every space without a non-Fano brace: 47 of 47 where found, then 110 of 110 fresh spaces. The plain block count: 42 and 83. | computed, fixed before the fresh test | B, C |
| 7 | **Non-Fano handles are not read.** Census 58 is itself a single brace of another kind; it and the trisum brace defeat the rules and the count. | computed | B, C |

## Answer

- **Do blocks, one-way creation and silence recover the decomposition?** For spaces built from Fano atoms and plane glue: yes, as far as
  tested.
  - **Atoms.** Blocks of mutual creation, after the source rule drops the spurious ones, are the Fano atoms. Their number is the genus,
    on every three-fold space of 23 to 26 points.
  - **Directions.** One-way creation gives the direction of every cut between two atoms.
  - **Glue.** Silence marks plane glue.
- **The block lemma.** Proved for atoms attached at a line, checked for atoms attached at a point.

## Reading

- **Native selection reads the handle tree, not just the handle count.** A process internal to the logic, removal and gluing, recovers
  how many handles a space has, where they are, and which way each pair of touching handles is glued, with no embedding. Touching atoms
  were exactly where NATIVE-GENUS's count failed; the source rule resolves them.
- **Why it works.**
  - Inside an atom, creation is complete.
  - Across a cut, it runs one way, from the receiver's intact lines toward the emitter.
  - Two atoms hanging from one atom see each other fully, but their footprints on that atom differ. A block that mixes them has no line
    whose blindness covers the others', and the rule drops it.
- **What it cannot see.** Handles that are not Fano atoms (census 58, the trisum brace) are invisible to the rule. Native selection reads
  Fano atoms, which in three-fold spaces are almost all the handles.
- **Doctrine.**
  - Blocks, directions and silence are relations among lines given by creation; no distance, orientation in space or metric is
    introduced.
  - Direction here is which side of a cut lost a point, not a direction in any space.

## Literature

- **Ours.** The splitting, interface and screening lemmas (NATIVE-GENUS A, HANDLE-LOCALITY A, B); the native count (NATIVE-GENUS B); the
  three-fold grammar and census (THREEFOLD-GRAMMAR A, B); genus = Fano atoms (THREEFOLD-SURFACES A, B).
- **Classical.** Tight-cut decompositions into bricks and braces (Lovász). Clique covers and maximal cliques are standard tools; the
  source rule is not.
- **New here.**
  - The native relations and the dictionary.
  - Native cut directions.
  - The source rule and its test on fresh spaces.
  - Creation relayed between glue pieces through a Fano atom.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — a native reading of the brace tree | **Status:** Successful | **Found.** Atoms are blocks (proved for atoms attached at a line), cut directions are native (213 cuts), the tree fixes creation between atoms joined by atoms (42,090 pairs, no exception), and the source rule counts the genus on 157 of 157 spaces without a non-Fano brace (110 of them fresh). **Refuted.** Determinism through plane glue, and B's glue rule (creation relayed across an atom). |
| Local direction — reading Fano-atom spaces | Practically complete as computation | **What is left.** Proofs: the block lemma for atoms attached at a point, the one-way rule, and the source rule as a theorem. |
| Broader exploration — handles that are not Fano atoms | Opened | **Leads.** Census 58 is a single 'other' brace with octahedral blocks; the trisum brace adds a handle the rule cannot see. **Unassessed.** What native creation does see of them. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native selection reads the genus and the oriented handle tree of three-fold spaces up to 26 points, touching atoms included, with no embedding. **Missing bridge.** Proofs, and handles that are not Fano atoms. |
| Next recommendation — a two-bit screening lemma | **Next step:** Continue. Prove that a side attached at a line, which passes its line's six patterns to the cut, acts as that line for creation as well as for solutions. This would complete the splitting lemma, and likely give the block lemma for atoms at a point and the one-way rule across cuts. Then aim for a theorem that the source rule counts Fano atoms. | **If yes.** Native reading of the handle count becomes a theorem for three-fold spaces. **If no.** The obstruction locates where two bits across a cut matter. **Alternatives.** Non-Fano handles (2/3); the source rule beyond 26 points with SAT enumeration (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Every rule it would prove is exact on all data, and the one-bit screening lemma is a template. **Main uncertainty.** Two bits cross the cut, a case HANDLE-LOCALITY left unexplained, so a proof may need a new idea. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The proof, with exact checks on the existing families. **Stop when** the lemma is proved, or its failure is located on a counterexample. |
