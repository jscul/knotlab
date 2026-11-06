# Closure of the walls-with-choices epic

Status: Proved

Epic `WALLS-WITH-CHOICES-20261024-001` closed on 2026-10-24. This is a ledger: one line per conclusion, with its novelty label
and evidence. It makes no new claim. The decision note is `research/WALLS-WITH-CHOICES-20261024-001/walls_with_choices.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A cylinder has an assignment exactly when some cyclic cover of it does: its assignments form a one-dimensional shift of finite type, which has periodic points when nonempty. | Classical | `WALLS-WITH-CHOICES-20261024-001A-P001`, Lemma 2 |
| 2 | The wall theorem. For every three-place tiling contact with a constant frame (27 of 30), an odd class has an assignment on its cylinder exactly when the torus's wall graph has a closed walk with a transverse class and no overlap in ℤc + ℤe: a periodic wall that crosses the cylinder without meeting its own copies. | Standard method; the statement is new to the program; low to moderate folklore risk | `…001A-P001`, Theorem 1; 292 assignments explained and rebuilt, 469 contradictions with no good simple cycle |
| 3 | The rules of `DIRECTIONAL-RIGIDITY-20261023-001` for straight walls and for walls without choices, and its Remark 8, are special cases of the wall theorem. | New to the program | `…001A-P001`, Corollary 2 |
| 4 | The quadrant rule. For the six directed bending contacts (54, 62, 110, 147, 155, 203), every odd class with c₁c₂ > 0 contradicts together, exactly when the wall graph has no cycle. Honeycomb contacts can split the first quadrant. | Elementary; new to the program | `…001A-P001`, Theorem 3 and Remark 4; no split among 363331584 frozen configuration-twists |
| 5 | Simple cycles of the wall graph decide every configuration of the twelve bending contacts on 3 × 3, and of the eight with directed walls or without a free place on 3 × 4. For 111, 125, 159 and 215 on 3 × 4 they report contradictions that do not exist: the histograms differ by 5640 configurations per contact, a lower bound on those misjudged. | A recorded computation | `WALLS-WITH-CHOICES-20261024-001B-E001`, refuted (prediction P2 fails); 9119 s of a 10800 s budget |
| 6 | For those four contacts good walls must sometimes repeat a wall state. Three certified configurations of 159 on 3 × 4 have an assignment along an odd class, yet no simple cycle passes the criterion. The crossing wall of a cover assignment winds with det(c, e) equal to the number of sheets (3, 3, 5) and rebuilds an assignment alone. | Low novelty (generic for self-avoidance on a quotient); the witnesses are new | `WALLS-WITH-CHOICES-20261024-001D-P001`, Proposition 1 and Corollary 2 |
| 7 | Planted staircases make the eight bending contacts with directed walls or without a free place (54, 62, 109, 110, 147, 151, 155, 203) selective on every L × M torus with L, M ≥ 3. | Standard method; the constructions are new to the program | `WALLS-WITH-CHOICES-20261024-001C-P001`, Theorem 2 and Corollary 3; verified up to 9 × 9 |
| 8 | Open: whether 111, 125, 159 and 215 are selective on every large torus. They are selective on every torus computed, but none of their configurations on 3 × 3 or 3 × 4 contradicts along every odd class, so a planted wall has no quiet background. | Recorded as open | `…001C-P001`, Remark 4 |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that walls with choices need a different, transfer-matrix rule (false: the same periodic-wall rule holds);
- that a good wall is a simple cycle of the wall graph (false for the honeycomb contacts with a free place);
- that selectivity can always be built by planting one wall on a quiet background (false for that kind on small tori);
- that directed and honeycomb bending contacts select in the same way (refined: directed walls keep the first quadrant
  together).

## Recommendation

**Continue with a fresh epic: the cost of reading a direction.**
- **The question.** How hard is it to decide whether a configuration contradicts along a class? The program decides it by direct
  rules for straight walls (staircases) and for walls without choices (cycles of a partial permutation), each a polynomial test.
  Does it stay polynomial when walls have choices, and if not, where does the difficulty begin?
- **Why now.** The wall theorem turns every instance into a search for a closed walk that avoids its own copies. For the honeycomb
  contacts with a free place, conclusion 6 shows that this walk must sometimes repeat states and wind several times, so
  simple-cycle search fails there. That is the first difference found between kinds of three-place contact in how a direction
  is decided.
- **The first discriminator.** Measure the fewest sheets needed on samples of the four contacts on 4 × 4 and 4 × 5; in D's
  witnesses it equals the winding of the good wall. A bound polynomial in the torus would put the decision in NP, with walls as
  certificates; growth would point to hardness. Alongside, test an extremal-wall decider for the directed contacts with choices
  against the frozen record.
- **Interest:** 2/3. It ties the three-place contacts to a complexity question in the program's two-versus-three thesis. The main
  uncertainty is that a bounded cover search may make every kind polynomial, which would end the line with a negative answer.
- **Alternatives:** selectivity of the four open contacts on every large torus (1/3) and the 3/4 constant (1/3).
- **Stop if** the sheet count stays below a small constant on every sample and the extremal decider matches the frozen record;
  then record the polynomial rule and stop.
- **Execution:** deferred to the owner.
