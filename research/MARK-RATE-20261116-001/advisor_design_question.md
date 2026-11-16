Advisor: soundness review before freezing (under 500 words; say what you checked; point out gaps).

Setting: BLOCK-REACH-20261116-001 (proofs/BLOCK-REACH-20261116-001A/.../proof.md, Theorem F): along a path of orbit blocks, group j
holds O_(k+j), the side subtrees of O_(k+j-1)'s other children and the knots placed at O_(k+j-1); groups j-1 and j share O_(k+j-1).
If every r consecutive block steps compose to a rectangular relation, a bond reaching s levels down has >= 1 + ceil(s/r) members. Cyclic
small-orbit rulers mostly have r = 2, so this gives rate 1/2, while the census reads s + 2 at depth 9.

Plan, Theorem M (no single skip). Suppose a bond B meeting level k and level k+s has no member in group i (1 <= i <= s-1). Left part
L = members in groups < i (so outside the proper subtree of O_(k+i-1), O_(k+i-1) itself allowed); right part R = members in groups > i
(strictly below O_(k+i)). For an assignment sigma, X(sigma_L) = values of O_(k+i-1) taken by full states realising sigma_L, Y(sigma_R) =
values of O_(k+i) taken by full states realising sigma_R. By the tree decomposition, sigma is realisable iff some (x, y) in X × Y lies
in T_i (the block step with the side subtrees unmarked). B constrained needs some sigma with (X × Y) ∩ T_i empty. I compute, at stable
depth, families U(t) (up signatures: O's values consistent with marks outside its proper subtree, own pins allowed, knots not placed at O
or below) and below(c) (O's values consistent with marks strictly below O, with O's and deeper knots), closed under every finite marking;
then cut X to values extending through the step to a feasible child and Y to the step's range (a part no full state realises is itself
constrained, so not in a bond). If every cut X and Y meet T at every step, no group is skippable: |B| >= 2 + (s-1) = s+1, so the rate
is at least 1 at every depth (the up-then-down case as in Theorem F). Restricted to r0 = 0 (F constant), so finite-depth families are
subfamilies of the stable ones.
Pilot on a disclosed held-out sample (8 cyclic, 4 acyclic, 4 half-rate): cyclic r = 1: 2/2 pass (automatic), r = 2: 3/5 pass, r = 3:
0/1; acyclic 4/4 pass; half-rate 0/4 (as they must, since their least bonds skip levels). Gate: 360 SAT-computed real signatures from
random markings at depth 7 all lie in the computed families.
Predictions to freeze for the other descriptions: P1 at least half of the small-orbit cyclic rulers with r >= 2 pass; P2 every acyclic
ruler passes and no half-rate passes; P3 every passing description has census L(s) >= s + 1 (a sanity check, settled?).

Questions: Is X × Y ∩ T = ∅ the exact constraint condition here (is the projection onto L ∪ R really the join through T with the
unmarked side subtrees of O_(k+i-1)'s other children)? Is the cut to dom/range sound? Is it right that marks in O_(k+i) are excluded
from R? Does a failure say anything (skips may be possible but cost members elsewhere)? Any cheap sharpening to get s + 2?
