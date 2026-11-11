# Pre-registration: a learned memory that computes parity

Epic `LEARN-PARITY-20261111-001` (sub-goal B146, G15 with G16), written on 2026-11-11 before any learning run, at the coordinator's
go-ahead. The learner, probe, budget and marks are frozen here with the code in
`proofs/LEARN-PARITY-20261111-001A/LEARN-PARITY-20261111-001A-P001_learning_parity/` (`parity_lib.py`, `check.py`). If the learner needs a
change, this epic closes on the unchanged learner and the change is proposed as the next epic.

## The question

`PARITY-NEEDS-20261111-001` found that the 8-point lattice torus (2, 0, 4), in its most constrained class, computes the parity of three held
points. Can a learner that sees only its own dissonance under the world's clamps, with no outside map, learn that map from its eight
examples and hold it, on the bare torus and inside a memory?

## How a learned parity map squares with what is proved

- **Theorem D (self-duality) is not crossed.** Parity of three inputs is self-dual: flipping all three inputs flips the output. It is one
  of the maps theorem D allows.
- **Theorem M is not crossed.** Theorem M bounds readings of *stored classes*: as a function of which atoms act, a reading is monotone.
  Here the inputs are values of points the world holds, which supply a frame from outside; theorem M says nothing about them. As a function
  of the stored class the parity map is a gate: present in one class (the torus's most constrained) and absent in the others, which is
  consistent with M.
- **What would be crossed is an observation, not a theorem.** Every map learned so far, and every map read at the learned memories'
  interfaces (`THREE-IN-20261110-001`, `UNATE-20261111-001`), was unate. A learned parity map would be the first learned non-unate map.
- **A difference to state.** Earlier interfaces were an atom's three sides; here the held points are inside the torus, which is where
  parity is realizable.

## The spaces (structure checked before freezing; no learning run)

- **T1:** the bare torus (2, 0, 4): 8 points, genus 1. Interface: inputs 0, 1, 4 held, output 5 (parity in its most constrained class).
- **T2 (a memory):** the knot sphere K_2 with the torus (2, 0, 4), less a point, grown as an atom at its first line: 23 points, genus 1.
  Interface: inputs 16, 19, 20 held (points inside the atom), output 0 (a side of the atom). A structure check (SAT over its four classes,
  no learning) showed parity realizable there; check 1 repeats it exactly.
- Start: the base Kasteleyn law (no class added) at the solver's first satisfying state, relaxed by M1. The starting maps are not parity
  (T1 `0x1010x1`, T2 `uu1010uu`).

## The learner (frozen, unchanged)

`CREDIT-PIN-20261110-001B`'s credit learner with `THREE-IN-20261110-001B`'s three-input sturdier probe (positive checks one 4,000-step
walk; each negative check four 25,000-step walks, three from fresh states), attention widening from the interface lines. Budget
8,000,000 steps per target. Ten runs per space, learner seed 9000 + k. Targets in turn: parity `01101001`, its negation `10010110`, and
parity again. After each stop, one random point outside the interface (T2: a point of the host sphere) is flipped and M1 runs to the
floor; every map is read by SAT.

## Marks (decisive, one line each)

- **R (exact):** parity is realizable at each interface (check 1).
- **P1:** on T1, parity (the first target) is learned and held in at least 8 of 10 runs.
- **P2:** on T2, the same.
- Reported: the other targets, inexact stops, steps. No mark is settled by its own definition: R is computed, and P1 and P2 are runs.

## Predictions

R, P1 and P2 hold; no inexact stop. If P2 fails, the report says what stopped the learner (never reaching the class, reaching it in the wrong
frame, or not holding it).

## Stop

A learned parity map that holds after disturbance, or a clear statement of what stops the learner; then report and hold.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58. The run takes more than ten minutes, is registered in
`docs/LONG_RUNNING.md`, and has a wall-clock cap of 90 minutes set now (systemd); over the cap it is dropped by rule.
