# Reading a growth from its start on pieces with a cycle, and the twin exception afresh: what stands

Epic `CYCLE-READ-20261127-001` (G17 with G1; at the coordinator's pick after `GRADED-ORDER-20261126-001`; register entry
A307), closed 27 November 2026. Computed, frozen with the advisor's review before any start was scored; referee pending.
[The note](README.md)

## What stands

1. **Pieces with a cycle are read (computed, frozen).** The node reading (the start's core births built by Lemma R's
   round rule from the round-1 groups and offshoots, chains by `late.py`'s terms, a relay exactly when the core finishes
   with one last birth) agrees in every round read under both laws on all 122 predicted starts with a piece with a cycle
   and no chained twins, including the late-views study's six-knot cycle starts it could not predict. Its cores finish
   on most pieces `late.py` counts as a cycle (126 of 159); 7 do not finish by rank 25 and are read with no relay.
2. **The twin exception holds afresh (computed, frozen).** On fresh samples of the standard `tree+` weighting at nine
   knots and the scaffold `tree+s50` at eight, all 263 starts without chained twins agree (118 with chains, where the
   unproved chain counting is tested), and all 42 scored starts with chained twins differ under both laws; with Part 1's
   11, every chained-twin start scored differs, first at the round equal to its twins' least rank.
3. **How often a core is unending** (counted, cap 5,000 core births): never in these draws under `grow` at seven to nine
   knots or `tree+` at seven and eight; 0.4% of accepted `tree+` draws at nine knots and 1.8% at ten; 1.1% and 3.4% under
   the scaffold at seven and eight; 24 of the 159 cycle starts. Every one seen is explosive.
4. **The advisor's review was right in every case it named.** The first-coded relay (by `late.py`'s count) and chain
   count (points as sets on a core that does not finish) miss exactly the three starts it named, at the rounds it named.

**Not shown.** The chain counting as a theorem; chains on a core that does not finish (two starts), which need the
unrolled map's copies; unending cores; the twelve chained-twin starts whose growth did not finish in two minutes; the
caps varied.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — cycle pieces, the fresh twin test, unending cores | **Status:** Successful | All nine frozen predictions held on fresh samples of two weightings |
| Local direction — reading a growth from its start alone | Continue | The only exception seen is chained twins, now tested fresh; the chain counting is the unproved step |
| Broader exploration — what a local reader keeps of a start | Capability gained | Pieces with a cycle are read without growing, except chains on a core that never finishes |
| Long-term goal — G17 with G1 | Capability gained | The late view of every read start without chained twins is read off the start, on 385 fresh starts |

**Next step:** Continue — #1, the coordinator's sequenced #3, starts now

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the chain counting on node cores without chained twins | 3/3 — turns the computed reading into a theorem | 2/3 — R2's induction gives the core; `CHAIN-IDENT` and `DOUBLE-IDENT` give the tree case | Extend R2's two induction properties to chain births and their fresh counts → a proof, or a start without chained twins that fails | Selected |
| 2 | Read chained twins: count the mixed group {A, B, C′, D′} | 2/3 — removes the last exception seen | 2/3 — the mechanism and the first round are known | Add the group the chain creates to the core's round rule; test on the 53 chained-twin starts → every round, or the next exception | Proposed |
| 3 | Chains on a core that never finishes: copies from the unrolled map | 2/3 — completes cycle pieces | 2/3 — `RING-IDENT`'s clusters carry the copies | Count chained-point copies per node by lifting to the unrolled map; test on draw 109 and fresh rings with chains → exact, or the case it misses | Proposed |
| 4 | The Helly test of unending cores | 1/3 — explains Part 3's counts | 3/3 — the draws are in hand | Count groups of three or more in the first rounds of Part 3's draws → a separation, or none | Proposed |

**Corrections:** none from this study; the predecessor's referee R2 added one entry (two Blocks: the core reduction needs
no chained twins, and the rank checker skipped its ends), folded in before this study's freeze.
**Goals:** checkpoint row added (G17 with G1; capability gained).
**Assumptions:** A307 entered (the cycle starts, two twin weightings, the count caps, the horizons).
**Scaffolds:** the weighting `tree+s50`, the buckets, the seeds, the caps (5,000 families, 250,000 pairs), rank 25, the
two-minute growth limit. T1 to T3 hold under the standard weighting and the scaffold alike, so they are about the
reading, not the weighting; the caps decide which starts are read, were not varied, and are expected to go when the
unrolled-map count replaces them.
**Advisor:** consulted before the freeze; its two faults, its label bug and its count-cap advice were taken, and its five
predicted misses of the first-coded reading all held.
