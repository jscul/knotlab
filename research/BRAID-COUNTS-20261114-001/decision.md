# What counting adds to one-strand tests

A crossing sends $(x,y)$ to $(y,2y-x)$ modulo a prime $p$. Its powers read $x+k(y-x)$. Starting from a set of possible pairs, the same label test can return whether it found any state, the parity of the number found, or the exact count.

With three labels, the four numbers of distinct records among all 512 tables are 110 for existence, 128 for parity, 399 for existence and parity together, and 490 for exact counts. The corresponding minimum fixed message lengths are 7, 7, 9 and 9 bits. Two named difference-class parities complete the original parity data at three labels. Two named difference-class presence bits complete the original exact counts. [Finite classification](../../proofs/BRAID-COUNTS-20261114-001A/BRAID-COUNTS-20261114-001A-P001_reader_comparison/proof.md)

An exact-count tie exchanges equally many full and empty classes of constant $y-x$. A parity tie can complement an even number of entire classes, including partially occupied classes. If any test originally says no, any nonempty such change puts a state into that test. Consequently any table reporting even one no is uniquely identified by its existence and parity data together. An ambiguous table with precisely $p$ states must occupy an entire difference class, since full coverage by $p$ states requires that their observed labels never meet. Its complete joint class consists of odd unions of whole classes and has $2^{p-1}$ members. At five labels the five exceptional size-five tables share a class of 16, with 5, 10 and 1 tables of respective sizes 5, 15 and 25. The independent referee tested every five-label table using explicit crossings. [Uniform proof and limits in characteristic two](../../proofs/BRAID-COUNTS-20261114-001B/BRAID-COUNTS-20261114-001B-P001_count_fibres/proof.md)

The count kernel specializes classical finite-transform results. Sin, Sorci and Xiang give the rank and parallel-class differences over fields of characteristic different from $p$; the proof handles the binary case directly. The mixed Boolean conclusion and matched census are local to these observations. Parity of the number of witnesses is a different operation from solving a supplied system of XOR equations. [Sin, Sorci and Xiang](https://arxiv.org/abs/1908.06824) · [Prior-work comparison](preregistration.md)

| Scope | Verdict | Evidence |
| --- | --- | --- |
| This attempt — counting the states a crossing test accepts | **Status:** Successful | Uniform ambiguity criteria and matched census; complete independent five-label threshold check. |
| Local direction — one-pair tests | Change the question | A single no suffices for recovery with joint observations. Larger ambiguities remain connected to full coverage. |
| Broader exploration — shared choices | Continue | Several simultaneous conditions on one allowed state test the correlation between pairs. |
| Long-term — G16 and G3 | Capability gained for G16 | Only the size of a message before future questions was counted. An algorithm handed one formula can proceed differently. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step and stopping condition | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Simultaneous existence tests on several crossed pairs | 3/3 | 3/3 | Bound the shortest exact message as the number of pairs grows; stop at matching exponential rates or an explicit gap. | Selected |
| 2 | More ternary missing-direction statistics | 1/3 | 3/3 | Count the additional observations needed; stop if they only refine this one reader. | Deferred |

No terminal correction or new standing assumption. The prime field, allowed tables and reader are explicit hypotheses. Two scientific leaves and one synthesis. The declared basket had no untaken competing high-payoff entry. The separate referee also identified the direct classical rank source and independently addressed the binary exception.

## Final report as sent

2026-11-15 07:01:17 UTC. Epic 2 found that parity resolves nearly all of the smallest ambiguities. With five labels, only five of the 53,130 five-state tables still have a competitor giving the same existence and parity answers. The referee checked all 33,554,432 possible competitors. I’m moving to tests that require several pairs to agree on one shared choice.
