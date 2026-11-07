# Closure of the handles-and-counting epic

Status: Proved

Ticket `HANDLE-COUNT-20261106-001Z`, 2026-11-06.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/HANDLE-COUNT-20261106-001/handles_and_counting.md`.

## The question and the answer

Are weighted 2-colouring counts on the knot's spaces fixed-parameter tractable in the number of Fano atoms (the genus), or hard already at
bounded genus?
- **Genus.** Fixed-parameter tractable, by classical theorems; never hard at bounded genus.
- **Atoms.** Fixed-parameter tractable on the knot's own (plain) spaces, because there every junction of the glue is paid for by an atom.
  Not on Pfaffian triple systems in general: with signs, or without them on colourable braces, counting is #P-hard with no atom at all.
- **Where hardness lives.** In handles, but not in the knot's: Fano atoms meet the rest through three edges and cost nothing. The
  handles that cost are the glue's four-port junctions.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Weighted 2-colouring counts of 3-uniform hypergraphs (any incidence signs, any complex weight per monochromatic edge) are even-subgraph sums on the incidence graph, hence computable from 4^g determinants on a genus-g surface: fixed-parameter tractable in the genus, never #P-hard at bounded genus. | known (Galluccio–Loebl 1999; Tesler 2000; Cimasoni 2010); not re-proved | decision note |
| 2 | For a Pfaffian incidence graph, three-edge tight cuts cost nothing, and each Robertson–Seymour–Thomas 4-sum junction whose tensor violates the matchgate identity costs a factor 2 on the piece it hangs from: time poly(n)·2^J. For colourings, only junctions at or above squares with three twisted branches cost: poly(n)·2^b. | known technique; candidate local delta in the parameter | A (Theorem 1, Corollary 1) |
| 3 | For a simple Pfaffian cubic bipartite graph other than the Heawood graph and any Pfaffian signing σ: J + p ≤ a + \|σ\| − 2 (junctions, planar braces, Heawood braces). The bound is attained by the trisum of three cubes with three edge atoms (29 points). | no overlap found | A (Theorem 2, Proposition 6) |
| 4 | Hence on hypergraphs that are not 2-colourable without signs every such count takes time poly(n)·2^{a−2}, and polynomial time with planar glue at any number of atoms. The #P-hard couplings on these spaces need unboundedly many atoms; on Pfaffian systems in general, counting is #P-hard with a = 0. | new corollary; hardness known from the counting arc | A (Corollaries 2, 3) |
| 5 | On 257 three-fold spaces (census to 26 points, 80 random with plane glue, 6 larger, 28 fresh with trisum glue) the bound holds wherever it applies, with equality on the 13-point splice, twisted classes and the 29-point space; all 771 counts at λ = 2, λ = 1 + i and for colourings under random signings agree between the decomposition and an independent elimination; evaluations grow with junctions, never with atoms. | computed | B |

## Recommendation

**Continue** (2/3): native reading of junction handles, in a fresh epic depending on this closure.
- **The question.** Do exact creation maps read the trisum junctions, and the atoms that pay for them? `BRACE-TREE-20261105-001` left
  non-Fano handles unread, and on the knot's spaces they are exactly where counting cost lives.
- **First discriminator.** On the 29-point space of ticket A (Proposition 6) and the edge-atom chains of 47 and 58 points, test whether
  the lines at a junction form a class that creation distinguishes.
- **Alternatives.** A hardness bound in the number of atoms (counting #P-hard with n^ε atoms) (1/3); `GLUE-READ-20261106-001`'s pending
  "reading with the far sides" (2/3, the owner's earlier choice).

The full research-next-steps table is in the decision note.
