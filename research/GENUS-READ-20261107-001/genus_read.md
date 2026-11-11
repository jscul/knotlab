# Reading the genus natively

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `GENUS-READ-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, continue." to ATOM-ONE's recommendation: prove that FAR-READ B's rule returns exactly the Fano
  atoms of every Fano tree, then add plane glue.
- **What happened.** The proof needed creation inside an atom. A composition model of it disagreed with an exact creation map, and the
  disagreement came from the order in which a line's points were written.
- **So the epic asked first** what the creation map reads when nothing depends on how lines are written down.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Census 6 depends on how it is glued.** The creation test glues a far side's split-point lines to the gluing line's points in their listed order. For K4^(3), the Fano plane and census 58 the split point's signed stabilizer realizes all six permutations, so they are order-free. For census 6 it realizes two, so there are three gluings. | proved: exhaustive symmetry computation | A |
| 2 | **Measured.** On 64 saved spaces census 6 changes with the order in 8,046 of 11,552 pairs, creating at none, one or all three gluings. K4^(3), the Fano plane, census 58 and whether creation occurs never change. In the Fano plane alone, census 6's "14 of 42" (BRACE-TREE A) is natively one gluing of three at every pair. | computed | A |
| 3 | **Natively a Fano piece is homogeneous.** In every Fano tree, every ordered pair of lines of a Fano piece gets one native vector: no K4^(3), census 6 at one gluing of three, the Fano plane, census 58. It is forced by every state the atom's closed sides can show. | proved: 253 configurations, 2,990 pairs | B |
| 4 | **Atoms act as one natively on Fano trees.** ATOM-ONE B's bound holds at every gluing order. With a free port relation, deep points change nothing at any order. | proved | B |
| 5 | **FAR-READ B's split step is not a native reading.** Given native vectors it cuts every atom of six or seven lines. On the 23 saved and fresh Fano trees it reads none natively, against all 23 in census 6's stored order. The yes/no twin rule reads all 23 and is a theorem under CHAIN-TRANSFER C's condition N. | proved (corollary) and computed | B |
| 6 | **The information that separates atoms through glue is native.** K4^(3), the Fano plane and census 58 alone tell apart all 372 yes/no twins across atoms (39 spaces), and every atom acts as one on them (1,065 of 1,065). For 114 pairs the difference lies only in their rows at glue lines. | computed | C |
| 7 | **Native row twins at atom lines read 234 of 277 spaces** (yes/no: 219). They merge atoms in 38. Adding columns reads 11, because an atom's lines differ in what they receive. | computed | C |

## Answer

- **On Fano trees, the native reading of the genus is the yes/no twin rule.** It is a theorem under condition N, for example whenever no
  atom has more than four cuts. Natively the far sides see nothing inside an atom, which is homogeneous. So FAR-READ's split step, which
  needed internal structure, is not native: it cuts atoms.
- **Through plane glue, no native reading exists yet.**
  - **The information exists.** The order-free far sides separate every pair of atoms that whether creation occurs cannot.
  - **Where it sits.** For a third of those pairs, only in what the lines do to glue lines.
  - **What is missing.** A rule that uses this without cutting atoms.

## Corrections to earlier records (pending the owner)

- **`FAR-READ-20261106-001-D002`** ("which far side creates reads the atoms through plane glue").
  - **The scope it needs.** The four-step rule reads every saved and fresh space only with census 6 glued in each line's written
    order.
  - **Natively.** Its split step cuts every atom of six or seven lines.
  - **What survives.** The information it used to separate atoms is native (conclusion 6).
  - **Proposed:** qualify it.
- **`FAR-READ-20261106-001-D001`.** Its second sentence, the far sides nesting with census 6, holds in the stored orders only. Its
  first sentence, atoms acting as one, holds natively for K4^(3), the Fano plane and census 58, and on Fano trees for census 6's count
  too. **Proposed:** qualify the second sentence.
- **Not discovery records.** BRACE-TREE A's census-6 count and FAR-READ A's four strengths at atom lines. The proof documents of
  ATOM-ONE B and GLUE-READ A make far-side statements about census 6 that hold per gluing order.
- **Unaffected.** Every statement about whether creation occurs.

## Reading

- **A handle is homogeneous, natively.**
  - **From outside.** A Fano piece acts as one (ATOM-ONE).
  - **From inside.** All its lines are alike to each other, far side by far side.
  - **The intuition's word.** A handle is one bound unit, with nothing inside it for creation to tell apart.
- **Representation must not do the work.**
  - **What went wrong.** Census 6's listing order quietly broke an atom's symmetry. A rule then used that broken symmetry to avoid cutting
    atoms, and looked native while depending on how lines were written.
  - **The control that would have caught it.** Re-listing the points of every line and asking whether anything changes.
- **What is native through glue.**
  - **The separation survives** without census 6.
  - **Where it sits.** For many pairs it lies only in the glue lines' view, where an atom's own lines differ too. That is the remaining
    problem.
- **Doctrine.** No space is assumed. The native vector is invariant under re-listing any line's points.

## Literature

- **Classical.**
  - Invariance of a gadget's verdict under its symmetries.
  - The Fano plane's 2-transitive collineation group.
- **Ours.**
  - The four census far sides and the creation map (TWO-BIT-SCREEN, BRACE-TREE).
  - The twin rule (CHAIN-TRANSFER C), the receiving-cut law (GLUE-READ A).
  - Transparency and acts-as-one (ATOM-ONE).
  - FAR-READ's far-side rule, here corrected.
- **New here.**
  - The gluing classification.
  - Native homogeneity, the reachable states of Fano-tree sides, and the all-orders bound.
  - The native measurement through glue.

## Pending the owner

- **From this epic.** Qualifying `FAR-READ-20261106-001-D002`, and the second sentence of `FAR-READ-20261106-001-D001`.
- **From STRIP-RELAY.** Qualifying `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
  - Whether to publish the recent epics to knotlab and jscul.dev.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the genus reading on Fano trees | **Status:** Successful, by refutation and correction | **Refuted.** FAR-READ B's rule is not a native reading: natively it cuts atoms, and its success rested on census 6's listing order. **Settled.** The native reading of Fano trees is the yes/no twin rule (a theorem under condition N), and atoms are provably homogeneous inside. |
