**Verdict:** the extension is a reasonable minimal escape from the bounded-ports theorem, but the observable cannot see counting, so Q2 is settled by definition and Q1 nearly so. This is from reasoning alone; I ran nothing.

**Settled by definition**
- **Monotonicity:** the depth-t+1 triangle is the depth-t triangle plus knots, because the truncation leaves the last row free. So alive(t) is non-increasing and T_{t+1} ⊆ T_t.
- **Q2 is vacuous:** T_t is a descending chain among subsets of 4 complement classes, so it drops at most 4 times and is then constant. This holds for any local rule, including P3b gadgets.
- **The "counts" test is degenerate:** a monotone sequence is periodic only if constant, so the test reduces to "T_t drops after depth 20". That is a long transient, not counting.
- **Q1 is mostly the weighting:** taking gamma(n+1), since gamma(0) is undefined, the empty rule alone has about 55% of the weight and rules with ≤2 knots about 83%. Those almost certainly stabilise by depth 3, so the 90% threshold only tests about half of the 3–6-knot classes.
- **Q3 will be small:** dying needs a non-2-colourable hypergraph, so only dense rules can die, and rules with ≥7 knots carry about 3% of the weight.

**Is NAE too weak?**
Probably, but that is a separate issue from the observable. A knot forces a value only when two of its sites agree (the third is the complement). So there are no XOR-like or non-self-dual transition functions, and one bit per site leaves no room for signals. "Counting needs a richer local rule" is plausible, but this experiment cannot show it.

**Fixes**
- **Add a base case:** put a boundary condition on the last row, such as a fixed closing knot pattern. T_t is then non-monotone and can genuinely depend on t; this is the real smallest extension.
- **Or use a non-nested observable:** the language of left-edge columns realisable in deep triangles. Measure word complexity p(n) or the growth of Myhill–Nerode classes; non-regular growth is counting. Solutions per row (entropy) is a cheap companion.
- **Report weights conditional on #knots ≥ 1**, and set thresholds per knot-count class.
- **"Alive at 40 = lives" is a proxy:** report the last depth at which anything changed, across all rules.
