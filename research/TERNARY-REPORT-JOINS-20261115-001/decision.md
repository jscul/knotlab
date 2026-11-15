# A four-report deduction and the cost of hiding intermediate products

## The two three-report checks

The first two constraints require \(F_0+F_1+F_2=0\) and \(F_0+F_3+F_4=0\), with \(F_i=z_i(x_i y_i+ab)\) and all sums modulo two. Forgetting the eliminated triple gives exactly \(F_1+F_2+F_3+F_4=0\). The same value of the eliminated report works for both checks. At every fixed \(a,b\) that value is attainable by an actual triple, so every allowed boundary assignment has a common extension. The other two checks eliminate \(F_5\) and give the opposite required parity on the same four reports. Each side is proved from just its own clauses. [Exact projection and checked derivation](../../proofs/TERNARY-REPORT-JOINS-20261115-001A/TERNARY-REPORT-JOINS-20261115-001A-P001_four_report_join/proof.md)

In the unnamed degree-two calculus, for every four-bit selector setting \(u\) derive the conditional line
\[
 (z_1,z_2,z_3,z_4)=u\quad\Longrightarrow\quad\sum_{i=1}^4 u_i(x_i y_i+ab)=c,
\]
where \(c=0\) on the first side and \(c=1\) on the second. For each outside setting, adding the two checked child equations separately under \(z_0=0,1\) cancels the shared contribution. A Boolean cut removes \(z_0\). Mask 1010 gives \(x_1y_1+x_3y_3=0\) at zero-based row 135928, and \(x_1y_1+x_3y_3=1\) at row 136104. The left row traces back to 192 failed assignments of the first block and 192 of the second, with none from the other two blocks. Changing a coefficient in row 135920 is rejected. The finite check covers 16,384 raw boundary assignments per side, of which 10,144 are accepted on the left and 6,240 on the right. [Readable proof steps](../../proofs/TERNARY-REPORT-JOINS-20261115-001A/TERNARY-REPORT-JOINS-20261115-001A-P001_four_report_join/trace.json) · [Checks](../../proofs/TERNARY-REPORT-JOINS-20261115-001A/TERNARY-REPORT-JOINS-20261115-001A-P001_four_report_join/checks.json)

Each failed eleven-bit assignment is encoded by nine strict ternary clauses with eight private chain bits. The full certificate derives the 32 child lines from these sources in 135,808 primitive nodes, uses 176 nodes per join and 160 to close. The empty line at row 136319 has all 30,960 strict clauses among its ancestors. There are no hidden report or product declarations. The zero selector case is tautological on the even side, and the other fifteen lines are individually necessary within this full-selector-guard format. On the odd side all sixteen are individually necessary within the same format. A different proof language or collection of guards can have a different minimum. [Complete kernel certificate](../../proofs/TERNARY-REPORT-JOINS-20261115-001A/TERNARY-REPORT-JOINS-20261115-001A-P001_four_report_join/four-check-proof.jsonl.gz)

## Grow the non-affine constraints

Use \(m\) AND checks on \(m+1\) common data bits \(R_i\) and report the XOR of their products. In a star every product uses the same center bit. In a path consecutive products share one bit. The earlier raw reports can realize every vector of these independent data bits simultaneously. A star needs exactly two affine pieces to describe its complete product graph. A path needs exactly \(2^{\lfloor(m+1)/2\rfloor}\). For any simple graph the complete product vector costs \(2^{\tau(G)}\), where \(\tau(G)\) is its minimum vertex-cover size. For its lone parity output the exponent is half the polar rank of the Boolean quadratic. A three-vertex cycle separates the two measures, requiring four pieces for all products and two for their XOR. [Uniform theorem and small strict control](../../proofs/TERNARY-REPORT-JOINS-20261115-001B/TERNARY-REPORT-JOINS-20261115-001B-P001_interacting_products/proof.md) · [Checked counts](../../proofs/TERNARY-REPORT-JOINS-20261115-001B/TERNARY-REPORT-JOINS-20261115-001B-P001_interacting_products/checks.json)

