# What SEED's copy step reads: pre-registration

Epic `COPY-CLASS-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead after `COPY-READ-20261118-001`'s referee.
Goals G1 and G16; challenges A101. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

`COPY-READ-20261118-001`'s referee found every copy step (a crossing-making fill SEED accepts after its switch) in one closure class,
with about 55 refused fills for each one. What separates them, and how far out must a reading look?

## Ticket A (written before this freeze)

`proofs/COPY-CLASS-20261118-001A/COPY-CLASS-20261118-001A-P001_model/proof.md`.
- **C1.** Every new crossing joins splits separating the two end pairs.
- **C2.** SEED's verdict is read on those splits and the crosser set of a model.
- **C3.** In a full two-way grid a model's crossers are a whole order.

## Ticket B

`experiments/COPY-CLASS-20261118-001B/COPY-CLASS-20261118-001B-E001_class/`: `classlib.py`, `run.py`, `checks.py`, building on
`KEEP-READ-20261118-001B`'s `keeplib.py` and its pinned predecessors. 2 checks pass.
- SEEDK from every bracketing of 5, 6 and 7 and every third of 8 (105 starts), and from 30 random bracketings of the line of 12, to
  n = 30. Every crossing-making knot set after the switch is scored, at the extension level: a rule accepts an extension when it
  accepts one of its knot sets.
- **CR (frozen, the advisor's candidate).** The model is sought only among the crossed splits separating the end pair that shares
  a distinction with the middle knot's pair. Clause (a) is read on the end pairs' splits (C1). It is a rule naming only the move's
  own pairs, together with those splits' crossers.
- **CRANY.** The same with the model sought among all crossed splits, which is SEED's own clause (b), read locally for clause (a).
  It is a control, equal to SEED on the gate runs.
- **Readings.** For every extension: SEED's verdict, CR's, CRANY's, whether it is in the copy class, and the reason for a refusal.
  The reason is clause (a), or clause (b) as a strict subset, a strict superset or mixed. For each absorbing fill, the size of the
  model's crosser set and the number of splits.

## Decision rules (frozen)

- **CR decides the copy step** if it agrees with SEED on every crossing-making extension. Every disagreement is printed; there is
  no tolerance.
- Otherwise CR's recall on absorbing fills and its false acceptances among refused fills are reported, with every counterexample.

## Predictions (frozen)

| # | Prediction | Source |
| --- | --- | --- |
| P1 | CR agrees with SEED on every crossing-making extension | advisor ("0 errors both ways") |
| P2 | CRANY agrees with SEED on every extension, and C1 holds on every knot set | proved / engine check |
| P3 | Most refusals are clause (a) (crossed splits come to cross), and among clause-(b) refusals subsets outnumber supersets | advisor (refusals where r lands partway, giving the tail a strict subset) |
| P4 | Some absorbing fills have a model with two or more crossers (from the lines of 12) | advisor's stratification |
| P5 | Every absorbing fill is in the copy class, at the new sizes too | `COPY-READ-20261118-001` |

**Exploration disclosed.** One smoke run (a bracketing of 7 to n = 22) printed only C1's equality and SEED against CRANY, not CR.

The advisor was consulted before this freeze. It advised cutting the knot-radius tiers as vacuous (an 81% ball on a line of 14),
derived the roles of the three knots and the candidate rule CR, and asked for classifier scoring, the refusal breakdown, and
starts with models of more than one crosser.
