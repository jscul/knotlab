<!-- modelUsage: claude-fable-5-2 -->

**Verdict:** both proofs are correct once three lemmas are made explicit, the theorem is not law-independent, and P3–P4 hold (P4's alternating clause is in fact an equality). P5 cannot be checked because τ is not defined in the document. I assumed the measure is uniform on allowed states with ±1 spins, and that a "law" is any 3-place relation with K1 and K2 (K3 is not defined here).

## (1) Upper bound: correct
- **Missing lemma:** the base projected onto the path variables equals the chain's own solution set. Subtrees hang off single variables, and by K2 any single value extends through a knot, hence through a subtree.
- **Forgetting p_j:** K_j's projection onto (v_{j−1}, v_j) is full, so the solution set is exactly sol(left) × sol(right). Each side has a quantified end variable and is full by greedy extension (K2 on the pair (v, p)). This holds for every law.
- **Forgetting x or y:** the "free third distinction" sentence does not cover this case. It needs the greedy extension from the other end, using K2 on (p_j, v_j). It is true and should be written down.
- **Constrained:** the forcing argument is correct. For betweenness, argue directly: any law forbidding an antipodal pair {s, ¬s} forces the out-value for a suitable pendant value. The "switch to not-all-equal" is always consistent on a tree but can be frustrated on a ring.

## (2) Lower bound: correct, product exact
- Delete K_j to get components A ∋ x, B ∋ y, C ∋ p_j. If S misses all of C, projecting out C gives exactly sol(A) × sol(B). This needs K2 for K_j plus the lemma that p_j takes both values in sol(C).
- So S's projection is the product of its two sides, and a non-full product has a non-full factor, which is a proper subset.
- "Third branch" must mean the whole subtree C, not just p_j. The count |S| ≥ k + 2 still follows because the branches are disjoint.
- This half uses only K2, so it holds for any law.

## (3) Not for every law
The upper bound fails when the composed chain is free.

- **Counterexample:** the law "not all ones" (forbid 111 only), which satisfies K1 and K2. For (x, v, p₁), (v, y, p₂), setting v = 0 satisfies everything, so {x, y, p₁, p₂} is free. The only bonds are the two knots, so no bond contains x and y.
- **General statement:** bond distance ≥ steps + 1 always (possibly infinite), with equality iff the path chain's projection onto S is non-full.
- **Classification:** K2 laws are the non-empty forbidden sets with no two states at Hamming distance 1. Up to symmetry there are five: one state (a clause), two states at distance 2, an antipodal pair (not-all-equal and betweenness), three states, and four (parity).
- The theorem is unconditional only for the antipodal pair and parity. For clauses, the chain is constrained iff the shared variable occurs with opposite polarity (resolution).

## (4) Predictions
**P3 holds.**
- z = x⊕y is determined and E[xy] = (−1/3)^k.
- {x, y, z} is a bond, so bond distance − 1 = 1.
- κ_{xyz} = 1 − 9^{−k}, so δ ≤ 1 − log₃(1 − 9^{−k}): 1.0113 at k = 2 and 1.0012 at k = 3. The 1.1 threshold would fail only at k = 1, by 0.007.
- δ_K = k trivially: κ_{xy} ≠ 0 disqualifies every larger S.

**P4 holds, and is provable.** If S misses a pendant p_j, the ring opens exactly into a chain, so the bonds are:
- the arc sets {v_a, v_b, pendants between}, and
- those containing all pendants P: P itself for pure parity; P ∪ {v_a} for pure not-all-equal with n odd, or for any mix with at least one knot of each law.

Consequences:
- **Parity:** κ_S ∈ {0, ±1}, non-zero only on circuits, since partitions into dual words are partitions of runs and the Möbius sum vanishes. So δ = bond distance − 1.
- **Parity vs steps:** bond distance − 1 is below steps for pendant pairs at n = 3 (1 vs 2) and for opposite pendants at n = 4 (2 vs 3).
- **Not-all-equal:** bond distance − 1 = steps on every pair.
- **Alternating:** P ∪ {v_a} has size n + 1 and never undercuts an arc, so the registered "≤" is actually "=".

**P5 is not checkable as written.** If τ = −log₃|pair correlation|, the ring-variable correlation is (−1)^d (3^{n−d} + (−1)^n 3^d)/(3^n + (−1)^n), which is never 3^{−d}. The values are τ = 1.33 (n = 3, d = 1), 1.38 (n = 4, d = 2), 2.37 (n = 5, d = 2) and 2.37 (n = 6, d = 3). A tolerance needs to be registered.

## (5) Literature
From memory, since I cannot search here:
- **Standard term:** a set with full projection is *shattered* (VC theory). Bonds are the minimal non-shattered sets, i.e. the minimal non-faces of the shattering complex. See Sauer–Shelah, Pajor, and the shattering-extremal work of Bollobás–Radcliffe, Anstee–Rónyai–Sali and Mészáros–Rónyai.
- **"Minimal non-free sets":** I do not recognise this as an established phrase. "Circuits" is justified only in the linear case, where bonds are the minimal supports of dual codewords.
- **Product lemma:** this is join-tree or acyclic-scheme decomposition (Beeri–Fagin–Maier–Yannakakis 1983) and Freuder's 1982 tree-CSP consistency result.
- **Clause law:** this is resolution and prime implicates.
- **The tree theorem itself:** I know of no published statement. It is probably folklore-level.

## (6) Making it more valuable
- **Prove the full characterisation.** On trees, bonds should be exactly the leaf sets of subtrees in which every knot keeps all three branches (I sketched this, not fully proved it). With the ring list above, P1, P2 and P4 become code checks, so say so.
- **Add a negative control and the general theorem.** Use the clause law, and state the result as "lower bound always; equality iff the chain is constrained", across all five law classes.
- **Scope D1.** If δ minimises over all S, it breaks on some linear codes. For ten equal variables, κ₁₀ = 7936 gives 8 − log₃7936 ≈ −0.17, below bond distance − 1 = 0.
- **Test the triangle inequality.** It holds for linear bases by circuit elimination; it is open for nonlinear ones.
- **Define terms in the document.** τ, steps on rings, the measure and K3 are all undefined.
- **Try harder cases.** Frustrated betweenness rings and bases with two cycles would test more than the current set.
