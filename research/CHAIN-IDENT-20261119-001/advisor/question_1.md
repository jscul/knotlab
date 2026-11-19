# Question for the advisor (CHAIN-IDENT-20261119-001, before freezing the statement)

You have no tools. Answer only from this text; check the argument and say exactly where it fails, if it does.

**Background.** RING-IDENT proved (you checked it): for the cheapest parity growth (complete rounds; candidates = live junctions with
a common neighbour; groups = maximal valid sets plus uncovered candidate pairs; offshoots from leftover loose bits; fresh =
max(d, 3 − p, 1), or d if implied), under (S1) sh_k + d_k ≥ 3, (S2) surplus only where d_k ≥ 2, (S3) no round-1 group of three,
(S4) no two knots with two common neighbours, and (S5) a cycle in K: round t's junctions are the deck orbits of clusters of t + 1
points of the universal cover of the candidate complex X (blocks N(w); a pendant point per surplus), with parents = R*(C) (points
whose removal leaves a cluster holding a knot) and loose bits = |∂C|. The core is the union lemma (incidence girth ≥ 8 ⇒ a cluster
and a nontrivial translate fit only in a cluster ≥ 4 points larger).

**The extension (drop S1, S2, S5).** Bare sizes: knot k holds max(3, sh_k + d_k) + surplus_k, so open_k = max(3 − sh_k, d_k) +
surplus_k loose bits and s_k = open_k − d_k leftover bits, whose round-1 offshoots o carry floor effects. Define X⁺: X's knot
blocks, plus for each knot w its s_w *pendant points* o (block {w, o}), plus at each pendant point R(open_w) *rays* (infinite paths of
size-2 blocks): R = 0 if open_w ≥ 3, 1 if open_w = 2, 2 if open_w = 1. Rays add no cycles, so the cover of X⁺ is the old cover
with rays hung at every lift of each pendant point.

**Claimed theorem.** Under (S3), (S4), (S5⁺) every component of X⁺ holding a live knot is infinite (holds a cycle of I(X) or a ray),
and (S6) at least two live knots: round t's junctions ↔ orbits of clusters of t + 1 points holding a knot, with parents = R*(C) and
loose bits = |∂C|. Non-live knots (open 0) are isolated points of X.

**Proof plan.** Lemmas 1–3 (girth, union lemma, L1–L3) are unchanged: rays are pendant trees, and axes lie in the core.
- *R\* now can have one point.* |R*(C)| = 1 exactly for C = {w, o} or C = {w, o, a1, …, ak} (one knot w, a non-cut point, and a single
  path from o along one ray): removing anything but the tip leaves no knot. Clusters with |R*| ≥ 2 are groups (Lemma 4 unchanged:
  every place it needed "holds a knot" still holds, because a cluster holding a knot and a pendant or ray point holds that point's
  knot); clusters with |R*| = 1 are offshoots, one parent.
- *Counting.* For j with cluster C: x ∈ ∂C gives a group if |R*(C ∪ x)| ≥ 2 and an offshoot if R*(C ∪ x) = {x}; so d + r = |∂C|,
  where d = demand and r = offshoot extensions. Need fresh = max(d, 3 − p, 1) = d + r:
  - C = {w}: loose = open_w = d_w + s_w = |∂{w}| (round 0, no fresh rule).
  - C = {w, o} (p = 1): d = d_w + s_w − 1 = open_w − 1, r = R(open_w). open ≥ 3: max(d, 2) = d, r = 0. open = 2: max(1, 2) = 2 =
    1 + 1. open = 1: max(0, 2) = 2 = 0 + 2.
  - C = {w, o, a1..ak} (p = 1): d = d_w + s_w − 1 + (R − 1), r = 1; open = 2 gives d = 1, open = 1 gives d = 1; max(1, 2) = 2 = d + r.
  - |R*(C)| ≥ 2: r = 0, p ≥ 2, d = |∂C| ≥ 1 by (S5⁺), so max(d, 1) = d.
- *Implied.* Only matters for p = 1 with d ≤ 1. A chain offshoot's parent P has |∂P| ≥ 2 loose bits, so the new junction takes only
  one of them: not implied. A round-1 offshoot is implied only if its knot holds the start's only loose bit, excluded by (S6).

**Corollary (dimension).** If a component Y of X⁺ has a tree core F (finite), its clusters are Q ∪ (prefixes of a set S of rays
based in Q), Q a cluster of F holding a knot, so its count of clusters of size m is Σ_Q Σ_S C(m − |Q| − 1, |S| − 1): eventually a
polynomial of degree R_Y − 1, R_Y = the number of rays in Y. So for K a tree, c(t) is eventually a polynomial of degree R − 1, R the
largest number of rays in one component; for bare trees a ray comes from each leaf whose neighbour has degree 2 (plus tiny cases).

**Questions.**
1. Is each step sound? In particular the R* characterisation, the "holds a knot" claims in Lemma 4 with rays present, the case table,
   and the implied argument.
2. What does (S5⁺) exclude (relays: a finite component without rays while others still grow)? Is (S6) needed or implied?
3. Is the corollary right as stated (including the leading coefficient, the number of clusters of the core holding all ray bases)?
   What does it say about why two is the census's typical dimension?
4. Predict three facts a machine check on small floor starts should show, including one that would refute the extension.
