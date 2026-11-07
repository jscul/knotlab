# A Fano atom with a line removed is transparent

Status: Proved (an exhaustive finite check on top of KNOT-COMPOSE A's cut theorem, as corrected by NATIVE-PATHS A; computed confirmation on
the saved spaces)

Ticket `ATOM-ONE-20261107-001A`, 2026-11-07.

## Question

- **Background (FAR-READ A).** Every Fano atom acts as one from outside: every line of another atom receives the same far-side vector
  from each of its lines. This was computed on 1,065 atoms and is not proved.
- **The first half of a proof.** What does an atom send through its cuts when one of its lines is removed, and does it depend on which
  line?

## Dependencies

- **`KNOT-COMPOSE-20261101-001A`, Theorem 4(1), as corrected by `NATIVE-PATHS-20261101-001A`, item 3.** Across every nontrivial 3-edge
  cut of a knot space, the point side accepts exactly one antipodal pair {v, v̄} of patterns on its three ports, and the line side
  accepts exactly the six other patterns.
- **`GLUE-READ-20261106-001A`.** The tight-cut structure of a space (`port_lib.py`).
- **`FAR-READ-20261106-001A`.** The saved spaces (`far_lib.py`, which loads GLUE-READ B's maps).

## Setting

- **Knot spaces.** These are connected cubic systems with no not-all-equal colouring (THREEFOLD-SPACES).
- **Fano atoms.** A Fano atom is a Heawood brace of the tight-cut decomposition. Some of its points and lines are contracted, one for
  each of its cuts.
  - **A line-type cut.** The atom lost a line there; the side beyond acts as that line on three of the atom's points.
  - **A point-type cut.** The atom lost a point there; the side beyond holds the point's three copies, one on each of the atom's lines
    through it.
- **Closed sides.** A side is closed when the removed line is not in it.
- **The relation sent.** The atom's side of a cut, with a line removed, allows some patterns on the cut's channels. That set is the
  relation it sends.
- **Signs.** A signed Fano plane carries a sign on each of its 21 incidences. Flipping a point or a line (all three literals of a line)
  changes no colouring question, so signs count up to these flips.

## Theorem (transparency)

**In every knot space, a Fano atom with any one of its lines removed sends the free relation through each of its cuts.** On a cut with
three distinct channels that is all eight patterns, and on a cut whose two channels are one point it is all four. In particular the
relation is the same whichever line is removed.

*Proof.*

1. **Closed sides act as their lost elements.**
   - By KNOT-COMPOSE A as corrected, a closed point side accepts exactly one antipodal pair: its channels are copies of one point, up to
     signs.
   - A closed line side accepts exactly the six other patterns: it is not-all-equal on its channels, up to signs.
   - So the atom with all its closed sides restored is a signed Fano plane K. This holds whichever cut its sides meet, including two
     contracted elements that share a channel.
2. **K is the plain Fano plane.**
   - The whole space has no colouring, so K has none.
   - Of the 256 sign classes of the Fano plane exactly one has no colouring, the plain plane (check 1). So K is the plain Fano plane
     after flipping some points and lines, and flips map free relations to free relations.
3. **The relation sent.**
   - Remove a line a of the atom, and let X0 be one of its cuts.
   - The other sides are closed and enter only through their channels, so the atom's side of X0 accepts exactly what K minus X0 minus a
     accepts on X0's channels.
4. **Freeness.** In the Fano plane, removing any line together with any other element leaves the other element's three variables free,
   in all 91 cases (check 2). ∎

## The knot is needed (check 3)

- **The test.** Drop step 1 and let the other cuts carry arbitrary nonempty complement-closed relations.
- **When it still holds.** Over all 253 ways to contract the Heawood graph (up to collineations), the relation sent is the same
  whichever line is removed for every atom with at most one line-type cut: 134 of 134 (configuration, cut) pairs.
- **When it fails.** With two or more line-type cuts, only 209 of 1,609 pairs are invariant for every relation.
- **The criterion.** For every pattern on the outgoing cut, the complement-pair patterns of the other cuts compatible with it must not
  depend on the removed line. Singleton products show this is also necessary.
- **What carries the theorem.** The exact relations that the knot imposes on closed sides.

## Computed confirmation (check 4)

On the 191 saved spaces (GLUE-READ B):
- **Closed sides.** All 1,014 closed sides at Fano atoms' cuts are as stated:
  - 594 line sides on three ports, which accept six patterns;
  - 374 point sides on three ports, which accept one antipodal pair;
  - 46 point sides whose two channels are one point, which accept one antipodal pair on two ports.
- **The relation sent.** For all 6,058 (atom, cut, removed line) triples, the atom's side sends the free relation.

## Reading

- **An atom is all or nothing from outside.**
  - With all its lines present, a Fano atom constrains its cuts exactly as one lost element would.
  - With any one line gone, it constrains nothing that any cut can see.
  - No partial state shows through a cut. So the rest of the space cannot tell which line went, as far as port relations go.
- **This is the knot's own property, lifted to the atom.**
  - The Fano plane is not only minimally non-colourable: removing any line frees every other element completely.
  - In the knot test's terms, the atom behaves like a single knot whose constraint vanishes as soon as one of its lines is forgotten.
- **What this gives acts-as-one.** Any port relation a removal in the atom causes elsewhere is the same for every line of the atom.
  Ticket B shows that a Fano atom's lines see only such relations, apart from one exception.
- **Doctrine.** Cuts, channels and relations are relations among lines and points. No space is assumed.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Signed Fano planes | 256 sign classes; exactly one knot, the plain plane |
| 2 | Freeness | 91 of 91 |
| 3 | The knot is needed | at most one line-type cut: 134 of 134 invariant; more: 209 of 1,609 |
| 4 | Computed, 191 saved spaces | 1,014 of 1,014 closed sides as stated; 6,058 of 6,058 free |

## What this does not establish

- **Deeper relations.** The deep points of an atom's side do depend on which line was removed, as FAR-READ A's glue lines show. Ticket B
  bounds what they can do at Fano atoms' lines.
- **Non-Fano handles.** Braces other than the Heawood graph are not treated.

## Novelty

- **The cut theorem is the project's** (KNOT-COMPOSE A, NATIVE-PATHS A).
- **New here.**
  - The classification of signed Fano knots: one class.
  - The transparency theorem.
  - The control showing that the knot is needed.
- **Provenance.** That the Fano plane is the unique smallest non-2-colourable 3-uniform hypergraph, and that it is critical, is classical.
  No statement of the uniqueness of its signed version or of transparency was found.
