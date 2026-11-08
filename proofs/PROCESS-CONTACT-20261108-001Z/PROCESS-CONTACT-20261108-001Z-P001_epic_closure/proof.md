# Closure of knots between processes

Status: Proved

Ticket `PROCESS-CONTACT-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PROCESS-CONTACT-20261108-001/process_contact.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A contact binds two rings at lag T, every minimally decisive set of c(T) meeting both, exactly when neither ring's first row with c(0) decides c(T), and exactly when forgetting either ring frees c(T). | known-with-delta (elementary); proved | A |
| 2 | A listening contact sees each ring only through its contact histories. | known-with-delta (elementary); proved | A |
| 3 | A memoryless listening contact binds exactly when it is XOR or XNOR of two nonconstant contact cells, its knots joining one decisive set of each ring. With memory, binding at lag 1 needs one of the four parities. | known-with-delta (canalizing functions, certificates); proved | A |
| 4 | Between linear rings the parity contact binds at every lag exactly when neither ring polynomial is nilpotent: it ends only for rules 0 and 255, and for 60, 102 and 90 and their negations on rings of 2^k cells. | known (Martin, Odlyzko and Wolfram 1984) with delta; proved | A |
| 5 | Sharing the contact costs persistence: 44 of 128,128 shared configurations bind at every lag, all with a parity combiner; sharing breaks 13,068 of the 13,104 parity bindings a listening contact keeps forever and rescues 8; lag-1 binding needs a parity and no rule canalizing at its centre; 53 non-parity configurations bind from some lag on. | not found in prior work (Boolean automata double-cycles are the nearest, with another model and observable); exploratory experiment | B |

## Answer

A contact that listens to two processes binds them, two-sided and lost under erasure of either, exactly when it is a parity, and it
persists while both remember their first rows. A contact that is part of both processes feeds them back, and then binding at every
lag is rare at the sizes tested.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with shared contacts that do not read themselves (G5, A31): contact laws that combine their four ring neighbours
without their own value, on the census's rings, exact at every lag. Rated Payoff 2/3 (Substantial), Concreteness 3/3 (Ready). The
table is in the decision note.
