<!-- claude -p --model claude-fable-5-2 --tools "" (modelUsage: claude-fable-5-2), 2026-11-14 -->

**Short answer:** (1) yes; (2) no, D is false as stated, and your lateral-path worry is exactly the failure; (3) the right condition is separation in the undirected layered graph, decided by a 22-state automaton, giving r ≤ 17. All of this is hand-derived; I have not run the counterexample.

**(1) Disconnection implies product.** 
- **Peeling is exact:** if v occurs in one constraint only, ∃v replaces that constraint by its projection on the other two coordinates, which is full (always, for NAE).
- **Disconnection:** a system whose constraint graph is disconnected has a product solution set, and projections of products are products.
- **Conclusion:** if no component of the peeled composite meets both C_0's ports and C_r's ports, R_w is X × Y (possibly empty).

**(2) Counterexample shape (c = 1).** Realise x≠y with own u,v,w and no repeats: NAE(x,y,u), NAE(x,y,v), NAE(x,y,w), NAE(u,v,w). Nothing peels, since each of u,v,w is in two knots. Take the block

- p0 ≠ a1
- p1 ≠ p2 (ports only)
- a0 ≠ a2 (arguments only)

with SELF(a0,a1,a2), the a's being own distinctions. D has the single edge 0→1, so it is acyclic, and no port is passed by identity.

Composing two levels gives:
1. p0 ≠ a1 from level 0.
2. a1 ≠ a2 from the child's own "p1 ≠ p2".
3. a2 ≠ a0 from level 0, so a0 = a1 ≠ p0.
4. a0 is the child's port 0, so a0 ≠ a''1, hence a''1 = p0.

Inductively, top port 0 fixes port 1 at every depth up to alternation, so no R_w is a product.

The path is down, lateral through the child's block, up through a second argument, and down again. D misses it because the ports-only and arguments-only components contribute no D edge, yet they splice at the shared layer.

**(3) Correct condition.** For each call i, let π_i be the partition of {p0,p1,p2,a0,a1,a2} by components of the peeled block (an argument that is port j is identified with it). Build the layered graph Γ_w with nodes (t,j), where level t carries the blocks of π_{w_{t+1}}. The condition is that no component of Γ_w meets both layer 0 and layer r.

This is decidable top-down, because climbing paths are captured by remembering the connectivity above:
- **State:** (σ, M), with σ a partition of the current layer's three nodes induced by everything above, and M the set of its blocks connected to layer 0.
- **Start:** discrete partition, all blocks marked.
- **Step on call i:** join σ with π_i on the top nodes, restrict to the bottom nodes, and carry the marks.
- **Dead states:** M = ∅. These are absorbing, and a product composed with anything is a product, so forgetting is monotone in r.

There are 22 states, 17 of them live. The family forgets if the live part of the reachable automaton is acyclic, and then r ≤ the longest live path ≤ 17. A live cycle is the syntactic obstruction; it is not a proof of non-forgetting, since connection does not imply dependence.

Your 705 passes probably contain no ports-only component together with an arguments-only one. Before freezing, re-run the held-out split with the automaton condition and run the gadget above as a regression case.