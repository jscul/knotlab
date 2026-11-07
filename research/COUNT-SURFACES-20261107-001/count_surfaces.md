# The knot's count on surfaces

Epic `COUNT-SURFACES-20261107-001` (program complexity), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, please continue" to `COUNT-TFNP-20261107-001`'s recommendation (i): does the surface's Euler
  characteristic and orientability decide the class of the knot's count (PPADS, PPAD, PPA, or satisfiable)?
- **The agreed first step.** Start with small projective-plane and torus systems.
- **What was done.** The count was proved on every closed surface. Satisfiability was then settled on the lattice tori by a theorem,
  and on Klein bottles, projective planes and genus-2 covers by computation.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Signs.** Each face's agreement parity is fixed by the signs. The even faces D satisfy \|D\| ≡ χ (mod 2), every such D occurs, and each D carries 2^(2 − χ) sign classes. So Kasteleyn signs (D = ∅) exist iff χ is even, on the torus and Klein bottle but not on the projective plane. | known-with-delta (bipartite Kasteleyn condition); proved | A |
| 2 | **The count.** violated lines − Σ⌊agree/2⌋ = (χ − \|D\|)/2 under every assignment. It forces a violated line only on the sphere with Kasteleyn signs, and over-agreeing faces when χ < \|D\| (every genus ≥ 2 with Kasteleyn signs). Wherever it forces, the false-clause search is in PPADS^dt, on orientable and non-orientable surfaces alike, so no knot count is PPA^dt-hard. | new as far as found; proved | A |
| 3 | **Matchings.** When χ = \|D\|, satisfying assignments are, two to one, the perfect matchings of lines with faces off D in the one homology class the signs prescribe. Each corner map is accepted by exactly one class. | new for these constraints; proved; checked by brute force on 9 spaces | A |
| 4 | **Lattice tori.** A class is satisfiable iff the slope triangle conv{(0,0), (p,q), (0,−r)} has an integer point of matching parity. The unsatisfiable classes are exactly one on each degenerate torus, one on each thin torus (circumference √3) of even index, and the untwisted class of the two Fano tori. Thin tori are cyclic chains, so a violated line is found in O(log n) queries. | criterion known-with-delta (Kenyon–Okounkov–Sheffield; Ibeas Martín); classification new as far as found; proved, SAT to index 40, criterion to 120 | A |
| 5 | **Other surfaces.** Simple lattice Klein bottles (222), hexagonal projective planes (48 class instances), genus-2 covers (17), and double covers of the knot spheres branched at 4 or 6 corners are satisfiable in every class. | computation only | A |

## Answer

- **χ decides whether the count forces.** It forces when χ ≠ \|D\|, and on which side:
  - lines on the Kasteleyn sphere, where it is PPADS^dt-complete;
  - faces when χ < \|D\|, where it is in PPADS^dt with hardness not studied;
  - nothing when χ = \|D\|.
- **Orientability never enters.** The knot's count is not Sperner's: it never drops to PPA.
- **Off the sphere the lattice spaces are satisfiable**, except thin tori (one-dimensional chains, FP^dt) and the two Fano tori.
- **So the TFNP class of the knot's own contradiction is a property of the sphere.** On other surfaces a contradiction comes only from
  a sphere hidden inside: three-fold spaces of any genus are refuted by their plane core's count (`TWO-ROUND-BRIDGE-20261106-001B`).

## Reading

**Interpretation, not a theorem.**
- **What the count is.** It is a discrete Poincaré–Hopf theorem. A line's index is agree − 1 ∈ {0, 2} and a face's is 1 − agree; they
  sum to χ.
- **Where the defect sits.** Positive curvature must be paid on a line, which is the knot's contradiction. Negative curvature must be
  paid on a face. A flat surface pays nothing.
- **The odd defects** (the even faces D) are placed by the signs in advance. On the projective plane, χ = 1 forces the signs themselves
  to carry one.
- **Why orientation is invisible.** The count counts agreeing corners, which carry no orientation. Sperner counts oriented triangles,
  which is why its class drops to PPA on non-orientable surfaces and the knot's does not.

## Literature and provenance

- **The bipartite Kasteleyn condition on surfaces.** Kasteleyn 1963; Cimasoni–Reshetikhin, CMP 2007; Cimasoni, LMP 2009
  (non-orientable, 2^(2 − χ) Pfaffians).
