# Closure of the three-fold-spaces epic

Status: Proved

Ticket `THREEFOLD-SPACES-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes
no new claim. The decision note is `research/THREEFOLD-SPACES-20261030-001/the_knots_three_fold_spaces.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: three-fold spaces are three-regular contradictions; the earlier text is in git history.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For a connected 3-regular triple system the following are equivalent: not 2-colourable; minimally not 2-colourable; incidence matrix sign-nonsingular; every nice cycle of the incidence graph of length 2 mod 4; no even directed cycle in its 2-in 2-out digraph. | classical in substance (Seymour; Bassett–Maybee–Quirk) | A-P001, Theorem 1 |
| 2 | Across a 3-edge tight cut the perfect-matching signs factorize, so the pieces are sign-nonsingular up to one common twist, and an untwisted non-colourable piece acts as a single point or line. Hence Fano compositions are not 2-colourable, and the knot has three-regular contradictions with 7 + 6k triangles for every k. | standard tight-cut reasoning; no overlap found for the knot reading | A-P001, Theorems 2–3 |
| 3 | The premise of the previous recommendation is false: a 13-point Fano splice is a linear 3-regular triple system that is not 2-colourable. Gluings whose contacts are all phase locks or odd three-fold contacts contain no lock, so the planned mixed class is empty. | elementary | A-P001, Corollary 6, Proposition 7 |
| 4 | Exhaustively (SAT, replayed), the non-colourable connected 3-regular triple systems on at most 13 points are exactly the Fano plane and the Fano splice, and no twisted one exists. So the knot's three-regular contradictions with at most 13 triangles are their duals. | no overlap found | B-P001 |
| 5 | A Fano block forces its ports to one colour. A cycle of k Fano blocks resists 2-colouring iff k is odd, and with one twist iff k is even. The twisted 2-cycle (14 points) is the smallest twisted system, and two of them splice to a 27-point system. So the knot has three-regular contradictions with 21, 27, 35, … triangles that are not Fano compositions. | elementary given 2; no overlap found for the reading | C-P001, Theorems 1–3, Corollary 4 |
| 6 | Ticket A's Theorem 4 (reduction to Fano compositions) is false. Its induction missed tight-cut contractions that repeat a point on a line. | erratum | C-P001 (erratum) |
| 7 | Open: every non-colourable 3-regular triple system is assembled from Fano blocks by splices and odd cycles (Heawood graphs and Kasteleyn-even planar pieces). | conjecture | C-P001, Conjecture 5 |

## Recommendation

**Continue**, as a fresh epic: the grammar of three-regular contradictions (2/3).
- **The task.** Prove Conjecture 5 by tight-cut decomposition with doubled incidences, using Robertson–Seymour–Thomas for the braces and
  Kasteleyn's parity for the planar pieces.
- **The check.** Extend the SAT census to pieces with doubled incidences.
- **Status.** Deferred to the owner. The decision note has the full assessment.
