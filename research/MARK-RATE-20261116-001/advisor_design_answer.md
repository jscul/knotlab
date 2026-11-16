**What I checked:** the argument as you stated it, by hand. I did not open `proof.md` or the pilot code, so anything that depends on how they define groups or families is flagged, not verified.

**Exactness of (X × Y) ∩ T_i = ∅.** Yes, on two conditions:
- **Separation:** no knot placed at O_(k+i-1) touches its parent or grandchildren, and no knot placed elsewhere touches the side subtrees. Then the three regions meet only in O_(k+i-1) and O_(k+i), and states glue across those two blocks.
- **T_i as used:** it must be the projection of the knots at O_(k+i-1) together with the solvability of the unmarked side subtrees at the actual depth.

**Cut.** Sound, and it only turns raw signatures into your full-state X and Y. One thing to confirm: Y must be cut to T(U(∅)), the image of the up-feasible values, not the step's whole range. They coincide only if U(∅) is everything.

**Marks in O_(k+i).** Correctly excluded, since they are group i. But the groups must partition the marks for the count 2 + (s-1). Say explicitly that a mark on the shared block O_(k+i-1) belongs to group i-1 only.

**Gaps.**
1. **Depth transfer.** The test is monotone in X, Y and T, but the discard step is not. A signature whose cut is empty at stable depth can have a non-empty cut at finite depth, where truncated subtrees make T and below(∅) larger. That pair was never tested. "Subfamilies of the stable ones" needs a proof for the cut families, or test uncut X′ against T ∩ (X′ × Y′) directly at each depth.
2. **The gate is one-sided.** 360 samples show containment on random markings only. A pass verdict needs the families to contain every real signature. Prove the closure: the generators are all single marks and pins, and the combining operation is the join through the block, not a plain intersection.
3. **Predictions.** P3, and "no half-rate passes" in P2, are consequences of the theorem. Label them consistency gates; a violation means a bug. P1 is the real prediction, and the pilot (3 of 6 with r ≥ 2) sits exactly on its threshold.

**What a failure says.** As run, nothing definite. The test ranges over all markings, while a bond needs L and R each unconstrained. A failing pair may come from a constrained L, so the bond sits inside L. If you record a failing witness where every assignment of L and of R has a non-empty cut, a real bond skipping group i exists. Even then it does not bound the rate, since the skip may cost members elsewhere. The half-rate cases show skips can pay, so failure leaves s + 1 open.

**Sharpening to s + 2.**
- **Thin families:** compute the signatures reachable with exactly one mark per group, and one each at the ends. If no thin pair misses T at any step, every bond has a group with at least two members, so |B| ≥ s + 2. This is finite if the thin signatures stabilise.
- **Least-mark costs:** attach to each signature the least number of marks producing it and propagate by min-plus through the steps. That gives the exact L(s) at every depth and makes failures quantitative. I would freeze this version.
