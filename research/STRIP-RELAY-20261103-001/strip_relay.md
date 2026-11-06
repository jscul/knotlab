# The frozen region by heights, and rigid strips

Epic `STRIP-RELAY-20261103-001` (program topology), 2026-11-03.

## The question

- **The approval.** The owner said "Yes, let's continue." to FACE-CLAIM-20261103-001's recommendation.
- **What it asked.**
  - Prove that a port pattern freezes exactly the points whose height difference to the ports cannot vary.
  - Explain the junction where the halo left the faces around the attachment point.
  - Test whether long rigid strips through liquid bodies carry the halo.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The heights lemma.** The port class fixes the ports' heights, since the merged face's skip lies on a known arc. Heights with fixed port values are closed under rounded midpoints, so a port pattern freezes exactly the points whose height difference to the ports cannot vary. | proof; 488 of 488 frozen cases | A |
| 2 | **The reduction lemma.** Across a 3-edge cut, a side holding neither the attachment point nor the gluing line acts as the vertex it lost. Collapsing it leaves the transfer and creation unchanged. | proof (transfer and pipeline); 253,536 pipeline cases, 1,080 exact | A |
| 3 | **The junction explained.** In the collapsed space every creating far line lies on a face around the attachment point, including the 28 that were off those faces in the spliced space. A ring point sees the closed prism, where the ring's far face is its opposite face. | proof plus computation | A |
| 4 | **Pendant rings.** From the middle point of the ring's removed line, the halo runs along the ring's whole far face, k − 3 lines for every ring length tested. | proof (given the ladder law) plus computation | B |
| 5 | **Rigid strips relay.** In a grid–strip–grid dumbbell, an opened handle in the strip or the far grid creates in the first grid near its cut. It does so from every distance along a rigid strip, at the same lines for every length. | computation; exact on small dumbbells | C |
| 6 | **Liquid connectors screen.** With a grid in place of the strip, only points three steps from the first grid relay. | computation | C |
| 7 | **Orientation.** A relay enters only a side split at a point at that cut, and a handle leaves its grid only where the grid lost a line. A line-attached composite handle is screened. | computation, explained by HANDLE-LOCALITY's screening | C |

## Answer

- **The frozen region by heights.** Yes: a point is frozen exactly when its height difference to the ports cannot vary. The class fixes the
  ports' heights, and midpoint convexity does the rest.
- **The junction.** It was the interface lemma at work. The grid beyond the ring's cut acts as the ring's missing line, so the ring sees
  the closed prism. The faces-around-the-point law holds once untouched sides are collapsed.
- **Rigid strips.**
  - **Pendant rings.** They carry the halo along their whole length.
  - **Strips between two liquid bodies** relay a handle's halo to the far body, at the same lines for every length.
  - **Liquid connectors** screen it within three steps.
  - **Direction.** The relay flows only one way through each cut: from the side that lost a line to the side that lost a point.

## Reading

- **Rigid strips as channels.** A rigid strip is a native channel for a handle's one-bit reading. Native selection sees a handle at the far
  end of a frozen channel, in a liquid region the handle is not in.
- **A composite handle.** Seen from the receiving grid, the channel and everything behind it is one composite handle attached at the cut.
- **Directed channels.** The cut orientation makes the channels directed, the same direction as a handle's own splice.
- **The dimer phase, made concrete.** Frozen carries, liquid screens, and the heights say exactly which points are frozen.
- **Doctrine.** Distances only describe where creation was found. The heights are a proof device. Hubs remain equality fan-out. A channel
  carries a reading, not a metric.

## Literature

- **Ours.** FACE-CLAIM A–C, PHASE-HALO B (the ladder law), HANDLE-LOCALITY A–B (the interface lemma and the screening of line-attached
  handles), PLANAR-THEOREM A (midpoint convexity), HALO-FORCING B (heights).
- **Classical.** L♮-convexity of difference systems (Murota), and frozen regions of dimer models.
- **New here.** The heights lemma, the reduction lemma with its explanation of the junction, the ring law, relays, their screening and
  their orientation.

## Pending the owner

- **Supersession.** Whether to supersede or qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
  - **PHASE-HALO's D001.** Its law of the faces around the point holds after reduction.
  - **FACE-CLAIM's D003.** It called that law refuted; the refutation applies to the unreduced space only.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the frozen region by heights, and rigid strips | **Status:** Successful | **Proved.** Frozen means a fixed height difference; untouched sides beyond a 3-edge cut collapse without changing creation; pendant rings carry the full ladder halo. **Computed, exact on small pieces.** Rigid strips relay a handle's halo to a second liquid body, at the same lines for every length; liquid connectors screen; relays are directed. |
| Local direction — the halo | Practically complete for single channels | **What is left.** Proofs of the relay's length independence and of the composite-handle reading, and the claim rule's converse. |
| Broader exploration — where selection creates | Remapped with channels | **The map.** Handles create at their gluing lines, on the faces around their point after collapsing untouched sides, and at the far end of rigid channels. Liquid regions and line attachments screen. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native selection reads a handle through directed frozen channels: a native, one-bit, directed connection between distant regions, without any metric. |
| Next recommendation — relay networks | **Next step:** Continue. Branch and chain rigid strips through small pieces, and test whether one handle's halo reaches several grids, how relays from two handles combine where channels meet, and whether directed channels compose into native paths. | **If yes.** Native selection supports directed wiring, a candidate native path structure for the contact-network program. **If no.** Junctions of channels screen or merge readings, which bounds what channels can carry. **Alternatives.** Proofs of the relay's length independence and the composite-handle reading (1/3). The converse of the claim rule (2/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Relays are exact, length-independent and directed. Branching pieces are easy to build with the same splices. **Main uncertainty.** A branch point is a small piece that may act as a hub (equality fan-out). It might copy the reading or screen it. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Networks of up to a few hundred points with the validated pipeline and exact checks on small ones. **Stop when** branching and meeting are decided for rigid channels. |
