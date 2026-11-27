# What the node cores over the cap are: what stands

Epic `CAPPED-CORES-20261127-001` (G17 with G1; after `TWO-EXCEPTIONS-20261127-001`), closed 27 November 2026. Computed,
structure only, predictions committed before the certificates were read; referee pending. [The note](README.md)

## What stands

1. **Capped cores grow steadily; almost none is shown to finish (computed).** Of 221 certified capped cores (the first
   40 a size under `tree+` at seven to eleven knots, and the one under `grow`), 219 grow by a steady factor of 1.17 to
   2.52 births a rank to 50,000 births; one nine-knot core finishes by the subset pattern after 2^84 − 85 more births;
   none repeats. C1 to C3 held.
2. **They sit on pieces with a cycle (computed).** 217 of the 220 `tree+` ones are on pieces `late.py` counts as a cycle.
3. **The subset pattern is a finishing certificate (proved in the note):** a rank whose m births all share one parent is
   followed by all their sets of k + 1, and the core ends after 2^m − m − 1 more births.

**Not shown.** That the growing cores are unending (no certificate of unbounded growth); the uncertified capped starts
(1,433 of 1,654 distinct); repeats beyond 50,000 births.

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

**Corrections:** none.
**Goals:** checkpoint row added (G17 with G1; capability gained).
**Assumptions:** none new; the limits (50,000 births, rank 60, a pair guard of 2,000,000) are stated with each class, and
the population is the counts' draws.
**Scaffolds:** the limits and the prefix of 40 a size; "unresolved" depends on the limits, the three certified classes
do not.
**Advisor:** not consulted (its usage limit was reached earlier in the session).
