# Referee report RING-IDENT-001-R1 (proof read line by line; own scope test, girth, growth, cover and cluster enumeration)

**Verdict: confirmed. The theorem is proved. No Block; three presentation points. Proposition 5 (the Narrowing of RING-PAIR) is
confirmed by the referee's own regrowth.**
- **The proof is correct** (Section 1). Lemma 0, Lemma 1 (girth), Lemma 2 (the union lemma), Lemma 3, Lemma 4 with its size
  counts, and the induction all hold as written. Three steps are presented thinly: Section 1's points (a) to (c). None is a gap in
  the mathematics.
- **(S3) and (S4) give girth at least 8.**
  - **Length 4:** two blocks sharing two knots give those knots two common neighbours.
  - **Length 6:** three pairwise candidates with no common neighbour are a round-1 group of three. They are live, since each has
    demand at least 2.
  - **Checked** on every one of the 332 starts on 3 to 7 knots, and the 8-knot sample, that satisfy (S3) and (S4), in scope or not:
    none has girth below 8.
  - **The bound is reached.** Girth exactly 8 occurs at 8 knots (18 sampled starts, such as an 8-cycle). The theorem holds there,
    as it must, since Lemma 2 needs only k ≥ 4.
- **The identification checks out with an independent enumeration, more strictly than the study's check.**
  - **The method.** The referee's own cover is built lazily from non-backtracking walks, and a frontier enumeration meets each
    connected set containing the root once. Each rooted cluster is weighted 1/|C|.
  - **The key compared.** For every junction: parents, fresh distinctions, and the sorted keys of its parents. On the model side:
    |R*(C)|, |∂C| and the keys of C − v. The study compared (parents, fresh) only.
  - **3 to 7 knots.** The referee's own scope test finds the study's 88 in-scope starts. All 45 with a cycle agree at every round to
    6. Of the 43 trees, 21 differ, as the study found.
  - **One size past (8 knots, a sample of graphs with girth at least 5 and a cycle, with and without one surplus distinction):**
    81 of 81 in-scope starts agree.
- **The two stars joined at their centres, regrown.** In scope by (S1) to (S4), with sizes 5, 3, 3, 5, 3, 3 and blocks {1, 2, 3}
  and {0, 4, 5}. The referee's engine grows 6, 6, 2, 2, 4, 6, 8, 10, 12, 14, 16. The cluster orbits per size are 6, 6, 2, 0, 0, …
  So (S5) is needed, and RING-PAIR's stated scope is too wide.

## 1. The proof, step by step

- **Lemma 0.**
  - (1) holds by construction.
  - (2) **Correct.** A cycle of K has at least five knots, since three or four are excluded by (S3) and (S4). The walk c₀, N(c₁),
    c₂, … is closed and cyclically reduced: c_i ≠ c_{i+2}, the blocks are indexed by their centre so N(c_{i+1}) ≠ N(c_{i+3}) as
    nodes, and the closing steps differ too. So every component of I(X), each of which holds some c_i, has an infinite universal
    cover.
  - (3) **Correct.** Two block-nodes of a tree share at most one point-node, and a triangle of adjacencies through three distinct
    blocks would be a cycle in T. So the adjacency graph is a block graph, and induced subgraphs of block graphs are block graphs.
    The three facts are standard. The third needs exactly the case Q = {v, v′}, which the proof rules out.
  - (4) **Correct.** That includes the three-point case, where C − {v, v′} cannot be a lone surplus point: v and v′ would both
    have to meet it, and it meets only its knot.
  - (5) **Correct.** The joined walk has point-nodes exactly B and contains the span. Subtrees intersect in subtrees, whose
    point-nodes are connected through adjacency.
- **Lemma 1** is correct (above).
- **Lemma 2 (the union lemma) is correct.**
  - **The axis.** f acts freely and keeps points and blocks apart, so it is hyperbolic, with an even translation length 2k.
  - **k ≥ 4.** The axis segment from x to fx projects to a closed walk that is cyclically reduced, because the covering map is a
    local isomorphism and fx continues as x does. It contains a cycle, so 2k ≥ 8.
  - **The projection.** π(fx) = π(x) + 2k. span(D) contains the axis path from α to α + 2k. Of the nodes α to α + 2k − 1, k are
    point-nodes, so they are points of D by Lemma 0.5. None lies in span(fB), which projects to [α + 2k, ∞).
  - **The bound:** |D| ≥ |B| + k ≥ |B| + 4.
- **Lemma 3 is correct.**
  - **(L1) and (L3)** put B ∪ gB inside a cluster of |B| + 1 points.
  - **(L2)** puts gB and g′B inside A ∪ gB ∪ g′B, which has at most m + 2 points.
