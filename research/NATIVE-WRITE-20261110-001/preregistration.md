# Pre-registration: native writing

Epic `NATIVE-WRITE-20261110-001` (backlog B119, G15), written on 2026-11-10 before any run on the test spaces, at the coordinator's
go-ahead. The learner, its information, the marks and the test set are frozen here, with the code in
`proofs/NATIVE-WRITE-20261110-001A/NATIVE-WRITE-20261110-001A-P001_native_writing/` (`write_lib.py`, `check.py`) and
`proofs/NATIVE-WRITE-20261110-001B/NATIVE-WRITE-20261110-001B-P001_one_size_past/check.py`, committed with this file.

## The question

Every address in the learning line was written by a targeted search that is told the target configuration, an outside map, and that
stops when every named atom holds a unit, so it can stop with a unit in an atom that does not act (the inexact writes of
`NEST-ATOMS-20261110-001` and `MANY-POINTS-20261110-001`). Can a learner that sees only its own dissonance and the address it is asked
for write addresses into the layered memory, exactly?

## Not blind

The learner was developed on the dev spaces only (the outer host K_2 with two composites C(2, thin) or C(2, Fano), the spaces of
`NEST-ATOMS-20261110-001C`), in scratch runs: a learner with the bias alone (no attention) stopped exactly every time it stopped (22 of
22) but needed up to six million steps; the attention rule below wrote 72 of 72 dev addresses exactly and held them, in at most 52,000
steps; with the probe replaced by an instant check, 28 of 30 dev writes were inexact stops. No run has touched S1 to S5.

## What the learner may use (frozen)

- **Its own dissonance:** which lines are violated, how many corners agree at each face, W (A49), and the change in W of each of its own
  moves (A47).
- **The floor** |χ|, a count of its own points, lines and faces.
- **The address asked for:** a bit per atom, each atom given by its region, its lines and every face they touch (lemma 3 of
  `OTHER-ATOMS-20261110-001A`: interior and junction faces). Read as an assumption, A57.
- **Its own moves:** state flips of any point; sign changes only where dissonance shows (A21: at a violated line, or on an edge ending at
  an even face).

It never reads a role, a class, a solver's answer, a target configuration or a distance to one. Roles are read by SAT only afterwards,
to score.

## The learner (frozen in `write_lib.py`)

- **Probe.** Its test of its own memory: on a copy, 20,000 steps of a state-only walk on the floor plateau (a random point flipped when W
  does not rise), no bias. An atom asked 1 fails if its region is ever free of dissonance (no violated atom line, every region face odd
  and agreeing at fewer than two corners); an atom asked 0 fails if its region is never free of it.
- **Attention.** The atoms the last probe failed are hot. Sign changes are allowed only on hot atoms' lines.
- **Moves.** Proposed at random: a state flip of a random point (probability 1/2) or a sign change at a random A21 site. Accepted by the
  Metropolis rule on φ = W + λ·(dissonance outside the regions of atoms asked 1), at temperature 2.0 when the move touches a hot atom's
  line and 0.7 otherwise, never above floor + 4 (the old search's envelope); λ = 1.
- **Stop.** Every 200 steps at the floor it probes; it stops when nothing is hot. Budget: 2,000,000 steps per write (probe steps not
  counted; reported separately).

This uses A50's alternative (state flips at a temperature) while writing; the probe itself is A50's walk.

## What is proved before any run (by hand)

- **P1.** An atom that acts has dissonance in its region in every state (lemma 3 of `OTHER-ATOMS-20261110-001A`: in every state
  satisfying the atom's lines some region face has at least two agreeing corners; otherwise an atom line is violated). So the probe never
  fails an acting atom asked 1, and an atom asked 0 whose region the probe clears is transparent: the probe does not change signs.
- **P2.** An atom's role depends only on its own lines' signs, and learning changes only hot atoms' signs, so a write never changes an
  atom the last probe found met.
- **Consequence.** At a stop, every atom asked 0 is transparent. An inexact stop can only be an atom asked 1 that does not act and whose
  dissonance stayed in its region for 20,000 probe steps.

## Ticket A: the frozen test

- **Census (exact).** On every class of the dev spaces and S1 to S4: an atom acts exactly when its own constraints (its lines satisfied,
  each region face agreeing at exactly one corner) cannot hold together. The writable addresses are those of classes with a floor state.
- **Test spaces.** S1: K_3 with thin leaves at its first line and the first lines at distances 2 and 3. S2: the same with Fano leaves.
  S3: the outer host K_3 with composites C(2, thin) at its first line and its farthest line. S4: the same with C(2, Fano). Each run starts
  in the first class where no atom acts, at the solver's first satisfying state, relaxed by M1.
- **Writes.** 20 per space, each target drawn uniformly from the space's writable addresses other than the last (sequence seed 119 + k,
  learner seed 1190 + k for S_k). After each stopped write one random point of the outermost host is flipped and M1 (ADDRESS-STEER's
  learner) runs to the floor; the write is held if the acting set is then the target. The sequences (atoms listed, "-" the empty
  address):
  - S1: 12 0 01 2 12 1 2 02 - 02 0 01 02 2 01 02 2 0 - 2
  - S2: 0 01 12 02 2 0 12 1 0 02 01 0 2 02 - 2 12 1 02 0
  - S3: 12 012 123 3 013 0 2 02 23 012 1 3 123 2 12 01 0 02 1 2
  - S4: 0 02 0 23 023 013 0 3 23 - 03 12 1 02 023 3 - 012 01 023
- **Outcomes, each counted on its own:** exact and held; exact, not held; inexact stop; not stopped within the budget.
- **Control U.** The same learner, sequences and seeds with the probe replaced by an instant check (the same test read once, no walk).

## Ticket B: one size past (stress test)

S5: the outer host K_3 with three composites C(2, thin) at its first line and the first lines at distance 2 and the farthest (six atoms,
genus 6, 4,096 classes, 63 writable addresses): the census, and 20 writes (sequence seed 124, learner seed 1195), with control U. Its
sequence: 5 02 12345 - 01345 45 5 012 0345 02 2345 0245 01 0235 013 034 5 0234 24 034. If it runs past ten minutes it is registered in
`docs/LONG_RUNNING.md` and may be pending at the close.

## Marks (decisive, one line each)

- **Native writing holds on a space** iff at least 18 of its 20 writes are exact and held. **B119 is answered yes** iff it holds on all of
  S1 to S4, and **no** otherwise; there is no in-between. Inexact stops count against the 18 and are reported on their own.
- **R (the probe's reliability):** no inexact stop among the 80 test writes.
- **U:** the control makes inexact stops on at least a quarter of its 80 writes (20).
- **Census:** the region lemma holds on every class of the six spaces.
- **S5** (stress test): the same 18-of-20 mark.

## Predictions

Native writing holds on all four spaces (B119: yes); R holds; U holds; the census holds; S5 holds. If B119 is answered no, the report
says which outcome kept a space below 18: not stopped (this learner cannot find the class in its budget), not held (a written address
does not survive its disturbance), or inexact (the probe is fooled).

## Stop rule (one epic)

One frozen test. A no is reported as the answer for this learner, with the outcome that caused it; a fix is a new pre-registration.

Assumptions in force: A20, A21, A46, A47, A49, A50 (its alternative while writing), A52, and A57 (added with this file). Ticket A is
expected to take under ten minutes.
