# Halos carried along wires

Status: Proved (exact computation; the whole hub network follows by the splitting lemma)

Ticket `NATIVE-GENUS-20261104-001C`, 2026-11-04.

## Question

Wires and hubs carry an opened atom's halo far from the atom (STRIP-RELAY C, RELAY-NET). Can they carry one atom's halo into another
atom's region, and does that blur the native count of ticket B?

## Dependencies

- **`NATIVE-GENUS-20261104-001A`.** The splitting lemma and `genus_lib.py`.
- **`NATIVE-GENUS-20261104-001B`.** The native count.
- **`STRIP-RELAY-20261103-001C`.** The small dumbbell: two 4-point cubes joined by a rigid strip from a ring over an 8-cycle.
- **`RELAY-NET-20261104-001B`.** The small hub network: a cube hub relaying into two prisms over 6-cycles, with a ring.

The halo of an atom is the set of glue-side lines where its removals create.

## 1. A rigid strip (exact on the whole space)

- **The wire.** The dumbbell has 14 points: the near cube receives from the strip, and the far cube emits into it.
  - **Lone atoms.** A Fano atom alone at a strip point sends its halo into the near cube from five of the seven strip points.
  - **The first atom, X,** sits at point 10 of the far cube. Its halo covers 2 lines of the near cube, 3 of the far cube and 3 of the
    strip: it crosses the wire.
- **The second atom, Y,** sits at each of the 13 other points and lines of the two cubes. The whole space (26 points) is computed exactly.

| Y | Placements | X's halo on Y's cut or ports | X's halo on Y's halo | Count | Pieces |
| --- | --- | --- | --- | --- | --- |
| At a point of the near cube | 3 | 1–2 lines | 2 lines | 2 | one per atom |
| At a point of the far cube | 3 | 2–3 lines | 4 lines | 2 | one per atom |
| At a line of the near cube | 4 | 2 lines | — (no halo) | 2 | one per atom |
| At a line of the far cube, off X | 1 | 2 lines | — | 2 | one per atom |
| At a line of the far cube through X's point (touching) | 2 | 3 lines | — | 1 | merged |

- **The halos overlap in every placement (13 of 13).** X's relayed halo lands on Y's cut lines or ports, and, for Y at a point, on lines
  of Y's own halo.
- **The count is unchanged.**
  - **Separated placements.** In all 11, the quiet part is unique, the count is 2 through shared points and through interior points, and
    each piece is one atom.
  - **Touching placements.** The 2 merge, as ticket B predicts.
- **Each halo stays its atom's.** In all 13, the halo of each atom in the whole space equals its halo with that atom alone, which is the
  splitting lemma at work.

## 2. A hub (each atom alone, exact; the whole space by the splitting lemma)

- **The network.** It has 19 points: a ring, a cube hub, and two receivers A and B.
- **The first atom** sits at each of the six ring points.

| Ring point | X's halo beyond the ring and hub | Receiver points reached | Where X's halo meets the second atom's cut |
| --- | --- | --- | --- |
| 13 | 3 lines of A | 5 | 5 of 5 |
| 14 | none | — | — |
| 15 | 3 lines of B | 5 | 5 of 5 |
| 16 | none (the hub only) | — | — |
| 17 | 3 lines of A, 2 of B | 7 | 7 of 7 |
| 18 | 2 lines of A, 3 of B | 7 | 7 of 7 |

- **Broadcast.** From ring points 17 and 18 the hub copies X's halo into both receivers, as in RELAY-NET B.
- **Overlap.** A second atom at any receiver point the halo reaches has X's halo on its cut lines: 24 of 24 placements. Its own halo lies in
  its receiver (5 lines).
- **The whole space.** It has 31 points, too many to enumerate, but the splitting lemma determines it, since both atoms are attached at
  points:
  - every entry involving one atom is that atom's alone;
  - the count is fixed by the glue's quiet lines and the atoms' lines, as in ticket B.

## Reading

- **Wires do carry one atom's halo into another's region.** In these small networks the overlap is total: every placement of the second
  atom where the halo lands meets it.
- **The count does not blur.** It reads the quiet part and the creative part.
  - **The quiet part** holds the glue lines, among which nothing creates.
  - **The creative part** holds the atoms' lines, at which the glue's removals create.
  - **A halo does neither.** It is creation by an atom's removal at a glue line, so it changes neither part.
- **Each halo is attributed natively.** A halo line belongs to the removals that create there. Each removal lies in exactly one piece of
  the creative part, so each halo belongs to one atom, wherever the wire takes it.

## Checks

`check.py` (`result.json`, about ninety minutes; the whole spaces in section 1 use 8 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | A rigid strip, exact on 26 points | X's halo crosses the strip; overlap in 13 of 13 placements; count 2 with one piece per atom in all 11 separated placements; halos as alone in 13 of 13 |
| 2 | A hub, each atom alone | the halo lands in a receiver from four ring points, in both from two; it meets the second atom's cut at 24 of 24 receiver points |

## What this does not establish

- **Long wires and large hubs exactly.** Only the smallest strip and hub are computed; longer ones rest on STRIP-RELAY and RELAY-NET.
- **Atoms attached at lines as the first atom.** Such atoms have no halo on plane glue (ticket A), so they cannot be relayed.
- **The whole hub network.** It is not enumerated; it follows from the splitting lemma, proved for atoms attached at points.

## Novelty

New here: overlapping halos of two atoms, and the fact that the native count and each halo's attribution survive them.
