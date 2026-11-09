# Closure of large networks persistent without flips

Status: Proved

Ticket `REROUTE-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/REROUTE-20261109-001/reroute.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | FLIP-RULE-20261109-001B's six-contact example persists by two doubled pairs, which pair its closed walks; doubled pairs and automorphisms of the contact graph exchanging a contact's arcs make it persist, and a contact persists exactly when deleting it keeps det(I + tN) over GF(2). | known-with-delta (the criterion); new as far as found (the pairings as a reading); proved | A |
| 2 | On non-degenerate maps to six contacts every persistent contact that sends and hears is explained by a flip, a doubled pair or a contact-graph flip; from seven contacts most are explained by none. | new as far as found; computed | A |
| 3 | Re-routing a network at any set of contacts (partial duality) keeps its contact graph and so every contact's persistence; at law-(12, 12) contacts the automaton itself is unchanged. | known-with-delta; proved | B |
| 4 | The line networks of the square, triangular and honeycomb tori (2n rings, ring graph a cycle) read their distance plainly at every size, by single fastest ways. | new as far as found; proved (square), computed (others) | B |
| 5 | On the square contact graph a ring in a box of side 2^k − 2 is late, so an on-time re-routing of the n × n torus (n ≥ 64) has at most 64n rings. | new as far as found; proved | B |
| 6 | Random re-routings of the lattice tori are non-degenerate, keep every contact persistent and have no flip, and are all late; every small ring on tori of n ≥ 12 is late for some target, on all three lattices; the line networks admit no face toggle. | exploratory census, pre-registered | C |

## Answer

Large networks persistent without flips are generic, as re-routings, which change only how the automaton's cells are grouped into rings;
none of them reads its distance plainly as a plane, and on the square contact graph only groupings into long rings, lines, can.

## Corrections made

- `FLIP-RULE-20261109-001` narrowed (pairings up to six contacts) and `LATTICE-REACH-20261109-001`'s "digon face" reworded as a doubled
  pair, both logged in `docs/CORRECTIONS.md` (commit 8291ad565).

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Recommendation

**Research directions**, none selected, for the coordinator. The table is in the decision note.
