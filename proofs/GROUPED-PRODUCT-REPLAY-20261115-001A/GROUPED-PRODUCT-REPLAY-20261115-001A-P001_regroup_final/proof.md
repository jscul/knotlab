# Replacing a product tree while preserving its final AND

Status: Proved

## Standard statement

In a checked syntactic degree-two multiset refutation on \(n\) Boolean inputs, let a specified prefix introduce precisely one binary AND tree on \(k\ge2\) distinct signed original inputs. Other deductions may occur anywhere in the prefix. The tree has \(k-1\) charged fresh definitions and a final name \(T\). At the specified boundary, later deductions may read the original variables, \(T\), and fresh names declared later from these public variables. Every actual premise imported from the prefix must have a public clause.

For one such group with four inputs, the old tree can be replaced by **any sequential grouping and ordering** of the same inputs, preserving \(T\), the original CNF, and formal degree two. Arbitrary legal quadratic use in the prefix is allowed. A refutation with \(S\) nodes is converted to one with \(O(S)\) nodes independently of its widths. The explicit construction uses 16 input cases. For variable \(k\) its general bound is \(O(2^k(k+1)(S+k))\) nodes.

There is also an \(O(S+k)\)-node conversion for variable \(k\) under a checkable condition. Every imported clause must have a supplied public derivation, allowing any subtree of its old derivation to be replaced by one of the standard AND clauses, an input axiom, a default, or a syntactic weakening of one of these. The remaining suffix is copied once. Both converters check their output in the original named calculus. Product definitions belonging only to the obsolete grouping disappear.

## Nearest known result

