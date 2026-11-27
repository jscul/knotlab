# What the stage adds to the chain

**One extra three-place law explains all five checked lower failures.** The five occurrences use four chains on two starts. Across all 10,696 chain occurrences in the same six-round sample, the same law explains all 33 lower failures on 12 distinct chains. The three checked chains that pass the lower test while a law can be omitted have a different explanation. [Counts and cases](failure_rule_counts.json)

## The extra law

Number chain distinctions from 0 through 16. The first law uses $(x_0,x_1,x_2)$, the second uses $(x_2,x_3,x_4)$, and so on. The reading A0 reports agreement of $(x_3,x_4,x_5)$ and B0 reports agreement of $(x_0,x_1,x_{10})$. If both readings are 1, the first chain law forces $x_0=x_1\ne x_2$, and the second forces $x_3=x_4\ne x_2$. Hence $x_0=x_1=x_5$. The extra stage law requires these three values to be **not all equal**. This forbids A0 and B0 holding together. The triple (A0, B0, C0) now loses 110 as well as 111, and its first pair loses 11. The other three defining triples keep all seven words. The eight chain laws alone admit 110. One extra law therefore suffices and is minimal. [Exact extra-law subsets](failure_rule_counts.json)

| Checked exception | Extra words lost on (A0, B0, C0) | Upper 111 still absent after a chain-law deletion |
| --- | --- | --- |
| Four-knot census entry 90, round 4, chains 1 and 2, and round 5, chain 3 | 110 on all three occurrences. The last repeats round 4's first chain. | With B reading both, law 3 can be omitted. |
| Five-knot census entry 2030, round 3, chains 1 and 2 | 110 on both | With B reading both, law 3 can be omitted. On the first chain a second extra law on $(x_3,x_7,x_{11})$ also acts. Together the two extra laws allow law 7 to be omitted with A reading both. Deleting either extra law restores 111 in that test. |
| Five-knot census entry 3609, round 5, chains 1, 2 and 3 | None | Law 1 can be omitted with A reading both and law 2 with B reading both. The C role needs every law. |

In the last row two outside knots share a distinction $y$. Their laws are not-all-equal on $(x_0,x_1,y)$ and $(x_3,x_5,y)$. When the first pair agrees, $y$ must take its opposite value. When the second pair agrees, it imposes the same demand on $y$. This excludes 0011 and 1100 on $(x_0,x_1,x_3,x_5)$. Either outside law alone can always be satisfied at $y$. Both together preserve all 39 six-reading words of the intact bare chain, yet remove all restorations of upper 111 for the two deletions in the table. Over all chains there are eight such occurrences on four distinct chains at rounds 5 and 6. [All single deletions and minimal extra conditions](failure_rule_counts.json)

## Exact projection onto the 17 chain distinctions

Remove the eight chain knots, retaining the identities of their distinctions. Since a distinction has at most two holders, only the ten distinctions held once within the chain can occur outside it. On each connected part outside, those attachments are loose distinctions. A part with a ring completes every assignment to its loose distinctions. A part forming a tree misses two complementary loose words, with values agreeing at each holder and alternating between successive holders. If some loose distinction of the tree is outside the chain, every assignment to the attachments extends. A nonempty assignment can match at most one forbidden word and admits at least two completions. An empty assignment can be extended by any allowed word. If every loose distinction of the tree belongs to the chain, its two excluded words give one signed not-all-equal condition on those attachments. The parts have disjoint attachments and can be completed independently. The same calculation holds after deleting any chain law with the 17 distinctions retained. [Earlier tree and ring proof](../../NAE-LAYER-20261127-001/referee-R1/lemma_arguments.md)

Exactly 5,935 chain occurrences give the whole bare set of 13,122 chain assignments. Of the rest, 4,146 acquire one tree condition and 615 acquire two. Across all 10,696, exactly 9,478 retain the bare set of 39 words on the six agreements. For each lower reading, an allowed flip at an internal shared distinction changes that reading while preserving every outside knot. For a chain knot, direct grouping by its raw word tests whether the reading can vary. These checks cover every source knot on every occurrence. [Whole-stage counts](failure_rule_counts.json)

