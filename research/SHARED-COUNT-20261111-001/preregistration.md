# Pre-registration: counting through a shared distinction

Epic `SHARED-COUNT-20261111-001` (sub-goal B148, re-posed without the two-fold restriction; G15 with G16; program learning), written on
2026-11-11 before any run, at the coordinator's go-ahead after the owner lifted the pause and set the direction: bases where knots overlap
freely, a knot meeting any number of others, not only the two-fold weaves the record has studied. The spaces, the learner, the marks and
the caps are frozen here with the code in
`proofs/SHARED-COUNT-20261111-001A/SHARED-COUNT-20261111-001A-P001_counting_through_a_shared_distinction/` (`join_lib.py`, `check.py`).
Nothing is tuned after a result is read.

## The question

Do overlapping bases compute or learn what two-fold weaves cannot? `PARITY-FIVE-20261111-001` found that two counting copies grown on the
zero-pair weave K_2 count nothing, because the second copy unties the six distinctions the first one's count is carried on, and that no
lattice one-pair weave with up to 24 distinctions counts five held distinctions. Here the copies are joined the way an overlapping base
allows and a two-fold weave does not: the read distinction of one copy *is* an input distinction of the next, one distinction shared by
identity. Does the joined base count five (and seven) held distinctions, and does the unchanged learner learn it from examples?

## Words

Following lesson 1.1's language rule. A **copy** is the 8-distinction, 8-knot two-fold weave (2, 0, 4) (drawn as a torus; a lattice
one-pair weave), whose tightest class of law forces distinction 5 to the sum mod 2 of distinctions 0, 1 and 4 (`PARITY-NEEDS-20261111-001`).
**Closed tours** are what the drawing calls faces. **Counting** k held distinctions means a read distinction forced to their sum mod 2.

## What is known, and what this test settles by its own definition

- **Classical: every self-dual map is computed by some base.** A not-all-equal knot on signed distinctions, with hidden distinctions
  allowed, defines exactly the relations closed under flipping every distinction: not-all-equal is a base of that co-clone (Post's
  lattice, through the Galois connection of Geiger 1968 and Bodnarčuk, Kalužnin, Kotov and Romov 1969; the table of bases in Böhler,
  Reith, Schnoor and Vollmer 2005). With theorem D of `IN-OUT-20261110-001`, the maps of held distinctions on unrestricted finite bases are
  exactly the self-dual maps. So *which maps* an overlapping base can compute is settled by known results, not by this epic.
- **Settled by definition: the joined bases count.** Joining two counting relations by one shared distinction gives the count of all
  their other inputs (x5 = x0 + x1 + x4 and y5 = x5 + y1 + y4 give y5 = x0 + x1 + x4 + y1 + y4). So J2 counts five held distinctions and J3
  seven when every copy is in its tightest class. Check R confirms it exactly and lists the class combinations where it holds; it can fail
  only through a bug.
- **Known, flat.** The same two copies grown on K_2 count nothing; no lattice one-pair weave with up to 24 distinctions counts five
  (`PARITY-FIVE-20261111-001`, exact). J2 counts five with 15 distinctions.
- **Learning, prior work.** Learning from clamped examples by local rules is known in Boltzmann machines (Ackley, Hinton and Sejnowski
  1985) and in physical networks (coupled learning, Stern, Hexner, Rocks and Liu 2021; a later nonlinear electrical network of that kind is
  reported to learn XOR). Parity is the classical hard case for local and statistical learners (a parity of many inputs is not learnable from statistical
  queries, Kearns 1998; our learner sees each example exactly, so that bound does not apply directly). I found no work on a learner of
  this kind, one that changes the signs of its own knots where it feels dissonance, learning a parity of five or seven inputs.
- **Not settled by definition: learning.** Whether the unchanged learner, seeing only its own dissonance under the world's clamps, puts
  every copy into its tightest class and holds the count is a run, P5 and P7 below.

## The bases (structure checked before freezing; no class combination read, no learning run)

- **J1 (control):** one copy, exactly `LEARN-PARITY-20261111-001`'s T1.
- **J2:** two copies; copy 1's read distinction 5 is copy 2's input 0. 15 distinctions, 16 knots, 16 closed tours. Inputs 0, 1, 4 (copy 1)
  and 8, 11 (copy 2), read 12; the shared distinction 5 lies in six knots and is never held or read.
- **J3:** three copies in a chain. 22 distinctions, 24 knots. Inputs 0, 1, 4, 8, 11, 15, 18, read 19; shared distinctions 5 and 12.
- The engine counts distinctions and knots with one number, so J2 and J3 are padded with one and two inert distinctions in no knot,
  never held, read or disturbed. The dissonance is the sum of the copies' own (each copy keeps its closed tours, A66), so the floor is 0
  and the floor states are the states satisfying every knot. The start is every copy's base law at the solver's first satisfying state,
  relaxed by M1; the starting maps are not the count (J2 `0x10xxxx10x10x10...`).

## The learner (frozen, unchanged)

`PARITY-FIVE-20261111-001`'s harness: `CREDIT-PIN-20261110-001B`'s credit learner with the sturdier probe over every input pattern
(positive checks one 4,000-step clamped walk; negative checks four 25,000-step walks, three from fresh states), through
`LEARN-PARITY-20261111-001A`'s run. Budget 8,000,000 steps per target. Ten runs per base, learner seed 9200 + k (J2) and 9300 + k (J3).
Targets in turn: the count of the held inputs (32 examples on J2, 128 on J3), its negation, the count again. After each stop one random
real distinction off the interface (the shared ones included) is flipped, M1 runs to the floor, and the map is read again by SAT.

## Marks (decisive, one line each)

- **V1:** the joined harness with one copy at seed 9000 reproduces `LEARN-PARITY-20261111-001`'s first T1 run exactly. If V1 fails, no
  learning run is reported until the difference is found.
- **R (exact, settled by definition):** the count is realizable at J2's and J3's interfaces (check `harness`).
- **P5:** on J2, the count of five (the first target) is learned and held in at least 8 of 10 runs.
- **P7:** on J3, the count of seven is learned and held in at least 8 of 10 runs.
- Reported: the class combinations where R holds, the other targets, inexact stops, steps, dropped runs.

P5 and P7 failing is the frozen failure of this test: the joined base can count but the learner cannot learn it there. A pass says the
learner learns, through an overlap, a count that no flat composition tried so far even computes.

## Predictions

V1 and R hold; R holds exactly where every copy is in its tightest class. P5 holds; P7 is uncertain (128 examples, three copies to set);
the steps grow with the number of copies.

## Caps and long runs

Results are written per run as each finishes (`runs_learn2.jsonl`, `runs_learn3.jsonl`), so a part cap keeps every finished run (the
lesson of `PARITY-FIVE-20261111-001`'s dropped stage). Per run: 90 minutes on J2, 120 on J3; a run over it is recorded as dropped and
counts as not learned. Per part (systemd, MemoryMax 24G, no swap): harness 20 minutes, J2 120 minutes, J3 180 minutes; runs missing at
the part cap count as not learned. Both learning parts are registered in `docs/LONG_RUNNING.md` before they start.

## Stop

The count learned and held through a shared distinction, or what stops the learner (never reaching the combination of tightest classes,
reaching it in the wrong frame, or not holding it). Then report.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58, and A66 (added here).
