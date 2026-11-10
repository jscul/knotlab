# The atom rule for every knot sphere

Status: Proved, computer-assisted: theorem 1 and the lemmas by hand, with a finite local check and a finite classification computed by
`check.py` (run `atom-rule-a1c`, 3 minutes). Pre-registered in `research/ATOM-RULE-20261110-001/preregistration.md`. Two earlier launches
were stopped and are recorded in the long-running row ATOM-RULE-A1: the first stalled on the automorphism search at K_6, the second on SAT
calls that were not part of the check (deciding the unsatisfiable class, which `SPHERE-SIZE-20261107-001` shows needs resolution size
2^Θ(√n)).

## Setting

An octahedral knot sphere K_k (k ≥ 2) with its Kasteleyn law, and Fano atoms (the Fano plane less a point, uniform signs) spliced at lines
l_1, ..., l_g by compatible splices (`GROW-HANDLE-20261110-001`), the new sides signed so that no face is even. Atom j's **region** is its
four interior faces and its three junction faces; its **gadget** is the region with every line that has a corner at a region face and all
their points. The atoms are **separated** when their gadgets are disjoint. An atom **acts as its line** when it allows on its three outer
points exactly the six patterns the replaced line allowed, and is **transparent** when it allows all eight.

**Theorem 1.** For every k ≥ 2 and separated atoms:
1. each atom acts as its line in exactly one of the four classes of its own handle and is transparent in the other three, whatever the
   classes of the other atoms;
2. if every atom acts as its line, no state satisfies every line;
3. otherwise, in every state that satisfies every line, each acting atom has a face with three agreeing corners in its region.

## Lemmas (by hand)

- **Lemma A (homology).** Each atom is cut off by a separating curve, its three new sides. By Mayer–Vietoris over F2, the first homology of
  the grown surface is the direct sum of the atoms' handles: the sphere less g discs contributes only its boundary curves, which are
  separating, hence null-homologous. So a sign class is a tuple of handle classes, one per atom, and a change in atom i's handle is a flat
  change on sides inside atom i.
- **Lemma B (locality).** An atom's allowed patterns, and its gadget's local system, depend only on the signs of the gadget's sides, up to
  gauge. A change in another atom's handle does not touch them (separated atoms). On the gadget's sphere side, any two Kasteleyn laws
  differ by a gauge change, since that part is a disc; a gauge change flips points or complements lines, which relabels patterns without
  changing their number or the satisfiability of the local system. So each atom's role and local system are functions of its own handle's
  class and of the isomorphism type of its gadget.
- **Lemma C (gadget types).** The sphere side of a gadget (the line's three faces, every line with a corner at one of them, their points)
  lies in the closed stars of the line's three vertices. K_k is the triangular lattice except at six corners of degree four, at mutual
  distance k, so for k ≥ 3 that union of stars contains at most one corner, and its type is fixed by where that corner sits. The
  classification (computed, check 2) finds exactly four types over every line of K_2 to K_8: one only in K_2, and three that appear from
  K_3 on and are the only ones at every size up to K_8, 12 + 12 lines near the corners and the rest regular. No type appears beyond K_3.

## The finite check (computed, check 1)

For every line orbit of K_2 to K_4 and every line of K_5 to K_7, every compatible splice (three bijections, two chiralities), and each of
the atom's four classes: 2,700 splices. In every one, exactly one class acts as the replaced line, its allowed patterns equal to the line's
own, and its gadget's local system is unsatisfiable: no assignment satisfies every gadget line with at most one agreeing corner at each
region face. The other three classes are transparent, with satisfiable local systems.

## Proof of theorem 1

- **Part 1.** By lemmas B and C, an atom's role is that of its gadget type in its handle's class, and check 1 covers every type (every
  line of K_5 to K_7 includes all three types that occur for k ≥ 3, and K_2's types are checked directly): exactly one class acts. By
  lemma A the classes of different atoms vary independently.
- **Part 3.** Let atom j act, and let a state satisfy every line. Its restriction to atom j's gadget satisfies every gadget line. Every face
  is odd (no even face), so if no region face had three agreeing corners, each would have exactly one, a solution of the local system,
  which check 1 shows unsatisfiable. So some region face has three.
- **Part 2.** If every atom acts, every atom allows on its outer points exactly the patterns its line allowed. A state satisfying every
  line then gives the old points a state satisfying every line of the original sphere, which a Kasteleyn law on a sphere forbids
  (`COUNT-SURFACES-20261107-001A` theorem 3). ∎

## Scope and what is not proved

Octahedral knot spheres with separated Fano atoms. Atoms whose gadgets overlap (lines at small distance) are not covered; there the exact
SAT results of `ADDRESS-STEER-20261110-001` stand as computations. That extra units are free when fewer atoms act than there are units
(R-c there) is not proved here. The proof is computer-assisted: lemmas by hand, the local check and classification by exhaustive
computation.
