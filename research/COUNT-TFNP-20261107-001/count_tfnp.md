# The knot's count in TFNP

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern. Results are unchanged;
the earlier text is in git history.

Epic `COUNT-TFNP-20261107-001` (program complexity), 2026-11-07.

## The question

- **The approval.** The owner said "Yes let's continue on" to `COUNT-NOTE-20261107-001`'s recommendation (i): does the knot sphere's
  count have low-degree unary Nullstellensatz refutations (so lie in PPAD^dt), or is it a natural planar problem in PPADS^dt outside
  PPAD^dt?
- **The agreed stop.** Compute the Nullstellensatz degree for K_2..K_6 and see whether it grows.
- **Deviation.** The literature gave a cheaper and decisive route, so the small-case degree computation was not run. Two facts settled
  it:
  - Beame–Cook–Edmonds–Impagliazzo–Pitassi already separate PPADS from PPA and PPAD in the black-box world;
  - the count turns out to be PPADS^dt-complete.

  An unconditional classification replaces evidence from five small cases.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **One-sided 2D grid Sperner is PPADS^dt-complete, and two-sided grid Sperner is PPAD^dt-complete.** Chen–Deng's planar uncrossing re-pairs each crossing's arms. It keeps every in- and out-degree, hence every sink, source and orientation. Each path becomes a two-lane tube, and fully labelled triangles sit exactly at tube ends: positive at sinks, negative at sources. | known-with-delta; proved; construction checked exhaustively on 3 nodes and on random instances, with controls | A |
| 2 | **The knot's count is PPADS^dt-complete.** Finding a violated line of the octahedral knot sphere composes SINK → one-sided Sperner → (cyclic colour shift) → `FLAT-STATES-20261107-001B`'s map. Membership comes from the degree-3 unary Sherali–Adams certificate. | new as far as found; proved | B |
| 3 | **The two-sided count is PPAD^dt-complete.** Here a solution is a violated line or a monochromatic face. The map sends clockwise fully labelled triangles exactly to monochromatic faces, and the corner identity with face clauses as axioms is a degree-3 Nullstellensatz refutation with multipliers ±1. | new as far as found; proved; map property checked | B |
| 4 | **The count has no low-degree Nullstellensatz refutation and is not in PLS^dt.** By Beame et al. (PPADS^dt ⊄ PPA^dt) and the characterizations PPA^dt = F2-Nullstellensatz and PPAD^dt = unary Nullstellensatz, NAE(K_k) has no polylogarithmic-degree Nullstellensatz refutation over F2, nor a unary one, although unary Sherali–Adams refutes it at degree 3. Since resolution needs width Ω(√n) and PLS^dt is characterized by resolution width, the count is not in PLS^dt either. | proved (qualitative) | B |

## Answer

- **(i) settled, negatively for PPAD.** The count is not in PPAD^dt, nor in PPA^dt. It is complete for PPADS^dt.
- **What separates.** Only the knot's orientation: counting monochromatic faces as solutions too makes it PPAD^dt-complete.
- **Resolution** sees neither difference: both counts need size 2^Θ(√n).

## Reading

**Interpretation, not a theorem.**
- **What the clauses see.** The knot's Kasteleyn signs make its lines see one orientation of the label vortex:
  - a counterclockwise vortex violates a line;
  - a clockwise antivortex only makes a face monochromatic.
- **The classes.** That one-sidedness is the sink-versus-source information that END-OF-LINE (PPAD) cannot use and SINK (PPADS) does.
- **So** the knot's first emergence on the sphere is a complete problem for a standard class, and its orientation is exactly the
  PPAD/PPADS distinction.

## Literature and provenance

- **Positive Sperner.** PPADS-complete in dimension 3 and above (Beame et al. 1998).
- **Surfaces.** Locally 2-dimensional Sperner on surfaces of non-zero genus is complete for PPAD, PPADS and PPA (Friedl, Ivanyos,
  Santha, Verhoeven 2006).
- **The plane.** 2D Sperner is PPAD-complete (Chen–Deng 2006/2009).
- **Characterizations.**
  - PPADS^dt = unary Sherali–Adams, PPAD^dt = unary Nullstellensatz (Göös, Hollender, Jain, Maystre, Pires, Robere, Tao 2024).
  - PPA^dt = Nullstellensatz over F2 (Göös, Kamath, Robere, Sokolov 2019).
- **Not found:** the planar one-sided case stated explicitly. Folklore risk is high for that lemma, low for the knot sphere's
  classification.

## Ratio

Since the epic opened:
- **Substantive.** Two proof families: A (the planar construction and its checks) and B (the classification and its checks).
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
| Current attempt — the count's TFNP class (PPAD versus PPADS) | **Status:** Successful | One-sided: PPADS^dt-complete, outside PPAD^dt, PPA^dt and PLS^dt. Two-sided: PPAD^dt-complete. Settled by a classification rather than by small-case degrees. The Nullstellensatz lower bounds are qualitative. |
| Local direction — the knot sphere's count across proof systems | Practically complete | Resolution 2^Θ(√n) (width Θ(√n)); unary Sherali–Adams degree 3; no low-degree Nullstellensatz; PPADS^dt-complete. Open but incremental: explicit Nullstellensatz degrees, the circuit version, cutting planes and Res(⊕). |
| Broader exploration — the knot's counts on other spaces | Unmapped | Only the octahedral sphere is classified. The Euler count gives violated lines minus monochromatic faces = (F − L)/2, which depends on the space's topology. Friedl et al. tie Sperner's class to orientability (PPAD/PPADS against PPA). |
| Long-term goal — the complexity of the knot's spaces, the intuition "hardness at three places" | Capability gained | The knot's first emergence on the sphere is complete for a standard class, and its orientation is exactly the PPAD/PPADS distinction. This chain presupposes a drawn sphere, so it does not move question 9 (space from a law with nothing drawn). |
| Next recommendation — topology to TFNP class | **Next step:** Research directions. (i) The knot's count on non-orientable and higher-genus drawn knot patterns: does the surface's Euler characteristic and orientability decide its class (PPADS, PPAD, PPA, or satisfiable)? First step: the Euler count and satisfiability on small projective-plane and torus triple systems. (ii) Return to question 9, whose choice is yours. | (i) This would turn the TFNP class into a reading of the space's topology: logic's count would see the surface. That is the closest this line gets to the "space" intuition without drawing more. |
| Interest — that recommendation | **2/3 — Promising** for (i) | **Evidence:** the Euler count makes the surface's χ appear directly, and Friedl et al.'s Sperner results already split by orientability. **Uncertainties:** Kasteleyn-type signs need not exist on non-orientable spaces, and the analogue may be routine. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** the count, satisfiability and the class are settled for the projective plane and torus families, or an obstruction to signing them is found. |
