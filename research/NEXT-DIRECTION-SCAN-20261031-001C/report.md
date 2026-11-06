# Lane C: counting one line short of Seymour's bound

Ticket `NEXT-DIRECTION-SCAN-20261031-001C`, 2026-10-31. Scouting pass (documentation); no theorem is activated.

## Question

- **Seymour's bound.** A minimally non-2-colourable hypergraph has at least as many lines as points (Seymour 1974). The knot's spaces, the
  non-colourable cubic triple systems, sit on the bound.
- **Theorem 1 of the note.** #col(H − L) is computable in polynomial time for every connected non-colourable cubic triple system H and line
  L. That is a system with n points and n − 1 lines.
- **The lane's question.** Is there a counting question one line short of the bound beyond Theorem 1? The discriminator: are general
  deficiency-one systems trivially #P-hard, and does every structured subclass reduce to Theorem 1 or to the hardness theorems?

## Results

`short.py` checks two reductions from counting on cubic triple systems. That problem is #P-complete (Fan–Cai 2020, recorded in
SOFT-CROSS-20261031-001B).

1. **Disjoint union.** #col(Fano − L) = 10. Adding Fano − L to any cubic system H0 gives a system with one line fewer than points and
   #col = 10 · #col(H0). Checked on six systems: K4^(3), the 6- and 8-prism systems, Möbius–Kantor, Pappus and Fano.
2. **Point splitting (connected).**
   - **The construction.** Take a point v of a connected cubic system H0. Let H1 move v to a new point v′ on one of its three lines, and let
     H2 add the line {v, v′, w} with a new point w.
   - **Properties.** Both are connected, 3-uniform, of degree at most 3, with one line fewer than points. Both are also *Seymour-sparse*:
     every nonempty set of lines spans more points than lines (checked exhaustively on every split).
   - **The identity.** #col(H0) = 2 #col(H1) − #col(H2): H1 counts colourings with v = v′ once and v ≠ v′ once, while H2 weighs them 1 and 2.
   - Checked on all 54 splits tried (three points and three lines each, on six systems).
3. **Contrast.** On the Fano plane, the knot's smallest space, every H − L has exactly 10 colourings (Theorem 1's class).

**Consequence.** Counting 2-colourings is #P-hard on deficiency-one triple systems by a two-query reduction. This holds even for connected
Seymour-sparse ones of degree at most 3, which are all 2-colourable by Seymour's theorem. One line short of the bound, only the knot's
subclass is known to be easy.

## What is left

- **H − L for a colourable connected cubic H.** This subclass is not of the split form above, since H − L has three points of degree 2.
  - Its complexity is not settled here. In the Hadamard basis it is the even-subgraph sum avoiding one line vertex, so no knot-specific
    structure is visible.
  - It is the colourable-side counterpart of Theorem 1. Settling it would not touch native emergence.
- **Seymour-sparse systems** are settled: they contain the split systems H1 and H2, so counting on them is #P-hard. H − L, for H connected
  and cubic, is the Seymour-sparse subclass with exactly three points of degree 2.

## Interest as a standalone epic

**1/3 — Exploratory poking.** General deficiency one is hard by a routine reduction. The remaining subclass is a counting question about
colourable systems, with no visible native content. Theorem 1 already captures the knot's part.

## Files

- `short.py`: the checks (run with `--write`).
- `results.json` and `short.log`: the output.