There is an actual UNSAT decision test on the same connected products. Evaluate the same checksum twice and require the outputs to disagree. Its matched SAT control changes only that sign. At each branch let a solver ask any affine question on its visible variables. Let it use every affine consequence of each entire evaluator on that branch, repeating Gaussian elimination to a fixed point. If it sees only the source bits and the two final checksum outputs, the exact minima on a rank-\(2r\) quadratic are \(2^r\) terminal cases and depth \(r\). Since fewer independent queries leave both evaluator truth sets spanning the same case, even adaptive queries that mix inputs with either output cannot close earlier. This lower bound is for refuting this instance in the specified procedure. Refuting the instance is a different task from representing its satisfying evaluations. [Two-evaluator proof](../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/proof.md)

On 31 edges, that comparison gives two public cases on the star and 65,536 on the path. Allow just six intermediate prefix bits from the path, and four blocks of lengths 8,8,8,7 suffice for at most 64 leaves. When all products are visible, a parity question identifies which half has an odd discrepancy, and splitting alternating inputs inside its final block closes the case. The connected path then has between 22 and 32 leaves. A matching of \(k\) private product pairs has exactly \(2k\) product-visible leaves and depth \(1+\lceil\log_2 k\rceil\) even with arbitrary affine queries and both full evaluator hulls. [Finite affine-hull checks and block counts](../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/checks.json)

Finally regroup the proof. From the actual strict AND clauses derive \(p_i+R_uR_v=0\) and \(q_i+R_uR_v=0\). Adding them gives equality of the individual outputs. Reuse these equalities through the XOR prefixes. Both 31-edge instances have 492 strict clauses and a 7,143-node unnamed degree-two proof. A control removes identical product gates: the second evaluator computes \(lm+mr=m(l+r)\) using a genuine XOR followed by one AND. At sixteen edges the source has 220 clauses and the checker accepts 3,184 nodes. The size is linear in both constructions. [Three-edge complete proof](../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/opposed_path3.json.gz) · [Four-edge factored proof](../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/factored_path4.json.gz) · [Derived operands](../../proofs/TERNARY-REPORT-JOINS-20261115-001C/TERNARY-REPORT-JOINS-20261115-001C-P001_opposed_checksums/trace.json)

## Which inputs the decision algorithm can handle

For a single product checksum on any supplied graph, arbitrary affine constraints on its input reports and that checksum allow a polynomial-time witness algorithm. For multiple independent product combinations of coefficient rank \(k\), exact counting takes \(2^k\operatorname{poly}(N)\). Each of the \(2^k\) terms is a signed sum for a single quadratic and can be evaluated by elimination. Rank here belongs to the product coefficients in the supplied affine restrictions after substituting the checksum; the test makes no claim that it is the best possible parameter. [Decision and counting algorithms](../../proofs/TERNARY-REPORT-JOINS-20261115-001B/TERNARY-REPORT-JOINS-20261115-001B-P001_interacting_products/solver.py)

