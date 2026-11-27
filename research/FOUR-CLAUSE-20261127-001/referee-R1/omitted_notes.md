# All 211 omitted stages

Two omitted stages carry the four-clause step. Both are second rounds of different five-knot starts. Both starts have three three-place knots, one four-place knot and one five-place knot, with different meeting patterns. Each grows from 11 to 16 to 23 distinctions. Each second round has 12 knots, 14 four-clause patterns and 42 qualifying upper readings. All 84 upper relations have the seven words other than 111. Each needs two of five initial laws and six of seven birth laws individually. Removing any one of those eight restores 111. [Stage records, carriers and deletions](omitted_stages.jsonl)

| Population | Stages or starts with a birth-essential step | Number in population |
| --- | ---: | ---: |
| Omitted first-round stages | 0 | 18 |
| Omitted second-round stages | 2 | 193 |
| All omitted stages | 2 | 211 |
| Distinct starts represented among the omitted stages | 2 | 193 |
| All funded starts after including the authors' small-stage result | 3 | 426 |
| All sampled starts after including the small-stage result | 3 | 600 |

The omitted-stage frequency is **2/211 (0.948%)**, an exact count of this finite population. The two new starts, census entries 2439 and 3777, already had their 16-distinction first rounds in the authors' denominator. Holding the original 408 starts fixed and including their larger stages gives 3/408. Applying the original stage cutoff gives the frozen 1/408. Extending both coverage and denominator to all starts reaching a grown stage gives 3/426 (0.704%). [Counts and weighting](omitted_summary.json)

## Why the search is complete on these stages

The enumeration uses the earlier bound on the number of distinctions in a minimal set of source laws excluding a word. It implements the bound and all subsequent checks afresh. Each stage comes from the archived census start and the earlier independent ordinary-growth rule. The enumeration reproduces the sizes, numbers of knots, funded rounds and cutoff status of all 600 sampled starts. [Earlier bound](../../UPPER-GROWN-20261127-001/referee-R1/large_notes.md) · [Growth rule](../../NAE-LAYER-20261127-001/referee-R1/growth_rule.py) · [Search implementation](omitted_search.py)

1. Consider three disjoint carriers with two or three members each. Fix a word absent from the stage although each pair of its signed readings can occur together. Choose an inclusion-minimal set of source laws H that excludes that word together with the three signed conditions. Write h for its law count and d for the number of distinctions its laws mention. Every carrier meets these distinctions in at least two places. A carrier required to agree could always be satisfied if it met H in at most one place. A carrier required to disagree could always be satisfied if even one of its members were outside H. These extensions respect the other two disjoint carriers, whose two conditions can hold together. Every distinction used by exactly one law in H also belongs to a carrier. Otherwise one could erase its law, take a state satisfying everything that remains, and change that private distinction to restore the law. There can therefore be at most nine such private distinctions.
2. Within H, identify the members of each carrier required to agree. For each carrier required to disagree add its own not-all-equal law. Positive carriers may have one member outside H, which can always copy their common value. Consequently the reduced system has no allowed state. Each source law is needed by the choice of H. Each added law is needed because the other two signed readings occur together on the whole stage. In any such minimal inconsistent set of unsigned not-all-equal laws, the number of occurring variables is at most the number of laws. To see this, put one 1 per distinct member in the real incidence matrix of each law. More columns than rows gives a nonzero vector in the kernel. Every row meeting its nonzero coordinates contains both signs. Assign bits by these signs. Any untouched rows are a proper subset and can be satisfied independently, a contradiction.
3. A positive carrier meeting H in b places removes b−1 variables by identification. A negative one adds one law. Thus d−h is bounded by the sum of those contributions, at most six. If k carrier members lie in H, the same sum is at most k−3. The code examines every source-law subset satisfying these bounds, including disconnected subsets. It takes every possible set of six to nine carrier members in H containing every private distinction, every partition into three pairs or triples, and every sign choice. It tests exclusion, all three pair projections at the prescribed values and every single-law deletion by truth table. Global complement allows one raw bit to be fixed to zero. The cache key records every holder of every raw distinction. These restrictions retain a certificate for each eligible missing word.
4. Extend each positive two-member restriction to itself and to every triple containing it. The excluded word stays excluded under a stronger agreement. Discard a final carrier contained in a single source knot, since that knot directly determines it. Require the three final carriers to be disjoint. Each resulting signed clause really excludes its indicated word. Some clauses can exclude further words or have a reading determined at a source knot by the allowed states, so these lists are supersets of the eligible lower bonds.
5. At each signed reading of a clause in a four-clause pattern, one other clause must share exactly that reading. Its other two carriers must be disjoint from the first clause's other two carriers. Iteratively discard a clause if any of its three readings lacks such a second clause. All four clauses of any real pattern survive every pass, by induction. Of 6,983,469 signed candidates across 211 stages, 62 survived. They belong to two stages, 31 each.
6. Choose the least of a pattern's six signed readings. Denote its two clauses by (a,b,c) and (a,d,e). With the four other carriers disjoint, both assignments of d and e to the two upper pairs are tested. In each assignment look for the same remaining signed reading x in both completions (x,b,e) and (x,c,d). Require its carrier disjoint from all five. Every pattern has such a least reading and two clauses and occurs in this join. The two possible sets of four lower clauses on the same three paired carriers remain distinct. No pattern cap is applied. The 62 retained signed candidates produce 28 patterns.
7. For every candidate choice, require exactly seven words on each defining lower triple, and compare pairs of allowed states agreeing on each single source knot to ensure every lower reading can vary there. Project the whole stage to the six signed readings. Try each pair in the “both” role, check all three upper pair projections, and require each upper reading to vary at some fixed value of each of the four defining lower bonds. Test every source law's individual deletion against upper 111. All 28 patterns pass for all three roles. [Exact conditional checks](omitted_semantics.py) · [Direct truth-table validation](omitted_semantics_replay.json)

