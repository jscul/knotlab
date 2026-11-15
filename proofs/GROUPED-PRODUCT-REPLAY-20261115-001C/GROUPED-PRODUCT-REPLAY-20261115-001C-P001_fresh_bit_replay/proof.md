# Replaying a gated pair XOR below formal degree three

Status: Proved

## Standard statement

Let \(p_i=x_i y_i\) be the bottom gates of a read-once AND on \(2m\) distinct positive Boolean literals, with \(m\ge2\). Write \(U=\sum_i p_i\) and \(Q=\sum_i x_i y_i\) over \(\mathbb F_2\). The source may give \(U\) an explicit alias \(u=1\cdot U\). Its last producer gate is \(s=zU\), for an original bit \(z\) outside the pairs. The final AND output is \(T\).

Work in the occurrence-counted, formal degree-two polynomial resolution calculus with acyclic declarations of products of affine factors. An atom \([P]\) means \(P=0\). The input is a checked refutation and a cut after the producer. Every old premise used across the cut must have a new derivation. Here the supported premises are actual original clauses, Boolean choices, the standard clauses defining the meaning of the *final* AND, the specified pair and aggregate defining equations where their images are derivable, and the following explicit reports. A report at \(\alpha\in\{0,1\}^{2m}\) says that if the inputs take those values, then \(U=Q(\alpha)\). The caller supplies the index and \(\alpha\); the converter regenerates the report and authenticates the old clause. This defines a proof interface even when the old prefix contains other ordinary deductions. The [root-only conversion](../../GROUPED-PRODUCT-REPLAY-20261115-001A/GROUPED-PRODUCT-REPLAY-20261115-001A-P001_regroup_final/proof.md) also has a separate fixed-arity argument for arbitrary public crossing premises.

1. Fixing \(z=0,1\) eliminates \(s\) and all the pair names while carrying \(U\) directly as \(Q\), provided the displayed inferences on each case remain within degree two and any retained declaration has affine factors. A scalar-factor declaration can also be erased when the residual product has degree at most two. In particular this handles additive uses of \(U,s\) and ordinary multiplication of \(U\) by \(z\). Genuine quadratic side disjuncts and multiplication elsewhere in a line are permitted.
2. Alternatively split on the Boolean value of the quadratic \(Q\). If the later proof uses the pair names only through their formal sum, its two public values \(U,s\) become the affine expressions \(b,bz\) on the case \(Q=b\). All subsequent degree-two uses of these values and all subsequent legal declarations then replay. This includes additional independent multipliers. Each method uses two cases and polynomial overhead in the explicit input proof and reports. No pair gate or aggregate name is retained. The target keeps a single differently grouped producer of \(T\) shared by both branches.
3. Without a split, \(zQ\) can already prevent the direct replay at a single multiplication. After a split on \(z\), a later independent \(wQ\) can still prevent it. In the checked instances each obstructed value has Boolean degree three on a literal restriction that makes **all** the new AND names zero.

## Nearest known result

