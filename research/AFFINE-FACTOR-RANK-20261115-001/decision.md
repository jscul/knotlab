# Four cases at two independent factors

Fix two independent Boolean quantities \(a,b\) that are XORs of original choices, possibly with a constant. Their four joint values determine every XOR or complement formed from them. If each multiplication has a factor determined this way, it either returns zero or copies its other factor. That other factor may use any previously named results, however many times. Within one of the four cases an induction keeps all named results affine, meaning an XOR of original bits with an optional constant. A live refutation with four reusable names passed in four cases and produced 618 verified unnamed nodes. A signed projection that identified its two controlling bits reduced the same conversion to two cases and 238 nodes. [Rank-two example and general proof](../../proofs/AFFINE-FACTOR-RANK-20261115-001A/AFFINE-FACTOR-RANK-20261115-001A-P001_ranked_elimination/proof.md)

The same argument gives \(2^r\) cases for \(r\) independent affine questions. Proof length still enters the work: for a named refutation of \(S\) nodes over \(n\) original variables the unnamed proof uses \(O(2^r(n+r+1)(S+1))\) nodes. For every depth this works under a broader, exact test. On each case, process the declarations in order, expressing the two factors in the remaining original bits. The product is affine precisely when either factor or their XOR has a fixed value. In the XOR case the factors are equal or opposite. Equal Boolean bits multiply to that bit, and opposite bits multiply to zero. A formal derivation supplies the Boolean square identity needed by the proof calculus. In a separate 76-stage route proof the two distinct controls both came from one original choice; the four raw cases became two on the source clauses. [Exact test and formal conversion](../../proofs/AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/proof.md) · [Checked route replay](../../proofs/AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/checks.json)

Choosing one original factor per declaration amounts to the literature's Rank Vertex Cover problem, and a bounded search finds a minimum such rank in \(O(2^r\operatorname{poly}(N))\) work on the explicit proof. Allowing a question about the XOR of two factors can save arbitrarily many original-factor observations. For example, the products \(z_i(z_i+u)\) on independent input bits require one distinct independent original factor per product under the first rule. Asking only for \(u\) handles every product. The broader minimum up to a given rank \(r\) can be found in \(O(6^r\operatorname{poly}(N))\). [Factor selection](../../proofs/AFFINE-FACTOR-RANK-20261115-001B/AFFINE-FACTOR-RANK-20261115-001B-P001_finding_factors/proof.md) · [Minimum broader observation](../../proofs/AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/proof.md) · [Rank Vertex Cover](https://doi.org/10.1137/17M1154370)

With \(r\) products on disjoint input pairs, even a partition whose affine questions can differ between cases needs \(2^r\) parts to make all their values affine. Mere ancestry is weaker. Take \(p=ax,\ q=by,\ t=pq\) on four free bits. When \(a=b=1\), \(t=xy\) still needs a decision. One fixed list of affine questions needs eight cases here. An adaptive list needs exactly five: fix \(a,b\), and ask about \(x\) only when \(a=b=1\). The two disjoint products limit every valid part to at most four inputs. The part containing the only input with \(t=1\) has at most two, so any four parts cover at most fourteen of sixteen. If the *only* inputs anywhere in a chain are the two seed bits, fixing one already leaves functions of at most one Boolean bit, all affine. [Proof and exhaustive check](../../proofs/AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/proof.md)

On the previously admitted random source family, the simulation preserves an exponential lower bound on the size of named refutations whose required fixed observation rank is \(o(n)\), with high probability under the admitted source model. This follows by comparing the exponential source lower bound with the \(2^{o(n)}\) conversion overhead. The evidence concerns the length of the stated kind of contradiction proof. Whether all decision algorithms take superpolynomial work on some 3-SAT inputs remains open. [Signed transport and consequence](../../proofs/AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/proof.md) · [Pang v2, Theorem 7.2(a)](https://arxiv.org/html/2610.00837v2#S7)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — test four cases and generalize by factor rank | **Status:** Successful | Explicit proof conversion and an obstruction to ancestry alone |
| Local direction — affordable questions for a supplied proof | Continue | Five adaptive cases can replace eight fixed cases |
| Broader exploration — proof systems and general SAT methods | Known alternatives | Unrestricted product names already simulate ordinary extended resolution |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | A rank limit gives a proof-length theorem and a computable criterion for individual proofs |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Choose the next affine question from earlier answers | 2/3 — can reduce the cost of removing names | 3/3 — exact four-input discriminator | Compare the optimal adaptive partition and fixed span for two products followed by their product → stop at equality or a proved separation | Selected · started |
| 2 | Transfer a certificate bound to unrestricted SAT decisions (B181) | 3/3 — reaches arbitrary solvers | 1/3 — missing a simulation theorem | Identify the certificate required by an uncovered decision method → reassess if it admits a polynomial bound | Alternative · deferred |

For #1 the bounded comparison ended at an exact five versus eight, with all 307 affine subsets checked and a counting proof. It improves the measure used to remove names in G3 and distinguishes two kinds of reports in G16. A general characterization of the smallest adaptive proof conversion remains open. For #2 the wider payoff would address G3 directly, but the existing certificate transfer does not cover an arbitrary decision algorithm.

**Basis:** Three proved local claims, checked proof replays, independent finite truth-table comparisons and a same-task review. The external design advisor was unavailable at its weekly quota. The conditional source bound uses the previously admitted preprint specialization.

**Goals:** G3 Hardness at three places and G16 Learning the rules behind what a system allows gain a fixed-rank transfer and a sharp distinction between one list of questions and questions chosen from earlier answers.

**Assumptions:** The named proof is given explicitly, its fresh definitions are charged and acyclic, and all declared names are tested on the entire original Boolean cube. The restricted and adaptive alternatives are explicit theorem domains. No standing assumption changed.

**Corrections:** The prior empty-axiom, canceled-name and displayed-multiplier findings were checked as controls. This study found no further correction to the earlier claims.

**Basket:** The predecessor's completed one-factor probe is linked to this investigation. B181 remains the broader open direction. TWO-CHOICE-IMPLICATIONS-20261115-001#2 retains the independent question about how shared-choice reports are expressed.

## Final report as sent

2026-11-15 19:02:45 UTC

| Research question | Result |
| --- | --- |
| How many cases do two independent controlling factors need? | Four suffice at any depth. Two disjoint products can require all four. |
| What governs the general case? | If fixing \(r\) independent XOR questions makes every named product affine, \(2^r\) cases suffice. We can check this on a supplied proof and find a minimum such \(r\). |
| Can the choice of question depend on earlier answers? | Yes. For \(p=ax,\ q=by,\ t=pq\), the optimum falls from eight fixed cases to five adaptive cases. |
| What does this establish about 3-SAT? | It extends a lower bound for a particular kind of contradiction proof. The worst-case work of arbitrary SAT solvers remains open. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Choose later questions from earlier answers | 2/3 | 3/3 | Compare fixed and adaptive questions on the three-product example → stop at a proved optimum | Selected · started |
| 2 | Extend the proof bound to arbitrary SAT decisions | 3/3 | 1/3 | Identify a decision method the proof rules miss → reassess if it has a short certificate | Alternative · deferred |

The first comparison is complete. Finding the smallest adaptive set of cases for a general supplied proof remains open.
