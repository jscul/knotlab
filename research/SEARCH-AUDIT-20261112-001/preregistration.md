# Pre-registration: has the learner ever found a target faster than blind search?

Epic `SEARCH-AUDIT-20261112-001` (G15 with G16; program learning), written on 2026-11-12 at the coordinator's request, before any
comparison below is computed. The criteria, the cases and the code are frozen here with
`proofs/SEARCH-AUDIT-20261112-001A/SEARCH-AUDIT-20261112-001A-P001_learning_against_blind_search/` (`audit.py`). It reads recorded runs
only; it runs no learner.

## The question

`NATIVE-GRADE-20261112-001` found that on one copy of (2, 0, 4) the learner needed far more probes to find the count than random draws
among the laws it may rest at. If that holds for every result the line calls learned, the examples only stop a search; they do not speed
it, and the word "learned" overstates what was shown.

## The random baseline (frozen)

The learner probes only at rest. Blind search draws a law at rest uniformly at random for each probe and stops at the first whose map is
the target. A law at rest is a signing whose class (signings up to flipping distinctions and complementing knots) is one the learner can
rest at and has a satisfying state. The map read at an interface depends on the signing through its class and the flips of the
interface's own distinctions: flipping an input permutes the map's patterns, flipping the read distinction swaps 0 and 1. So the chance p
that one draw gives the target is the average over the classes at rest of the share of the interface flips that turn the class's map into
the target. For a written address (a set of acting atoms), which depends on the class alone, p is the share of classes at rest with that
address. Blind search then needs a geometric number of probes: mean 1/p, median the least n with 1 − (1 − p)^n ≥ 1/2.

## The cases (frozen): every learned result in the learning note's cold-start section

1. Native writing of addresses (`NATIVE-WRITE-20261110-001`, S1 to S4, every write).
2. Gates from examples with the credit learner and the sturdier probe (`STURDY-PROBE-20261110-001`, S3, S4, S5, every interface, the first
   target `1uu0`).
3. Deeper memories (`DEEP-MEM-20261111-001`, every group, the first target).
4. Parity of three held distinctions (`LEARN-PARITY-20261111-001`, T1 and T2, the first target).
5. The count of five through a shared distinction (`SHARED-COUNT-20261111-001`, J2, the first target).
6. The rest-set and graded learners (`LAW-RIGIDITY-20261112-001` R, RS, N1 on J1, N0 on U; `NATIVE-GRADE-20261112-001` J1 and U; the
   first target).

A case is one space and interface (or base). Its learner probes are the recorded probes of the runs that stopped at the target; runs that
did not stop are counted as not found, with probes at least the recorded count.

## What counts as learning and what as search (frozen)

- **Learning:** the learner's median probes to find is at most half the blind median, and at least 3 of 4 of its runs find within the
  blind median.
- **Search:** neither faster than that nor slower than twice the blind median.
- **Slower than search:** the learner's median is more than twice the blind median.
- **The word "learned".** If no case is learning, the line's results show maps found and held under examples that act as the test that
  stops a search, not guided learning; the published word "learned" then gets a correction, logged and reported, with its verdict judged
  against G15 and G16: Narrowing if the found-and-held results stand and only their reading changes. If some cases are learning, the report
  says what differs there.

Not settled by definition: the baseline is exact from the classes; the learner's probes are recorded data.

## Prediction

No case is learning; most are search or slower.

## Relation to B159

B159 (two histories ending in one state must leave a learner in different laws) asks whether the learner's law records its history; this
audit asks whether its examples steer its search. They are different tests; B159 stays in the basket.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58.