The decision problem broadens if the input can impose affine equations on individual product wires and the data bits, including ties between wires. A star still takes at most two Gaussian branches. On a path the problem is NP-complete. Per 3-SAT clause, two selected ANDs multiply its three literal-falsity bits and an affine equation requires the resulting product to be zero. Other genuine products connect each gadget to the rest of the fixed path and carry no imposed condition. The reduction has five sparse affine equations per clause and is checked in both projection directions. A polynomial-time method handling *all* of these extended path inputs would therefore give a polynomial-time algorithm for general 3-SAT. The single-checksum family and the explicitly doubled witnesses have their own proved polynomial shortcuts. [Reduction and matched instances](../../proofs/TERNARY-REPORT-JOINS-20261115-001B/TERNARY-REPORT-JOINS-20261115-001B-P001_interacting_products/proof.md) · [Projection checks](../../proofs/TERNARY-REPORT-JOINS-20261115-001B/TERNARY-REPORT-JOINS-20261115-001B-P001_interacting_products/checks.json)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — join two ternary checks | **Status:** Successful | Sixteen exact conditional lines come from the two source blocks |
| Local direction — grow interacting AND checks | Continue at intermediate summaries | Public and product-visible affine case counts have different growth |
| Broader exploration — decision on a path | Known boundary | One checksum is tractable and constraints on individual product wires can express 3-SAT |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | The facts a proof may expose change a measured bound on one contradiction |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Partially visible intermediate checksums | 2/3 | 3/3 | Expose one internal prefix per evaluator → find a matching affine-case lower bound or a cheaper choice of prefix | Selected · started |
| 2 | Compress larger ternary parity summaries | 2/3 | 2/3 | Grow the surviving report set → exhibit a checked summary smaller than the full selector table or isolate its obstruction | Alternative · deferred |

For #1 the source exposes exactly the two prefixes belonging to each selected internal boundary. The 31-edge control with one midpoint per evaluator gives a bound of 512 cases, compared with 65,536 from only the ends. This makes an intermediate case-information question explicit; the next discriminator is the lower bound with one such additional pair, even if its placement or its two linear combinations may be chosen. For #2 the concrete four-report result establishes that eliminating shared choices is legal under selector guards. The payoff would be a bound that still works when more reports survive. Fewer guards or a different reusable relation could change the cost.

**Basis:** Three local constructive proofs and same-task independent checks. The strict proofs replay in the existing unnamed kernel. Additional checks use exhaustive assignment projection, actual SAT queries, exact affine-subspace enumeration and a separate matching adversary. Prior results on affine restrictions and elimination are comparisons. The external design advisor returned its weekly usage limit.

**Corrections:** None. A large affine cover for a relation and a lower bound for an explicitly stated refutation procedure are different claims. Both allow stronger decision algorithms elsewhere.

**Goals:** G3 and G16 gain a checked four-report interface and a way to vary how much information about nonlinear checks survives in a proof or a decision procedure.

**Assumptions:** The displayed coordinates, strict encodings, permitted affine side conditions, local hull oracle, tree-shaped case splits and access to intermediate product bits are explicit parameters. No standing assumption changed.

**Basket:** The two chosen directions from SHARED-REPORT-CANCELLATION-20261115-001 were taken for this study. The broader all-solvers question remains open.

## Final report as sent

2026-11-15 21:36:05 UTC

| Scope | Verdict | Checked result |
| --- | --- | --- |
| This attempt — join two three-report checks | **Status:** Successful | Sixteen conditional lines exactly describe the four surviving reports. |
| Local direction — grow interacting AND checks | Continue at intermediate summaries | On 31 products, the public affine solver needs two terminal cases for a star and 65,536 for a path. |
| Broader exploration — satisfiability on a path | Known boundary | One constrained checksum admits polynomial decision. Arbitrary affine equations on individual products and inputs can encode 3-SAT. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | The facts a proof can use change the cost of refuting the same contradiction. |

On the 31-edge path, exposing six intermediate prefix bits cuts the upper bound to 64 cases. Combining the actual quadratic equations gives a checked 7,143-node proof on the 492 strict clauses. The shortcut also works when the second evaluator uses a different factorization with no identical product gates.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Partially visible intermediate checksums | 2/3 | 3/3 | Expose one prefix from each side → prove a matching case bound or find cheaper information to expose | Selected · started |
| 2 | Compress larger ternary parity summaries | 2/3 | 2/3 | Increase the surviving report count → check a smaller summary or identify the first failed inference | Alternative · deferred |

For #1, one midpoint per side already lowers the 31-edge upper bound to 512 cases. How much a single pair of well-chosen observations can save remains open.
