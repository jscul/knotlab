# The touching rule at every distance

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `CHAIN-TRANSFER-20261106-001` (program topology), 2026-11-06.

## The question

- **The approval.** The owner said "Yes, let's continue." to PENDANT-LINE's recommendation: a transfer along chains, proving the
  touching rule at every distance in Fano trees.
- **Why it mattered.** It was the one gap between the dictionary up to distance two and the statement that "the tree can be recovered
  from creation by a short rule". The short rule in question was BRACE-TREE's source rule.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The touching rule holds at every distance.** In every Fano tree, a line creates at a line of another atom exactly when that line touches its atom's cut toward the first. With the block lemma, creation on a Fano tree is fixed by its tree. | proved: reduction to chain profiles; 47 profiles, closed after three atoms; 12,894 verdicts checked | A |
| 2 | **Free ports; creation decided in the receiving atom.** A removal leaves the three ports of every cut beyond it free, and the last atom alone decides creation. | proved (same computation) | A |
| 3 | **The source rule holds up to five atoms and fails at six.** A receiver with two loaded cuts that emits the line through their points has no source. | proved: every tree of at most five atoms checked; the counterexample confirmed by an exact creation map | B |
| 4 | **Creation reads the directed tree.** Twin classes are the atoms, and receivers' footprints give every cut with its direction, in every Fano tree whose atoms have at most four cuts (condition N). | proved by hand from 1; checked exhaustively up to five atoms and on random trees | C |
| 5 | **Through plane glue the reading rule does not extend as stated.** On BRACE-TREE C's 93 spaces with plane glue, a glue line joins an atom's twin class (155 atoms) and an atom splits into three twin pairs (10 atoms). No class ever mixes two atoms. The source rule counted those spaces correctly. | computed: exact creation maps of the 111 fresh spaces | C |

## Answer

- **The touching rule is proved at every distance.** The chain carries only finitely much: 47 profiles, of which every chain ends in one.
  Every profile leaves the ports free, so the receiving atom decides creation by itself.
- **The source rule is not a theorem.** It held on every space computed before, all of at most four atoms. It holds on every Fano tree of
  at most five atoms, and fails at six.
- **A short rule that is a theorem.**
  - **The rule.** Two lines lie in one atom when they create at each other and at the same other lines. The other atoms that create at a
    proper subset of an atom's lines are those beyond one of its receiving cuts.
  - **What it reads.** The atoms and the directed tree of every Fano tree whose atoms have at most four cuts.
- **So "the tree can be recovered from creation by a short rule" is a theorem for Fano trees, with that rule.**
- **Through plane glue neither rule is enough yet.**
  - **Twins.** The twin rule is disturbed by glue in two ways: a glue line can join an atom's class, and an atom can split into three twin
    pairs.
  - **The source rule.** It counted the glued spaces computed so far, but it fails on larger Fano trees.

## Reading

- **Directions are decided at the receiving end.**
  - **Openness travels intact.** A removal opens every cut beyond it, whatever the atoms between.
  - **Direction is read at the receiver.** Whether a line feels it depends only on whether it touches its own atom's cut facing the
    removal.
- **An atom is a set of lines that are seen together.** Lines of one atom create at each other and are created at by the same lines
  elsewhere. That is the native meaning of a handle.
- **The tree is read from its receivers.** Every cut has one receiver. The receiver's lines through the point it lost are the only ones
  that feel the far side, so each cut leaves a footprint that names it.
- **Doctrine.**
  - **No space is assumed.** Twins and footprints are relations among lines, so the tree is read from native creation alone.
  - **The far sides.** Creation is the creation map's, against its four census far sides.

## Literature

- **Ours.**
  - The two-round rule (PENDANT-LINE A).
  - Exact contraction (PENDANT-LINE C).
  - The block lemma (TWO-BIT-SCREEN B).
  - The source rule and its evidence (BRACE-TREE B and C).
- **Classical.**
  - Finite-state computation over tree-like decompositions (transfer along bounded interfaces).
  - Trees determined by their edge splits (Buneman).
  - Tight-cut decompositions (Lovász).
- **New here.**
  - The profile automaton and its closure.
  - The touching rule at every distance.
  - The refutation of the source rule.
  - The twin and footprint reading.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
- **No new decision.** `BRACE-TREE-20261105-001-D002` and `D003` stay correct as stated. Their spaces have at most four atoms, where
  the source rule holds. This epic's discoveries record where it fails.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the touching rule at every distance | **Status:** Successful | **Proved.** The touching rule holds at every distance (47 chain profiles; 12,894 verdicts). **Refuted.** The source rule fails at six atoms, though it holds up to five; exact maps confirm the failure at six and seven atoms. **Replaced.** Twins and footprints provably read the atoms and the directed tree of every Fano tree whose atoms have at most four cuts. |
| Local direction — reading Fano trees | Complete under condition N | Every Fano tree whose atoms have at most four cuts is read exactly. **Open.** Trees with heavily loaded atoms; an atom that lost all its lines cannot be read as lines at all. |
| Broader exploration — reading every three-regular contradiction | Open at plane glue | **Twins through glue.** On BRACE-TREE C's 93 spaces with plane glue, a glue line joins an atom's twin class (155 atoms) and an atom splits into three pairs (10 atoms). No class ever mixes two atoms. **The source rule** counted those spaces correctly. **Untested.** Non-Fano handles. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native creation recovers the directed handle tree of every Fano tree with at most four cuts per atom, by a short rule, and every cut's direction is read at its receiver. **Missing.** Plane glue, present in every three-regular contradiction with planar pieces. |
| Next recommendation — reading through plane glue | **Next step:** Continue. Add plane pieces to the profile automaton, starting with doubled squares and the smallest planar braces. Explain the joined glue line and the split atoms. Look for one rule that reads the atoms, and so the genus, of every three-regular contradiction. | **If yes.** The genus and the tree of handles would be read natively on every three-regular contradiction. **If no.** The first glue piece that no finite rule reads, which marks where native reading stops. **Alternatives.** Non-Fano handles through the same automaton (1/3); the bridge to proof complexity (2/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The automaton works for any finite piece, and the census disturbances are few and structured. **Main uncertainty.** Plane pieces have no size bound, so finiteness needs either a reduction of plane glue to small pieces or a uniform planar argument. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Doubled squares and the smallest plane braces, then the census. **Stop when** the effect of plane pieces on profiles is classified, or a reading rule through glue is proved or refuted on the census. |
