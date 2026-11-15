# How much must be remembered before a joint crossing test?

A sender receives an arbitrary set of allowed joint states on $b$ pairs of three-label strands. A reader later specifies one crossing power and desired label per pair and asks whether **one and the same state** passes them all. Let $L_b$ count the bits in the shortest deterministic fixed-length message that answers every such question without further access to the table.

The exponential base of the required message is exactly six: $\lim_{b\to\infty}L_b^{1/b}=6$. At one pair, five is the largest number of states that can each be picked out individually within the chosen set. At eight pairs the construction singles out 459,270 states; choosing five per pair supplies 390,625. Each subset of the larger set gives a different answer to some future query, so 459,270 is a lower bound in **bits**, independent of how the sender encodes the data. [Finite certificates](../../proofs/JOINT-BRAID-READS-20261114-001A/JOINT-BRAID-READS-20261114-001A-P001_finite_certificates/proof.md)

The lower bound for every $b$ is $3^b\binom{b}{\lfloor b/2\rfloor}$. A two-level submatrix lets a test mistake a member at one level for a member at the other in only one direction. On strings with a fixed number of high-level members, a successful confusion would need a mistake in both directions. For the upper bound, choose a smallest subset generating a report. Every retained state needs a test private to it in that subset. The ternary incidence matrix has rank six over the three-element field and its $b$th tensor power has rank $6^b$. Describing that many state indices costs $O(b6^b)$ bits. These bounds leave the exact polynomial factor open. [Message-growth proof](../../proofs/JOINT-BRAID-READS-20261114-001B/JOINT-BRAID-READS-20261114-001B-P001_message_growth/proof.md)

Correlations matter: if the input itself is a Cartesian product, there are precisely $1+109^b$ possible joint reports. The fixed message then grows linearly in $b$. The empty product report accounts for the initial one and each nonempty report determines its nonempty one-pair factors. Changing the order of communication matters too: the reader can send one of $9^b$ questions first and receive a single answer bit. This protocol charges communication only. Sender computing time is unbounded; an explicit joint truth table would itself take $9^b$ membership bits. These bounds give no general lower bound for deciding one formula. [One-pair baseline](../BRAID-READOUT-20261114-001/decision.md)

The Boolean cut function and the interplay of triangular submatrices, matrix powers, and representative sets are established theory. The concrete certificates and rate identify what that theory implies for this particular crossing. At eight pairs the referee directly tested 37,200,870 compatible word pairs and found exactly the claimed 459,270 diagonal hits of the fixed-weight kind. [Bui-Xuan, Telle and Vatshelle](https://arxiv.org/abs/0903.4796) · [Groenland and coauthors](https://doi.org/10.4230/LIPIcs.ICALP.2024.77) · [Prior-work comparison](preregistration.md)

| Scope | Verdict | Evidence |
| --- | --- | --- |
| This attempt — one exact advance message | **Status:** Successful | Matching exponential bases for all deterministic encodings. |
| Local direction — improving polynomial factors | An exact gap remains | This would refine the communication estimate within the same model. |
| Broader exploration — actual Boolean rules | Change angle | A short supplied formula may answer a single query without first sending any table. |
| Long-term — G16 and G3 | G16 gained a restricted asymptotic result | Reversing when the question arrives invalidates the communication lower-bound inference for ordinary SAT. |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step and stopping condition | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Fixed overlap in explicitly supplied strict 3-CNF rules | 3/3 | 3/3 | Compare all ternary projections before pins and the effort to decide the pinned problem; stop at a counterexample or a matching proof. | Selected |
| 2 | Determine the polynomial factor between the two message bounds | 1/3 | 2/3 | Check finite product examples; stop if only the existing asymptotic rate survives. | Deferred |

**Basket:** BRAID-COUNTS-20261114-001#1 taken here; BRAID-READOUT-20261114-001#1 supplied the predecessor. Corrections: none to an accepted claim. Goals: G16 checkpoint; ordinary SAT time in G3 stays open. Assumptions: Arbitrary tables, a fixed-length exact message, and its time order are stated hypotheses with explicit competitors. Two research leaves and one synthesis.

## Final report as sent

2026-11-15 07:08:15 UTC. Epic 3 proved the growth rate. With b crossed pairs, the shortest exact summary for every possible later joint test grows with exponential base 6. If the question can come first, it takes only the question and one yes/no reply. For the fourth epic I’m testing what happens when a solver gets an explicit Boolean formula with the same pattern of overlapping triples.
