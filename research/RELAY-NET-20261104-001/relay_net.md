# Relay networks

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `RELAY-NET-20261104-001` (program topology), 2026-11-04.

## The question

- **The approval.** The owner said "Yes continue." to STRIP-RELAY-20261103-001's recommendation.
- **What it asked.**
  - Branch and chain rigid strips through small pieces, and test whether one handle's halo reaches several grids.
  - Find how relays combine where channels meet.
  - Find whether directed channels compose into native paths.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Arc signals.** After a frozen hop, a relay reaches the next cut as an arc signal: two ports fixed and disagreeing, the third free. | proof (from the reading lemma) | A |
| 2 | **The arc lemma.** An arc signal freezes exactly the lines with a corner on the own arc between its fixed ports. | sufficiency proved; converse computed (160 of 160, 0 of 3,542), junction exceptions | A |
| 3 | **Repeaters.** A station passes an arc signal on exactly when its out-line lies on that arc. Aligned chains repeat it losslessly, the same live pins at every cut; misaligned ones lose it. | computation | A |
| 4 | **Depth.** Aligned chains carry relays four cuts into the final grid, misaligned ones stop within two. At separated cuts every creation k cuts away passed cut k live. A live signal creates at the end only when the claim rule allows (20 of 44). | computation | A |
| 5 | **Broadcast.** A hub copies a relay into several receivers at once. | computation; exact on a small hub | B |
| 6 | **Direction.** No relay ever creates upstream of the handle's piece. | computation | B |
| 7 | **Bypasses.** Stations with adjacent cut vertices pass relays without loss, at every chain length tested. | computation | B |
| 8 | **Exact.** A broadcast, a three-cut chain and a two-cut relay are confirmed by exact creation on small networks. | exact | B |

## Answer

- **Several grids.** Yes: hubs broadcast.
- **Chains.** Relays travel as wires that carry one bit, whether two ports agree. They pass a station exactly when its out-line lies on the
  wire's arc. Aligned stations repeat the bit without loss; a misaligned one ends the wire.
- **Native paths.** Directed wires compose. They never run upstream, they branch at hubs, and they run as far as alignment allows. The
  claim rule decides where the bit is displayed as creation.
- **Meeting channels.** Only one handle is opened by any removal, and an intact handle is invisible. So two handles never meet in one
  relay.

## Reading

- **Wiring.** Native selection supports a directed wiring. The wires are frozen arcs in the plane glue, and they carry one bit of an opened
  handle's state. They branch at hubs and end at misaligned stations.
- **What it is not.** The wiring is not a metric and not a contact network. It is where the reading of a handle can be found.
- **Doctrine.**
  - Steps only describe placements.
  - A hub is equality fan-out: it copies a reading.
  - The heights and patterns are a proof device.

## Literature

- **Ours.** STRIP-RELAY A–C, FACE-CLAIM A, HANDLE-LOCALITY A–B.
- **Classical.** Frozen regions of dimer models; unit propagation in matchings.
- **New here.** Arc signals, the arc lemma, repeaters, broadcast and the depth scan.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — relay networks | **Status:** Successful | **Found.** Wires (arc signals), repeaters, broadcast through hubs, downstream-only flow and bypasses. **Proved.** The arc lemma's sufficiency. **Exact.** On small networks. **Withdrawn along the way.** A "two-cut" depth limit, which was an artifact of one cut placement. |
| Local direction — relays | Practically complete | **What is left.** The display rule (when a live wire creates), the arc lemma's converse as a theorem, and networks with overlapping cuts. |
| Broader exploration — where selection creates | Mapped as a wiring | **The map.** A handle creates around its point, after collapsing untouched sides. It also creates at the end of every aligned wire leaving its piece, and at every branch of a hub. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native selection's reading of a handle has a directed wiring structure. The missing bridge: whether that reading sees the space's topology, such as its number of handles. |
| Next recommendation — a native reading of genus | **Next step:** Continue. Build spaces with several Fano pieces in plane glue joined by wires and liquid regions. Ask whether the creation map over all removals splits into one halo per atom, so that it counts the handles and locates them, and when wires make the halos of different atoms overlap. | **If yes.** Native selection counts handles, a native genus invariant. **If no.** Overlapping halos show what native selection cannot separate. **Alternatives.** The display rule (1/3). The claim rule's converse as a theorem (2/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Each removal opens exactly one atom, and halos and wires are now computable at scale, so the creation map is computable and attributable. **Main uncertainty.** Wires and hubs can carry one atom's halo into another's region, which may blur the count. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Spaces with up to four atoms and a few hundred points, with exact checks on small ones. **Stop when** the count and location of handles from the creation map is decided on the families tested. |
