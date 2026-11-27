# All 351 stages above the cutoff

The unrestricted search found **zero boxes on all 351 stages**. These were 28 first-round and 323 second-round stages of 323 sampled starts, with 20–38 distinctions. Every set of source laws was eligible, including disconnected sets and sets omitting carrier members. The result establishes the two negative growth predictions on these particular stages under the frozen six-carrier reading. [Stage results](large_stages.json)

| Check | Independent count |
| --- | ---: |
| Signed triple incidences certified to exclude a word, before requiring disjoint alternatives | 12,159,949 |
| Stages on which repeated disjoint-alternative checks eliminated every triple | 319 |
| Surviving triple incidences on the other 32 stages | 4,031 |
| Stages on which two surviving triples used six disjoint carriers | 2 |
| Pairs of such triples on those two stages | 1,632 and 2 |
| Pairs admitting any matching that supplies all eight required clauses | 0 |

The two stages in the penultimate row are the second rounds of the census entries numbered 1,573 and 2,045. The search counted sufficient certificates for absent words. Some of the triples in its lists have a reading determined at one source knot or exclude multiple words. Retaining them enlarges the set searched. The 12,159,949 figure counts candidate incidences across stages and cannot be used as a full-stage bond count. [Recheck of all 32 stages](large_controls.json)

## Why the search includes every eligible triple

Write `C₁, C₂, C₃` for three disjoint carriers of two or three raw distinctions. A signed reading requires its carrier to agree (value 1) or to be not all equal (value 0). Suppose the full source stage excludes one word of these readings and allows the other seven. Choose an inclusion-minimal subset `H` of source laws which, together with the three requirements for that word, has no allowed state. Keep the carrier distinctions available, including those held by no law in `H`. Let `h` be the number of source laws in `H`, let `V` be the distinctions they hold, and write `d = |V|`.

1. **Each carrier meets V in at least two places.** Dropping any one of the three requirements permits a state even on the full source stage, because the two retained values occur. If a carrier required to agree met V in at most one place, its unheld places could copy that value. If a carrier required to disagree had even one place outside V, that place could be set opposite to another member. The carriers are disjoint. Neither extension changes the other two readings. Both would give a state for the excluded word. Thus every negative carrier is wholly in V. A positive carrier may have one place outside V.
2. **Every distinction held by just one law of H belongs to a carrier.** Otherwise delete that law, take a satisfying state of the remaining laws and the three requirements, then restore the law by setting its private distinction opposite to one of its other places. Consequently there are at most nine such distinctions.
3. **There are at most h + 6 distinctions in V.** For every positive carrier identify the members of `Cᵢ ∩ V`. Add one not-all-equal law for each entire negative carrier. All resulting laws are ordinary unsigned not-all-equal laws. No substitution negates a distinction. Repeated names within a law after identification can be reduced to a single occurrence of each name. A one-place law has no allowed state. The compressed family remains unsatisfiable. Each source law is needed by minimality of H. Each added negative law is needed because dropping that reading gives a full-source solution for the other two requirements, respecting all positive identifications. This establishes inclusion-minimality on the compressed family, including its added laws.
   
   For a finite inclusion-minimal unsatisfiable family of unsigned not-all-equal laws, the number of occurring distinctions is at most the number of laws. Form its real incidence matrix, with a 1 for each distinct member of a law. More columns than rows would give a nonzero vector in its kernel. Every law meeting the support of the vector contains both a positive and a negative entry, since its row sum against the vector is zero. Assign a bit by sign on that support. All touched laws hold. At least one law is touched because the columns are occurring distinctions. The untouched laws are a proper subfamily and therefore admit a state, which completes the assignment on the remaining variables. This contradicts unsatisfiability.
   
   The compressed family has `d − Σpositive (|Cᵢ ∩ V| − 1)` occurring distinctions and `h + number of negative readings` laws. Each positive contribution is at most two. Each negative reading costs one new law. Hence `d − h ≤ 6`. More precisely, if `k = Σ |Cᵢ ∩ V|`, then `d − h ≤ k − 3`, because each negative carrier has at least two members.

The search enumerates **every** subset H of the actual source laws passing these bounds. It enumerates every possible union of six to nine carrier members inside V containing all private distinctions, then every partition of the union into three pairs or triples. All positive and negative choices are tried. A truth table checks that the three requirements are impossible on H, that each two of those requirements can hold, and that deleting any law of H permits them. The first bit can be fixed to zero because every law and reading is unchanged under a global complement. If a positive carrier has a third member outside V, a state after deletion extends by copying the common bit there. The checks therefore retain the restriction of every qualifying full-stage triple to its minimal H. The ordering used to cache small tables retains the complete list of holders of every distinction and changes only how often an isomorphic table is built. [Enumeration](large_cores.py)

