# When does a branching pattern read its depth?

Fix the target as a fresh distinction of the copy reached by repeating the first recursive call. Let `L(s)` be the minimum size of a knot-bond joining any top distinction to any eligible target at depth `s`. Its other members may lie anywhere in the infinite pattern. The minimum is undefined at depths with no such bond. We measure size in distinctions.

## Two ways a branch can behave

In the new example the first call sends `(a,b,c)` to `(x,a,c)`, and every copy requires `NAE(a,c,y)`. The same top distinction `c` enters the knot with a fresh `y` at every depth. Every possible endpoint pair is free. Hence `L(s)=3` for every positive depth. A second record passes the same port forever but never uses it in any constraint, even inside a side copy. Its value can be chosen separately from every other distinction. Identity matters through the constraints that use it. [The two rules and their exact extensions](../../proofs/BRANCH-DEPTH-20261112-001B/BRANCH-DEPTH-20261112-001B-P001_bounded_depth/proof.md)

In a forgetting rule, a run of `r` unobserved levels can join any realizable input on the left with any realizable output on the right. Leaving such a gap makes the two parts of a proposed bond independently realizable. Consequently every bond to depth `s` needs at least `1 + ceil(s/r)` members. An explicit chain of knots, each of which lifts from every allowed incoming assignment, ensures existence at every depth with at most `s+3` members. The unobserved port relation alone cannot determine growth. Two concrete rules have the same relation and different behavior. [Gluing, upper construction and counterexamples](../../proofs/BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/proof.md)

There is a different exact test for a fixed maximum size `k`. After projecting all other distinctions away, there are finitely many possible relations on the ports and at most `k−1` marked variables in a subtree. Closing this collection under all finite placements of the marks includes arbitrary side supports. On a fixed repeating branch, the resulting sequence of finite states eventually repeats. Thus the exact set of depths reachable with at most `k` distinctions is computable for each specified `k`. This does not give a uniform test for whether *some* finite `k` works at every depth. On the previous growing example it gives the exact minima **3, 3, 4, 4, 5, 5** at depths one through six. [Fixed-size proof and executable tests](../../proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/proof.md)

## All 664 sampled one-definition rules

Every eligible record was drawn from the same eight archived sample files and has an allowed state in the usual infinite limit after dying at a finite depth. A knot-bond has at least three distinctions. A two-variable tie is recorded separately.

| Broad behavior | Records | Evidence |
| --- | ---: | --- |
| Bounded | **432** | **393** have exact minimum three at every positive depth. **39** have size at most four everywhere and exact minimum four from depth eight onward, often earlier. |
| Linear growth | **69** | For every depth there is a bond, and all bonds to that depth obey a linear lower bound, even with arbitrary side support. |
| Linear lower bound with existence open | **154** | A bond to depth `s`, whenever one exists, must grow at least linearly with `s`. |
| Larger sizes unresolved | **9** | Size three eventually fails. These records have no general verdict on larger sizes from this study. |

The computation gives exact certificates for the sampled records at all positive depths. Relative frequencies refer only to those records. The four verified ways of strengthening the initial comparison are a rectangle on just the reachable port states, a helper in a side copy, forgetting port slots that never occur in any constraint, and unrestricted placement at fixed size. [Census, individual certificates and replay](../../experiments/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/FINDINGS.md)

The separate ray study follows the same first branch with a narrower support search and includes size-two ties in its reported minima. Its referee confirmed the finite values and 194 bounded ray cases, and withdrew the growth classification. The depth-30 trends answer a different observation question. The counts above come from the archived usual-limit inputs. [Ray study](../BOND-DEPTH-20261112-001/bond_depth.md)

## Interpretation and prior work

Increasing bond size means that a relation between a top distinction and a fresh target needs more participating distinctions. The recursive presentation supplies the depth index. A fixed support can still encode a periodic dependence on depth. On sample 0, line 4582 the same three top ports and one target local forbid a different complementary pair of states at odd and even depths, although the least size is four at every depth from three onward.

