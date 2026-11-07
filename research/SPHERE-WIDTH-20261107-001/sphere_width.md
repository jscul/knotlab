# Resolution width of the sphere's count and of grid Sperner

Epic `SPHERE-WIDTH-20261107-001` (program complexity), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, let's continue." to `FLAT-STATES-20261107-001`'s recommendation: prove resolution width
  Ω(m) for grid Sperner, which would give width Θ(√n) for the knot's sphere.
- **The agreed stop.** The width bound proved, refuted by a trapping configuration, or reduced to a named lemma.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The sphere's count needs resolution width Θ(√n).** Every refutation of the octahedral knot sphere K_k has width ≥ c·k − 1, and O(k) suffices. Duplicator keeps the vortex where pebbles are sparse; any obstruction is a closed walk with a bounded number of steps per pebble, so pebbles can trap only an area quadratic in their number. | proved (winding bound and isoperimetric constant by sketch); criterion, certificates and a simulated game checked | A |
| 2 | **Window criterion on the sphere.** Pebbled colours admit a label state with a given vortex iff a sheet system on the pebbles has no negative cycle; the largest solution is a valid single-defect state. | proved; 216 of 216 solver comparisons | A |
| 3 | **Grid Sperner needs resolution width Θ(m).** The fixed boundary is free for Spoiler, but a certificate walk through it stays within O(w) of the boundary, so a full triangle kept deep inside meets only pure Spoiler walks. As corollaries, Itsykson et al.'s Sperner CSP needs width Ω(n) (only tree-like size was known), and the knot sphere gets its bound a second time through `FLAT-STATES-20261107-001B`'s reduction. | proved; 54 certificates and the locality checked | B |
| 4 | **Locality on the disk.** A pebble chain whose colours advance at most 4 times blocks only triangles next to it; one that advances 5 or more times fits no state at all. So consistent answers never let far pebbles pay for a long chord. | measured (m = 18) | B |

## Answer

- **Width settled for both.** The width of the sphere's count is Θ(√n), and grid Sperner's is Θ(m).
- **No winding-control lemma was needed.** `FLAT-STATES-20261107-001` had reduced the width to that lemma, but the exact window
  criterion already makes every obstruction short relative to its pebbles.
- **Sphere versus disk.** The sphere, with no boundary, is the cleaner case. The disk needs one more lemma, because its fixed boundary
  costs Spoiler nothing.
- **Size is still open.** Width Ω(√n) on n variables gives no size bound for these planar formulas.

## Literature and provenance

- **Width and pebble games.** Width is the existential pebble game (Atserias–Dalmau). Tseitin width comes from expansion or treewidth.
  Grid matching and Tseitin size bounds use tiling games (Dantchev–Riis; Alekhnovich).
- **Sperner.** Tree-like resolution size 2^Θ(n) (Itsykson–Malova–Oparin–Sokolov 2014,
  [arXiv:1412.1124](https://arxiv.org/abs/1412.1124)); queries Θ(√N) (Crescenzi–Silvestri; Friedl–Ivanyos–Santha–Verhoeven). PPADS
  equals unary Sherali–Adams (Göös et al. 2022, [arXiv:2205.02168](https://arxiv.org/abs/2205.02168)).
- **The tools.** Difference constraints (McShane extension, Bellman–Ford), the Vitali covering lemma, discrete isoperimetry.
- **Folklore risk.**
  - Low for the statements: no general-resolution width bound for grid Sperner or for these formulas was found.
  - Moderate for the method. Density or covering arguments are standard in other settings, and specialists may consider the Sperner
    width bound expected.

## Reading

**Interpretation, not a theorem.**
- **Width as span.** Resolution width measures how much of the formula a refutation must hold at once. For the sphere's count it is a
  separator's worth, Θ(√n).
- **Locality.** The knot's vortex can always flee to where nothing is held, because the only thing that pins it is a closed chain of
  held points with few steps per point. The contradiction the knot forms on a closed surface is global, yet any piece of it is local.
- **The contrast with Tseitin.** Its parity charge has the same width profile. The difference between them (counting against parity)
  is invisible to width; it must show up in size or in stronger systems, which is where the open question now sits.

## Ratio

Since the epic opened:
- **Substantive.** Two proof families changed conclusions: A settled the sphere's width, and B settled grid Sperner's.
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
| Current attempt — width of the sphere's count and of grid Sperner | **Status:** Done, proved | Width Θ(√n) for K_k and Θ(m) for grid Sperner. Lemma 3's winding bound and lemma 4's isoperimetric constant are by sketch. |
| Local direction — width bounds by density | Complete | The method covers closed surfaces and, with the boundary lemma, the disk. Nothing local remains. |
| Broader exploration — size for the knot's spaces | **Open; now the main question** | Width cannot give size here. A size bound needs zone-wise randomness (Dantchev–Riis tiling games) adapted to label states with pebble windows. |
| Long-term goal — the complexity of the knot's spaces | Real progress | The sphere's count is now known to be a one-sided Sperner principle (`FLAT-STATES-20261107-001`), easy for Sherali–Adams at level 3, and of resolution width Θ(√n). The remaining gap is resolution size: 2^O(√n) is known, 2^Ω(√n) is conjectured. |
| Next recommendation — resolution size of the sphere's count | **Next step:** Continue. A fresh epic adapting Dantchev–Riis tiling games: zones of constant size, label states random per zone, and the density bad set in place of their bad region. | **If yes.** Resolution size 2^Θ(√n) for the knot's sphere and for grid Sperner: "the mutilated chessboard of the sphere". **If no.** An obstruction to zone-wise randomness for height principles with a vortex. **Alternative.** Settle whether the level-3 Sherali–Adams refutation is unary, placing the count in PPADS (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The width proof supplies the geometric core (sparse regions are safe), and Dantchev–Riis did the same for matchings. **Main uncertainty.** Zone states must disagree on every open point while gluing across zone borders, and labels are pinned only up to three values. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** size 2^Ω(√n) is proved, or the zone-randomization obstruction is exhibited. |
