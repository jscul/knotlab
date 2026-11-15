# The cost of discarding the earlier stages

A fixed prefix of live positive implications constrains $w$ named Boolean variables that a later part can still use. Keep the source true and the sink false. A consistent prefix determines which names are forced true, which are forced false, and which neutral names force which others. On the neutral names the implication relation is a preorder. Every choice of these data can occur. Existentially forgotten variables disappear after their implications among retained names have been taken into account. An inconsistent prefix has its own answer.

Consequently the exact number of distinguishable prefix relations is $1+\sum_{n=0}^w\binom{w}{n}2^{w-n}Q(n)$, where $Q(n)$ counts labelled preorders. At $w=0,1,2,3,4,5$ the numbers are 2, 4, 13, 74, 732 and 12,085. These are the known numbers of Boolean families closed under intersection and union. To recover the whole answer relation using questions with at most one positive and one negative pin, the fixed universal menu for $w\ge1$ needs all $w(w+1)$ distinct unary or ordered mixed-pair queries. The query restriction is part of this result. [Exact relations and menu](../../proofs/ROUTE-FRONTIER-MEMORY-20261115-001A/ROUTE-FRONTIER-MEMORY-20261115-001A-P001_exact_boundary_profiles/proof.md) · [Classical counts](https://oeis.org/A306445)

A two-stage segment of the joined route construction can carry one selectable implication from named middle $u$, through a private boundary, to named middle $v$. Concatenating isolated segments gives a fixed formula containing a complete prefix and future test menu. Switch values supply the choices. In particular the prefix can store any bipartite array of implications on two sets of $k$ names, and later switches can single out any one of its $k^2$ entries. Every deterministic single-pass stage reader needs at least $k^2$ bits at that cut. Keeping reachability on the names still in use, plus the source and the current stage boundary, gives the matching $O(w^2)$ bound on activation-dependent memory with public indexed wiring. A whole-input reachability traversal takes linear indexed work. [Bounds and actual formula transfer](../../proofs/ROUTE-FRONTIER-MEMORY-20261115-001B/ROUTE-FRONTIER-MEMORY-20261115-001B-P001_one_pass_memory/proof.md)

At width two the fixed elementary menu needs six questions. Four tests of complete assignments suffice if the menu may use arbitrary pins. An independent minimax calculation also found that four *adaptive* elementary questions suffice there. At width six an independent enumeration gave 319,988 possible relations. These distinguish worst-case continuation information, fixed questions and adaptive questions.

The directed-streaming matrix construction and the labelled relation count are classical. Here both occur on a single fixed guarded two-route schedule, including the upper bound on what a suffix can distinguish. [Feigenbaum and coauthors](https://www.cs.yale.edu/homes/jf/FKMSZ-ICALP2004.pdf) · [Siggers on the preorder representation](https://arxiv.org/abs/1412.0011) · [Preregistration](preregistration.md)

| Scope | Status | Finding |
| --- | --- | --- |
| This attempt | Successful | Exactly 732 distinguishable projected relations on four available bits, with both finite and uniform evidence. |
| Local direction | Tested | An unrestricted choice of representation within a one-pass protocol still requires quadratic memory in the worst case. |
| Broader exploration | Continue | Share hidden padding bits and seek an exact decision rule |
| Long-term G3 and G16 | Scoped capability | The lower bound measures a specified access pattern. Whole-input work is linear for this family. |

**Next step:** Continue — Share hidden padding bits and seek an exact decision rule

| # | Direction | Payoff | Concreteness | First step and stopping condition | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Share hidden padding bits and seek an exact decision rule | 2/3 | 3/3 | Start with one conflicting pair of padding demands; test the same scope with at most one highly repeated middle identity and stop at an algorithm or a falsified cut rule. | Selected |
| 2 | Optimize constant factors in explicit frontier representations | 1/3 | 2/3 | Try the smallest new case and stop if it only repeats the current classification. | Deferred |

**Corrections:** No new correction. The prior directed two-route attribution is recorded with the preceding epic.

**Goals:** G3 and G16. The finding concerns the explicit Boolean systems and cost model above.

**Assumptions:** No change to a standing premise. Supplied wiring, observation order and existential status of variables are stated with each claim.

**Basket:** UNSIGNED-ROUTE-JOINS-20261115-001#1 taken here. SIGNED-KNOT-OVERLAP-20261114-001#1 remains a separate flat-versus-factored question.

**Basis:** Exact prefix projection, tests with explicit pins, fixed schedule wire compilation, and independent scientific review. The Fable design advisor's weekly limit remained in effect. 

## Final report as sent

2026-11-15 07:57:25 UTC. Epic 2 found a real cost to reading the stages in order. With four shared Boolean choices, a prefix can leave 732 distinguishable sets of possibilities. In general, an exact one-pass reader can need quadratically many bits in the number of shared choices, even though the full graph still has a linear-time solver. Next I’m letting the same hidden padding bit control different implications.
