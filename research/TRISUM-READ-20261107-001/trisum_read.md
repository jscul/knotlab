# Native creation at junction handles

Epic `TRISUM-READ-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes  continue." to REFINE-READ's recommendation: on HANDLE-COUNT's spaces with trisum glue,
  compute exact creation maps and ask whether native creation fixes the junctions, and whether junction lines carry a native
  signature.
- **Why junctions.** HANDLE-COUNT found that on the knot's plain spaces the cost of counting sits at the glue's junctions, where planar
  pieces meet along squares, and that atoms pay for them. REFINE-READ had shown that native creation fixes the atoms.
- **How it was run.** Seven small spaces for training (ticket A), then seven frozen statements tested on ten larger spaces whose maps
  were computed only after the freeze (ticket B), and on one space with four junctions as a stress test one size past (ticket C). The
  work began in one session and was finished in a second that took it over within the project.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Yes/no creation reads the atoms.** The lines no removal blocks are exactly the atom cores, and each root is created at by exactly its six core lines. 18 of 18 spaces. | computed | A, B, C |
| 2 | **With the atoms set aside, it reads the junctions.** A junction's two lines are never degenerate and each is the only remaining removal that blocks the other; no other pair is. One to four junctions are counted. 18 of 18 spaces. | computed | A, B, C |
| 3 | **The signature belongs to non-planar glue.** In REFINE-READ's 277 spaces it fires once, in design 7, the only one whose glue holds a non-planar brace other than Heawood, at that brace's junction. | computed | A |
| 4 | **Pair refinement fixes atoms, skeleton, junctions, square-mates and leaves.** 18 of 18 spaces. | computed | A, B, C |
| 5 | **Where an atom hangs is not always native.** In one held-out space (seed 5, three junctions) a symmetry of the native map exchanges the line carrying an atom with an unloaded line of the same cube piece and fixes every atom line. One skeleton automorphism induces it; it keeps the signing's switching class and moves the atom. | computed (exact automorphism) | B |
| 6 | **Yes/no creation is native here.** In all 18 maps census 6 never creates alone. | computed | B, C |
| 7 | **One size past holds.** On the smallest four-junction space the generator gives (62 points), chosen before its map, every frozen statement holds. | computed | C |
| 8 | **The generator is not a function of its seed.** HANDLE-COUNT's Pfaffian signing depends on Python's hash seed, so a run over seeds 1 to 400 gives 17 or 18 spaces. Each space used here is reproduced at its seed under a recorded hash seed. | computed | A |

## Answer

- **Yes: native creation fixes the junctions, and reads them simply.** Once the atoms are read, a junction is a pair of lines that block
  only each other. That held on all seven training spaces, on all ten held-out ones, up to three junctions, and on one with four.
- **Both kinds of handle are native.** HANDLE-COUNT's two handles, the atoms that are free for counting and the junctions that cost,
  are both read from creation alone, with nothing drawn.
- **One limit.** Native creation does not always see on which incidence an atom sits. In seed 5 the glue's symmetry moves an atom
  within its switching class, and the native map cannot tell the two places apart.

## Reading

- **A junction is a mutual block.** Two lines that depend on each other alone: any other removal outside the atoms creates at both,
  and removing either one silences only the other. Plane glue never shows it.
- **What native creation sees of a signing.** In the one space where a frozen statement failed, it failed because the native map has
  a symmetry the space lacks: it sees the glue and the atoms but not where, within the switching class, an atom sits. That suggests a
  conjecture this epic did not test: the native creation map depends on the signing only through its switching class, which is also
  all that Pfaffian counting depends on.
- **The line is near its end.** Where creation happens (atoms and junctions) is now fixed natively in every computed space. What is
  left are a uniform rule through plane glue (REFINE-READ: none reads more than 234 of 277), a proof of the junction signature, and
  the switching-class conjecture.
- **Doctrine.** Everything here is invariant under relabeling lines and re-listing their points.

## Literature

- **Classical.** Trisums and trisectors of Pfaffian braces (Robertson, Seymour and Thomas); switching classes of signed graphs
  (Zaslavsky); Weisfeiler–Leman refinement and its counting logic (Cai, Fürer and Immerman).
- **Ours.** The creation map and the order-free far sides (GENUS-READ), the junction count and its bound (HANDLE-COUNT), the atom
  reading (REFINE-READ).
- **New here.** The junction signature, the held-out test, and the native symmetry that hides where an atom sits.

## Pending the owner

- **An older open epic on the same question.** `JUNCTION-READ-20261106-001` was left active and uncommitted when a restart cut off its
  session on 2026-11-06. This epic answers its question, and it is not this task's node to close.
- **Still open from earlier epics.** Qualifying `FAR-READ-20261106-001-D002` and the second sentence of D001; qualifying
  `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum; superseding
  `KNOT-COMPOSE-20261101-001-D001`; whether counted length should ever count as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — junctions in the native creation map | **Status:** Successful | Junctions read and counted on 18 of 18 spaces, ten held out and one four-junction stress test; one frozen sub-statement failed, by a native symmetry |
| Local direction — reading handles from native creation | Practically exhausted | Atoms and junctions are fixed natively; no uniform rule through plane glue |
| Broader exploration — what native creation sees of a signing | Unmapped | One space shows it blind to the atom's place within the switching class |
| Long-term goal — G4 Emergence lives in handles | Capability gained | Both of HANDLE-COUNT's handles are read natively |

**Corrections:** none.
**Goals:** checkpoint for G4 (capability gained); no goal change. The switching-class conjecture is parked as backlog B5.
**Assumptions:** A29 added, assumed: an atom's place within its signing's switching class does not change what is measured.

The local line ends because its question is answered on every computed space; what remains is a uniform rule (open since REFINE-READ)
and proofs, not a new reading. The missing bridge to G4 is a theorem: why a junction's lines block only each other.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does native creation see only the switching class? | 2/3 — Substantial | 2/3 — Testable | Map a second placement of seed 240 → maps equal on skeleton lines or not | Selected · awaiting go-ahead (parked as B5) |
| 2 | Prove the junction signature | 2/3 — Substantial | 1/3 — Stated | Derive the mutual block on the 29-point space → a proof or a counterexample | Alternative · deferred |
| 3 | A uniform native reading of atoms and junctions | 1/3 — Incremental | 3/3 — Ready | Run one rule over all 294 spaces → read or fail per space | Alternative · deferred |

1. **The switching class.** If the native map depends on the signing only through its switching class, native creation sees exactly
   the data that Pfaffian counting uses, a bridge between G4 and G3 (hardness); if not, seed 5's symmetry is a local accident. The
   question is precise and seed 5 is evidence, and the cheapest test is one 54-point map (about ten minutes): the generator's two
   placements for seed 240 are the same switching class. Parked as backlog B5, at the owner's request to wrap up current work before opening new directions.
2. **A proof of the signature.** It would explain why non-planar glue shows up as a mutual block. The statement is exact on 18 spaces
   and a 277-space control, but no proof route is written.
3. **A uniform rule.** Yes/no creation reads the atoms and junctions of every trisum space; whether one rule reads them in the 277
   planar-glue spaces too is REFINE-READ's open question, and repeating it here adds little.
