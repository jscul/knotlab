# What one failed proof line tells us about the whole computation

Let \(Q_i=x_i y_i+ab\) and \(F_i=z_iQ_i\), with addition modulo two. Start with two checks requiring equal neighboring reports and a third requiring the first and last reports to differ. All three are derived from original strict 3-CNF clauses. Each failed assignment of eight original bits is forbidden using six ternary clauses and five private splitting bits. There are 1,968 strict clauses in this example, 11 original bits and 1,640 private bits. It is minimally unsatisfiable down to the individual clause. [Source proof](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001A/SHARED-REPORT-CANCELLATION-20261115-001A-P001_strict_checks/proof.md) · [Portable complete named certificate](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001A/SHARED-REPORT-CANCELLATION-20261115-001A-P001_strict_checks/triangle.json.gz)

The checker derived the three singleton parity equations at zero-based rows 4318, 8508 and 14155. Rows 14156 and 14157 added them and produced \(1=0\); row 14158 deleted that false alternative to conclude contradiction. This uses four charged proof names and 14,159 nodes. The earliest failure on removing the names directly is row 16, a multiplication that would print \(z_0(x_0y_0+ab)\) of degree three. No reordering makes a proper nonempty sum one quadratic on the original bits. Even one disjunction of any number of quadratic equations, with any number of fresh freely projected witnesses, cannot represent its required truth set. [Source operands and row numbers](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001A/SHARED-REPORT-CANCELLATION-20261115-001A-P001_strict_checks/trace.json) · [Exact one-line obstruction](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001C/SHARED-REPORT-CANCELLATION-20261115-001C-P001_order_and_obstruction/proof.md)

The successful rewrite records what is true at the four joint settings of the two outside selector bits. When the proof joins two adjacent parts it adds their equations twice, once at each middle bit value, and removes that bit. Each join costs 36 primitive nodes. On these same strict clauses the complete guarded proof takes 13,243 nodes and zero product names. There is also an ordinary resolution proof using 1,968 input nodes and 2,163 resolution steps, 4,131 nodes in all. It translates to 9,264 nodes of the same primitive unnamed calculus. Minimal unsatisfiability requires every clause to occur in any sound explicit refutation of a cycle. Together with the uniform constructions this gives tight linear order in the number of checks for this explicit proof-size measure. [Guarded row-by-row joins](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001C/SHARED-REPORT-CANCELLATION-20261115-001C-P001_order_and_obstruction/comparison.json) · [Ordinary signed certificate](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001B/SHARED-REPORT-CANCELLATION-20261115-001B-P001_regroup_paths/triangle.res) · [Measured costs](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001B/SHARED-REPORT-CANCELLATION-20261115-001B-P001_regroup_paths/checks.json)

Changing the grouping can change actual work. On the same five-check input with charges \((1,0,0,0,0)\), a left-associated, balanced, and minimum-cost connected grouping used 7,487, 7,075 and 6,663 ordinary proof nodes with the last check held out for the close. The minimum is within the specified constructor using its fixed middle-bit order. On six checks, taking three disjoint even checks first would give 454,272 full forbidden rows for their single XOR. Storing the three separate pair relations uses 216 rows or twelve conditional lines. On the same six-check CNF, the consecutive and interleaved orders both took 7,311 ordinary or 24,277 guarded proof nodes. The proofs use source axioms in arrival order. A growing single XOR table measures the price of that representation. [Grouping theorem](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001B/SHARED-REPORT-CANCELLATION-20261115-001B-P001_regroup_paths/proof.md) · [Chronology and original-CNF hashes](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001C/SHARED-REPORT-CANCELLATION-20261115-001C-P001_order_and_obstruction/comparison.json)

Making the network of pair checks denser preserves a shortcut. Propagate assigned report bits until a mismatch supplies one inconsistent cycle, and replay the cycle against the original input clauses. If assignments remain consistent, all report values can be realized simultaneously with \(a=b=0, x_i=z_i=1,y_i=F_i\). All 729 possible absent/even/odd pair graphs on four labelled reports were compared with exhaustive assignments. On the exact promised single-cycle encoding even the input header counts determine the parity of the number of one-charges; connected inputs with two cycles already admit identical-header SAT/UNSAT examples. More generally, any supplied affine system on these independent reports can be decided by Gaussian elimination. This leaves the worst-case decision cost for arbitrary 3-SAT open. [General result and matched controls](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001C/SHARED-REPORT-CANCELLATION-20261115-001C-P001_order_and_obstruction/proof.md) · [Verified counts](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001C/SHARED-REPORT-CANCELLATION-20261115-001C-P001_order_and_obstruction/checks.json)

