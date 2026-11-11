# Closure of the space-selection epic

Status: Proved

Ticket `SPACE-SELECTION-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/SPACE-SELECTION-20261030-001/which_spaces_the_harmony_builds.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: three-fold spaces are three-regular contradictions; a base corner is a sign-carrying place; the earlier text is in git history.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For finite gadgets of triangles glued at vertices, the standing wave w_q = K + qM is exact iff six signed sums over sector assignments with mixed corner sectors vanish. The flip parity is odd for every gadget, so the conjectured criterion "sector locking plus odd flip parity" is refuted as a characterization. A gadget is exact either for all q outside the roots of a monic λ of degree n − 1, or for at most n values. | no overlap found | A-P001, Theorems 1-2 |
| 2 | Phase locking and balanced cancellation each suffice and together explain every exact gadget with at most five triangles (3,078 and 2,616 at n = 5). Algebraic cancellation is needed for some gadgets with six (non-linear) and seven (linear) triangles. | no overlap found | A-P001, Theorem 3; B-P001 |
| 3 | Exact gadgets are closed under substitution (λ multiplies), and tadpoles keep exactness and corner chains, so growth exponents of exact towers are unbounded: the law selects no growth exponent. | elementary | A-P001, Theorems 4, 6 |
| 4 | Census to five triangles (1, 0, 30, 1,293, 73,326 gadgets): the standing wave is generic-exact on 1, 14, 172, 5,694 and signed not-all-equal is exact on 1, 14, 206, 8,584 (3,082 at the knot angle only). On linear gadgets the two coincide up to five triangles. Special angles include π/4, π/6, π/8 and cos 2θ = −1/3. Growth rates are certified algebraic integers in [2, n − 1]. Exact examples show the small-size coincidences end at six and seven triangles. | no overlap found | B-P001 |
| 5 | No law with nonnegative values and support not-all-equal is exact on a gadget with 2 ≤ n ≤ 6 triangles, and plain not-all-equal is exact on the 7-triangle Fano gadgets. Signed not-all-equal is exact on the 3-triangle Sierpinski gadget. This supersedes ticket A's Theorem 5, whose claim missed n = 1 and whose proof used the wrong hypergraph. | classical inputs (property B), short | C-P001, Theorem 1 (erratum for A-P001, Theorem 5) |
| 6 | At the knot angle a contact of three triangles with an odd count of sign-carrying places acts on their phases as the not-all-equal knot. A gluing made only of such contacts is plain not-all-equal on its dual configuration, so the knot needs at least seven triangles there. At seven, with distinct corner triangles, the exact gluings are exactly the 64 Fano gadgets, exact for both the signed and the plain knot. | no overlap found | A-P001, Proposition 7; C-P001, Theorem 2, Corollary 3, Proposition 4 |

## Recommendation

**Continue**, as a fresh epic: the knot's three-regular contradictions (2/3).
- **The task.** Prove, or cite exactly, that every connected 3-regular triple system other than the Fano plane is 2-colourable. Then the Fano
  gadgets are the knot's only three-fold odd spaces at every size.
- **The aim.** Classify mixed gluings, of two-fold phase locks and three-fold phase knots, up to six triangles.
- **Status.** Deferred to the owner. The decision note has the full assessment.
