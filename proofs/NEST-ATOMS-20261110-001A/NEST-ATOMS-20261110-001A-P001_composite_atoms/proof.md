# Composite atoms

Status: Proved by hand (theorem N and lemma U), given two hypotheses that are checked here or in `OTHER-ATOMS-20261110-001D`.
`check.py` (9 seconds) reads every named composite of `research/NEST-ATOMS-20261110-001/preregistration.md` (frozen in commit
`4b27647cb`) at every removed point, in every class: 274 points. The first full launch stopped at an assertion (with the removed point
inside a 4-point thin leaf, that leaf's own sides no longer reach its handle); class representatives are now taken from all sides inside
each top-level group, which keeps every outer side and new side as before. The proof was written after the run.

## Setting

As in `OTHER-ATOMS-20261110-001A`: knot spaces with Kasteleyn laws (no even face), atoms grown by compatible splices with completions
with no even face. A **closed atom** is a closed knot space T with a Kasteleyn law; the atom is T less a point P, grown at a line. T is
**free at P** in a class if each of P's three sides, flipped alone, leaves a satisfiable law; **free** if free at every point in every
class. Lemma 2 of that record does not use the genus of T: the atom allows the replaced line's forbidden pair exactly where T is
satisfiable, and the other six patterns exactly where T is free at P. So a free closed atom with exactly one unsatisfiable class acts as
its line in that class and is transparent in every other, whichever point is removed. Call such a closed atom **good**.

A **host** is a knot sphere with a Kasteleyn law that has, at each of its lines l, a state violating l and no other line (a flat state
at l). The class-forced lattice tori are good: they are free at one point in every class and have one unsatisfiable class
(`OTHER-ATOMS-20261110-001D`, to 40 points), and translations move any point to that one.

## Theorem N (composites are good)

Let a host H carry good closed atoms T_1, …, T_g, each less a point, grown at distinct lines l_1, …, l_g (at any distances), and let T
be the resulting closed knot space. Then T is good: its only unsatisfiable class is the one where every T_j acts, and it is free. So T
less any point is an atom that acts as its line exactly where every atom inside it acts, and is transparent otherwise; and since T is good
again, composites nest to any depth, the outer role being the AND of all the leaves inside.

*Proof.* Each atom constrains H only through its relation on its outer points, the replaced line's or all eight (theorem of
`OTHER-ATOMS-20261110-001A`, part 2).
- **Unsatisfiable classes.** If every atom acts, a state of T satisfying every line gives H a state satisfying every line, which a
  Kasteleyn law on a sphere forbids (`COUNT-SURFACES-20261107-001A` theorem 3). If atom j is transparent, H's flat state at l_j violates
  only l_j, so it satisfies every other replaced line, and it extends inside every atom (each allows the pattern it sees): T is
  satisfiable.
- **Freeness at a point P of H on no replaced line.** For each of P's lines i (a line of H) and every class, H's flat state at i violates
  only i and so extends to T. Flipping P's side in i then leaves i agreeing only at its corner opposite the side: satisfied.
- **At a point P of H on a replaced line l_j.** For P's lines of H, as above. For its side in atom j's line, the new side: flipping it
  negates P's literal in atom j's relation. Where atom j acts, the relation becomes l_j with P's sign flipped, and H's flat state at l_j,
  whose three literals on l_j were equal, now satisfies it; where atom j is transparent, it stays transparent and T is satisfiable there.
- **At a point P inside atom j.** Flipping a side of P changes atom j's law only. By lemma 2 of `OTHER-ATOMS-20261110-001A` (its literal
  correspondence needs no Kasteleyn condition), atom j then allows its line's forbidden pair exactly when T_j with that side flipped has a
  satisfying state, which it has because T_j is free at P. H's flat state at l_j shows one of that pair on l_j's points and violates no
  other line, so it extends to T. ∎

## Lemma U (the units of a composite)

Let a closed atom T of genus g, with N lines and N + 2 − 2g faces, be grown less a point in a space with no even face. In every state
satisfying the atom's lines its region (every face at its triangles) holds at least g − 1 units, where a face with a agreeing corners holds
(a − 1)/2; and at least g where T is unsatisfiable (where it acts).

*Proof.* The region's faces are T's faces, three of them merged with the host's. The atom's N lines agree at N corners, all in the region;
with h agreeing corners of host lines at the junction faces, the region holds (N + h − (N + 2 − 2g))/2 = g − 1 + h/2 units. If it holds
only g − 1, then h = 0, so each junction face's agreeing corners are the atom's; each such face is odd, so in T's terms each vertex of the
removed point's triangle has an odd number of agreeing corners. As in lemma 3 there, its parity is 1 + b_j + b_k, so the removed point is
read as one value by its three lines and T has a satisfying state. ∎

So at the floor of a space made of an outer sphere and top-level groups of genera g_1, …, g_r (G = Σ g_i, floor G − 1 units), each group
holds g_i − 1 units plus one if it acts, at most r − 1 groups act, and the rule one level up is the atom rule again, with groups as atoms.

## What is computed (check.py)

- **Check 1 (the host hypothesis).** On K_2 and K_3 every line has a state violating it and no other (SAT, every line).
- **Check 2 (N1, the frozen claim's points).** At all 128 removed points off the replaced lines, every composite acts exactly in the
  class where all its leaves act, with the replaced line's own six patterns, and is transparent in every other; nested composites too.
- **Check 3 (N2 as stated).** At the 44 points on a replaced line it holds. At the 102 points inside a leaf it fails as stated: the leaf
  cut open by the removed point has six outer points and no role, so the AND read where the leaves are grown leaves it out, while the
  composite still acts in exactly one class.
- **Check 4 (post hoc).** Reading each class on the closed composite, where no leaf is cut open, the composite acts exactly where all its
  leaves act at all 274 points, as theorem N says.

Composites checked: C(2, ·) and C(3, ·) with Fano and thin (2,1,2) leaves, three Fano leaves on K_3, and the depth-two composites D(·).
The stress test (`research/NEST-ATOMS-20261110-001/stress_test.py`) adds C(4, ·) at all 146 of its points.
