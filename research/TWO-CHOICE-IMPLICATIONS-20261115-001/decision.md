# What a block can say about two shared choices

In the original three-stage example at start, cut and end values \(1,0,0\), the left block forces \(h=1,k=0\). The right block permits exactly \(00,01,11\). The entire right report is the single implication \(h\to k\). Comparing it with the left pins rejects precisely the incompatible choice. Checking the two bits separately would give the wrong answer. [Example and witness solver](../../proofs/TWO-CHOICE-IMPLICATIONS-20261115-001A/TWO-CHOICE-IMPLICATIONS-20261115-001A-P001_implication_reports/proof.md)

For positive implication blocks, also including pads whose conditional halves can all be released by compatible values, first report infeasibility or forced bits. If both bits are free, inspect just \(10\) and \(01\). Only \(10\) missing means report \(h\to k\); only \(01\) missing means report \(k\to h\). If both are missing, report equality, which takes both implications. If neither is missing, the two choices are independent. Directed reachability computes the exact report and an assignment in linear work for two observed choices. Of the sixteen Boolean relations, ten are rectangular (including empty), two are the individual implications, and one is equality. An internally repeated middle first realizes full unforced equality in three stages. Actual raw checks covered all 440 endpoint-compatible ordered pairs of positive reports; 16 gave a false positive when compared one bit at a time. [Proof and realizations](../../proofs/TWO-CHOICE-IMPLICATIONS-20261115-001A/TWO-CHOICE-IMPLICATIONS-20261115-001A-P001_implication_reports/proof.md) · [Counts](../../proofs/TWO-CHOICE-IMPLICATIONS-20261115-001A/TWO-CHOICE-IMPLICATIONS-20261115-001A-P001_implication_reports/checks.json)

Internally mixed guards give all three remaining reports. A padding bit used with opposite active signs can choose which one of two implications to enforce. This gives OR or NAND with one such pad and XOR with two. These counts are minimal over two-use layouts. With a descending pair of ends all sixteen binary relations occur on one stage. Across all four choices of the two ends, both uniform joint states must be allowed and lowering the initial bit or raising the final bit must preserve feasibility. These conditions completely describe the 324 possible full tables; one 152-stage catalogue gives every table by switches alone. The catalogue length is an upper bound. [Construction and sharp pad counts](../../proofs/TWO-CHOICE-IMPLICATIONS-20261115-001B/TWO-CHOICE-IMPLICATIONS-20261115-001B-P001_mixed_padding/proof.md)

Recognizing the shape of a report from unrestricted long blocks can already encode strict 3-SAT. With just earlier switches changing on fixed wiring, an exact single-implication report can be equivalent to the satisfiability of the encoded input. A second construction makes the choice between the full relation and OR encode the same decision. Four calls to SAT recover the report for specified ends. Knowing its four entries and finding them are distinct tasks. [Guard-only reductions](../../proofs/TWO-CHOICE-IMPLICATIONS-20261115-001C/TWO-CHOICE-IMPLICATIONS-20261115-001C-P001_report_recognition/proof.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — report two shared choices | **Status:** Successful | Exact classifier, linear positive solver, mixed-pad counterexamples |
| Local direction — summarize several shared choices | Continue | Positive relations compose by reachability |
| Broader exploration — SAT work under changing representations | Known alternatives | Exact reports can be tiny even when recognition encodes SAT |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | Identifies the correlations that a two-choice summary must retain |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Test whether three choices are determined by all their pairs | 2/3 — limits of pair reports | 3/3 — one forbidden assignment | Forbid only \(111\) at descending ends → find a guarded witness or prove it impossible | Selected · started |
| 2 | Compare one work measure on equivalent flat and factored formulas | 2/3 — representation dependence | 3/3 — an explicit paired input | Evaluate a proposed measure on both encodings → reassess at a separation | Alternative · deferred |

For #1 the first discriminator follows the mixed-clause construction. The condition \(\neg a\lor b\lor\neg h\lor\neg k\lor\neg s\) excludes precisely \(111\) at \((a,b)=(1,0)\). Split it with two fresh Boolean variables into \((\neg a\lor\neg h\lor u),(\neg u\lor\neg k\lor v),(\neg v\lor\neg s\lor b)\). All three clauses have both signs and hence each has the two-use pad construction in B. Observe one occurrence in each of the three different signal blocks. Every two-choice projection is full but one triple is impossible. This answers the smallest follow-up. Finding the minimum number of mixed pads for that stronger observation remains open. For #2 the forms and their equivalence are concrete, while a work measure that would change a solver decision remains to be selected.

**Basis:** Three locally proved mathematical results, original guarded-clause checks, and a separate constructive witness implementation. The support count for abstract positive preorders was previously known; the route realizations, exact mixed-pad thresholds and recognition reductions supply the local changes. Finite checks are V1. The outside design advisor was unavailable under its weekly quota.

**Corrections:** None to the shared-choice theorems. **Goals:** G3 and G16 gain the exact two-choice classification and its cost boundary. **Assumptions:** The reports describe existence of satisfying extensions for fixed local endpoints on a supplied finite formula. Private versus mixed pads are declared cases. No standing assumption changed.

**Basket:** B181 concerns general proof simulations and stays open. GUARD-CHOICE-SEPARATION-20261115-001#2 points to the existing flat/factored comparison in candidate #2. The completed one-bit study's #1 is linked to this substantive continuation.

## Final report as sent

2026-11-15 18:17:59 UTC

One implication completely describes the right side of the three-stage example. Positive implication blocks give a linear classification. Mixed internal pads can force OR, NAND or XOR instead, and recognizing the report on arbitrary fixed guarded wiring can encode 3-SAT.
