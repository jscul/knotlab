# Closure of the three-fold-spin epic

Status: Proved

Ticket `THREEFOLD-SPIN-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes
no new claim. The decision note is `research/THREEFOLD-SPIN-20261030-001/the_knots_spin_structure.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Face splice: across a tight 3-edge cut, if each contracted vertex lies on three distinct faces, a genus-additive gluing has exactly three crossing faces, each one face from each side. Kasteleyn face parities add across the cut. | no overlap found; folklore risk moderate | A-P001, Lemma 1 |
| 2 | On every minimal map of a three-fold space with planar glue, every face has length 2 mod 4 and every vertex lies on three distinct faces: the knot's trivial signing is a Kasteleyn signing. | new | A-P001, Theorem 2; B-P001 (all spaces up to 22 points, 35- and 43-point maps) |
| 3 | For a Pfaffian signing that is Kasteleyn on a map, the Cimasoni–Reshetikhin form vanishes on every matching difference, and its Arf invariant does not depend on the perfect matching. | direct from Cimasoni–Reshetikhin; the observation is new here | A-P001, Proposition 3 |
| 4 | The knot's spin structures are even. The form splits over the Fano atoms, each atom has Arf 0, and every induced spin structure is even on every handle, at most 3^h of them. Exactly 3^h are realized up to 22 points. | new | A-P001, Theorem 4; B-P001 |
| 5 | On the Fano torus the 24 perfect matchings induce exactly the three even spin structures, 8 each. The four Kasteleyn classes have determinants 24, 8, 8, 8, and only the knot's counts the matchings. | new (computation on a classical map) | A-P001, Proposition 5; B-P001 |
| 6 | Non-planar glue: trisums of prisms are rigid of genus one, Kasteleyn with their Pfaffian signing on all minimal maps, and even. | computational, new | B-P001 |
| 7 | On non-minimal maps the same signs can be Kasteleyn with odd spin structures. About 1–2% of such maps are odd, all of genus 3 or more. | computational, new | B-P001 |

## Recommendation

**Continue**, as a fresh epic: the knot's amplitude as a spin sum (2/3).
- **The task.** The amplitude is an Ising partition function at half the knot's angle (`THREEFOLD-AMPLITUDE-20261030-001C`). On a surface
  that is a signed sum over spin structures of Pfaffians. Which spin structures contribute at the knot's coupling? Does 5 per handle come
  from the even ones alone?
- **Status.** Deferred to the owner. The decision note has the full assessment.
