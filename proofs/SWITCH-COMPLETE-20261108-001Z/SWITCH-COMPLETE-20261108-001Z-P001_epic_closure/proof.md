# Closure of the complete-invariant test

Status: Proved

Ticket `SWITCH-COMPLETE-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SWITCH-COMPLETE-20261108-001/switch_complete.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The glue block is not a complete switching invariant: 448 values on the smallest glue's 512 classes, 1,526 on the 10-line glue's 2,048. | new; computed | A, B |
| 2 | On the smallest glue it separates all 42 orbits of the glue's symmetries but one pair, whose signed glues have 40 and 34 solutions. | new; computed | A |
| 3 | On the 10-line glue it takes 429 values on 576 orbits; 92 of 98 shared blocks span orbits and 76 mix solution counts. | new; computed | B |
| 4 | The 10-line glue's largest shared block is exactly the 190 classes where nothing creates (66 orbits, 60 to 110 solutions). | new; computed | B |
| 5 | Colliding pairs at both sizes have identical glue blocks on their plain spaces, and census 6 under every order separates neither. | new; computed | A, B |
| 6 | At both sizes the Pfaffian class is the only class without solutions, and no other class shares its block. | new; computed | A, B |
| 7 | Each row depends only on the class on the glue without its line; on the smallest glue it takes 55 or 57 values on 128 classes. | new; computed, reduction proved | A |

## Pending

- The earlier items listed in SWITCH-READ's ledger.

## Recommendation

**Continue** (2/3): does creation always single out the contradictory class? Test the four 12-line glues, following only the classes
whose rows match the Pfaffian class's.
- **Alternatives.** Where nothing creates (1/3, deferred); what of counting creation carries (2/3, deferred).

The tables are in the decision note.
