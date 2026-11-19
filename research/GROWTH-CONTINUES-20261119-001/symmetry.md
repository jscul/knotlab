# Symmetry screen of the sixteen starts

The archive screen found no roster permutation that carries every live
junction to a different noncandidate. The direct checks excluded every
such permutation on **69 of 75** archived stages across all sixteen
starts. Start-00 had five capped checks followed by a checked absence at
age 21 and a closed roster at age 22. All ten partnered controls gave
literal involutions with the required behavior. [Stage-by-stage record](../../artifacts/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/symmetry_archive.json)

At start-03 age eight, the 28,065 junctions have 28,053 distinct
profiles from their incident block sizes alone. Junction 0 is the sole
holder of its profile. Any permutation preserving the blocks fixes it.
The same invariant excludes the proposed symmetry at ages zero and
seven. The separate unary-parent persistence argument applies to
start-03.

| Start | Ages with a direct exclusion | Other ages screened |
| --- | --- | --- |
| 00 | 0–15, 21 | 16, 17, 19 and 20 hit the work cap. 18 hit the size cap. 22 closed. |
| 01 | 0, 8–10 | |
| 02 | 0, 8–9 | |
| 03 | 0, 7–8 | |
| 04 | 0–8 | |
| 05 | 0, 8–9 | |
| 06 | 0, 6–7 | |
| 07 | 0, 6–7 | |
| 08 | 0, 8–9 | |
| 09 | 0, 5–6 | |
| 10 | 0, 6–7 | |
| 11 | 0, 6–7 | |
| 12 | 0, 6–7 | |
| 13 | 0, 6–7 | |
| 14 | 0, 7–8 | |
| 15 | 0, 7–8 | |

The finite terminal paths for starts 00 and 04 also give a theorem-based
exclusion at every earlier funded stage. A displacing permutation
would persist under the joining rule and prevent closure. This
deduction covers the five capped stages of start-00. Along another
verified path, a later exact exclusion also rules out such a
permutation at an earlier stage from which the symmetry would have
persisted. The table gives the ages checked directly.

## Checks

The first profile of a junction records the multiset of its incident
block sizes and its open count when exact counts are available. Further
refinement records multisets of block and junction profiles across
incidences. Every roster permutation preserves each refinement. A
singleton profile class forces a fixed junction. An entire profile
class contained in some member's closed candidate neighborhood
also leaves that member without a permissible image. The screen found
64 singleton obstructions and four closed-neighborhood obstructions.
When opens are unavailable these obstructions use the maximal blocks alone.

On a remaining small roster the checker tests for a permitted
bijection between copies of each class and then searches colored
incidence automorphisms. Start-00 at age 15 was excluded by exhaustive
incidence search. The exact search used at most 240 incidence nodes
and 400,000 tested placements. A positive certificate must preserve the
literal block family and the open counts, and send every junction to a
distinct noncandidate. The partnered controls all preserve exact open
counts. The checker also supports replay at a noninitial stage from a
verified one-parent flag, since the block rule fixes group demand and
the open count is the maximum of demand, one, and three minus the
parent count. [Screen implementation](../../experiments/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/symmetry_check.py)

Direct permutation enumeration agreed on all 64 labeled graphs with
four junctions and on 144 smaller randomized cases of five to seven
junctions. A three-junction positive required an order-three
certificate. One regular asymmetric control exercised the exact
incidence search and agreed with an independent adjacency-automorphism
enumeration. The shared runner completed all 85 archive and partnered
rows without timeouts or memory errors. [Control results](../../artifacts/GROWTH-CONTINUES-20261119-001/GROWTH-CONTINUES-20261119-001-E001_checks/symmetry_controls.json)
