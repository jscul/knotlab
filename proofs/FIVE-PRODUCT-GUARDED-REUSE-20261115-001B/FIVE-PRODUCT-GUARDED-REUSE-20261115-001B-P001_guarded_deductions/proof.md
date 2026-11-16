# Eight affine-query cases use six distinct terminal proofs

Status: Proved

## Standard statement

Let the five products be the adjacent products of six input bits. All sums are in \(\mathbb F_2\). Write

\[
 Q=x_0x_1+x_2(x_1+x_3)+x_4(x_3+x_5).
\]

The nine visible coordinates are \(x_0,\ldots,x_5,s,u,v\). The **rich evaluator** requires \(s=Q,\ u=x_0x_1,\ v=x_2(x_1+x_3)\). The **plain evaluator** requires \(s=1+Q\) and accepts either value for each summary. The two masks are 1 and 6 when bit zero selects the first path product. Each of the 64 inputs has one honest rich state. There are 256 plain states. After changing the opposite total to the matching total, the joint relation has 64 solutions.

A *guard* is a conjunction of affine equations on these nine coordinates. A guard is **terminal** if repeated intersection with the affine hulls of its two separate evaluator restrictions gives the empty set. A proof may ask any visible affine question, infer from a single rich restriction that its branch satisfies an earlier guard, and cite the terminal proof at that guard. Route every original honest rich point according to its answers and retain it until the terminal citation. Count the number of distinct directly terminal guards cited this way. On the displayed pair the exact minimum is **six**. A depth-three tree makes eight calls to these six guards. Two different pairs of branches literally cite the same proof under the same assumptions. The proof uses only the first summary in its queries.

That DAG contains 21 nodes and 22 parent references. Its fully expanded tree contains 23 nodes and 22 references. Under plain-first hull evaluation they use 20 and 24 separate evaluator checks after charging all eight rich entailments. Closing the eight raw leaves of these same questions costs at least 22 checks under the better of the two alternating evaluator orders at each leaf. A different eight-case tree costs only 16 checks. Thus the exact six counts the terminal proofs needed in this routing model. Total work also depends on which questions and local deductions the proof uses. [Saved proofs](certificates.json) · [Checked counts](checks.json)

## Nearest known result

