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

**Predictions** (written before any certificate was read):

| # | Prediction | Fails when |
| --- | --- | --- |
| C1 | Under `tree+`, most certified capped cores at each size from eight knots are unresolved and growing (70%) | half or more finish or repeat at some size |
| C2 | At least one capped core finishes by the subset pattern at nine knots or more (50%) | none does |
| C3 | Repeating cores are at most 10% of the certified capped cores at each size (70%) | more at some size |
