# Exact genera and minimal maps by SAT

Status: Proved

Ticket `THREEFOLD-SURFACES-20261030-001B`, 2026-10-30.

**What it uses:**
- `THREEFOLD-SURFACES-20261030-001A`: the splice lemma, the genus formula, the structure and count of minimal maps, and the library.
- `THREEFOLD-GRAMMAR-20261030-001B`: the census of cores and the decoration that lists every three-fold space up to 22 points
  (8 untwisted and 24 twisted classes).
- `THREEFOLD-GRAMMAR-20261030-001A` and `THREEFOLD-SPACES-20261030-001A`: libraries.

## Why this ticket exists

Ticket A proves that the incidence graph of a three-fold space has genus equal to its number of Fano atoms (plus the genus of rigid
non-planar glue). It also proves that its minimal maps are connected sums of Heawood maps. This ticket measures both directly, by exact
computation, on every small space and on large ones. It is an independent check, since nothing here uses ticket A's proof.

## Standard statement

**Method.**
- **Genus by SAT.** For a cubic graph and a number F, a SAT model asks for a rotation system (one bit per vertex) and a labelling of the
  edge-ends by F face labels. Every label must be used, and labels must be constant along face tracing. It is satisfiable iff some
  rotation system has at least F faces.
- **Exact genus.** The genus is the least g for which F = E − V + 2 − 2g is satisfiable. A lower bound is proved by unsatisfiability one
  step below.
- **Minimal maps.** All minimum-genus rotation systems are enumerated with blocking clauses on the rotation bits.

**Results.**
- **(1) Every space up to 22 points.** For the 8 untwisted and 24 twisted classes, the genus equals the sum of the braces' genera.
  - That is the number of Heawood braces in every class but one.
  - The exception is a twisted 22-point class whose glue is the trisum of three cubes: 2 Heawood braces, genus 3.
  - Untwisted genera: 1, 2, 3, 3, 3, 3, 3, 3.
- **(2) Larger spaces.** The genus equals the number of Heawood braces, plus one where the glue is the trisum of three cubes:

  | Space | Points | Genus |
  |---|---|---|
  | Fano compositions of four and five planes | 25, 31 | 4, 5 |
  | Cycles of five and seven Fano blocks | 35, 49 | 5, 7 |
  | Twisted cube | 43 | 6 |
  | Hexagonal prism as glue | 45 | 6 |
  | Truncated octahedron as glue | 90 (180 vertices) | 12 |
  | Trisum of three cubes as glue | 35 | 5 = 4 atoms + 1 |
- **(3) Minimal maps up to 19 points.**
  - The spaces with 7 and 13 points, and each of the four 19-point classes, have exactly 16, 128 and 1024 minimum-genus rotation systems.
    This is 16^h / 2^(h − 1), ticket A's formula.
  - Every one is a standard connected sum at every tight cut: the two transitions are inverse 3-cycles.
  - Up to automorphisms and mirroring there are 1, 2, and (for the four 19-point classes) 3, 4, 4 and 6 minimal maps.
  - Face profiles:
    - Fano: 7 hexagons;
    - 13 points: 8 hexagons and 3 decagons;
    - 19 points: 10 hexagons, 4 decagons and a 14-gon; or 11 hexagons, 2 decagons and two 14-gons; or 9 hexagons and 6 decagons.

  At 21 and 22 points, ticket A's formula predicts 4096 and 8192 minimal rotation systems. These were not enumerated.
- **(4) Additivity beyond the Heawood graph.**
  - The trisum of three cubes and the Petersen graph keep their genus 1 when a vertex is deleted, and they splice additively, with the
    cube, the Heawood graph, K₃,₃ and each other.
  - K₃,₃ loses its genus when a vertex is deleted, and K₃,₃ spliced with K₃,₃ has genus 1 instead of 2.
  - One rigid side suffices: K₃,₃ spliced with the Petersen graph has genus 2.

## Nearest known result

- **Ticket A** proves (1)–(4) in general. This ticket confirms them by computation.
- **The SAT approach to minimum genus** follows, in spirit, Beyer, Chimani, Hedtke and Kotrbčík's SAT and ILP formulations.
- No overlap found for the values.

## Proof

- **Soundness of the model.**
  - Each edge-end receives exactly one label.
  - Labels propagate along the tracing map chosen by the rotation bits, so each face is constant.
  - Every label is used, so there are at least F faces.
  - Conversely, a rotation system with at least F faces labels its faces with the F labels, merging extra faces into one label. The
    labels' order of first appearance breaks the symmetry between them.
  - Fixing the first vertex's bit loses nothing, because mirroring flips every bit and preserves the genus.
- **What is computed.** The genus values, the enumerations and the cut transitions are computed by `check.py`. Section 1 rebuilds the
  32 classes from the census exactly as ticket B of the grammar epic does.
- **Pass conditions.** Each claim above is a check that must pass.
- **Orbits.** They are canonical forms under all graph automorphisms and mirroring. ∎

## What the computation checks

`check.py` (about 12 minutes; the 180-vertex space takes most of it):
- the 32 classes;
- the nine larger spaces;
- the enumeration and classification of minimal maps of six spaces;
- the additivity tests;
- controls:
  - the SAT bound below the genus is unsatisfiable for the 13-point space;
  - a random rotation system exceeds the minimum;
  - the cube and the Heawood graph have genus 0 and 1.

## Reading

- **The handles can be counted.** The formula holds on every small space and on spaces with up to 180 vertices. Each Fano atom is one
  handle and each doubled square or planar glue piece adds none. The one non-planar glue piece found, the trisum of three cubes, adds one
  handle of its own: in the 35-point space and in a twisted 22-point class.
- **The minimal maps are few and rigid.**
  - Each space has finitely many minimal maps, and every one is assembled from Heawood maps at the tight cuts. No minimal map uses any
    other way of crossing a cut.
  - Their number up to symmetry grows only with the choices of handedness and attachment at each atom.

## Nonclaims

- **Counts at 21 and 22 points** are predictions of ticket A, not enumerations.
- **Twisted spaces** are reported for genus only.
- **Only the listed spaces** are computed.
