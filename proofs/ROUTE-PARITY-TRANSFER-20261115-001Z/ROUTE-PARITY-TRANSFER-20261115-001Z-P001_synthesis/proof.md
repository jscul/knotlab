# Proof length after encoding strict 3-SAT as two-use routes

Status: Proved

## Accepted conclusions

- A single signed-literal and constant substitution maps every axiom and every guard pin of the compiled formula to a tautology or to a selected source clause, with exactly the listed multiplicity. [A, candidate-local-delta](../../ROUTE-PARITY-TRANSFER-20261115-001A/ROUTE-PARITY-TRANSFER-20261115-001A-P001_literal_projection/proof.md)
- Every S-line DAG refutation in parity resolution with one-premise semantic weakening projects to a checked source refutation using at most S lines and no more resolution depth. Conversion costs polynomial work in the supplied encoding. [B, candidate-local-delta](../../ROUTE-PARITY-TRANSFER-20261115-001B/ROUTE-PARITY-TRANSFER-20261115-001B-P001_dag_transport/proof.md)
- Pang v2 Theorem 7.2(a), specialized to degree one and characteristic two, supplies an exponential node lower bound with high probability for 8n independently sampled uniform strict ternary clauses. The local one-premise semantic weakening convention preserves an exponential node bound. [C, known-overlap-found](../../ROUTE-PARITY-TRANSFER-20261115-001C/ROUTE-PARITY-TRANSFER-20261115-001C-P001_source_admission/proof.md)
- With probability tending to one, the two-use guarded route formulas induced by the density-eight source require exp(Ω(r)) parity-resolution nodes on listed schedules and exp(Ω(r^(1/3))) on uniform fixed schedules of r stages. [D, candidate-local-delta](../../ROUTE-PARITY-TRANSFER-20261115-001D/ROUTE-PARITY-TRANSFER-20261115-001D-P001_encoded_lower_bound/proof.md)

The synthesis binds the accepted conclusions and the decision note. The scientific arguments and independent checks are in the linked proof records.
