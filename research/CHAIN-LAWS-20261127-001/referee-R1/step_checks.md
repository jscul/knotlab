# How the carried readings were checked

Both rival laws give the same 1,325 chain-positive start and round pairs. For every pair, the entire ordered list of support laws and every ordered chain agree across arms. The computation therefore checks 26,373 chain occurrences once and counts them separately under each growth law. Of these occurrences, 3,932 belong to the first three chains at a stage and 22,441 fall later. The 26,373 occurrences represent 21,720 identities when each chain's ordered knot list counts once per start across rounds. [Start and round incidence](step_incidence.jsonl.gz) · [Stage inventory](step_inventory.json)

| Gate per rival law | First three per stage | Remaining chains | All chains |
| --- | ---: | ---: | ---: |
| Frozen test | 3,919 | 22,396 | 26,315 |
| Frozen test and all eight laws needed in each role | 3,918 | 22,391 | 26,309 |
| No stage bond alone determines an upper reading | 2,398 | 17,387 | 19,785 |
| Frozen test and no such determining bond | 2,396 | 17,371 | 19,767 |
| Every gate in all three roles | 2,395 | 17,366 | 19,761 |
| Every gate in at least one role | 2,396 | 17,371 | 19,767 |

Under every gate in all three roles, the first three chains supply a witness on 816 of 817 surviving starts at round six and on 872 starts at some round. The full search supplies a witness on all 817 survivors at round six and 873 of 7,075 starts at some round. A chain omitted from the frozen prefix supplies a witness on six additional start and round pairs. On the three-knot census entry 2, the fifth of 25 chains passes at round five and the sixth of 61 passes at round six. Searching all chains gives a complete witness on 1,304 of 1,325 chain-positive stages. [Start, stage and role counts](step_summary.json) · [Joined chain records](step_passes.jsonl.gz)

## Lower and upper words and individual law removal

The stage relation requires each support to contain both raw values. For a chain, the check carries the six named agreements to their identities in the stage and asks whether each of their 64 joint words extends to a full allowed state. Each three-reading projection is stored as a bit mask, with bit zero for 000 and bit seven for 111. In each of the three upper relations one named pair reads “both” and the other pairs read “either”. Seven allowed words imply four allowed words on every pair.

The frozen test also requires each of the six lower agreements to vary while the raw values of each single source knot stay fixed. Two complete copies of the source decide each test. With one chain law removed and every other stage law enforced, the check separately asks whether 111 can be restored in each upper relation. The eight masks in each output row follow the chain order. Within a mask the three bits represent the A, B and C choices of “both”. The frozen test and all 24 individual deletions are reported separately. [Reading and deletion rows](step_reading_rows.jsonl.gz) · [Checked against the frozen archive](step_frozen_counts.json)

Across all chains the four lower projections are exact in 105,434 of 105,492 tests, and all 79,119 upper relations are exact. No individual source knot determines a named lower agreement in 2,786,814 comparisons. No defining lower triple determines a named upper function in 632,952 comparisons. Removing one chain law restores upper 111 in 632,860 of 632,952 law and role tests. Direct raw-state enumeration checks the bare chain, a grown stage, and three constructed extensions that separately expose loss of a lower word, loss of an upper word, and loss of individual law necessity. [Direct controls](step_controls.json)

## How outside laws change the carried reading

One additional source law suffices with the chain for each of the 58 lower failures. On 42 occurrences at the three-knot census entry 2 and the five-knot entry 2030, the first A and first B readings cannot both hold. The additional law requires the two free places of the chain's first knot and the free place of its third knot to differ somewhere. This is the previously reported explanation from the ordinary-growth sample. [Ordinary-growth comparison](../../CHAIN-STEP-20261127-001/referee-R1/failure_rule.md)

The other 16 failures are every chain on the second and last grown round of five-knot census entry 3196. Each loses word 101 as well as 111 at one lower triple. For the first chain the two agreements on (4,6,10) and (0,1,3) cannot both hold. If they did, the source law on (0,3,4) would force the two common values opposite. The law on (0,1,2) would then force 2 equal to 4 and 6, violating the law on (2,4,6). In six further chains on the four-knot census entries 173 and 238, all four lower and all three upper projections survive, but deleting one chain law fails to restore upper 111 in one role. Three additional stage laws suffice for each of these six failures, and the search exhausted every smaller outside set. [Exact exclusions](step_exceptions.json)

## Every lower bond on the stage

An eligible lower bond uses three disjoint carriers, each an agreement of two or three raw distinctions. Its word set must be nonempty and proper, with all three pairs free. Every reading must vary at fixed raw values of each individual source knot. These requirements admit bonds missing several words.

For a named upper pair X, Y, any such bond containing X and Y determines both their conjunction and their disjunction. Every possible disjoint third carrier was examined. For a triple omitting X or Y, the second search first checks that each raw distinction in X or Y can change the upper reading in a single allowed flip. This requires every determining triple to cover every one of those raw distinctions. Further exclusions use pairs of explicit whole-stage states with identical lower values and opposite upper values, then a complete test of the remaining triples. Allowed sample assignments accelerate both searches. Every unanswered existence question goes to the whole-stage constraints. [Bonds containing both named carriers](step_paired.md) · [Completeness for other carriers](step_nonpaired_notes.md)

## Scope and reproduction

The upper exclusion itself follows from the four alternating lower clauses. These checks concern its whole-stage extensions, the lower and upper readings visible to one source knot or one lower bond, and the need for each chain law. The equal weighting of census entries and the separate weighting by chain occurrences answer different frequency questions. Other upper forms and later rounds remain open.

The inventory pilot used every 97th start, covering 73 of 7,075. The reading pilot checked all 228 chains on its 13 chain-positive stages, and a separate truth-table pilot covered the bare chain. Each main computation uses one process with all numerical library thread counts set to one and at most 1.5 GiB of address space. The check of disjoint triples missing a named carrier uses at most 1.25 GiB. The resource summaries record wall seconds and peak resident memory. [Replay script](replay.sh) · [Reading run](step_readings.json) · [Complete start and occurrence counts](step_summary.json)