Restriction and proof simulation in bounded-degree polynomial resolution are established techniques. Arithmetic-circuit proof balancing concerns a different proof language. The earlier local simulation made every name affine under given affine observations. It would still need to handle each \(x_i y_i\) there. Here the aggregate remains a quadratic in the same degree-two proof, and a different output bit can be chosen for the split. All substitutions and reductions below are proved directly. [Khaniki on resolution over polynomial calculus](https://eccc.weizmann.ac.il/report/2020/034/) · [Hrubeš and Tzameret on balancing arithmetic proofs](https://arxiv.org/abs/1112.6265) · [Earlier affine-name simulation](../../AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/proof.md)

## The checked replacement of a premise

Build the new AND chain in order \(x_1,\ldots,x_m,y_1,\ldots,y_m\). Its first gate uses \(x_1,x_2\), and every subsequent prefix contains these two inputs. It has no gate computing a source pair. From its own declarations A derives \(T\Rightarrow x_i,\ T\Rightarrow y_i\) and the all-inputs-imply-\(T\) clause. Source private intermediate clauses are never imported as axioms. Each time a source step cites a prefix premise, check the actual target disjunction and its multiplicities.

For a requested assignment report, let \(H_\alpha\) be the disjunction of the literals saying that some pair input differs from \(\alpha\). For one pair at values \(a,b\), use the formal identity
\[
 xy+ab=(x+a)y+a(y+b).
\]
Start from the Boolean choices for \(x,y\), multiply the selected \(x+a\) by \(y\), and combine with the selected \(y+b\) with coefficient \(a\). The unselected equations are the two failure literals. In the source, add the defining equation \(p_i+x_i y_i\) to get the reported pair value. This extra step is unnecessary in the target. Sum the pair reports, adding both equational sides with coefficient one. Their disjoint guards give \(H_\alpha\vee[Q+Q(\alpha)]\). This costs \(O(m)\) nodes per assignment. With an old XOR alias, its defining axiom yields the old report on the alias. The same construction on the target needs no alias. B gives a separate polynomial derivation of the Boolean choice \(E_Q=[Q]\vee[Q+1]\). [Direct quadratic proof](../../GROUPED-PRODUCT-REPLAY-20261115-001B/GROUPED-PRODUCT-REPLAY-20261115-001B-P001_carry_quadratic_xor/proof.md)

## Fix the fresh bit

For \(z=b\) use the failure guard \(H=[z+b+1]\). Throughout that branch substitute \(z\mapsto b,\ p_i\mapsto x_i y_i,\ U\mapsto Q,\ s\mapsto bQ\). The old defining equation of \(s\) maps to zero **formally**, before any multiplication rule is emitted. Fixing only the abbreviation \(s\) while leaving \(z\) symbolic would leave the cubic \((z+b)Q\). The old final-root clauses and assignment reports do not use \(z\), so adding the guard gives their required conditional versions.

An original input clause may contain \(z\), and it remains a genuine premise on the original variable roster. More generally, for a derived clause \(L\) and one of its formal atoms \(P\), write
\[
 P(z)+P(b)=(z+b)D,\qquad \deg D\le1
\]
when \(\deg P\le2\). Multiply the selected \(z+b\) in \(E_z\) by \(D\), and combine the result with \(P\) in \(L\). It replaces that occurrence by \(P(b)\) under the guard. Repeat for every affected occurrence and contract only the extra guard copies. An unaffected clause is weakened once. This works for repeated literals and formal powers.

Replay the suffix in order. Binary combinations contract their extra guard, and a Boolean default for a quadratic image uses the derived choice \(E_P\). Check the degree of every displayed atom, selected occurrence and multiplier, including the multiplier of a zero polynomial. A retained fresh declaration must still have affine factors in the target language. If a scalar factor permits complete elimination, substitute its product and derive the zero image of the old definition. A name needed in both branches can receive separate new defining variables after the common AND producer. Their already-defined right hand sides make these legitimate unconditional target declarations. The induction gives \(H\) on each branch because each source refutation ends with the empty disjunction. A cut on the two complementary failure atoms derives the empty disjunction in the same target proof.

## Fix the XOR instead

The branch guard is \(H=[Q+b+1]\) and the condition \([Q+b]\) under that guard is exactly \(E_Q\). Map the first \(m-1\) old pair names to their true quadratics. Give the last name the expression
\[
 p_m\ \longmapsto\ b+\sum_{i<m}x_i y_i .
\]
The last pair's defining equation now has image \(Q+b\); its guarded version has the genuine derivation \(E_Q\). The written sum of the pair names becomes \(b\) **as a formal polynomial**. Consequently \(s\) maps to \(bz\) whether its old declaration used the sum literally or through a named alias. On the selected case all individual assignments also agree with their original Boolean meanings.

A target assignment report \(H_\alpha\vee[Q+c]\) and \(E_Q\) yield \(H_\alpha\vee H\vee[b+c]\) by combining selected atoms. This is exactly the conditional image of the old report. All other public premises are handled as before. For the general suffix guarantee, take formal expressions over original variables, \(T\), \(U\), \(s\), and later names, with \(U\) either written in full or named. Assume the factors and other printed fields have the indicated degree in those public symbols. After replacing \(U,s\) by \(b,bz\), affine fields remain affine and quadratic fields remain quadratic. This proves the full suffix simulation by induction on its proof DAG. The checker also accepts any wider input on which each formal operation and crossing-premise check passes. An arbitrary old proof citing other private facts has no such guarantee.

Let \(S\) count written proof nodes, \(V\) the number of distinct variable names that occur, \(W\) the maximum number of disjuncts in an input or proof clause, and \(R\) the number of explicitly requested assignment reports. There are \(O(S+V+m)\) variables available in the two-branch output. A quadratic has \(O((S+V+m)^2)\) terms and its Boolean choice takes a number of nodes linear in its sparse term count. Each original input clause requires \(O(W+1)\) nodes to condition it, and each other ordinary operation takes constant extra nodes per branch beyond Boolean choices. Adding the common prefix and reports gives the coarse bound \(O(m^2+Rm+(S+1)((S+V+m)^2+W+1))\) nodes. The symbol or bit length and construction time are polynomial as well: even a tentative substitution into a printed quadratic has degree at most six before normalization or rejection in the unconditioned comparison, and degree at most four on each claimed branch. The sparse representation has polynomially many terms at these fixed degrees. The two positive methods use only degree-two printed proof steps.

## An inspected contradiction and the first failing step

The downloadable four-input example uses twenty strict ternary clauses. Positive units on all four inputs and a negative unit on \(y_2\) are each encoded by four clauses with two independent padding bits. The two groups forcing opposite values of the sum separately leave \(z\) free. To derive one side, force \(T=1\) with the all-inputs-imply-\(T\) clause, read every input back through \(T\), then resolve a checked XOR report at that assignment. The other side uses the input assignment with just \(y_2\) flipped. Neither the old nor new proof receives a free assertion of the XOR.

With zero-based row indices, the original pair names are 9 and 10, \(T\) is 11 and \(s\) is 12. The source has **no XOR alias**. Row 164 selects \([p_1+p_2]\) from row 155, multiplies it by original variable 5 (\(z\)), and concludes \([zp_1+zp_2]\). The same operation after unrestricted pair substitution first prints the forbidden monomial \(x_1y_1z\). On the two \(z\) branches its actual checked target clauses are:

| Source row | Target row | Target conclusion |
| --- | --- | --- |
| 164 | 217 | \([z+1]\vee[0]\) |
| 164 | 379 | \([z]\vee[x_1y_1+x_2y_2]\) |

The following rows combine the result with the old gated definition, now a derived truth on each branch. The opposite XOR report supplies the other side of a real selected pivot and the joined proof ends in the empty clause. The checker accepts all 174 original nodes and all 397 new nodes. The three target names compute \(x_1x_2,\ (x_1x_2)y_1,\ ((x_1x_2)y_1)y_2\); their recycled numeric IDs do not denote the old pair functions. Fresh-bit replays also pass at 3, 5 and 9 pairs. [Complete old and new certificates and trace](rewrite.json) · [Checker](check.py) · [Recorded outcomes](checks.json)

For a negative control let the later proof multiply the still-available \(U\) by another independent original coordinate \(w\), and use it in the deduction of the contradiction. Row 169 of the second alias-free certificate selects \([p_1+p_2]\) and multiplies it by \(w\). With \(z\) fixed, direct substitution would print \(wQ\). Set \(x_2=0\) and all irrelevant inputs to zero. Every new AND gate vanishes. On \(x_1,y_1,w\) the output is one only at \(111\). Any polynomial of degree at most two has even parity across these eight inputs, so **no single quadratic** over the remaining bits and retained gates represents that displayed value. The identical argument with \(z\) as the third bit proves the obstruction for unconditioned \(zQ\). A different grouping, case assumption or proof may encode the information differently. On the version with the extra \(w\) use, the two cases on \(Q\) produce a checked 483-node proof. The result concerns the rewrite and the supplied explicit refutations. [Additional multiplier and complete repaired proof](parity_rewrite.json) ∎
