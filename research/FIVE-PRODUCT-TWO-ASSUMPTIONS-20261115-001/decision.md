# Can a second assumption make a reusable proof cheaper?

Both proposed deductions leave the optimum at **23** when the proof may choose whether to learn one. Each one can be cited twice on branches where it makes a genuine deduction. Reaching total cost 21 or 22 is impossible with either rule.

## The fixed problem

Write \(p_i=x_{i-1}x_i\) for the five products and \(Q=\bigoplus_{i=1}^5 p_i\). The nine visible bits are \(x_0,\ldots,x_5,s,u,v\). The reporting evaluator requires \(s=Q,\ u=p_1,\ v=p_2\oplus p_3\), so \(v=x_2(x_1\oplus x_3)\) on its rows. The other evaluator requires \(s=1\oplus Q\) and allows all values of \(u,v\). A joint proof may ask any visible XOR, check the full affine consequences of one evaluator on the current assumptions, or cite a learned consequence whose guard follows from equations already earned there. Each operation costs one. A stored deduction costs its whole proof against the opposite conclusion. The ordinary optimum of 23 and the lower bound of 23 with one affine equation as premise and one as conclusion come from the immediately preceding study. [Accepted proof and cost convention](../FIVE-PRODUCT-TOTAL-WORK-20261115-001/decision.md)

## Why both five-unit deductions fail to beat 23

Fix \(a\in\{0,1\}\). Compare the requested rule \((v=0,\,x_2=a)\Rightarrow x_0=0\) with \(x_2=a\Rightarrow x_0=0\). Proving the second costs just as much as proving the first. Assume \(x_0=1,\ x_2=a\), leave \(v\) free, and ask \(x_4=c\). Then

\[
Q=x_1\oplus a(x_1\oplus x_3)\oplus c(x_3\oplus x_5).
\]

In each answer this is affine in the remaining bits. The reporting evaluator supplies \(s=Q\). The other evaluator closes the branch. One question and two checks per answer cost **five**. The same proof works under the extra assumption \(v=0\). Five is necessary even there. On the further restriction \(x_1=x_3=u=v=0\), the two evaluators impose opposite values of \(s\) for the product \(x_4x_5\). Both sets of four rows span the full three-bit space, so they require a question and at least two operations in each answer. These conditional deductions are obtained by refuting the opposite conclusion using both evaluators. [Guard comparison and original-coordinate controls](../../proofs/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001A/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001A-P001_guard_comparison/proof.md)

Now take any main proof using the requested rule. Keep every question, every evaluator check that establishes its assumptions, and every citation. Wherever the current equations establish both \(v=0\) and \(x_2=a\), they establish \(x_2=a\). Replace each citation by one use of the broader rule. It adds exactly the same equation \(x_0=0\). By induction every subsequent cell, including the cells of live consumers, stays identical. The broader training costs five. A 21- or 22-unit proof for either proposed rule would therefore give one with a single affine premise at the same or smaller cost, contradicting the checked lower bound of 23. The direct tree that asks \(x_0,x_2,x_4\) attains 23 with no named deduction. [All one-premise implications](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/one_premise.md)

## Paying for repeated uses

For \(a=0\), first ask \(x_2\). On answer zero a paid reporting-evaluator check gives \(v=0\). For \(a=1\), first ask \(x_2\oplus v\). On answer one a paid reporting check gives \(x_2=1,v=0\) and \(x_1=x_3\), since its rows satisfy \(v=x_2(x_1\oplus x_3)\). In each example the two actual affine guard equations are now available to both children. Split on \(x_1\). Each child cites the rule, asks \(x_4\) and closes each answer with a reporting check followed by an opposite check. That part costs \(1+1+2(1+5)=14\), including the check that establishes the guard, the split on \(x_1\), and two separate paid citations.

| Guard value | Five-unit training | First question | Child containing both citations | Other child | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| \(a=0\) | 5 | 1 | 14 | 11 | **31** |
| \(a=1\) | 5 | 1 | 14 | 15 | **35** |

On the other child ask \(x_0,x_4\). For \(a=0\), \(x_2=1\) is already known and two evaluator checks close each of the four answers. For \(a=1\), the other child knows \(v=x_2\). At each answer a reporting check fixes the first and last contributions to \(s\); an opposite check forces \(x_2=1,\ x_1=x_3\). A final reporting check closes, giving \(3+4\cdot3=15\). In the \(a=0\) witness each citation leaves 16 of 32 previously surviving rows after full local inference. In the \(a=1\) witness each leaves 8 of 16. These numbers come from replaying all 512 visible assignments. [Two live uses, programs and controls](../../proofs/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B-P001_two_live_uses/proof.md) · [Serialized certificates](../../proofs/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B-P001_two_live_uses/certificates.json)

The guard can also be earned independently after the two branches have split. Asking \(x_1\) first, then deriving the guard on each answer, gives checked costs of **32** and **36**. The common-ancestor versions above already pay for the earlier guard deduction and a fresh citation in each child. Across all 511 possible XOR questions, the maximum number of genuinely live uses of the same rule in a tree is four for \(a=0\) and two for \(a=1\). Each live continuation occupies at least eight points, and the retained common fixed sets have 32 and 16 points respectively. These capacities are attained. [Detailed cost breakdown and capacity witnesses](../../proofs/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001B-P001_two_live_uses/proof.md)

| Use requirement on the trained rule | \(a=0\) | \(a=1\) |
| --- | ---: | ---: |
| Training required, any number of citations | **24** exact | **26–28** |
| At least two live citations, all visible affine questions | **24–31** | **26–35** |
| Both separate rules trained, only those two stored | At least **28** overall | Same shared bound |

