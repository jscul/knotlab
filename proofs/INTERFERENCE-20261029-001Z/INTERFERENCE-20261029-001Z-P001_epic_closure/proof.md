# Closure of the interference epic

Status: Proved

Ticket `INTERFERENCE-20261029-001Z`, 2026-10-29. A ledger: one line per conclusion, with its novelty label and evidence. No new
claim. The decision note is `research/INTERFERENCE-20261029-001/interference.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Sums over hidden bits of products of nonnegative two-variable functions have majority-closed supports, so none is a three-bit relation free on every pair but constrained as a whole (a knot); a product of two-variable functions (no hidden bits) never has a knot as support, whatever the signs. | classical (Baker–Pixley, Schaefer) | A-P001, Theorems 1–2 |
| 2 | A clause of any width is 1 − Π(1 − ℓ), a signed sum with one hidden bit, so a k-CNF with m clauses is a signed pairwise sum with m hidden bits; this is the first step of OpenAI's refutation and of Anthropic's bound in n. | elementary (inclusion–exclusion) | A-P001, Theorem 3 |
| 3 | Every one of the 16 classes of three-bit knots is exactly a signed pairwise sum with one hidden bit (real tensor rank 2; not-all-equal and twisted not-all-equal after one pairwise sign; golden ratio in the three-excluded and not-all-equal decompositions). | no overlap found | A-P001, Theorem 4 |
| 4 | With weights ±1, native gadgets of three and five copies of their own law rebuild 14 of the 16 knot classes and reproduce 12 exactly, against only parity with nonnegative counts; 10 classes are exact on the native triangle, and every exact fixed point keeps its law at every level of its tower. | no overlap found | B-P001, Theorems 1, 3 |
| 5 | Two copies sharing two variables contract to an identity exactly when a flattening has orthogonal rows of equal norm; with nonnegative weights only parity has such a wire. | elementary | B-P001, Lemma 2 |
| 6 | Signed not-all-equal (−1 on one tuple) is reproduced by the native triangle with factor 3; every signed not-all-equal-type law of positive Cayley hyperdeterminant is. | no overlap found | B-P001, Proposition 4 |
| 7 | Under the triangular-lattice (shared-boundary) substitution, signed laws constant on rotation orbits are exact on the tetrahedron, octahedron and icosahedron only for parity. | negative; first discriminator | B-P001, Proposition 5 |
| 8 | The finite cancellation cores of both refutations replay independently: the eight-square identity and its 3-versus-6-bit costs, the grouped pieces of Anthropic's Lemma 2 for one and two blocks, the pieces of Anthropic's Theorem B at 1, 2 and 3 bits, and the swap-matrix lemmas of OpenAI's construction at small parameters; every control fails as it should. | replay of unreviewed claims (exploratory) | C-E001 |
| 9 | Nonnegative rewritings of a crossing cannot lower its cut cost (fooling-set argument), so the speedups need cancellation. | textbook | decision note |

## Recommendation

**Continue** with a fresh epic on interference on genuine two-dimensional space. It would test signed and real-weighted laws on
the triangular-lattice rules of `SHARED-SUBDIVISION-20261029-001`, starting from the golden-ratio weights of the Fibonacci knots,
and signed hub gadgets for not-all-equal below seven copies. It is deferred to the owner, together with the decision request on
the interference reading (`research/INTERFERENCE-20261029-001/canonical_correction_request.md`). See the decision note for the full
assessment.