Finite relation powers and automata on trees are classical. The fixed-size proof constructs the exact marked port tables directly for these rules. No claim of field-wide novelty or of native finite-flip sources at an infinite solution is made. [Rabin, *Decidability of second-order theories and automata on infinite trees*](https://research.ibm.com/publications/decidability-of-second-order-theories-and-automata-on-infinite-trees)

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — transfer depth reading beyond the first example | **Status:** Successful | A second genuine family has the opposite exact behavior. The sufficient criteria separate 501 of 664 sampled records into bounded and genuinely linear groups. |
| Local direction — what makes a branch remember depth | Continue | Uniform forgetting forces a cost for every unobserved gap. For 154 records the missing step is a bond reaching every depth. |
| Broader exploration — limits of branching patterns | Known alternatives | The fixed-size procedure can decide which depths are reachable for a specified `k`. Exact rates and finite-flip sources are separate questions. |
| G7 Limits and G17 Typical and rare meeting patterns | Capability gained | Depth is readable with a growing number of distinctions in some fixed patterns and with three in others. The distinction can be proved at every depth. |

**Next step:** Continue — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Reach every depth in the rules with a linear lower bound | 2/3 — substantial | 2/3 — testable | Start with sample 0, line 4710, whose two successive copies introduce just four fresh distinctions. Test their 128 possible assignments for a step that repeats and reaches both even and odd depths. | Selected · candidate chosen |
| 2 | Find the exact slope in the original growing example | 2/3 — substantial | 2/3 — testable | Test whether every bond can be reduced to one of the known chains, or exhibit a shorter bond at a depth beyond six. | Alternative |
| 3 | Decide boundedness without choosing a size in advance | 2/3 — substantial | 1/3 — conjectural | Identify a cost that composes across a recursive cut while preserving minimality. Stop at a preserving composition or a counterexample. | Alternative |

The first direction addresses the largest group for which existence still changes the answer. It can use already checked local extension tables. The original example has exact small values and a constructive upper bound but no matching coefficient. The fixed-size theorem does not by itself give a terminating search over every size.

**Corrections:** No accepted conclusion needed correction. The root-to-fresh-target convention is explicit, and the counts use the usual limit and the three-variable minimum arity for a knot. **Goals:** G7 and G17 gained a checkpoint. Their wording and status are unchanged. **Assumptions:** The archived sampling convention in A79 is used to identify records. No weighting or independent-source hypothesis is added.

**Basket:** BOND-BALLS #2, ACROSS-FOLD #3 and FAR-BOUND #2 were first in the spacing basket. They concern different bases. The owner selected the branching-depth issue from BONDS-AND-COUNT #1. The current recommendation builds on the verified positive and negative cases for that issue.

**Discovery disposition.** New D001 records the sufficient lower and upper tests for linear growth, and D002 records decidability of reachable depths at any fixed size. The contrasting single rule is an application; the 664-case study has exploratory status. The controls, sharp small-depth values, and source-zero closure are supporting evidence. No earlier entry was retained, superseded, or withdrawn. The generated discoveries index has the disposition `maintenance required`. [Accepted synthesis](../../proofs/BRANCH-DEPTH-20261112-001Z/BRANCH-DEPTH-20261112-001Z-P001_synthesis/proof.md) · [Durable disposition](discovery_disposition.json)

## Final report as sent

2026-11-12T20:06-08:00

**Depth forces larger bonds in 69 of the 664 sampled rules. In 432 others, three or four distinctions suffice at every positive depth.** I fixed the target on the first recursive branch and let a bond use distinctions anywhere in the infinite pattern, including side branches beyond the target. A bond here has at least three members. They are constrained together, and forgetting any one leaves the rest free. [Census and individual results](https://github.com/jscul/knotlab/blob/main/experiments/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/FINDINGS.md)

| What happens as the target gets deeper | Sampled rules |
| --- | ---: |
| The least bond size is exactly 3 at every positive depth | 393 |
| The least size is at most 4 at every positive depth and exactly 4 from depth 8 onward | 39 |
| A bond exists at every positive depth and its least size grows linearly | 69 |
| Every bond obeys a linear lower bound. Existence at every depth is open | 154 |
| Three eventually stops working. Larger sizes remain unresolved | 9 |

The growth proof turns on what an unobserved stretch can forget. Suppose that after three levels every possible incoming value can combine with every possible outgoing value. A bond spanning that stretch must include a distinction there, because otherwise its two ends can vary independently. Each such stretch adds to the cost. In a contrasting rule, the same top distinction participates in a fresh three-member bond at every depth. [Forgetting proof](https://github.com/jscul/knotlab/blob/main/proofs/BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/proof.md) · [Bounded example](https://github.com/jscul/knotlab/blob/main/proofs/BRANCH-DEPTH-20261112-001B/BRANCH-DEPTH-20261112-001B-P001_bounded_depth/proof.md)

We also proved that **for any fixed maximum bond size, the depths it reaches can be computed exactly**. After a finite beginning, the answer repeats. In the original growing example, the exact least sizes at depths one through six are **3, 3, 4, 4, 5, 5**. Its exact long-run growth rate remains open. [Fixed-size proof](https://github.com/jscul/knotlab/blob/main/proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/proof.md)

**I’d pursue the 154 next.** We already know how much any bond reaching a deep target must cost. What would change the answer is a construction that reaches every depth.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Build a bond at every depth in one of the 154 rules | 2/3 | 2/3 | Test the 128 two-level assignments in sample 0, line 4710, for a repeatable step covering even and odd depths | Selected |
| 2 | Find the exact rate in the original rule | 2/3 | 2/3 | Prove the known construction is shortest or find a shorter bond beyond depth six | Alternative |
| 3 | Decide whether some finite size suffices for all depths | 2/3 | 1/3 | Test whether minimum size can be tracked exactly across one recursive call | Alternative |

The counts apply to these 664 archived records. The two general proofs and the remaining questions are in the [research note](https://github.com/jscul/knotlab/blob/main/research/BRANCH-DEPTH-20261112-001/depth.md).