- **Height changes on tori.**
  - Kenyon–Okounkov–Sheffield, Annals 2006.
  - Ibeas Martín, arXiv 1206.5178 (every integer point of the Newton polygon is realized).
- **Antiferromagnets on triangulations.**
  - On lattice tori the satisfying assignments are the zero-frustration ground states of the triangular Ising antiferromagnet
    (Wannier 1950; Blöte–Hilhorst 1982), with periodic or antiperiodic couplings.
  - Jiménez–Kiwi, arXiv 1107.3767: for the related satisfying states on triangulations of orientable surfaces of unbounded genus,
    existence is NP-complete.
- **Sperner on surfaces.** Friedl–Ivanyos–Santha–Verhoeven, CIAC 2006.
- **Classes.** Göös et al., JACM 2024 (PPADS^dt = unary Sherali–Adams); Beame et al., JCSS 1998 (separations).
- **Provenance.** The holes view chose the invariant (the corner count as an index sum) and supplied the reading. The proofs are
  standard: T-joins, Poincaré duality, height functions and lattice slicing.
- **Folklore risk.** Moderate for the torus classification, which the antiferromagnet literature may hold in another form. Low for the
  count's orientation-blindness.

## Ratio

Since the epic opened:
- **Substantive.** One proof family (A: theorems 1–5 and the computations).
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
| Current attempt — whether χ and orientability decide the count's class | **Status:** Successful | The count forces iff χ ≠ \|D\| (lines on the Kasteleyn sphere, faces when χ < \|D\|). It is in PPADS^dt wherever it forces and orientation-blind, so it is never PPA-hard. Lattice tori are classified exactly; Klein bottles, projective planes and genus-2 covers are satisfiable in every tested class (computation). Open: hardness on the face side; Klein bottles and projective planes are not proved. |
| Local direction — the knot's count across surfaces | Practically complete for lattice surfaces | Every lattice family tested is satisfiable off the sphere except thin and Fano tori. Non-lattice surfaces of fixed genus are not classified. For unbounded genus a related problem is NP-complete (Jiménez–Kiwi). |
| Broader exploration — the complexity of the knot's spaces | Known alternatives | Sphere: PPADS-complete (COUNT-TFNP). Three-fold spaces: PPADS via plane cores. Surfaces: this epic. Unmapped: the face-side count's hardness and non-lattice fixed-genus families. |
| Long-term goal — "hardness at three places" and question 9 (low-dimensional shape from a uniform local law, nothing drawn) | Capability gained for the first; no demonstrated advance on the second | The knot's own contradiction needs positive curvature: the count is a discrete Poincaré–Hopf theorem and reads χ. But the faces (co-lines) here are drawn, so question 9 does not move. A law that supplied its own co-lines (each pair in a line lying in exactly one co-line) would build the surface, and the count would then read it natively. |
| Next recommendation — curvature and the knot's class, or question 9 | **Next step:** Research directions. (i) Negative curvature's count: is finding an over-agreeing face on Kasteleyn spaces of genus ≥ 2 (χ < \|D\|) PPADS-complete, mirroring FLAT-STATES-B's Sperner embedding with clockwise orientation? (ii) Return to question 9: which uniform laws of lines and co-lines build their own closed surface, and on which does the count force the knot's contradiction (a sphere grown, not drawn)? The choice is yours. | (i) would make the classification symmetric: the sign of χ − \|D\| alone decides which side fails, and both sides are PPADS-complete. (ii) moves question 9 directly, with the count as a native detector of positive curvature. |
| Interest — those recommendations | **(i) 2/3 — Promising; (ii) 2/3 — Promising** | **(i)** Membership is proved, and COUNT-TFNP-B's map already sends clockwise triangles exactly to monochromatic faces. The risk is that cone points absorb the forced excess, which needs a flat state outside the region on a surface with cone points. **(ii)** The native-surface definition is immediate. Whether a uniform law supplies its own co-lines is exactly question 9's open rung, and native genus reading (GENUS-READ-20261107-001) is related work to read first. |
| Execution — that action | Deferred to the owner | **Not started.** (i) Stop when a mirrored reduction on a genus-2 cover or the trivially signed octahedral sphere is proved, or an obstruction is found. (ii) Stop when small uniform line/co-line laws are enumerated with their χ, and the count's forcing is decided on each. |
