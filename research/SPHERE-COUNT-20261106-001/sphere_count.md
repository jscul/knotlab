# Is the sphere's Euler count hard for resolution?

Epic `SPHERE-COUNT-20261106-001` (program complexity), 2026-11-06.

## The question

- **The approval.** The owner said "Yes let's continue." to `TWO-ROUND-BRIDGE-20261106-001`'s recommendation. The plan was to prove
  resolution width Ω(√n) for the octahedral three-fold spaces from a lemma that the violated line can always move away, and then to
  attempt the size bound.
- **The agreed stop condition.** Stop if the width bound is proved, or if a configuration is found where the violated line cannot move.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The violated line can be pinned.** Frozen states (concentric alternating rings around it) block local moves: in the bulk, for both classes of adjacent line and every radius up to 3; on K_8 (256 points), for each of the six adjacent lines of the central line at radius 2 and 3, by whole-sphere states. | proved (exhibited configurations, exhaustive solver checks) | A |
| 2 | Random states always move: all 149 tested pairs within radius 2. Frozen states are rare but real. | measured | A |
| 3 | **Label states.** Colouring by a 1-Lipschitz Z6 height through six sublattice patterns makes every triangle not-all-equal except at vortices. A counterclockwise vortex is exactly a violated line and a clockwise one a monochromatic face. | proved | A |
| 4 | Resolution width Ω(√n) reduces to a flat-state pursuit lemma for label states. The size bound was not attempted. | reduction; lemma open | A, B (retired) |

## Answer

- **Not decided.** Whether the sphere's Euler count is hard for resolution remains open.
- **The planned proof fails at its first step.** Tseitin's charge can always be moved by flipping one edge. The knot's violated line
  cannot: it is a vortex of a height function, and in frozen states of maximal tilt it is pinned. That is the stop condition we agreed
  on, met by an explicit configuration.
- **Not a lower-bound failure.** Duplicator chooses her states, so frozen ones can be avoided in principle. Label states, where one
  sublattice is always free, are the natural flat class. Within them the problem becomes topological: the vortex and its six level
  boundaries must be steered through the pebble-free region.

## Reading

- **Parity against counting, once more.**
  - **Tseitin.** Tseitin's contradiction is a Z2 charge, and a Z2 charge has no tilt to freeze.
  - **The knot's spaces.** Their contradiction is an integer count, and its carrier is a vortex of an integer height. Integer heights
    can be maximally tilted, and then the vortex cannot move locally.
- **Same structure as the dimer model.** Frozen regions of the dimer model are the same structure: the knot's single-defect states are
  ground states of the triangular antiferromagnet, which is the honeycomb dimer model.
- **A Poincaré–Hopf reading (interpretation, not a theorem here).** The count "violated lines − full faces = 1" fixes the net vortex
  charge against the corners' curvature.

## Literature and provenance

- **Heights and frozen regions.** Triangular antiferromagnet and dimer heights (Blöte–Hilhorst 1982; Nienhuis–Hilhorst–Blöte 1984);
  frozen regions (Cohn–Kenyon–Propp).
- **Tseitin width by moving charges.** Ben-Sasson–Wigderson; Galesi–Talebanfard–Torán.
- **Width and pebble games.** Atserias–Dalmau.
- **Folklore risk.** High for frozen regions themselves. Low for the obstruction as a statement about these formulas. Moderate for
  label states, which are the ideal states of the antiferromagnet in another notation.

## Ratio

Since the epic opened:
- **Substantive.** One proof family (A) changed a conclusion: the obstruction, and the reduction to a named lemma.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics; nothing new here:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — width from local mobility of the violated line | **Status:** Failed in its planned form | The mobility lemma is false: frozen states pin the violated line, even in whole-sphere states of K_8. The width bound itself is not refuted. |
| Local direction — state-by-state local moves | Retire | Frozen cones block them at every radius tried. Any proof must choose its states. |
| Broader exploration — width and size for the knot's spaces | Unresolved; one route mapped | **Width.** Reduced to the flat-state pursuit lemma. **Size.** Not attempted; it would need restrictions that keep flat states available. |
| Long-term goal — complexity of the knot's spaces | Obstruction learned | Counting principles carried by height vortices are not Tseitin-like: their carrier can freeze. The SA-versus-resolution question stays open. |
| Next recommendation — the flat-state pursuit lemma | **Next step:** Continue. A fresh epic that proves the width bound through label states. First construct label states on the octahedral sphere with corner structures (a finite search). Then prove that the vortex's six strings can be re-routed in thick pebble-free regions. Then run the giant-component Duplicator. | **If yes.** Resolution width Θ(√n) for the knot's three-fold spaces, and a flat-state framework the size argument would need. **If no.** A pursuit configuration that traps the vortex with few pebbles, which would point to small width. **Alternative.** A bounded literature search for planar height-function or flow principles with known resolution bounds, which might give the bound by reduction (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The structure is explicit (strings, vortex, half-circle pebble constraints), and random states move freely. **Main uncertainty.** The topological argument is long, and width alone does not give size in the planar regime. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** label states with corners exist and the pursuit lemma is proved, or a trapping configuration is found. |
