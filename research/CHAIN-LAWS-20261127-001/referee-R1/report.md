# Independent referee report on eight-knot chains under the two growth cuts
**Confirmed with fixes. Block on the prediction that at least 95% of checked chains carry the complete step.**

Every one of the **817 round-six survivors** carries the step under either cut. Across all 7,075 starts, **873** carry it at some reached round. The survivor advantage over ordinary growth is almost entirely selection. Applying ordinary growth to those same 817 starts already gives **816** witnesses. [Full recount](step_summary.json) · [Matched starts](selection_counts.json)

## What holds

Each of the 7,075 connected census classes gets one vote. Starts have three to five knots and at most twelve distinctions. A chain has eight three-place knots, each sharing one distinction with the next, with all nonconsecutive knots disjoint. A full pass requires the four lower triples, the upper relation in all three choices of “both”, individual necessity of all eight laws, and the two tests of whether a reading is visible at a single source knot or stage bond.

| Claim | Independent result per rival law |
| --- | --- |
| Funding | 5,111 fund a first round. The same 817 reach round six and can fund round seven. Of the 4,294 others that grew, 171 closed and 4,123 stalled. [Growth counts](growth_counts.json) |
| L1, fewer than 10% ever | Failed. The frozen test found 878/7,075. The full test finds **873/7,075 (12.34%)**, including 56 that stop before six. The bound allows at most 707. [Start counts](step_summary.json) |
| L2, within 10 percentage points of ordinary growth | Failed. At round six the frozen test gives 816/817. The full test gives **817/817**, against **4,213/5,111 (82.43%)** under ordinary growth. [Matched counts](selection_counts.json) |
| L3, at least 95% of checked chains | **3,919/3,932** pass the frozen test and 3,918 also need every law. Adding the single-bond test leaves 2,396 frozen passes and **2,395 complete passes (60.91%)**. Among the 22,441 chains after the first three, 17,366 pass every gate (77.39%). Overall **19,761/26,373 (74.93%)** pass. [All gate combinations](step_summary.json) |
| What the stage can change | 105,434/105,492 defining lower triples and 79,119/79,119 upper relations have exactly the seven words other than 111. No single source knot determines a named lower reading in 2,786,814 comparisons. Deleting one chain law restores upper 111 in 632,860/632,952 law-and-role tests. [Reading and deletion counts](step_readings.json) |

The four clauses already rule out upper 111. Seven binary triples already imply three free pairs, so that control had zero opportunities to fail once seven words occurred. All 16,519 chain laws counted once per stage retain the full three-place not-all-equal relation. The 58 lower failures each have a one-law explanation. Number the chain so knot `i` uses `(2i,2i+1,2i+2)`. Adding the law on (0,1,5) to the bare chain reproduces 42 failures. The law on (7,9,11) and its reversal on (5,7,9) explain eight each. [Source projections](source_projections.json) · [Previous ordinary-growth explanation](../../CHAIN-STEP-20261127-001/referee-R1/failure_rule.md)

## The fixes

1. **Block — L3 for the complete step.** Replace “L3 held” in the decision and position table with “L3 held for the frozen test alone. The complete step occurs on 2,395 of the 3,932 checked chains. The predicted 95% fails.” It needed 3,736 passes. In the method, qualify “`laws.py` counts the same on every census start” by stating that the rival code omits the single-stage-bond test and counts law necessity separately. Across all chains, one stage bond determines an upper reading on **6,588** occurrences. There are 30,865 determining bond occurrences, 26,327 with a third carrier outside the six named readings. Testing only the four defining bonds detects zero of them. [Decision](../decision.md) · [Method](../README.md) · [Determining bonds](step_paired.json)

   One example occurs on the third chain in round four of three-knot census entry 2. Read X, Y and Z as agreement on (3,4,8), (11,13,15) and (0,9,12). On 13,110 allowed states their word counts from 000 through 111 are **8,586, 1,968, 942, 186, 1,206, 90, 132, 0**. Every reading varies at a fixed value of each source knot. XYZ is a lower bond, and its first two values determine both X AND Y and X OR Y. The chain passes the frozen test. [Direct truth table](local_witness.json)

2. **Narrowing — start counts and chain selection.** In the decision table replace the rival entries “816 (99.9%)” and “878 (12.4% of all)” with **“817/817 at round six”** and **“873/7,075 at some reached round”**. Retain the original figures in a row labelled “Frozen test, first three chains”. Use the same replacements in the ticket status beginning “under the cuts 816 of 817” and the object entry beginning “817 starts still grow”. With every gate but only the first three chains, the counts are **816** and **872**. The sixth of 61 chains supplies the round-six witness on three-knot census entry 2. No stage reached the 1,000-chain cap (maximum 314). The 3,932 selected occurrences represent 2,840 distinct chains when counted once per start. In the ordinary “some round” cell write “4,213/7,075 by six”. The earlier census directly measured round six, and the matched replay verifies the same numerator over the full window. [Decision](../decision.md) · [Ticket](../../../tickets/CHAIN-LAWS-20261127-001.json) · [Object entry](../../../docs/OBJECTS.md) · [Round and first-appearance counts](step_summary.json)