| Local direction — a native reading through plane glue | Open | **The information is native.** 372 of 372 obstructed pairs are separated. **Rows are not enough.** Native row twins at atom lines read 234 of 277; 114 pairs differ only at glue lines. **Watch for diminishing returns.** This obstruction has outlived two rule designs (GLUE-READ, FAR-READ). |
| Broader exploration — handles that are not Fano pieces; other far-side statements | Known alternatives | **Untouched.** Junction handles (HANDLE-COUNT) and census 58. **To review.** Earlier far-side statements that rest on census 6's order (listed above). |
| Long-term goal — topology from native emergence | Capability gained, obstruction learned | **Gained.** The genus of Fano trees is read natively by a theorem, and a representation artifact is removed. **Learned.** Inside a handle, native creation sees no structure. Through glue, the native distinction sits in the glue's view. |
| Next recommendation — colour refinement on the native creation map | **Next step:** Continue. Run colour refinement (1-dimensional Weisfeiler–Leman) on the native creation map, with lines as vertices and native far-side vectors as edge colours. It is canonical, so representation-free by construction. **The discriminator.** Does its stable partition ever put lines of two different atoms in one class, on the 277 spaces? **If never.** Assemble atoms from its classes with the acts-as-one relation, and test on fresh spaces. **If it does.** Those spaces are natively symmetric across atoms as far as refinement can see, a sharper obstruction. | **Why this, not another hand-made rule.** It replaces rule design by a canonical procedure, so a negative is decisive rather than one more failed rule. **Alternatives.** Whether junction handles act as one natively (2/3); a native audit of earlier far-side records (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The native map separates every obstructed pair, and refinement uses rows and columns at glue lines together, which the twin rules could not. **Main uncertainty.** Refinement may separate too finely, splitting atoms whose lines differ at glue lines, and reassembly may need a principle not yet in hand. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The 277 saved and fresh maps, with census 6 counted natively where the refinement needs it. **Stop when** refinement is shown to read every space or to merge atoms somewhere. |