With nine checks, grouping the eight open checks left to right or balancing them takes exactly 10,491 ordinary proof nodes on identical input. Their longest chains of dependent resolutions are 34 and 22, respectively. Generally, the balanced proof has at most five levels for the strict clause chain, three for each level of joins, and eight at the final close. Conversely, a binary proof of depth \(d\) can reach at most \(2^d\) input leaves, and every original strict clause is necessary. Thus the optimal ordinary proof depth is \(\Theta(\log h)\) while the optimal total number of nodes is \(\Theta(h)\). The parallel schedule assumes all source checks are available. [Depths from the actual certificates](../../proofs/SHARED-REPORT-CANCELLATION-20261115-001C/SHARED-REPORT-CANCELLATION-20261115-001C-P001_order_and_obstruction/comparison.json)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — cancellation from strict clauses | **Status:** Successful | Both named and unnamed proofs replay |
| Local direction — change grouping and arrival | Continue at three reports per check | Pair checks always have a short cycle proof when inconsistent |
| Broader exploration — shortcuts for SAT | Known alternative | Gaussian elimination covers supplied parity checks on these reports at any arity |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | A sharp test for one proof line and a short replacement proof |

The original question about total work has a definite answer for this family. A single line fails for an algebraic reason while the complete proof remains linear. Observing a failed representation or a growing table gives no general lower bound for all solving methods.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Conditional reports for three-way parity checks | 2/3 | 3/3 | Join two of the four test checks → derive a reusable four-report summary or identify the first failed inference | Selected · started |
| 2 | Interacting non-affine checks | 2/3 | 2/3 | Test a growing family against parity elimination and small case splits → reassess when either shortcut scales | Alternative · deferred |

For #1 the six-report control has four three-way checks of odd total charge. Each pairwise sum keeps four reports, and deleting any one check gives eight models. It is a bounded way to investigate the cost of reporting more than two endpoints in the unnamed calculus. The remaining target is a checked strict-input derivation and a bound across increasing sizes. For #2 a growing set of non-affine constraints would challenge a decision shortcut closer to G3. The missing discriminator is a family that survives both a change of variables and small explicit case splits. A single bounded non-affine relation over an affine system can already be handled by conditioning on its arguments.

**Basis:** Constructive proofs, ancestor-checked original clauses, two formal calculi, exact Boolean matrix ranks, finite satisfiability and deletion controls, and independent mathematical and checker replays within this task. The external design advisor returned its weekly usage limit. No external result supplies a missing proof step.

**Corrections:** None. Raw-bit inlining fails and two different name-free proofs succeed on the same instance. The earlier substitution result remains valid under its stated interface.

**Goals:** G3 and G16 gain a way to distinguish an obstruction to a single report from the total work of a proof. No general SAT time bound follows.

**Assumptions:** The specified strict encoding, original variables, supplied wiring, primitive proof language and the unit full-row table convention are explicit parameters of the comparisons. No standing assumption changed.

**Basket:** B181 remains the broad SAT decision-to-certificate question. TWO-CHOICE-IMPLICATIONS-20261115-001#2 concerns flat and factored input presentations. Neither was taken; the present study kept the strict input fixed.

## Final report as sent

2026-11-15 20:47:22 UTC

| Scope | Verdict | What the checks showed |
| --- | --- | --- |
| This attempt — cancel three overlapping checks | **Status:** Successful | 1,968 original clauses yield a checked contradiction |
| Local direction — change the grouping | Continue at three reports per check | Four conditional lines suffice for each connected pair-check path |
| Broader exploration — shortcuts for SAT | Known alternative | Every consistent set of supplied parity checks can be solved by elimination on the reports |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | Linear total proof work and logarithmic parallel proof depth on cycles |

On nine checks, two proofs used exactly 10,491 nodes. Grouping changed the longest dependency chain from 34 resolutions to 22. On six checks, putting three disjoint pairs first gave 454,272 rows for their single XOR, versus 216 for the three separate relations. Both arrival orders still had 24,277 primitive steps in the conditional proof.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Conditional proofs for three-report checks | 2/3 | 3/3 | Combine two checks that leave four reports → get a checked summary or locate the first failed step | Selected · started |
| 2 | Growing sets of non-affine checks | 2/3 | 2/3 | Test parity elimination and small case splits → reassess if either scales | Alternative · deferred |

The four-check test for #1 already has the required overlap. Removing any check restores eight report assignments. Its efficient decision algorithm is known. The open question is how much an unnamed proof must retain.