3. **Narrowing — survivor selection.** Replace “Whether a law keeps growing appears to be what decides it: the starts that grow longest build chains of eight” in the decision and “the step comes with long growth under all three recorded laws” in the goals row with **“On the same 817 survivors, ordinary growth gives 816 full witnesses and either cut gives 817. Ordinary growth also gives 3,397 round-six witnesses on the 4,294 initially funded starts that stop early under the cuts.”** Of the 17.57 percentage-point difference, selecting the survivor identities accounts for **17.45 points** and changing the law adds **0.12 points**. In 815 of the 817 matched pairs, the complete ordered round-six supports agree. Five-knot census entry 1591 has 19 rival chains and zero ordinary chains at equal duration. [Decision](../decision.md) · [Goals checkpoint](../../../docs/RESEARCH_GOALS.md) · [Matched counts](selection_counts.json)

   The observation window accounts for most of the difference in the opposite direction when all starts get one vote. Stop observing each ordinary start at the last round its rival reached. The ordinary count drops from **4,213 to 872**, and either cut gives **873** in those same windows. All 872 qualify under both. Of those, 871 first qualify in the same round, and five-knot entry 1675 qualifies one round earlier under the cuts. [Matched observation windows](selection_counts.json)

4. **Narrowing — agreement between laws.** Replace “The two rival laws agree on every count here. They differ only in when 48 starts stall” with **“The rivals give identical ordered supports and chains on all 1,325 chain-positive stages. Their first-round grants differ on 48 starts.”** Each of those 48 has one join that stays live and short of funding under one-fewer, while the arity floor gives it zero fresh distinctions. They stall after rounds one and three respectively. The laws reach **4,506 versus 4,554** second rounds and **3,227 versus 3,275** third rounds. All 96 additional stages are chain-free. Zero chain-bearing stages could distinguish the rivals' readings. [Decision](../decision.md) · [Grant and support comparisons](growth_counts.json)

5. **Not a block — credit.** After “So the step is not peculiar to ordinary growth” in the decision, credit the earlier closure census for the 817 survivors and 48 differing histories, and its referee for a four-clause witness under both cuts. On five-knot entry 5246, the same six earlier readings admit **468** assignments with upper 111 under ordinary growth and zero under either cut. The four-clause referee identified the bare chain. The preceding closed twelve-knot example used eight clauses and a different upper reading. The new result is the rival frequency for the carried chain. The guide already scopes its 4,213 to ordinary growth. [Earlier rival witness](../../CLOSED-BY-CUTS-20261127-001/referee-R1/report.md) · [Recount](local_witness.json) · [Bare chain](../../FOUR-CLAUSE-20261127-001/referee-R1/report.md) · [Eight-clause witness](../../RING-BOND-20261127-001/referee-R1/layer_notes.md) · [Index searches](record_counts.json) · [Guide](../../../publication/knotlab/INTUITIONS.md)

## What was not run

Other upper functions, unrestricted carrier choices, steps on chain-free stages, larger census classes and chains after round six were not searched. Round-seven funding was checked separately. These frequencies concern the carried pattern within six rounds.

## How it was checked

Run `bash research/CHAIN-LAWS-20261127-001/referee-R1/replay.sh` from the repository root. It includes the timing pilots and individual commands. We reused the earlier independent ordinary proposal and applied each rival allowance on its actual preceding stage. The replay matched **222 ordered support arrays and 639 birth records** on 36 earlier sources. The new chain detector matched all **2,808** earlier first-three chain identities. The ordinary comparison regrew **37,741 stages** and verified all 4,213 archived round-six chain identities. [Replay](replay.sh) · [Growth](growth.py) · [Earlier proposal](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py) · [Matched-start code](selection.py)

The new single-bond check covers all disjoint triples of two- or three-distinction agreements. It searched every third carrier when both carriers of an upper function were present. For other triples, whole-stage state pairs certified which raw distinctions a determining bond must cover. Exact stage tests resolved the candidates left by the witness search. Of 53,098 remaining triples counted by chain and upper function, zero were eligible bonds. On a separate four-knot control the search recovered all 32 determinations of this kind. [Full method](step_checks.md) · [Completeness and controls](step_nonpaired_notes.md)

Both freeze hashes match at freeze, close and review. No result chunk was in the freeze, and all sixteen closing chunks match the raw files. The record shows no later change to a threshold or carried reading. The study records no advisor consultation. The linked `post/` is the earlier four-clause study's bare-chain replay. All four rows match the ordinary referee's independent replay. [Freeze and prior-work audit](record_counts.json) · [Earlier post data](../../FOUR-CLAUSE-20261127-001/post/chain_replay.json)

| Scope | Verdict | Evidence |
| --- | --- | --- |
| Six-round starts | Confirmed with fixes | 817 survivors and 873 starts overall |
| 95% complete-chain prediction | Block | 2,395 of 3,932 qualify |
| G17 and G18 | Census measured and laws compared | One extra qualifying start at equal duration |

**Next step:** Research directions. STOP this referee round. Row 1 gives the action for the closed study.

| # | Direction | Payoff | Concreteness | Discriminator | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Correct the study summaries | 3/3 | 3/3 | Match their gates and denominators to the recount | Edits specified |
| 2 | Explain the extra witness and earlier onset | 2/3 | 2/3 | Restore the differing grant on each start and check its witness | Deferred |

**Corrections:** Block on L3 for the complete step. Narrow the start counts, duration explanation and agreement between laws. Credit the earlier witnesses.  
**Goals:** G17 gains a census frequency. G18 gains a matched-start comparison.  
**Assumptions:** One vote per census entry and a six-round horizon.  
**Scaffolds:** The rival grants, carried eight-knot pattern and upper roles. The recount removes the three-chain selection limit.
