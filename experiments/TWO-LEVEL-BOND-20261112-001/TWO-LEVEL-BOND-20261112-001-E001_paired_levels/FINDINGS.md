# Can two levels carry a bond in sample 0, line 4710?

Five of 27 choices produce a three-member knot when the other inputs are forgotten. None gives the same set of extensions for every full input with the same selected bit. As a result, this rule has no repeatable two-level step made from one such knot and a helper introduced in the two copies. Whether a bond reaches every depth in this rule remains open. Its previously proved lower bound on the size of every bond to depth `s` is `1 + ceil(s/6)`. [Earlier case census](../../../experiments/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/FINDINGS.md)

## A specific comparison

Write the top inputs as `a,b,c` and the fresh distinctions as `x0,y0` and `x1,y1`. The first child receives `(x0,a,y0)`, so the next first child receives `(x1,x0,y1)`. All three outputs have fresh identities. There is no literal carry of any top input across the two levels. All eight top assignments have infinite extensions. Of the 128 assignments to the seven distinctions, 32 are compatible with both copies and the infinite side calls.

For example, the projection on `(a,x1,y0)` is the six-state not-all-equal relation. With full input `(a,b,c)=(0,0,0)`, only `(x1,y0)=(0,1)` and `(1,1)` are possible. With input `(0,1,0)`, the additional pair `(1,0)` becomes possible. The selected bit `a` stayed zero. A construction based on that bit alone could promise an extension which the actual input forbids.

There are three choices for the top slot, three for the outgoing slot and three eligible helpers distinct from the output. The check keeps each full input until after comparing its output-helper table. All 27 choices give unequal tables for at least one pair of full inputs sharing the selected bit. Five ordered choices pass the three-member knot test after projection, representing four distinct triples of physical variables. Every positive table is exactly not-all-equal. Its three two-member projections are all free. The other 22 choices fail the marginal knot test already. [All candidate tables and conflicting inputs](../../../artifacts/TWO-LEVEL-BOND-20261112-001/TWO-LEVEL-BOND-20261112-001-E001_paired_levels/result.json)

The test covers one selected input, one fresh outgoing slot, and one helper owned by these two copies. Wider input descriptions, other kinds of links and helpers in deeper side copies remain open. The result leaves the 69 all-depth linear cases and 154 conditional cases in the earlier census unchanged.

## Replay

```sh
python3 -B experiments/TWO-LEVEL-BOND-20261112-001/TWO-LEVEL-BOND-20261112-001-E001_paired_levels/check.py
PYTHONPATH=tools python3 -B -m knotlab check --cnf 'X Y Z;~X ~Y ~Z' --loops X Y --contact Z --json
```

The checker recomputes the exact unmarked infinite port relation, compares the result to the stored tables, accepts a constructed uniformly liftable not-all-equal step and rejects the unconstrained control. The second command checks the single six-state relation shared by all five positive marginal tests.

A separate enumeration rebuilt the greatest fixed point and both copies directly. It agreed on all eight input counts, the same five ordered candidates with a marginal knot, and zero uniformly liftable links.
