# Where regrouping still works after the original stage scan breaks

Two positive middle variables $J$ and $K$ can serve as the true start and false end of many independent directed paths. On each path let the hidden padding bits control whether each implication is live. The path creates a contradiction precisely when every tested literal is false. Thus keeping all the paths broken is exactly the original clause-satisfaction question. A uniform guarded template with two repeated middle identities and at most three binary-edge placements per shared pad can express arbitrary strict 3-SAT by changing just its visible switches. Variable copies are linked by additional width-two implications, so the three-occurrence limit applies to a mix of clause sizes. [Fixed construction](../../proofs/TWO-RELAY-PADDING-20261115-001B/TWO-RELAY-PADDING-20261115-001B-P001_two_middle_reduction/proof.md)

For that **disjoint-path layout**, grouping by padding bits instead of by path gives a second linear reader whenever each pad occurs in at most two surviving normalized clauses. A pad used with only one sign can satisfy its clauses immediately. Each remaining pad can satisfy one of two clauses. In the usual graph of these competing pairs, a connected group is feasible exactly when it contains an already satisfied clause or a cycle. An unmarked tree has one fewer available bit than clauses, and is minimally contradictory. This exact criterion covers arbitrary path lengths. [Witnesses and controls](../../proofs/TWO-RELAY-PADDING-20261115-001A/TWO-RELAY-PADDING-20261115-001A-P001_track_regrouping/proof.md)

In a different construction, allow many positive middle identities to repeat, but use each in at most two stage positions. Even if each pad is also used in at most two implication positions, a fixed wiring per source width can express general 3-SAT. The reduction uses opposite signs of a fresh pad to express a disjunction of implications and unconditional directed cycles to make several ports agree. Disjoint cuts in two directed networks already imply the abstract two-use pad result. The contribution here is its exact transfer to the serial guarded layout, both occurrence caps, and fixed wiring. The checker verified the raw guarded decisions and projected source assignments, including deliberately broken sign and feedback controls. A different upper bound on this arbitrary layout is $O(2^q r)$ for $r$ stages when only $q$ pads appear with conflicting single-half signs. [Both bounds and prior result](../../proofs/TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md) · [Boros et al.](https://www.keisu.t.u-tokyo.ac.jp/data/2007/METR07-35.pdf)

Give the six middle and edge-pad positions of each stage a fixed order. When the two occurrences of every repeated name enclose or avoid each other, solve from the innermost pair outward. A constant-size relation keeps just the states a single stage needs at the two ends. Matching the pair means trying its shared bit both ways. Thus arbitrarily deep nesting still takes linear total work. More generally, if removing $k$ names suffices to leave only nested or disjoint pairs, two separate searches find such a set and try its values in $O(2^k r)$ indexed operations. Even if one name interleaves with a thousand others, it alone can cost just a factor of two in the value search. The test concerns the occurrence order of the supplied formula. A diagram or a count of crossings alone yields no runtime lower bound. [Nested grouping](../../proofs/TWO-RELAY-PADDING-20261115-001D/TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/proof.md) · [Alur and Madhusudan](https://www.cis.upenn.edu/~alur/nw.html)

Both hardness statements are polynomial-time reductions and the target languages belong to NP. They establish exactly what a general polynomial shortcut for the specified inputs would entail. They leave P versus NP open. Positive implication cycles used as wiring supply no independent native-recurrence claim.

The two independent fixed-wiring reductions agreed with all 256 clause selections on three names. In the two-use construction the oracle also projected the compiled solutions back onto prescribed source assignments. In the nested case the raw checker agreed on all 65,536 half-activation settings for the designated two-stage wiring. At depth 1,200 it checked both SAT and UNSAT on 38,432 strict clauses. A separate test with 17 interleavings needed just one exceptional name. The [dated index replay](same_day_index_replay.md) records a prior-work search whose same-day matches changed after the one-middle proof was activated. Its named predecessor was already an admitted dependency.

| Scope | Status | Finding |
| --- | --- | --- |
| This attempt | Successful | Two distinct placement restrictions can already carry general 3-SAT; explicit linear readers survive under the stated joint restrictions. |
| Local direction | Tested | In the two-use layout, the number of names whose removal leaves nested pairs gives a constructive work bound even when the number of crossing pairs grows. |
| Broader exploration | Research directions | Find the least number of names to condition on after choosing a branch order at each stage |
| Long-term G3 and G16 | Scoped capability | An all-input polynomial-time solver for either hard family would give a polynomial-time solver for general strict 3-SAT. |

**Next step:** Research directions — Find the least number of names to condition on after choosing a branch order at each stage

| # | Direction | Payoff | Concreteness | First step and stopping condition | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Find the least number of names to condition on after choosing a branch order at each stage | 2/3 | 3/3 | Freeze the allowed within-stage branch swaps, then test whether a zero-deletion order is efficiently recognizable or a small instance defeats a candidate greedy rule. Open a new scope only if selected. | Suggested |
| 2 | Tighten the finite-state constants for one stage | 1/3 | 2/3 | Try the smallest new case and stop if it only repeats the current classification. | Deferred |

**Corrections:** No new correction. Abstract switching-network, bounded-occurrence SAT and nested-word results are credited in the individual proofs.

**Goals:** G3 and G16. The finding concerns the explicit Boolean systems and cost model above.

**Assumptions:** No change to a standing premise. Supplied wiring, observation order and existential status of variables are stated with each claim.

**Basket:** ONE-RELAY-PADDING-20261115-001#1 taken here. The four-epic allowance ends here. The previous flat-versus-factored direction remains separately open.

**Basis:** Admitted strict 3-SAT reduction, separate two-middle and two-occurrence compilations, constructive algorithms, SAT replays and independent technical review. The Fable design advisor remained quota-limited. 

## Final report as sent

2026-11-15 08:30:15 UTC. Epic 4 reached general 3-SAT and found another linear-time grouping.

| Scope | Status | Result |
| --- | --- | --- |
| This attempt | Proved | Two repeated middle names suffice to encode arbitrary 3-SAT when hidden bits can be shared. |
| Local direction | Proved | Even two occurrences per name in both roles suffice if many different names can repeat. If deleting one name leaves nested pairs, decision stays linear even with arbitrarily many interleavings. |
| Broader exploration | Open | How much can a solver gain by finding a different grouping of the same input? |
| Long-term goal | Open | A polynomial-time shortcut for the hard family would give a polynomial-time 3-SAT solver. |

**Next step if this line resumes** — Test whether swapping the two equivalent branches within stages can reveal a nested grouping.

| Candidate | Payoff | Concreteness | First check |
| --- | --- | --- | --- |
| Choose the branch order in each stage | 2/3 | 3/3 | Check whether local swaps can be chosen to make all pairs nest; test the first failure of a greedy rule. |
| Tighten constants in the nested-pair reader | 1/3 | 2/3 | Measure the states needed by one two-route stage. |
