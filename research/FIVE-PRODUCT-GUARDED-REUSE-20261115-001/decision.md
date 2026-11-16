# Five products need eight cases, and two of the final proofs can be reused

The five adjacent products are \(p_i=x_{i-1}x_i\), numbered from one, and their XOR is \(Q\). One evaluator requires \(s=Q\) and sets two summary bits to fixed XORs of its own products. The other requires \(s=1+Q\) and permits every value of the two summary bits. All six inputs, \(s\), and the two summary bits are visible. A tree may ask any adaptive XOR of these bits. At every branch each evaluator may supply every affine consequence of its own remaining possibilities. The process repeats until the joint affine conditions stop changing or give a contradiction.

## Every one of the 35 pairs costs eight cases

The exact minimum is **eight terminal cases and three worst-case questions** for all 35 independent pairs. Fix \(x_1,x_3,x_5\). Every product has a fixed factor, so both evaluators give affine equations for the total and the opposite equations close every case. This supplies the same eight-leaf tree for all pairs. [Proof and full census](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A-P001_pair_census/proof.md) · [Checked tree](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A-P001_pair_census/certificate.json)

To count the pairs, regard each product XOR as a five-bit mask. Adding the total to a report can be undone using \(s\) on the reporting evaluator, and an invertible change of the two reported bits preserves every available affine question. There are \(15\cdot14\) ordered independent pairs after removing multiples of \(Q\). Each two-dimensional space has six ordered bases. This gives 35, representing 840 independent ordered choices of the two original masks.

The shared lower bound gives the reporting evaluator **all five individual products**. Any two allowed reports can be computed with XORs of these five. For an honest reporting-evaluator input \(x\), a visible question reduces to an XOR of six input bits and five products. There are 2,047 nonconstant possibilities up to exchanging the answers. At each branch, the plain evaluator can ignore every private report. Whether a set of original inputs can close in a single case is decided by the affine span of its pairs \((x,Q(x))\). The list of largest such sets contains 5,040 sets of twelve inputs each. The size bound alone would give six cases. A tree also has to separate the sets by legal binary questions. The exact recursion tries each question, assigns a positive integer leaf budget to each answer, and succeeds only if both answers fit. It rules out seven leaves even with all five products visible. The separate census on each pair agrees. [Calculation and the projection argument](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A-P001_pair_census/proof.md) · [Results](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A/FIVE-PRODUCT-GUARDED-REUSE-20261115-001A-P001_pair_census/checks.json)

## What a branch can reuse under its actual assumptions

Keep the same inputs, and fix one independent pair for both proofs, \(u=p_1,\ v=p_2\oplus p_3\). Write \(c=x_4\). After asking for \(c\), define \(d=x_1\oplus x_3\) and \(z=s\oplus c(x_3\oplus x_5)\). Each is an available XOR within this branch. On the reporting evaluator,
\[
z=u\oplus x_2d,\qquad u=x_0x_1.
\]
The two reported bits remain available throughout. The proof only needs \(u\).

For each fixed \(c\), ask \(h=u\oplus d\), then use the following tree. Each row checks that the reporting evaluator implies both guard equations before citing the indicated contradiction. The guard retains the value of \(c\).

| Answer to \(h\) | Next question | Answer | Assumptions for the terminal proof |
|---|---|---:|---|
| 0 | \(z\oplus x_3\) | 0 | \(x_3=0,\ z=0\) |
| 0 | \(z\oplus x_3\) | 1 | \(x_1=1,\ z=x_0\) |
| 1 | \(d\) | 0 | \(x_1=1,\ z=x_0\) |
| 1 | \(d\) | 1 | \(d=1,\ z=x_2\) |

In the two middle rows exactly the same equations hold. Under those equations the reporting evaluator forces \(x_2(1\oplus x_3)=0\), while the plain evaluator forces that product to be one. The latter forces \(x_2=1,x_3=0\), which closes the rich side. The same two-step argument proves the other two contradictions using \(x_1(x_0\oplus x_2)\) and \(x_0x_1\), respectively. Each guard has a nonempty set of traces on each evaluator before these deductions. Using the middle proof on the first row fails the guard check on the all-zero input. [Guarded proof](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B-P001_guarded_deductions/proof.md) · [Direct replay on all 512 visible assignments](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B-P001_guarded_deductions/terminal_library.py)

There are **eight terminal calls and six distinct terminal contradiction proofs**. Their guards cover all 64 original reporting-evaluator inputs. A guard that closes with the original inference rule contains at most twelve such inputs, even allowing arbitrary affine conditions on the visible reports. Thus five guards cannot cover all 64. Six is a minimum for libraries of terminal proofs used this way. The lower bound assumes every original reporting-evaluator input is routed to a guard that contains it. Proofs allowed to discard some inputs using earlier lemmas derived jointly from the two sides need a different bound.

| Costs on the fixed visible pair | Shared terminal proofs | Same proof expanded | Same questions, direct checks | Direct alternating-input tree |
| --- | ---: | ---: | ---: | ---: |
| Branch questions across the certificate | 7 | 7 | 7 | 7 |
| Terminal cases | 8 | 8 | 8 | 8 |
| Rich-side entailments routing a case to its guard | 8 | 8 | 0 | 0 |
| Local evaluator checks establishing the terminal contradictions | 12 | 16 | 22 | 16 |
| Total local evaluator checks under this unit | 20 | 24 | 22 | 16 |

