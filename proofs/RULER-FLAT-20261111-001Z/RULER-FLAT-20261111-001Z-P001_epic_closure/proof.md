# Closure of the ruler on balanced weaves

Status: Proved

Ticket `RULER-FLAT-20261111-001Z`, 2026-11-11.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RULER-FLAT-20261111-001/ruler_flat.md`, with the review and the next-steps report; the pre-registration is beside it.

Words (2026-11-11). The statements use the literature's words for a given substrate: a triangle is a knot, a vertex a
distinction, an edge a co-knotted pair and a triangulated surface a two-fold weave (Intuitions guide, Glossary). One-sided and two-sided weaves are now non-orientable and orientable,
and a balanced weave six-regular; the earlier text is in git history

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On a 6-regular torus the admissible tilts are the slopes satisfying three inequalities, and the best tilt's margin M is a multiple of 3 at most 3/2 the edge-width. | known-with-delta; proved | A (T0) |
| 2 | Ground states of the triangular Ising antiferromagnet on the torus exist exactly when M ≥ 0. | known-with-delta; proved, refereed | A (T1) |
| 3 | For two vertices at graph distance d, the smallest non-shattered set containing both with every co-1 subset shattered has at least min(d, M/3) + 2 vertices, and exactly d + 2 when d < M/3. | known-with-delta; proved, refereed; checked to 96 vertices | A (T2, T3) |
| 4 | If M > 3 the minimal non-shattered sets of at most three vertices are exactly the triangles (nothing frozen and no tie already when M ≥ 3). | known-with-delta; proved, refereed | A (T4) |
| 5 | The same holds on every Klein bottle whose glide keeps the forward steps (an edge glide), with M over the deck group; these are exactly the non-orientable weaves whose co-knotted pairs can be directed so that every knot is a directed cycle. | known-with-delta; proved, refereed; checked to 48 vertices | A (Lemma K0, Theorem K) |
| 6 | Klein bottles with an altitude glide are not proved; the extension lemma the pre-registration named is false as phrased. | gap | A |

## Answer

The not-all-equal knot measures every closed six-regular two-fold weave that is orientable, or non-orientable and directed, exactly below a
third of the best winding's margin. All of it needs each co-knotted pair in exactly two knots. One correction, Not a block (the
pre-registration's note on non-orientable weaves).

## Recommendation

**Research directions**, selected #1, overlapping bases (pairs in any number of knots); the owner gave the go-ahead on 2026-11-11.
