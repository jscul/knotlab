# Searching for a non-unate map of held points

Status: Proved (exact searches; every instance re-read independently). `check.py` (about six minutes), ticket A of
`research/UNATE-20261111-001/preregistration.md`, frozen in commit `ca98cab51` before the searches ran; one job dropped as infeasible
before any result was read (deviation, commit `771a8f5bf`).

## Answer

**No: maps of held points are not unate in every knot space.** An 8-point knot space of genus 4 computes the parity of three held points
exactly: with points 0, 3 and 4 held, point 5 is decided at every input pattern and equals their sum mod 2.

## The gadget (exact, three independent readings)

Random knot space n = 8, seed 35 (8 points, 8 lines, 2 faces, genus 4), in its class 123 of 256, a Kasteleyn law (no even face). Its
lines, as point triples with signs: (0,4,6) 010, (1,2,4) 110, (6,5,7) 100, (0,4,7) 000, (1,2,0) 100, (3,5,1) 100, (7,3,6) 010,
(5,3,2) 000.

- Brute force over all 256 states: exactly 8 satisfy every line.
- The dissonance engine of `NATIVE-WRITE-20261110-001A` on all 256 states: W takes the values 6 (8 states), 10, 14, 18 and 22, and the 8
  floor states (W = |χ| = 6) are the satisfying ones.
- On points (0, 3, 4, 5) the floor states are exactly the eight patterns of even weight: point 5 = point 0 ⊕ point 3 ⊕ point 4. A SAT
  re-read of the map gives `01101001`, the same.

Another parity map occurs in a 12-point space of genus 6 (seed 54, class 786; inputs 3, 5, 6, output 7; `10010110`).

## Counts (exact)

| Search | Maps read | Parity | Majority | Other non-unate | Dictator |
| --- | --- | --- | --- | --- | --- |
| Census, T1 (radius 1, 256 classes) | 564,224 | 0 | 0 | 0 | 0 |
| Census, T3 (radius 1, 256 classes) | 779,264 | 0 | 0 | 0 | 0 |
| Random spaces, n = 6 (200 spaces, genus 1 to 3) | 579,120 | 0 | 7,200 | 0 | 16,262 |
| Random spaces, n = 8 (199 spaces, genus 2 to 4) | 9,115,400 | 16 | 48,509 | 0 | 199,996 |
| Random spaces, n = 10 (200 spaces, genus 3 to 5) | 96,552,120 | 0 | 107,206 | 0 | 1,295,060 |
| Random spaces, n = 12 (200 spaces, genus 4 to 6) | 922,521,600 | 4 | 144,536 | 0 | 4,189,636 |

One n = 8 space was disconnected and skipped. Every map is self-dual (theorem D). The only non-unate maps found are total parity maps; no
partial non-unate map occurs.

## What it says

Unateness is not a property of knot spaces: small knot spaces with many handles for their size compute majority often and parity
rarely. It is a property of the learned memories' interfaces, where every map read so far (`THREE-IN-20261110-001` and these censuses) is
unate. The gadgets found have only two faces: every handle the surface can hold.
