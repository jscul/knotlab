# Closure of the contradictory-class test

Status: Proved

Ticket `CONTRA-READ-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/CONTRA-READ-20261108-001/contra_read.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On each of the seven trisum glues of 8 to 12 lines exactly one switching class has no solution, the Pfaffian class. | new; computed | A, B |
| 2 | On the 8- and 10-line glues every single row of creation between glue lines singles that class out. | new; computed | A |
| 3 | On the five 12-line glues its glue block is its own; after the first row only the four classes over its restriction remain. | new; computed | B |
| 4 | In the glue without a line, that line's points are tied for the contradictory class and for no other class. | new; computed, with the argument | A |
| 5 | In its rows, lines sharing two points with the removed line are degenerate, and where no line does, degeneracy alone singles the class out. | new; computed | A |

**Stress test.** Every single row also singles the class out on the five 12-line glues
(`research/CONTRA-READ-20261108-001/stress_test_p2.json`).

## Pending

- The earlier items listed in SWITCH-READ's ledger.

## Recommendation

**Continue** (2/3): prove that one row reads the removed line's tie.
- **Alternatives.** Why there is one contradictory class (2/3, deferred); the 14-line glues (1/3, deferred).

The tables are in the decision note.
