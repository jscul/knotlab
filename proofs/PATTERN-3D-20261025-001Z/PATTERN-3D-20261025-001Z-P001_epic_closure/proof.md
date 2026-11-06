# Closure of the patterns-of-patterns-in-three-dimensions epic

Status: Proved

Epic `PATTERN-3D-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/PATTERN-3D-20261025-001/patterns_of_patterns.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For any triangle rule, triangles that lie in no allowed tetrahedron never enter a move identity. | Local lemma; folklore risk low to medium | `PATTERN-3D-20261025-001A-P001`, Theorem 1 |
| 2 | Let the long edge of each triangle be a function of its two short edges, on any finite label set. The law survives the ordered 2–3 and 1–4 moves exactly when its working triangles are the compositions of a finite groupoid whose components share the value objects × group order. Then λ = 1 and μ is that value, and the objects are recovered as the idempotent labels. | `candidate-local-delta`; folklore risk medium (nearest: Duskin–Glenn) | `…001A-P001`, Theorem 2; exhaustive checks on all partial operations up to three labels and on groupoids up to eight arrows |
| 3 | The invariant is Σᵢ \|Hom(π₁(M), Gᵢ)\|/\|Gᵢ\|. With cited group theory, these laws see exactly the finite quotients of π₁. Lens spaces of equal order and the pairs of Funar and Hempel are never separated. | Classical: Dijkgraaf–Witten, Freed–Quinn, cited profinite facts | `…001A-P001`, Corollaries 3 and 4 |
| 4 | Every triangle relation on three labels whose law survives reduces to one of seven groupoid laws with free decorations. Every surviving multiplication table on four labels reduces to a groupoid: Z₄, Z₂ × Z₂, the pair groupoid, or one or two constants. | `no-overlap-in-bounded-search`; low depth; the table part independently checks conclusion 2 | `PATTERN-3D-20261025-001B-E001`, supported |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- **A non-group structure might survive with composite labels and see something new.** False for functions, and false for all
  relations on three labels.
- **Seeing more of three dimensions needs signs.** Refined: composite labels see every finite quotient of π₁ without signs; phases are
  still needed for linking forms.
- **Patterns of patterns grow what can be seen without bound.** Bounded: all counts together see exactly the finite quotients of π₁.

## Recommendation

**Continue with a fresh epic: where counting in three dimensions becomes hard.**
- **The question.** For which finite groups G is counting homomorphisms from π₁ of a triangulated 3-manifold into G polynomial, and for
  which is it #P-hard?
- **What is known.**
  - Abelian and class-2 nilpotent groups are easy. The class-2 result is Samperton and Weiß, 2026.
  - Non-abelian simple groups are #P-complete (Kuperberg and Samperton, 2018).
- **The first discriminator.** S₃, the smallest non-nilpotent group. Its count is a sum over H¹(M; Z/2) of twisted Z/3 cohomology
  sizes.
- **Interest:** 2/3.
- **Alternatives:**
  - prove the classification for relations (1/3);
  - phases and linking forms (1/3);
  - a short note on the converse (1/3).
- **Stop if** neither a hardness reduction nor an algorithm for S₃ emerges; then record the open boundary.
- **Execution:** deferred to the owner.
