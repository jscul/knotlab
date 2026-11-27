# What the node cores over the cap are: what stands

> **Referee report R1, 27 November 2026: refuted — Block on the headline counts, on "every one grows steadily", and on
> the proposed two-cycle condition; both certificates (subset finish, repeat) proved sound** ([the report](referee-R1/report.md)).
> - **Block: the counts.** The six run files hold 181 distinct starts, not 221 (20 + 40 + 40 + 40 + 40 + 1); 180 are
>   unresolved, one finishes by the subset pattern, none repeats. 1,473 of the 1,654 capped starts were not certified,
>   not 1,433. The growth range 1.17 to 2.52 is one window (the fourth root of the ratio four ranks apart, ending one rank
>   before the last); twelve pieces decrease somewhere and 87 of 184 have a last one-step ratio above 2.52.
> - **Block, and a new result: at least 127 of the 181 never finish.** The referee proved it with a certificate the study
>   lacked: mark each pair of a rank's births that share a parent with 0 or 1 so that every three births that pairwise
>   share carry an even sum and some closed walk an odd one; the round rule carries such a marking to every later rank, so
>   the core never ends. 131 pieces of 127 starts carry one at rank 1. One seven-knot start has births growing without
>   bound, by the exact factor λ with λ^7 = (λ + 1)^2.
> - **Block: the two-cycle condition is false.** That seven-knot start has one independent cycle; the proposed test fails.
> - **Narrowings.** The caps and their counting conventions are stated more precisely in the report; 177 of the 180
>   `tree+` starts sit on pieces counted as a cycle; the earlier finishing cores had 65,726 and 67,108,976 births (the
>   figures quoted were nodes, with the starting knots). Read this record with these changes.

Epic `CAPPED-CORES-20261127-001` (G17 with G1; after `TWO-EXCEPTIONS-20261127-001`), closed 27 November 2026. Computed,
structure only, predictions committed before the certificates were read; referee pending. [The note](README.md)

## What stands

1. **Capped cores grow; almost none is shown to finish (computed; R1: 181 starts, not 221, and at least 127 proved unending).** Of ~~221~~ 181 certified capped cores (the first
   40 a size under `tree+` at seven to eleven knots, and the one under `grow`), 219 grow by a steady factor of 1.17 to
   2.52 births a rank to 50,000 births; one nine-knot core finishes by the subset pattern after 2^84 − 85 more births;
   none repeats. C1 to C3 held.
2. **They sit on pieces with a cycle (computed).** 217 of the 220 `tree+` ones are on pieces `late.py` counts as a cycle.
3. **The subset pattern is a finishing certificate (proved in the note):** a rank whose m births all share one parent is
   followed by all their sets of k + 1, and the core ends after 2^m − m − 1 more births.

**Not shown.** That the growing cores are unending (no certificate of unbounded growth; R1 built one and proved 127); the uncertified capped starts
(1,473 of 1,654 distinct, R1); repeats beyond 50,000 births.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what the capped cores are | **Status:** Successful | Three certificate classes counted; steady growth on all but one |
| Local direction — how often a core is unending | Continue | A certificate of unbounded growth is the missing piece |
| Broader exploration — reading growth from the start | Capability gained | The limit of the proved reading is now located: pieces with a cycle whose cores grow |
| Long-term goal — G17 with G1 | Capability gained | Under `tree+`, the capped cores are measured and characterized by size |

**Next step:** Research directions — #1 or #2; the choice is the coordinator's

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Certify unbounded growth: a capped core's piece has cycle rank two or more, and its node core contains the unrolled map's clusters | 2/3 — turns "growing" into "unending" | 2/3 — `RING-IDENT`'s clusters and the cycle rank are in hand | Compute cycle ranks of the 219; prove clusters embed in node cores → a proof, or a growing core of cycle rank one | Proposed |
| 2 | A structure for births after a twin family or a lift split | 3/3 — reads the last exceptions | 1/3 | As in `TWO-EXCEPTIONS-20261127-001` | Proposed |
| 3 | Decide whether N1 and N2 imply N3 | 2/3 | 2/3 | As in `CHAIN-COUNT-20261127-001` | Proposed |

**Corrections:** one entry after R1 (three Blocks, one Narrowing, one Not a block).
**Goals:** checkpoint row added (G17 with G1; capability gained).
**Assumptions:** none new; the limits (50,000 births, rank 60, a pair guard of 2,000,000) are stated with each class, and
the population is the counts' draws.
**Scaffolds:** the limits and the prefix of 40 a size; "unresolved" depends on the limits, the three certified classes
do not.
**Advisor:** not consulted (its usage limit was reached earlier in the session).
