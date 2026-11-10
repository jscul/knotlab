# Boards of abstract names

Status: Partial (pre-registered 2026-11-10, before any computation and before ticket B's census)

Ticket `BARE-NAMES-20261110-001A`, the challenge of A54.

## Setting

- **Names.** A countable set N with no structure: no letters, no order the law can read.
- **States.** Each pair of distinct names u, v has a neighbour distinction n(u, v), and each name a value s(u) in a finite alphabet.
  The board is the graph of the neighbour distinctions. Where identity distinctions e(u, v) ("one place") are added, they are an
  equivalence that the values and the neighbour distinctions respect.
- **Laws.** A uniform law is a finite set of clause templates applied to every tuple of names alike.
  - A **finitary** clause has finitely many literals.
  - An **existence** clause, "every place has a neighbour with value b", is one infinite clause per name, of the kind Leibniz's rule
    already is.
  - A **count law** reads each place's value and the multiset of its neighbours' values, with existence clauses for its degree.
    The 1,024 Life-like one-bit laws, read without letters, are the count laws of degree four.

## Targets

1. **T1, finitary laws (Ramsey).** Every finitary law that allows a state allows one in which adjacency and values are constant: all
   names pairwise neighbours, or none, with one value; with identity distinctions, possibly all names one place. Corollaries: no
   finitary law forces a place to have a neighbour; a finitary law bounds the degree only by forbidding a homogeneous star, which
   names a degree; no finitary law forces a finite board other than one place.
2. **T2, what the letters draw.** With existence clauses giving every place exactly 2k neighbours, every board is a disjoint union of
   Schreier graphs of F_k: an Euler orientation and k perfect matchings of the oriented double cover, by compactness. So the letters
   draw the degree and the connectivity; their labelling comes free.
3. **T3, unfolding without letters.** A count law allows the universal cover of every component of every allowed board, and
   disjoint unions. So a count law that allows a board with a cycle allows a tree.
4. **T4, connectivity and one named face.** No first-order law (finitary and existence clauses) forces connected boards if one of its
   boards has a component of infinite diameter (compactness). A named square, with coordinates mod 3 and an aperiodic tile set in
   the values, makes every component a plane.
5. **T5, boards are not frozen.** In any state of a count law, two disjoint edges whose ends carry the same pair of values can
   exchange partners, and two far places of different value can exchange names. Both are finite changes, so every neighbour
   distinction and every value is flipped by one. Under the source-aware reading, counted per name, knots involving the board can be
   native, against `BOARD-DIST-20261110-001A`'s frozen boards.

## Known before registration (disclosed)

The Ramsey argument of T1 and the switch of T5 were sketched by hand while this registration was written, before any computation.

## Checks to come

`check.py`: T2's decomposition on random finite 2k-regular graphs; T3's lift of count-law solutions to covers; T5's moves on random
count-law states; T4's square law on small tori.
