# Closure of the where-counting-in-three-dimensions-becomes-hard epic

Status: Proved

Epic `HARD-3D-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/HARD-3D-20261025-001/counting_becomes_hard.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Fin handlebodies over plane multigraphs are compact orientable 3-manifolds whose number of homomorphisms into a finite group is the spin model Σ_y Π_e \|C(y_u y_v⁻¹)\|. For S₃, interpolation over repeated edges recovers 2·P(G, 3). So counting homomorphisms from compact 3-manifold groups into S₃ (and D₈) is #P-hard. | `candidate-local-delta`; folklore risk medium | `HARD-3D-20261025-001A-P001` |
| 2 | Their doubles are closed. With edges repeated, the count is an exponential polynomial whose target coefficient is a chromatic polynomial, proved by Potts duality on the dual graph: 2·P(G, 9)/3^\|V\| for S₃ (pairs of 3-colourings), with analogues for dihedral groups, Q₈ and A₄. | `candidate-local-delta`; folklore risk low to medium | `HARD-3D-20261025-001B-P001`, Theorem 3 |
| 3 | Counting homomorphisms from closed orientable 3-manifold groups is #P-hard for S₃, for every dihedral group whose order is not a power of 2 at least 16, and for Q₈ and A₄. The S₃ case was listed as open in 2026. | Settles a named open case; no later work found | `…001B-P001`, Theorem 1 |
| 4 | For the class-2 groups (D₈, Q₈) the bounded-H² hypothesis of the Samperton–Weiß algorithm cannot be dropped, unless every #P function is polynomial-time. | Consistent with the authors' revision | `…001B-P001`, Corollary 2 |
| 5 | The dihedral group of order 16 satisfies the identity, but 256·16 = 64² contaminates its extraction (192 on the 4-cycle). It is left open. | Documented obstruction | `…001B-P001`, Section 5 |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- **Closing a manifold might hide the colourings.** False: the dual sector adds a second colouring.
- **Only simple groups are known to be hard on 3-manifolds.** Extended: S₃, dihedral groups, Q₈ and A₄.
- **Class-2 targets are polynomial on all closed 3-manifolds.** False for unbounded H², unless every #P function is polynomial-time.

## Recommendation

**Continue with a fresh epic: the full dichotomy.**
- **The question.** Is counting homomorphisms from closed 3-manifold groups #P-hard for every finite non-abelian group?
- **First:** the dihedral group of order 16, using a second gadget whose growth rates tell reflections from central edges.
- **Interest:** 3/3.
- **Alternatives:**
  - result conversion with a triangulation-level check (2/3);
  - bounded homology (1/3).
- **Stop if** a second gadget does not separate the collision.
- **Execution:** deferred to the owner.
