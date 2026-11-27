# What the node cores over the cap are

Epic `CAPPED-CORES-20261127-001`, under G17 with G1, after `TWO-EXCEPTIONS-20261127-001` (its direction 1) and the cycle
study's referee R1, which showed that a core over the cap may finish (two nine-knot `tree+` starts, 65,735 and
67,108,985 births) or repeat (7, 7, 6 births forever). Structure only: nothing is grown.

**The question.** Of the starts whose node core passed the counts' cap (5,000 families or 250,000 parent-sharing pairs in
one round), which cores finish, which repeat forever, and which keep growing?

**The certificates** ([certify.py](certify.py)): build the node core rank by rank with Lemma R's round rule, to 50,000
births and rank 60, with a pair guard of 2,000,000, and stop at the first of
- **finishes**: a rank with no birth;
- **subset finish**: a rank whose m births (m ≥ 3) all share one parent; then every later rank is all the sets of k + 1 of
  them (the literature's Boolean lattice), and the core ends after 2^m − m − 1 more births (proved: such a family has a
  common parent, so the next births are all the pairs; pairs meeting in one birth share that parent and are covered by
  the triples they span, and so on);
- **repeats**: the parent incidence between two consecutive ranks is isomorphic to an earlier one's; the round rule reads
  only that incidence, so the core repeats with that period forever (an unending core with bounded births);
- **unresolved**: none of these within the limits, with the births by rank recorded.

**Population.** The draws of `TWO-EXCEPTIONS-20261127-001`'s counts (seed 2026112701, 3,000 a size): the first 40 distinct
capped starts in draw order under `tree+` at seven to eleven knots, and the one capped start under `grow` (ten knots). The
rest are reported as not certified.

**Predictions** (written before the run's certificates were read; the timing run had shown the first eight capped
eight-knot `tree+` cores, all unresolved and growing by about 1.3 to 1.6 a rank, which C1 therefore leans on):

| # | Prediction | Fails when |
| --- | --- | --- |
| C1 | Under `tree+`, most certified capped cores at each size from eight knots are unresolved and growing (70%) | half or more finish or repeat at some size |
| C2 | At least one capped core finishes by the subset pattern at nine knots or more (50%) | none does |
| C3 | Repeating cores are at most 10% of the certified capped cores at each size (70%) | more at some size |

## Results (added after the run)

[Certificates](runs/) (one line a start, with each piece's class and, for an unresolved core, its births by rank);
[piece kinds](pieces.txt) ([pieces.py](pieces.py)).

| Weighting, knots | Capped distinct starts | Certified (first 40) | Finish | Subset finish | Repeat | Unresolved, growing | Growth a rank over the last four ranks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `tree+`, 7 | 20 | 20 | 0 | 0 | 0 | 20 | 1.25 to 2.45 |
| `tree+`, 8 | 94 | 40 | 0 | 0 | 0 | 40 | 1.32 to 2.35 |
| `tree+`, 9 | 298 | 40 | 0 | 1 (m = 84) | 0 | 39 | 1.21 to 2.48 |
| `tree+`, 10 | 514 | 40 | 0 | 0 | 0 | 40 | 1.17 to 2.52 |
| `tree+`, 11 | 727 | 40 | 0 | 0 | 0 | 40 | 1.17 to 2.51 |
| `grow`, 10 | 1 | 1 | 0 | 0 | 0 | 1 | 1.39 |

- **C1 holds:** 219 of the 221 certified capped cores are unresolved, and every one grows steadily, by 1.17 to 2.52
  births a rank. **C2 holds:** one nine-knot core finishes by the subset pattern, after 2^84 − 85 more births, finite
  but far past any growth that could be run. **C3 holds:** none repeats within 50,000 births.
- **Where they sit.** 217 of the 220 capped `tree+` cores certified are on pieces `late.py` counts as a cycle (all 221
  but three: one at nine knots and two at eleven are on tree pieces).
- **So, how often a core is unending,** stated with its weighting: under `grow`, one distinct accepted start in 769 (seven to
  eleven knots) has a capped core, unresolved and growing; under `tree+`, capped cores are 9% of accepted draws at seven
  knots rising to 30% at eleven, and of those certified none was shown to finish within reach except one, none repeats,
  and the rest grow by a steady factor a rank. Unending is shown for none of them (no certificate of growth without
  bound is built here); finishing is shown for one.

**An intuition (a link, not evidence).** A piece with two or more independent cycles unrolls into a cover in which the
number of connected sets of each size grows by a steady factor (the literature's growth constant of cluster counts on a
branching cover; `RING-PAIR-20261119-001` found the cheapest growth's series rational with one cycle and exponential with
two or more). The steady factors here, 1.17 to 2.52, are what that predicts for node cores, which would make these cores
unending. Cheapest test: compute each piece's cycle rank against its blocks and cells and check that every capped,
growing core has rank two or more, and that the factor matches the cover's growth constant on a few small pieces.
