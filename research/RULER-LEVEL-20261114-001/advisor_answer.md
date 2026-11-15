**Verdict:** both theorems hold as stated for s ≥ 1, with two proof lines to repair, and I would freeze a weaker condition than "tree-isomorphic". I checked everything by hand and did not open the RANDOM-FATES-001B record or run anything.

**Holes in A\***
1. **Acyclicity is under-argued.** "At most two knots per address, at most one shared address" does not exclude a cycle. The real reason is that every address of levels 1..N has exactly one parent knot: the deepest address on a cycle would need two knots at or above it, but its lower knot has no other member that high.
2. **Connectedness holds** because level 0 is a single address and every address ascends to it. Say so if 001B requires it.
3. **"Every other pair is farther" is true, but the count needs the shared knot.** With the last common ancestor at level j < k, the distance is 2(k−j) + s − 1 ≥ s + 1, because the ancestor's knot is counted once. This fails at s = 0 (siblings are at distance 1), so state s ≥ 1.
4. **"Descendant" means descendant in the knot tree**, not by word prefix. In Theorem A the parent of v0 is g(h1⁻¹(v)), not v.
5. **Confirm 001B's hypotheses** cover a finite truncated pattern with single-knot addresses (root, level N) and a minimum over all sets, and that it is proved, not computed. Declare it as a dependency.

As a sanity check of d + 2, I verified on the bare chain that {ends + pendant members} is non-shattered for s = 1, 2, 3. I did not check minimality or the lower bound.

**Theorem A**
The proof is sound. The three addresses are distinct by level and last letter, and distinct w give distinct knots. Automorphisms preserve length, so uniqueness of upper and lower members follows as written. No hole found.

**Census**
- "No tree-isomorphic description has another outcome" is implied by A\*, so it checks the code and is not evidence.
- "Tree-isomorphic at N = 9" is a property of the instance. Only descriptions of Theorem A's form are covered at every N, so say how many of the 299 have that form.

**Condition to freeze**
The proof never uses fullness. Level distance ≥ s is free, since knots span at most adjacent levels. What it uses is:
- no cycle of knots; and
- from the level-k address, a chain of s knots descending one level each.

Freeze that, provided 001B covers forests. It is strictly weaker and costs no new proof.

**Cheapest next step for the 158**
1. Test incidence-graph acyclicity at N = 9. Any that are forests with a descending chain are already covered.
2. For the cyclic remainder, test the discriminator your six breaks suggest: no cycle of knots passes through two members of one cross-level knot of the chain. The intuition is that a cyclic part attached at a single address can only stand in for that address and cannot shorten a bond.
3. Do not assume L ≤ s + 2 in general. Adding knots keeps the chain set non-shattered, but its minimal non-shattered subset may drop an endpoint.
