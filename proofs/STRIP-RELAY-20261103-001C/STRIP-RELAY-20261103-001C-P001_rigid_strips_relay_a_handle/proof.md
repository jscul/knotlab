# Rigid strips relay a handle

Status: Computed exhaustively on the dumbbells tested, exactly on small ones; the mechanism and the orientation rule are explained by the
composite-handle reading (no new proof)

Ticket `STRIP-RELAY-20261103-001C`, 2026-11-03.

## Question

- **The setting.** A strip between two liquid bodies has no single 3-edge cut that leaves the gluing side untouched. So the reduction
  lemma does not apply.
- **The question.** Can an opened handle's halo cross such a strip?

## Dependencies

- **`STRIP-RELAY-20261103-001A`.** The reduction lemma and the library (`strip_lib.py`: dumbbells, port alignment).
- **`FACE-CLAIM-20261103-001A`.** The claim rule.
- **`HANDLE-LOCALITY-20261103-001B`.** Handles attached at a line are screened.
- **The validated pipeline and the join method.**

## Setting

- **Dumbbells.** A grid (the dual of the subdivided octahedron), a connector, and a second grid, joined through two 3-edge cuts. The
  connector loses two vertices as far apart as possible.
- **Connectors.**
  - **Rigid strips.** A ring (the prism over a 2k-cycle) minus two vertices.
  - **Liquid connectors.** Grids.
  - **Thick tubes.**
- **The first grid** is split at a point at its cut: its cut vertices are lines.

## 1. Rigid strips relay (computed)

Strips from rings over 16-, 24-, 32- and 48-cycles, between two 16-point grids, with an opened Fano handle at every attachment point.
- **Strip handles.** At every distance from the first grid up to the strip's far end (7, 11, 15 and 23 steps), two strip points relay:
  they create in the first grid beyond the strip.
- **Second-grid handles.** One point of the second grid relays as well.
- **The relayed lines.** Always the same four lines of the first grid, around its removed vertex, whatever the strip's length.
- **The claim rule.** It agrees with the pipeline at every first-grid line seen from outside the first grid: 473 cases, 20 creating
  (strip from a 16-cycle).

## 2. Liquid connectors screen (computed)

| Connector | Points | Distances from which points relay (steps to the first grid) | Farthest point |
| --- | --- | --- | --- |
| 64-point grid | 94 | 3, 3, 3, 3 | 21 |
| 256-point grid | 286 | 3, 3, 3, 3 | 37 |
| thick tube 4 | 62 | up to 5 | 15 |
| thick tube 6 | 78 | up to 7 | 17 |
| thick tube 8 | 94 | up to 9 | 19 |

- **A liquid grid screens.** Only points next to the first grid's cut relay.
- **Thick tubes are between.** They relay part of the way, about half their length. Their long polar faces carry part of the reading,
  as PHASE-HALO found for their halos.

## 3. Orientation (computed)

Creations by where the handle sits and where the line lies (strips from 16- and 24-cycles):

| Second grid at its cut | grid2 → grid1 | strip → grid1 | strip → grid2 | grid1 → anything else | grid2 → strip |
| --- | --- | --- | --- | --- | --- |
| lost a line (cut vertices points) | 3, 3 | 17, 29 | 0 | 0 | 20, 32 |
| split at a point (cut vertices lines) | 0 | 20, 32 | 21, 33 | 0 | 0 |

- **Grids split at a point receive.** The first grid always is, and receives from the strip.
- **A grid that lost a line emits.** The second grid's handles reach the strip and the first grid only when it lost a line.
- **First-grid handles never leave.**

## 4. Exact relays (exact on small dumbbells)

- **The dumbbells.** Two 4-point cubes (the census's K4^(3) as a grid) joined by strips from rings over 8- and 12-cycles: 14 and 18 plane
  points, 20 and 24 points with the handle.
- **The test.** At the points relaying from 5 or more steps (one point at 5 steps; three points at 5, 5 and 7), exact creation (join
  method) runs at every line, removal and far side.
- **The result.** It agrees with the pipeline in every case (326 and 1,152 cases), and creates in the first grid (8 and 24 instances).

## Reading: the composite handle

**What a relay is.**
- **The composite handle.** Seen from the first grid, everything beyond its cut (connector, second grid and the opened Fano plane) is a
  non-planar knot space minus a line: a **composite handle** attached at the grid's removed point.
- **A relay is that handle's halo.** It sits around the removed point, at the same few lines whatever the strip's length.
- **What the strip does.**
  - **A rigid strip** carries the Fano plane's opened state to the cut, as a ladder carries its two bits.
  - **A liquid connector** forgets it within three steps, so the composite handle looks intact.

**The orientation rule.**
- **Receiving.** A grid receives only through a cut where it is split at a point. Where it has lost a line instead, the composite handle
  is attached at a line, and line-attached handles are screened (HANDLE-LOCALITY B).
- **Leaving.** For the same reason, a handle leaves its grid only through a cut where its grid has lost a line.

**So** information flows across a 3-edge cut from the side that lost a line to the side that lost a point. That is the direction of the
handle's own splice.

## What this does not establish

- **A proof that relays are length-independent.** The strip's transfer between its cuts should depend only on the parity of its length,
  by the ladder's period-2 transfer matrix. This is not checked here beyond the lengths tested.
- **A proof of the composite-handle reading.** It interprets the computations. The screening of line-attached handles it relies on is
  itself computed (HANDLE-LOCALITY B).
- **Exactness at large sizes.** The pipeline is used there; exact creation is checked on small dumbbells.

## Novelty

New here: relays through rigid strips, their screening by liquid connectors, and the orientation rule.
