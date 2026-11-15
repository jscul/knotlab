# Changing the grouping of one AND inside a proof

The four-input AND has the same value in \((ax)(by)\) and \(((ax)b)y\). Making *every named intermediate* affine takes five parts for the first grouping and four for the second. These are exact minima over affine partitions of the original sixteen assignments. The checked refutation had 147 nodes in each grouping. The saving concerns the number of parts a proof translation might use; the measured proof sizes were equal. [Proof](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001A/GROUPED-PRODUCT-REPLAY-20261115-001A-P001_regroup_final/proof.md) · [Original and regrouped deductions](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001A/GROUPED-PRODUCT-REPLAY-20261115-001A-P001_regroup_final/rewrite.json)

The polynomial rewrite rebuilds what the later proof can actually cite. Both AND groupings derive the clauses saying the output implies each input and that all inputs together imply the output. A proof using these clauses or supplied public deductions from them can reuse its later lines for any number of inputs. For four inputs the conversion also covers arbitrary old prefix deductions passed to the later proof if every crossing clause and later proof inscription is public. Its fallback uses at most sixteen assignments and polynomial overhead at this fixed arity. With a growing number of inputs and arbitrary derived crossing facts, the fallback has an exponential factor. [Proof-interface theorem](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001A/GROUPED-PRODUCT-REPLAY-20261115-001A-P001_regroup_final/proof.md)

Write \(U=p_1+\cdots+p_m\), \(p_i=x_i y_i\), in the original proof. In the new proof \(Q=\sum_i x_i y_i\) is an ordinary quadratic polynomial. A polynomial-size checked derivation gives its Boolean choice, and each used old boundary fact is rederived. A crossed AND chain, beginning with \(x_1x_2\), removes every original pair definition. Both aggregate values then coexist. On two pairs the source had 124 nodes, the rewrite 194. New row 186 selects opposite values of \(Q\), and row 189 selects opposite values of the retained AND. An additive occurrence of \(Q\) can remain in a disjunction even when another equation on that line is multiplied. [Direct XOR certificate](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001B/GROUPED-PRODUCT-REPLAY-20261115-001B-P001_carry_quadratic_xor/rewrite.json) · [Proof](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001B/GROUPED-PRODUCT-REPLAY-20261115-001B-P001_carry_quadratic_xor/proof.md)

If the source multiplies its pair XOR by a fresh bit \(z\), the direct image \(zQ\) has degree three. On the two cases \(z=0,1\), the required images are \(0,Q\). In the saved strict example source row 164 multiplies \(p_1+p_2\) by \(z\). The converter derives target rows 217 and 379 in its two branches and checks the final empty disjunction. All 174 source nodes and 397 new nodes use the same original twenty clauses. The source writes the sum directly and the target retains only three names for its AND chain. [Complete certificate and row map](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001C/GROUPED-PRODUCT-REPLAY-20261115-001C-P001_fresh_bit_replay/rewrite.json)

If the suffix also asks for \(wU\) with an independent \(w\), fixing \(z\) leaves \(wQ\) in that actual deduction. The second certificate's source row 169 first encounters the obstruction. On three free input bits the remaining value is true only at \(111\), while every quadratic has even parity across those eight inputs. The crossed AND names are all zero on this restriction. Asking instead for \(Q\) uses its derived Boolean choice. On \(Q=b\) the two public expressions are \(U=b\) and \(zU=bz\); other permitted uses through those expressions can then be replayed at degree two. The 178-node second proof becomes a checked 483-node proof with this choice. This statement concerns explicit contradiction proofs. The replays do not give an algorithm for general satisfiability. [First obstruction and alternative proof](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001C/GROUPED-PRODUCT-REPLAY-20261115-001C-P001_fresh_bit_replay/parity_rewrite.json) · [General construction](../../proofs/GROUPED-PRODUCT-REPLAY-20261115-001C/GROUPED-PRODUCT-REPLAY-20261115-001C-P001_fresh_bit_replay/proof.md)

| Scope | Verdict | Reason |
| --- | --- | --- |
| This attempt — regroup the AND and carry the pair parity | **Status:** Successful | Actual before-and-after refutations and a first failed multiplication |
| Local direction — choose what value to ask about | Continue | A two-way split on the derived XOR handles later uses for which a two-way split on the fresh input fails |
| Broader exploration — shortcuts for SAT | Known alternatives | A supplied proof and its boundary deductions still matter |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Capability gained | One can recognize and implement a proof shortcut from the public quantities that later steps use |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Ask for a shared quadratic value used by several multipliers | 2/3 — one choice can serve many later uses | 3/3 — explicit second multiplication | Add a new independent multiplier and compare the fresh-bit and parity splits → stop after a full replay or an unavoidable degree failure | Selected · started |
| 2 | Cover arbitrary SAT decisions with small checkable proofs (B181) | 3/3 — bears on unrestricted work | 1/3 — no simulation for arbitrary algorithms | Identify a decision method outside the formal calculus → reassess if it yields a bounded certificate | Alternative · deferred |

For #1 a single extra multiplier gives the first failure of the fresh-bit split, and the parity split completes the same refutation. This bounded discriminator settles which of these two observations covers arbitrary later uses of these public values. Recognizing useful low-cost observations in proofs with several different reported quadratics remains open. For #2 the method has a larger possible payoff for G3 but currently lacks a corresponding simulation.

**Basis:** Three constructive local results, strict-CNF certificates with exact occurrence and degree checks, independent truth evaluations, an exact four-bit partition comparison and an independent same-task review. The external design advisor returned its weekly usage limit. No external theorem is needed to establish the rewrites.

**Corrections:** None. The preceding rank result measures simultaneous affine descriptions of the old named values. Changing the names required by the proof, or allowing a reported value to remain quadratic, changes the question.

**Goals:** G3 and G16 gain a checked change of representation for a supplied proof and a demonstrated boundary for one-bit reports.

**Assumptions:** The original proof, its cut, its allowed operations and the premises cited across the cut are explicit. An affine-part count and proof size are distinct measurements. No standing assumption changed.

**Basket:** B181 remains the broad decision/certificate question. TWO-CHOICE-IMPLICATIONS-20261115-001#2 compares equivalent flat and factored formula presentations; this study instead keeps the input formula fixed and varies its proof. Neither item was taken.

## Final report as sent

2026-11-15 19:45:50 UTC

| Checked proof | Result |
| --- | --- |
| Final AND only | Both requested groupings took 147 proof nodes. The minimum number of affine parts fell from five to four. |
| Final AND and pair XOR | The new proof used the quadratic XOR as a pivot and the AND as another pivot. It took 194 nodes and retained neither original pair name. |
| Fresh bit times the XOR | Asking for the fresh bit gave a complete 397-node proof. |
| One more independent multiplier | Fixing the first bit left a genuine cubic at source row 169. Asking for the XOR instead gave a complete 483-node proof. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Ask for the value shared by later multiplications | 2/3 | 3/3 | Add a second multiplier → check whether one split still gives a full proof | Selected · started |
| 2 | Extend the result to arbitrary SAT decisions | 3/3 | 1/3 | Identify an uncovered decision method → reassess if it yields short certificates | Alternative · deferred |

The first comparison is complete. Once the proof knows the XOR’s value, every later multiplication by that XOR becomes multiplication by zero or one.
