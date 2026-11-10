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
