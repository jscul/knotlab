# How much proof survives the two-use route encoding?

A short parity refutation of these routes would give a refutation of the original clauses with at most the same number of lines. This is stronger than ordinary SAT equivalence. The encoding introduces many hidden choices. A single signed substitution fixes those choices consistently for every proof step. Each guarded clause becomes a tautology or one selected source clause. Any parity test may mention any number of the route variables, and a deduction may reuse an earlier line. [Axiom projection](../../proofs/ROUTE-PARITY-TRANSFER-20261115-001A/ROUTE-PARITY-TRANSFER-20261115-001A-P001_literal_projection/proof.md) · [Proof transformation](../../proofs/ROUTE-PARITY-TRANSFER-20261115-001B/ROUTE-PARITY-TRANSFER-20261115-001B-P001_dag_transport/proof.md)

The inherited lower bound therefore applies to every proof in this system, even one discovered by an entirely different search algorithm. On a list of eight random strict clauses per variable, with probability tending to one it is exponential in the number of stages when wiring is made from the list. On wiring fixed for all inputs with the same variable count, it is exponential in the cube root of the number of stages. The source is Shuo Pang's October 2026 preprint. Its argument supplies the asymptotic lower bound. We checked the conventions and proved a polynomial node simulation for one-premise semantic weakening. This bounds explicit refutation length. An unrestricted algorithm can answer the decision question by a different method. [Source admission](../../proofs/ROUTE-PARITY-TRANSFER-20261115-001C/ROUTE-PARITY-TRANSFER-20261115-001C-P001_source_admission/admission.json) · [Encoding and input-size bounds](../../proofs/ROUTE-PARITY-TRANSFER-20261115-001D/ROUTE-PARITY-TRANSFER-20261115-001D-P001_encoded_lower_bound/proof.md) · [Pang v2, Theorem 7.2(a)](https://arxiv.org/html/2610.00837v2#S7)

In end-to-end replays, 4,112 guarded proof nodes became 415 source nodes on three variables, and 5,964 became 590 on a four-variable fixed catalogue. Each included a surviving two-variable parity cut. A separate check evaluated every source line on every assignment. The first and second sample sizes exercise the translation, while the density-eight probability law comes from the source theorem. [Replay evidence](../../proofs/ROUTE-PARITY-TRANSFER-20261115-001D/ROUTE-PARITY-TRANSFER-20261115-001D-P001_encoded_lower_bound/checks.json)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt, transport parity proof length | Successful | Every target proof gives an equally short or shorter source proof. |
| Local direction, guarded two-use encodings | Continue | The map and proof converter are reusable. |
| Broader exploration, shortcuts for SAT | Known alternatives | Nesting and implication reachability already yield short decisions on other layouts. |
| G3 Hardness at three places; G16 Learning the rules behind what a system allows | Capability gained | One proof model is controlled; the all-solver question remains open. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Search permitted branch orders for a cheap decision | 3/3 — decision algorithms | 3/3 — explicit swaps | Minimize names that interrupt nesting and replay original guard witnesses → an exact bound or counterexample | Selected · started |
| 2 | Transfer another proof model through the same compiler | 2/3 — stronger proof limits | 2/3 — needs matched source | Check closure under the signed substitution and locate an admitted strict-clause source → stop if either fails | Alternative · deferred |
| 3 | Search for a simulation covering unrestricted algorithms | 3/3 — long-term question | 1/3 — no bridge | Identify one solver model outside parity resolution and a precise simulation obligation → reassess before any claim | Alternative · deferred |

**Goals:** G3 and G16. The mathematical changes concern supplied Boolean formulas and computed proofs. **Assumptions:** This study inherits the basic parity proof rules and EVIDENCE-001 source policy. It explicitly chose density eight, the sparse and fixed encodings, and the node, word and explicit-bit measures for this comparison. None changes a standing program premise. **Corrections:** The earlier equivalence and tractability results survive. This study adds a proof-resource bridge and does not change a previous theorem. **Basket:** The separately selected branch-order epic owns the predecessor's branch-swap entry.

**Review:** The three scientific components were proved or admitted separately. The source proof-length theorem remains external, and the finite replays and independent internal reviews are V1. The outside design advisor was unavailable under its existing quota. No claim of worldwide novelty is made for affine substitution.

## Final report as sent

One proof method with freely chosen parity tests provably needs exponentially many steps on some two-use guarded layouts, under the admitted source theorem. The constructive question pursued alongside it is how to choose the branch order and group the names on instances that admit a shortcut.
