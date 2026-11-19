# Advisor answer for RING-IDENT-20261119-001

**Verdict: do not freeze the statement as written.** Steps 1–4 are sound, but step 5 fails inside the scope: the claim "d = 0 only for C′ = X̃ finite, where the junction takes every loose bit" is false when K is a tree that is not a star. Everything below is by hand from your text; nothing was run.

## The failure (step 5, the d = 0 case)

"Start connected" makes K connected, not X. Blocks are neighbourhoods, so two knots are joined in X only by even walks in K. If K is bipartite, X has two components, one per side.

If K is a tree, both components of I(X) are finite trees, and they are exhausted in different rounds. The junction of the smaller side's whole component has d = 0 and p ≥ 2. It does not take every loose bit of the presentation, because the other side still has some. As you state the rule, it gets max(0, 3 − p, 1) = 1 fresh bit, while the theorem says |∂C| = 0.

**In-scope counterexample (7 knots, no surplus).** K has w adjacent to a and b; a has leaves a1, a2; b has leaves b1, b2.

- **S1:** w has 2 + 4, a has 3 + 1, a1 has 1 + 2.
- **S2:** vacuous.
- **S3 and S4:** K is a tree.
- **X:** one side is the single block N(w) = {a, b}; the other is {w, a1, a2} ∪ {w, b1, b2}.
- **Round 1:** junction ab has p = 2 and d = 0, and is not implied because the other side has loose bits. So fresh = 1 against |∂{a, b}| = 0.
- **After that:** ab's only neighbours are a and b, and no other live junction shares them. Its loose bit becomes an offshoot every round, which is an endless chain.

The same happens later for the spider (centre u, three arms of degree 3), at the junction abc in round 2. If the two sides have equal size, neither final junction alone "takes every loose bit" either, unless the code's implied test is per component. The star K_{1,3} is fine, because its other side is one knot with no loose bits.

**Fix.** Either of these works:

- **Add (S5): K contains a cycle.** A cycle in K gives a reduced closed walk in each component of I(X), so every component of X̃ is infinite. Then ∂C ≠ ∅ for every cluster, d ≥ 1 always, and the implied clause is never invoked. This is the cleaner option.
- **Keep trees and change the count.** State loose bits as |∂C| + 1 at a whole finite component that is not implied, and describe the chain.

Either way, say "universal cover of each component of I(X)".

## Question 1: step by step

- **Step 1 (girth): sound.** A 4-cycle means two knots with two common neighbours, which S4 excludes. A 6-cycle gives a, b, c pairwise candidates through distinct w1, w2, w3. Any neighbour common to all three would equal each w_i by S4, so there is none, and the triple is valid, against S3. Write that S4 supplies "no common neighbour"; the plan reads as if S3 does. This also holds when a = w3. It needs a, b, c live, which holds if d_k is defined with all knots live; say so, since the definition of d_k is circular otherwise. Translation length is at least the girth, so k ≥ 4.
- **Step 2 (union lemma): sound, wording wrong.** "B's point at α" need not exist: α can be a block node, or B's span can miss the axis so that α is not in B. The count does not need it.
  - If α is a vertex-node, the nodes α, α + 2, …, α + 2k − 2 are k vertex-nodes of span(D), so they lie in D. None is in fB, because fB ∩ axis ⊆ [α + 2k, …], or is empty when the span misses the axis.
  - If α is a block node, the k vertex-nodes α + 1, …, α + 2k − 1 do the same.
  - So |D| ≥ |fB| + k in every case.
- **Step 3 (L1, L2): sound.** L2 needs m ≥ 2 so that D is connected, and you have that.
- **Step 4: sound, including the count in (iii).** A1 ∪ A_i ∪ A_j has t + 3 points and gA_j adds at most one, so t + 4 < (t + 1) + 4. "All c_j equal" follows because any b_l differs from one of two unequal b_i, b_j. Two details should be written out:
  - **Connectivity of C′ − {v, v′}.** It holds because a non-cut vertex of a block graph lies in exactly one clique, so v′ stays non-cut after removing v unless C′ = {v, v′}.
  - **A knot in C′ − {v, v′}.** For t = 1 the remainder is a single point, and it is a knot because a surplus vertex's knot is a cut vertex of C′, so it is never in R*.
- **Step 5: sound except the d = 0 case above.** The round-1 base is fine.

Where k ≥ 4 is actually needed: maximality in 4(i) and 4(iii). L1 needs k ≥ 2; L2 and "no common parent" need k ≥ 3.

## Question 2: what is used beyond the scope

- **Connectivity of X**, as above. It is not given.
- **The implied test.** It is the only place the theorem depends on a global property of the presentation. With (S5) it disappears.
- **Demand "with all new junctions live".** This is consistent: junctions with ∂ = ∅ lie in no group, and groups depend only on parent structure, so there is no circularity.
- **The code's pruning.** I cannot check it from here. The proof needs only that the enumeration returns all maximal valid sets and the uncovered pairs.

## Question 3: the wider class

- **First-round groups of three: step 1.** An incidence 6-cycle gives k = 3. L1, L2 and "no common parent" survive, but maximality in 4(i) and 4(iii) do not, since their D has |U| + 3 points. The base case already fails, because a three-parent junction is not a 2-cluster. Adding the triple as its own block creates incidence 4-cycles with the N(w) blocks, so the tree-of-blocks cover is the wrong object there. That class needs a different complex, not a weaker lemma.
- **The floor (dropping S1/S2): only step 5.** Steps 1–4 stand, but fresh > d leaves loose bits whose offshoots are candidates with the junction's other children. This acts like a pendant vertex attached to a cluster, not to a knot, so it is not a deck-invariant part of X. The tree-K failure above is this same mechanism, already inside your scope.

## Question 4: is it known

I know of no result that states this growth-to-animals equivalence. The ingredients are standard:

- **Clusters on tree-like covers.** Site animals on Bethe lattices and Husimi trees (cacti), with perimeter read from the cluster: Fisher and Essam 1961; Harary and Uhlenbeck 1953 for Husimi trees. This is the nearest.
- **The parent rule.** "Remove a non-cut vertex" is the reverse-search enumeration of connected induced subgraphs, Avis and Fukuda 1996.
- **X itself.** It is the open-neighbourhood hypergraph of K. S4 makes it linear, and S3 with S4 removes Berge cycles of length 2 and 3. Its splitting in two for bipartite K is the standard halved-graph fact.
- **The union lemma.** It is the usual free-action, translation-length argument on a tree.

What you would be adding is the exactness for all t, not only below the girth, by counting deck orbits. Treat my "no known statement" as a recollection, not a literature search.