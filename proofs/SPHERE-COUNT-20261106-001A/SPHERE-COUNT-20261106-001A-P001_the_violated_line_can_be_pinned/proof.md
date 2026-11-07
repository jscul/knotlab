# The violated line can be pinned

Status: Proved (statements 1 and 2 by exhibited configurations with exhaustive solver checks; statement 3 by hand, checked
exhaustively); the width bound it was meant to give remains open

Ticket `SPHERE-COUNT-20261106-001A`, 2026-11-06.

## Standard statement

Take the not-all-equal formula of a Kasteleyn-signed planar cubic triple system, the octahedral knot spaces K_k. In the bulk it is the
not-all-equal system on the up-triangles of the triangular lattice. An assignment violating exactly one line is a ground state of the
triangular-lattice Ising antiferromagnet with one defect triangle.
1. Unlike the charge of a Tseitin formula, the violated line cannot always be moved locally. Some such states, including whole-sphere
   states of K_8, admit no change within distance 3 that moves it to a given adjacent line.
2. In label states (colourings read off a 1-Lipschitz Z6-valued height through six sublattice patterns) every triangle is
   not-all-equal except at vortices. A counterclockwise vortex is a violated line and a clockwise one is a monochromatic face.

## Nearest known result

- **The antiferromagnet as dimers.** Ground states of the triangular antiferromagnet correspond to dimer coverings of the honeycomb
  and to height functions (Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984).
- **Frozen regions.** Dimer models have frozen regions of maximal tilt (Cohn, Kenyon and Propp).
- **Tseitin width.** Resolution width lower bounds for Tseitin formulas move the charge by local changes, which always exist
  (Ben-Sasson and Wigderson; Galesi, Talebanfard and Torán).
- **Classification.** known-with-delta. Frozen regions are classical. The delta has two parts: they block the pebble-game proof for these
  formulas, and violated lines and full faces read as vortices and antivortices.

## Setting

- **The bulk.** Away from the six corners, complementing points (which changes no clause width) makes every sign zero on any ball of
  the lattice.
- **Lines and faces.** Lines are the up-triangles U(x, y) = {(x, y), (x+1, y), (x, y+1)}. The faces of the incidence graph are the
  down-triangles D(x, y) = {(x+1, y), (x, y+1), (x+1, y+1)}.
- **Single-defect states.** In a state violating only the line M, every face has exactly one agreeing corner
  (`TWO-ROUND-BRIDGE-20261106-001B`, theorem 2). So every triangle, up or down, is not-all-equal except M.
- **Moves.** The violated line moves from M to an adjacent line M′ within radius r when recolouring the points at distance at most r
  from M ∪ M′ can make M′ the only violated line among the lines touching them.
- **Why moves matter.** The Tseitin template for a resolution width lower bound needs such moves from every state. Duplicator keeps
  the defect in the largest pebble-free region and moves it there locally whenever a pebble comes near.

## 1. Local moves fail in the bulk

**Statement.** For both classes of adjacent line and every r ≤ 3, there is a colouring of the ball of radius r + 1 around M ∪ M′ in
which every triangle is not-all-equal except M, and from which no recolouring within radius r moves the violated line to M′.

*Proof.* A two-level search proposes local single-defect colourings and refutes each candidate move. It ends with an explicit
colouring, which is checked directly: it is locally valid, and the solver finds no move (check 1, for M′ = U(1, 0) and U(1, −1),
r = 0, …, 3). ∎

**The blocking colouring at r = 3** is a frozen cone: concentric alternating rings around the violated line.

```
         1 1 1 1 1 0 . . . . .
        1 0 0 0 0 1 1 . . . .
       1 0 1 1 1 0 0 1 . . .
      1 0 1 0 0 1 1 0 1 . .
     1 0 1 0 1 0 0 1 0 1 .
    1 0 1 0 1 1 1 0 1 0 1
   . 0 1 0 1 0 0 0 1 0 1
  . . 0 1 0 1 1 1 1 0 1
 . . . 0 1 0 0 0 0 0 1
. . . . 0 1 1 1 1 1 1
```

From it, within radius 2, the violated line reaches only two of its six adjacent lines, U(−1, 0) and U(1, −1) (check 2).