The candidate list expands each retained positive pair to itself and to every three-place carrier containing it on the full stage. A positive value of any extension forces its pair to agree. Other signed carriers stay as they were. Thus each returned word is indeed absent on the full source. Any full carrier contained in a single knot is a function of that knot and is discarded. Disjointness is required of the three resulting carriers. Other whole-stage tests for a bond can only delete candidates. Hence the list includes every eligible one-word first bond, with its correct sign, even if its shortest source certificate omits members or uses separated laws. [Candidate construction](large_search.py)

## Why every box survives until the final join

In a box, every signed triple can replace each one of its readings with its disjoint partner and remain a signed triple. The search repeatedly deletes a triple if any one of those replacements is unavailable. Induction on the number of deletions preserves all eight members of a box. The main join enumerates disjoint partners for the least signed reading of the six and looks for the other four readings in their common triples. Each pair of those remaining readings assigned to different upper pairs must occur with both of the first pair. The join requires the four combinations and disjointness within the remaining two pairs.

A second join directly chooses two surviving triples whose six carriers are disjoint. It tries all six matchings between them and checks membership of all eight transversals. Every box supplies such an opposite pair. This check independently gave zero on all 32 stages with any surviving triples. On the known closed twelve-knot example, both joins find the same eight structural boxes when the available source certificates are deliberately limited to subsets of at most three knots. The unrestricted box total on that source is a separate question. [Two joins and controls](large_controls.json)

## Where the local count missed actual bonds

The archived opportunity threshold was at least twelve distinctions and eight bonds. Only two of the large stages fell below eight in the archived search. Independent raw-state constraint checks first exhibited eight distinct eligible first bonds in each. Exhausting their structural lists then gave the following counts. For each accepted bond, the seven other words all occur. For **each** source knot and **each** reading, two allowed states have equal bits on that knot and opposite reading values. [Eight witnesses per stage](large_controls.json) · [Complete one-word bond counts](large_low_bonds.json)

| Stage | Knots | Distinctions | Archived local bonds | Whole-stage one-word first bonds |
| --- | ---: | ---: | ---: | ---: |
| Second grown round of census entry 32 | 13 | 34 | 6 | 12,486 |
| First grown round of census entry 2,547 | 9 | 20 | 0 | 3,100 |

For example, the carriers `(0,1,3)`, `(2,12,13)`, and `(4,8)` on that first-round stage miss exactly 111. Every member of every carrier in the two complete counts changes its reading under a single allowed raw-bit change, covering 6,450 and 1,991 carrier-member incidences respectively. The coarse threshold count for the sample is **1,693**, comprising 1,342 fully searched stages and all 351 larger stages. Six disjoint eligible carriers entering all eight required triples is a stronger opportunity condition.

## Checks and scope

The earlier independent ordinary-growth rule supplied each stage from the archived start arrangements. All reproduced knot and distinction counts agree with the saved stages. Direct enumeration of allowed states and single-knot determination on the source ring and its first two rounds recovered all **0, 9 and 411** eligible single-word bonds in the structural list. On the second grown round that list also contained 171 other signed triples, illustrating its use as a superset. A four-knot source with repeated shared distinctions supplied two bonds excluding multiple words. A disconnected test supplied none. Direct enumeration confirmed every listed absent word on all five controls. On the closed twelve-knot witness all eight named lower clauses were recovered, including the six with disconnected source laws. All eight needed at least one carrier completed by a distinction outside its three certifying source laws. Each single-clause erasure destroyed the named box. A mixed-sign synthetic control and an all-positive control also lost the box on all eight single erasures. [Controls](large_controls.json)

The result covers the 351 stages above the archive's cutoff only. The number of all first bonds on all 351, other upper readings, stages beyond the sample or beyond its growth rounds, and the selection of any reading by the growth law were not run here. A separate check recounts the archived 2,065 full searches.

## Rerun

From the repository root, run one command at a time. The first five stages took under one second together in the timing run. The stage with 38 distinctions took 0.76 seconds, using 155,208 KiB. The full reconstruction took 39.13 seconds summed over stages and peaked at 202,372 KiB. [Five-stage timing](large_pilot.json) · [Largest-stage timing](large_pilot_largest.json)

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ref=research/UPPER-GROWN-20261127-001/referee-R1
.venv/bin/python -B "$ref/large_search.py" --count 5 --output "$ref/large_pilot.json"
.venv/bin/python -B "$ref/large_search.py" --first 69 --count 1 --output "$ref/large_pilot_largest.json"
.venv/bin/python -B "$ref/large_search.py" --output "$ref/large_stages.json"
.venv/bin/python -B "$ref/large_controls.py" --pilot --output "$ref/large_controls_pilot.json"
.venv/bin/python -B "$ref/large_controls.py" --output "$ref/large_controls.json"
.venv/bin/python -B "$ref/large_low_bonds.py" --limit 128 --output "$ref/large_low_pilot.json"
.venv/bin/python -B "$ref/large_low_bonds.py" --output "$ref/large_low_bonds.json"
```
