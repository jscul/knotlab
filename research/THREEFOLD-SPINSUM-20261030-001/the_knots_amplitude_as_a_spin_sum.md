# The knot's amplitude as a spin sum

Epic `THREEFOLD-SPINSUM-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, let's continue." This approved the recommendation of `THREEFOLD-SPIN-20261030-001`.
  - The knot's amplitude is an Ising count at half the knot's angle on its triangle–contact graph (`THREEFOLD-AMPLITUDE-20261030-001C`).
  - On a surface such a count is a signed sum over spin structures.
  - Does 5 per handle come from the even spin structures alone, with the odd one cancelling?
- **Scoping (not evidence).** On the Fano torus every spin sector contributes. A first probe mislabeled the knot's spin structures by pairing
  classes through coordinates instead of the intersection form; this was corrected before activation.
- **Intuitions targeted:**
  - everything is relational: whether the contradiction and the amplitude are properties of the whole;
  - the law equipping its space.

**The evidence:**
[Spin sectors of the knot's count](../../proofs/THREEFOLD-SPINSUM-20261030-001A/THREEFOLD-SPINSUM-20261030-001A-P001_spin_sectors_of_the_knots_count/proof.md)
(A, proof with exact finite computations).

## Outcome in one paragraph

**No.** The knot's amplitude takes contributions from every spin structure, and "five per handle" is not a spin-sector phenomenon.
- **The spin sum (proved).** The colouring counts are Arf-signed averages of spin sectors, and the knot's contradiction is a balance between
  even and odd sectors.
  - On the Fano torus the closed space has sectors 8, 8, 8 (its three even spin structures, the knot's own) and 24 (the odd one), and
    3 · 8 = 24.
  - Opening a contact makes them 16, 16, 16 and 28, and 2 · 5 = (3 · 16 − 28)/2.
  - So the even sectors alone would give 12, and the odd sector does not cancel.
- **No localization.** At genus 2 the sector values do not factor over the two handles: the 4 × 4 sector matrices have full rank, while the
  amplitude is exactly 5 · 5.
- **A clean spin fact (proved).** Of the 4^g sign classes Kasteleyn's condition allows on the surface, the knot's is the only one that cannot
  be 2-coloured. Every twist of it can.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemmas 1–2, Theorem 3 | #col(H) and #col(H − L) are 2^{−g} Σ_q (−1)^{Arf q} N_q; non-colourability is the balance of even and odd sectors. |
| A, Proposition 4 | The knot's sign class is the only non-colourable one among the 4^g Kasteleyn classes; every nonzero twist is 2-colourable. |
| A, Proposition 5 | Fano torus: 8, 8, 8 \| 24 closed and 16, 16, 16 \| 28 opened, on all 16 maps and 7 contacts; the even sectors are the knot's own. |
| A, Proposition 6 | 13-point space: sector matrices over the two handles have rank 4; no factorization. |

## Reading

- **The amplitude belongs to the whole.** Five per handle is exact, but it comes from the colouring count factoring across cuts (the point
  lemma), not from spin sectors.
- **The contradiction is a balance.** The knot's space cannot be 2-coloured because its odd spin sector exactly cancels its even ones.
  Opening a contact unbalances them by twice the amplitude.
- **Uniqueness.** Among all the sign classes its surface admits, the knot's is the only contradictory one.
- **Limits.**
  - Sector values are computed for two spaces, not given by a formula.
  - Their Pfaffian (Kac–Ward) form is classical context, not used.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the knot's amplitude as a spin sum | **Status:** Successful (negative answer) | Proved spin sum and balance; exact sector values; the even sectors do not carry the amplitude, the odd one does not cancel, and sectors do not localize on handles. |
| Local direction — spin structures and spin sums of three-fold spaces | Retire | The spin structure is identified (previous epic) and the spin decomposition does not localize. Further refinement would not change these conclusions. |
| Broader exploration — three-fold spaces (question 9) | Practically complete | Five epics give atoms and glue, handles, the amplitude (5 per handle, tree counts, one amplitude per space) and the spin structure. Unmapped: mixed contact sizes, and the complexity of the amplitude beyond the knot's spaces. |
| Long-term goal — space from logic, and the two/three boundary | Obstruction learned | The amplitude's structure is not topological in the spin sense. What the line did find is linear-algebraic: the knot's spaces sit exactly on Seymour's bound, where non-colourability is a determinant condition. |
| Next recommendation — where counting near-critical instances becomes hard | **Next step:** Continue, as a fresh epic. The knot's spaces are exactly the cubic systems on Seymour's bound for minimally non-2-colourable hypergraphs: as many lines as points, non-colourability a determinant condition, and the count with one line removed a product of determinant-like amplitudes. Is that count polynomial-time on every such system, including non-planar glue? Does it become #P-hard once a minimal system has more lines than points, or is not regular? | Ties the line's results to the program's complexity thesis. Counting on Seymour's bound would be easy because it is a determinant, and it may be hard just off the bound. That is a two/three-style boundary in counting. |
| Interest — that recommendation | **2/3 — Promising** | The easy side has a concrete route (the product formula, determinants for planar braces, a boundary-tensor recursion over the Robertson–Seymour–Thomas decomposition). Main uncertainty: the hard side may need reductions that preserve minimality, which may not exist. |
| Execution — that next action | Deferred to the owner (fresh epic) | First discriminator: the trisum amplitude from boundary tensors of its pieces (easy side), and small critical systems with one more line than points (hard side). Stop if both sides stay open after these. |

**Recommendation.** **Continue**, as a fresh epic: where counting near-critical instances becomes hard (2/3). Two alternatives were
considered.
- **A write-up of the three-fold line (1/3).** Atoms, handles, Tutte trees, one amplitude per space, even spin structures. It is coherent
  but needs a deeper literature check. The owner asks for write-ups only for results of real magnitude.
- **Mixed contact sizes (1/3).** Spaces with both two- and three-fold contacts. Unmapped, but no probe points at a payoff yet.
