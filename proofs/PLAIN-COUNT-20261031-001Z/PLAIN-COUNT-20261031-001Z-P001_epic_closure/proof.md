# Closure of the counting-without-signs epic

Status: Proved

Ticket `PLAIN-COUNT-20261031-001Z`, 2026-10-31. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes
no new claim. The decision note is `research/PLAIN-COUNT-20261031-001/counting_without_signs.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A long edge with k capped pairs acts by 9^k (P₊ + tP₋), t = (−1/3)^k; with L of them the count is 9^{kL} q(t), and q(−1) is the signed count (q(1) the count with the signs dropped). | standard technique (interpolation) | A-P001, Lemma 1 |
| 2 | Long edges inside planar pieces keep the Pfaffian certificate; the soft crossing switches to 2 + 4 negations, the exhaustive minimum per page. | new (elementary) | A-P001, Lemmas 2–3 |
| 3 | Counting proper 2-colourings of 3-regular 3-uniform hypergraphs whose incidence graphs are Pfaffian is #P-hard; 9·#col(K₃,₃) = 54 is recovered from 100 plain Pfaffian counts. | new (no overlap found; folklore risk moderate) | A-P001, Theorem 4, Corollary 5 |
| 4 | Every planar cubic bipartite graph has at least six square faces and at most five meet a square, so every plain page is twisted. | new (classical ingredients) | B-P001, Lemma 1, Theorem 2 |
| 5 | In a plain cubic Pfaffian brace every trisum square has three twisted branches, and no root is good. | new (no overlap found) | B-P001, Corollary 3 |
| 6 | A plain non-colourable system has only nice cycles of length 2 mod 4; the Heawood graph is the only brace whose plain system is not 2-colourable. | classical form (Little; Vazirani–Yannakakis); likely known (Robertson–Seymour–Thomas) | B-P001, Lemma 4, Corollary 5 |

## Recommendation

**Continue**, as a fresh epic: counting on plain braces (2/3).
- **The finding behind it.** All 2500 junctions of pairs of plain pages are non-matchgate, yet none is a crossover.
- **The question.** Decide whether plain cubic Pfaffian braces are #P-hard to count, or hide another tractable structure.
- **Status.** Deferred to the owner. The decision note has the full assessment.
