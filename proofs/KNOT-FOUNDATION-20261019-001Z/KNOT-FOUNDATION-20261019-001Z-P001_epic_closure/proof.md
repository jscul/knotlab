# Closure of the knot foundation epic

Status: Proved

Epic `KNOT-FOUNDATION-20261019-001`, closed on 2026-10-19 at the repository
owner's request, after the epic met its stop rule. This is a ledger: one line
per conclusion, with its novelty label and evidence. It makes no new claim.
The write-up is `docs/FOUNDATION_READING.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: a shape is a free complex; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Relations definable by 2-CNF with existential witnesses are majority-closed, so none is constrained as a whole while free on every pair. Three-literal clauses with witnesses define every relation. | known-overlap-found | `KNOT-FOUNDATION-20261019-001A-P001`, `KNOT-FOUNDATION-20261019-001E-P001` |
| 2 | Under the forgetting reading, the knots on three variables are the 34 relations whose excluded states are pairwise non-adjacent in the 3-cube, in five classes up to symmetry. A knot on m variables has at least 2^(m−1) states, with equality only for parity. | known-overlap-found | `KNOT-FOUNDATION-20261019-001E-P001` |
| 3 | Proof 0009's executor rule adds a loop's presence as a literal, and the earlier Lean kernel's erasure condition accepts a 2-CNF relation. | candidate-local-delta | `KNOT-FOUNDATION-20261019-001A-P001` |
| 4 | A relation has one least model for every choice of fixed values exactly when it is closed under AND, and negating every variable exchanges closure under AND and OR. Every knot leaves each variable free. Every three-literal clause on distinct variables is a knot, so systems of knots state any 3-SAT instance. | known-overlap-found | `research/KNOT-FOUNDATION-20261019-001/choice.md` |
| 5 | A relation's free sets are the sets it shatters and form a simplicial complex; a knot on m variables is a hollow simplex. Bonds that share one variable compose into a bond or into nothing (resolution). Every simplicial complex is the free-set complex of some relation. | known-overlap-found | `research/KNOT-FOUNDATION-20261019-001/space.md` |
| 6 | Loop presence as a variable dissolved under the forgetting reading. The exploratory dynamic pass stays recorded. | not applicable (retired) | `research/KNOT-FOUNDATION-20261019-001/presence.md` |

The 63 earlier foundations and topology records carry labels under the knot
test in `research/KNOT-FOUNDATION-20261019-001/foundation_triage.md`. The
owner's decisions are recorded in
`research/OPERATIONAL-ARITY-BOUNDARY-001/canonical_correction_request.md`
(K1–K3 adopted) and `research/KNOT-FOUNDATION-20261019-001/canonical_correction_request.md`
(erasure read as forgetting).

## Position and next action

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: ticket D, whether contact structure is space-like | **Status:** Successful | Contact structure has intrinsic holes, paths and a measure of separation. Every free complex is some system's free complex, so logic selects no space. |
| Local direction: the knot foundation epic | Practically exhausted under its stop rule | Each question ended in classical facts plus a reading. The results are kept in the write-up, `tools/knotlab` and two Lean kernels. |
| Broader exploration: the contact-first program | Known alternatives | Space from a uniform local law, a crowded field (causal sets, quantum graphity, hypergraph rewriting). The proof-complexity line behind the ECCC TR26-007 counterexample. Neither has been assessed for novelty here. |
| Long-term goal: logic constructs relative structure without presupposing space | Obstruction learned | Logic gives knots, holes and separation but selects no space. The missing bridge is a law. |
| Next recommendation: the contact-first program | **Next step:** Full pivot. Leave foundation research. The next action is a bounded comparison of three options: space from a law, the proof-complexity line, and stopping. | The foundation is complete as a reading of known logic. No further foundation epic is justified without a new question. |
| Interest: the bounded comparison | **1/3 — Exploratory poking** | Space from a law is heavily studied, and there is no evidence yet that bonds or free complexes give an edge. The proof-complexity line has one verified external result but no assessed successor. |
| Execution: the bounded comparison | Deferred | The program's direction is the owner's choice. The epic was closed at the owner's request. |
