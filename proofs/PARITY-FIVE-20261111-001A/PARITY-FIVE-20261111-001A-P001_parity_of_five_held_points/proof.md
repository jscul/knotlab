# Five-input parity: exact search and learning

Status: Proved (exact, exhaustive for each space that finished; stage 1b dropped by rule; learning not run). `check.py`, ticket A of
`research/PARITY-FIVE-20261111-001/preregistration.md`, frozen with the code in commit `95e0c04c3` before any five-input search. Each part
reproduces (`check.py --part <part>` without `--write`).

## The test

For each space and class, the floor states are listed by SAT. A set of k + 1 points carries the parity of k held points exactly when its
indicator is a parity check of the floor states (orthogonal over F2 to every difference of two floor states) and the floor states'
projection onto k of its points is full. Every set of 4 points (three inputs) and 6 points (five inputs) was checked, in every class.

## Results

| Part | Spaces | Dropped | Five-input parity | Three-input parity | Time |
| --- | --- | --- | --- | --- | --- |
| harness (V1, V2) | the torus (2, 0, 4) and LEARN-PARITY's T1 run | none | not searched | (2, 0, 4), class 3 only, sets (0, 1, 4, 5), (2, 3, 6, 7) | 103 s |
| 1a search | 421 lattice tori, 3 to 24 points, 1,684 classes | none (no space over 600 s, no class over 200,000 states) | **none** | 16 tori, of 8, 12, 16 and 18 points | 122 s |
| 1b extra | 342 lattice tori, 25 to 32 points | **the whole part**, at its 60-minute cap | undecided | undecided | 60 min |
| 1c composed | K_2 with (2, 0, 4) grown at both lines, 30 points, genus 2, 16 classes | none | **none** | **none** | 51 s |
| 2 learn | not run: no five-input parity space was found | | | | |

- **V1 (harness).** The five-input harness, run with three held inputs at seed 9000, reproduced `LEARN-PARITY-20261111-001`'s first T1
  run exactly.
- **V2.** The method finds three-input parity on (2, 0, 4) in class 3 only, at the two sets found before.
- **V3.** The lattice tori up to 20 points with a three-input parity set are exactly `PARITY-NEEDS-20261111-001`'s 16. They are also the
  only ones up to 24 points: none of the 196 tori with 19 to 24 points computes even three-input parity.

## After the run (computed, not pre-registered)

`after_run.py` (43 s, `result_after.json`) lists the whole space of parity checks in every class of the one-atom memory
(`LEARN-PARITY-20261111-001`'s T2, K_2 with one (2, 0, 4) atom) and of the composed space.

- **One atom.** In every class six host points (0, 1, 2, 3, 4, 8) are tied together, 15 tied pairs: a wire. In class 1 the atom's three
  inner points 16, 19, 20 force that wire to their parity, which is why each of the six is an output of a parity set.
- **Two atoms.** In all 16 classes the space of parity checks is zero: no two points are tied, and no set of points has a fixed parity. The
  second atom unties the wire the first one used, so nothing carries the first atom's output anywhere. That is why the composed space
  computes neither five-input nor three-input parity, though each atom alone does.

## Against the pre-registration

- F failed: no five-input parity on lattice tori up to 24 points. My prediction (found, at 12 to 16 points) was wrong.
- I predicted the composed space would compute five-input parity; it computes nothing, and loses three-input parity too.
- Stage 1b was dropped by rule at its cap. My estimate (about 15 minutes) came from one class with few checks; classes with many floor
  states or many checks are slower, and the part writes its results only at the end, so the cap left nothing. That is a design fault of
  this check, not a result: 1b is undecided.
- P5 was not tested: stage 2 runs only on a found space.

## What it says

- **Exact, for lattice tori:** no lattice torus up to 24 points counts five held points; only tori of 8 to 18 points count three. This is
  not a bound: it does not show that genus 1 cannot count five, or bound the genus five needs.
- **Exact, for this composition:** growing two parity tori at the two lines of the knot sphere K_2 leaves no forced relation at all. The
  composition the pre-registration expected (genus adds, parity composes) fails at its first requirement, a wire between the atoms.
