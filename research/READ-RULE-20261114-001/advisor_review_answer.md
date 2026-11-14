<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

Hand-derived only; nothing was run, including the Q3 example.

## Q1. Theorem R
Sound for a positive knot, but the exception is not exactly right.

- **Signs.** A complement-closed knot on three distinctions excludes exactly one antipodal pair. If nesting gives `NAE(k, x, ¬z)`, the tie that kills it is z *equal* to p (or x). Freeze the exception as "z tied to p or to x with the sign that makes the excluded pair unreachable".
- **Exactness.** A bond inside {p, x, z} contains p and x iff {p, x} is tied, or neither {p, z} nor {x, z} is tied. An opposite tie alone is not enough to fail: z tied opposite to both gives p = x and L = 2.
- **Where ties come from.** The knot is judged on S's block with free ports, so a killing tie is imposed from above, through the ports.
- **Syntactic condition.** If z is own and occurs in no other clause, R holds unconditionally: either {p, x} is tied, or all four (p, x) values occur and z is free whenever p ≠ x. Beyond that, test ties between tie classes rather than clause shapes; the four-clause gadget defeats any shape test.

## Q2. Lemma C
**Claim 1 is false as stated when |T| ≥ 2.** With T = {p, q}, a far top u tied to q and a bottom clause `NAE(p, q, v)`, the set {p, u, v} is a bond with members on both sides of the stretch. What the hypothesis proves:

- **Claim 1′.** A bond containing all of T lies on one side plus T: some T-slice is a non-full product, so one factor is non-full, and minimality empties the other side.
- **Claim 2′.** With h = |T \ W| hidden carried coordinates, the bond is a union of at most 2^h products. It has at most 2^h clusters, and they may sit in the middle, not only at top and bottom.

"Within r levels of the target" is also wrong. Rectangularity bounds gaps, not cluster length, and a cluster may run below the target and into side copies. I would define:

- **Stretch:** the path copies at depths a to a+r together with their side subtrees, all member-free.
- **Local:** the minimal cluster size depends only on a finite state, namely the carry map, the allowed T-values, and which T-values the cluster excludes.

Periodicity then holds because the set of states reachable in exactly s steps is eventually periodic. "Bounded or at least s/r" survives.

## Q3. Read but growing
Outside the exception, none exists. Every port value is a main port or an ancestor's own distinction. A non-shattered triple holding carried p and an own x of depth d therefore gives L(d) ≤ 3, unless the exception applies. Triples of main ports do not depend on depth.

Inside the exception, with one definition:

```
S(a,b,c), own u, x, w:
  u ≠ a               (gadget, or NAE(a,u,u))
  NAE(a,x,b)
  NAE(c,x,w)
  SELF(a,u,x)
```

Below the root, b holds ¬p, so the knot {a, x, b} reads carried a at every copy but is vacuous. What remains is the chain `NAE(x_{i-1}, x_i, w_i)`. By my count L(s) = s + 3, with bond {p, q, w_1..w_s, x_s}.

This contradicts the census sentence about unbounded families, unless the family is outside the census or the census judges knots after system ties. Run it first.

## Q4. Characterization
Candidate rule: L is bounded on a residue iff, at those depths, some set of bounded size containing an own distinction of the target and a position holding a carried value *up to tie class* stays non-shattered in the whole system, and no tie splits p from x.

- **Provable:** the ⇐ direction (R generalized from knots to bonds), and ⇒ under conditional rectangularity via Claims 1′ and 2′.
- **Census facts:** that every non-forgetting family is conditionally rectangular for some r, that exception families are absent, the 83 undecided, and the 86% knot share.