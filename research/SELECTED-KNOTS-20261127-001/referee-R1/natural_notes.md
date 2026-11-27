# Three tests of the choice of places and knots

## A meeting cycle on the frozen places

The study's three rings of four starting knots have six families. Write $p_i,q_i$ for the two family parities of ring $i$ and $R_i$ for their sum. The tree has nine nonconstant places. To give them disjoint carriers, use the starting loose distinctions for each $R_i$ and the first-round fresh distinctions of its two families for $p_i,q_i$. This rule applies to every ring equally. More generally, one can take each cluster's family distinctions from the generation one less than its depth below the root. Incomparable clusters use disjoint families, and nested clusters use different generations. That construction presupposes the required funded rounds.

At round five, the nine carriers jointly take 32 values. Their 11 inclusion-minimal parity relations comprise four triples, three quadruples, three quintuples and one sextuple. Each relation passes K1–K3 with every place in turn as the contact. The four triples are precisely the frozen node-with-children selection. Taking **all** inclusion-minimal relations of the same nine places is also invariant under renaming. It includes exactly three four-place knots,

$$
\{p_1,q_1,R_2,R_3\},\qquad
\{R_1,p_2,q_2,R_3\},\qquad
\{R_1,R_2,p_3,q_3\}.
$$

Each pair shares a different ring carrier, and no carrier lies in all three. Each of the six first-round birth laws in ring $i$, when removed alone, frees all 16 readings of just that ring's quadruple. Every family carrier has least change 13 and every ring carrier has least change 15. None of the 168 first-layer knots reads any nonconstant class fact at scale 12. The cycle therefore occurs on the study's own whole-held facts. Its three four-place equations are distinct even when carriers of the same function are identified. Algebraically each follows by adding the root equation to a different ring equation, so the four triples still generate the full law space.

There are also two distinct choices of independent equations. The frozen choice uses the four triples, which here are precisely the shortest-support relations. The alternative keeps the root equation and eliminates each ring's shared place between the root equation and that ring's equation. The resulting three quadruples and the root are independent. Adding the root recovers each original ring equation. This second basis therefore has exactly the same allowed words and contains the meeting cycle. Both selections respect every renaming. [Check of both independent bases](record_checks.json)

## An alternative using each family's generations

Use every disjoint group of distinctions fresh to each family in each generation, starting with its loose distinctions. On the recorded three rings of five knots each ring is one family. At round four the 15 places have 30 pair equalities and 125 minimal triples, one choice of generation for each of three families. In particular, the three triples using one first-round family carrier and two starting carriers meet pairwise in three different starting carriers. Each triple passes K1–K3. Removing any of that family's five first-round birth laws frees its triple alone among these three. Each of the 15 costs is 13, and none of the 81 first-layer knots keeps a nonconstant local fact at scale 12.

All generations of one family carry the same function. Identifying those copies leaves one parity triple. Keeping the separate physical carriers leaves four joint words, whose three nonzero changes each have weight ten. They span the changes and the third-layer class dimension is zero. This example distinguishes separately carried facts from functions on family values.

## What the sum of local reads measures

Let the places be every nonroot cluster in the frozen hierarchy, including the leaves. An allowed word records the parity of the leaves below each cluster for an even set of changed leaves. The least weight is two. A pair of leaves with the same parent changes just their two places, and at least one such pair exists at a deepest internal node. Conversely, a word of weight two changes exactly two leaves. Distinct parents would force a change at a proper internal cluster holding just one of them. Thus the least words are precisely the pairs of leaves with a common parent.

Every parity of place values is a parity of leaves. To be constant on the least changes its coefficients must be equal on each group of leaves with a common parent. Every such class fact is therefore a sum of the parities of those groups. Each group parity is read from the leaf places of its own parent. Their total vanishes, and this is their only relation. With $b$ nonempty sibling groups, counting singletons, the third-layer class dimension is $b-1$. The quotient by the **span** of local class facts always has dimension zero under these definitions. This argument uses no family distances, growth measurements or particular scale.

## A fact that requires two of the selected knots

A built stress start has six five-knot rings $a,b,c,d,e,f$. Each ring knot holds two loose distinctions. Join the pairs $ab,de,bc,cf,fd$ by routes of respectively 3, 3, 4, 5, 5 holder steps. Each joining uses two separately attached routes, one at each of two neighboring ring knots, and each step uses a pair of shared distinctions. This gives 60 starting knots and one family per ring. Single linkage first joins $a,b$ and $d,e$, then joins $c$ to $a,b$, then joins the three remaining groups. At round five all nine disjoint tree-place parities cost 15 to 17 to change, and none of the 210 underlying knots holds a nonconstant local scale-12 fact.

The only least second-layer changes are the pairs $ab$ and $de$. There are seven nonconstant class parities. Five have a single reader among the four frozen knots. The other two are $c+d+e$ and $a+b+d+e$. The certificate gives, for each, an allowed word agreeing with zero on each proposed reader and taking the opposite fact value. The individual reads span all three independent bits. Adding all inclusion-minimal relations makes both missing single reads available. In particular, one of those relations binds all six leaves, whose values determine every cluster fact.

The single-reader counterexample concerns the literal frozen claim and the choice of which knots count as parts. Establishing a fact outside the full span of local reads, or another knot binding such facts, would require a different result. All three examples have a supplied start and an explicit reading of which changes count as small.

## Reproduction

Run from the repository root. The pilot uses the same starts, growth, carrier rules, exact cost method, canonical checks and reader tests on shorter funded prefixes. The full run stops at the rounds named above. It uses one process and caps its address space at two GiB. The code imports the canonical knot checker and rebuilds ordinary growth on these starts, the parity images and the minimum changes.

```sh
r=research/SELECTED-KNOTS-20261127-001/referee-R1
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -B "$r/natural_places.py" --pilot
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python -B "$r/natural_places.py"
```