## 2. Local moves fail on the whole sphere

**Statement.** Take K_8 (256 points), the line M farthest from the corners, and each of its six adjacent lines M′. For r = 2 and r = 3
there is a whole-sphere state violating only M from which the violated line cannot move to M′ within radius r.

*Proof.* The same two-level search, with the proposing level ranging over whole-sphere states of K_8 (check 3: 6 of 6 adjacent lines at
both radii). ∎

**Contrast: random states move.** From 25 random states of K_8, all 149 pairs of a violated line and an adjacent line are reached:
99 within radius 0, 39 within radius 1 and 11 within radius 2 (check 4). Frozen states are rare but real.

**Consequence.** Local moves exist from typical states but not from frozen ones. The Tseitin template therefore cannot be applied
state by state. A width proof must keep Duplicator's states away from frozen ones, and that is not proved here.

## 3. Label states

Give each point a label in Z6. Colour it by the label's pattern on its sublattice, where (x − y) mod 3 is the sublattice and every
triangle meets all three. The patterns are the six not-all-equal colourings of the sublattices, consecutive ones differing on one
sublattice:

  S0 = 011, S1 = 001, S2 = 101, S3 = 100, S4 = 110, S5 = 010.

**Lemma 1.** If a triangle's labels lie within two consecutive values s, s + 1, it is not-all-equal.

*Proof.* S_s and S_{s+1} agree on two sublattices, so the triangle's colours are those of S_s except possibly on the third sublattice,
where they are those of S_{s+1}. Either way the triangle is coloured by a not-all-equal pattern. ∎

So a 1-Lipschitz labelling (adjacent labels differing by at most one) colours every triangle not-all-equal.

**Lemma 2 (vortices).** Let a point's six neighbours carry the labels 0, …, 5 in cyclic order. Whatever the point's colour, exactly one
of its six triangles is monochromatic. That triangle is a line when the labels increase counterclockwise and a face when they decrease.

*Proof.* A direct computation over the 6 rotations, 2 orientations and 2 colours (check 5). ∎

**The reading.** In label states, violated lines are counterclockwise vortices of the height and monochromatic faces are clockwise
ones. The count of `TWO-ROUND-BRIDGE-20261106-001B` (violated lines − full faces = 1) says that the vortices' net charge is fixed by the
corners. Away from vortices the states have slack: one sublattice is free in each pattern. A frozen cone is not a label state, because
its rings are monochromatic.

## What remains: the flat-state pursuit lemma

**The lemma (open).** There are constants c and ρ such that Duplicator wins the existential (c·k)-pebble game on K_k by playing label
states. She keeps:
- a single counterclockwise vortex at distance at least ρ from every pebble, in the largest component of the region at distance at
  least ρ from the pebbles;
- the six label boundaries ("strings") from the vortex to the corner structures routed through that region, crossing pebbles only
  where they are pinned;
- every pebble answered with its colour.

**What it gives.** By Atserias–Dalmau, resolution width Ω(k) = Ω(√n) for K_k. The pebble simulation of
`TWO-ROUND-BRIDGE-20261106-001B` then carries the bound to its three-fold decorations.

**What it needs.**
- Corner structures compatible with label states.
- Re-routing of strings within thick regions.
- Control of strings pinned by pebbles. A pebble fixes its label only to within three consecutive values, half the circle, so strings
  can cross it a bounded number of times.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Bulk blocking configurations | both adjacent-line classes, every r ≤ 3 |
| 2 | The frozen cone at r = 3 | reaches only 2 of 6 adjacent lines within radius 2 |
| 3 | Whole-sphere blocking states on K_8 | 6 of 6 adjacent lines at r = 2 and r = 3 |
| 4 | Random states move | all 149 pairs within radius 2 |
| 5 | Label states | two consecutive values: never monochromatic; three: 36 monochromatic cases (control); vortices as stated |

## What this does not establish

- **No width bound.** Resolution width Ω(√n) is neither proved nor refuted. Frozen states obstruct only the state-by-state argument.
- **No global label states.** Their existence on the sphere, with corner structures, is not established.
- **Larger radii.** Blocking was searched only up to radius 3. Frozen cones of larger radius presumably block larger moves.
