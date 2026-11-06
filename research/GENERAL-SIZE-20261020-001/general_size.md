# Tseitin size on all graphs: the barrier

Epic `GENERAL-SIZE-20261020-001`, closed 2026-10-20.

## What was found

The epic was a bounded idea search on the open problem: do resolution and PCR
need size 2^{Ω(tw)} for Tseitin formulas on every bounded-degree graph? Its
stop condition was that no restriction keeps a large tangle without short
cycles. That condition is met. The findings are in the
[proof](../../proofs/GENERAL-SIZE-20261020-001B/GENERAL-SIZE-20261020-001B-P001_immersions/proof.md).

- **Immersions transfer hardness, but do not help.**
  - Resolution and PCR size moves from G to any graph weakly immersed in it,
    at a 2^{O(Δ)} factor. Identifying vertices is a weakening.
  - The problem reduces to graphs of maximum degree 3, by the degree-3
    sparsifier of Chekuri and Chuzhoy. There, immersions are topological
    minors.
- **All graphs.** Every graph needs 2^{Ω(tw^{1/9}/polylog tw)}. This uses
  walls and the Chuzhoy–Tan grid-minor theorem. It is new for PCR as far as we
  know.
- **The reduction.** The open problem, up to polylog factors, follows if every
  subcubic graph has a topological minor, keeping its treewidth up to polylog
  factors, that is either:
  - *cellular*: short cycles with short detours; or
  - *compact*: few vertices beyond its treewidth.
- **The obstruction.** Take walls joined along an expander by bundles that
  reverse blocks of b ports and permute each block.
  - **Compact minors fail.** A genus–crossing separator bound shows
    tw(H)² = O(m(|V(H)| + mwb)) for every topological minor H. So once
    b ≤ w/polylog, no compact minor keeps the treewidth.
  - **Cells only at scale √b.** The cells there have length about √b. The
    natural cellular minors lose a factor √b.
  - **The cell method's loss is inherent.** Its loss equals the cell length:
    kill rate times tangle retention is about 1/L.
- **Not counterexamples.** Uniform bundles have a compact ladder minor, with
  spectral gap near 0.04. Ordered bundles are cellular.
- **Candidate counterexample.** At b ≈ √w neither case survives, so these
  networks are the candidate counterexample and the cheapest test case.

## Corrections to earlier records

- **Grids for resolution were already known.** Dantchev and Riis
  ([Planar tautologies hard for resolution](https://www.cs.le.ac.uk/people/ssd6/FOCS01/paper.pdf),
  FOCS 2001) proved 2^{Ω(n)} for resolution on Tseitin formulas of the n × n
  grid.
  - `PC-SIZE-GRID-20261020-001` credited grid resolution bounds only to
    bounded-depth Frege. `CELL-SIZE-20261020-001` reported no resolution
    statement on grid graphs. Both are wrong for the two-dimensional grid and
    resolution.
  - As far as the searches show, Dantchev–Riis does not cover the PCR
    results, other planar graphs, minor-free graphs or grids of dimension at
    least 3.
- **Lemma 5 of `CELL-SIZE-20261020-001B-P001`.** It holds in multiplicative
  form, size(T(W)) ≤ O(size(T(G))), because only the axioms a refutation uses
  need a derivation. Its stated additive form is vacuous when the graph has
  exponentially many vertices. Corollary 6 there stays true.
- **Regular resolution.** The bound is 2^{Ω(tw)} up to a polynomial factor for
  all graphs (Itsykson, Riazanov and Smirnov, SAT 2022).

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — 2^{Ω(tw)} for Tseitin on all bounded-degree graphs | **Status:** Partially successful | Proved:<br>• an unconditional PCR bound for all graphs;<br>• a reduction to cellular-or-compact minors;<br>• a family on which the compact case fails.<br>The open problem is not settled. |
| Local direction — restrictions plus renaming through topological minors | Practically exhausted at polylog precision | On block-scrambled wall networks, compact minors fail. The cell method loses the cell length, about w^{1/4}. Accepted results stay. |
| Broader exploration — Tseitin lower-bound techniques | Known alternatives, not assessed here | Two alternatives exist:<br>• Dantchev–Riis's grid argument, which uses no cell restrictions;<br>• bounded-depth Frege through grid minors (Galesi et al.).<br>Neither has been tried on the obstruction family. |
| Long-term goal — breaching proof-complexity barriers | Obstruction learned | Restriction methods need short cycles or compactness. The obstruction family isolates what a new method must handle. |
| Next recommendation — Tseitin lower bounds | **Next step:** Research directions. Read the Dantchev–Riis argument and decide, in one bounded session, whether it extends to two targets:<br>• planar graphs beyond rectangular grids;<br>• block-scrambled wall networks.<br>Compare this with converting the PC-degree and PCR-size results into a note. | If the argument extends, it attacks the barrier directly. If it is tied to rectangular geometry, conversion or a pivot wins. |
| Interest — that search | **2/3 — Promising** | A known argument is already tight on grids without cells. The main uncertainty is how much it relies on grid geometry, and whether anything carries over to PCR. |
| Execution — that search | Deferred | Awaits the owner. Bound: one session. Stop if the argument depends essentially on rectangular geometry. |
