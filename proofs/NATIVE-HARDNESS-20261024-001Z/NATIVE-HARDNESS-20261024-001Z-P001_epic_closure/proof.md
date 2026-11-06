# Closure of the hubs-and-memory epic

Status: Proved

Epic `NATIVE-HARDNESS-20261024-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/NATIVE-HARDNESS-20261024-001/hubs_and_memory.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | All 34 knots are coverable delta-matroids (the two parity knots even), as are all 155 nonempty three-place delta-matroids; the hub relation, all-equal on three places, is not a delta-matroid (degree set {0, 3}). | `candidate-local-delta` (finite census) | `NATIVE-HARDNESS-20261024-001A-P001`, Theorem 1 |
| 2 | With hubs, the 16 knots outside Schaefer's classes give NP-complete networks; this is the knot-level form of Tovey's boundary between two and three occurrences per variable. | Classical, applied; conditional on Feder and Schaefer | `…001A-P001`, Corollary 3(b) and (c) |
| 3 | In an unsatisfiable native network, every knot whose removal keeps the network connected allows exactly half the states of its edges, and the rest allows exactly the complementary parity relation (the half rule); for surrounded knots, every non-parity knot meets the rest (5 + 4 > 8). | `candidate-local-delta`; folklore risk medium | `NATIVE-HARDNESS-20261024-001C-P001`, Theorem 1; `…001B-P001`, Theorem 2 |
| 4 | Every native contradiction, cut at its bridges with the forced values pinned, is a set of unsatisfiable parity systems; without parity knots it is a necklace of odd wire rings. | `candidate-local-delta`; folklore risk medium | `…001C-P001`, Theorem 2; `…001B-P001`, Corollary 3 |
| 5 | Native networks of every law are decided in polynomial time by peeling, the tree of bridges, the half rule and Gaussian elimination, without external theorems; ticket A's tractability statement becomes unconditional. | New to the program; standard dynamic programming on a new structural fact | `…001C-P001`, Corollary 3 (20,000 networks against a solver) |
| 6 | Without parity knots, unsatisfiable native networks are refuted with derived clauses of at most two literals in linear size. | `candidate-local-delta` (the single-clause case is classical) | `…001B-P001`, Theorem 4 |
| 7 | Every unsatisfiable native network needs resolution width at least the balanced edge boundary of its graph, because K2 is flip repair and hub-freeness gives two occurrences per variable. So parity networks on cubic expanders need width Ω(n), and size 2^Ω(n) given Ben-Sasson and Wigderson. Native contradictions are hard for resolution exactly when the law contains a parity knot. | Folklore for the width bound (risk high); the dichotomy is new to the program | `…001B-P001`, Theorem 5 and Corollary 6 |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that hardness needs hubs (refined: true for NP-hardness, but native parity networks are already hard for resolution);
- that hub-free tractability of the knots needs Kazda, Kolmogorov and Rolinek (superseded by a two-line count);
- that non-parity native networks have bounded resolution width (confirmed in a sharper form);
- that emergence and hardness are unrelated (refined: natively the only contradiction is memory's, parity).

## Recommendation

**Continue with a fresh epic: counting what emerges natively.**
- **The question.** Deciding a native network is easy, but counting its witnesses, the emergent information, may not be.
- **What is already easy.** The topological knots count trivially (2^g; Verlinde dimensions, `SURFACE-GLUING-20261024-001`).
- **First discriminator.**
  - Classify native counting for the seven symmetric knots through the published dichotomy for three-regular Holant problems, and
    confirm on small networks.
  - Test whether not-all-equal counting is hard in general but easy on planar networks.
- **Interest:** 2/3. It asks whether emergence is hard to count while contradiction is easy. The main uncertainty: published
  dichotomies probably settle it.
- **Alternatives:** native logic of every arity (1/3); a note on the half rule (1/3).
- **Stop if** every knot's native counting is affine or topological.
- **Execution:** deferred to the owner.
