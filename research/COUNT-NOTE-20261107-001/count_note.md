# The sphere's count written out, and stronger proof systems

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `COUNT-NOTE-20261107-001` (program complexity), 2026-11-07.

## The question

- **The approval.** The owner said "Could you do both a and b?" to `SPHERE-SIZE-20261107-001`'s two directions:
  - (a) one self-contained note proving the width and size results with every lemma written out (the sketched ones and the
    grid-Sperner boundary), plus a final literature check;
  - (b) test cutting planes or Res(⊕) on the count.
- **The agreed stop.**
  - The note proves every lemma, or names the gap it finds.
  - The count's standing in Sherali–Adams, cutting planes and parity reasoning is recorded with its evidence class.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The sphere's bounds hold with every lemma proved.** Width Θ(√n) and size 2^Θ(√n). The two sketched steps were replaced rather than patched. The vortex moves one step at a time inside one octant, so certificates only need adjacency, not winding numbers. Straight cuts from the vortex to the six corners make zero-weight steps rare, which gives d ≥ (dist − 19)/2. Connectivity is a count of lattice rows. | proved; two local lemmas decided exactly by computation | A |
| 2 | **Grid Sperner needs resolution width Ω(m) and size 2^Ω(m)**, and so does Itsykson et al.'s Sperner CSP. In general resolution only tree-like size was known. Three straight cuts to the doors make the fixed boundary flat, so every boundary term is ≥ 0, and certificates through a deep vortex never reach the boundary. | proved (the size bound was a sketch) | A |
| 3 | **The count has a degree-3 Sherali–Adams refutation with coefficients ±1** (4n − 8 terms: lines' clause falsifiers minus faces' monochromatic conjunctions = 1). So "find a violated line" is in PPADS^dt (Göös et al.). It sits between one-sided 2D Sperner and PPADS. | proved; the placement by citation | B |
| 4 | **Stronger reasoning does not help solvers.** A cutting-planes solver (Exact) and an XOR-reasoning solver (CryptoMiniSat) do no better than plain CDCL on K_2..K_7. At k = 6, Exact fails within 600 s and CryptoMiniSat takes 108 s, against 18 s for CDCL. | experiment | B |

## Answer

**(a) Done; no gap found.**
- The proof is now self-contained modulo the cited, proved facts about frames and labels (`FLAT-STATES-20261107-001A`,
  `SPHERE-COUNT-20261106-001A`).
- Rewriting changed the method, which is now simpler than the sketch it replaces:
  - no winding numbers;
  - no isoperimetric inequality;
  - only adjacency, one local geometric lemma, and a row count.
- The grid-Sperner boundary turned out harmless for a structural reason. In the three-arc gauge the fixed boundary is a flat state:
  boundary points carry no slack.

**(b) Placed in Sherali–Adams; open for cutting planes and Res(⊕).**
- The count is a low-degree, unary counting refutation, which places it in PPADS^dt.
- Solvers using cutting planes or XOR reasoning do not exploit any advantage.
- Whether short cutting-planes or Res(⊕) proofs exist is open.

## Literature and provenance

The final check found:
- no general-resolution bound for 2D Sperner (only tree-like, Itsykson–Malova–Oparin–Sokolov 2014);
- no proof-complexity treatment of height functions with vortices;
- nothing on cutting planes or Res(⊕) for these formulas.

The methods are Atserias–Dalmau and Dantchev–Riis. The new ingredients:
- single-step vortex moves;
- straight cut systems;
- island terms;
- the flat-boundary gauge for Sperner.

Folklore risk: moderate for the method and for the grid-Sperner statement, low for K_k.

## Reading

**Interpretation, not a theorem.** On the sphere, the knot's first contradiction is a global count of lines against faces: Euler's
two extra faces.
- **Sherali–Adams** reads that count directly, with weights ±1 and degree 3: a PPADS-type "unbalanced count".
- **Resolution** must find it by local reasoning, and pays 2^Θ(√n): the vortex can always be moved away from anything held densely.
- **Solvers** with cutting-planes or parity reasoning behave like resolution here.

So the count behaves like the mutilated chessboard, and unlike Tseitin, whose parity hides from Sherali–Adams as well.

## Ratio

Since the epic opened:
- **Substantive.** Two proof families: A (the note, with new lemmas and checks) and B (the unary certificate and the solver
  record).
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
| Current attempt — the self-contained note (a) and stronger systems (b) | **Status:** Successful | (a) Every lemma is proved, with no gap, and grid Sperner's size bound is upgraded from a sketch. (b) The count is in unary Sherali–Adams of degree 3 (PPADS^dt). Cutting planes and Res(⊕) remain open as proof systems. |
| Local direction — resolution lower bounds for the knot's spaces | Practically complete for the plane core | Width Θ(√n) and size 2^Θ(√n) are written out. Decorated three-regular contradictions are not covered; extending to them is routine, not discovery. |
| Broader exploration — the count among proof systems and TFNP classes | Searching | Sherali–Adams: easy (unary, degree 3). Resolution: 2^Θ(√n). Cutting planes, Res(⊕) and unary Nullstellensatz (PPAD) are unassessed. |
| Long-term goal — the complexity of the knot's spaces | Capability gained | The knot's emergence on a closed surface is a natural PPADS^dt count that is exponentially hard for resolution. Its place relative to PPAD, the two-sided Sperner class, is the missing bridge. |
| Next recommendation — the TFNP placement | **Next step:** Research directions. (i) Does the count have low-degree unary Nullstellensatz refutations? Yes would put it in PPAD^dt. A degree lower bound would make it a natural planar member of PPADS^dt outside PPAD^dt. (ii) Alternative (1/3): a short cutting-planes refutation built from the line–face count. | (i) This decides whether one-sided orientation, the knot's sign, matters to the TFNP class. The cheap discriminator is the Nullstellensatz degree over Q on K_2..K_6 by linear algebra, before any proof. |
| Interest — that recommendation | **2/3 — Promising** for (i); **1/3** for (ii) | (i) A separation would be a clean structural statement. The uncertainty is that unary Nullstellensatz lower bounds are hard, and small instances may not reveal growth. (ii) Cutting planes probably succeeds on counts, which leaves less to discover. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** the Nullstellensatz degree is computed for K_2..K_6 and either grows or stays bounded. |
