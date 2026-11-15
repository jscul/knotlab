# Shared hidden choices and the one-middle decision rule

Every original implication $D$ has two strict triples $D\lor z$ and $D\lor\neg z$. A triple acts only when its three supplied switches are on. The same hidden Boolean $z$ may now pad several different implications. With exactly one triple active, disabling the implication requires one value of $z$. If both are active the implication is unavoidable. A satisfying assignment chooses each hidden bit once for the entire formula.

With all middle names distinct, a satisfying assignment with the endpoints on needs a single broken stage. Breaking that stage requires one disabled implication on each of its two branches. A pad used on both branches contributes two extra minimal contradictions, one per orientation. If $c_i$ distinct pad names occur on both branches of stage $i$, the number of global inclusion-minimal contradictory switch sets is $\prod_i(2+2c_i)$, regardless of how often those pads are shared with other stages. Each original stage contributes two. Sharing can raise that to six, so even $6^r$ minimal contradictions can have a linear decision rule. [Stage classification](../../proofs/ONE-RELAY-PADDING-20261115-001A/ONE-RELAY-PADDING-20261115-001A-P001_local_pad_obstructions/proof.md)

Allow a single middle name $J$ to occur at any stages, with no bound on how often a padding bit is reused. If $J$ is true, take the **last true boundary** of a satisfying assignment. Make all earlier boundaries true and all later ones false. Every outgoing implication from $J$ into the false part must be disabled. With $J$ false, take the **first false boundary** instead and disable every incoming implication from the true part into $J$. At the change, also break each branch whose middle is private. In either case the resulting demands on pads are individual Boolean literals. Accumulating them while moving the cut gives an indexed linear-time decision and a satisfying assignment whenever one exists. [Proof and witness construction](../../proofs/ONE-RELAY-PADDING-20261115-001B/ONE-RELAY-PADDING-20261115-001B-P001_one_middle_cut/proof.md)

Two stages already show that independent identifications can interact. Enable $x_0\to J$ and the ordinary second route $x_1\to b_2\to x_2$. Make $J\to x_1$ live for $z=0$ and $J\to x_2$ live for $z=1$. Fix $x_0=1,x_2=0$ and disable the other implications. Splitting either $J$ or $z$ restores satisfiability. Sharing both makes the contradiction unavoidable. The switch support has 48 members. In the full two-stage census, 52 of the 168 placements of one middle-pair join and one edge-pad-pair join admit such an input. Across all 11,010,048 placement/half-activation pairs, 4,944 have this property. Every inclusion-minimal such contradiction in that census has 48 or 54 raw switches, including both endpoints. These are labelled counts over normalized half activations, with a raw realization for each. [Replay and output](two_stage_census.py) · [Numerical record](two_stage_census.json)

Independent enumeration checked the complete two-stage guard projection for all 4,140 partitions of the eight padding positions. A separate three-stage enumeration compared the cut rule to all 33,554,432 combinations of fixed repeated-middle value and half activations on a wiring with both middle slots joined in the first stage. Forcing two particular stages to drop can impose opposite values on one pad. The ordinary decision asks whether *some* drop can occur and therefore has a different answer on such inputs.

| Scope | Status | Finding |
| --- | --- | --- |
| This attempt | Successful | An arbitrary number of shared hidden pad values remains compatible with a linear decision procedure when at most one middle name repeats. |
| Local direction | Tested | Each pad shared across the two branches of a stage supplies exactly two new local minimal obstructions; different stages can still be treated separately when their middles are private. |
| Broader exploration | Continue | Repeat two distinct middle names and regroup by shared padding occurrences |
| Long-term G3 and G16 | Scoped capability | This work identifies a tractable unrestricted-in-pad-reuse subclass of the explicit guarded decision problem. |

**Next step:** Continue — Repeat two distinct middle names and regroup by shared padding occurrences

| # | Direction | Payoff | Concreteness | First step and stopping condition | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Repeat two distinct middle names and regroup by shared padding occurrences | 2/3 | 3/3 | Use the two fixed middle truth values as entry and exit for independent clause tests. Check the reduction and attempt linear decision on pads used at most twice. Stop at the budget of four epics. | Selected |
| 2 | Seek a faster online implementation for the one-middle witness | 1/3 | 2/3 | Try the smallest new case and stop if it only repeats the current classification. | Deferred |

**Corrections:** No change to earlier statements. Earlier private-pad reachability explicitly assumed freshness.

**Goals:** G3 and G16. The finding concerns the explicit Boolean systems and cost model above.

**Assumptions:** No change to a standing premise. Supplied wiring, observation order and existential status of variables are stated with each claim.

**Basket:** ROUTE-FRONTIER-MEMORY-20261115-001#1 taken here. The earlier flat-versus-factored suggestion remains separate.

**Basis:** Finite guarded SAT, the two-stage joint identification census, proof of the cut normal form and independent reviews. The Fable design advisor remained quota-limited. 

## Final report as sent

2026-11-15 08:12:56 UTC. Epic 3 found a second linear-time solver. When one middle choice is shared arbitrarily often, try it true and false. Each case reduces to finding one place where the boundary switches from true to false and checking that the hidden bits can break the paths there. I’m now testing the same rule with two shared middle choices.
