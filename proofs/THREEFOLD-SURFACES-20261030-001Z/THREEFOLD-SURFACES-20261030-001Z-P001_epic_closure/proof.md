# Closure of the three-fold-surfaces epic

Status: Proved

Ticket `THREEFOLD-SURFACES-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/THREEFOLD-SURFACES-20261030-001/the_surfaces_of_three_fold_spaces.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: three-fold spaces are three-regular contradictions; a Fano atom is a Fano piece; the earlier text is in git history.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Across a 3-edge cut, 2(g − g₁ − g₂) = cyc(rτ) + cyc(r̃π) − cyc(πτ) − 3 for the transitions τ, π and the rotations r, r̃ at the contracted vertices; a face turning back across a cut edge costs that side a handle. | face-permutation calculus in the spirit of Stahl; no overlap found for the statement | A-P001, Lemmas 1–3 |
| 2 | Splice lemma: if A keeps its genus when the splice vertex is deleted, splicing A into any R along three edges gives genus γ(A) + γ(R). Without the hypothesis additivity fails (K₃,₃ ⊙ K₃,₃ has genus 1). With both sides rigid, the minimal maps are exactly the compatible gluings of minimal maps of the sides, N(A)N(R)/2 of them. | no overlap found in a bounded search; folklore risk moderate | A-P001, Theorems 4–5 |
| 3 | The incidence graph of a three-regular contradiction with planar glue has genus equal to its number of Fano pieces (Heawood braces); in general the sum of its braces' genera when every non-planar brace is rigid. Every minimal map is a connected sum of Heawood maps and planar maps of the glue, Π N(B)/2^(cuts) of them. | new | A-P001, Theorems 6–7 |
| 4 | The Fano plane's space is the Heawood map: 16 torus rotation systems, one orbit, chiral; its dual is K₇ on the torus with the Fano plane's points and lines as the two colour classes. | classical map; the reading is new | A-P001, Proposition 8 |
| 5 | Exact SAT genus confirms the formula on all 32 classes up to 22 points and on nine larger spaces up to 180 vertices (trisum glue adds one); the 7-, 13- and 19-point spaces have exactly 16, 128 and 1024 minimal rotation systems, all standard connected sums, with 1, 2 and 3–6 orbits. | computational confirmation | B-P001 |

## Recommendation

**Continue**, as a fresh epic: the knot's amplitude on its surface (2/3).
- **The task.** Prove that the knot's exactness factor λ(0) on a three-regular contradiction is 5 per handle times a factor from planar glue, and
  identify that factor.
- **Scratch probe (not evidence).** λ(0) = 5^genus at every corner line for twelve spaces with doubled-square glue. The twisted cube gives
  2·5⁶.
- **Status.** Deferred to the owner. The decision note has the full assessment.
