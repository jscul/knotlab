**Lower bound: correct, but weak, and probably not tight.**

- **Simplification.** A copy containing a dead copy is itself dead, so A_t is just the number of minimal dead copies and no DP is needed.
- **Sharper bound for free.** The limit state restricted to a copy is itself a living state of that definition's limit. So each dead copy needs its own *minimum* witness count, not just one: w_t ≥ Σ over an antichain of w_{t−s}(i), with the minimum taken per definition over all ends. For SELF-only families this gives w_t ≥ N_{t−T}·w_T.
- **P1 is likely already refuted.** At t = T, A_T is typically 1 (the root). If the 797/800 result was measured at depth T, P1 fails there before you run anything, so check that first. P1 can only hold where w_T = 1.

**P2: yes, settled.**

- With regular branching b, the bound alone gives w/N ≥ b^−T at every depth, so "constant" and "between" are excluded.
- P1 would make the share exactly b^−T, so the ratio is 1.
- The factor-2 test over two depths only measures drift inside [b^−T, 1].
- P2 is only open where dead copies sit in a subdominant part of the call graph, so that A_t/N_t → 0.

**Also settled.** If relations shrink with depth (R¹ ⊆ NAE), every depth-t witness contains a depth-(t+1) witness, so w is nondecreasing along any one state. Only the converse share is informative.

**What would be interesting.**

1. **Multiplicativity:** whether w_t = N_{t−T}·w_T exactly (copies independent) or strictly more. Report the excess and where it sits: inside minimal dead copies, or in copies that are alive on their own but forced dead by their ends.
2. **Simultaneity:** whether one state attains all three minima. Failure means the depths trade off against each other, which no per-depth bound can see.
3. **Thresholds:** replace P1 with the multiplicative law at ≥90%, and report the distribution of w_t/(N_{t−T}·w_T).
