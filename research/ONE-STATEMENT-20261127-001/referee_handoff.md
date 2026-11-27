# Referee hand-off: ONE-STATEMENT-20261127-001

The note is [README.md](README.md) (parts frozen in order: `01938c1654` for (a), `5766f5c23b` for (d), with the cut at
`5f7eb36f7c`); the statement is [statement.md](statement.md); the decision is [decision.md](decision.md).

| # | Claim | Evidence class | Code | Data |
| --- | --- | --- | --- | --- |
| 1 | a1: of 840 bases of the relations among the nine facts, 20 keep two holders, 12 meet in a ring, one is the tree | computed, frozen | `checks_a.py` | `checks_a.json` |
| 2 | a2: removing any start law frees each four-place relation | computed, frozen | `checks_a.py` | `checks_a.json` |
| 3 | a3: on rings of 10, 4 and 4, "shorter" depends on the count (places, carriers, laws) | computed, frozen | `checks_a.py` | `checks_a.json` |
| 4 | a4: the advisor's three marked-loose pairs | computed, frozen | `checks_a.py` | `checks_a.json` |
| 5 | (b) the statement, and that the marked-loose agreement is entailed | argument (Whitney; `STATES-GROWTH-20261119-001`) | statement.md | |
| 6 | (c) the tree presentation as a start closes at round 3; the second layer gains two-place copies | computed | `recursion_c.py` | `recursion_c.json` |
| 7 | (d) under not-all-equal the reader's pair fixes the knots on 1,193 of 1,194 census starts read, and the families and tree on all; under parity the knots on 1,499 of 7,075 | computed, frozen | `nae_pres.py` | `frozen_nae.jsonl`, `frozen_parity.jsonl` |

**Points to press.** Whether the presentation search is complete (as many knots as the start; knots of at least three
places; connected) and whether a different count of knots changes (d); the entailment argument in the statement; a3's
three counts; whether "the states choose the knots under not-all-equal" holds past the census prefix; census 959.