For a lower bound charging the citations explicitly, remove the countercase \(F_a=\{v=0,x_2=a,x_0=1\}\) from both source relations. Every surviving row satisfying the guard already has \(x_0=0\), so a citation can be deleted from the main proof on these restricted relations. An ordinary proof there still costs at least 17 for \(a=0\) and 18 for \(a=1\). Consequently total cost with \(c\) citations is at least \(5+17+c\) or \(5+18+c\). A second bound checking all 511 possible first questions makes the lower bound 24 or 26 even when the rule is cited only once. It allows arbitrary visible XORs and arbitrary timing of checks. For two citations the resulting floors are 24 and 26. The upper endpoints 31 and 35 are explicit two-use programs. A one-use witness costs 24 or 28. [Finite lower bounds, exceptional questions and one-use proofs](../../proofs/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001A/FIVE-PRODUCT-TWO-ASSUMPTIONS-20261115-001A-P001_guard_comparison/proof.md)

If both specified rules are trained, their countercases have opposite \(x_2\), so neither can help prove the other on a nonempty branch. Training both costs at least ten. Replace them in the main proof by the single rule \(v=0\Rightarrow x_0=0\), whose main proof alone costs at least 18 by the preceding result. Thus training both costs at least 28 total. The wider question permitting other learned facts still has a proved range of 21–23.

## A control on seven products

Extend the same path by two products and keep the same two summaries. In either training countercase fix \(x_4\) and \(x_6\). Every remaining product has a fixed factor, so three questions across the tree and eight local checks suffice. For the matching lower bound, keep \(x_1=x_3=u=v=0\), and take \((x_4,x_5,x_6,x_7)=(y,w,t,w\oplus r)\). The total becomes \(yw\oplus tr\). The direct five-bit recurrence for the two opposed totals gives 11 operations with arbitrary XORs and local checks. Thus dropping \(v=0\) costs zero extra in the training at this size as well. This control prices only the training. [Executable training controls](training_checks.py)

## A different second assumption

Any two-equation guard lies in three one-equation affine guards. The comparison above immediately applies if one of them can be trained at the same cost with the same consequence. Replacing the particular condition \(x_2=a\) by \(x_4=a\) changes this test. For each \(a\), the narrow countercase \(v=0,\,x_4=a,\,x_0=1\) closes in **three** evaluator checks, in the order reporting, opposite, reporting. All three possible one-equation premises containing this guard, \(v=0\), \(x_4=a\), and \(v\oplus x_4=a\), cost **more than three** to train for the same conclusion. The executable check tries both source operations and every visible affine question through budget three. This makes the cost of the main proof a fresh question. [Original-coordinate replay](training_checks.py)

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the two specified five-unit rules | **Status:** Successful | Both miss budgets 21 and 22. |
| Local direction — reuse below a conjunction | Settled for these two guards | A stronger implication has the same training price. The two-branch witnesses cost 31 and 35. |
| Broader exploration — saving total work with learned consequences | Known alternatives | The remaining overall values are 21, 22 and 23 for more general stored rules. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Obstruction learned | Same-price replacement lets the known lower bound survive adding an assumption. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Check the rule with premises \(v=0,x_4=a\) | 2/3 — Substantial | 3/3 — Ready | Test all three containing affine premises → stop the price comparison as soon as equality is found or all three cost more | Selected · started |
| 2 | Price two uses on opposite answers to the first question | 1/3 — Incremental | 2/3 — Testable | Compare the two root-answer costs → close the interval for either original rule | Alternative · deferred |

The first comparison stops with exact three-unit training for both \(x_4\) candidates and no same-price one-equation premise. To establish any advantage each candidate still needs a complete proof costing 21 or 22. The second direction could refine the price of replication on the original rules after both improvement budgets have already been excluded.

**Basis:** Accepted predecessor proofs, two new same-task scientific families, independent raw replay on 512 visible words and a separate original-coordinate review. The decisive lower results were reproduced with all 511 possible first questions. The project design-advisor CLI could not authenticate.

**Goals:** G3 and G16 gain exact exclusions under the matched operation costs. No goal wording changed.

**Assumptions:** The work uses the same unit prices and the same two visible summaries as the predecessor, including checking raw guard entailment at every paid citation. The alternatives above use these same prices. No standing assumption changed.

**Corrections:** No accepted claim changed. The previous five-unit training costs stand for both values, and the earlier broader 21–23 interval stays open.

**Basket:** This study takes the previous total-work direction #1. Its #2, involving interacting single-premise implications, remains available. No new research home was opened for the \(x_4\) screen.

## Final report as sent

2026-11-16 04:28:49 UTC

| Scope | Verdict | What the checks show |
| --- | --- | --- |
| Both five-unit deductions | **Status: Successful.** Both targets are ruled out. | Neither can reach 21 or 22. The ordinary tree costs 23. |
| Two live uses of the same deduction | Genuine reuse | For \(a=0\) the cost is between 24 and 31. For \(a=1\) it is between 26 and 35. |
| Broader search for a cheaper proof | Open | A different guard or interacting learned facts could still reach 21 or 22. |
| G3 and G16, understanding what forces proof work | Obstruction learned | Here one can drop a premise at zero training cost and transfer every branch to a previously bounded proof system. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First test and stopping point | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Replace \(x_2=a\) by \(x_4=a\) in the guard | 2/3 — Substantial | 3/3 — Ready | Check whether one affine premise can train at the same price. Both three-unit deductions passed this first test. | Selected · started |
| 2 | Find the exact cost when the two uses lie on opposite answers to the first question | 1/3 — Incremental | 2/3 — Testable | Close the remaining gap for either value. | Alternative · deferred |
