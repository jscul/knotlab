# Does every law that composes like cycles keep its top layer rigid?

Epic `TOP-LAYER-20261102-001` (program topology), 2026-11-02.

## The question

- **The approval.** The owner said "Yes, let's continue on with this" to RIGID-SELECTION-20261101-001's recommendation.
- **The plan it approved.** Test the non-abelian groups that compose like cycles up to order 24 and the 1020 non-simple three-value
  Mal'tsev laws, then attempt a proof.
- **What it would show.** If true, the knot stands apart at every number of values.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Three values.** Every law on three values that composes like cycles is rigid. All 1020 non-simple ones (185 classes): every three-place knot is pulled back from a two-element section (exhaustive), and every global failure met is rigid (443 in all, with Z3 and 300 simple classes). | finite validation | A |
| 2 | **Which groups.** A group's coset law composes like cycles iff every subgroup has a unique maximal normal subgroup. Such groups have cyclic Sylows and a top of prime order. Up to order 60: the cyclic p-groups and 18 non-abelian groups (dihedral of order 2p^k; C5⋊C4, C7⋊C3, C13⋊C3, C13⋊C4, C11⋊C5, C19⋊C3). | proof; enumeration | B |
| 3 | **Group laws keep their top rigid.** Knots are pulled back from cyclic p-group relations, so systems with declared domains reduce to Z_(p^K) and RIGID-SELECTION D applies. The law is rigid at prime-order sections; C5⋊C4 and D9 keep knots below the top. | proof; brute force (108 global failures) | B |
| 4 | **Depth is needed.** In every Mal'tsev law, knots are pulled back from abelian sections. If every abelian section is simple, every global failure of a system with declared domains is rigid. Hence all laws on three values and all non-affine laws on four. Two layers are necessary but not sufficient: T2(F2) is rigid on regular substrates. | proof; 26 random four-value algebras (1518 knots, 573 global failures) | C |
| 5 | **The global top is the wrong layer.** A simple Mal'tsev law on five values containing Z4 composes like cycles and keeps knots in its top (RIGID-SELECTION B's systems inside it). So the statement as phrased is false. | construction; brute force | D |
| 6 | **The section's top is the right layer.** When the sections of a failing system come from one chain ring, the leading digits of all variables form at most one line after any removal. Every kept knot has at most one varying leading digit. Two different rings joined through tops: 407 global failures, none against it, not proved. | proof; checks | D |
| 7 | **Correction to ticket B.** Its theorem holds for systems with declared domains. Lines with their own smaller ranges are not covered by the proof, though every such case met was rigid. | correction | D |

## Answer

- **Not as phrased.** The top of the whole algebra can contain deep sections.
  - **The example.** A simple five-value law built around Z4 composes like cycles. Its top is everything, so the knots it keeps inside
    Z4 sit in its top.
- **True in the form that matters.**
  - **Depth is needed.** A law that composes like cycles keeps emergence inside a selected space only through an abelian section with
    two layers, which needs at least four values.
  - **Kept below the top.** It keeps that emergence only below the top of that section. This is proved when its sections come from
    one chain ring, which covers every group and every law met so far.
- **The knot stands apart.** It keeps three-place emergence on two values, with no depth at all, in its only layer: on the Fano plane
  after every removal, and on 5 of the 8 Pfaffian census substrates.

## Reading

- **Depth is a carry.**
  - **In Z4.** The emergence that survives selection lives where a digit carries into the next. In example 1 the system is solvable
    mod 2 and fails mod 4.
  - **The owner's harmonies.** Read through them, a law that composes like cycles can hide a harmony only one digit down. Its
    leading digits are pinned to a single line, as a field's would be.
- **The knot needs no carry.**
  - **No cancellation.** Its failures need none (the spaces are sign-nonsingular).
  - **Its emergence.** It keeps emergence where it has its only layer.
- **The 2-versus-3 boundary, sharpened.**
  - **Where selection kills emergence.** In laws that compose like cycles, every one-layer section collapses to ties, which are
    pairwise.
  - **Where three-place emergence survives.** Below a carry, or in the knot.
- **Selection leaves a hub.**
  - **The leftover.** When the knot's selected space loses a line, the line's three points become tied (the rest forces it to be
    all-equal), and knots remain around it.
  - **In the Fano plane.** The four points off the line become a new four-place knot.
  - **Why it matters.** The knot's spaces are Fano atoms glued along lines (THREEFOLD-GRAMMAR). So selection's leftover is exactly the
    gluing interface: this is the lead for the next step.

## Literature

- **Ours.**
  - KNOT-CIRCUITS Theorem 1.
  - BEYOND-TWO B and C.
  - RIGID-SELECTION A, B and D.
  - MUTUAL-SELECTION C's census.
  - THREEFOLD-GRAMMAR (trisums).
- **Classical.**
  - Commutator theory for modular varieties (Freese–McKenzie; Herrmann; Gumm).
  - Fleischer-style fork arguments.
  - Z-groups (Hölder, Burnside, Zassenhaus).
  - Burnside's basis theorem.
  - Wedderburn's theorem.
  - Smith forms over chain rings.
- **New here.**
  - The depth theorem for selection.
  - The list of groups that compose like cycles and their top theorem.
  - The five-value counterexample.
  - The layer-wise statement.
  - The T2(F2) example.

  These are elementary, with moderate folklore risk.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — does every law that composes like cycles keep its top layer rigid? | **Status:** Successful | **As phrased, no:** the five-value simple law built around Z4. **In the corrected form, yes**, for sections from one chain ring: emergence needs depth and stays below the section's top. **Open:** mixed domains, and sections from several chain rings. |
| Local direction — comparing laws that compose like cycles with the knot | Practically exhausted | **What remains is technical completion:** mixed domains, uniserial sections from several rings, non-commutative layers. The evidence is uniform: over 1800 global failures across the checks, none against the corrected statements. |
| Broader exploration — selection, composition and space | Lead found | **Answered by this branch.** What distinguishes the knot: emergence on two values, in its only layer. **Not yet related to it:** the knot's spaces are Fano atoms glued along lines, and how that gluing relates to what selection leaves. |
| Long-term goal — composed topology from native contact | Obstruction sharpened, lead gained | **The obstruction.** No law that composes like cycles selects as the knot does without depth. **The lead.** When the knot's selected space loses a line, the line becomes a hub of tied points, exactly where pieces glue. |
| Next recommendation — what selection leaves, and how pieces glue | **Next step:** Continue. **Claim to test.** In the knot's spaces, removing a line leaves a hub (its tied points) and kept knots, and the trisum glues along that hub. **First test.** On the census and on trisums of Fano atoms: does the emergence each piece keeps survive the glue, and does gluing selected spaces along their leftover hubs build every space of the knot natively? | **If yes.** Composed spaces are built from selection itself, a native composition through hubs that keeps emergence. **If no.** The hubs separate, and composed topology needs something beyond selection. **Alternatives.** Completing the theorem (mixed domains, several chain rings; 1/3). The converse: which two-layer sections keep emergence (T2(F2) does not, Z4 does; 1/3). Revising the selection note (conversion; awaits the owner's erratum decision). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** A concrete mechanism: forced all-equal lines are hubs, trisums glue along lines, and the Fano complement becomes a knot. It connects selection, hubs and the knot's space grammar. **Main uncertainty.** It may reduce to the known trisum decomposition without new native composition. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The 73 census substrates and trisums of up to three Fano atoms. **Stop when** the leftover-and-glue picture is proved or refuted on these. |
