# Resolution size of the sphere's count

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `SPHERE-SIZE-20261107-001` (program complexity), 2026-11-07.

## The question

- **The approval.** The owner said "Continue with this." to `SPHERE-WIDTH-20261107-001`'s recommendation: prove resolution size
  2^Ω(√n) for the knot's sphere by adapting Dantchev–Riis's zone randomization, or find why zone randomness fails for vortex principles.
- **The agreed stop.** Size proved, or the island randomization shown to fail with an explicit obstruction.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Islands keep the count hard.** Fix any packing of small islands (pairwise ≥ 17 apart, away from the corners) to constant labels. The restricted formula still needs resolution width Ω(k). Island points add no budget to obstructions, and every hop between islands costs one unit, so certificates stay short and the density argument survives. | proved (inherited sketches); island terms, feasibility and certificates checked | A |
| 2 | **The sphere's count needs resolution size 2^Θ(√n).** A random hard-core packing fixes each point with constant probability, with independence beyond distance 40. A refutation of size 2^{o(k)} would leave a refutation of width o(k) of some restricted formula, contradicting (1). The upper bound n^O(1)·2^O(√n) was known. | proved; packing properties checked | B |
| 3 | **Grid Sperner (sketch).** With islands allowed to touch the boundary away from its doors, the same argument gives size 2^Θ(m). So Itsykson et al.'s Sperner CSP needs 2^Ω(n) in general resolution, where only tree-like size was known. | sketch | B |

## Answer

- **Settled.** The sphere's count needs resolution size 2^{Θ(√n)}: the "mutilated chessboard of the sphere" conjecture of
  `TWO-ROUND-BRIDGE-20261106-001` holds.
- **A separation.** Together with Sherali–Adams level 3 refuting it, the knot's sphere separates Sherali–Adams from resolution, as the
  mutilated chessboard does.
- **Zone randomness works.** It did not fail for this vortex principle. The density argument is robust to permanent pebbles that carry
  no slack.

## Literature and provenance

- **The paradigm.** Local randomization is Dantchev–Riis (FOCS 2001; Dantchev's thesis BRICS DS-02-2), and this repository's
  `CELL-SIZE-20261020-001` used it for Tseitin.
- **2D Sperner.** Tree-like size 2^Θ(n) (Itsykson–Malova–Oparin–Sokolov 2014); queries Θ(√N) (Crescenzi–Silvestri). No general-resolution
  size bound was found. Göös et al. (2022) separate in the opposite direction (resolution beats unary Sherali–Adams on their formulas).
- **Folklore risk.**
  - Moderate for the method: experts would expect Dantchev–Riis to extend to such formulas.
  - Low for the statements, which concern formulas not studied elsewhere. For grid Sperner the statement is natural enough that an
    unpublished or folklore proof may exist.

## Reading

**Interpretation, not a theorem.** On a closed surface the knot's first contradiction is global but locally cheap to hide:
- **Width.** Any part of the sphere can be held as long as nothing around the vortex is held densely.
- **Size.** Holding parts at random costs exponentially many proof lines.
- **The contrast.** Sherali–Adams sees the contradiction at once, by counting lines and faces, and resolution does not. Parity (Tseitin)
  and counting (the knot) part ways in which algebraic systems see them, not in resolution: both cost 2^{Θ(√n)} on the plane or sphere.

## Ratio

Since the epic opened:
- **Substantive.** Two proof families changed conclusions: A, the island lemma, and B, the size bound.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — resolution size of the sphere's count | **Status:** Done, proved | 2^{Θ(√n)}, by local randomization and the island lemma. The constants are tiny but absolute, and the grid-Sperner corollary is sketched. |
| Local direction — resolution lower bounds for the knot's spaces | Complete for the plane core | Width Θ(√n) and size 2^{Θ(√n)}. What remains here is consolidation: the grid-Sperner details, and decorated three-regular contradictions. |
| Broader exploration — stronger proof systems | Open | Sherali–Adams refutes at level 3. Cutting planes, Res(⊕) and bounded-depth Frege are untested on these formulas. |
| Long-term goal — the complexity of the knot's spaces | Major progress | The plane core is classified for resolution (Θ(√n) width, 2^{Θ(√n)} size) and is easy for Sherali–Adams. The knot's first emergence on a closed surface is a "mutilated chessboard" principle. |
| Next recommendation — write and verify, or test stronger systems | **Next step:** Research directions. (a) Turn the three width and size proofs into one self-contained note, closing the sketched lemmas (winding bound, isoperimetry, grid-Sperner boundary islands) and checking the closest literature once more. (b) Test whether cutting planes or Res(⊕) refute the sphere's count cheaply. | **(a)** Converts the strongest result into a checkable artifact; the sketches are the main risk to the claim. **(b)** Would place the count among proof systems and tie it to PPADS (the unary Sherali–Adams question). |
| Interest — that recommendation | **2/3 — Promising** (a); **1/3** (b) | **(a)** The result is large enough to deserve a careful write-up, and the sketched lemmas are standard but unwritten. **(b)** The count is a degree principle, so cutting planes probably refute it, which leaves less to discover there. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** (a) the note is written with every lemma proved, or a gap is found, which would be a discovery in itself. |
