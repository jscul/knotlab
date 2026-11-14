<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Fix before freezing: the training counts do not add up.** With 6,321 families and 2,961 without a tie cycle, 3,360 have one. Only 3,322 + 5 = 3,327 of those are listed as non-forgetting. That leaves 33 families with a tie cycle that forget, which contradicts H1 on training, unless "tie cycle" differs from "self-tie in some product" (empty products?) or there is an unreported third class.

**(1) The residual can be named, and the equivalence is then a theorem.**
- **Reduction:** Rectangular relations (with the empty one) form an ideal: X·(A×B)·Z is rectangular. Every long enough word has a factor whose product is idempotent. So non-forgetting ⟺ some cycle product is a non-rectangular idempotent E, provided cycle words can be pumped in your grammar.
- **Classification:** For idempotent E, take the core {x : xEx}; E is a preorder there. E is non-rectangular ⟺ the core has at least two classes.
- **Two types:** Incomparable classes give a conserved label, f(start) = g(end). A tie is the case where the label is one bit, and a parity is the case where it is linear. Comparable classes give a one-way order with no conserved quantity.
- **Residual:** I expect the 55 to be non-linear labels (such as "start ∈ {011,100}", a complement-closed class) or orders.

So "no tie cycle and no knot cycle ⟺ forgetting" is a near-tautology if "knot cycle" means "everything else". The empirical content is the split by type.

Your example does not recur as stated. "Full minus (011,010) and (100,101)" squares to the full relation, via 011→000→010. Check that the 55 are reported at an idempotent power.

**(2) H2's bands are loose.**
- **Non-chains:** Training is 93.4%, and the standard error at n ≈ 835 is about 0.9 points. So 90–97% is ±4 SE and nearly unfalsifiable; about 91.5–95.5% would be a real test. The refutation itself only needs one counterexample.
- **Chains:** 2,126 of 2,126 suggests a theorem. Predict 0 violations or prove it; ≥ 99.5% tolerates about 10.

**(3) Settled by construction.**
- **H1:** It is a proof check, as you say. Also, 3,322 of the 3,327 tie cases are identity cycles, which are ties trivially, so the tie rule's reach rests on 5 families. Report held-out results with identity cycles excluded.
- **H3:** A tie-free conserved parity exists in principle (a₁⊕a₂ = b₁⊕b₂). It is only a test if your generator can produce one; otherwise it is vacuous.
- **H4:** It is unfalsifiable as worded. Replace it with: every residual family has a cycle idempotent with at least two core classes, counted by type (label or order).

I ran nothing; the reduction and classification are from reasoning only, so replay them on the 55 before relying on them.