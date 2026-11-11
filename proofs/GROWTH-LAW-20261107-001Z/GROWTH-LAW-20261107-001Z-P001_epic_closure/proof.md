# Closure of growth as a law

Status: Proved

Ticket `GROWTH-LAW-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROWTH-LAW-20261107-001/growth_law.md`.

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a world of knots is now a grown pattern and a thread a chain. The mathematics is
unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For a growth rule that reads only the law, the joint law of history and states on a fixed grown pattern is a product, so no knot joins the order to the states; when grown patterns vary, with absent things forgotten and constraints accumulating, every knot containing an order variable contains an existence variable, and existence enters as a presence literal. | known-with-delta (products of relations); proved | A |
| 2 | The local history (at most one parent) is 2-CNF and holds no knot; the knots of "time has no loop" are exactly the grown pattern's cycles, each not-all-equal on its seams; on a ring the beginning is one knot over every seam and contradicts the local history. | known-with-delta (topes of graphic oriented matroids); proved | A |
| 3 | Along any growth order the steps' changes of the Euler characteristic sum to the grown pattern's: beginnings and ends less closing moves. Sprouting builds trees, disc moves discs and spheres. | known-with-delta (discrete Morse theory, shellability); proved | A |
| 4 | A radius-r law with k hidden labels that allows a chain of (2r + 1)k^(2r+1) + 2r + 3 knots allows a ring; the open-end rule never grows one. In two dimensions a law excludes flat tori exactly when its flat configurations are aperiodic, and the seam law allows every flat torus. | known-with-delta (pumping, proof-labeling schemes, aperiodic tile sets); proved | A |
| 5 | Grown outward from one tile by its own label-free collar law with coins, the pinwheel left its patches in all 70 runs of four orders (66 dead ends within 304 tiles; 4 forced-first runs reached 500 tiles of non-pinwheel collar-legal patches); genuine continuations are never rejected. | not found in prior work (deceptions: Dworkin and Shieh 1995); exploratory experiment | B |
| 6 | Replaying ticket B's runs, the first move that left the pinwheel's patches was always a coin, never a forced move (70 of 70), usually where 1 of 2 or 3 options was right. | exploratory experiment | C |
| 7 | An oracle keeping the right options grew 1,000 tiles in 15 of 15 runs, supplying 4.0 to 9.6 bits after the seed against 45.7 to 88.1 bits of apparent choice; 693 of its 775 choices had one right option. | not found in prior work; exploratory experiment | C |
| 8 | The collar law plus the radius-2 atlas dead-ended in 40 of 40 runs: it changes when growth fails, not whether. | consistent with Dworkin and Shieh (1995); exploratory experiment | C |

## Answer

A growth order never knots with the grown pattern; written into the law it adds a history whose local part is pairwise and whose global
part, time without a loop, is a knot on every cycle, so a beginning is a knot. What growth adds is whether a grown pattern has a beginning:
in one dimension that is what grows the number line, and no bounded static witness replaces it; on spheres it is free; in the
round plane growth cannot stand in for the hidden structure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with knots across time (G5), awaiting the owner's go-ahead under the wrap-up request: read Ledrappier's law as the
space-time law of rule 60 and classify the temporal knots of rules 90, 150 and one nonlinear rule. Rated Payoff 2/3 (Substantial),
Concreteness 2/3 (Testable). The table is in the decision note.
