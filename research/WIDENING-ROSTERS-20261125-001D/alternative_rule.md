# Two alternatives to choosing by holder count

This is the rule specification and test rationale written before either alternative was run. Assumption A257 selects the unique most-held distinction from a shared offer. Its probe found made knots linking different descents on the recorded five-knot starts. The question here is whether an alternative rule produces such a meeting on its own growth, and whether that meeting actually uses the extra reach. [A257](../../docs/ASSUMPTIONS.md#a257--a-birth-may-take-the-most-held-distinction-within-two-holder-steps-of-knots) · [Earlier probe and limits](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/README.md)

## The offer shared by all four rules

Use the snapshot before the complete round, for a birth with nonempty parent set $P$. For each parent $p$, let $N_1(p)$ consist of the other knots that share a distinction with $p$. Let $N_2(p)$ consist of those knots and the knots they in turn meet, omitting $p$. For $j=1,2$, put

$$
K_j(P)=\left(\bigcap_{p\in P}N_j(p)\right)\setminus P .
$$

The offer $C_j(P)$ consists of the distinctions already shared by at least two knots, held by a knot in $K_j(P)$, and held by no parent. The order of operations matters for a join. One and the same holder must be within the stated reach of every parent. All four rules choose from $C_2$. A selected $d$ in $C_2\setminus C_1$ has no eligible common holder at the shorter reach. For each holder certifying its eligibility in $K_2$, at least one parent needs both steps. An explicit certificate gives that parent, the intervening knot and this holder, as well as the shorter-reach exclusion over every holder. [Original candidate construction](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/make_engine.py)

## The primary alternative

Call a distinction *taken in the preceding round* if at least one birth selected it as an extra take in exactly the last completed round. The first round begins with no such distinctions. Ordinary transfer to a child and the creation of a fresh distinction do not set this flag. All births read the same preceding flags. After their takes are fixed, set the flags for the next round to the union of those extra takes. This is an existence test for an event on each distinction. The number of births that took it, its number of holders and all older occurrences are immaterial. The incidence record and parent lists also recover this flag without retained counts. For an already shared candidate $d$, look for a non-start holder born in the last round, none of whose parents holds $d$. Such a birth had to take $d$ as an extra. A fresh distinction made in that same round would still have only its maker as holder, since every take reads the old snapshot.

| Rule | If the full offer has one distinction | If the full offer has more than one |
| --- | --- | --- |
| Preceding-round take (RECENT) | Take it | Take the unique candidate taken in the preceding round, if there is one |
| Two-step-only offer (OUTER) | Take it | Take the unique candidate in $C_2\setminus C_1$, if there is one |
| Most holders (MOST, A257) | Take it | Take the unique candidate with the most holders, if there is one |
| Sole offer (SOLE) | Take it | Make no take |

An empty offer or unresolved tie always gives no take. RECENT uses the preceding round as supplied by this growth law. A Boolean stored with each distinction suffices. OUTER reads only the current meeting pattern. Both preserve all choices under renaming of knots and distinctions. They do still require the original shared-eligibility and uniqueness tests. Neither alternative compares holder counts, sees a roster part or reads a label of descent. The recency flag and the preference for a unique two-step-only candidate are each a new supplied rule.

**A disagreement proved on the actual input.** In the recorded five-knot start with three loose distinctions per knot, knot $i$ holds shared distinctions $i-1$ and $i$, with indices modulo five. Its two first groups leave one offshoot. For the offshoot of knot 0, the near offer is $\{1,3\}$ and the full offer is $\{1,2,3\}$. The holders of distinction 2 are knots 2 and 3. Neither meets knot 0, and each is reached through one intervening knot. All three candidate distinctions have two holders and all flags are initially clear. OUTER therefore takes distinction 2. The other three rules abstain. This is a first-round action calculated from the actual start. Its later descents still have to be grown to test for a meeting. [Recorded five-knot input](../WHAT-A-BIRTH-CARRIES-20261125-001B/starts.json)

**An abstract eligible offer separating RECENT and MOST.** Let $d,e$ be two eligible distinctions with three and six holders. Let $d$ alone have been taken as an extra in the preceding round. RECENT chooses $d$ and MOST chooses $e$. If the same offer and holder counts have only $e$ flagged, RECENT chooses $e$. No ranking of the candidates by their present holder counts alone can give both actions. This is a counterexample at the rule interface. Reachability of either marked offer on the recorded starts is an empirical question. A choice that disagrees with MOST on a tested snapshot is stronger evidence of distinct behaviour there.

## A decisive test on recorded starts

The run panel is the epic's fixed set of 205 source configurations, pairing each rule with the same start, ration and treatment under both tested knot laws, subject to the contract's resource prefix. Read each rule on descendants actually grown under that rule. For a common-snapshot diagnostic, also compute what the other selectors would choose when presented with the same offer, flags and near offer. After a divergence, that diagnostic alone cannot establish what another rule's descendants do.

Three published records anchor the comparison under not-all-equal, the cap of three, and short knots making offshoots.

| Source | Archived case to recover under MOST | Discriminator |
| --- | --- | --- |
| Five knots in cyclic order, three loose each except four at the first knot (`Ring(5,3)+1`) | Distinct parts after round 2. The first meets two others in round 5, with no start knot holding a linking distinction | Made-only meetings on the reference start |
| Five knots in cyclic order with loose counts 2, 2, 2, 4, 4 | Distinct parts after round 2. The first meets two others in round 5, with no start knot holding a linking distinction | Made-only meetings at another supply of loose distinctions |
| Four-knot census input 28 | Distinct parts after round 2. First meetings in rounds 4 and 5 run through made knots using start-held distinctions | Separates the origin of a linking knot from the origin of its distinctions |

The old files contain first-meeting rounds and the linking classifications. These examples are positive checks for reproducing the older rule. The alternatives may give different parts, rounds or no meeting at all. [Five-knot records](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/links_rings.jsonl.gz) · [Unequal loose-count records](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/links_ringk.jsonl.gz) · [Census records](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/links_census.jsonl.gz)

Read the following levels separately.

1. **Offer and actual take.** Reconstruct $C_1,C_2$ for the named birth at its own round, its actual extra take, the preceding-round flag when used, and an explicit holder witness. Record a take from $C_2\setminus C_1$ separately from one that was merely offered there. A name reversal must transport the witness and the decision.
2. **First meeting of separated descents.** Start with distinct roster parts in different classes of direct sharing at the separation round. Trace their descendants by the recorded parent relation. At the first meeting give both descendants, their descent from the two parts, the actual common witness or supplying holder, its shared distinctions, and its round of birth. A meeting solely through made knots requires checking every linker at this meeting. Record separately whether an original knot holds any linking distinction. To recover the earlier two-meeting outcome, exhibit one first part and two different second parts with both first meetings under the tested rule.
3. **Ancestry and extra reach.** For an explicit witness $w$ and meeting descendants $u,v$, check separately whether $w$ is $u$ or an ancestor of $u$, and whether $w$ is $v$ or an ancestor of $v$. The old class “no ancestor of both” permits an ancestor of one. A claim that $w$ is an ancestor of neither requires both tests to be false. Identify exclusive descendants of the two chosen parts and note separately any other contributing separation part. For a claim that the meeting uses the further reach, trace a selected $C_2\setminus C_1$ distinction to this very meeting. A take elsewhere in the same run supplies only a run-level observation. Evidence that the take *caused* the meeting would require removing it and regrowing from that snapshot.

The inherited first-meeting reader counts several ways to meet, including a take from a holder of the other descent. The common-knot reading must exhibit a knot sharing distinctions with an exclusive descendant of each part. A supplier incident with only one side establishes only the cross-take event. Likewise a made-only witnessed meeting establishes no verdict about the joint allowed states by itself. [Frozen meeting and linking definitions in code](../../experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/read.py)

## Rival explanations and stop

Recent extra takes can keep handing the same distinction onward. Although the rule reads no holder counts, on a particular run the candidate so flagged may always be the unique most-held one. Record same-snapshot action agreement, disagreements owing only to abstention, and actual choices of a lower-held candidate. A positive meeting whose history agrees with MOST supports the alternative's ability to reproduce the meeting on that start. It leaves the reinforcement explanation available. A disagreement elsewhere in the run does not place it in the meeting's history.

OUTER can also first choose a distinction on a start knot, as the five-knot example shows. Only a later certified made-only meeting can answer the stronger question. SOLE tests whether the extra branch of either rule mattered. A test ending at its round or resource cap bounds the observed cases. If neither alternative supplies a corresponding meeting on completed cases, the original result survives that challenge on the tested panel.
