# Joining two strict three-report checks at a shared report

Status: Proved

## Standard statement

Let \(a,b,(x_i,y_i,z_i)_{i=0}^{5}\) be independent Boolean input bits. Use \(F_i=z_i(x_i y_i+ab)\) as notation for an input function, with arithmetic over \(\mathbb F_2\). A check on three report indices has a specified parity charge. Its input is the strict 3-CNF below, including fresh, private variables for each excluded original assignment.

Join two checks with one common report \(m\) and four distinct other reports. For every pair of charges, the existential projection of their two strict blocks onto the four surviving input triples and the shared \(a,b\) is described by sixteen selector-guarded quadratic clauses. Each has a derivation from just those two blocks in the existing unnamed degree-two multiset calculus. This holds under renaming report positions and the private variables. It applies with the actual \(a,b\) shared through both checks, even when their values are pinned.

For supports \(012,034,135,245\), with charges \(0,0,0,1\), the first two and last two checks give opposite summaries of the same four original triples. Together they give a 136,320-node primitive refutation of the 30,960 input ternaries. It introduces zero names for products or reports. Every input clause is an ancestor of the final empty clause in this construction. The machine-readable proof includes the complete raw CNF and every indexed deduction. [Portable certificate](four-check-proof.jsonl.gz) · [Selected rows and input ancestry](trace.json) · [Checker output](checks.json)

## Nearest known result