Each of the eight guarded applications checks the branch entails the guard using the rich source. Each terminal proof uses two local evaluator steps. The guarded proof has 21 nodes, including seven split nodes, eight checks of the assumptions at their applications, and six terminal proofs. It has 22 references including the split children. Its literal expansion has 23 nodes and the same number of references. On this certificate two out of eight terminal derivations are duplicates, saving four local evaluator checks relative to its expansion. The simpler direct proof uses sixteen checks. These counts establish the saving on the displayed proof and the exact number of distinct terminal guards. They leave the smallest total cost among general proofs with learned intermediate deductions open. [Certificate, cost conventions and controls](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B-P001_guarded_deductions/proof.md)

The checker also reuses an intermediate affine deduction while both consumer branches are still live. A three-case subproof from the two evaluators refutes \(v=0,\ x_0=1\), establishing the learned implication \(v=0\Rightarrow x_0=0\). Under \(v=0\), the \(x_2=0\) and \(x_2=1\) branches both cite that same subproof. Their already-saturated sets of visible rows shrink from 128 to 32 and from 64 to 16. Discarding the premise \(v=0\) is rejected by the checker. This learned implication uses the opposed evaluators together. The twelve-input limit applies to a raw terminal guard and supplies no lower bound for general use of such intermediate deductions. [Live deductions and controls](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B-P001_guarded_deductions/proof.md)

## One size further

For seven products, fixing \(x_4,x_6\) leaves the same four-question-answer table after an affine adjustment of \(s\). The checked construction has 16 terminal calls and twelve distinct guards on the same initial pair of summaries. A single terminal guard can cover at most 24 of the 256 original reporting-evaluator inputs, so at least eleven are required in the same format. Whether eleven suffice is open here. [Checked seven-product construction](../../proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B-P001_guarded_deductions/seven_guard_stress.py)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — 35 independent pairs on five products | **Status:** Successful | All need eight cases, even with all five products exposed. |
| Local direction — reuse a terminal proof under its assumptions | Settled at five products | Eight calls use exactly six distinct terminal proofs. |
| Broader exploration — total proof work with learned deductions | Open | Sharing saves four local checks versus expansion; a direct proof uses sixteen. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | Cases, distinct contradictions and total local checks can be measured separately. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Minimize all local proof work on the fixed five-product pair | 2/3 — Substantial | 3/3 — Ready | Compare the best tree and guarded proof with charged guard checks → certify a strict saving or a matching lower bound in the fixed rule set | Selected · started |
| 2 | Eleven or twelve distinct guards on seven products | 1/3 — Incremental | 3/3 — Ready | Seek an eleven-guard cover with a valid branch proof → exhibit that proof or exclude the cover | Alternative · deferred |

For #1 the direct, shared, and expanded certificates already give a reproducible comparison on the same nine visible bits. The missing result is the minimum charged cost in each specified proof system. For #2, the seven-product replay gives twelve and the covering bound gives eleven. Deciding that single-guard difference would explain growth in this restricted format.

**Basis:** Two finite classifications with same-task mathematical and computational checks. The per-pair search and stronger all-products recurrence are independently implemented. The guarded proof was replayed via the explicit graph of deductions and an independent implementation on the raw nine-bit coordinates. The advisor command could not authenticate during design. The cited literature supplies background.

**Goals:** G3 and G16 gain an obstruction for all five-product summaries on one side and an exact comparison between eight cases and six terminal proofs. No goal wording changed.

**Assumptions:** The visible bits and the affine rule are given. The accounting distinguishes direct checks, cached terminal proofs, guard entailments, references and expanded proof work. The six-proof lower bound is conditional on covering all original reporting-evaluator inputs. These comparisons add no standing assumption.

**Corrections:** No previous accepted result changed. The bound of twelve original inputs per terminal guard proves six, while ruling out a seven-leaf binary tree requires its own argument.

**Basket:** The previous study's first direction was taken on the five-product path. Its alternative of replacing a finite induction base by hand remains deferred.

## Final report as sent

2026-11-16 00:16:11 UTC

On the fixed pair \(u=p_1,\ v=p_2\oplus p_3\), sharing saves four local evaluator checks compared with expanding the same proof. A simpler eight-case proof takes fewer checks than either version.

| Scope | Result |
|---|---|
| Five products, all 35 pairs | Eight cases are necessary and sufficient |
| Reusing terminal contradictions | Six distinct proofs serve eight calls |
| Total local evaluator checks | 20 shared, 24 expanded, 16 in the direct proof |
| What forces work | The case count and the cost of proving each case can vary independently |

**Next step.** Compare the cheapest fully charged proofs on these same visible bits.

| Direction | Payoff | Concreteness | First test |
|---|---|---|---|
| Minimize the whole proof | 2/3 | 3/3 | Include guard checks and references in the comparison |
| Test seven products | 1/3 | 3/3 | Close the checked gap of eleven to twelve distinct terminal proofs |
