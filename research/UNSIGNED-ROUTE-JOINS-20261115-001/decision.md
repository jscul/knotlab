# Where the original two-route scan first breaks

Start with true $x_0$, false $x_r$, and two independently switched implication routes $x_{i-1}\to a_i\to x_i$ and $x_{i-1}\to b_i\to x_i$ per stage. Each implication keeps its own six input switches. Here two or more middle variables can denote the same Boolean value. An edge occurrence remains distinguishable by its own switches. The endpoint units keep their twelve switches apiece.

An equality within a stage permits entry on one branch and exit on the other. An equality across stages permits jumping over a boundary. Consequently the original named-branch scan is correct on every input exactly when all middle variables are distinct. Two stages already suffice for a contradiction with neither stage individually complete. Testing all live implications by reachability on their actual variable names decides the same inputs in linear time on an indexed adjacency representation. If the source cannot reach the negative endpoint, assigning true to precisely the reached variables gives a satisfying assignment to the implications; private padding and witnesses extend it. [Decision and controls](../../proofs/UNSIGNED-ROUTE-JOINS-20261115-001B/UNSIGNED-ROUTE-JOINS-20261115-001B-P001_joined_reachability/proof.md)

Counting the minimally constrained switch sets alone misses the first change. Identifying the two middles in one stage doubles their number. Joining one middle in each of two stages $d$ places apart leaves $3\cdot 2^{r-2}$ long minimal paths and adds $2^{r-d-1}$ shorter ones. At $d=1$ their sum is exactly the old $2^r$. The actual allowed switch states still change. At $d>1$ there are fewer minimal paths than before. Each minimal path contributes all its own edge-switch blocks and both endpoint blocks. [Counts and direct formula checks](../../proofs/UNSIGNED-ROUTE-JOINS-20261115-001A/UNSIGNED-ROUTE-JOINS-20261115-001A-P001_single_join_census/proof.md)

As an independent check, at four stages with a join between stages two and four, the referee tested all 65,536 patterns of live implications against the guarded strict CNF. The old scan missed 5,943 contradictions. Further checks classified 101,568 labelled paths across all 4,083 choices of a single repeated middle class among twelve occurrences at six stages. A three-stage example even forces the order of visited boundaries to be 0, 2, 1, 3.

The equality-domain two-route example was published in 2003. The exact unguarded directed Boolean baseline, including its path count, also appears in Kleine Büning (2024), §5, Fig. 2. The one-join census, decision changes and strict-switch transfer are the specific results discussed here. The Fable design advisor's existing weekly limit remains in effect. A separate referee checked the comparison. [Kleine Büning](https://doi.org/10.1016/j.tcs.2024.114538) · [García de la Banda, Stuckey and Wazny](https://doi.org/10.1145/888251.888256) · [Preregistration](preregistration.md)

| Scope | Status | Finding |
| --- | --- | --- |
| This attempt | Successful | A single identified middle gives a falsifiable counterexample to the independent-stage scan. |
| Local direction | Tested | Reachability on shared names works for arbitrary positive identifications; one-join support counts are exact. |
| Broader exploration | Continue | Measure memory at a stage boundary with several shared names |
| Long-term G3 and G16 | Scoped capability | A procedure using a different grouping decides the original source inputs in linear time. |

**Next step:** Continue — Measure memory at a stage boundary with several shared names

| # | Direction | Payoff | Concreteness | First step and stopping condition | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Measure memory at a stage boundary with several shared names | 2/3 | 3/3 | Compare all future implication tests, compile the full comparison to the two-route formula and stop at matching memory bounds or a counterexample. | Selected |
| 2 | Extend the single-join census to several distinct joined classes | 1/3 | 2/3 | Try the smallest new case and stop if it only repeats the current classification. | Deferred |

**Corrections:** The previously credited 2003 equality example has a direct published Boolean counterpart in Kleine Büning (2024). The earlier strict-switch cost calculations stand. Novelty narrowing reported to the owner.

**Goals:** G3 and G16. The finding concerns the explicit Boolean systems and cost model above.

**Assumptions:** No change to a standing premise. Supplied wiring, observation order and existential status of variables are stated with each claim.

**Basket:** SIGNED-KNOT-OVERLAP-20261114-001#1 proposes comparing flat and factored descriptions. This owner-selected change varies the actual identities and leaves that earlier suggestion open.

**Basis:** Exact proofs and independent enumeration; the program's knot verdict concerns allowed states under forgetting. No native recurrence construction is asserted. 

## Final report as sent

2026-11-15 07:51:14 UTC. Epic 1 is complete. Joining middle choices from adjacent stages leaves the number of minimal contradictions unchanged, yet changes which inputs are satisfiable. Grouping occurrences by the variable they share recovers a linear-time decision rule. I’ll now test what a stage-by-stage reader must remember to get the same answer.
