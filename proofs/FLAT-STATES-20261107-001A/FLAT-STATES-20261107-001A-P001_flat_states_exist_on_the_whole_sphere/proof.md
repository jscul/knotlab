# Flat states exist on the whole sphere

Status: Proved (statements 1 and 2 by hand for every k, checked for k = 2..12; statement 3's locality by hand, its existence of
re-routings checked for k = 8, 10, 12)

Ticket `FLAT-STATES-20261107-001A`, 2026-11-07.

## Standard statement

Take the not-all-equal formula of the octahedral knot sphere K_k (the Kasteleyn-signed plane cubic triple system dual to the
k-frequency octahedron; n = 4k² points). Give each point a frame, a sublattice index in Z3 and a sign gauge in Z2.
1. **Corners.** Frames moved along lines compose to nothing around every three-point face and, around each of the six two-point faces,
   to a sublattice turn plus a complement. On the six labelled colourings S0..S5 this is a shift by −1.
2. **Flat states.** Fix any point z and any six vertex-disjoint paths of the line–face graph from the six triangles around z to the six
   corner faces. Develop one frame over the sphere cut along these paths and colour every point by the label-0 pattern in its frame.
   The result violates exactly one line, and that line passes through z, whatever colour z gets.
3. **Locality.** Re-routing the cut inside a region changes colours only inside it. From a shortest cut star, the vortex steps to each
   neighbour by re-routing inside radius 3, changing at most 5 points.

## Nearest known result

- **Ideal states.** Ground states of the triangular Ising antiferromagnet carry a height function (Blöte–Hilhorst 1982). Labelled
  "ideal" states and their vortices are part of the same picture (Nienhuis–Hilhorst–Blöte 1984).
- **Disclinations.** A cone point of angle 240° turns the three-sublattice structure by a third of a turn. This is standard for lattice
  defects.
- **Classification.** known-with-delta. The delta:
  - for the Kasteleyn-signed knot sphere, the sign gauge adds a complement at each corner, and the exact holonomy is −1 at all six;
  - single-vortex flat states therefore exist on the whole sphere, with an explicit construction.

## Setting

- **Frames.** For a line l containing a and b, the move a → b shifts the sublattice by +1 or −1 (b after or before a in l's cyclic order
  in the plane embedding) and the gauge by s_a ⊕ s_b, the relative sign of a and b in l.
- **Lines become plain.** In a common frame, x_p ⊕ g_p is constant-shifted plain not-all-equal on l, and l's three points sit on three
  distinct sublattices.
- **Labels.** A point with frame (σ, g) and label λ gets colour S_λ[σ] ⊕ g, with S0..S5 = 011, 001, 101, 100, 110, 010
  (`SPHERE-COUNT-20261106-001A`).
- **Frame changes act as label shifts.** S_{s+2}[σ] = S_s[σ − 1] and S_{s+3} is the complement of S_s. So a frame change by
  sublattice d and gauge e is the label shift 2d + 3e (mod 6).

## 1. Corners

Go once around a face of the incidence graph along its boundary. Every step a → b is taken against the orientation of its line, since
adjacent faces traverse a shared edge in opposite directions.
- **Sublattice.** The shift around a face with d points is −d: zero mod 3 for three-point faces, and −2 ≡ 1 for corner faces.
- **Gauge.** The flip around the face is ⊕(s_a ⊕ s_b) over its corners. The number of agreeing corners of any assignment is
  deg F + Σ(x_a ⊕ x_b) + ⊕(s_a ⊕ s_b) ≡ deg F + flip (mod 2). It is odd for every assignment (`TWO-ROUND-BRIDGE-20261106-001B`,
  theorem 2), so flip ≡ deg F + 1: zero for three-point faces, one for corners.
- **Label holonomy.** At a corner, 2·1 + 3·1 = 5 ≡ −1 (check 1). ∎

**Sign check.** The label holonomy could only be ±1, and its sign is forced. With +1 the construction below would make z a clockwise
vortex: by `SPHERE-COUNT-20261106-001A` lemma 2 that gives a monochromatic face and no violated line, contradicting unsatisfiability.

## 2. Flat states

Let D be the sphere cut along the six paths.
- **D is a disk.** It is the complement of a tree. It contains no corner, since each path ends inside its corner face after crossing
  one of that face's two point-pair edges.
- **Development is well defined.** By statement 1, frames develop over D (z excluded) consistently: every loop in D is a product of
  three-point face loops.
- **Lines in D.** A line not cut by any path has its three points in one frame with label 0, so it is not-all-equal.
- **Lines cut by a path.** A path crossing a line leaves one of its points on the other side. A loop through the line that crosses the
  path once encircles that path's corner alone, so the far point's label in the line's chart is ±1. Labels {0, 0, ±1} are not-all-equal
  by `SPHERE-COUNT-20261106-001A` lemma 1.
- **No line is cut twice.** Paths are vertex-disjoint and visit each line at most once.
- **The lines at z.** Around z the six neighbours' labels change by the holonomy at each of the six paths, so they read 0..5 in cyclic
  order. By lemma 2 exactly one of z's triangles is monochromatic, whatever z's colour. The sign check makes it a line. ∎

Check 2 confirms this for k = 2..12: 924 states over many z and cut stars (one shortest, two random), all with exactly one violated
line, through z.

## 3. Locality

**Proof.** Let two cut stars γ, γ′ with vortices z, z′ agree outside a region B, and develop both from the same base point outside B.
- For any point p, the two frames at p differ by the holonomy of a loop from the base to p in D_γ and back in D_γ′.
- If p ∉ B, the two developing paths can be chosen to agree up to a homotopy inside B. The loop then encircles no corner, and the
  vortex charge 6 is invisible mod 6.
- So p's colour is the same in both states. ∎

**Existence (check 3).** For k = 8, 10, 12, vortices at distance ≥ 4 from the corners, and both shortest and random cut stars:
- all 360 steps to a neighbour were re-routed inside radius 3;
- each gave a valid flat state with its violated line through the new point;
- at most 5 points changed, all inside the ball.

## What this gives and does not give

- **Supplies.** The flat states that `SPHERE-COUNT-20261106-001A` lacked, on the whole sphere and for every k, with explicit local vortex
  moves. This is the first step of the pursuit lemma.
- **Does not supply.** A width bound. Pebbled colours can still pin strings, and steering the vortex through a pebbled sphere is
  `FLAT-STATES-20261107-001B`'s question.
- **Crowded stars.** Local steps were checked only from the tested stars. A cut star crowded near its vortex can block local re-routing,
  just as a frozen cone does.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Face holonomy, k = 2..12 | three-point faces trivial; all six corners (1, 1, −1) |
| 2 | Flat states, k = 2..12 | 924 of 924 violate exactly one line, through z |
| 3 | Local vortex steps, k = 8, 10, 12 | 360 of 360 re-routed inside radius 3; at most 5 points change |
