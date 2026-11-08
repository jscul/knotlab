# Counting 2-colourings of 3-regular hypergraphs with Pfaffian incidence graphs

[PDF](counting_note.pdf) · [TeX source](counting_note.tex) ·
[independent.py](independent.py) · 10 pages · draft of 31 October 2026

**Results.** Counting the proper 2-colourings of a 3-regular 3-uniform
hypergraph is #P-hard (Fan and Cai), and polynomial when its incidence graph is
planar (Valiant). The note studies the class in between, where the incidence
graph is Pfaffian. That class contains every hypergraph that cannot be
2-coloured, since these are exactly the ones whose incidence matrix is
sign-nonsingular (Seymour; Robertson, Seymour and Thomas).

- **(A)** For every connected non-2-colourable such hypergraph H and every
  edge L, the 2-colourings of H − L can be counted in polynomial time. The
  count is a product over braces of determinants, assembled along trisum trees
  by a three-term "trisum law".
- **(B)** With signed incidences, counting stays polynomial while the signs
  differ from a Pfaffian signing by a twist that does not branch.
- **(C)** Once twists branch, counting is #P-hard on Pfaffian graphs.
- **(D)** It stays #P-hard without any signs.
- **(E)** It stays #P-hard when the incidence graph is a Pfaffian brace.

The hardness proofs build crossings inside Pfaffian graphs. Along the way, every
plain planar piece turns out to be twisted. The Fano plane is the only
non-2-colourable 3-regular 3-uniform hypergraph whose incidence graph is a
brace.

**The intuition.** A 2-colouring of such a hypergraph is a world of a network
of not-all-equal knots, in which every distinction sits in exactly three knots.
Deciding is easy natively, but counting worlds is a different matter. See
[INTUITIONS, lesson 6.2](../../INTUITIONS.md#62-the-worlds-of-not-all-equal-knots).

**Checks.** `python3 independent.py` needs numpy, sympy and networkx. It was
written separately from our research libraries, and it recomputes:
- the soft crossing and its snake multipliers;
- the cube junction and its characteristic polynomial;
- the 2-colourings of K₃,₃ recovered through plain braces;
- sign interpolation;
- Theorem A on compositions of Fano planes;
- the similitude identity in all 32 cases.

It prints `ALL OK` when every part agrees.

**Status and novelty.** Proved in the note. No human expert has reviewed it.
Each theorem's novelty and folklore risk is in the table of the note's last
section. For most theorems we found no prior statement; the Fano uniqueness is
likely known. The record names in that table are folders under
`proofs/` in this repository, each with its own `check.py`.
