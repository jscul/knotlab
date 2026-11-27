# How often does ordinary growth make the four-clause step one layer up?

`FOUR-CLAUSE-20261127-001`. `UPPER-GROWN-20261127-001`'s referee found a second form of the step one layer up. Take six
agreements on disjoint carriers in three pairs. Four bonds forbid one triple each, on (A0, B0, C0), (A0, B1, C1),
(A1, B0, C1) and (A1, B1, C0). Read one pair as "both hold at their forbidden values" and the other two as "either
holds", and the three upper readings cannot all hold. It found one on a sampled grown stage: census start 420 at round
2, the first stage it tried, with all six birth laws needed. This study measures how often ordinary growth makes it.

**Definitions** (`fourclause.py`). The pattern is the same from each pair's side, so each pattern gives three upper
relations. Each is read on the stage's allowed states for:
- its upper words;
- whether every two upper readings are free;
- whether some upper reading is a function of one lower bond's three readings;
- which laws are needed (removing the law lets the forbidden upper word occur).

A **step** is a relation that is proper (fewer than eight words) and free in pairs, with no upper reading read at one
lower bond. Checked on census start 420 at round 2: 4 patterns, all 12 relations are steps, all with a birth needed.

**Sample** (`census_four.py`). 600 census starts outside UPPER-GROWN's sample, its pilots and start 420 (seed 20261130).
Rounds 0 to 2 are read with the full search on stages of at most 19 distinctions. Larger stages are recorded as not
read. At most 60 patterns are read per stage.

## Frozen predictions

- F1. No start has a step at round 0. Census starts have at most 12 distinctions, so six disjoint carriers would have to
  be six pairs covering every distinction.
- F2. Of the starts with a round-1 or round-2 stage read, at least 5% have a step with a birth needed.
- F3. At least 90% of the steps read have exactly seven upper words.

**Scaffolds:** the four-clause form, the readings and carriers (A308, A309), the 19-distinction cap and the 60-pattern
cap. **Advisor:** not consulted (usage limit). **Compute:** about 20 seconds per start on average from the pilot, in 12
chunks, with a 6G memory cap and a 45-minute stop.