Boolean conjunction is associative, and fresh circuit gates with defining clauses are standard in extended resolution. The previous local named calculus derives the three clauses of one binary AND from its single formal product equation. An earlier result classified affine restrictions of a supplied fixed gate list. Here the object being changed is a checked refutation, complete with its premise references, polynomial operands, and later fresh definitions. Equality of truth tables alone supplies none of those references. The two constructions below give the required proof nodes. External novelty remains unassessed. [Binary gate derivations](../../PRODUCT-NAME-TRANSFER-20261115-001C/PRODUCT-NAME-TRANSFER-20261115-001C-P001_depth_and_unrestricted/proof.md) · [Affine restrictions of a fixed list](../../AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/proof.md) · [Krajíček on circuit evaluation and extended resolution](https://doi.org/10.1017/fms.2016.13) · [Pang’s underlying syntactic rules](https://arxiv.org/html/2610.00837v2#S1)

## A complete rewrite

The stored example contains the same 18 strict ternary input clauses and three complete proofs, one node per physical line. Its `old_proof` is the balanced input. Its `specified_chain_proof` groups the inputs in the requested order `[1,2,3,4]`, and `new_proof` uses the crossed order `[1,3,2,4]`. Variables 1 through 4 represent \(a,x,b,y\). Four ternary clauses per input force it true. The remaining two clauses are \(\neg a\lor\neg x\lor e\) and \(\neg e\lor\neg b\lor\neg y\). Their resolvent denies the conjunction. There are seven original variables in all. [Checked old and new proofs, CNF and boundary](rewrite.json)

| Zero-based node | Old balanced definitions and deductions | New crossed order |
| --- | --- | --- |
| 0 | \(p_8=ax\) | \(s_8=ab\) |
| 1 | \(q_9=by\) | \(s_9=s_8x\) |
| 2 | \(T_{10}=p_8q_9\) | \(T_{10}=s_9y\) |
| 33 | \(a\land x\land b\land y\to T_{10}\) | The same clause from the new definitions |
| 39 | \(T_{10}\to a\) | The same clause from the new definitions |
| 113 | \(v_{11}=T_{10}a\) | The same later declaration |
| 146 | Empty | Empty |

Node 42 starts the suffix. It imports the four root-to-input clauses, the converse, and the Boolean default for \(a\). It derives \(T=1\), recovers that assertion by adding \((T+1)T\) and \((T+1)^2\), then uses the later named product and the root-to-input clauses to refute the CNF. The private identifiers 8 and 9 are local to each certificate. Their new defining equations compute \(ab\) and \(abx\), respectively. Neither obsolete pair \(ax,by\) is defined in the crossed output. The literal order \(a,x,b,y\) instead produces \((((ax)b)y)\) and retains the one shared pair \(ax\).

Both four-input outputs have **147 nodes**, equal to the old proof. Their canonical UTF-8 proof lists have 13,369 bytes, compared with 13,371 bytes for the old list, using compact JSON with sorted keys. All four declarations in each proof are ordinary ancestors of empty. Removing the five nodes outside that ancestry produces three independently verified 142-node certificates. The affine partition optimum falls from five to four in this example.

## The checked boundary

Write \([f]\) for \(f=0\). Each gate declaration is a singleton \([t+fg]\). The operands of the old tree are literal truth polynomials on the stated inputs or positive variables denoting its earlier AND subtrees. Each signed leaf has a distinct original variable. Disjoint child leaf sets and the final root covering all \(k\) leaves establish a binary tree. The prefix contains exactly its \(k-1\) declarations. All remaining original variables are available for the CNF and ordinary deductions.

The integer cut is exclusive. An imported parent is any node before the cut named by an ordinary premise reference at or after it. If the whole proof lies in the prefix, the final empty node is the required export. Inspect every atom of the imported clause, including raw monomial occurrences. Inspect every suffix clause, both selected operands of a linear combination, the selected operand of each unary rule, every multiplier, each Boolean-default identifier, and both raw factors of every later declaration. Any use of an old nonroot gate name in this interface fails the final-only check, including repeated occurrences that cancel. The initial verification still checks every node of the old certificate. Private computations inside the prefix may feed a public conclusion. Their contribution must either be replayed or replaced by a derivation of that conclusion from the new producer.

For example let \(q=by\). From \([1+a]\), multiply separately by \(q\) and \(1+q\), then add to recover \([1+a]\). The output says nothing about \(q\), although its parents used it. Direct substitution \(q\mapsto by\) produces the cubic term \(aby\). Also, multiplying the true equation \([0]\) by \(q^2\) displays only \([0]\), while direct substitution puts a formal quartic in the written multiplier. The strict four-input stress test uses both inferences on the ancestry of the final contradiction. Moving the boundary to the charged private multiplier makes that proof fail the final-only test.

## Reconstructing a public derivation for arbitrary arity

For a chain or binary tree, first derive the three ordinary AND clauses at each gate \(v=fg\). For literal truth polynomials they are \(v\to f, v\to g, (f\land g)\to v\). The accepted construction uses Boolean choices, formal multiplication and linear combination. Traverse the tree from the root to derive \(T\to s_i\) for each signed input. At each child compose the implication for its parent with the corresponding local implication by ordinary resolution, implemented by addition and deletion of the false constant. In the opposite order resolve the positive child names out of each local converse. At the root this gives \((\bigwedge_i s_i)\to T\). The resolution operands have disjoint original leaf sets, and these compositions require no large duplicate contractions. The entire set of exports takes \(O(k)\) primitive nodes. The accumulated literal listings can occupy \(O(k^2)\) occurrences.

For every old prefix node needed by the suffix, first try to derive its full public multiset by weakening one of these clauses, an original input axiom, the true axiom, or a Boolean choice on a public variable. If this succeeds, no old private premise is used. Otherwise require an ordinary public rule with public operands and recursively cover all its ordinary premises by the same test. The source DAG orders those dependencies, so each requested prefix node need be handled once. The successful nodes form a derivation with the exact required multiplicities. A private premise needed after this process supplies a concrete failure of this particular condition. There may be a different public derivation which the supplied prefix did not give.

Now copy each later rule and its formal operands, replacing parent identifiers with the new ones. Both producers use \(k-1\) fresh names, and the checked suffix refers only to the shared root and its own later fresh identifiers. Thus its post-boundary declarations, arbitrary polynomial multiplications and repeated premise uses remain legal. Each old prefix node accepted by the public rule costs one step. An export weakened from a supplied axiom costs at most a new seed and one weakening. The bound is \(O(k+S)\) nodes. Enumerating and matching explicit multisets, copying inscriptions, and checking the certificate take polynomial work in \(n\) and the explicit input length. The direct rules cover unbounded clause width in this node measure.

The five-input check exports the genuinely quadratic singleton \([T(1+a)]\). Its supplied public derivation starts from \([T]\lor[1+a]\), multiplies the first occurrence by \(1+a\), the other by \(T\), then contracts the equal products. Three old public deductions are replayed above the replacement implication. The original and resulting proofs both contain 190 nodes.

## Arbitrary quadratic prefix calculations at fixed arity

Make the new chain and predeclare the later names in their original order. Those later factors are free of old private symbols. Their availability follows from the original chronology, and they can be declared before the ordinary derivations. In all cases keep \(T\), every original variable, and every later name as variables. This retains the actual new final AND for subsequent arbitrary quadratic uses.

Choose truth values \(b_i\) for the \(k\) signed inputs. The common failure context \(H\) has one occurrence of each \([s_i+b_i+1]\). The Boolean choice for \(s_i\) gives \(H\lor[s_i+b_i]\) by weakening. If \(H\lor[f+a]\) and \(H\lor[g+b]\) are available, multiply the selected first atom by \(g\), then add \(a\) times the second selected atom. The new atom is
\[
(f+a)g+a(g+b)=fg+ab.
\]
Contract one additional copy of every member of \(H\). At a new gate, add its defining equation \([v+fg]\) to derive \(H\lor[v+ab]\). Induction up the new chain supplies \(H\lor[T+\bigwedge_i b_i]\).

Substitute the value on this case for every old **private** name. For each of its old defining equations the product calculation just given derives exactly the substituted atom \(fg+ab\) under \(H\). A child already replaced by its value supplies \(H\lor[0]\) from the true axiom. At the old root, combine the product calculation with the proven value of the *new* \(T\), and contract the duplicated \(H\). This derives the substituted old root equation while keeping the shared output symbol present. Later definitions come directly from their new unconditional declarations.

Replay the whole old refutation in this one context. A public or private Boolean default maps to a variable or constant Boolean choice. Every ordinary rule commutes with this substitution of constants and variables into the formal ring. This applies to the written multiplier even when its product vanishes. At a binary combination contract the extra \(k\) guards, retaining the original multiset counts. No formal degree exceeds two. Each branch now ends in \(H\). Merge complementary branches by adding the opposite last case equations, deleting the false constant, and contracting the repeated prefix of guards. The final conclusion is empty. The only declarations in the output are the new chain and the allowed post-boundary declarations. ∎

Each branch uses \(O((k+1)(S+k))\) nodes. At most \(k\) guards are contracted per binary operation, and the final merge takes \(O(2^k(k+1))\) nodes. In this construction the whole refutation is replayed. Merging exported clauses separately would duplicate their common side contexts and can add a contraction per occurrence. For fixed \(k\), the emitted bit length and work are polynomial in \(n\) and the encoded input. The displayed \(2^k\) construction makes no polynomial-in-\(k\) guarantee for unrestricted private prefix histories. Consecutively applying a one-group simulation to many entangled groups needs its own bound.

## Affine parts and verification

On four independent bits, the old private outputs \(ax,by\) force each simultaneous affine part to have at most four points. Indeed, each projection onto one input pair has dimension at most one if its product is affine, and the dimensions of those two projections bound the whole part's dimension by two. A part containing the all-ones input has at most two points, since the final conjunction has exactly one true value there. Four parts can therefore cover at most fourteen points. Ask \(a,b\), and split only the \(a=b=1\) case on \(x\), to attain five.

For any sequential four-input ordering one can first test its first input, continue if it is one, and repeat up to its third input. There are parts of sizes \(8,4,2,2\), and every prefix product is affine on each. For the final AND alone three affine parts cannot cover the cube. The part containing its unique true point has size one or two, leaving fifteen or fourteen points, neither a sum of two powers of two. Thus four is optimal for either chain. An exact cover calculation over all 307 nonempty affine parts confirms all the counts. This is a count of parts on which the chosen names are affine. It does not assign a node cost to the checked rewrite.

| Checked setting | Old nodes | New nodes | Old proof bytes | New proof bytes |
| --- | ---: | ---: | ---: | ---: |
| Four inputs, either chain, ordinary exports | 147 | 147 | 13,371 | 13,369 |
| Four inputs, crossed chain, private quadratic histories | 156 | 6,718 | 14,277 | 856,912 |
| Five inputs, public quadratic export | 190 | 190 | 17,599 | 17,597 |
| Eight inputs, signed permutation, ordinary exports | 307 | 307 | 28,982 | 29,090 |
| Twelve inputs, signed permutation, ordinary exports | 467 | 467 | 45,958 | 46,300 |

The named kernel checked every deduction in each complete result. A separate evaluator checked their Boolean meanings on all 128 original assignments at arity four and all 512 at arity five. It used 193 specified assignments at each larger size. Raw leaked premises, hidden squared multipliers, canceled private mentions in later factors, a wrong leaf polarity or cut, and a changed formal inference all failed their corresponding checks. The saved example is reproduced byte for byte. The finite checks are V1 within this research task. The uniform bounds follow from the constructions above. [Checker](check.py) · [Numerical checks](checks.json)

## Public API and replay

`regroup(n, cnf, proof, inputs, cut, mode="portals")` returns the new checked proof and resource counts. The requested order consists of signed, nonrepeated original inputs. Use `mode="cases"` for arbitrary private prefix deductions behind a final-only boundary. On an existing named DAG, `chain_portals(dag, inputs)` introduces the target chain and returns its root identifier, a dictionary mapping each signed input to its root-implies-input proof node, and the converse proof node. Proof sizes in bytes refer only to each complete proof list, including all operands, node identifiers, and definitions. The stored example also contains its CNF, cut and statistics. [Transformer](solver.py)

```sh
python3 -B proofs/GROUPED-PRODUCT-REPLAY-20261115-001A/GROUPED-PRODUCT-REPLAY-20261115-001A-P001_regroup_final/check.py
```
