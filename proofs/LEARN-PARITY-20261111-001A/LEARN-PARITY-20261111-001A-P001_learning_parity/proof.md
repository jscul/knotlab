# Learning parity on a torus and in a memory

Status: Proved (exact realizability; learning computed, frozen). `check.py` (about two and a half minutes, twenty runs in parallel),
ticket A of `research/LEARN-PARITY-20261111-001/preregistration.md`, frozen with the code in commit `00aafe7f6` before any learning run.
It reproduces.

## The test

The credit learner of `CREDIT-PIN-20261110-001B` with the three-input sturdier probe of `THREE-IN-20261110-001B`, unchanged, budget 8,000,000
steps per target, ten runs on each of two spaces: T1, the bare 8-point lattice torus (2, 0, 4), interface inputs 0, 1, 4 and output 5; T2, a
memory, the knot sphere K_2 with the torus (2, 0, 4) less a point grown as an atom at its first line (23 points, genus 1), interface inputs
16, 19, 20 inside the atom and output 0, a side of the atom. Targets in turn: parity `01101001`, its negation `10010110`, parity again. After
each stop one random point off the interface (in T2, a point of the host sphere) was flipped, M1 ran to the floor, and the map was read
again by SAT.

## Results

- **Check 1 (exact).** Parity is realizable at both interfaces, each in one of its four classes (T1: maps `0x1010x1`, `u00uu11u`,
  `xx0101xx`, `01101001`; T2: `uu1010uu`, `01101001`, `x11xx00x`, `011xx001`).
- **Check 2 (computed, frozen).**

| Space | Parity (first target) learned and held | All writes learned and held | Inexact stops | Median steps, first target (all writes) |
| --- | --- | --- | --- | --- |
| T1, the bare torus | 10 of 10 | 30 of 30 | 0 | 13,400 (9,900) |
| T2, the torus inside a memory | 10 of 10 | 30 of 30 | 0 | 18,000 (12,500) |

The longest write took 75,600 steps.

## Against the pre-registration

R, P1 and P2 held, and no stop was inexact, as predicted.

## What it says

A learner that sees only its own dissonance under the world's clamps learned the parity of three held points from its eight examples, held
it after a disturbance, switched it to its negation and back, every time, on a bare torus and inside a memory. It is the first learned map
that is not unate. Theorem D (self-duality) and theorem M (monotone readings of stored classes) are not crossed: parity is self-dual, and as
a function of the stored class it is a gate, present in the torus's most constrained class alone.
