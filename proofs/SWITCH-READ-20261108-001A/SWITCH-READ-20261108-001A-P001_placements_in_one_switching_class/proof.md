# Placements in one switching class

Status: Proved (exact computation on the placements HANDLE-COUNT A's generator gives TRISUM-READ's glues; five pairs mapped)

Ticket `SWITCH-READ-20261108-001A`, 2026-11-08.

## Question

- **Where it came from.** In TRISUM-READ one frozen statement failed in one space: the native creation map had a symmetry that moves
  an atom to another incidence of its glue while keeping the signing's switching class. That suggested a conjecture (backlog B5 of
  the goals doc): the native creation map of a plain space depends on the signing of its glue only through its switching class.
- **The test.** Two placements of the atoms on one glue, in one switching class, should then give the same native creation map.

## Dependencies

- **`TRISUM-READ-20261107-001A`, B and C.** The spaces, their stored maps, the generator's hash-seed dependence, and the fixed-order
  enumerator (`order_lib.py`).
- **HANDLE-COUNT A's generator** (`families.py`): a trisum brace (the glue), a Pfaffian signing, a signing with fewest signs in its
  switching class, and a Fano atom on every signed incidence.

## Setting

- **Placements.** The generator's Pfaffian signing walks sets, so the minimal signing it returns, and with it the incidences that
  carry atoms, depends on Python's hash seed. The glue does not. A placement class is a class of the generated spaces up to
  isomorphism.
- **One switching class.** Two signings are in one switching class when they differ by the edge set of a cut of the glue's incidence
  graph: switching at a point complements its value, and switching at a line flips all three of its literals, which the knot's law
  does not see.
- **Comparing maps.** The glue's lines keep their indices in every placement; the atom lines are appended after them. So the block of
  glue lines can be compared entry by entry. The whole maps are compared up to isomorphism of coloured complete digraphs, with the
  glue's lines fixed or under any bijection. Each line's row and column multisets are an invariant that decides most cases.

## Results

1. **The placements (check 1).** Under hash seeds 0 to 23, every one of the 17 glues comes out the same, and its Pfaffian and minimal
   signings all lie in one switching class. Eleven glues get two or three placements that are not isomorphic as spaces, 25 in all.
2. **The glue block sees only the switching class (check 3).** In each of the five pairs mapped here (seeds 36, 192, 246, 240 and 354,
   38 to 56 points), removing a glue line and gluing at a glue line gives the same order-free vector in both placements, entry by entry.
3. **The whole map sees the placement (check 3).** In each pair the whole native maps are not isomorphic, neither with the glue's lines
   fixed nor under any bijection.
4. **Where the difference lies.** Removing a glue line creates at the atom lines with the same multiset of vectors in both placements.
   Removing a line of an atom creates differently at some glue lines: which glue lines see K4^(3), and which are degenerate, follows
   the atom's incidence.
5. **TRISUM-READ's frozen statements transfer (check 4).** P1 to P7 hold on all five alternative placements: the atoms, the junctions
   and the leaves are read there as in the stored placements.

## Reading

- **Native creation splits in two.** Creation among glue lines sees only the switching class of the signing, which is what Pfaffian
  counting sees. Creation started by removing an atom's line reads where that atom sits.
- **Why atom removals see more.** An intact Fano atom acts on the glue as one negated incidence (ATOM-ONE), and switching-equivalent
  signings give the glue the same solutions up to complementing points. Removing a line of an atom makes it transparent and frees its
  incidence, and which incidence is freed is exactly what the placement records. This is a reading, not yet a proof.
- **What this means for TRISUM-READ.** Its junction signature uses only glue removals and gluing at glue lines, so it belongs to the
  glue block. Its atom reading uses atom removals, yet it held on every alternative placement too. Its one failure, seed 5's
  loaded line, is a placement that a symmetry of the glue moves, not a general blindness.
- **Doctrine.** Everything here is invariant under relabeling lines and re-listing their points.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; TRISUM-READ's tickets Proved | pass |
| 1 | The placements under hash seeds 0 to 23 | one glue and one switching class each; 11 glues with 2 or 3 placements |
| 2 | Two rows of each alternative map, recomputed | equal |
| 3 | The five mapped pairs | glue block identical; whole maps never isomorphic; differences only from atom removals |
| 4 | P1 to P7 on the five alternative placements | all hold |

## What this does not establish

- **The other placements.** Nine more placements, 56 to 60 points, are being mapped in the background and will be folded in.
- **A proof.** The glue block's invariance is computed on five pairs, with a mechanism read from ATOM-ONE, not proved.
- **Other signings.** Only placements that the generator returns are compared, not every minimal signing of each class.

## Novelty

- **New here.** The comparison and the split of native creation into a switching-class part and a placement part.
- **Classical.** Switching classes of signed graphs (Zaslavsky); Pfaffian signings of a matching-covered bipartite graph form one
  switching class, checked here directly for each glue.
