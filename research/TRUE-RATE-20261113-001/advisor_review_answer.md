**Verdict: Plan A is sound, given three conditions; Plan B is false as stated.** This is reasoned from your description alone; I have not seen the code or run anything.

**Plan A exactness**
- **Table:** Knuth's least fixed point is correct here, since cost is own members plus the sum of child costs (superior, non-negative). It terminates on a finite universe.
- **Condition 1:** least cost per summary suffices only if combine is a congruence on summaries. Partial summaries must stay over all of C_j's environment distinctions until every child is joined; deduplicating after projecting to ports is unsound.
- **Condition 2:** base summaries must treat every SELF call of C_s as a side call.
- **Condition 3:** if the ray may choose among SELF calls, the edges need one transition per call.
- **Karp:** on the trimmed graph with n nodes, any length-s walk is cycles plus a simple path, so L(s) ≥ λ(s − n + 1), with t = n − 1. Pumping the minimum-mean cycle gives L(s) ≤ λs + c only on one residue class, so λ is the liminf, as you wrote; the limsup may be larger.
- **Acyclic case:** if the trimmed graph has no cycle, bonds stop existing at large s. Report that separately.

**Tractability**
- One-at-a-time combination is a min-plus product and is fine. The risk is the table size, since families of masks number up to 2^256.
- **Fallback:** if the table does not close, restricting to listed summaries gives an upper bound on λ. Mapping all unlisted summaries to one optimistic summary at cost cap + 1 gives a lower bound, but only if combine is monotone in a forcing order.

**Plan B**
- **As stated, false:** a side subtree realises a 3-port relation (e.g. equality) that no ≤ 3 own NAE members of C_j need express.
- **Weak form, also false:** if arguments pass parameters through, a level can transmit at zero cost, so "one member per level" fails.
- **What survives:** weights are integers, so λ_true > 0 iff the trimmed graph has no zero-weight cycle, and then λ_true ≥ 1/n. Zero-weight edges are the pure pass-through map τ, so P2 reduces to whether τ has a periodic point among summaries reachable only via sides.

**Settled by construction (not predictions)**
- λ_true ≤ λ_ray.
- λ_true is rational with denominator ≤ n.
- The gate is a valid check: the old cap lost nothing per s, since a side cost ≥ L_ray − 1 cannot improve on the ray.

**Better predictions**
- **P2′:** no zero-weight cycle in any complete family.
- **P3′:** drop the factor 3, which has no mechanism. Predict λ_ray − λ_true = 1/2 exactly in the 4 families, and 0 (bounded deficit) in most of the other 58 or more.
- **P4:** the fallback sandwich closes wherever the table closes.
