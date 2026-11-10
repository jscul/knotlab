# Pre-registration: three held inputs

Epic `THREE-IN-20261110-001` (backlog B133, G15 with G16), at the coordinator's go-ahead of 2026-11-10. In two stages: **stage 0**
(this section) freezes the exact census's design before it runs; **stage 1** (appended below, after the census and before any learning
run) freezes the learning design and its prediction from the census.

## The question

Theorem D of `IN-OUT-20261110-001`: every map from held inputs to a held output is self-dual. With two inputs that leaves only gates and
copies or negations of one input. With three held inputs self-duality allows majority and parity; parity is neither monotone nor unate.
Which maps of three held points does a knot memory compute, is any non-unate, and can one be learned from examples?

## Stage 0: the census (exact; frozen in `proofs/THREE-IN-20261110-001A/THREE-IN-20261110-001A-P001_maps_of_three_held_points/`)

- **Spaces.** Every class of the dev spaces (outer K_2 with two composites C(2, thin) or C(2, Fano)) and of S1 to S4.
- **Where.** At every group G (a leaf or a top-level composite) with sides s1, s2, s3; its neighbourhood N(G) is every point of every line
  through a side. The floor states are projected onto N(G) exactly (SAT enumeration).
- **Interfaces.** Three inputs and one output in N(G): the three sides held and the output another point of N(G); or two sides and one
  other point held and the output any point of N(G) not held.
- **Readings.** 0, 1, u (undecided) or x (excluded) at each of the eight input patterns.
- **Kinds.** Total maps (every reading decided) are dictators (± one input), majority (of inputs up to negation, up to negating the
  output) or parity (up to negation); any other total map would contradict theorem D. A partial map is **non-unate** when some input
  moves the decided output both ways: one pair of decided patterns differing only in that input rises with it and another falls.
- **Checks.** Every map self-dual (theorem D, again, exactly); the counts of each kind by space, group kind, held set and whether the group
  acts; the first instance of each total majority, total parity and partial non-unate map.

## Stage 0 result (exact, ticket A)

2,976,256 maps read on every class of six spaces: every one self-dual; **no total majority, no total parity and no partial non-unate map
occurs**. The only total maps (1,074) copy or negate a single input, the other two never reaching the output; the rest are partial and
unate (935,160), never decided (2,025,954) or have no floor state (14,068). By lemma G of `IN-OUT-20261110-001` every Kasteleyn law of
these spaces is a class's representative up to negating interface points, and negation keeps a map's kind, so the census covers every
law: **at these interfaces no knot law computes parity, majority or any non-unate map.**

## Stage 1: the learning test (frozen before any learning run)

Frozen in `proofs/THREE-IN-20261110-001B/THREE-IN-20261110-001B-P001_learning_a_map_of_three_points/` (`io3_lib.py`, `check.py`).

- **Learner.** `CREDIT-PIN-20261110-001B`'s credit learner, unchanged, with `STURDY-PROBE-20261110-001A`'s sturdier probe extended to three
  inputs (eight examples; positive checks one 4,000-step walk; each negative check four 25,000-step walks, three from fresh states).
  It sees what it saw before: its dissonance, the floor, the interface points and the examples. Maps are scored by SAT.
- **Interfaces.** In each test space, the first interface in census order where a total map occurs, with that map as the realizable
  target: S1 and S2, leaf 0, inputs points 0, 1, 2 and output 4, target `10101010` (the output is the negation of the third input);
  S3 and S4, leaf 0, inputs 1, 36, 37 and output 3, target `00001111` (the output copies the first input).
- **Targets in turn:** that map, then parity `01101001`, then majority `00010111`; learner seed 7000 + k (k = 0 to 3 for S1 to S4);
  budget 4,000,000 steps each. After each stop, a disturbance and M1 as before.
- **Marks.** **I:** parity and majority never stop (8 of 8): the census proves them impossible here, so any stop is a fooled probe.
  **L3:** the realizable single-input map is learned and held at 3 or 4 of the 4 interfaces.
- **Predictions.** I holds; L3 holds. Learning counts are computed; the census claims are exact.
