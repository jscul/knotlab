# Pre-registration: a native grade for rigidity

Epic `NATIVE-GRADE-20261112-001` (sub-goal B160, G15 with G16; program learning; challenges A68 and A69), written on 2026-11-12 before any
learning run, at the coordinator's go-ahead. Frozen with the code in
`proofs/NATIVE-GRADE-20261112-001A/NATIVE-GRADE-20261112-001A-P001_a_graded_native_rule/` (`grade_lib.py`, `check.py`). Nothing is tuned
after a result is read.

## The question

`LAW-RIGIDITY-20261112-001` separated the drawing's two jobs: where the learner may rest decides whether it finds a count, and something
that makes a learned law costly to change decides whether it keeps it. On the 6-distinction base U, which no drawing fits, a rest set read
from the knots ("every shortest sum of the law 0") found the count, but the keeping came from a rule we supply (A68: repairs flip
distinctions only), and the value 0 was chosen by us for U, as 1 was for one copy of (2, 0, 4) (A69). Can a graded, value-free rule of the
knots do both jobs, with the learner's own repair free to re-sign?

## How much of LAW-RIGIDITY's stage 2 was settled by its own definition

- **N0 on U: little beyond the exact count.** The rest set held 2 laws, the plain law where the learner starts and the counting law, and
  A68's repair cannot change a law. So a learner that keeps moving until a probe passes can only stop at the count, and what it learns it
  holds by definition: the disturbance could never move it to the other law. The runs show only that it left the plain law quickly: a
  median of 5.5 probes at the first target.
- **N1 on one copy: a real search, but not a guided one.** The rest set held 32 laws, 4 counting; drawing laws at rest at random needs 8
  draws on average, and the learner took a median of 46.5 probes. Stage 1's RS (4 laws at rest, 1 counting, 4 draws expected) took a
  median of 23. The learner found the count no faster than random draws among the laws at rest, so its success follows from the rest sets
  being small, not from the examples steering it. That is the plain reading of those 30 of 30s.

## What the knots' shortest sums can and cannot do (exact, computed before freezing; `check.py --part harness`)

| Base | Laws | Counting laws | Shortest sequences | At rest when all equal (counting) | All 0 | All 1 | Places on 0 / 1 / 2+ shortest sequences |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J1, one copy of (2, 0, 4) | 512 | 4 | 4, of two knots | 64 (4) | 32 (0) | 32 (4) | 8 / 16 / 0 |
| U, 6 distinctions, 8 knots | 2,048 | 1 | 14, of two knots | 2 (1) | 2 (1) | 0 | 2 / 4 / 18 |
| U(7, 9), seed 27 | 4,096 | 1 | 11, of two knots | 8 (0) | 8 (0) | 0 | 3 / 10 / 14 |
| U(8, 10), seed 15 | 8,192 | 2 | 11, of two knots | 8 (0) | 8 (0) | 0 | 5 / 11 / 14 |

- **A value-free rule serves both of LAW-RIGIDITY's bases.** "All shortest sums equal, whatever the value" leaves a counting law at rest
  on J1 (4 of 64) and on U (1 of 2), so the value need not be supplied there (it removes A69 for these two bases).
- **But the shortest sums do not contain the count in general.** On the next two bases of `UNDRAWN-LEARN-20261111-001`'s frozen search,
  U(7, 9) and U(8, 10), every rule of this kind leaves 8 laws at rest and none of them counts. LAW-RIGIDITY's success on U was specific to
  U; this narrows its reading (logged in `docs/CORRECTIONS.md` at this epic's close). Those two bases are therefore not run: learning
  there fails by definition.

## The rule (frozen)

**GE, graded and value-free:** W = 2 × violated knots + 2 × min(number of shortest sums 0, number of shortest sums 1): the number of
shortest sequences that would have to change for all to be equal, each charged 2. The learner rests where all shortest sums are equal. A
sign change is proposed at a violated knot or at a place on a sequence of the smaller kind (both kinds at a tie). The credit rule reads
distinctions (`UNDRAWN-LEARN-20261111-001`'s engine). **The repair is free:** after each stop the learner's own M1 may re-sign knots (A68
is not used). Native, point by point: computed from the knots and the law only; one rule for every shortest sequence; it reads no target,
example or chosen value; nothing is supplied beyond the learner as before.

**Why it might give rigidity, and where it cannot (exact).** At rest, a sign change at a place on c shortest sequences costs 2c (for c up
to half the sequences), and mends at most one violated knot (−2), so a repair re-signs there only if c ≤ 1. On J1, 8 of the 24 places lie
on no shortest sequence and 16 on one: a repair can re-sign every place at no net cost when it mends a violated knot, so J1 gets no
rigidity from this rule by construction. On U, 18 of 24 places lie on two or more. So the test can fail on either base, and is expected to
behave differently on the two.

## Runs (frozen)

Ten runs on J1 and ten on U, learner seeds 10000 + k, targets the count of the three held distinctions, its negation, the count again,
budget 8,000,000 steps per target. After each stop one random real distinction off the interface is flipped, the free repair runs to rest,
and the map is read again by SAT. 30 minutes per run, written as each finishes; 40 minutes per part.

## Marks and frozen readings (one line each)

- **V:** the engine's running dissonance equals a fresh count (computed before freezing: it does).
- **E (exact):** the table above.
- **P(J1), P(U):** learned and held at the first target in at least 8 of 10 runs.
- **Readings, per base:** *holds* if P passes (native rigidity enough there); *still drifts* if at least 8 of 10 runs stop at the count
  but fewer than 8 hold it; *not found* if fewer than 8 stop at the count.
- **Reported, not marks:** all targets; the first-target probes against the random-draw expectation (64 / 4 = 16 on J1, 2 on U).
- If P(U) passes, A68 is not needed on U and is Overturned for it (a native grade keeps the law); if U still drifts, A68 is Confirmed for
  that reason. A69 is Overturned for J1 and U in either case (the value-free rule leaves a counting law at rest on both, exact).

## Predictions

U holds (most places lie on two or more shortest sequences); J1 still drifts (no place does). Finding on J1 no faster than random draws.

## Prior work

The reading of a law as a Z2 gauge field, with sums around cyclic sequences as its gauge-invariant content, is the literature's
frustration (Toulouse 1977) and gauge symmetry of random magnets (Fradkin, Huberman and Shenker 1978). Learned couplings treated as
dynamical Z2 gauge variables with a plaquette term are known in the gauged neural network of Kemuriyama, Matsui and Sakakibara
(cond-mat/0203136), which learns by a Hebbian rule and shows ordered and disordered phases; there the plaquette term is what keeps learned
couplings stiff. What I did not find: a rest set and a rigidity cost separated, plaquettes chosen as the shortest Berge cycles of a
hypergraph with no drawing, or a value-free version. So the gauge reading is known; its use here is known-with-delta.

## Stop

P(J1) and P(U) settled, with the readings above. If B160 stalls (both drift or fail), the next cheap step is the tie (B157).

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58, A66; A68 and A69 under challenge.
