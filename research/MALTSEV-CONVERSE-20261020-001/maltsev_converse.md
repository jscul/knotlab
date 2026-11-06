# What composing knots like cycles forces

Epic `MALTSEV-CONVERSE-20261020-001`, closed 2026-10-20.

## The question

`KNOT-CIRCUITS-20261020-001` proved two things:
- a law with a Mal'tsev ("difference") polymorphism composes knots like cycles
  exactly when no subalgebra splits;
- Boolean laws compose like cycles exactly when affine.

It left the converse open: does composing knots like cycles force a difference
operation? The owner asked for this and the space question together ("Do
both").

**The evidence.**
- [The census](../../experiments/MALTSEV-CONVERSE-20261020-001A/MALTSEV-CONVERSE-20261020-001A-E001_converse_census/contract.json),
  with [result](../../artifacts/MALTSEV-CONVERSE-20261020-001A/MALTSEV-CONVERSE-20261020-001A-E001_converse_census/result.json).
- [The proof](../../proofs/MALTSEV-CONVERSE-20261020-001B/MALTSEV-CONVERSE-20261020-001B-P001_converse/proof.md).

## What was found

- **The naive converse is false.** A parity law on {0, 1} placed beside an
  unrelated law gives knots that compose like cycles with no difference
  operation anywhere.
  - Beside x ≤ y on {2, 3}, only ties fail.
  - Beside an isolated-value relation on {2, 3, 4}, nothing fails.

  Knots live where the law is parity. The rest of the domain carries no knots.
- **The converse reduces to one property.** Call a knot **rectangular** when
  its fibres over any variable are pairwise equal or disjoint. If every knot is
  rectangular, knots compose like cycles exactly when no two knots meeting at
  a variable split its range. This holds whether or not a difference
  operation exists.

  So the open question is now only: does composing knots like cycles force
  knots to be rectangular?
- **Settled cases.**
  - A knot whose fibres all meet at some variable forms a hub with a copy of
    itself.
  - So does a knot with a selector, meaning a variable whose every value
    leaves meeting fibres.
  - On two values, every knot of a law that composes knots like cycles is a
    single parity.
- **The open step, with strong evidence.**
  - Some knots have neither direct property. The Boolean knot {000, 010, 011,
    101, 110} is one.
  - For every such 3-variable knot tested (on 2, 3 and 4 values), one fixed
    derivation gives a knot that does:

    K′(x₀, x₁, x₂) = ∃h: K(x₀, x₀, h) ∧ K(x₁, x₂, h)

    This "diagonal" derivation works for some ordering of the variables.
  - The census agrees: all 34 sampled laws that have knots are non-Mal'tsev,
    and all of them have hubs between knots.
- **A correction.** In the previous epic I took the not-all-equal relation
  (NAE) to need a twisted construction. It does not: one of its variables is
  a selector for another.
  - The twisted forms remain correct.
  - The circuits proof is unaffected.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Naive converse false (disjoint unions) | Searching for what the converse should mean | Elementary |
| Converse reduces to rectangular knots | Isolating what the difference-law proof uses | Elementary given the circuits proof |
| Direct hubs (meeting fibres, selectors) | The fibre criterion, extended to two shared variables | Elementary |
| Bits ⇒ every knot is a parity | The Boolean classification | Corollary |
| Diagonal derivation resolves every tested knot | Search over two-copy derivations | Computational evidence; the general statement is open |

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the census and the proof.
- 2 are administrative: this note and the ledger.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the converse of the difference-law theorem | **Partially successful** | The naive form is refuted. The converse is reduced exactly to rectangularity of knots, which is proved on two values and computed for 3-variable knots on up to four values. |
| Local direction — characterizing cycle-like composition | Continue | One concrete statement stands between the program and a full answer to question 3: the diagonal lemma. |
| Broader exploration — the source-aware foundation | Questions 3 and 9 being run together | The space question runs as `KNOT-SPACE-20261020-001`, at the owner's request. |
| Long-term goal — intrinsic structure from logic | Capability gained | Cycle-like composition needs no difference operation as such. It needs rectangular knots and unsplit ranges, a local property. |
| Next recommendation — the diagonal lemma | **Next step:** Continue. Prove that every non-rectangular 3-variable knot with neither direct property has a diagonal derivation with a direct property, or find a counterexample on 5 or more values. Then lift it to knots on 4 or more variables by identifying variables. | It would complete the characterization: knots compose like cycles exactly when they are rectangular and no range splits. |
| Interest — the diagonal lemma | **2/3 — Promising** | Every tested knot of this kind (94 in the exploratory searches and 52 in the proof's checks) satisfies it, and the statement is concrete. The risk is that the derivation is only one of several needed on larger domains, or that knots on more variables escape it. |
| Execution — the diagonal lemma | Deferred | Not started. The owner asked for the space question in the same run. Stop if a counterexample appears on 5 values. |
