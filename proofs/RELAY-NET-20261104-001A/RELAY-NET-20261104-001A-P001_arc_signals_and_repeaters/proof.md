# Arc signals and repeaters

Status: Proved (the arc lemma's sufficiency); the lemma's converse, the repeaters and the depth law are computed

Ticket `RELAY-NET-20261104-001A`, 2026-11-04.

## Question

- **Background (STRIP-RELAY C).** A rigid strip relays an opened handle's halo across one strip.
- **The question.** What happens through chains of pieces, and what decides how far a relay travels?

## Dependencies

- **`FACE-CLAIM-20261103-001A`.** The reading lemma: in the split at a point, the own arc between ports i and j is barred exactly when
  they disagree, and barred faces fix two points of each line.
- **`STRIP-RELAY-20261103-001A`.** The reduction lemma and `strip_lib.py`.
- **`STRIP-RELAY-20261103-001C`.** Relays, and their orientation (a side receives where it lost a point).
- **The validated pipeline.**

## Setting

- **Networks.** Trees of plane pieces joined through 3-edge cuts (`relay_lib.py`).
- **Chains.** grid ← c1 ← c2 ← c3 ← ring.
  - **Each station** loses a line toward the grid (it emits there) and a point toward the ring (it receives there), at a chosen distance
    d from the line.
  - **The handle.** An opened Fano handle is attached at a ring point.
- **The signal at a cut.** Build the part upstream of the cut with the cut's line restored; by the reduction lemma, everything downstream
  collapses to it. For every removal and pinned pair of handle points, the set of that line's patterns left is:
  - **single:** one pattern;
  - **arc:** two patterns with two points fixed;
  - **lost:** more.
  - A pin that is single or arc is **live**.

## 1. The arc lemma

**Arc signals.** After a frozen hop, a relay arrives at the next cut as an **arc signal**. The frozen line's two corner points are fixed
and disagree, and its third point is free. So two ports are fixed and disagree, and the third port is free.

**Statement.** In a plane piece split at a point, an arc signal on ports a and b freezes a line other than the port lines exactly when
the line has a corner on the own arc between a and b.

**Sufficiency (proved).**
- **What the signal allows.** Its two patterns are a class-a and a class-b pattern with z_a fixed.
- **Both bar the arc.** By the reading lemma, classes a and b both bar the own arc between a and b, so it carries no skip in either.
- **So the arc's points are fixed.** Its points are fixed by z_a, and each line with a corner there has that corner's two points fixed. ∎

**Converse (computed).** Off the arc, the two classes bar different faces, so the line keeps at least three patterns.
- **Generic pieces.** Checked on a ladder, a prism, the 16- and 64-point grids, a grown space and a thick tube, with no exception.
- **The junction.** On the ladder arm spliced onto a grid, some junction lines off the arc are frozen too: the junction rigidity of
  FACE-CLAIM C.

**So a station passes an arc signal on exactly when its out-line has a corner on the signal's arc.**
- **The out-line's corner points** are then fixed and become the next arc signal's fixed pair.
- **Otherwise** the signal is lost.

## 2. Repeaters (computed)

The signal leaving each of the three stations, for every ring point:

| Chain | Live pins leaving c3, c2, c1 (per ring point) |
| --- | --- |
| aligned: strip stations, out-cut 5 steps from the in-cut (separated cuts) | 32, 32, 32 at six ring points; 16, 16, 16 at five; 0 at one |
| misaligned: strip stations, out-cut 7 steps | 16, 0, 0 at one ring point; 0 at the other eleven |

- **Aligned chains.** Every ring point's signal leaves every station unchanged: lossless repeaters.
- **Misaligned chains.** The signal dies at the first station whose out-line is off the arc.

## 3. Depth (computed)

**The scan.** Chains of three stations: strips (prisms over 12-cycles), 16-point grids or cubes, with the out-cut at every available
distance and in three placements. 21 configurations, every ring point.

| Stations and out-cut placement | Deepest creation (cuts from the ring: ring points) |
| --- | --- |
| strips, 3 or 5 steps, two of three placements | 4 (the final grid): 5; 1: 1; none: 6 |
| strips, 3 or 5 steps, the third placement; strips, 7 steps | 2: 1; 1: 5; none: 6 |
| 16-point grids, 3 steps, one placement | 4: 5; none: 7 |
| 16-point grids, 3 steps, other placements | 2: 1; 1: 5; none: 6 |
| 16-point grids, 5 or 7 steps; cubes | 1: 5; none: 7 |

- **The depth law, where a station's two cuts are separated** (5 or more steps apart, so that no line meets both). Every creation k cuts
  from the ring (k ≥ 2) passed cut k as a live signal.
- **Transmission and display.** A live signal reached the final grid in 44 cases, and 20 of them created there.
- **Overlapping cuts.** Where the cuts are 3 steps apart, one line meets both. In 5 cases (16-point grids, one placement) a relay reaches the
  final grid through cuts whose measured signal is lost: the overlap carries it, as adjacent cuts do (ticket B).

## Reading

- **Wires.** An arc signal is a wire. It carries one bit, the agreement of two ports, from cut to cut through stations whose out-line lies
  on the arc. Aligned stations are lossless repeaters, and a misaligned one cuts the wire.
- **Transmission against display.** A live signal can reach the end without creating there. Creation also needs the claim rule's single
  points to keep the final line's claims, and that depends on where the handle sits.
- **Doctrine.**
  - Steps only describe placements; the wire carries a reading, not a distance.
  - Hubs remain equality fan-out.

## Checks

`check.py` (`result.json`, under a minute with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Arc lemma on seven families | generic pieces: 160 of 160 on-arc cases frozen, 0 of 3,542 off-arc cases; the ladder arm on a grid: 32 junction lines off the arc frozen |
| 2 | Signals along the aligned and the misaligned chain | aligned: constant live pins for all 12 ring points (32, 16 or 0); misaligned: none past the first station |
| 3 | Depth in 21 chain configurations | 252 cases; the law holds at every separated cut; 5 configurations reach the final grid; 5 overlapping-cut cases pass lost signals |

## What this does not establish

- **The converse of the arc lemma as a theorem.** It is computed on generic pieces.
- **Exact creation.** Creation here rests on the validated pipeline. Exact checks on small networks are in ticket B.
- **Chains with overlapping cuts.** Where a station's cuts are three steps apart, so that one line meets both, the measured signal does not
  bound the relay.

## Novelty

New here: arc signals, the arc lemma, repeaters and the depth scan.
