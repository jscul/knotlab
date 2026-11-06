# Closure of the native-paths epic

Status: Proved

Ticket `NATIVE-PATHS-20261101-001Z`, 2026-11-01.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/NATIVE-PATHS-20261101-001/paths.md`.
- **The correction records** are `research/NATIVE-PATHS-20261101-001R/records.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Across every nontrivial 2-edge cut of a knot's space, one side is exactly equality and the other exactly disequality: complementary two-place parity, no hub. | new; elementary | A, item 2 |
| 2 | Across every nontrivial 3-edge cut, the point side is exactly an antipodal pair and the line side its complement: a knot against a hub, up to signs. | new form; from the atom lemma and the point lemma | A, item 3 |
| 3 | KNOT-COMPOSE's "compose only through hubs" is withdrawn, and its "exactly" holds only up to signs. Its "hub-free failure is parity" stands. | correction | A, R |
| 4 | Every nontrivial 3-edge cut is a proper splice cut or the shift of a 2-edge cut, with the twist rule. | new; elementary | B, item 1 |
| 5 | Routes are fixed by the space. In ten spaces, proper splice cuts never cross each other or a 2-edge cut; relabelling-invariant. | computed; classical in kind | B, item 2 |
| 6 | A route through atoms carries its length mod 2, and two routes of opposite parity are the failure. A route through a hub carries nothing beyond it. Cutting both routes separates. | classical graph facts; the reading is new | B, items 3–5 |
| 7 | Witness counts: 5 per Fano unit and 5^m per arc. A count, not a relation. | elementary | B, item 6 |
| 8 | The twist criterion: failure survives a twist iff the twist is a cocycle. | classical in substance (Pfaffian signings) | C, item 1 |
| 9 | Knot meets knot only pairwise: both sides of a cut accept knots only when the cut has two edges. | new | C, item 2 |
| 10 | Every statement of the withdrawn claim is recorded, with the note's erratum. | documentation | R |

## Pending the owner

- **The note.** It needs an erratum before it is shared.
- **The old record.** `KNOT-COMPOSE-20261101-001-D001` should be marked superseded by `NATIVE-PATHS-20261101-001-D001`. This awaits the
  owner, following the precedent of commit `bb2bed541`.

## Process note

- **Two records.** Each ticket has a status class, set with `research_scope.py set-status`, and a lifecycle journal, set with
  `research_scope.py transition`.
- **B and C.** Their status classes were set to active before their evidence runs and to proved after verification. Their lifecycle
  journals were advanced at closure.
- **R.** Its status class was set to active before its records check; its lifecycle journal was also advanced at closure.
- **A.** Its lifecycle reached active before its first run, but its status class only afterwards. Its frozen result comes from a run
  made after both (A's proof records this).
- **Ticket C** was added to the epic during the work, after B named its question. Z's dependency list was extended to include it.

## Recommendation

**Full pivot**, from native paths in the knot's own spaces to selection versus composition (2/3). The question is whether any law both
selects its spaces and composes natively.
- **First discriminator.** Test the five weak four-place classes for cycle-like composition.
- **Alternatives.**
  - The note's erratum and reissue (1/3).
  - Counted length as a measure (1/3).

The table is in the decision note.
