# Closure of the competition epic

Status: Proved

Epic `KNOT-COMPETITION-20261019-001` was closed on 2026-10-19 after both of
its tickets ended. This is a ledger, one line per conclusion with its novelty
label and evidence. It makes no new claim. The decision note is
`research/KNOT-COMPETITION-20261019-001/competition.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: a shape is a free complex; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On three Boolean variables, a relation that is constrained as a whole but has every one-variable projection full is the minimizer set of a quadratic pseudo-Boolean function exactly when its two excluded points are complementary. These are the four not-all-equal relations, the minimum-violation states of frustrated triangles. | known-overlap-found | `KNOT-COMPETITION-20261019-001A-P001` (Lean) |
| 2 | On four or more variables, no such relation is the minimizer set of a quadratic pseudo-Boolean function. | candidate-local-delta | `KNOT-COMPETITION-20261019-001A-P001` (Lean) |
| 3 | With auxiliary variables, every relation on three variables with a satisfying point is the projection of the minimizer set of a sum of violated two-literal clauses. | textbook | `KNOT-COMPETITION-20261019-001A-P001` (Lean) |
| 4 | Pairwise constraints that must all hold never have such a relation as their solution set on three or more variables. Minimum-violation states equal satisfying states whenever the system is satisfiable. | known-overlap-found | `KNOT-COMPETITION-20261019-001A-P001` (Lean) |
| 5 | Among 470 translation-invariant agree-or-differ rule systems on rings of 4 to 10 variables, none has two distinct separation values under the strict reading. Under minimum violation, 178 have two, and none has more. | no-overlap-found | `KNOT-COMPETITION-20261019-001B-E001` (exploratory, exact) |
| 6 | On strips and rings of triangles with up to 14 vertices, minimum violation counted per triangle equals the strict not-all-equal law on the triangles, and its separation grows with distance in the strip. Counted once per pair, it has at most two separation values. | no-overlap-found (the equality is Wannier's ground-state condition) | `KNOT-COMPETITION-20261019-001B-E002` (confirmatory, exact) |

The repository owner chose not to decide open question 10 in advance. Both
readings are now mapped, and the decision remains the owner's.

## Position and next action

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: both readings of question 10 | **Status:** Successful | Competition makes exactly the not-all-equal triangle from pairs, none on four or more variables, and every knot with hidden variables. The strict reading makes none. Near and far under competition is inherited from a layout. |
| Local direction: competition as the law for question 9 | Practically exhausted for that purpose | Competition turns a supplied triangulated layout into a chain of knots but does not make the layout. Larger surfaces would refine this, not change it. |
| Broader exploration: the contact-first program | Known alternatives | Laws that build their own layout, such as rewriting and growth rules (crowded: hypergraph rewriting, causal sets). The proof-complexity line behind the ECCC TR26-007 counterexample. A write-up of the foundation and these results. None assessed beyond this epic's search. |
| Long-term goal: logic constructs relative structure without presupposing space | Obstruction learned | Growing separation needs a three-place law or a supplied triangulated layout. Neither strict logic nor competition generates the layout; the missing bridge is a law that creates one. |
| Next recommendation: question 9 | **Next step:** Research directions. Run a bounded search for a law that creates its own layout, starting from the owner's naming recursion, in which each knot names its difference as a new distinction. | Targets the missing bridge directly. Credible alternatives are the proof-complexity line and a write-up. |
| Interest: that search | **1/3 — Exploratory poking** | Every fixed-layout law tested inherits its near and far, so generative laws are the remaining route in the program's terms. Main uncertainty: naming recursions may grow like trees, with no low dimension, and hypergraph rewriting already covers much of this ground. |
| Execution: that search | Deferred | The program's direction is the owner's choice, and this epic's authorization covered its three items. Reassess after about ten queries and one probe. Stop if the generated free complexes are tree-like or add nothing over hypergraph rewriting. |
