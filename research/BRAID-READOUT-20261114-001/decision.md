# What survives every one-strand test

The crossing on a pair of labels sends $(x,y)$ to $(y,2y-x)$ modulo the alphabet size. For each number of crossings and each label, a reader asks whether any allowed pair places that label on the first strand. The second strand advances the same test by one crossing. A summary committed before the question is known must preserve all these answers.

For three labels, one, two and three distinct crossing positions distinguish respectively 8, 50 and 110 classes among 512 possible input tables. The exact worst-case message lengths are 3, 6 and 7 bits. With all positions, 73 tables are uniquely determined and 214 give yes to every question. [Finite classification](../../proofs/BRAID-READOUT-20261114-001A/BRAID-READOUT-20261114-001A-P001_power_menu_census/proof.md)

For prime alphabet size $p$, every input table with fewer than $p$ states is determined, even against larger competitors. At size $p$ the first disjoint ties consist of two entire constant-difference families. Ties differing in one state correspond to permutations with no fixed positions on $p-1$ positions. At $p=5$ the two counts are 10 and 2,250. [Sparse recovery and equalities](../../proofs/BRAID-READOUT-20261114-001B/BRAID-READOUT-20261114-001B-P001_sparse_tables_and_extremal_collisions/proof.md)

The classical Reed–Solomon cover-free bound already gives the below-threshold result. Füredi and Ruszinkó use the tight-cover argument behind the disjoint equality case. The local yield is the exact observation census and the single-replacement count. The earlier two-strand study already saved all three masks for each of the 512 input tables and reported the two-position class count. Its saved rows reproduce all seven menus without generating fresh data. The ternary counts here are a reanalysis, independently certified by inclusion–exclusion. The five-label enumeration and the uniform single-replacement count are separate. The earlier result also reported 34 uniquely predictive marginal tables and a 371/512 optimum. A third independent calculation recovered all 110 classes. At the next prime a separate referee tested 10,737,573 possible common sets for each of two fixed pairs, finding 265 ties on the crossing pair and zero on the parallel pair. The Fable design advisor reported its weekly quota exhausted. Separate investigators and the referee supplied the mathematical checks. [Prior-work gate](preregistration.md) · [Earlier two-strand study](../STRAND-RETURN-20261114-001/strand_returns.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — one-strand questions | **Status:** Successful | Exact finite answer classes and two all-prime equality cases established. |
| Local direction — changing the later question | Continue | The large all-yes class makes the reader's choice quantitatively important. |
| Broader exploration — overlapping choices | Known alternatives | Compare counts, then simultaneous tests; a conventional affine description remains available. |
| Long-term goal — G16, recover rules from what can be seen; G3, understand hardness | Capability gained for G16 | The obstruction concerns a message sent before a later test. It measures no lower bound on formula-only SAT time. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Compare existence, parity and exact counts for identical crossings | 2/3 — tests what causes the loss | 3/3 — same finite input and three precise outputs | Compare all tables and look for an all-prime description of identical counts; stop at a proof or counterexample. | Selected |
| 2 | Classify collisions with intermediate overlap | 1/3 — refines the threshold | 2/3 — small examples are available | Test one intermediate size and stop if it only enumerates cases. | Alternative |

Corrections: No terminal research claim changed. Goals: G16 checkpoint; G3 unrestricted decision stays open. Assumptions: The prime alphabet and timing of the message are explicit hypotheses, varied by competing directions. Basket: holes-and-proofs had no untaken direction at payoff two or above. Two scientific families changed the result; one source-zero ledger records closure.

## Final report as sent

2026-11-15 06:50:10 UTC. Epic 1 reanalyzed all 512 three-label tables and certified that they give only 110 distinct answer records across every one-strand crossing test. One answer is shared by 214 tables. I’m continuing with the same crossings and changing only what the reader keeps: existence, parity, or the exact count.
