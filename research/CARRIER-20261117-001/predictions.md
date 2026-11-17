# CARRIER-20261117-001: predictions

Frozen at the commit that adds this file (its time is the freeze time). Disclosure: the threshold run on the 24 patterns (LONG_RUNNING
`CARRIER-A1`) was launched at 18:20 UTC, before this file was written; none of its outputs has been read (their files are not
opened before this commit). Seen before: the smoke on 8db5da810c00-73 (no bond of at most 5 at s = 5 and 6 at depth 11, already known
from KEEP-REACH's exact reading), and KEEP-REACH's results. The advisor was not consulted for this study's design: it reuses
KEEP-REACH's reviewed design, its search engine, and its classification of the 25.

Conjecture C′ predicts that each of the 25 eventually exceeds every bound; at depth 11 and s ≤ 6 the test can only see the first step.

- **P1 (the 13 whose top pair projections become products).** For each of the 12 besides 8db5da810c00-73, the certified search finds
  no bond of at most 5 members at s = 6 (L₁₁(3, 6) > 5), as for −73.
- **P2 (the 12 with an unexposed dependence).** For at least 8 of the 12, the search decides s = 6 within 900 s, and every decided
  one has no bond within its parent's bound (4 for the bace53f8f952 mutants, 6 for the ca1efb37ad88 ones).

A decided "yes" (a bond within the parent's bound at s = 5 and 6) is a candidate refutation of C′'s open direction, to be followed by a
search for a three-orbit structure that would bound it at every depth.
