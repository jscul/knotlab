# Reading with the far sides

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `FAR-READ-20261106-001` (program topology), 2026-11-06.

## The question

- **The approval.** The owner said "Yes, please continue." to GLUE-READ's recommendation: read with the far sides.
- **The obstruction to lift.** Where several Fano pieces meet one planar brace, their lines can be indistinguishable to whether creation
  occurs, so no yes/no rule reads them.
- **What to look for.** A rule that uses which far side creates and separates those atoms without splitting any atom. Then test it,
  frozen, on fresh spaces.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The far sides nest.** The Fano plane and census 58 create at exactly the same pairs. K4^(3) creates only where census 6 does. Census 6 creates without the Fano plane only at glue lines. So at an atom line creation has one of four strengths. | computed: 191 saved spaces, 142,420 pairs | A |
| 2 | **A Fano piece acts as one from outside.** Every atom line outside it receives the same far-side vector from each of its lines. Its lines differ only on glue lines and in what they receive. | computed: 731 of 731 saved atoms and 334 of 334 fresh ones | A, C |
| 3 | **A rule reads every saved space.** It has four steps: twins; twins among atom lines; a split into the finest parts of three or more lines that act as one; reattachment of single port lines through the Fano plane. It returns exactly the Fano pieces of all 191 saved spaces, and every step is needed (168, 185, 188, 191). | computed on the development maps | B |
| 4 | **Frozen, it reads every fresh space.** It reads all 86 fresh spaces within the cost cap (334 atoms), including the 24 where whether creation occurs cannot tell atoms apart. On them the two-stage rule reads 51 and the source rule counts 68. | computed on spaces fixed in advance | C |
| 5 | **The far sides always separate atoms.** In none of the 277 spaces are two lines of different atoms indistinguishable far side by far side. | computed | C (and GLUE-READ C) |

## Answer

- **Which far side creates is enough, in every space computed.**
  - **The rule.** It was frozen after development on 191 maps.
  - **What it returns.** Exactly the Fano pieces, and so their number, in all 277 spaces. That number is the genus wherever every handle is
    a Fano piece.
  - **Where the yes/no relation fails.** This includes the 39 spaces where no rule using only whether creation occurs can read the atoms.
- **Not proved.** Neither the rule nor the property behind it is a theorem.

## Reading

- **A handle is one thing from outside.**
  - **What the others see.** Whichever line of a Fano piece is removed, every other handle sees the same creation, far side by far side.
  - **What differs inside.** The atom's lines differ only in what they do to glue and in what they receive.
  - **Atomic topology.** The intuition speaks of the first atomic topology. Here an atom is atomic in a precise sense: its parts are not
    separately visible from outside.
- **Why the yes/no relation failed.**
  - **The plane hides the source.** Where atoms share a plane piece, the plane hides which atom a removal came from, so whether creation
    occurs is the same.
  - **The far sides keep it.** How creation completes, that is which far side, still carries each atom's unity. The small far sides, census
    6 and K4^(3), see more finely than the large ones.
- **A known shape.**
  - **Modules.** "Acting as one" is a one-sided module: the notion behind Gallai's modular decomposition and the clans of 2-structures
    (Ehrenfeucht and Rozenberg), weakened to the vectors an atom sends.
  - **Why the closure is well defined.** One-sided modules are closed under intersections and under unions of overlapping ones. So the
    closure in step 3 is the smallest such module containing its seed.
  - **What is new.** Reading handles as the finest such modules of the creation map is new here.
- **Doctrine.**
  - **No space is assumed.** Cuts, ports and far sides are relations among lines.
  - **The far sides.** They are the creation map's four census far sides, unchanged in this epic.

## Literature

- **Ours.**
  - The receiving-cut law, the two-stage rule and the yes/no obstruction (GLUE-READ).
  - The twin rule (CHAIN-TRANSFER C).
  - The source rule and the census (BRACE-TREE).
  - The two-round rule (PENDANT-LINE A).
- **Classical.**
  - Modules and modular decomposition: Gallai (1967); clans of 2-structures (Ehrenfeucht and Rozenberg).
  - Exact-cover search for the finest partition.
- **New here.**
  - The nesting of the far sides.
  - That atoms act as one.
  - The rule, and its confirmation on fresh spaces.

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
| Current attempt — reading with the far sides | **Status:** Successful (computed) | **Computed.** A four-step far-side rule reads all 191 saved spaces. Frozen, it reads all 86 fresh ones (334 atoms), including the 24 fresh spaces where no yes/no rule can. **Not proved.** The rule, and the property behind it. |
| Local direction — reading the atoms from creation | Reached by computation; proof open | **Kept.** The rule and its record on 277 spaces. **Unresolved.** Whether atoms always act as one; whether the split and the reattachment are theorems. **The cap's gaps.** Census spaces with three more atoms, and the largest plane spaces. |
| Broader exploration — reading every three-regular contradiction | Known alternatives | **Untouched.** Non-Fano handles (census 58). **Carried.** The relation a planar brace presents, derived from its faces. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** The genus of every computed space built from Fano pieces is read from native creation, and the reason is visible: each handle acts as one unit from outside. **Missing.** A proof, and handles that are not Fano pieces. |
| Next recommendation — atoms act as one, proved | **Next step:** Continue. Prove that a Fano piece acts as one from outside. **A scratch probe** on the saved spaces, not part of this epic's evidence, splits the work. **The easy case.** In 576 of 731 atoms (every atom with at most four ports, and 5 with five), removing any line leaves every port pattern allowed. So the solutions outside the atom are the same whichever line was removed. **The hard case.** In the other 155, with five to twelve ports, what the atom allows on its ports depends on the removed line. There the proof must go through the receiving-cut law, over what the other cuts' sides present. | **If proved.** Step 3 of the rule becomes a theorem, and the genus reading rests on a proved unit property of handles. **If it fails.** A counterexample shows where the reading must change. **Alternatives.** Non-Fano handles through the receiving-cut law (1/3); a planar brace's relation from its faces (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** 1,065 of 1,065 atoms act as one, and the easy case covers 576 of 731 saved atoms by a short argument. **Main uncertainty.** Far-side vectors depend on deeper relations, not only on three-port patterns, so the many-port case may need a larger finite check than GLUE-READ A's. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The atom types that occur in the census and the saved maps, against the receiving-cut law's relations. **Stop when** acts-as-one is proved for every atom type that occurs, or a counterexample is found. |
