# Broadcast, depth and bypasses

Status: Computed with the validated pipeline, and exactly (join method) on three small networks

Ticket `RELAY-NET-20261104-001B`, 2026-11-04.

## Question

- **Branching.** Can one opened handle's relay branch into several receivers?
- **Direction.** Does a relay ever travel against the cut orientation?
- **Bypasses.** What do stations with adjacent cut vertices do?
- **Exactness.** Are relays exact on small networks?

## Dependencies

- **`RELAY-NET-20261104-001A`.** Arc signals, repeaters and `relay_lib.py`.
- **`STRIP-RELAY-20261103-001A`.** The reduction lemma and `strip_lib.py`.
- **The validated pipeline and the join method** (HALO-FORCING, HANDLE-LOCALITY B).

## 1. Broadcast (computed)

A hub receives from a ring (a prism over a 12-cycle carrying the opened Fano handle) at a point. It emits into two 16-point grids at
the two lines nearest that point, directly or through strips.

| Hub | Receivers | Ring points reaching both | Reaching one |
| --- | --- | --- | --- |
| 16-point grid | directly | 5 | 0 |
| cube | directly | 2 | 3 |
| 16-point grid | through strips | 0 | 2 |
| cube | through strips | 0 | 2 |

- **Directly.** A hub broadcasts: the same opened handle creates in both grids.
- **Through strips.** Each grid is reached from fewer points, and none reaches both: the strips' out-lines must also be aligned.

## 2. Direction (computed)

Chains grid ← three stations (strips, cubes, 16-point grids or thick tubes), with the handle at every point.

| Stations | In the handle's piece | 1 cut downstream | 2 cuts downstream | Upstream |
| --- | --- | --- | --- | --- |
| strips | 40 | 15 | 2 | 0 |
| cubes | 6 | 0 | 3 | 0 |
| 16-point grids | 21 | 15 | 0 | 0 |
| thick tubes | 41 | 21 | 0 | 0 |

- **No creation lies upstream of the handle's piece.**
- **Placement.** Here each station's out-cut is placed as far as possible from its in-cut, and the relays stop within two cuts; ticket A
  gives the aligned placements that go further.

## 3. Bypasses (computed)

- **Thin stations.** Each station's two cut vertices are adjacent, so the second cut returns an edge to the previous piece.
- **The result.** The relay reaches the final grid from 5 ring points through 1, 2, 3 or 4 such stations, both for cubes and for strips.
  This is as many as with no station at all.

## 4. Exact relays (exact on small networks)

At the relaying ring points, every removal and far side, and every gluing line beyond three steps:

| Network | Plane points | Cases | Disagreements | Exact creations |
| --- | --- | --- | --- | --- |
| a cube hub relaying into two small prisms | 19 | 576 | 0 | 16 in each receiver |
| an aligned chain cube ← prism ← prism ← ring | 19 | 576 | 0 | 16 three cuts away, 16 two cuts, 8 one cut |
| a two-cut relay prism ← cube ← prism | 18 | 744 | 0 | 48 two cuts away, 8 one cut, 8 in the handle's piece |

## Reading

- **Broadcast.** A hub piece copies a relay into every outgoing channel whose out-line its frozen region reaches. One opened handle is then
  read in several places at once.
- **Direction and depth.** Relays never run upstream. They run downstream as far as the wires stay aligned (ticket A).
- **Bypasses.** When a station's two cut vertices are adjacent, the second cut returns an edge to the previous piece. The station is then
  no barrier: relays passed every number of such stations tested, up to four.
- **Doctrine.**
  - A hub is equality fan-out here too: it copies a reading, it does not create contact.
  - Steps describe placements only.

## Checks

`check.py` (`result.json`, about three minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Broadcast through hubs | the 16-point-grid hub relays 5 ring points into both receivers, the cube hub 2; through strips, none reaches both |
| 2 | No creation upstream | no creation upstream in four chain families, at every point |
| 3 | Thin-station chains | 5 ring points reach the final grid through 1 to 4 thin stations |
| 4 | Exact creation on three small networks | 1,896 cases, no disagreement; broadcast, a three-cut and a two-cut relay exact |

## What this does not establish

- **Exact creation on the larger networks.** They rest on the pipeline.
- **A rule for which hub out-lines receive a copy.** The broadcast is observed for out-lines near the receiving point, and its rule is ticket
  A's arc lemma applied at the hub.
- **Networks with cycles.** Splicing two pieces of one network together makes a handle, and these are not studied here.

## Novelty

New here: broadcast through hubs, the downstream-only law in networks, bypasses, and the exact small relays.