| Gate on the carried pattern | First three per stage | Remaining chains | All chains |
| --- | ---: | ---: | ---: |
| Chain occurrences | 2,808 | 7,888 | 10,696 |
| Four exact lower clauses and the study's upper and lower tests | 2,803 | 7,860 | 10,663 |
| Those gates and every law needed for all three roles | 2,800 | 7,855 | 10,655 |
| Those lower and upper tests, plus no determining bond among all 20 triples of the six chosen agreements | 2,603 | 6,875 | 9,478 |
| The preceding test and all eight laws needed in all three roles | 2,600 | 6,870 | 9,470 |

All 10,696 occurrences have seven upper words for each choice of “both” and pass the upper nonlocality check against each **defining** lower triple. The other 16 triples among the same six agreements contribute 1,192 additional bonds on 1,192 occurrences across 290 stages of 189 starts. Each determines an upper function for every choice of “both”. In the checked prefix, the same 201 occurrences on 192 stages of 137 starts are identified by the independent whole-stage solver. The 9,478 surviving occurrences are exactly those that retain the chain's full 39-word image. At least one choice of “both” still needs all eight laws in each. Across rounds 2 through 6, the numbers of growing starts with at least one chain meeting the stronger six-carrier test and needing all eight laws for **all three roles** are 6, 25, 81, 344 and 604. The two additional round-three losses are five-knot census entries 1446 and 2030. Bonds involving other carriers require a wider test. [Per-role, chain and stage tables](failure_rule_counts.json) · [Independent whole-stage comparisons](stage_readings_summary.json)

## A control that loses an upper word

A single extra law with a fresh distinction leaves the chain projection free of additional conditions. Every other single allowed extra law is a choice of at least three of the ten attachable distinctions. Of all 968 such choices, 20 spoil a lower clause and another 10 leave all four lower clauses intact while spoiling an upper relation. The result for the 33 actual lower failures describes the sampled ordinary stages. [All one-law extensions](failure_rule_one_law.json)

For example, require $(x_0,x_1,x_{15})$ to be not-all-equal. With B reading both, B = 1 gives $x_0=x_1=x_{10}$ and $x_6=x_{15}=x_{16}$, with opposite common values by the added law. C0 = 1 would set $x_7=x_8=x_9$, forcing $x_6=x_{10}$ by chain laws 4 and 5. C1 = 1 would set $x_2=x_{14}$, forcing $x_0=x_{16}$ by the end laws. Thus B = C = 1 is impossible. The upper image loses 011 as well as 111, while each of the four lower triples still has its seven words. This constructed extension uses nine three-place knots. Its occurrence under ordinary growth was not tested. [Upper word sets](failure_rule_one_law.json)

## Replay

The input is the independent stage archive with all chains, reconstructed using the earlier ordinary-growth rule. Its supports match the earlier named witnesses and every archived stage size and count. Each run below uses one process. The initial runs time 282 actual chain occurrences, three direct whole-stage comparisons and 22 single-law controls. [Stage reconstruction](recount.py)

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd research/CHAIN-STEP-20261127-001/referee-R1
py=../../../.venv/bin/python
"$py" -B failure_rule.py --pilot --out failure_rule_pilot.json
"$py" -B failure_rule.py --direct --pilot --out failure_rule_direct_pilot.json
"$py" -B failure_rule.py --one-law --pilot --out failure_rule_one_law_pilot.json
"$py" -B failure_rule.py --out failure_rule_counts.json
"$py" -B failure_rule.py --direct --out failure_rule_direct.json
"$py" -B failure_rule.py --one-law --out failure_rule_one_law.json
```

For a direct comparison, retain one representative of each complementary pair of assignments. A bare chain has 6,561 representatives. Each single-law deletion adds 2,187 distinct representatives violating precisely that law, giving 24,057 queries per occurrence. The check queried a whole-stage Boolean solver on every one of these assignments for each of 73 occurrences covering every observed list of outside conditions and every one of the 41 original-step or law-deletion exceptions. All 1,756,161 answers agreed. The projection and single-law runs each took less than two seconds. The direct comparison took under six seconds. [Direct comparison](failure_rule_direct.json)