## Stronger reading at any lower bond

For each new positive stage, 36 different upper recipes occur across its 42 roles. Every raw distinction in the two carriers of each upper recipe has two allowed source states in which flipping just that distinction changes the upper value. A lower triple determining the upper reading must therefore contain all those distinctions. The signed candidate lists before the four-clause disjointness test include every missing word of any pairwise-free lower bond, even if it excludes several words. In order of census entry, only 1,880 and 1,592 combinations of one upper recipe and one candidate triple survive this raw-member condition. For every one, two allowed states have the same three lower readings and different upper values. Thus all 84 upper roles also pass the stronger test at **every** stage bond. As a positive control on each stage, an upper recipe taking “both” on two readings from the same lower bond has 12 genuinely determining stage bonds. The search for witnesses uses 4,096 sampled allowed states with seed 739116 and sends each unresolved case to full enumeration. [All checks and raw flip witnesses](omitted_global.json)

## Controls and replay

On the twelve-distinction, seven-knot first round of census entry 61, direct enumeration of all 570 allowed states and all 187,046 triples of disjoint eligible carriers found 10,362 one-word lower bonds. The structural list contained all 10,362 with the correct signs, including seven different sign words, and 516 additional signed candidates. Every one of the 10,878 structural candidates excluded its stated word. The first two ordinary rounds of a three-knot start gave all 9 and 411 genuine missing words, respectively. The closed four-knot control with repeated shared distinctions gave all four missing words on its two multiple-word bonds. The four-clause join agreed with direct four-clause selection on all 256 subsets of the eight possible transversals of three disjoint pairs. Thirty subsets contained one pattern and one subset contained both orientations. The other 225 contained none. A control with overlapping carriers yielded none. [Counts](omitted_controls.json)

All 211 omitted stages are included. Stage sizes run from 20 to 38 distinctions. The study stops at round two and restricts lower carriers to the frozen agreements on two or three distinctions. Lower-bond totals outside the controls and later rounds were not run. The per-stage times in the exact pass sum to about 55 seconds. The process peaked at 141 MiB. The largest-stage pilot with 38 distinctions took under one second.

Run these commands sequentially from the repository root. Each uses one compute process.

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 3000000
ref=research/FOUR-CLAUSE-20261127-001/referee-R1
.venv/bin/python -B "$ref/omitted_search.py" --structural-only --stage 5260 2 --stage 15 2 --stage 1283 2 --output "$ref/omitted_structural_pilot.jsonl"
.venv/bin/python -B "$ref/omitted_search.py" --structural-only --output "$ref/omitted_screen.jsonl"
.venv/bin/python -B "$ref/omitted_search.py" --all-patterns --stage 5260 2 --stage 2439 2 --stage 1283 2 --output "$ref/omitted_exact_pilot.jsonl"
.venv/bin/python -B "$ref/omitted_search.py" --all-patterns --output "$ref/omitted_stages.jsonl"
.venv/bin/python -B "$ref/omitted_semantics_replay.py" > "$ref/omitted_semantics_replay.json"
.venv/bin/python -B "$ref/omitted_global.py" --pilot
.venv/bin/python -B "$ref/omitted_global.py"
ulimit -v 1250000
.venv/bin/python -B "$ref/omitted_controls.py" --pilot
.venv/bin/python -B "$ref/omitted_controls.py"
.venv/bin/python -B "$ref/omitted_summary.py"
```
