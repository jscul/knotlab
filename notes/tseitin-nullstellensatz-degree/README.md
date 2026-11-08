# The Nullstellensatz degree of Tseitin formulas is the toggle width

[PDF](tseitin_ns_degree.pdf) · [TeX source](tseitin_ns_degree.tex) ·
[replay.py](replay.py) · 7 pages · draft of 20 October 2026

**Result.** Let G be a connected graph with an odd charge, and T(G, c) its
Tseitin formula, written as polynomials clause by clause. Over every field of
characteristic other than 2, the Nullstellensatz degree of T(G, c) equals the
*toggle width* of G. This is the least k such that the empty vertex set can be
turned into the whole vertex set by adding or removing one vertex at a time,
where toggling v at the set U costs |δ(U) ∪ E(v)|. When G has at least three
vertices, the toggle width lies between cutwidth + 1 and
cutwidth + ⌊Δ/2⌋. So on graphs of maximum degree at most three the degree is
exactly **cutwidth + 1**. Over characteristic 2 it is the maximum degree Δ. In
the ±1 encoding, with degree measured after reduction, the degree is exactly
the cutwidth.

**The intuition.** The odd unit of charge can be moved anywhere by flipping
edges along a path, so no small window sees the contradiction. A refutation
has to carry the charge across a layout of the graph, and the widest boundary
it must cross is the degree it needs. See
[INTUITIONS, lesson 5.2](../../INTUITIONS.md#52-how-deep-a-hole-is).

**Checks.** `python3 replay.py` uses only the standard library. On ten graphs,
including K₃,₃ and the Petersen graph, it:
- verifies the explicit sweep refutation as a polynomial identity over the
  integers;
- verifies the lower-bound design over F₃, F₅ and Q against every axiom
  multiple of the relevant degree;
- recomputes each degree independently by Gaussian elimination over F₂
  and F₃;
- checks the graph lemmas and the ±1 statements;
- runs controls that must fail, such as even charge.

It exits with status 0 when every check passes.

**Status and novelty.** Proved in the note. No human expert has reviewed it.
After a targeted search we did not find the main theorem, its corollary for
degree three, or the ±1 statement stated before. The methods (sweeping
refutations, character-sum designs, monotonicity of submodular games) are
standard. We would be glad to learn of prior statements.

The note's footnote mentions the research workspace where the proofs were
first checked. That workspace is private, but `replay.py` is self-contained.
