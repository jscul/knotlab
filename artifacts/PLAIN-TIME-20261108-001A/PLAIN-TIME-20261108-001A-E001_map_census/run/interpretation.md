# When the plain first need is on time: interpretation

Experiment `PLAIN-TIME-20261108-001A-E001` (exploratory), run once on 2026-11-08 under the frozen contract, in 87 s on 16 workers.
Exact: route counts by breadth-first search, least odd walk lengths by rows mod 2 to their span. Every row is in `result.json`.

## Control

The pilot: the group construction agrees with `distance_lib.regular_map` read through `loopnet_lib` on every map of A4 and S4, and every
target contact gives the same readings on tori of index at most 13, loops and two rings sharing up to 8 contacts. No row of the run has
a cone mismatch (a ring on time without an odd count, or the reverse).

## Primary observable

| Family | Distinct maps | On time |
| --- | --- | --- |
| Regular maps of genus 0 (the five Platonic networks, loops and two rings sharing contacts from the dihedral groups) | 61 | 61 |
| Loops of 2 to 60 rings, two rings sharing 2 to 60 contacts | 118 | 118 |
| Tori {4,4}, {3,6}, {6,3} | 344 | 24 |
| Regular maps of genus 2 to 2,430, from 18 groups (1,620 generating pairs up to the centraliser, merged by readings) | 706 | 141 |

- **The smallest failing maps.** Among the roster's tori (one chirality each), {4,4}_(4,0) (16 rings, never pairs at the antipode,
  `LATTICE-NET-20261108-001A`) and {4,4}_(4,1) (17 rings, late at distance 4). The roster missed a smaller one: the mirror image of the
  on-time {4,4}_(3,2), the 13-ring {4,4}_(2,3), is late (ticket B, check 6). Among maps of higher genus, the map of S5 = PGL(2,5) with six contacts per ring and square
  faces, of genus 6 and 20 rings: four rings late for each contact, at distances 5 and 6, each with its single closest contact reached
  by two shortest routes.
- **Large maps on time.** The largest on time is a map of PSL(2,29) with 29 contacts per ring and faces of 15, genus 2,430, 420 rings.

## Reading against the decision rule

- **H1 is refuted.** 258 maps are on time although some contact has two or more shortest routes: a ring is rescued whenever one of its
  closest contacts receives an odd number.
- **H2 is refuted.** 565 maps of genus at least 2 are late, from the 20-ring map of S5 on. Every map of genus 0 is on time, and tori
  are on time only at small sizes (largest on time: 13 rings square, 21 triangular, 18 honeycomb). So curvature alone does not decide;
  the follow-up (ticket B) reads the universal covers.

## Deviations, recorded

- **Triangular tori.** `plain_lib.lattice_torus` builds {3,6}_(b,c) in a basis whose index is b² − bc + c², not b² + bc + c² as the
  contract says, so the roster's triangular shapes are a different sample of the same family, and it included the degenerate torus
  (1,1) with one ring whose contacts join it to itself, which the contract's rule excludes. That row is left out of the table above.
  Ticket B rereads every torus of every shape and both chiralities up to its index bounds, so no conclusion rests on the roster's sample.
- **Chirality.** The roster took one of each pair of mirror-image tori (c ≤ b). Mirror images can differ, since the contact graph is
  directed: the triangular torus of index 19 is on time and its mirror image is late. Ticket B reads both.

## Nonclaims

- **Exploratory and finite:** the roster only; regular maps, tori and loops only.
- **Two-time knots only** (A30).
