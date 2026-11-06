# Closure of the Res(⊕) bit-PHP audit

Status: Proved

Epic `BPHP-RES-PARITY-AUDIT-20261019-001` was closed on 2026-10-19, after both
of its tickets ended. This is a ledger: one line per conclusion, with its
novelty label and evidence. It makes no new claim. The decision note is
`research/BPHP-RES-PARITY-AUDIT-20261019-001/audit.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The Lean formalization of Braun's exponential lower bound for the bit pigeonhole principle in DAG-like Res(⊕) (arXiv:2609.23015, commit `8904bf09`) builds from source with Lean 4.34.0-rc2 and the pinned Mathlib. All 7 declarations the paper cites depend only on `propext`, `Classical.choice` and `Quot.sound`, and the aggregate passes a fresh kernel replay. | known-overlap-found (replication of the author's published procedure) | `BPHP-RES-PARITY-AUDIT-20261019-001A-E001` (confirmatory replay) |
| 2 | The formal statement means what the paper claims. Its proof system contains every standard rule set of DAG-like Res(⊕) (any sound inference from at most two earlier lines over linear clauses, reuse unrestricted, size counting every line), and its initial clauses are exactly the usual BPHP clauses with 2^ℓ + 1 pigeons and all 2^ℓ labels. | known-overlap-found (audit of an external statement) | `BPHP-RES-PARITY-AUDIT-20261019-001B-P001` |
| 3 | The statement is not vacuous. The formal clause set is unsatisfiable for every ℓ, and the formal system refutes the instance ℓ = 1 in 11 lines. Both witnesses are checked in Lean against the author's definitions. | elementary | `BPHP-RES-PARITY-AUDIT-20261019-001B-P001` |

No gap was found. The prose proof and the novelty claim were not assessed.

## Position and next action

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: independent audit of Braun's Res(⊕) lower bound | **Status:** Successful | The from-source replay passed, the definitions are faithful, and the statement is not vacuous. The prose proof and the novelty claim are outside the audit. |
| Local direction: the repository's depth-restricted Res(⊕) line (affine erosion, ECCC TR26-007) | Retire for bit PHP | An unrestricted bound supersedes depth-restricted routes for this formula. The TR26-007 counterexample remains a separate correct result. |
| Broader exploration: the proof-complexity program | Known alternatives | Braun's Theorem 9.1, already formalized, bounds Res(⊕) size for any clause set with a dense separated space of low-degree polynomials, and no second formula is known (Remark 9.3). The paper also leaves open unary PHP in Res(⊕), AC⁰[2]-Frege, and resolution over linear equations modulo p > 2. |
| Long-term goal: proof-complexity lower bounds | Capability gained (external) | A frontier result is now independently checked here, and later work can build on its machine-checked criterion. There is no consequence for P versus NP. |
| Next recommendation: the proof-complexity program | **Next step:** Continue. In a fresh epic, search for a second formula family with a dense separated space for Theorem 9.1, starting with exact linear algebra on small instances: unary and functional PHP, the ordering principle, random 3-CNF. | This builds directly on the checked result and reuses its formalized criterion. |
| Interest: that search | **2/3 — Promising** | The paper poses it as an explicit open problem, the formal infrastructure exists, and small instances give a cheap discriminator. Main uncertainty: dense separated spaces may be specific to the bit encoding, since the paper knows none for unary PHP, and specialists will pursue the same question. |
| Execution: that search | Deferred | It needs the owner's go-ahead. Sending this audit to the author is also the owner's call. Stop if no candidate shows separated density that grows with size at small n. |
