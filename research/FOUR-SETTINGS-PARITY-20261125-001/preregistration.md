# Four detector settings on one parity knot

Exploratory reconstruction, 25 November 2026. The owner requested the continuation of a comparison with Sean Carroll's account of emergent space. This is a known-answer test. The three-particle prediction, the ordinary local bound and a previous quantum calculation were known before this run.

## Question and stop

Can the same four allowed words account for the complete outcome distributions of three detectors, each offered two settings? Compare ordinary local readings of one definite word with the coherent preparation and phase-sensitive measurements already specified in the program. Distinguish the rule defining the words from the rule assigning detector probabilities. Stop when each claimed match has been checked cell by cell and each control has an explicit differing entry or certificate.

The allowed words in detector order are 000, 011, 101, 110. Inputs are three independent fair bits. Score the four even-parity input triples with equal weight, and retain the other four in the quantum comparison. Each detector sees its own setting. In the scored experiment the required outcome parity is even for 000 and odd for 011, 101 and 110. Each of the four permitted outputs has probability 1/4. For the other inputs the specified quantum benchmark is uniform over all eight outputs.

## Prior work in the program

`python3 -B scripts/track.py objects "parity three-reader" --until 2026-11-25 --exclude FOUR-SETTINGS-PARITY-20261125-001 --limit 3`

`python3 -B scripts/track.py objects "Mermin" --until 2026-11-25 --exclude FOUR-SETTINGS-PARITY-20261125-001 --limit 3`

`python3 -B scripts/track.py objects "one even parity knot" --until 2026-11-25 --exclude FOUR-SETTINGS-PARITY-20261125-001 --limit 3`

- `THREE-READERS-AND-GROWTH-20261120-001` specifies the positive coherent preparation, the local projectors and squared probabilities. Its common explanation for parity uses the ordinary value and unturned flip. [Definitions](../THREE-READERS-AND-GROWTH-20261120-001A/readings.md)
- `KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001` already has the parity control for a value read and a quarter-turned flip, including all 64 probabilities. The independent phase note mainly discusses the six-word not-all-equal comparison. The archived parity calculation is a direct predecessor. [Earlier tables](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A/observations.json.gz) · [Earlier implementation](../KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001A/reader_tables.py)
- `ENTANGLEMENT-READ-20261120-001`, `NEWBORN-TABLES-AND-THREE-DONOR-RETURNS-20261121-001` and `SPENT-PASTS-AND-TWO-SHARED-NAMES-20261121-001` study different preparations or three-reader records. The signed score must use the same four signs for every comparator.
- `CHEAP-COUNT-20261112-001`, `RING-FORMULA-20261118-001` and `JOIN-GROWTH-20261118-001` concern the descriptions or growth of knots. They supply no detector calculation here.

## Fixed comparisons

1. Enumerate the 4,096 ways to answer each of the six local questions with a Boolean function of that reader's bit in the uniformly drawn parity word. Count complete scored tables matched. Also allow any shared random list of the six predetermined answers independent of the settings. Enumerate its 64 deterministic possibilities, derive the uniform-average bound, and check whether a mixture attains it on every scored input.
2. Use equal real amplitudes on the four words and the already specified local questions Z and Y, with probabilities from the squared magnitude of the joint projection. Compare all 64 probabilities with the quantum benchmark and the earlier archive. Replace the pure preparation with its diagonal mixture, and replace Y with the earlier unturned flip X. Keep settings, outcome signs and target fixed.
3. Test the strongest fixed-parity alternative at the level of allowed states. Let the settings and outputs participate in the same finite system of ordinary parity equations, with freely forgotten auxiliary bits. Check whether the scored six-bit relation is closed under sums of three members. A failed triple rules out this whole class and leaves choices of setting-dependent operations open.

Use exact arithmetic, one CPU process per replay, and retain zero cells. Check that a wrong parity target fails. The finite run uses at most 4,096 tiny candidates and no training or sampled estimates. Time a short prefix before the full pass. The matched controls vary the supplied coherent preparation and calibrated measurement (existing assumption A144). The inputs and the scoring convention are features of the named experiment.

## External background

Carroll asks how local physics might emerge when the starting point is an abstract quantum state with unitary evolution. The detector predictions are the standard three-particle benchmark. This reconstruction concerns neither a new quantum prediction nor a derivation of space. [Carroll, *Reality as a Vector in Hilbert Space*](https://arxiv.org/abs/2103.09780) · [Mermin, *Quantum mysteries revisited*](https://physics.umd.edu/courses/Phys622/bedaque/mermin.pdf)
