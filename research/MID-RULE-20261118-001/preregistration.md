# A rule whose second phase reads only the fill's knots: pre-registration

Epic `MID-RULE-20261118-001`, 18 November 2026, by Claude. It takes `KEEP-READ-20261118-001`'s first direction; the coordinator
gave the go-ahead and asked for runs well past n = 24. Goals G1 and G16; challenges A101. Frozen before any read-out of ticket B.
The canonical K1–K3 test is unchanged.

## The question

`KEEP-READ-20261118-001` found no local reading that is SEED's second phase, but one local sign that never raised the orders: a new
distinction in the middle of two or more of its knots. Take only such fills after the first fill (MID2), or more generally fills
certified with at most one end knot (ONE). Do these rules keep two orders and grow full two-way grids, with knots on any pairs (free)
and with knots only on co-knotted pairs (knot-local)?

## Ticket A: the proof (written before this freeze)

`proofs/MID-RULE-20261118-001A/MID-RULE-20261118-001A-P001_ends/proof.md`.
- **E1.** A new crossing needs two different end knots.
- **E2.** A fill certified with at most one end knot keeps every relation, on any base.
- **E3.** From a line, MID2 and ONE keep two orders forever.
- **E4.** From a full grid, the free forms refill every new row.
- **E5.** From a line, the free forms reach a full grid exactly when the first fill spans the line (chance 6 / (n (n − 1))).

So the free forms are proved; the computation checks them and reads the knot-local forms, which the proof leaves open.

## Ticket B: computation

`experiments/MID-RULE-20261118-001B/MID-RULE-20261118-001B-E001_mid/`: `midlib.py`, `run.py`, `checks.py`, building on
`KNOT-SWITCH-20261118-001B`'s `knotlib.py` and its pinned predecessors. 4 checks pass before this freeze. Among them, E1 was checked on
3,110 fills of random bases (the advisor's retro-check): no fill certified with at most one end knot made a crossing.
- **K.** MID2 and ONE knot-local from every bracketing of 5, 6 and 7 and every third of 8 (105 starts), to n = 60.
- **F.** MID2 and ONE free from the lines of 5, 8 and 12 and the 2 × 2 pattern (10 runs each), and ANY free from the lines of 5 and
  8 (5 each, the positive control), to n = 60 (free runs stop at 60 states).

**Readings at every step.** k, λ, a full two-way grid, whether nothing crosses, the step's kind; for the knot-local forms, the
move's middle knots.

## Decision rules (frozen)

- **Invariant.** No phase-two step changes k or λ (E2). A violation means a bug or a false theorem, and stops the study.
- **Strong** (as before): from each start, every run keeps k = λ = 2 at every step after its first fill, and at least 90% pass a full
  two-way grid three times with every later subdivision at a full grid.
- **Starved:** fill fraction on steps 31 to 60 at most 0.15.
- **Stratified for the free forms from lines:** "a spanning first fill gives strong", and "a non-spanning one gives no full grid,
  ever" (E5).

## Predictions (frozen; the advisor's unless marked)

| # | Prediction |
| --- | --- |
| Q1 | The invariant holds at every step of every run (proved) |
| Q2 | MID2F and ONEF from the 2 × 2 pattern are strong in every run (E4) |
| Q3 | MID2F and ONEF from lines: strong exactly in the runs whose first fill spans the line, no full grid in the others (E5) |
| Q4 | MID2K and ONEK starve: fill fraction on steps 31 to 60 below 0.15 in every start size, with λ = 2 throughout; MID2K about one fill per run |
| Q5 | ANY raises λ above 2 in every run (mine; the harness detects raises) |

**Exploration disclosed.** Single timing runs of MID2K from one bracketing of 7 and MID2F from the 2 × 2 pattern and the line of 8,
to n = 40, read for time only.

The advisor was consulted before this freeze. It strengthened my lemma to E1 (the copy principle; "at most one end knot"), predicted
E5's exact share and MID2K's starvation, and asked for ONE, the ANY control and the retro-check.
