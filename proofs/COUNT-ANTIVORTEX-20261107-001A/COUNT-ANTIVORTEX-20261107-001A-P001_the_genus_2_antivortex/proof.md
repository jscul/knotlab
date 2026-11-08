# The genus-2 antivortex

Status: Proved by hand, by composing proved reductions with new local facts. The local facts are checked by computation with controls
(`check.py`).

Ticket `COUNT-ANTIVORTEX-20261107-001A`, 2026-11-07.

## Standard statement

**The family.** Let G_a be the double of the lattice torus T = Z² / 3aZ² (`COUNT-SURFACES-20261107-001A`) along a hexagonal hole:
- remove the hexagon of side 3 around a vertex;
- glue a second copy with swapped colours along the hexagon's boundary.

G_a is a closed orientable surface of genus 2. Its knot space has n = 2(9a² − 27) points. Every face has three corners except the
hexagon's six corners, where two 240° wedges meet (degree 8): there faces have four corners. Give it its Kasteleyn signs. By
`COUNT-SURFACES-20261107-001A`, every assignment then has

  (over-agreement) − (violated lines) = Σ_v ⌊agree_v / 2⌋ − viol = 1,

so some face always over-agrees: three agreeing corners at a three-corner face, or three at a four-corner face.

**Theorem.**
1. **The face problem.** "Find an over-agreeing face" on G_a is PPADS^dt-complete.
2. **The two-sided problem.** "Find a violated line or an over-agreeing face" is PPAD^dt-complete.
3. **The lines alone** (the knot's own formula) are satisfiable on G_a, so "find a violated line" is not total there.

Together with `COUNT-TFNP-20261107-001B`:
- On the sphere (positive curvature) the knot's lines are forced to fail and finding one is PPADS-complete.
- On genus 2 (negative curvature) its faces are forced to over-agree and finding one is PPADS-complete.
- In both cases the two-sided problem is PPAD-complete. The sign of the curvature decides which side fails, and the class is the same.

## Nearest known result

- **The mirror of the sphere.** `FLAT-STATES-20261107-001A/B` and `COUNT-TFNP-20261107-001B`: on the knot sphere, flat states have one
  vortex, Sperner embeds with violated lines in counterclockwise triangles, and the count is PPADS^dt-complete.
  - FLAT-STATES-B already notes that clockwise triangles "hold a full face, an antivortex".
  - What is new here is a surface whose count forces the antivortex, and the flat state that carries it.
- **The count on surfaces.** `COUNT-SURFACES-20261107-001A`: the identity, the Kasteleyn classes, and PPADS^dt membership of the forced
  face problem.
- **Classes and reductions.**
  - SINK reduces to one-sided grid Sperner, and SOURCE.OR.SINK to two-sided (`COUNT-TFNP-20261107-001A`).
  - PPADS^dt = unary Sherali–Adams and PPAD^dt = unary Nullstellensatz (Göös, Hollender, Jain, Maystre, Pires, Robere, Tao, JACM 2024).
- **Sperner on surfaces.** Friedl–Ivanyos–Santha–Verhoeven (CIAC 2006) put Sperner problems on surfaces of non-zero genus into PPAD,
  PPADS and PPA. Here the genus enters through the count, not through a boundary.
- **Classification.** New as far as found. The method mirrors FLAT-STATES-B; the genus-2 surface, its sign class and the antivortex
  state are new.

## 1. The frames

**Lemma 1 (holonomy).** In every sign class, the frames of FLAT-STATES-20261107-001A turn as follows (check 2: 16 classes on two
sizes):
- around a three-corner face: not at all;
- around a four-corner face: by (sublattice −1, complement), which shifts labels by +1.

*Proof.*
- **Three-corner faces.** Each is a lattice hexagon of the incidence graph, flat as on the sphere.
- **Four-corner faces.** Every four-corner face has the same neighbourhood, two 240° wedges of the lattice.
  - The sublattice turns by −1: the sphere's degree-4 corners turn by +1, and a degree-8 vertex has the opposite angle excess.
  - The Kasteleyn parity (four corners, odd) adds a complement.
- **Class independence.** A change of class adds a cocycle, whose flip is even at every face. ∎

**Lemma 2 (the handles).** Let the cut star stay in a chart of the first sheet: a disk holding the region and the hole. Then exactly
one Kasteleyn class makes the frames consistent on the surface cut along the star (check 4: one of 16, for m = 3 and 5).

*Proof.*
- **The open loops.** Up to homotopy in the surface minus the four-corner faces, every loop avoiding the star is a product of:
  - the two torus loops of each sheet, which lie outside the chart;
  - loops around the seam, which encircle all six four-corner faces or none.
- **Seam loops.** These encircle all six four-corner faces and turn by 6 × (sublattice −1, complement) = (0, 0).
- **Sublattice.** The torus loops are translations by vectors of 3aZ², which keep the sublattice index (i − j) mod 3. So their sublattice
  turn is 0.
- **Gauge.** The classes form a torsor over H¹(G; F2) ≅ F2⁴, and a change of class by φ changes each loop's gauge bit by φ(loop). So
  exactly one class makes all four flat.
- **Control.** For a torus whose lattice does not lie in L3 = {i ≡ j mod 3} (25 × 25), no class works: the handles turn the sublattice
  (check 7). ∎

## 2. The antivortex

**Lemma 3 (the flat state).** Develop label 0 over the surface cut along six disjoint paths, from the triangles around a point z to the
six four-corner faces. The resulting assignment violates no line and over-agrees at exactly one face, a face at z, whichever colour z
gets (check 4).

*Proof.*
- **Jumps.** Across each cut path the label jumps by the holonomy of its end face, +1 (Lemma 1).
- **Away from z.** Every line and every three-corner face sees labels within two consecutive values. In a common frame its three points
  lie on the three sublattices. The six patterns S0..S5 then make it never monochromatic (local lemma, check 3: all 48 cases).
- **Four-corner faces.** They have one neighbourhood type, so one finite check covers them: agreement 1 (check 4).
- **At z.** Its neighbours carry the six labels in the reverse cyclic order, an antivortex. The finite check gives no violated line and
  one over-agreeing face, for both colours of z (check 4). ∎

**Corollary.** The lines alone are satisfiable (statement 3), and the face problem is total (check 6: the identity on 40 assignments).

## 3. The reduction

**Construction.**
- **The family.** Take a = ⌈(2m + 22)/3⌉, the hole centred at (2m + 12, 2m + 12), and FLAT-STATES-B's region R of side 2m at (5, 5) in
  the first sheet. The Sperner map Φ is FLAT-STATES-B's:
  - doubled labels (2c at coarse vertices, halfway at midpoints) in frames developed over R;
  - the fixed antivortex state outside R.
- **The star.** It leaves R through FLAT-STATES-B's three crossing pairs:
  - the head inside R is FLAT-STATES-B's;
  - six disjoint tails run in the chart from the crossing pairs to the six four-corner faces.

  The tails exist by Menger's theorem. In the planar chart outside R, separating the six crossings from the six faces needs a curve
  around R or around the hexagon, which meets at least six vertices.

**Lemma 4 (the boundary).** R's boundary carries the canonical Sperner boundary with colours 1 and 2 swapped:
- corners (0, 0), (m, 0), (0, m) coloured 0, 2, 1;
- each side takes its far corner's colour after its first vertex.

Checked for m = 3..7 (check 5). No colour shift appears, unlike the sphere's −m (mod 3) in COUNT-TFNP-20261107-001B.

*Proof.*
- The labels on ∂R come from the antivortex state: two jumps of +1 at each corner of R.
- So each side is monochromatic, and the colour rises by one at each corner going clockwise. That is the canonical boundary with its
  orientation reversed, i.e. with 1 and 2 swapped. ∎

**Lemma 5 (defects).** In Φ(c):
- the over-agreeing faces lie exactly one in each clockwise fully labelled triangle of c;
- the violated lines lie exactly one in each counterclockwise one;
- there are none outside R;
- every point reads at most two Sperner colours.

*Proof.*
- Inside R this is FLAT-STATES-B's local lemma (statement 1), which is local, and R lies in a flat lattice part of the first sheet.
- Outside R it is Lemma 3.
- Check 5 confirms it on 80 colourings for m = 3..7 (116 counterclockwise and 196 clockwise triangles, each holding its one defect) and
  that the clockwise count minus the counterclockwise count is 1. ∎

**Proof of the theorem.**
- **(1) Membership.** COUNT-SURFACES-20261107-001A's identity is a unary Sherali–Adams refutation of the face constraints of degree 4,
  so the face problem is in PPADS^dt.
- **(1) Hardness.** Compose three steps:
  - SINK → canonical one-sided Sperner_m (COUNT-TFNP-20261107-001A);
  - swap colours 1 and 2: the boundary becomes Lemma 4's, and the positive (0, 1, 2 counterclockwise) triangles become exactly the
    clockwise full triangles;
  - Φ.

  An over-agreeing face names its clockwise triangle by position (Lemma 5). The composition has depth O(log N), into n = O(m²).
- **(2)** The same steps from SOURCE.OR.SINK and two-sided Sperner give both orientations as solutions, so the two-sided problem is
  PPAD^dt-hard. The identity, with line and face constraints as axioms, is a Nullstellensatz refutation with multipliers ±1, so it is in
  PPAD^dt.
- **(3)** Lemma 3. ∎

## Checks

`check.py` (`result.json`), about 2 minutes:

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Five doubles (a = 3..12, hole side 1..4) | closed, orientable, χ = −2, six four-corner faces, the rest three-corner, simple |
| 2 | Face holonomy in all 16 classes, two sizes | three-corner faces (0, 0, 0); four-corner faces (2, 1): label +1 |
| 3 | Local lemma | never monochromatic in all 48 cases |
| 4 | Classes and the flat state, m = 3, 5 | exactly one class consistent; no violated line, one over-agreeing face at z, for either colour of z |
| 5 | The reduction, m = 3..7, 80 colourings | boundary = swapped canonical; defects exactly in the full triangles of the stated orientation; reads ≤ 2 colours |
| 6 | The count | over-agreement − violated lines = 1 on 40 assignments |
| 7 | Controls | L outside L3: no class develops; counting lines against clockwise triangles fails; the unswapped boundary differs |

## Reading

**Interpretation, not a theorem.**
- **The mirror.** The knot sphere and the genus-2 double are mirror images for the count:
  - six faces of positive curvature (two corners, holonomy −1) force a vortex on a line;
  - six faces of negative curvature (four corners, holonomy +1) force an antivortex on a face.
- **The class.** Finding the forced defect is PPADS-complete either way. Orientation decides only which kind of defect the clauses see,
  not the class.
- **On genus 2 the knot is coherent:** its lines can all hold. What fails is the faces' closure, and the place where it fails is as hard
  to find as the sphere's violated line.

## What this does not establish

- **Other negatively curved spaces.** Only the doubled holed tori with lattice L ⊆ L3 are classified. Other genus-2 spaces, higher genus
  (several antivortices) and hyperbolic lattices are not treated.
- **Circuit TFNP.** The white-box version is not written out.
- **Concrete bounds.** No explicit Nullstellensatz degree bounds are claimed beyond the qualitative separations that follow from the
  classification.
