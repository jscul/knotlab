<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Verdict:** the growth certificate is sound, on two premises to check; the plan's main weaknesses are in (2) and in the extrapolation.

**Gap argument (free target, members anywhere): valid.**
- If the stretch product R is rectangular and a set has no member strictly inside the stretch, the set's allowed states are a product of an above part and a below part. A non-full product has a non-full factor, so the set is not minimal.
- Side subtrees branching above the stretch cannot reconnect below it. They reach lower copies only through the ports at the top of the stretch, and a passed-through variable sits in both port sets, which makes R non-rectangular.
- This rests on two premises: copies share variables only through call arguments (no globals), and G is the exact limit projection.
- A member on a stretch boundary port serves neither adjacent stretch.
- The true bound is 2 + floor(s/r), so the stated 1 + ceil(s/r) is safe.

**Settled by construction**
- (0) is, as you say.
- (1) is not a test of side support. Projecting out side subtrees gives the same relation the path-restricted reading uses, and the argument never looks at where members sit. If any of the 66 were certified in EVERY-RAY by forgetting, P1 is automatic for them. P1 is a real test only for those certified by the path DP alone; report it on those.
- Persistence of rectangularity in longer products is algebra, not evidence.

**Sufficient only**
- "Every length-r product rectangular" is sufficient, not necessary. A non-rectangular product shows the ports stay correlated, not that a bounded bond exists.
- The cap r ≤ 12 is arbitrary. The products form a finite semigroup, so decide exactly: either some r works, or a non-rectangular cycle exists. That cycle names the periodic path to feed into (2).

**Flaws in (2)**
- A non-shattered set of k members only contains a bond. Certify minimality, and that the bond keeps both the main port and the target.
- A cycle in the table graph gives infinitely many depths. "Every depth" needs acceptance at each step of the cycle.
- To stay finite with a choice per level: fixed port arity, marks capped at k, target depth untracked, side subtrees summarised by tables with at most k marks, and a subset construction over the c-labelled graph.
- TRUE-RATE's 24/226 closure warns that the unresolved bucket may dominate.

**Overclaims**
- With an unresolved bucket, shares are lower bounds. "1,500 to 2,100 growers" from n = 66 is not supported unless nearly everything resolves and the stratum weights are applied.
- P2 is existential and cannot be extrapolated.
- P1's "a third" has no stated basis.
- The certificate gives growth, not a rate: at most 1/12 against the path λ.
- Brute force to s ≤ 3 cannot discriminate anything when r runs to 12.