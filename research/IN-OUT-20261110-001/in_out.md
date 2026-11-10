# Inputs and outputs

Epic `IN-OUT-20261110-001` (backlog B120, G15 with G16; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen with the code in commit `6d6434df1` before any run on the test spaces. Proof family:
`proofs/IN-OUT-20261110-001A/`.

## The answer

**At a single atom, yes: the memory learns input-output maps from examples, a NOT gate included. Through a composite, not with this
learner.** The world holds two outer points of an atom or composite (the inputs) and reads the third at the floor: decided, undecided or
excluded (A58). A learner that sees only its own dissonance under the world's clamps, with no address and no outside map, learned 53 of
56 targets at 14 leaves and they held, but only 1 of 16 at 4 composites.

- **Theorem D (proved by hand): every map is self-dual.** Flipping every point leaves the dissonance unchanged, so f(¬x) = ¬f(x). No map
  is constant, and no knot space computes AND, OR or XOR of two held inputs as a total map. The learner never stopped on AND (18 of 18).
- **Lemma G (proved by hand): the world's inputs supply the frame.** A gauge flip negates one input or the output, so one class gives
  one map up to negations. This is why non-monotone maps appear: theorem M of `NOT-INSIDE-20261110-001` bounds readings of stored
  classes, and held inputs are not stored classes.
- **An acting atom is a gate (exact, every class).** Read with two sides held, an acting atom or composite forces the output exactly when
  the held sides agree (or exactly when they differ, in another frame): `1uu0`, the NOT gate, forces the output to the inputs' negation
  when they agree. A transparent one reads `uuuu`. 582 of 608 acting leaf-classes and 60 of 64 acting composite-classes give a gate.
- **Lemma C (proved by hand): examples cannot see inside a composite.** A composite's interface reads its inner atoms only through the
  AND of their acting bits, so until all act every example reads as if none did. The learner reached no composite gate exactly.
- **The probe is weaker than the native writer's (computed).** Its walks hold points and must climb to the floor; on the largest space
  they missed a reachable wrong value six times, so the learner stopped six times believing a gate was formed when none was.

## How the examples are stored

**By the example learner alone, with no outside map.** It is not the native writer of `NATIVE-WRITE-20261110-001` and uses no address: it
sees its dissonance, the floor, the interface points and the examples (the world holds the inputs and, as a teacher, the asked output).
It is never told which atoms exist, where they are, their roles, classes, a target signing or a solver's answer. It changes signs only on
lines near the interface, widening that neighbourhood when its probe keeps failing. What it stores is a role (the atom acts) and a frame
(the signs at the interface points), both written by its own dynamics.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| D: every map of held inputs is self-dual; no AND, OR or XOR of two inputs | proved by hand |
| G: a gauge flip negates one input or the output | proved by hand |
| C: a composite's interface reads its inner atoms only through their AND | proved by hand (from `NEST-ATOMS-20261110-001`) |
| D and G on every class of 18 interfaces; acting groups compute gates | exhaustive computation |
| Learning from examples: 53 of 56 at leaves, 1 of 16 at composites | computed, frozen |
| The impossible AND never stopped (18 of 18) | computed, frozen |
| The probe's reliability: 6 inexact stops, all on S4 | computed, frozen |

## Against the pre-registration

- **L held:** 53 of 56 leaf writes learned and held (94.6%; the mark was 90%). The NOT gate `1uu0`, the XOR pattern `u10u` and the copy
  gate `0uu1` were each learned at 13 of 14 leaves; the misses were all at one Fano leaf of S4, as inexact stops.
- **C failed, as predicted:** 1 of 16 (only "off"). Three composites never formed a gate in 4,000,000 steps; the fourth stopped three
  times on a false reading.
- **A held:** 0001 never stopped at any of the 18 interfaces.
- **R failed:** 6 inexact stops against a prediction of 0, all at S4 (Fano atoms, 90 points), all with the map still `uuuu`.
- **K held as frozen** (composite median 2,024,900 steps to turn a gate on, against 62,600 at leaves), but the composite stops it counts
  were the inexact ones, so it says little.
- **Census held:** D and G on every class.
- **A defect of the frozen learner, found in the run.** After a failed write the learner can be left above its floor; it probes only at
  the floor and widens its attention only after failed probes, so it never recovers. Every later target at those three composites failed
  with no probe at all (including the trivial "off"). It does not change L, A or the census; C would have failed regardless at those
  three, which never reached a gate on their first target.

## What it changes

- **The memory has an interface.** Held inputs and a read output turn an atom into a gate, a NOT gate among them, and a learner driven
  only by its own dissonance writes these gates from four examples and switches them off. The gate depends on the stored role
  monotonically (only an acting atom gates; a composite only when all its atoms act) and on the held inputs non-monotonically.
- **Self-duality is the real limit on held inputs,** not monotonicity: with two inputs only gates and copies or negations of one input
  exist. Three held inputs would allow majority and parity (backlog B133).
- **Depth is the open problem.** The examples carry no signal about which inner atom to change (lemma C). But each acting atom holds
  dissonance the state cannot walk away (P1 of `NATIVE-WRITE-20261110-001`), which the learner could see: partial credit that the
  examples withhold (backlog B132).

## Assumptions

Added: A58 (the interface reading). Relied on: A20, A21, A46, A47, A49, A50 (its temperature alternative while learning), A52.

## Corrections

None.

## In the owner's words

Hold two points of a learned knot and read the third: when the knot holds its contradiction, the third point is forced whenever the two
agree, and free otherwise. That is a gate, and a learner that feels only its own tension learns which gate from four examples. It cannot
yet reach a knot buried inside another: from outside, a pattern of patterns looks dead until every part of it is alive.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: inputs and outputs (B120) | **Status:** Partial | gates learned natively at single atoms (53 of 56); composites not reached (1 of 16); the probe fooled 6 times |
| Local direction: learning maps at an interface | Continue | the leaf result holds; depth fails for a stated reason (lemma C) with a native signal not yet used |
| Broader exploration: learning program | Known alternatives | credit from pinned dissonance, three held inputs, a sturdier probe |
| Long-term goal: G15 Learning: a point in a learned knot space | Capability gained | the memory computes and learns gates of held inputs, NOT included |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Credit from pinned dissonance (B132) | 2/3 — Substantial | 2/3 — Testable | the same learner, also counting dissonance it cannot walk away near the interface as partial credit, relaxing to the floor before it probes → composite gates learned, or pinned dissonance that misleads | Selected · awaiting go-ahead |
| 2 | Three held inputs (B133) | 2/3 — Substantial | 2/3 — Testable | census of maps with three held points (theorem D allows majority and parity), then learning parity → a learned map that is not unate, or a proof that none exists | Alternative · tied, independent |
| 3 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded; now also for clamped walks, which were fooled six times | Alternative · deferred |
| 4 | Writing with only the ones named (B131) | 1/3 — Incremental | 2/3 — Testable | as recorded | Alternative · deferred |

Directions 1 and 2 tie at the top and are independent; they could run in parallel.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B120 taken; B132 and B133 added. **Assumptions:** A58 added.
**Basket:** B132 (credit from pinned dissonance), B133 (three held inputs), B130 (a probe that is a theorem); taken: B132 as the selected
next step.
