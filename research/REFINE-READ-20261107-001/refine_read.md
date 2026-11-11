# Colour refinement on the native creation map

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `REFINE-READ-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, let's continue." to GENUS-READ's recommendation: run colour refinement on the native creation
  map and ask whether it ever merges lines of two atoms.
- **What changed early.** That test turned out to be the wrong discriminator. A canonical colouring must merge lines that a symmetry
  exchanges, and symmetric spaces exchange whole atoms.
- **The real question.** Does every symmetry of the native map map atoms to atoms, so that the map fixes the atoms? Then: does one
  uniform rule read them?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Colour refinement merges atoms where symmetry forces it.** Lines of two atoms share a class in 87 of 277 spaces, 14 of the 23 Fano trees among them. This is no obstruction: the yes/no twin rule reads every Fano tree. | computed | A |
| 2 | **Native creation fixes the atoms in every computed space.** Pair refinement (folklore 2-WL) never puts a pair within an atom and a pair across atoms in one class, in 277 of 277 spaces. Every symmetry of the native map maps atoms to atoms, and "same atom" is definable in three-variable counting logic in each space. | computed; classical logic of refinement | A |
| 3 | **The far sides are what do it.** On whether creation occurs alone, pair refinement mixes them in 42 spaces, including all 39 where lines of two atoms are yes/no twins. | computed | A |
| 4 | **No uniform rule tried reads every space.** Yes/no two-stage reads 219. Native row twins, maximal twin cliques, twins vetoed by refinement and twins compatible at glue lines each read 234. The native twin relation is an equivalence everywhere, and refinement cannot veto it. | computed | B |
| 5 | **How they fail.** Native twins merge atoms in 38 spaces, in 32 by complete twinship of two whole atoms. | computed | B |
| 6 | **A regularity.** Two lines of one atom that are native twins never create at a common glue line in different ways (17,494 of 17,494 pairs). Across atoms 530 of 1,572 do, too few to separate every merge. | computed | B |

## Answer

- **The handles are there to be read.** In every space computed, the native creation map determines the partition of lines into Fano
  atoms, and so the genus wherever every handle is a Fano piece. No symmetry hides them.
- **But no uniform rule reads them all.** The natural rules all stop at 234 of 277 spaces. Where two atoms meet one plane piece, they can
  be complete twins at every atom line, and their difference lies at the glue.
- **What existence leaves open.** Refinement proves a per-space definition exists. Whether one formula serves every space is open.

## Reading

- **Native emergence does not hide topology, in these spaces.**
  - **Yes/no creation alone has symmetries** that exchange lines of different handles.
  - **Which far side creates breaks every such symmetry.** That holds with the three far sides that do not depend on gluing.
  - **In the intuition's terms,** the handles are present in the native relations, as the theory would want.
- **Determined, but not yet read uniformly.**
  - **In logical terms,** the atoms are definable space by space, in the logic that pair refinement captures.
  - **The open question** is uniform definability across spaces. That is a question in descriptive complexity, the logic side of the
    owner's interest in hardness.
- **The regularity hints at the mechanism.** Lines of one handle can differ at the glue only by whether they create, never by how. Lines
  of two handles sometimes differ by how.
- **Doctrine.** Everything here is invariant under relabeling lines and re-listing their points.

## Literature

- **Classical.**
  - Weisfeiler and Leman refinement.
  - Cai, Fürer and Immerman: 2-WL types are C^3 types.
  - Invariance of refinement colours under automorphisms.
- **Ours.**
  - The order-free far sides and the native maps (GENUS-READ).
  - The yes/no obstruction and the two-stage rule (GLUE-READ C).
  - Native row twins (GENUS-READ C).
- **New here.**
  - That native creation fixes the atoms of every computed space.
  - The rule comparison, and the glue regularity.

## Pending the owner

- **From GENUS-READ.**
  - Qualifying `FAR-READ-20261106-001-D002` and the second sentence of D001. Flags are committed.
  - The publication of the GENUS-READ intuition entry and flags. The follow-up publish run was blocked by a permission check; this
    epic's closure publishes them.
- **From STRIP-RELAY.** Qualifying `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — colour refinement on the native map | **Status:** Successful | **Answered, and sharper than asked.** Colour refinement must merge symmetric atoms, but pair refinement shows the native map fixes the atoms in all 277 spaces. No symmetry obstruction exists in any computed space. |
| Local direction — a uniform native rule through plane glue | Practically exhausted for hand-made rules | **Four designs.** GLUE-READ's, FAR-READ's (not native), native row twins, and their refinements: all stop at 234 of 277. **What could reopen it.** A uniform formula found by a principled search over refinement invariants, or a proof that none of bounded size exists. |
| Broader exploration — handles that matter for counting | Known alternative | **Junction handles.** HANDLE-COUNT found that counting hardness on contradictions lives at the glue's junctions, not at Fano pieces. Whether native creation sees junctions is untested. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native creation fixes the genus of every computed space built from Fano pieces. Fano trees are read by a theorem. **Missing.** A uniform reading through glue, and handles that are not Fano pieces. |
| Next recommendation — native creation at junction handles | **Next step:** Continue, in the adjacent direction. On spaces with trisum glue (HANDLE-COUNT's constructions), compute exact native creation maps. Ask whether the map fixes the junctions, by pair refinement as here, and whether junction lines carry a native signature that counts them. | **If yes.** Native creation sees exactly the handles where counting becomes hard, linking emergence to hardness. **If no.** Hardness lives where native creation is blind, a sharp and interesting separation. **Alternatives.** Uniform definability of the atoms (1/3); a native audit of earlier far-side records (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The method here is general: refinement on the native map decides whether any structure is fixed. HANDLE-COUNT supplies the junction spaces and the hardness link. **Main uncertainty.** Exact creation maps of trisum spaces may be costly, and junctions may be invisible to creation. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** HANDLE-COUNT's trisum spaces and a fresh family of them. **Stop when** pair refinement shows whether native creation fixes the junctions, and a junction signature is found or ruled out. |
