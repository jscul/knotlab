# Bond readings on sets as large as the largest knot force the allowed states

## Standard statement

Let G be a graph (here the junction graph, with the outside vertex) and m the largest vertex degree among the junctions. A
permutation of the edges that preserves, for every set X of at most m edges, the size of the smallest cocircuit (bond) containing
X, maps the cut space onto itself. With the growth reading kept, it therefore carries every later round (EXTEND-ROUND, Claim B\*).

## Nearest known result

The advisor's lemma (THREE-RIGID's pre-registration): if bonds of at most three distinctions span the equations, three-way readings
force them. That a binary matroid's cocycle space is spanned by vertex cocycles, and that a vertex cocycle is a disjoint union of
bonds, is classical. Codex's `GROWN-END-READING-20261119-001` and `LATER-BOND-READING-20261119-001` show that no fixed number of
distinctions suffices on every reached stage. This proof gives the bound that does suffice for each stage.

## The statement

For an arrangement a, let K(X) be the smallest bond containing the set X of distinctions, less one, or none. Let m be the largest
number of distinctions held by one junction.

**Theorem M.** If a renaming φ of a's distinctions onto b's keeps K(X) for every X with |X| ≤ m (that is, K_b(φX) = K_a(X)), and b's
junctions also hold at most m distinctions, then φ carries a's equation space onto b's. If φ also keeps the growing end
(EXTEND-ROUND's reading), then by Claim B\* its extension carries every later round.

*Proof.*
1. **A set is a bond exactly when it reads one less than its size.** X is a bond if and only if K(X) = |X| − 1, since a smallest
   bond containing X with |X| distinctions is X itself. So for |X| ≤ m, φ maps bonds of a with at most m distinctions onto bonds
   of b with at most m distinctions, and the same holds for φ⁻¹.
2. **The small bonds span the equations.**
   - The equation space is the cut space of the junction graph, spanned by the junctions' stars.
   - The star of a junction j is the cut δ({j}). A cut whose side is one vertex is a disjoint union of bonds, one for each
     component of the graph with j removed.
   - Each of those bonds holds at most |star(j)| ≤ m distinctions.
   So the bonds of at most m distinctions span a's equations, and likewise b's.
3. **Spans.** φ maps a spanning set of a's equations into b's equations, so it maps a's equation space into b's. The same holds
   for φ⁻¹, and both spaces have the same dimension, so the images are equal. ∎

## What it says, with the hunts

- **Pairs and triples.** If every junction of a stage holds at most three distinctions, pair and three-way readings force the
  equations (m = 3). Junctions here hold more, up to 13 in the census, so triples suffice only where small bonds happen to span.
  The hunt found that on 1,589 of the 25,722 census stages.
- **Unbounded.** The number needed grows only with the largest junction. Codex's constructions that need ever more distinctions
  have junctions holding ever more: in the 239-junction stage each index junction holds 20.
- **The premise.** Read as bond distance over sets of distinctions as large as the largest knot, distance plus the growing end
  carries what grows, every round. Read over pairs, or over any fixed number of distinctions, it does not.
