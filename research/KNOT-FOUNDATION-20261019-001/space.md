# Whether contact structure becomes space-like

Ticket `KNOT-FOUNDATION-20261019-001D`, 2026-10-19. This decision note answers
the epic's last question. It gives short proofs and machine checks
(`PYTHONPATH=tools python3 -B -m knotlab space`; tests `SpaceTest` in
`tests/test_knotlab.py`). Everything uses the canonical forgetting reading of
the knot test.

## The question, made precise

A system's contact structure is read from its allowed states alone:
- a **free set** is a set of variables whose every assignment the system
  allows;
- the free sets form a simplicial complex, which we call the system's
  **shape**;
- a **bond** is a set of three or more variables that the system constrains
  while every smaller part is free: a knot inside the system;
- a **tie** is a constrained pair whose variables are each free.

"Space-like" would mean that the shape, or the pattern of bonds, behaves like
a space: low-dimensional, with local neighborhoods.

## Answer

The contact structure has intrinsic holes, paths and a native measure of
separation. It does not produce space by itself.

- **Bonds are intrinsic.** They depend only on the allowed states, not on how
  the clauses are written. The four-loop witness chain has clauses that touch
  three variables at a time. With its witnesses forgotten, its only bond is
  all five visible variables.
- **A knot is a hole.** A knot on m variables makes its shape a hollow
  simplex, an (m − 2)-dimensional sphere. The two-loop knot is a circle:
  three free pairs around a missing whole. This makes "one knot is the first
  atomic logical topology" literal.
- **Bonds compose into a bond or into nothing.** Take two bonds that share
  one distinction and forget the shared one. The result is either a bond
  among the rest or no constraint at all, never anything in between. Of the
  1,156 pairs of two-loop knots, 1,084 give a bond and 72 give nothing. For
  single clauses this is the resolution rule: they compose exactly when they
  hold the shared distinction to opposite values.
- **Bond size measures separation.** Along a chain of atoms, the smallest
  bond joining the ends grows by one per step (3, 4, 5). Bond size is a
  native, presentation-independent measure of how far apart two distinctions
  are.
- **Logic allows every shape.** Every simplicial complex is the shape of some
  system: the system whose allowed states are the complex's faces. This was
  checked on 200 random complexes. Logic therefore selects no space; whatever
  space a system has comes from its law.
- **The shape's holes are not all knots.** Two pairwise ties, a = c and
  b = d, surround a circle with no bond at all. Knots are the shape's atomic
  holes: its minimal missing sets of three or more. Its other holes can come
  from plain logic.

  In the knot sense, "2-clauses cannot be part of any topology" holds, since
  no 2-CNF system has a bond. In the sense of the shape's holes it does not.
  The foundation uses the knot sense: topology begins at bonds.

Space-like structure would need a law that is uniform, local and
low-dimensional without being written on a space in advance. That is the
open problem studied by causal sets (Bombelli, Lee, Meyer and Sorkin 1987),
quantum graphity (Konopka, Markopoulou and Smolin 2006) and hypergraph
rewriting (Wolfram 2020). Nothing here gives a shortcut.

## Proofs

1. **Bonds are minimal.** A bond's proper subsets are free, so no bond
   contains another.
2. **A knot is a hollow simplex.** Every proper subset of a knot's variables
   is free and the whole is not. That family is the boundary of a simplex,
   a sphere of dimension m − 2.
3. **Composition.** Let A, B, c and c, D, e be bonds, and take the composite
   on A, B, D and e. Each three-variable part of it is free. Take (A, B, e)
   as an example:
   - any value of (A, B) extends to some c in the first bond, because its
     pair (A, B) is free;
   - any value of (c, e) extends to some D in the second bond, because its
     pair (c, e) is free.

   So the composite is a bond or nothing. For single clauses the composite is
   the resolvent, which exists exactly when the shared variable appears with
   opposite signs.
4. **Separation along a chain.** The composite of a chain of k atoms is a
   single clause on its k + 1 loops and its end, so it has size k + 2. A set
   that leaves out one of the chain's loops can set that loop false, which
   frees the end, so no smaller set joins the ends. This was checked for up
   to three atoms.
5. **Every shape.** Let K be a simplicial complex, and consider the system
   whose allowed states are K's faces. It allows every assignment of a set S
   exactly when S is a face. If S is a face, each pattern on S is the face
   made of its true elements. Conversely, the all-true pattern on S needs a
   face containing S. This is the classical fact that a down-closed family
   shatters exactly its own members.
6. **Ties surround a hole.** The square's shape is the join of two
   two-point spaces, which is a circle.

## Nearest known results

- Free sets are the sets a family of assignments shatters (Vapnik and
  Chervonenkis 1971; Sauer 1972; Shelah 1972). Bonds are the minimal
  non-shattered sets of size three or more.
- For linear systems, bonds are the circuits of a binary matroid, and sharing
  a circuit is an equivalence relation (Whitney 1935).
- Composition is resolution (Robinson 1965).
- The join of spheres is a sphere.
- Space from non-spatial rules: causal sets, quantum graphity and hypergraph
  rewriting.

Novelty: `known-overlap-found`. The new part is the reading: knots are the
shape's atomic holes, and one knot is literally a circle.

## Stop rule

This ticket adds classical facts plus a reading. Ticket B dissolved under the
forgetting reading, and ticket C added classical facts plus a reading. The
epic's stop rule is therefore met: the foundation stands as a clean reading of
known logic. The write-up is `docs/FOUNDATION_READING.md`.
