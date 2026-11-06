# Sum-of-squares and Sherali–Adams on Tseitin formulas

Epic `SOS-SIZE-20261020-001`, closed 2026-10-20.

## What was found

The epic followed the Dantchev–Riis reading after
`GENERAL-SIZE-20261020-001`. That reading found no sum-of-squares (SoS) or
Sherali–Adams (SA) size bound for Tseitin formulas beyond expanders. The
[proof](../../proofs/SOS-SIZE-20261020-001B/SOS-SIZE-20261020-001B-P001_tangle_pseudo_expectation/proof.md)
closes that gap on every graph built from short cycles.

- **Tangles give pseudo-expectations.**
  - Set E[y_δ(X)] = s_X when X is the small side of a tangle of order k, and
    E = 0 off the cut space.
  - On every edge set of size below k, E is a genuine distribution. That
    defeats SA, and the clause axioms vanish under it.
  - Its moment matrix splits into rank-one blocks σσᵀ. That defeats SoS.
  - The construction is Grigoriev's, with the expander replaced by a tangle.
- **Degrees.**
  - SoS degree lies between cvw and cvw + 4 once cvw ≥ 2Δ − 2. The upper bound
    comes from Berkholz's simulation of PC at twice the degree, together with
    `PC-DEGREE-20261020-001`.
  - SA degree lies between cvw and ⌊3cvw/2⌋ + 1. The supports of the local
    distributions give Duplicator strategies, and a carving gives resolution
    width at most 3cvw/2.
  - So for Tseitin the static systems with positivity follow tree layouts, as
    PC does. Nullstellensatz instead follows linear layouts (the toggle width).
- **Sizes.**
  - With the cell restriction of `CELL-SIZE-20261020-001`, SoS and SA size is
    2^{Θ(tw)} on grids, d-dimensional grids, plane graphs with short faces and
    walls.
  - With twin variables, renaming is free, so the minor-free bound and the
    all-graphs bound 2^{tw^{1/9}} carry over.
- **A correction made during the epic.** For the balanced binomial encoding,
  the argument needs every degree below the tangle order. A hub joined to two
  copies of K₄ (Δ = cvw) breaks it. The check records this as a control, and
  the statement was amended.

## Where this leaves the program

Across the five Tseitin epics the degree picture is now complete up to small
constants:

| System | Degree |
| --- | --- |
| Nullstellensatz | the toggle width |
| PC | half the carving width, up to one |
| SoS | the carving width, up to four |
| SA | between cvw and 3cvw/2 |

The size picture is 2^{Θ(tw)} on graphs with cell systems for resolution, PC,
PCR, SoS and SA. The open problem for all graphs is untouched: the
block-scrambled wall networks still defeat every known method.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — SoS and SA on Tseitin beyond expanders | **Successful** | Degree within an additive constant (SoS) or a factor 3/2 (SA) of the carving width; size 2^{Θ(tw)} on cellular graphs; checked exactly on 15 graphs with controls. |
| Local direction — tangles plus restrictions | Practically complete for these systems | The remaining questions are constants (exact SoS and SA degree) and the all-graphs barrier, which this method cannot cross. |
| Broader exploration — proof complexity of Tseitin beyond expanders | Coherent body of results | NS, PC, SoS and SA degrees are governed by layouts. Size is 2^{Θ(tw)} on cellular and minor-free graphs. There is a polynomial-exponent bound for all graphs, and a family where every known method fails. |
| Long-term goal — breaching proof-complexity barriers | Capability gained, barrier mapped | First size bounds for SoS beyond expanders as far as we found. The general barrier is isolated, not crossed. |
| Next recommendation — the Tseitin body of results | **Next step:** Continue, by converting. Write one self-contained note covering the degree characterizations (NS, PC, SoS, SA) and the size theorem for cellular graphs across resolution, PCR, SoS and SA. Credit Dantchev–Riis for grid resolution and state the scrambled-wall barrier. | It is the most substantial and novel result set of the program, and checking it would give it an independent life. Completion check: a note whose every claim is replayed by one script. |
| Interest — that conversion | **2/3, Promising** | The results are plausibly new and form one story. The main uncertainty: experts may see the size results as standard technique applied well, and pieces may be folklore. |
| Execution — that conversion | Deferred to the owner | You asked for write-ups only for novel results of real magnitude. The alternative is a pivot to a new barrier, with a bounded scan first. |
