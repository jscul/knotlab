# Can a parity knot supply its own phase-sensitive reading?

Exploratory comparison, 25 November 2026. The owner asked what logical rules can supply before introducing quantum physics. The earlier comparison left setting-dependent changes open. The examples and analytic obstructions below were developed in designing this test. An independent reviewer had already checked the one-reader example through five measurements. This is a reproducible, known-answer investigation.

## Inputs and observations

Start with one of 000, 011, 101, 110, each with weight 1/4. A lawful change stays among these four words. An ordinary read (setting 0) reports the addressed bit and leaves the complete state untouched. A changed read (setting 1) may report a bit and change the word. Its rule can depend on the reader, its own setting, the whole current word and setting-independent randomness. The same rule applies in every order. No reader receives future settings, a transcript, elapsed step number, or information about earlier acts beyond the current word. Preserve all trials. Test every order of three distinct readers. In the extra-record control declare exactly which further states they can write.

Use the previous three-reader probabilities only in judging outputs. All eight settings are equally weighted and independent of the preparation. With zero changed reads the outcome has even parity. With two it has odd parity. Give each of the four words of the required parity probability 1/4. With one or three changed reads all eight outputs have probability 1/8. Match entire rows, including zero cells. Count the four promised rows separately from all eight. Check immediate repetition because matching single-use correlations alone does not fix a measurement's effect on the state.

## Prior work in the program

`python3 -B scripts/track.py objects "sequential three-reader GHZ memory" --until 2026-11-25 --exclude NATIVE-PHASE-READ-20261125-001 --limit 3`

`python3 -B scripts/track.py objects "phase sensitive change order" --until 2026-11-25 --exclude NATIVE-PHASE-READ-20261125-001 --limit 3`

`python3 -B scripts/track.py objects "isolated even parity knot three readers" --until 2026-11-25 --exclude NATIVE-PHASE-READ-20261125-001 --limit 3`

- `FOUR-SETTINGS-PARITY-20261125-001` fixes each target probability and excludes preassigned local answers and fixed ordinary parity equations. `THREE-READERS-AND-GROWTH-20261120-001` and `KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001` used explicitly calibrated readings on these and other preparations. [Previous comparison](../FOUR-SETTINGS-PARITY-20261125-001/results.md)
- `CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001`, `FREEDOM-CLOCKS-AND-BIRTHS-20261120-001` and `IDLE-PHASE-AND-TREE-CLOSURE-20261121-001` study admissible changes, the choice of a signed answer and the supplied phase of a pulse. The ordinary two-mark swaps and their calibration are directly relevant. [Admissible ordinary changes](../CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001A/native_records.md)
- `SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A` supplies an actual four-knot record and controlled swaps. `SPENT-PASTS-AND-TWO-SHARED-NAMES-20261121-001` concerns other preparations before and after growth. `UNSIGNED-ROUTE-JOINS-20261115-001` concerns a different question about computation. [Four-knot control](../SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/physical_records.md)

## Fixed tests and controls

1. At each changed reader permit any of the 24 permutations of the four words and report its own bit before the change, with either choice of sign. Exhaust the 48³ instruments, all six orders and four promised settings. Compare identity and pair-flip translations. Give a broader fixed-order control allowing a different readout. Then check analytically whether even an irreversible or stochastic write with an arbitrary readout could give the promised parities in every order. Compare an ordinary read immediately before versus immediately after a change by another reader.
2. Extend the state by a fair bit stored on a supplied second parity knot. On a changed read report the addressed bit plus that stored bit modulo two, then toggle the stored bit. Compare all 384 probabilities with the target. Vary the initial weighting, suppress the toggle, and try two immediate changed reads at the same reader.
3. Test the ordinary one-reader alternative. Name the three distinctions Z, X, Y for comparison only. For each of the six preparations hold the named bit fixed and weight its two words equally. Read one bit, then leave the other two unchanged or toggle them together with equal weight. Check repeatability and every next measurement by closure on the six preparations. Test a single preparation-independent pulse with the required sign action (z,x,y) → (z,−y,x), first on the four words, then with an extra orientation bit. Compare the ordinary four-cycle obtained by the allowed two-mark changes with its inverse and a fair choice of changes. Separately check which two quantum probe preparations a calibrated X/Y read can distinguish. Their amplitudes appear only in that scoring calculation.

The shared record, fair preparation and update, choice of ordinary read, and selection of moves are hypotheses of these tests. Choosing a positive example does not give the parity constraint an update law. Compare the one-knot start with the stated ordinary growth rule before claiming that it supplies an extra record. The shared-bit test permits communication through common state. It tests an alternative explanation of the statistics.

Time a prefix before the full census. Use exact finite counts, a single CPU process per checker, and a memory cap below 512 MiB for each. Stop once the bounds, positive controls and first failing observations are independently checkable. No random sampling, inference about all logical systems, or empirical claim about physical detectors enters this study.

The external benchmarks are the three-particle test and the distinction between the phase groups of a toy bit and a qubit. The project-specific question is which readings and changes the allowed words can support. [Mermin](https://physics.umd.edu/courses/Phys622/bedaque/mermin.pdf) · [Coecke, Edwards and Spekkens](https://arxiv.org/abs/1003.5005)
