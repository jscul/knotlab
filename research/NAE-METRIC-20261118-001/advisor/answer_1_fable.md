<!-- modelUsage: claude-fable-5-2 -->

**Verdict:** Lemmas 1 and 2 are correct as written, the gluing step is right, and the ring lower bound for thirds has a short proof (below). The one thing to fix before freezing is the definition of "block".

## 1. Lemmas 1, 2 and the block theorem

**Lemma 1 holds.** I checked each step:
- **Case y ∈ T:** T_R ∪ {y} is a proper subset because x ≠ w puts at least one of them in T_L. Worth saying explicitly.
- **Case y ∉ T:** T_L and T_R are both free proper subsets, so Y_L(u) and Y_R(r) are nonempty, and a missing pattern gives opposite singletons.
- **The complement step:** LL is itself complement-closed, being a projection of B by F2, so the missing patterns of B' come in complement pairs. Your argument that x ∈ B' then goes through.

**Lemma 2 holds, both directions.** The proof actually gives a stronger statement you should record:

> **Bond structure at a separating y.** The bonds of B are exactly the bonds of LL, the bonds of RR, and the sets (B_L ∪ B_R) − y for bonds B_L of LL and B_R of RR that both hold y.

Proof: your "T is constrained" argument never uses leastness, so (B_L ∪ B_R) − y is constrained. It sits inside the crossing bond T, and bonds are minimal constrained sets, so the two are equal. Lemmas 1 and 2 are both corollaries.

**What is really needed instead of complement-closure.** Two properties of y, on each side:
- **(a)** {y} is free on each side.
- **(b)** Every bond through y on that side misses patterns with both y-values.

Complement-closure gives both. Parity bases satisfy (b) for every bond of size ≥ 2, since the missing patterns form a coset. They can fail (a) when one side fixes y; then the projection onto L ∪ {y} is not LL and Lemma 1 as stated is false. So state the theorem for "balanced" separating variables.

**Gap in the block theorem: the definition.** Biconnected components of the incidence graph can cut at a knot vertex, and the lemmas say nothing about that.
- For arity 3 this only produces bridges from a knot to a variable, which is harmless if a block means a set of knots together with all their variables.
- For arity ≥ 4 a knot can sit in two cycles that share only that knot, and the theorem would be wrong as stated.

Define blocks as the biconnected components of the primal graph (variables adjacent when they share a knot). Its cut vertices are exactly the separating variables, and each knot lies in one block.

## 2. Gluing

Correct. Set d = b − 1 ≥ 0 for distinct points and d(u,u) = 0 as a convention for the tree-sum only. The target is d(x,z) ≤ d(x,y) + d(y,z) + 1.

- **Median is a cut variable c** (possibly one of x, y, z): the right side minus the left side is 2d(c,y) + 1 > 0. This always holds, with slack, and needs no block hypothesis.
- **Median is a block M** with gates x', y', z': the inequality reduces to d(x',z') ≤ d(x',y') + d(y',z') + 1 + 2d(y,y').
  - If the gates are distinct, this is the triangle inequality in M.
  - If two gates coincide, it follows from d ≥ 0.

The converse (B metric implies each block metric) is Lemma 1. So the "iff" stands, with infinite values allowed. Corollary to test: every violating triple has three distinct gates in one block.

## 3. Ring lower bound, all pairs

This uses three facts.

- **(i) Forgetting a private third removes its knot.** Any values of v_{j−1}, v_j extend to p_j. So a bond T missing p_j is a bond of the chain K_{j+1}, …, K_{j−1}.
- **(ii) Chain bonds are exactly the runs.** By the bond-structure statement and induction on cut variables, the bonds of a chain are the sets {v_{a−1}, p_a, …, p_b, v_b}. A single NAE-class knot's only bond is itself, and a bond through a cut variable must end at it.
- **(iii) The set P of all thirds is free.** Each knot is "tight" for one relation between its two ring variables (p_i forced) and "loose" for the other (p_i free). Choose the v's around the ring so that knots 1 to m−1 are loose. If knot m closes tight, its forced value flips under global complement of the v's, so either value of p_m is reachable. This works for any twisting.

Now let T be a bond holding x and z.

- **T misses some p_j.** By (i) and (ii), T is a run containing x and z. It therefore contains every knot on one route between them, so |T| ≥ steps + 2. This covers v–v, p–v and p–p pairs and replaces your product argument.
- **T contains all of P.** By (iii), T ≠ P, so |T| ≥ m + 1, and ≥ m + 2 for v–v pairs. The largest step counts are ⌈m/2⌉ for p–v pairs and ⌊m/2⌋ + 1 for p–p pairs. So m + 1 ≥ steps + 2 for m ≥ 3.

Hence b ≥ steps + 1 for every pair. Bonds of the second kind do exist: for m = 3 untwisted, P ∪ {v_k} is a bond of size 4.

## 4. A block condition to conjecture

I am unsure here; these are tests, not claims.

- **First, classify the 8-variable, 5-knot linear failure.** Record its variable-degree sequence and whether the failure is infinite (no common bond) or finite. The counts fit a "graph-like" block exactly (K4 with one edge subdivided: 7 shared variables plus 1 private), but also fit blocks with a variable in three knots. Which it is decides the next conjecture.
- **H1 (graph-like).** A linear block with every variable in at most two knots is a metric block. Knots are then vertices of a subcubic graph, and the edge boundary of a tree-like knot set is a bond. If the 8/5 failure is graph-like, H1 is dead and the condition must involve cycle structure.
- **H2 (two-variable cuts).** This is the next decomposition level after Lemma 2. If {y1, y2} separates the block and is not a double meet, conjecture that d(x,z) is the minimum over the two routes of the side sums, as in rings. It would give: metric iff every 3-connected piece is metric and no 2-cut is a double meet. Test it on rings with one knot replaced by a small two-terminal block.
- **H3 (failure type).** Every double-meet failure is infinite-type on a pair of "twin" variables; every linear failure is finite-type.

## 5. Literature

- **Parity bases:** this is the parallel connection of matroids (Brylawski 1971; Oxley, *Matroid Theory*, ch. 7). Its circuits are those of M1, those of M2, and (C1 ∪ C2) − y. Deleting y gives the 2-sum. Your bond-structure statement is the same thing for complement-closed relations.
- **F1/F2:** this is the join of consistent relations over an acyclic schema (Beeri–Fagin–Maier–Yannakakis 1983).
- **Bonds:** these are minimal non-shattered sets. The nearest work I know is on shattering-extremal systems and standard monomials (Anstee–Rónyai–Sali; Mészáros–Rónyai).
- **The non-matroidal additivity statement:** I do not know of it in print, but I cannot rule it out. Cite the parallel connection as the precedent.

## 6. Predictions to add or tighten

- **Bond count at a separating y:** #bonds(B) = #bonds(LL) + #bonds(RR) + (bonds through y in LL) × (bonds through y in RR). This is an exact identity and a good code check.
- **Rings:** every bond missing a third is a run, giving exactly m(m−1) of them. All other bonds contain every third and have size ≥ m + 1. The largest b is ⌊m/2⌋ + 2, between antipodal thirds.
- **Random 9-variable bases:** no violating triple spans two blocks.
- **Split bases:** "b ≤ 2 everywhere" makes b a metric trivially, since any function with values in [k, 2k] on distinct pairs satisfies the triangle inequality. Report it as a diameter result, not as evidence for the metric question.