The preceding investigation defines repeated exact separate affine hulls and counts terminal cases under visible parity queries. Its finite controls check fixed summary fibres and show how the two answers to one question can have different proof costs. Here different branches can cite one unchanged terminal contradiction, with an explicit check of its assumptions. Beame, Kautz and Sabharwal analyze how retaining derived clauses changes tree-like resolution proofs. The present guards, local inference rules, six-guard count and work comparisons are specific to the displayed pair of finite relations. [Predecessor finite controls](../../ONE-SIDED-PATH-SKETCH-20261115-001C/ONE-SIDED-PATH-SKETCH-20261115-001C-P001_affine_controls/proof.md) · [Beame, Kautz and Sabharwal, JAIR 2004](https://doi.org/10.1613/jair.1410)

## The six proofs and where they apply

First fix \(c=x_4\). Abbreviate \(d=x_1+x_3,\ z=s+c(x_3+x_5),\ h=u+d\). All are affine on that branch and require no extra coordinates. Rich points satisfy \(z=u+x_2d\). Plain points satisfy \(z=1+x_0x_1+x_2d\). In addition to \(x_4=c\), impose the equations in the middle column. Substitution gives the residual product in the last column.

| Guard | Further equations | Rich requires this product to be 0, plain requires it to be 1 |
| --- | --- | --- |
| \(G_{c,0}\) | \(x_3=0,\ z=0\) | \(x_1(x_0+x_2)\) |
| \(G_{c,1}\) | \(x_1=1,\ z=x_0\) | \(x_2(1+x_3)\) |
| \(G_{c,2}\) | \(d=1,\ z=x_2\) | \(x_0x_1\) |

At each guard, the plain evaluator sets both affine factors to 1. Its hull then has empty intersection with the rich evaluator. Each guard contains 64 visible states, 12 honest rich states and 16 plain states. The plain states themselves form an affine set of size 16.

After fixing \(c\), ask \(h\). The two additional questions give the following routing table for each value of \(c\).

| First answer | Third question | Answer 0 | Answer 1 | Honest rich sizes of the two branches |
| --- | --- | --- | --- | --- |
| \(h=0\) | \(z+x_3\) | \(G_{c,0}\) | \(G_{c,1}\) | 10, 6 |
| \(h=1\) | \(d\) | \(G_{c,1}\) | \(G_{c,2}\) | 4, 12 |

Indeed, if \(h=0\) then \(u=d\). When \(x_3=1\), choosing \(x_1=0\) would give both \(d=1\) and \(u=0\). Thus \(x_1=1\), \(d=u=x_0=z=0\), and the answer is 1 at \(G_{c,1}\). When \(x_3=0\), \(d=x_1\). If \(z=0\) we are in \(G_{c,0}\). If \(z=1\), \(u=d=1\) is necessary, so \(x_0=x_1=z=1\) and we are in \(G_{c,1}\). If \(h=1,d=0\), then \(u=1\) gives \(x_0=x_1=z=1\). If \(h=1,d=1\), then \(u=0\) gives \(z=x_2\).

Each of the eight citations needs a rich-side entailment. The raw branch guard, before checking an evaluator, implies only part of the target. The missing independent equations number 1, 2, 2 and 1 in the displayed order for each \(c\). In particular, the all-zero rich state at the first leaf refutes an attempted citation of \(G_{0,1}\). The two branches reaching each \(G_{c,1}\) are disjoint and both contain genuine rich points. The proof of that guard is executed once and referenced twice. [Independent nine-bit replay](terminal_library.py)

## Why five terminal guards cannot suffice

We prove a scalar capacity bound that permits arbitrary rich summaries. Project a guard onto \((x,s)\), deleting the summaries that the plain evaluator leaves free. If the plain points over the projected guard span it, their lifts span the whole guard. To see this, choose one lift for each point in an affine basis of the projection. Any nonempty fibre also supplies all the direction differences in the common fibre kernel. Together they generate the guard.

Consider a directly terminal guard with positive honest mass. Run its local hulls in sequence. At least one plain operation must strictly shrink the current guard, since rich operations alone preserve every honest rich point initially in it. Immediately before the first such plain operation all original honest points still remain. Let \(D\) be the current projection to \((x,s)\).

The polar form of \(Q\) has rank six. Indeed in the independent coordinates \(y=(x_0,x_2,x_4)\) and \(w=(x_1,x_1+x_3,x_3+x_5)\) it is the polar form of \(y\mathbin{\cdot}w\). One input hyperplane can reduce its rank by at most two, as restriction deletes one matching row and column in an adapted basis. Suppose \(D\) had codimension at most two. If \(s\) is free over its input projection \(L\), the restriction of \(Q\) to \(L\) retains rank at least two. The graph of a nonaffine function spans \(L\times\mathbb F_2\), including the graph of \(1+Q\). If \(s\) is pinned to an affine function on \(L\), the input codimension is at most one. On each hyperplane of \(L\) the quadratic still has rank at least two. Hence both levels of \(Q+s\) occur on each hyperplane of \(L\), forcing the plain restriction to span \(D\). In both cases the free-fibre argument precludes a strict plain operation. We conclude \(\operatorname{codim}D\ge3\).

If \(s\) remains free, this leaves at most eight distinct inputs. The same holds if it is pinned and the input codimension is at least three. In the remaining possibility \(s\) is pinned on a 16-point input space of codimension two. There the quadratic plus its pinned affine function still has rank at least two. Choose two directions having polar pairing 1. On every four-point coset of their span the XOR of the four values is 1, so at most three agree with a given value. This leaves at most 12 honest inputs. Each was counted once because a rich state is a function of its input. The exhaustive scalar check separately found maximum 12 over all 94,488 codimension-three affine spaces in the seven scalar coordinates. Their counts of honest inputs at sizes 4, 6, 8, 10 and 12 are 5,040, 21,504, 41,400, 21,504 and 5,040. Higher-codimension spaces sit inside some codimension-three space.

The rich-preserving routing rules send each honest input to a cited raw terminal guard that contains it. Six are necessary since \(\lceil64/12\rceil=6\). The explicit proof gives equality. An inference that has already discarded some honest rich points using the plain side or a previously discharged joint consequence can break this covering argument. The lower bound applies to the stated class of routes.

## What the checker charges

Every proof node carries a raw guard and either an affine consequence or a contradiction. Dependencies point to earlier nodes, every node must reach the final contradiction at the unrestricted guard, and each appearance in a parent list costs one reference. A terminal node runs whole-side hulls to a fixed point. The two sequential evaluation orders and simultaneous intersections yield the same answer. A rich route must verify that a nonempty rich restriction lies inside the entire cited guard. An affine split must have children exactly equal to the two raw restrictions. These rules are sound by restriction, since satisfying both sides implies satisfying the rich side and every admitted consequence. The expansion copies each referenced subproof whenever it is used and the expanded certificate is verified again. [Verifier and expander](solver.py) · [All ten saved certificates](certificates.json)

| Proof | Terminal checks | Rich entailments | Split nodes | All nodes | Parent references | Plain-first evaluator calls | Rich-first evaluator calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Six guards, DAG | 6 | 8 | 7 | 21 | 22 | 20 | 26 |
| Its literal tree expansion | 8 | 8 | 7 | 23 | 22 | 24 | 32 |
| Same questions, close raw leaf directly | 8 | 0 | 7 | 15 | 14 | 30 | 22 |
| Ask \(x_0,x_2,x_4\), close raw leaf directly | 8 | 0 | 7 | 15 | 14 | 16 | 16 |

The last two columns count each local hull or rich entailment as one evaluator call. At the direct leaves for these very same questions, the per-leaf (rich-first, plain-first) costs are (3,4), (3,4), (2,3), (3,4) for each value of \(c\). Choosing either order afresh at each leaf still requires 22 checks, compared with 20 when the guards are reused. If support points actually visited are charged instead, the rows respectively use 160, 192, 340 and 256 with the plain evaluator first, or 168, 200, 84 and 64 with the rich evaluator first. These are exact operation counts on the supplied finite evaluator tables. The timing of table construction, set operations and the sizes in bits of different instructions can depend on the implementation. The direct alternating-input tree offers a cheaper competitor for several of the stated measures.

The complete raw leaves of that direct alternating-input tree cannot be combined by caching a terminal weakening. Let two values of \(y\) differ by \(\delta\ne0\). On their affine line, with all \(w\) and outputs free, \(Q=y_0\cdot w+t(\delta\cdot w)\) is nonaffine. Its rich scalar graph spans the whole line times all \((w,s)\). Consequently the rich full hull projects onto that whole scalar space. The plain graph spans the same scalar space and both plain summaries are free. Its restriction to the rich hull therefore spans the rich hull by the fibre argument above. The rich points still span that hull as well. This gives a nonempty fixed point inside any raw affine guard containing the two complete leaf cells, for arbitrary rich summary masks. For 35 independent two-summary choices up to a change of summary basis and adding the total, the direct nine-bit check found 280 individual cells closing and all 980 pair spans staying live. The successful six-guard proof uses different questions and proves the needed rich implications. [Whole-case control](balanced_guards.py)

## Reusing an affine conclusion while both branches remain live

A second certificate allows assumption discharge. Prove \(G\Rightarrow L\) by an explicit refutation at \(G\land\neg L\). To call it under \(H\), check raw inclusion \(H\subseteq G\) and verify a continuation at exactly \(H\land L\). The rules are sound for every point satisfying both evaluators. Separate one-side source facts may also be cited under implied guards and combined when their XOR gives \(0=1\).

The saved proof `literal_live_lemma` derives \(v=0\Rightarrow x_0=0\) by a three-terminal refutation of \(v=0,x_0=1\). Under those assumptions write \(B=x_2(x_1+x_3),\ C=x_4(x_3+x_5),\ h'=s+u\). On the rich side \(u=x_1, B=0, C=h'\). Once \(u=x_1\) is shared, the plain side gives \(B+C=1+h'\). For \(h'=1\) the rich hull sets both factors of \(C\) to 1, then the plain side forces \(B=1\). Its hull forces both factors of \(B\) to 1, contradicting the rich side. For \(h'=0\) split on \(x_4\). Either \(x_4=0\) already enforces \(C=0\) or the rich hull enforces \(x_3+x_5=0\). The plain side again forces \(B=1\).

The same node is called at \(H_0=(v=0,x_2=0)\) and \(H_1=(v=0,x_2=1)\). Their fully saturated live sizes are 128 and 64. Applying the learned literal removes half of each affine set immediately. Further ordinary saturation leaves 32 and 16 points respectively, so both contexts still need a continuation. Their different cardinalities also preclude identifying them by an affine bijection. This DAG has 11 directly checked terminal nodes, against 14 in its verified tree expansion. A tree which specializes the same goal to each context uses 12. The independent direct eight-leaf proof remains available.

## Other explicit measures and the seven-product check

On the fixed alternating-input tree one can store elementary rich facts for the three summands independently. For each index \(i\) and bit \(b\), \(y_i=b\) makes its corresponding visible output (respectively \(u,v,s+u+v\)) equal \(b w_i\). These are six reusable source checks. Eight separate plain total equations and eight affine cancellations finish the proof. A prefix-local proof already inherits valid facts from ancestors and still checks these rich facts \(2+4+8=14\) times. Combining the first two rich outputs instead yields four checks at \((x_0,x_2)\) plus two at \(x_4\). A direct competitor uses one rich total and one plain total in every leaf.

| One-side affine proof | Source checks | All nodes | Parent references | XOR additions | Support points visited |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prefix-local three summands | 22 | 37 | 46 | 24 | 448 |
| Three summands with shared source nodes | 14 | 29 | 46 | 24 | 448 |
| Two groups with shared source nodes | 14 | 29 | 38 | 16 | 384 |
| Two whole totals per leaf | 16 | 31 | 30 | 8 | 320 |

In the model that uses raw whole alternating-input cells and one-side source equations followed by a cancellation, six is the minimum size of a **rich source-fact library**. This counts a different object from directly terminal guards. In a full \(y\)-cell, a fact selecting a nonempty set \(J\) of the three product outputs has odd-variable slope fixed by \(y|_J\). Each fixed affine fact can therefore serve only cells agreeing on those bits. Keeping just these restrictions gives 26 maximal candidate guards, since \(\sum_{\varnothing\ne J\subseteq[3]}2^{|J|}=26\). Each maximal guard is realized by the sum of its selected outputs and the corresponding affine odd-variable terms. An empty output selection adds no information beyond the bare cell. To cancel the one plain total, the rich selectors available at each cell must span \(111\). Enumeration checks every library of sizes zero through six. Four size-six libraries suffice, none smaller suffice, and at least 16 rich citations are needed among those size-six libraries. [Independent source-fact library census](fact_library.py)

Separately enabling affine transport changes the proof rules. Translation by an original input vector \(\delta\) changes each quadratic output by the affine difference \(f(x+\delta)+f(x)\). The optional certificate explicitly verifies that its maps preserve both entire evaluators and transport the cited guard exactly. It uses one terminal node, three charged transports and three splits, against eight terminals, seven transports and seven splits in its expansion. The six-guard certificate has zero transport steps.

For a nondegenerate quadratic on \(2r\) inputs the same first-effective-plain argument requires scalar codimension at least \(r\), and at most \(3\cdot2^{r-1}\) honest inputs can lie in one directly terminal guard for \(r\ge1\). Indeed codimension at most \(r-1\) leaves rank at least two for a free graph, or rank at least four before testing any further hyperplane in a pinned graph. At codimension \(r\), the largest remaining pinned input space has dimension \(r+1\) and a nonzero polar pair, giving the three-quarters bound. On a seven-product path one may use the same summaries, set both \(x_4,x_6\) as prefixes, and subtract the resulting affine tail contributions to obtain the same three conflicts. The check on all 2,048 visible rows gives 16 applications, 12 distinct guards, 24 honest inputs in each. Hence the seven-product minimum in this guard model is between 11 and 12. [Seven-product replay](seven_guard_stress.py)

## Replay

From the repository root run

```sh
python3 -B proofs/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B/FIVE-PRODUCT-GUARDED-REUSE-20261115-001B-P001_guarded_deductions/check.py
```

The checker reconstructs and verifies every saved proof and each physical tree expansion. It replays the independent guard, source-fact and next-size checks, verifies the matching-charge solutions, and rejects a wrong routed guard, erased assumptions, the opposite discharged literal, a circular dependency, an extra coordinate and a transport in the literal system. The output object has `status` equal to `passed` and is checked against the saved numerical record. [Main checker](check.py) · [Numerical record](checks.json)