Davis–Putnam elimination combines clauses at the two values of an eliminated Boolean variable. For these same gated reports a predecessor gives four selector cases for a check on two reports, then composes checks along paths whose surviving reports are two endpoints. Its one-line obstruction already covers four surviving reports. Here each original check uses three reports, the first join must retain four, and both halves derive independently checkable complementary summaries on the complete strict input. The proof uses elementary elimination and parity addition throughout. External novelty is unassessed. [Davis and Putnam, *A Computing Procedure for Quantification Theory*](https://homepage.cs.uiowa.edu/~tinelli/classes/295/Spring03/papers/Dav60.pdf) · [Two-endpoint proof and its one-line obstruction](../../SHARED-REPORT-CANCELLATION-20261115-001C/SHARED-REPORT-CANCELLATION-20261115-001C-P001_order_and_obstruction/proof.md) · [Unchanged primitive verifier](../../QUADRATIC-ROUTE-TRANSFER-20261115-001A/QUADRATIC-ROUTE-TRANSFER-20261115-001A-P001_quadratic_substitution/solver.py)

## The raw input

For each three-index support, list all \(2^{11}\) assignments to \(a,b\) and its three original triples. Each tuple whose three report values have the wrong parity yields the width-eleven clause that forbids exactly that tuple. For its literals \(L_1,\ldots,L_{11}\), use eight new variables \(s_1,\ldots,s_8\) and nine strict clauses

\[
 (L_1\lor L_2\lor s_1),\quad
 (\neg s_j\lor L_{j+2}\lor s_{j+1})\ (1\le j\le7),\quad
 (\neg s_8\lor L_{10}\lor L_{11}).
\]

All eleven original positions differ within a row. Each \(s_j\) belongs to that row alone. When every \(L_j\) is false, the first eight clauses force \(s_8=1\) and the ninth fails. When some literal is true, set \(s_j=1\) exactly when the first \(j+1\) literals are false. This assignment extends the original tuple. Resolving successively on \(s_1,\ldots,s_8\) also recovers the exact width-eleven clause *syntactically* from the nine indexed input axioms. Every step uses the primitive linear combination on complementary literal equations and deletion of the false equation.

For fixed \(a,b\), a private triple realizes report value one on one of eight assignments if \(ab=0\), and three if \(ab=1\). On three triples the odd counts are respectively \((8^3-6^3)/2=148\) and \((8^3-2^3)/2=252\). Three settings of \(a,b\) have product zero, so a zero-charge check excludes \(3(148)+252=696\) tuples. A one-charge check excludes the other 1,352. The four concrete blocks have 3,440 forbidden tuples, 27,520 private variables, 20 original bits, and 30,960 strict clauses. [Deterministic input encoder and row lifter](solver.py)

## Exact projection and witnesses

For outside set \(D\), selector assignment \(\sigma\in\{0,1\}^{D}\), and charge \(c\), define the failure disjunction \(H_\sigma=\bigvee_{i\in D}[z_i\ne\sigma_i]\) and the raw quadratic

\[
 P_{\sigma,c}=c+\sum_{i:\sigma_i=1}x_i y_i+
                    \bigl(\sum_i\sigma_i\bmod 2\bigr)ab .
\]

The exported clause is \(H_\sigma\lor[P_{\sigma,c}=0]\). Only the clause at the actual selector setting asks for its equation. The conjunction therefore expresses \(\sum_{i\in D}F_i=c\).

Given checks \(\{m,i,j\}\) and \(\{m,k,l\}\) of charges \(c_L,c_R\), their sum requires the four surviving values to have parity \(c_L+c_R\). Conversely, this parity makes the two requirements for \(F_m\) identical. Its desired value zero is realized by \(z_m=0\). Desired value one is realized by \(z_m=x_m=1,\ y_m=1+ab\). These choices preserve every fixed surviving bit and both shared bits. Independently fill the private chains of the two checks by the preceding rule. This proves exact projection with a common witness for the eliminated triple.

For full selector guards of precisely this form, charge zero has 15 individually necessary clauses and one tautology, at \(0000\). Charge one has 16 individually necessary clauses. To witness deletion, fix that mask and \(ab=0\). For charge zero and a nonempty mask, make exactly one selected product equal to one. For charge one, set every product to zero. Only the matching clause fails. These counts apply to deletion from this explicit representation. Other ways of grouping selectors or choosing proof clauses can have different costs.

The projected population on the 14 original boundary bits is 10,144 assignments for charge zero and 6,240 for charge one. Indeed the fixed-\(ab\) count of odd assignments on four triples is \((8^4-6^4)/2=1400\) for product zero and \((8^4-2^4)/2=2040\) for product one. Thus \(3(1400)+2040=6240\). [Exhaustive two-child witness tests](check.py)

## Derivation with the degree-two rules

A proof atom \([f]\) means \(f=0\). Clauses are multisets of these atoms. The rules used here include the Boolean axiom \([u]\lor[u+1]\), linear combination of one selected occurrence per parent, formal multiplication of one selected occurrence subject to degree two, weakening, deletion of \([1]\), contraction of duplicated occurrences, and the true atom \([0]\).

1. Fix three selectors in one original block. The selected equation \(P_{\sigma,c}\) uses only the active product variables. Fix those variables as well. On an assignment where the equation fails, every completion of the unused original data is an actual forbidden tuple of this block. Lift their width-eleven clauses from their strict input chains and resolve opposite values of the unused variables. The resulting literal clause excludes the fixed values. Weakening adds the selected equation.
2. On an assignment where the equation holds, derive the value of each active product from Boolean axioms. When \(x=s,y=t\) are the fixed bits, choose \([x+s]\) in the Boolean axiom for \(x\), multiply it by \(y\), and add \(s[y+t]\) selected from the Boolean axiom for \(y\). The selected result is \([xy+st]\), with the two bit-assignment failures in the context. Add these product-value equations. The products use disjoint variables within the fixed selector case. Their values sum to \(c\), giving exactly the required equation. For the empty true polynomial use the true axiom. Weaken to include the fixed selector failures.
3. Cut on opposite values of each active data variable, contracting both copies of the common context in each such cut to one. This gives \(H_\sigma\lor[P_{\sigma,c}]\) for each of the eight original selector settings. Every actual input premise used in the derivation comes from that block.
4. For a fixed outside mask on \(i,j,k,l\), condition on \(z_m=\beta\). Add the two selected child quadratics. Their equal occurrences of \(\beta(x_my_m+ab)\) cancel as formal polynomials, leaving the outside quadratic with charge \(c_L+c_R\). Both parents also contributed the failure of \(z_m=\beta\). Contract the duplicate occurrence. Repeat for the other \(\beta\), then cut on the two complementary failures, delete \([1]\), and contract the outside context. The surviving clause contains exactly the four outside failures and one quadratic. Repeating for all sixteen masks completes the derivation.
5. Joining \(012,034\) eliminates \(0\) and yields charge zero on \(1,2,3,4\). Joining \(135,245\) eliminates \(5\) and yields charge one on the same four triples. For each mask add the two selected, complementary equations, delete the resulting false atom, and contract each duplicated outside failure. The sixteen resulting clauses exclude every selector setting. Ordinary cuts on the four selector values now derive the empty clause.

The four original blocks account for 135,808 primitive nodes. With their eight cases per block available, each join costs 176 more nodes, eleven per outside mask. The two opposite summaries then need 160 nodes to reach the empty clause. Only step 2 multiplies, always a linear operand by a single variable. Neither substitution of a truth-table identity as a premise nor implicit Boolean reduction of a cubic is part of the derivation.

## One deduction in the portable proof

Use mask \(1010\) in order \(1,2,3,4\). Write \(p_i=x_i y_i\) here solely to label the printed monomials. For \(z_0=0\), primitive rows 7159 and 35314 supply the selected quadratics \(p_1+ab\) and \(p_3+ab\). Their addition at row 135918 gives \(p_1+p_3\). For \(z_0=1\), rows 21425 and 49578 supply \(p_0+p_1\) and \(p_0+p_3\). Their addition at 135920 gives the same \(p_1+p_3\). Rows 135919 and 135921 contract the two copies of the \(z_0\)-failure in each branch. The Boolean cut and its multiset contractions finish at 135928, with the clause

\[
 (\neg z_1\lor z_2\lor\neg z_3\lor z_4)\ \lor\ [x_1y_1+x_3y_3=0].
\]

Its ancestry contains precisely 192 forbidden tuples from each of the two left checks, for 3,456 actual strict axioms. One such tuple has long clause \((1,2,3,4,5,-6,-7,-8,9,10,11)\) in signed integer notation, represented at input indices 63 through 71 using private variables 77 through 84. Row 136104 is the independently derived right summary at the same mask, with \(1+x_1y_1+x_3y_3\). Combining them and contracting their guards gives the pure selector exclusion at row 136225. The complete proof ends at zero-based row 136319. The trace gives those branches and an odd-weight mask \(1000\), where the common \(ab\) must survive. [Actual rows, selected equations, and raw clause chains](trace.json)

## Checks and limits

The portable proof is gzip-compressed JSON Lines. Its first record declares the literal CNF and variable bound. Each subsequent record is one zero-based primitive instruction in the existing wire format. The checker reads every instruction into the unchanged verifier, checks block ancestry for all 32 derived child clauses and all 32 joined clauses, and traces the complete input ancestry of the four worked masks. The construction uses 111 shared parents, width at most 23 counting repeated disjuncts, and formal degree at most two. [Primitive certificate](four-check-proof.jsonl.gz) · [Numerical checks](checks.json)

The checker compares every one of the \(2^{14}\) boundary assignments, on each side, with all eight candidate middle triples. A separate SAT implementation checks the two literal source blocks under selected boundary pins and checks the unrestricted four-block CNF with final charge zero and one. All eight even global charge patterns have raw strict-CNF models. To see the general sign condition, every report occurs twice, so an odd total charge is inconsistent. For even charges \(c_0,\dots,c_3\), set \(F_0=F_1=F_3=0,\ F_2=c_0,\ F_4=c_1,\ F_5=c_2\). The last equation follows from even parity. With \(a=b=0\), each prescribed report is realized by \(x_i=y_i=1,z_i=F_i\).

Dropping the second selected term at primitive addition 135920 while keeping the claimed conclusion fails the old row checker on the authenticated parent clauses. Dropping \(ab\) from an odd-weight mask gives a wrong Boolean answer when \(a=b=1\) and every selected \(x_i y_i=0\). Finally, pinning \(a=b=0\) and every other selector to zero leaves \(z_i x_i y_i+c\) on the free three-bit cube. Its truth-table parity is odd for both charges, while every degree-at-most-two polynomial has even truth-table parity there. Thus a single raw quadratic equation cannot represent the four-report parity without conditioning. The stronger one-disjunction result in the predecessor concerns the same family of surviving original functions. The primitive-node count measures this concrete certificate. A lower bound on general solver time or on the shortest proof would require a separate argument.

From this directory, run `python3 -B check.py` to inspect the supplied result, or `python3 -B solver.py <output-directory>` to regenerate the portable certificate and trace from the original encoder. The certificate can also be replayed directly with `verify_certificate(path, four_check_source())`. [Generator](solver.py) · [Independent checker](check.py)
