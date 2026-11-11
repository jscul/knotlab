# Closure of the three-fold-amplitude epic

Status: Proved

Ticket `THREEFOLD-AMPLITUDE-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/THREEFOLD-AMPLITUDE-20261030-001/the_knots_amplitude_on_its_spaces.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: three-fold spaces are three-regular contradictions; a Fano atom is a Fano piece; the earlier text is in git history.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The knot's exactness factor on a three-fold odd gadget is λ(0) = (−1)^(n−1) A(H, L₀), where A(H, L₀) is the number of 2-colourings of the dual system minus the corner line, with that line fixed. | new (via the duality of SPACE-SELECTION C) | A-P001, Theorem 2; B-P001 |
| 2 | Point lemma, and factorization of A across 3-edge tight cuts: A(H, L) = a(B) · A(H′, L). | no overlap found | A-P001, Lemma 3 and Theorem 4 |
| 3 | Brace amplitudes: Heawood 5, doubled square 1, trisum of three cubes 6. A planar brace with a Kasteleyn signing has amplitude equal to the number of Tutte matchings of its trinity, hence Tutte's tree-trinity number: Kálmán's hypertrees, and the spanning trees of M for the omnitruncation of M. | the identification is new; Tutte, Kálmán and Mathews are external inputs; folklore risk moderate for the pointer argument | A-P001, Proposition 5; B-P001 |
| 4 | Two-way count for every cubic signed system: #col(H) + 6N_H(L) = 2Σ_p M_{Lp}N_{Hᵀ}(p) + R(L), and #col(H) = #col(Hᵀ). It comes from an Ising weight with couplings ±iπ/6 on the incidence graph, summed in both orders. | #col(H) = #col(Hᵀ) is likely an instance of Valiant's holographic identities (folklore risk moderate to high); the inserted count: no overlap found | C-P001, Lemma 2 |
| 5 | One amplitude: every connected cubic signed system that is not colourable has A(H, L) = A(Hᵀ, p) for all lines L and points p. A signed dictionary also holds: not colourable ⟺ Pfaffian ⟺ minimal. | new | C-P001, Theorem 3 and Lemma 4; B-P001 (all 2,652 census classes) |
| 6 | Product formula for every three-regular contradiction: λ(0) = (−1)^(n−1) Π_B a(B) over its braces, so |λ(0)| = 5^(Fano pieces) · Π ρ(planar glue) · Π a(non-planar glue). With doubled-square glue, |λ(0)| = 5^genus. | new | A-P001, Theorem 6; C-P001, Corollary 5; B-P001 |
| 7 | Tutte matchings of a planar brace are equinumerous for every outer triangle, white or black. | known via Tutte's theorem; new proof | C-P001, Corollary 6 |
| 8 | Trisums of three prisms along a square face are Pfaffian braces with one amplitude, which depends on the gluing: (2,3,3) gives 13 or 14, and (4,4,4) gives 36 or 52. Two cubes and a 2k-prism give 3k. | computational, new | B-P001 |

## Recommendation

**Continue**, as a fresh epic: the knot's spin structure (2/3).
- **The task.** Do the knot's own signs satisfy Kasteleyn's face condition on every minimal map of every three-regular contradiction? If so, identify
  the spin structure each space carries on its surface, and its Arf invariant per Fano piece.
- **Scratch evidence (not evidence of the claim).** Every face of the minimal maps up to 19 points has length 2 mod 4.
- **Status.** Deferred to the owner. The decision note has the full assessment.
