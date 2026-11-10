# Pre-registration: every accretion law

Epic `GROW-FACE-20261110-001` (`WEAK-APER-20261110-001` direction 2, the same as `HARD-FLAT-20261107-001#3` and
`GROW-COIN-20261107-001#2`; G1; program topology, group `spacing`), written on 2026-11-10 before any computation, at the
coordinator's go-ahead of 19:30 UTC. It is the board line's deciding epic.

## The question

Static laws, with letters or without, choose the plane only by naming a face. Growth is the one route the line has not tried. Can an
accretion law, a law that grows a board from a seed, choose the plane without naming a face?

## Frozen: what would count

- **An accretion law.** Over abstract names, a board grows from a finite seed. A step picks a site and applies the law's action for
  the site's radius-r view, which shows its graph and values but no names: add one new place with a value, joined to the site and
  possibly to places of the view, or join the site to a place of the view. Values come from a finite alphabet. Places are never
  removed or merged.
- **Every order.** An order is fair when every action that stays enabled is eventually taken. A result belongs to the law only if it
  holds in every fair order (`GROWTH-LAW-20261107-001`). A marker that moves with growth is history the process keeps, a witness in
  the sense of `GROW-COIN-20261107-001`.
- **Naming a face.** An action names a face when it closes a cycle: it joins a new place to two or more existing places, or joins two
  existing places. Any such cycle has length at most 2r + 2 and is fixed by the view.
- **Forcing the plane.** Every fair order's limit is the square grid of Z².
- **Growth forcing the plane without a named face.** An accretion law that names no face and forces the plane. That is the escape
  that would change the line's verdict.

## Frozen: what is already closed, and how this differs

| Closed result | What it settled | Why this epic does not redo it |
| --- | --- | --- |
| No undecorated pinwheel law forces roundness (`COLLAR-PLANE-20261108-001`, `ROUND-PRICE-20261108-001`) | Matching rules for one aperiodic tiling need hidden information to be round | It concerns the roundness of a given tiling, not whether growth can choose a two-dimensional shape at all |
| The band law makes the torus from a loop (`BAND-SURFACE-20261108-001`, `GENUS-BAND-20261108-001`) | A uniform law on a declared network of rings grows one surface | Its rings and contacts are declared, and its bands name the faces; here nothing is declared but a seed |
| The doubling law reads the drawn board's distance, scaled (`BOARD-READ-20261110-001`) | Growth on a drawn plane adds scale and clock, no shape | There the plane is drawn first; here it must be grown from a seed |
| Accretion needs a carried coin for round spheres (`GROW-COIN-20261107-001`) | Label-free accretion cannot tie the four equator corners | Spheres, not the plane; this epic's G3 is the plane's version of its "order that splits", and is not run on spheres |

## Frozen: targets, checks and decision

- **Ticket A's targets.** G1 to G3, as stated in its proof stub
  (`proofs/GROW-FACE-20261110-001A/GROW-FACE-20261110-001A-P001_accretion_needs_a_named_face/proof.md`).
- **Checks (`check.py`), with their predictions.**
  - P1: the spiral law of G2, run to 40 full turns, has after turn k exactly the (2k + 1) × (2k + 1) block of the square grid.
  - P2: for r = 3, 4 and 6, the slit order of G3 leaves two places at one grid position, and the place at the slit's base, once its
    neighbourhood is complete, has a radius-3 ball that is not the square grid's.
  - P3, a control: for the same radii the square-closing law filled from the slit's base upward leaves no two places at one position.
- **Decision.** If G1 holds, no accretion law grows the plane without a named face, and the verdict is again that the plane needs a
  named face. The decision note then carries the line's closing summary and marks the static and accretion routes closed. A law that
  escapes, or a failure of G1, would change the verdict and keep the line open.
- **Stop rule, one epic.** The checks run once. No further epic in this line without a new route named first.

## Known before registration (disclosed)

The three targets were sketched by hand while this registration was written. Nothing was computed.
