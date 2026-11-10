# Which gates the families read

Status: P1, P2 and lemma C proved by hand; the census computed exhaustively per network (SAT over every state of every class pair).
`check.py` (24 seconds), as frozen in `research/GATES-20261110-001/preregistration.md` (commit `6c0331519`). Lemma C and the last section
were written after the run.

## Setting

Two stored acting bits in thin-torus leaves (2,1,2), each in one of its four classes; networks of components, three parity names and one
top constraint (8 signed not-all-equal lines or 2 parity knots); the reading O is 1 when the network has no satisfying state. Five frozen
families: F1 (cut only, one network), F2 (names only, 4,320), F3 (a cut and a name, 7,200), F4 (a satisfiable host, 13,860) and F4′ (one
stored bit, 17,710).

## By hand

- **P1.** F1 is K_2 with both leaves cut in: by theorem N of `NEST-ATOMS-20261110-001A` it has no satisfying state exactly when both act. ∎
- **P2.** A component with no satisfying state leaves the whole network without one, whatever the names and the top say, since names only
  add constraints. A leaf's closed torus in its acting class, and K_2 with an acting leaf cut in, have none. So O = 1 when either leaf acts
  in F2 and F3, and when leaf 2 acts in F4; in particular O(1, 1) = 1 throughout, and no function that is 0 at (1, 1) (XOR, NAND, NOR,
  equivalence, and five more) is read by one network of these families. ∎
- **Lemma C (monotone through a cut).** If a leaf is cut into a component and no name reads a point inside the leaf, the reading cannot be
  0 where the leaf acts and 1 where it is transparent. The leaf's inner points occur only in its own lines, so it constrains the rest only
  through the relation on its outer points (lemma 2 of `OTHER-ATOMS-20261110-001A`): the line's six patterns where it acts, all eight
  where it is transparent. A satisfying state in the acting class therefore restricts to an assignment of everything else that extends in
  every transparent class. ∎ So a negation of an acting bit needs a name that reads inside a cut leaf; family F4′ tries every naming of the
  seven points of its component, inner points included.

## The census

| Family | Networks | Functions of the acting bits read (networks) | Depending on more than the acting bits |
| --- | --- | --- | --- |
| F1 | 1 | AND (1) | 0 |
| F2 | 4,320 | OR (4,184) | 136 |
| F3 | 7,200 | OR (6,942) | 258 |
| F4 | 13,860 | a_2 (13,812) | 48 |
| F4′ | 17,710 | 0 (17,599), a_1 (34), 1 (77) | 0 |

P1, P2 and P3 (OR in F2 and F3) held. **P4 failed: no network of F4′ reads NOT a_1.** It reads a_1 in 34 networks, a contradiction
created by names exactly where the leaf acts even though the host torus is satisfiable, but never the opposite. No P2 violation: the
failure line was not crossed.

## What the class-sensitive networks read (post hoc)

The 136 networks of F2 whose reading depends on more than the acting bits read finer facts about the classes. Twenty-four of them read,
besides the other leaf's acting bit, whether one leaf's class is one of the two classes (1,0) (its acting class) and (0,1): the classes
whose two bits differ. That is the parity of the leaf's two class bits, a reading that is not monotone in them. The rest read joint
conditions on both leaves' classes. So names see the full class of a closed leaf, and they see it through parity.
