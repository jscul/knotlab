**Bet against C1 (and with it C2 and C5), then C4, then C3 mildly.** The main problem is in "settled by construction": the outside swap is not the only table-invisible change. I reasoned this from your design text alone; I ran nothing.

**What is wrong in "settled by construction"**

- **Item 1 is incomplete.** The table is a function of the bond matroid, and Whitney's theorem only pins the stars down for a 3-connected graph. RING-READ had 3-connectedness; small census stages mostly won't.
- **Concrete case.** Take a chain A–B–C with loose distinctions. Then {B, outside} is a 2-cut, and twisting A across it gives B′ = B ⊕ A and outside′ = outside ⊕ A. The allowed states and the table are the same, and two stars change, so it is not an outside swap.
- **The twist is probably in the census.** Example: A has 4 places, shares 1 with B and has 3 loose; B goes from 3 places to 5. If both are census arrangements, any reader must fail on one of them.
- **Item 3 needs a condition.** It assumes the largest junction's star is a bond. If that junction is a cut vertex of the graph with the outside vertex, it isn't.

**Why each bet**

- **C1/C2/C5:** "exact or outside swap at every stage" fails at any stage with a nontrivial twist, however good the reader. Round-0 stages and the 41.6% that stall are the likeliest places.
- **C4:** it is a universal equality over every stage. Two junctions sharing two distinctions put that pair in the smaller junction's star (distance 2 for a 3-place knot), and non-bond stars shorten it further. Also, "scanning down from H − 1" finds the least h only if exactness is monotone in h; record the verdict at every h instead.
- **C3:** the swap is invisible whatever the size of L, and R3 runs stages to largest + 3. So an L of largest + 1 to largest + 3 distinctions can be found as a clique.
- **C6:** no view.

**Splits to add before the freeze**

1. **Table-equivalent or not.** For each non-exact output, test whether its stars and the outside star span the same GF(2) space as the truth's. If they do, it is the same relation and the same table, so class it as "another presentation" (outside swap, twist, or cut-vertex split). If they don't, it is a real reader error. This generalises your outside-swap class and costs one rank computation.
2. **Connectivity and table completeness.** Tag each stage by the junction graph with the outside vertex: 3-connected, has a 2-separation, or has a cut vertex. Tag it also by complete table (14 or fewer junctions) or pooled. Then restate C1 and C4 as "at 3-connected stages with no shared pair", which is the claim RING-READ actually supports. A misread above 14 junctions may be the side-≤6 pooling, so reread those with a fuller table before blaming R3.

Closed stages (L empty) and an L outside 3–5 places also need a stated rule for what counts as a swap.