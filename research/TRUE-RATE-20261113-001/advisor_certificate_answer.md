[claude-code:unrecognized_model] {"model":"claude-fable-5-2","query_source":"sdk"}
**Verdict: (1)–(4) is sound, with two things to pin down. The counterexample is a valid finite-computation proof, but it holds by construction and does not show reach.**

**Gaps**

- **Where `v` lives.** The transfer in (4) gives a bond with a local of C_s only if `v` is a local of the subtree's root copy itself. If `v` sits d ray steps below the root, you get L(s) ≤ 3 only for s ≥ d. If `v` is in a side copy, it does not count toward L(s) at all. State this in the claim.
- **Where `w` lives.** `w` must be off the ray. Otherwise L_ray(s) ≤ 3 for all s, contradicting L_ray(s) ≥ λ(s − t). Confirm this for each family; it is a free cross-check on both results.
- **Mislabel in (4).** Replacing cut-off SELF calls by G-clauses is exact because G is the exact port projection (compactness), not because of (1). (1) is the message from outside in; this is the message from below.
- **Wording in (3).** Say "has the same allowed-state set under the shift C_j → C_{j+s}", not "distributed". The shift needs the three ray args distinct, which R_1 = all 8 already forces.

**Steps**

1. Sound. Locals are fresh per copy, so the ports are a separator, and solutions on the two sides glue.
2. Sound. Side subtrees share only C_s's variables, so replacing each by G is exact.
3. Sound. R_{s+1} = F(R_s) with the same F at every s, and the full relation is a fixed point.
4. Sound given the first gap. "Triple constrained, all pairs free" is the full bond check, and free pairs also give satisfiability.

**Is it a proof?** Yes, for each family where the three computations were actually run: G as the greatest fixed point, R_1 = all 8, and the SAT check on the depth-3 truncation. It proves L(s) ≤ 3 for all s, so "the true bond grows whenever the ray bond grows" is false as stated.

**Does the bond measure reach here?** No. Port i of C_0 is the same variable as port i of C_s, so the bond {port i, v, w} lies inside one copy's neighbourhood. In the literature's terms, port i is at primal-graph (Gaifman) distance at most 1 from C_s's locals for every s. The variable is shared by infinitely many copies, so the endpoints never separate. L(s) is degenerate for any family with a pass-through port.

To make the question non-trivial, require the C_0 endpoint to be a variable that does not occur in subtree(C_1): a local of C_0, or a port that is not passed down. Alternatively, restrict to families where no a_i = i and no port is passed through by any cycle of the arg map.

**Closest standard fact.** Global consistency on a join tree: on an acyclic scheme, the projection onto a subtree is fixed by the message across the separator (Beeri–Fagin–Maier–Yannakakis 1983; Yannakakis' full reducer; equivalently, exact message passing on a junction tree). Compactness carries it to the infinite unfolding.
