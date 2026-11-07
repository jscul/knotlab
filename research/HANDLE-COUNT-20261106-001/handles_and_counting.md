# Do handles govern counting hardness? Decision note

Epic `HANDLE-COUNT-20261106-001`, opened 2026-11-06. Program: complexity.

## The request

The owner asked a new question: do handles govern counting hardness?
- **Background.** Plain Pfaffian triple systems are #P-hard to count (`PLAIN-COUNT-20261031-001`, `PLAIN-BRACE-20261031-001`).
  #col(H − L) is polynomial on every three-fold space (`SEYMOUR-COUNT-20261030-001`). The knot's amplitude is ±5^atoms times Tutte
  numbers of the planar glue (`THREEFOLD-AMPLITUDE-20261030-001`). Native creation reads the tree of Fano atoms (`BRACE-TREE` to
  `GLUE-READ`).
- **Hypothesis.** Planar/Pfaffian glue is tractable and hardness lives in the handles.
- **Goal.** Decide whether the counts are fixed-parameter tractable in the number of Fano atoms (genus), or hard already at bounded genus.
- **Instructions.** Check the classical precedent first and state its provenance. Compute counts by number of atoms on the census and on
  random spaces. Stop when FPT is proved, refuted by a reduction, or reduced to a known theorem.

## Provenance check (done first, 2026-11-06)

The question has two halves, and they have different provenance.

**Genus: reduced to known theorems.**
- Galluccio and Loebl, "On the theory of Pfaffian orientations I" (Electron. J. Combin. 6 (1999) R6), and independently Tesler (J.
  Combin. Theory B 78 (2000)), prove Kasteleyn's claim: the perfect-matching polynomial of a graph of orientable genus g is a linear
  combination of 4^g Pfaffians.
- Cimasoni, "A generalized Kac–Ward formula" (J. Stat. Mech. 2010, arXiv 1004.3158): the Ising partition function (even-subgraph
  generating function) of a graph embedded in a genus-g surface is an alternating sum of 2^{2g} determinants, indexed by spin structures.
- Loebl and Masbaum (Adv. Math. 2011, arXiv 0908.2925) prove this Arf-invariant formula optimal. Pant and Singh (arXiv 2605.21077,
  2026) show (8/3)^g Pfaffians can be necessary, even for cubic bipartite graphs. Junchaya, Lucchesi and Miranda (arXiv 2611.00468,
  2026) bound the Pfaffian number by a symbolic invariant.
- Our counts are even-subgraph sums on the incidence graph B (`TWIST-COUNT-20261030-001A` Lemma 1 at λ = 0, its λ-form in ticket A,
  Lemma 1; the spin-sector form was checked at genus 1 and 2 in `THREEFOLD-SPINSUM-20261030-001A`). So every count in the family
  (any coupling λ, any signing) is computable from 4^g determinants of size O(n): **fixed-parameter tractable in the genus of B, and
  never #P-hard at bounded genus** unless #P-complete problems are polynomial.
- Classification: known (a direct composition of Galluccio–Loebl/Tesler or Cimasoni with the Hadamard form). It is not re-proved; no
  proof family was opened for it.
- No source states it for hypergraph 2-colourings specifically; a search for bounded-genus holographic algorithms found only the planar
  theory (Valiant; Cai, Lu and Xia) and Turner's relaxation of planarity (arXiv 1510.01541).

**Atoms: open, and the subject of the epic.**
- On three-fold spaces with planar glue the genus equals the number of Fano atoms (`THREEFOLD-SURFACES-20261030-001`), so the classical
  route costs 4^atoms determinants there. Yet `SEYMOUR-COUNT` counts #col(H − L) on these spaces in polynomial time at any number of atoms,
  so the genus is not what governs.
- Small separations are classical for perfect matchings (Curticapean, ICALP 2014; Straub, Thierauf and Wagner, 2016). Three-edge tight
  cuts are of that kind, so Fano atoms, attached through three edges, should cost nothing.
- The question that remains: which handles cost, and are counts FPT in the number of atoms? That depends on what the glue's own handles
  (Robertson–Seymour–Thomas junctions) cost and whether atoms bound them.

## Tickets

- `HANDLE-COUNT-20261106-001A` (proof): what junctions cost (Theorem 1), and junctions paid for by atoms and signs (Theorem 2), with
  corollaries for plain three-fold spaces and for Pfaffian systems with signs.
