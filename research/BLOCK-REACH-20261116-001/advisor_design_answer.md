**Verdict:** Theorem F is sound with your groups, but three things should change before freezing: "never forgets" is not yet decided, P3 is already false on your own numbers, and the bound sits one below the census everywhere.

**What I checked:** I read the splicing lemma and Theorem 1 in the BRANCH-DEPTH-001A proof, and `exploratory/forget_windows.py`. I ran nothing.

**Soundness of the transfer**
- **Varying relations:** the splicing proof uses only the one window being spliced. It needs the composed window relation W to contain (incoming values of actual states) × (outgoing values of actual states). Each r-window being rectangular gives that, so type- and depth-dependence is harmless.
- **Longer runs:** rectangular ∘ anything is rectangular or empty, so passing at r implies passing at every longer window.
- **Groups and interface:** block(O_(k+j-1))'s knots must sit in group j together with all sibling subtrees, since a block knot may touch several children. Your choice does this. The interface O_(k+j) is owned by group j, which the lemma allows ("prescribed once at its introducing group").
- **Group 0:** "everything outside O_k's proper subtree" is fine; its relation is never used.
- **Up-then-down:** sound. The top member lies in group 1, group 0 may be empty, and the index gap is k+s−b−1 ≥ s. It uses only down-step relations, so the "both path cases" check in (2) adds no new windows. Say so rather than list it as a gate.
- **Finite depth:** the lemma's "infinite state" becomes "feasible state of P_N"; nothing else changes. Windows lie at remaining depth ≥ N−k−s+1, so your stabilised-only run already proves the bound for N ≥ k+s+r0 (check the exact offset). The full check only adds the shallow tail; state the theorem in those two tiers so a shallow failure does not sink it.

**All of Q, or reachable only**
Rectangular on all of Q is sufficient, not necessary. The lemma's "smaller hypothesis" needs only W ⊇ In × Out, the values actual states take at the two cuts. Restricting outputs to F keeps rectangularity and is free. Restricting inputs to those reachable from above depends on k and the path above, so keep all-of-Q as the uniform test. Use the reachable refinement only on the "none" cases.

**Gaps in the exploratory code**
- **`rmax=6`:** "none" and the 42 direct "never forget" mean only "not within 6". Iterate until the frontier set of (type, relation) repeats, which is finite, before writing "never".
- **Empty relations:** `rectangular(∅)` returns True. An empty window on an alive description means an unrealisable type path or a bug; count and log these, don't pass them silently.
- **`tree.step`:** confirm whether it restricts the path child's output to F, and record which.

**Is the bound 1 + ceil(s/r) or better**
The lemma gives exactly that; both endpoint groups are already counted. It is one below the census in both families: s+1 against [3,4,5,6], and 2,2,3,3 against [3,3,4,4]. Report that gap explicitly. The cheap fix is max(3, ·) wherever "no tie, no frozen" is already proved (DIRECT-REACH has it for the 43 half-rate). A real +1 needs a marked-window test (window still rectangular with one member pinned), which belongs with the upper-bound study.

**Predictions**
- **P1:** a real test, but one-sided. The full check can only raise or lose r. Freeze it as "r unchanged".
- **P2:** nearly settled. All 399 rulers already have r ≤ 3 at stabilised depth, so it tests only the shallow tail. Merge it into P1.
- **P3:** already false. The four without r include profiles [3,4,4,4] and [3,4,5,5], which rise. Replace it with something falsifiable: after closure and the reachable refinement, each of the four either gets an r or is proved bounded. [3,4,4,4] looks bounded at 4; [3,4,5,5] is the interesting one.
- **Census gate:** it has teeth for the 283 "other" with r = 1, which need a profile ≥ [2,3,4,5]. Treat undecided and capped cells as missing, not as passes.

**Cheap upper bounds now**
The projection onto a region depends on what lies below only through F at its lower boundary. So a census bond at depth 9 whose members and witnesses all sit at level ≤ 9 − r0 has the same projection at every N ≥ 9, and remains a bond meeting both levels. That gives L_N(k, s) ≤ census value for all N in those (k, s) cells, at the cost of a filter on the records you already have. Uniformity in k is not free, because the context above changes; that part does need the marked tables.