- **Lemma 4 is correct, with its size counts.**
  - **(F1).** A round-t junction meets only its parents, and round-t junctions share nothing.
  - **(F2).** For the "only if", |A ∩ h⁻¹B| ≥ t, and it is exactly t since u ≠ w. For the "if", W = A ∩ gB is a cluster holding a
    knot, the t = 1 surplus case giving u = w.
  - **(i).** In "no common parent", all lifts g_vW lie in C′ of |W| + 2 points, so one g serves, and gW ⊆ C′ − R*(C′) has at most
    t − 1 points. In "maximal", D = C′ ∪ h_vU ∪ h_{v′}U has at most t + 4 < |U| + 4 = t + 5 points.
  - **(ii).** Uniqueness through (L2).
  - **(iii) step 3, the count the hand-off asks about.**
    - A₁ ∪ A_i ∪ A_j = A₁ ∪ {c_i, c_j} has t + 3 points.
    - gA_j meets A_i in t points, so it adds at most one. Hence |D| ≤ t + 4 < |A_j| + 4 = t + 5.
    - g ≠ 1, because |A_i ∩ A_j| = t − 1.
    - **Correct.**
  - **(iii) steps 4 and 5.** Step 4 uses step 2's pair with b_i ≠ b_j. In step 5, C′ = A₁ ∪ {c} is connected, since c meets A_j
    − c ⊆ A₁, and the b_j are distinct because the members are.
  - **The conclusion** follows from (i) to (iii).
- **The induction is correct.**
  - **Round 0:** |∂{k̃}| = d_k + s_k, one lift per partner by (S4); every knot is live by Lemma 0.2.
  - **Round 1:** the pairs and the offshoots are exactly the two-point clusters, and (a) holds.
  - **Step 3:** j lies in exactly |∂C| groups, by (L3) and (L1), and holds |∂C| loose distinctions, so there is no offshoot and no
    stall.
  - **Step 4:** p ≥ 2, or an offshoot with d = d_k + s_k − 1 ≥ 2 by (S2), and d = |∂C′| ≥ 1, so the fresh count is d.

**Presentation points (not gaps):**
- **(a) The count rule for implied junctions.** The Setting says "if it is implied, it gets d instead". The program's fewest rule
  gives 0 when implied with demand 0, and otherwise max(d, 3 − p, 1). Under (S5) every case has d ≥ 1 and either p ≥ 2 or d ≥ 2, so
  both read d. The Setting should state the program's rule.
- **(b) Round 1's fresh counts and liveness.** For the round-1 pairs, p = 2 and d = |∂C| by Lemma 4 at t = 1. This is argued only
  inside step t → t + 1, part 4 (its offshoot bullet), which is stated for t ≥ 1. A sentence in the round-1 paragraph would close
  the induction's base cleanly.
- **(c) The t = 1 surplus case in Lemma 4(iii) step 2.** A₁ − b a lone surplus point would force A_j = A₁. This is the same
  argument as in (F2), and could be said there.

## 2. The machine check (`machine_check.py`, read)

- **The cover ball.** It unrolls the incidence graph without stepping back through the block just used, which gives the universal
  cover.
- **The enumeration.** The cluster enumeration meets each connected set containing the root once, using a seen-set.
- **The weighting.** Each rooted cluster is weighted 1/size. This is right because Γ acts freely and transitively on the lifts of
  each point, and no finite cluster has a nontrivial stabiliser, since every non-identity deck transformation is hyperbolic. So an
  orbit of m-point clusters is met exactly m times in all.
- **The cut-off.** The depth limit (max depth ≤ T + 1, radius T + 3) keeps the boundary exact.
- **The growth side** uses JOIN-GROWTH's engine with GF(2) elimination off. Its structural test is valid on these connected
  starts, and the referee's engine, with elimination on, agrees.

## 3. The referee's run (`job_ring.py` under `scripts/longrun.py`, 32 cases, all ok)

| Population | In scope (S1 to S4) | With a cycle: keys agree at every round to 6 | Trees: agree / differ |
| --- | ---: | ---: | --- |
| Knot graphs on 3 to 7 knots, no surplus or one surplus at one knot | 88 | **45 of 45** | 22 / 21 |
| One size past: sampled graphs on 8 knots (girth ≥ 5, a cycle) | 81 | **81 of 81** | — |

| Girth of I(X), every start with (S3) and (S4), in scope or not | Count |
| --- | ---: |
| No cycle | 162 |
| 8 | 18 (all at 8 knots) |
| 10 | 135 |
| 14 | 17 |
| Below 8 | **0** |

**Two stars joined at their centres:**
- **Growth:** 6, 6, 2, 2, 4, 6, 8, 10, 12, 14, 16.
- **Cluster orbits of sizes 1 to 7:** 6, 6, 2, 0, 0, 0, 0.

## Corrections for the owner (listed, not folded in)

None to the result.
- **Presentation (not blocks).** Points (a) to (c) in Section 1.
- **RING-PAIR's Narrowing** (its scope needs (S5)) is confirmed.

## How the work was split

- **The referee:**
  - read `ring_ident.md` and `proof.md` in full, and `machine_check.py` and its output;
  - wrote `job_ring.py`: its own round-1 groups and sizes, scope test, girth by breadth-first search, growth (FIRST-KNOT-R1 engine),
    lazy cover, frontier cluster enumeration, and keys with parents.
- **Read as data:** the networkx graph atlas.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 217 MB).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
