# Natively a Fano atom is homogeneous

Status: Proved (an exhaustive finite check on top of ATOM-ONE A; computed confirmation on the saved and fresh Fano trees)

Ticket `GENUS-READ-20261107-001B`, 2026-11-07.

## Question

- **The approved aim.** Prove that FAR-READ B's rule returns exactly the Fano atoms of every Fano tree.
- **What is already proved.** On Fano trees satisfying CHAIN-TRANSFER C's condition N, the twin steps give the atoms. ATOM-ONE proved
  that every atom acts as one from outside.
- **What remained.** Whether the split step ever cuts an atom of six or seven lines. That depends only on the far-side vectors inside
  the atom.
- **The complication.** Ticket A showed census 6's column depends on gluing order. So the question must be asked natively, with census 6
  counted over its gluings.

## Dependencies

- **`GENUS-READ-20261107-001A`.** The native vector, and the six-order verdicts (`gluing_lib.py`).
- **`ATOM-ONE-20261107-001A`.** Every closed side shows exactly its lost element, up to signs, and the configuration model
  (`atom_lib.py`).
- **`CHAIN-TRANSFER-20261106-001C`.** The twin rule on Fano trees, and the tree builder.
- **`ATOM-ONE-20261107-001B`.** Its bound (`bound_lib.py`), here read at every order of the gluing line.
- **FAR-READ B's frozen rule** (`rule_lib.py`, bound by hash).

## The composition (`inside_lib.py`)

- **Closed sides.** By ATOM-ONE A, a closed side shows its lost element exactly: equality of copies behind a lost point, not-all-equal
  behind a lost line. Its deep points add singles (channels plus one point) and pairs (channels plus two).
- **Inside an atom.** Creation at a line b of the atom, with a line a of the atom removed, is an OR over masks of b's points with one or
  two further points (PENDANT-LINE A). Those points are the atom's own variables, deep points of one side (alone, in pairs, or with an
  atom variable), and deep points of two sides.
- **Exactness.** The solutions join through each cut's channels, so these masks are exactly the real ones.
- **Checked (check 1).** On 12 built Fano trees (stars, two levels, two cuts meeting) the model's native vectors inside the centre atom
  equal the exact creation map's at all 420 ordered pairs. Relabeled masks agree with six separate verdicts.

## The states a Fano-tree side can show (check 2)

- **How a side is built.** A closed side of a Fano tree is a Fano atom with closed Fano-tree sides of its own.
- **Its state.** That is the union of what its atom's own points show (with exact children, a leaf's state) and what its children's deep
  points show through it, singly and in pairs.
- **The union is finite.** Starting from the leaves and hanging children until nothing new appears, it is reached in three rounds.
  - **Behind a lost point:** 2 singles and 5 pairs.
  - **Behind a lost line:** 4 singles and 32 pairs.
- **Every state lies between the leaf's and the union.** Every side contains its adjacent atom's own points, so its state includes the
  leaf's.

## Theorem (native homogeneity)

**In every Fano tree, every ordered pair of lines of a Fano atom gets one and the same native vector:** no K4^(3); census 6 at one of its
three gluings (two of the six orders); the Fano plane; census 58.

*Proof.*

1. **Masks are monotone in the states.** A larger state gives a superset of masks, and creation is an OR. So the real vector lies, far
   side by far side and order by order, between the vector with a leaf behind every cut (the floor) and the vector with the union behind
   every cut (the ceiling).
2. **Floor equals ceiling (check 3).** For all 253 configurations of a Fano atom (up to collineations), floor and ceiling agree at all
   2,990 ordered pairs, and every one is the vector stated. ∎

**Remark.** By 2-transitivity, the bare Fano plane gives every ordered pair the same vector too (ticket A, check 3). The theorem says
nothing behind an atom's cuts can break that symmetry.

## Corollaries

1. **The split step cuts atoms natively.**
   - **Acting as one natively (check 5).** ATOM-ONE B's bound holds at every order of the gluing line: deep points of the removal's
     side never change creation, and change far sides only in its exception. With a free port relation, which is what reaches every
     atom of a Fano tree, they change nothing at any order. So every atom of a Fano tree acts as one natively from outside, census-6
     count included.
   - **Why the split fires.** Inside an atom every line sends every other line the same native vector, and the atom acts as one from
     outside. So every subset of three or more lines acts as one.
   - **What the split then does.** It partitions every atom of six lines as 3 + 3 and every atom of seven as 3 + 4. FAR-READ B's frozen
     rule, given native vectors, cuts atoms.
2. **Its success rested on census 6's listing order.**
   - **The stored order.** Census 6's verdict, in the order each line happens to be written, scattered across an atom's ordered pairs.
     BRACE-TREE A counted 14 of 42 in the Fano plane alone.
   - **What that scatter did.** It broke every split into parts acting as one.
3. **On Fano trees the native reading is the twin rule.** CHAIN-TRANSFER C proves that yes/no twins return the atoms (and the directed
   tree) of every Fano tree satisfying condition N, for instance every one whose atoms have at most four cuts. Whether creation occurs does
   not depend on gluing (ticket A). The far sides add nothing inside atoms.

## Computed confirmation (check 4)

On the 23 saved and fresh Fano-tree spaces (102 atoms, 88 of them with six or seven lines), with native maps:
- **Inside atoms.** All 3,376 ordered pairs carry the native vector.
- **From outside.** Every atom acts as one natively, 102 of 102.
- **The yes/no two-stage rule** reads all 23 spaces.
- **FAR-READ B's frozen rule** reads all 23 with census 6 in its stored order and none with native vectors. In every space it cuts an
  atom of six or seven lines.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The composition is exact | 420 of 420 ordered pairs on 12 built trees; relabeled masks = six verdicts |
| 2 | States of Fano-tree sides | union reached in 3 rounds: P (2, 5), L (4, 32) |
| 3 | Native homogeneity, 253 configurations | floor = ceiling = the native vector at 2,990 of 2,990 pairs |
| 4 | The saved and fresh Fano trees | 3,376 of 3,376 native; 102 of 102 act as one; twin rule 23 of 23; frozen rule natively 0 of 23 |
| 5 | ATOM-ONE B's bound at every gluing order | creation never changes; far sides only in its exception; free port relation: nothing at any order |

## Reading

- **A Fano atom is one thing, inside and out.**
  - **From outside.** It acts as one (ATOM-ONE).
  - **Inside.** Natively, all its lines are alike to one another, at every ordered pair.
  - **So** the four far sides see no internal structure at all. The structure FAR-READ's split relied on was the listing order of
    census 6.
- **What reads a handle.** On Fano trees the handles are read by twins, from whether creation occurs alone. Which far side creates adds
  nothing there.
- **Doctrine.** The native vector is invariant under rewriting any line's points in another order. Nothing in it depends on a
  representation.

## What this does not establish

- **Spaces with plane glue.** Ticket C measures them. Native homogeneity inside atoms there is not proved, because the sides are not
  Fano-tree sides.
- **Fano trees violating condition N.** For those the twin rule is not proved (CHAIN-TRANSFER C).

## Novelty

- **New here.** Native homogeneity, the reachable states, and the correction of the split step.
- **The theory's.** The composition rests on the project's PENDANT-LINE A and ATOM-ONE A.
