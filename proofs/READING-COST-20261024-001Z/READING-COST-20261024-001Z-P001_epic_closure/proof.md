# Closure of the cost-of-reading epic

Status: Proved

Epic `READING-COST-20261024-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is `research/READING-COST-20261024-001/reading_cost.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In the six directed placements (54, 62, 110, 147, 155, 203) a wall is a monotone path whose moves are allowed one at a time, so walls of one left value form a lattice under pointwise maximum and minimum. | Elementary; new to the program | `READING-COST-20261024-001A-P001`, Lemmas 1 and 2 |
| 2 | A wall is good for a class with c₁c₂ ≤ 0 exactly when its copy one period of the cylinder away lies strictly above it or strictly below it; the good walls of each kind are closed under maximum, minimum and the translations that keep the coins. | Elementary; new to the program | `…001A-P001`, Lemma 3 |
| 3 | Aubry's ordered maximum and a split at a repeated square shorten every good wall to one that never repeats a square of the type-preserving cover. So simple cycles of the wall graph decide the directed placements on every torus. | Classical methods; the result is new to the program; moderate folklore risk | `…001A-P001`, Lemmas 4 and 5, Theorem 6; walls of up to 25 squares shortened in the check, up to 41 in scoping |
| 4 | Reading a class of a directed placement takes time polynomial in L · M and the bit length of the class: a cycle test, or arc consistency on a max-closed constraint problem for each period up to the size of the type-preserving cover. | New to the program; moderate folklore risk | `…001A-P001`, Theorem 7; 1432 classes in the check and about 19700 in scoping, no disagreement |
| 5 | Among the twelve bending placements, only the four honeycomb placements with a free place (111, 125, 159, 215) now lack a known polynomial rule. | Synthesis | `…001A-P001`, Corollary 8 |
| 6 | Cover sheets do not measure difficulty: directed placements sometimes need 3, 5 or 7 sheets on 3 × 3 and are polynomial. | Observation | Scoping disclosed in `…001A-P001`; decision note |
| 7 | For the four honeycomb placements with a free place, simple cycles keep misjudging classes on larger tori: 0.51 to 0.57% of their contradiction verdicts on 4 × 4 and 0.32% pooled on 4 × 5, against 0.229% on 3 × 4, with misjudged classes needing 2 to 10 cover sheets. The growth to 4 × 5 is weak (about 1.5 standard errors). The directed controls had no misjudgment among 1.85 million verdicts. | A recorded computation | `READING-COST-20261024-001B-E001`, supported (all four predictions) |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- that the number of cover sheets measures how hard a class is to read (false);
- that good directed walls can be taken simple on the torus itself (refined: simple on the cover that undoes the twist);
- that trivial polymorphisms mean no tractable structure (refined: the tractability lives in the wall picture and in the
  restricted instances).

## Recommendation

**Continue with a fresh epic: honeycomb walls, hard or easy?**
- **The question.** Can a class be read in polynomial time for the four honeycomb placements with a free place (111, 125, 159,
  215), or is reading hard there?
- **Why now.** They are the only bending placements without a polynomial rule.
  - The lattice method of conclusions 1 to 4 fails exactly there: in height variables each triangle rule is max-closed for one
    chirality and min-closed for the other, and a winding wall meets both.
  - Their good walls must sometimes repeat states (`WALLS-WITH-CHOICES-20261024-001D-P001`), and conclusion 7 shows the failure of
    simple cycles persists on larger tori.
- **The first discriminators.**
  - A lattice test: do two good walls combine under the height maximum or minimum? A certified pair where both fail closes the
    lattice route.
  - A bounded search for configurations that confine walls to corridors on tori up to 6 × 6, the building block of a reduction.
- **Interest:** 2/3.
- **Alternatives:** selectivity of these four on every torus (1/3, overlapping with the corridor search); the 3/4 constant (1/3);
  a note on the wall theorem and the directed rule (1/3).
- **Stop if** the lattice test passes, and then pursue a polynomial rule instead; or if no confining configuration appears on tori
  up to 6 × 6.
- **Execution:** deferred to the owner.
