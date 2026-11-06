# The census of handles

Status: Proved (the Fano plane never uses an own arc, from the route lemma); the census and the rule's agreement are computed exhaustively

Ticket `FACE-CLAIM-20261103-001B`, 2026-11-03.

## Question

- **Which faces each handle creates through.** Its own arcs, its opposite faces, both, or none.
- **What decides it.**

## Dependencies

- **`FACE-CLAIM-20261103-001A`.** The reading lemma, the claim lemma and the claim rule (`claim_lib.py`).
- **`HALO-FORCING-20261103-001C`.** The validated pipeline.
- **`PHASE-HALO-20261103-001B`.** On a ladder, every far line's transfer depends only on its parity.

## Setting

- **The spaces.** Up to isomorphism, 24 non-planar knot spaces:
  - the census's two, the Fano plane and census 58;
  - the Fano plane minus a line spliced into each planar census space at each point;
  - each planar census space minus a line spliced into the Fano plane at a point.
- **A handle.** One of these spaces minus one of its lines li: 305 handles in all.
- **The test.** Each handle is attached at a point of the ladder over a 20-cycle in all six orders of li's points, giving 1,830 cases.
- **What the ladder reads.**
  - **The bottom port.** The port joined to the ladder's third line through the point is the bottom port.
  - **The bottom face** is the face opposite the bottom port.
  - **The top face** is the own arc of the other two ports.
  - Every far line lies on one of the two.

## 1. The census (computed)

**The rule.** Which faces are used depends only on which port is at the bottom (all 305 handles). So a handle's **signature** is one
entry per bottom port: O if the opposite face is used, W if the own arc is.

| Signature | Handles |
| --- | --- |
| no face at any port | 93 |
| O at every port | 75 |
| OW at every port | 44 |
| O at one port only | 33 |
| O at one port, OW at the other two | 33 |
| W at two ports | 10 |
| O at every port, W at one | 6 |
| W at every port | 6 |
| W at one port only | 5 |

**By where the removed line sits.**

| Removed line | Signatures |
| --- | --- |
| A line of the Fano plane or census 58 | O at every port (9); census 58's six lines through 0 or 5: O at every port, W at one |
| A line of the Fano plane minus a line, spliced into a planar space | O at every port (66 of 66) |
| An intact Fano line of a planar space spliced into the Fano plane | OW at every port (44 of 44) |
| A cut line, Fano plane into a planar space | O at one port (32); no face (1) |
| A cut line, planar space into the Fano plane | O at one port, OW at the other two (33 of 33) |
| A glue line, Fano plane into a planar space | no face (24); W at one, two or three ports (5, 10, 6); O at one port (1) |
| A glue line, planar space into the Fano plane | no face (68 of 68) |

So where the removed line sits largely decides the signature.
- **Lines inside a Fano atom.** They read like the Fano plane.
- **Lines of an atom opened at a point.** They read both faces.
- **Glue lines.** They read the opposite face rarely.

`result.json` lists the same table.

## 2. The claim rule decides it (computed)

The claim rule of ticket A, applied at one far line of each ladder face, agrees with the pipeline on all 3,660 (case, face) pairs. So
does its form in the handle's ports alone. Classes are relative to the plane's all-agree pattern, and the ports other than c are a and b.
- **The opposite face of port c is used** exactly when some removal and pair of handle points pin one class-c pattern, and each point
  of the pair alone still allows both disagreeing values of (z_a, z_b). By the claim lemma, those values are the face's two claims.
- **The own arc of a and b is used** exactly when some removal and pair pin patterns of classes a and b with z_a fixed, and each point
  alone still allows both class-c patterns. Those patterns are the arc's two claims.

So **which faces a handle uses is a property of its port relation**:
- the patterns pairs of its points pin after a removal;
- what single points leave.

## 3. The Fano plane (proved, with a finite check)

Every line of the Fano plane meets li, so every removal meets li at one port a. On all 7 lines and 6 removals, the following holds.
- **Pairs pin only the class of the met port.** Pairs that pin one allowed pattern pin a class-a pattern (336 of 336).
- **Single pins exclude a fixed amount.** Every single pin excludes exactly one allowed pattern of each other class, on different values
  of those two ports, and at most one of class a (336 of 336).

**Consequences.**
- **No own arc is ever used (proved).**
  - **Pins of class a.** An own arc at port a, say the arc of a and b, has one claim per value, the two class-c patterns. Every single
    pin excludes one of them, so the rule's route direction (proved) gives a route.
  - **Pins of another class.** The same holds for pins of class b or c.
- **The opposite face of a is used (computed).** Its claims at the two values are the two disagreeing values of (z_b, z_c), each
  carried by one class-b and one class-c pattern. A single pin excludes one pattern of each class but never both of one value. So both
  claims survive, and the converse of the rule (computed) gives creation at every port.

So the Fano plane's opposite-face behaviour comes from how sharply its single points cut the port patterns. Each removes one pattern per
other class, enough to kill a one-pattern claim but never a two-pattern one.

## 4. Census 58

- **The special pair.** Its lines (5, 7, 3) and (7, 0, 3) share the two points 7 and 3.
- **When the own arc is used.** Exactly when the bottom port is one of their third points, 0 or 5 (48 of 48 line-order cases). The
  opposite face is used at every port.
- **What decides it.** By the port form of the rule, it is whether some pair pins the top ports' classes while each of its points
  leaves both patterns of the bottom port's class. The census shows this happens exactly for bottom ports 0 and 5. A structural reason
  is not established.

## Checks

`check.py` (`result.json`, about fifteen minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The 24 spaces fail minimally and are non-planar; the ladder's two faces | pass |
| 2 | The census: far halo on the two faces only, depending only on the bottom port; nine signatures | pass |
| 3 | The claim rule and its port form agree with the pipeline | 3,660 of 3,660 |
| 4 | The Fano plane's pins | 336 pairs, 336 single pins |
| 5 | Census 58's two points | 48 of 48 |

## What this does not establish

- **Handles beyond this census.** The census contains one Fano atom per space, and no spaces with two or more atoms.
- **The converse of the claim rule.** It is computed, not proved.
- **Plane pieces other than the ladder.** The census is read on the ladder. Ticket A checks the rule on other pieces for three handles.

## Novelty

New here.
