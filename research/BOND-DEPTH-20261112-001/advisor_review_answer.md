**Verdict:** the method is exact for what it computes (the least spine-only bond), and the (F,G) union is correct.

**Is the minimality condition right?**
- Yes. Being constrained is monotone under adding distinctions, so single-x deletions suffice for minimality.
- The union is sound for two reasons: the block update acts elementwise on families, so it commutes with union, and the final test "∅ ∉ G" distributes over union.
- The update must be G′ = step(G) ∪ ⋃ₓ stepₓ(F), where stepₓ unions over both values of an x in the new block.

**What is settled:**
- **Spine bonds are true bonds.** Side branches and the tail are summarized exactly when W avoids them, so L_spine ≥ L holds.
- **The classes are not a reading.** For one definition, blocks 1..s−1 are identical, so L_spine(s) is a fixed-length shortest path in a finite weighted graph (a min-plus matrix power). It is therefore eventually linear plus periodic, with the rate given by the minimum cycle mean. Bounded versus growing is decidable per family, and nothing in between (such as log growth) can occur.
- **s ≤ 8 is not enough.** The transient can exceed 8, so compute the cycle mean instead of sampling.

**Flaws:**
- **Asymmetry.** "Bounded" transfers to L, but "growing" and "ruler" are only upper bounds until side branches are included.
- **Missing class.** Some (u,v) pairs may lie in no common bond, so L = ∞.
- **Arbitrary endpoints.** Port 0 and "first own distinction" depend on labeling; take the min or max over ports and locals, or report both.
- **Brute-force semantics.** The brute force must close truncated calls with the limit relation, not leave them free, or it validates a different problem.

**Exact side branches:** yes, by running bottom-up instead of top-down.
- Summarize a subtree by (F,G), where F is the family of relations it can induce on its 3 args over all words.
- Combine as G = c(G₁,F₂) ∪ c(F₁,G₂) ∪ cₓ(F₁,F₂).
- Get the least cost per summary by a least fixed point (Knuth's 1977 generalization of Dijkstra), pruned at the L_spine budget.
- An empty side branch is the summary ({limit relation}, ∅) at cost 0.

**Prior work:**
- **Shattering.** "Constrained" means not shattered by the solution set, so bonds are the minimal non-faces of the shattering complex (Sauer–Shelah, Pajor). Teaching sets are a different notion.
- **Prime implicates.** Bonds are the minimal supports of implicates, which ties to knowledge compilation. For XOR systems they are matroid circuits; NAE is not linear, so expect no exchange property.
- **Bounded treewidth.** The property is MSO (∃ assignment to W, ∀ extensions fail), so Courcelle plus Arnborg–Lagergren–Seese gives the DP in principle. Your subset construction is the usual ∃∀ blow-up (2-QBF on bounded treewidth: Chen; Pan–Vardi).
- **MUS.** The MUS literature minimizes over clauses, not variables, so it does not apply directly.