- `HANDLE-COUNT-20261106-001B` (exact computation): counts by number of atoms on the census and on random spaces, by the decomposition
  and by an independent elimination.
- `HANDLE-COUNT-20261106-001Z`: closure.

## Results

| # | Result | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Every count in the family is fixed-parameter tractable in the genus of the incidence graph (4^g Pfaffians); never #P-hard at bounded genus. | known; cited, not re-proved | this note |
| 2 | Three-edge tight cuts (so Fano atoms) cost nothing; each 4-sum junction whose tensor violates the matchgate identity costs a factor 2 at the piece it hangs from: time poly(n)·2^J. At the knot's law only junctions at or above squares with three twisted branches cost. | proved (known techniques; candidate local delta) | A, Theorem 1 and Corollary 1 |
| 3 | J + p ≤ a + \|σ\| − 2 for every simple Pfaffian cubic bipartite graph other than Heawood and every Pfaffian signing σ; attained by the trisum of three cubes with three edge atoms (29 points). | proved (no overlap found) | A, Theorem 2 and Proposition 6 |
| 4 | On plain three-fold spaces every count takes time poly(n)·2^{a−2}; polynomial with planar glue at any number of atoms. Off them, #P-hard with a = 0. | proved | A, Corollaries 2 and 3 |
| 5 | On 257 three-fold spaces (census to 26 points, 80 random with plane glue, 6 larger, 28 fresh with trisum glue) the bound holds wherever it applies, with equality on the 13-point splice, twisted classes and the 29-point space; all 771 counts at λ = 2, λ = 1 + i and for colourings under random signings agree between the decomposition and an independent elimination; evaluations grow with junctions, never with atoms. | computed | B |

## Decision

- **FPT in genus:** yes, classical.
- **Hard at bounded genus:** no.
- **FPT in the number of Fano atoms:** yes on the knot's own plain spaces (new: junctions are paid for by atoms); no on Pfaffian triple
  systems in general (hard with no atom).
- **The hypothesis:** half right. Planar glue is tractable. Pfaffian glue is not tractable by itself: hardness lives in its own handles,
  the 4-sum junctions, and on the knot's plain spaces those are paid for by atoms.

## Next steps (research-next-steps assessment at closure)

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — FPT of counts on the knot's spaces in atoms or genus | **Status:** Successful | Genus: classical FPT, never hard at bounded genus. Atoms: FPT on plain three-fold spaces (J + p ≤ a − 2, sharp at J = 1); not FPT on Pfaffian systems in general (#P-hard with a = 0). Atoms cost nothing; hardness enters at glue junctions. Open: whether 2^J is necessary. |
| Local direction — handle-parameterized counting | Practically complete for the stated question | A lower bound on the exponent would need exponential-time hypotheses, whose status is under review. |
| Broader exploration — the counting arc (complexity program) | Mapped in three layers | Polynomial: the knot's class, unbranched twists, planar glue at any number of atoms. FPT: in branched squares b (λ = 0), in junctions J (any λ), in atoms a on plain spaces. #P-hard: b or J unbounded. |
| Long-term goal — hardness at three places; space from native emergence | Capability gained | Counting cost is located at four-port junctions; three-port (atom) structure is free, because the first matchgate identity lives at arity four. The bridge to native reading of junction (non-Fano) handles is open. |
| Next recommendation — native reading of junction handles | **Next step:** Continue: a fresh epic depending on this closure. Do exact creation maps read the trisum junctions, and the atoms that pay for them? First discriminator: on the sharp 29-point space and the edge-atom chains (47 and 58 points), test whether the lines at a junction form a class that creation distinguishes. | BRACE-TREE left non-Fano handles unread; they are exactly where counting cost lives on the knot's spaces. Alternatives: a hardness bound in the number of atoms (#P-hard with a = n^ε atoms) (1/3); GLUE-READ's pending "reading with the far sides" (2/3, the owner's earlier choice). |
| Interest — that next recommendation | **2/3 — Promising** | Small sharp spaces exist and the creation-map tools are in place; the main uncertainty is whether creation sees junctions at all (a clean negative would also settle it). |
| Execution — that next action | Planned, awaiting the owner | Stop when junction handles are read natively on the edge-atom family, or shown invisible to creation there. |

## Ratio check

Since this epic opened: two artifacts changed a mathematical or empirical conclusion (ticket A's theorems, ticket B's census computation);
administrative artifacts are the closure ledger (Z), the two discovery records and the disposition. Substantive work outweighs
administration.
