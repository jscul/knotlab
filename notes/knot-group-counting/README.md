# Counting homomorphisms from knot groups to solvable groups can be #P-hard

[PDF](rowell_note.pdf) · [TeX source](rowell_note.tex) · [link checks](links/) ·
14 pages · version of 6 November 2026, prepared for arXiv

**Results.** For a finite group G and a link L in S³, let H_L(G) be the number
of homomorphisms from π₁(S³ ∖ L) to G. Rowell conjectured in 2009 (Conjecture
3.2(b)) that H_L(G) can be computed exactly in polynomial time from a diagram
whenever G is solvable. Unless every #P function is computable in polynomial
time, this fails.

- **On links** it fails already for S₃, and for every dihedral group of
  order 2n with n odd. Tying torus knots into the components and cabling some
  of them turns the count into a Potts model. This needs unboundedly many
  components.
- **On knots**, where metabelian targets are easy, counting is #P-hard for S₄,
  the smallest group for which this can happen, and for its double covers
  GL(2,3) and 2O. The S₄ proof rests on a "bicycle law" for transposition
  colourings of alternating diagrams with tripled crossings.
- **Fitting height two.** Counting is #P-hard for UT₃(F₄) ⋊ C₃, and for the
  Heisenberg groups H(F_p) ⋊ C_r (p odd) whose action has a "hard pair" of
  eigencharacters. Without a hard pair the count is polynomial, both for knot
  groups and for closed 3-manifolds with bounded first homology.
- **Approximation.** For UT₃(F₄) ⋊ C₃ the reduction preserves approximation, so
  approximating the count is #BIS-hard.

**The intuition.** In the Heisenberg families, hardness appears exactly when a
twisted obstruction joins three nontrivial characters at once. Borromean
surgery (three components, pairwise unlinked) supplies that interaction, and
everything pairwise stays countable. This is a statement about counting, not
about knots in the program's sense. See
[INTUITIONS, lesson 6.3](../../INTUITIONS.md#63-patterns-in-three-dimensions).

**Checks.** The [links/](links/) folder checks the link results end to end:
the sector formula, cables, local knots, the Potts and colouring reductions
for S₃, and the same reductions for D₅ and D₇. It also includes a separate
brute force of the two smallest instances. Run `python3 run_all.py` there; it
needs numpy and takes about three minutes. The knot results rest on the proofs
listed in the note's last section, which are in this repository under
`proofs/`. The note's replay driver,
`proofs/ROWELL-NOTE-20261026-001/ROWELL-NOTE-20261026-001-P001_note/replay.py`,
reruns all ten of their checks from here (about five minutes). Two reviews with separately written code reproduced the main
numbers. Both were done by AI systems, and they are no substitute for expert
review.

**Status and novelty.** Proved in the note. No human expert has reviewed it.
We found no earlier refutation of Conjecture 3.2(b); Kuperberg and Samperton
(2018) called it doubtful but open.

The note builds on earlier work:
- Galindo (2026) proved hardness for every non-abelian group on closed
  3-manifolds, with hard instances whose first Betti number grows; the note
  treats link and knot complements and bounded homology;
- Livingston (1995) proved the identity that the note re-proves for S₄ lifts;
- Moussard (2017) gave the rational precursor of the steering formula.
