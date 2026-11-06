# Tseitin size from cells

Epic `CELL-SIZE-20261020-001`, closed 2026-10-20.

## What was found

The grid argument works for any graph in which every edge lies on a short cycle
(a *cell*) with a short detour around that cycle
([proof](../../proofs/CELL-SIZE-20261020-001B/CELL-SIZE-20261020-001B-P001_cell_theorem/proof.md)).

- **The restriction.** Set well-separated cells to random values.
- **The detour lemma.** Each fixed edge is detoured with bounded congestion,
  so every cut keeps a 1/(L+1) fraction of its edges.
- **What survives.** The tangle of the graph survives at that fraction. The
  degree lemma of `PC-DEGREE-20261020-001` then gives degree Ω(tangle order).
- **The size bound.** Constant kill probability turns that degree into size
  2^{Ω(tw)}. This holds for PC (0/1 basis), PCR (both over characteristic
  other than 2) and resolution.

It applies to:
- **Plane graphs with short inner faces** where any two faces share at most
  one edge, which includes every 3-connected planar graph with short faces:
  2^{Θ(tw)}.
- **d-dimensional grids** [k]^d: 2^{Θ(k^{d−1})}.
- **Graphs excluding a fixed minor**, planar graphs included: 2^{Ω_H(tw)} for
  PCR and resolution.
  - Every such graph of large treewidth contains a linear-size wall as a
    subdivision, by the linear grid-minor theorems.
  - Restriction with parity correction, followed by renaming along subdivided
    paths, carries the wall's bound to the whole graph.
  - This needs no degree bound. With bounded degree it is tight.

## Where this leaves the open problem

Itsykson et al. asked whether general resolution needs size 2^{Ω(tw)} for all
bounded-degree graphs. Their regular-resolution bound is now 2^{Θ(tw)}.
- **For general resolution and PCR** this epic answers it for planar graphs,
  minor-free graphs and d-dimensional grids.
- **All graphs remain open.** The method needs short cycles. Graphs whose
  large treewidth comes from long-cycle (locally tree-like) structure have no
  cell system.

## Recommendation

**Continue** with `GENERAL-SIZE-20261020-001`, which the owner has already
asked for. Its first step is the general case:
- Tseitin hardness transfers through immersions (edge-disjoint path
  embeddings), not only through topological minors.
- That would reduce the open problem to whether large-treewidth graphs immerse
  large expanders.
- An unconditional 2^{tw^{Ω(1)}} for PCR follows from walls and the
  polynomial grid-minor theorem.
