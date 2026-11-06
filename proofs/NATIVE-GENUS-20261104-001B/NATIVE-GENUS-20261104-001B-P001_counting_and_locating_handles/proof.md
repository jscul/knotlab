# Counting and locating handles

Status: Proved (exact computation on families fixed before evaluation)

Ticket `NATIVE-GENUS-20261104-001B`, 2026-11-04.

## Question

Can native selection count a space's handles and say where they are, from its creation map alone?

## Dependencies

- **`NATIVE-GENUS-20261104-001A`.** The creation map, the splitting lemma and `genus_lib.py`.
- **`THREEFOLD-SURFACES-20261030-001A/B`.** The genus of a three-fold space is its number of Fano atoms on plane glue, and the exact
  genera of every three-fold space up to 22 points.
- **`THREEFOLD-GRAMMAR-20261030-001A/B`.** The census of three-fold spaces up to 22 points, rebuilt here as in THREEFOLD-SURFACES B.

## The statistic (fixed before evaluation)

- **The quiet part.** A largest set of lines among which no removal creates at a gluing line, in either direction. Every largest set is
  enumerated.
- **The creative part.** The lines outside the quiet part.
- **The native count.** The number of pieces of the creative part, in two versions:
  - **Through points.** Two creative lines are joined when they share a point.
  - **Through interior points.** A point is interior when all three of its lines are creative. Interior points are joined along creative
    lines.
- **Blocks (exploratory, without a prediction).** Within each piece, the number of maximal sets of creative lines that create at one
  another in both directions.
- **Ground truth.** The SAT genus of the incidence graph.

## Predictions recorded before evaluation

- **One atom.** The quiet part is unique, and the creative part is one piece in both versions.
- **Separated atoms.** When no two atoms' cuts share an edge, the count through interior points equals the number of atoms and the SAT
  genus, and each piece lies inside one atom.
- **Touching atoms.** When two atoms' cuts share an edge, they merge.

## 1. Single atoms (720 spaces)

- **The family.** The Fano plane at every point and every line of the cube, the prisms over 6- to 12-cycles and the 16-point grid (112
  spaces). Census 58 minus each of its 8 lines at every point, and split at each of its 8 points at every line, of the cube and the
  prisms over 6- and 8-cycles (288). On the cube also with the five other orders of its ports (320).
- **The quiet part is unique in all 720.**

| Atom | Spaces | Through points | Through interior points | Blocks |
| --- | --- | --- | --- | --- |
| The Fano plane, at a point or a line | 112 | 1 | 1 | 1 |
| Census 58, split at point 0 or 5 | 76 | 1 | 1 | 10 |
| Census 58, other elements | 456 | 1 | 1 | 6 |
| Census 58 minus line 4 or line 5 | 76 | 1 | **2** | 2 |

- **Through points, every single atom is one piece (720 of 720).**
- **Through interior points, 76 census-58 atoms split into two.** Census 58 has three pairs of lines sharing two points, and one pair of
  disjoint lines, 4 = (6, 7, 2) and 5 = (4, 3, 1). Removing one of the disjoint pair makes the other quiet. Then only points 0 and 5 are
  interior, and they share no creative line. This refutes the first prediction for the interior version.
- **Blocks.** A Fano atom is one block: all its lines create at one another. Census 58 is not.
  - Its lines sharing two points never create at each other, in either direction.
  - So its creative lines split into many small blocks: 6, or 10 when it is split at point 0 or 5 and no line is quiet.

## 2. Pairs (486 spaces)

- **The family.** Two Fano atoms at every pair of positions on the prisms over 8- and 10-cycles: two points, two lines, or a point and a
  line (310). On the prism over an 8-cycle, census 58 with a Fano atom or with a second census 58, at every ordered placement (176).
- **The quiet part is unique in all 486, its complement holds only atom lines, and the genus is 2 in all 486.**

| Placement | Spaces | Through points | Through interior points | Blocks |
| --- | --- | --- | --- | --- |
| Fano, separated, lines not meeting | 220 | 2 | 2 | 2 |
| Fano, two lines sharing a point | 36 | **1** | 2 | 2 |
| Fano, a point on the other's line (touching) | 54 | 1 | 1 | 2 |
| Census 58 with Fano, separated, lines not meeting | 80 | 2 | 2 | 7 or 11 |
| Census 58 with Fano, two lines sharing a point | 32 | **1** | 2 | 11 |
| Census 58 with census 58, separated | 40 | 2 | 2 | 16 |
| Census 58 with census 58, touching | 24 | 1 | 1 (8) or **2** (16) | 52 or 16 |

- **Separated atoms (408).** Through interior points the count is 2 in all 408, with each piece inside one atom. The second prediction
  holds.
- **Atoms meeting at a base point (68).** When two atoms attached at lines share a point of the glue, the shared point lies on a creative
  line of each, so the count through points merges them. The count through interior points does not, since that point also lies on a
  quiet glue line.
- **Touching atoms (78).** Through points they merge, all 78, as predicted. Through interior points 62 merge and 16 census-58 cases do not.
- **Blocks.** Every Fano pair has exactly 2 blocks (310 of 310), touching pairs included.

## 3. Triples (60 spaces)

- **The family.** Three Fano atoms on the cube: at three points (4), at three lines (4), at two points and a line (24), at a point and two
  lines (24). On the prism over an 8-cycle: at three points (3), and at two points and a line off both (1).

| Placement | Spaces | Through points | Through interior points | Blocks |
| --- | --- | --- | --- | --- |
| Separated: the prism, and three points of the cube | 8 | 3 | 3 | 3 |
| Separated: three lines of the cube | 4 | **1** | **1** | **1** |
| Touching one pair (cube) | 24 | 1 or 2 | 2 | 3 |
| Touching two pairs (cube) | 24 | 1 | 1 | **2** |

- **Separated triples.** Through interior points, 8 of 12 are counted 3 and located.
- **The exception refutes the second prediction.** Three atoms at three of the cube's four lines leave the glue one line. The largest quiet
  sets then have a single line (22 of them), and the whole space is one piece and one block.
- **Touching triples merge**, as predicted.

## 4. Atoms on atoms (21 spaces)

- **The family.** A Fano atom attached to the Fano plane at a point or a line (2), to census 58 at every point and line (16), and two Fano
  atoms on the Fano plane: at two points, at a point and a line, and one attached to the other (3).
- **The genus is the number of atoms plus one in all 21:** the base is an atom too.
- **The count.** Through points it is 1 in all 21, with several largest quiet sets in each. Through interior points it is 1, or 2 for some
  largest quiet sets on census 58. Nothing separates atoms that touch with no glue between them.
- **Blocks.**

| Space | Genus | Blocks |
| --- | --- | --- |
| The Fano plane with a Fano atom at a point, or at a line | 2 | 2 |
| Census 58 with a Fano atom | 2 | 6 or 10 |
| The Fano plane with Fano atoms at a point and at a line | 3 | 3 |
| The Fano plane with a Fano atom, and another on that atom | 3 | 3 |
| The Fano plane with Fano atoms at two points | 3 | **4** |

- **The overcount.** At two points, the two atoms create at each other in both directions, so besides one block per atom, their union
  with one base line is a block too.

## 5. Every three-fold space up to 22 points (32 classes)

- **The census.** The 8 untwisted and 24 twisted classes of THREEFOLD-GRAMMAR B, rebuilt as in THREEFOLD-SURFACES B. Each twisted class
  carries its twisted incidence as a sign, and each fails. Atoms touch in most of them, with doubled squares or small plane pieces as glue.

| Classes | Genus | Count (through points, through interior points) | Blocks |
| --- | --- | --- | --- |
| The Fano plane | 1 | (1, 1) | 1 |
| 13 points (two Fano planes spliced) | 2 | (1, 1) | 2 |
| 19 points (three Fano planes): 3 classes | 3 | (1, 1) | 3 |
| 19 points: 1 class | 3 | (1, 1) | **4** |
| Twisted 14, 15, 18 points and the twisted 20-point class 10 | 2 | (2, 2) | 2 |
| Untwisted 21 and 22, twisted 21 (class 0) and 22 (classes 0, 1) | 3 | (3, 3) | 3 |
| Twisted 20 (6 classes) and 21 (5 classes) | 3 | (2, 2) | 3 |
| Twisted 20 (4 classes), depending on the largest quiet set | 3 | (1, 1) or (2, 2) | 3 |
| Twisted 21, class 1, depending on the largest quiet set | 3 | (1, 1) or (2, 2) | **4** |
| Twisted 22, class 2 (glue: the trisum of three cubes) | 3 | (2, 2) | **10** |

- **The count equals the genus in 10 of 32.** In the other 22 it is lower, so some atoms share a piece. Which braces touch was not
  computed here.
- **The trisum class.** The count is 2, its number of Fano atoms, while the genus is 3. The trisum of three cubes adds a handle that
  creation does not see as an atom.
- **Blocks equal the genus in 29 of 32,** where atoms touch as well. The exceptions are two classes with one extra block and the trisum
  class.

## Why the count works on separated Fano atoms

The splitting lemma (ticket A) reduces the count to facts about one atom at a time.
- **The glue side is quiet.** Two glue-side lines involve no atom, so their entries are those of the plane glue, which never creates.
- **Every Fano line is creative.** With the atom alone, every line of a Fano atom is created by some removal in the glue. This was checked
  separately on the 56 single Fano atoms of the cube and the prisms over 6- to 10-cycles; it is not part of `check.py`. By the splitting
  lemma, the same holds with the other atoms present.
- **No piece reaches two atoms.** A point of the glue lies on a glue line, so it is never interior. When the cuts share no edge, a line of
  one atom holds no point of another, so no interior point is shared and no creative line joins two atoms.
- **Each atom is one piece.**
  - At a point, the four points off the removed line are interior, and any two lie on a common line of the atom.
  - At a line, the six points of the split atom are interior and are joined along its lines.
- **What is computed rather than proved.** That plane glue never creates, that every Fano line is created from the glue, and that no
  other largest quiet set exists.

## Answer

- **Separated handles: yes.** On plane glue, the lines outside the largest creation-free set fall into one piece per atom whenever atoms
  are separated, counted through interior points. The pieces are the atoms, so the count also locates them: 416 of 420 separated spaces.
- **Where it stops.**
  - **Touching atoms merge**, with no glue line between them to stay quiet.
  - **Glue too thin.** Three atoms on the 4-point cube leave one glue line, and merge.
  - **Joining.** Through shared points, atoms meeting at a glue point merge too. Through interior points, census 58 can split, because a
    quiet line inside it cuts its interior points apart.
- **Blocks (exploratory).** Within a piece, maximal blocks of mutual creation separate touching Fano atoms in most small three-fold
  spaces (29 of 32). They overcount by one where two point-attached atoms hang from one Fano atom, and undercount on the 4-point cube.
  Census-58 atoms break into several blocks.

## Reading

- **Native selection sees non-planarity locally.** Plane glue never creates, the glue creates at every Fano line, and the splitting lemma
  keeps atoms apart. So the creative lines are the handles' lines, and their pieces count them.
- **What the count reads.** It reads Fano atoms, not genus as such: on the trisum class it gives 2 for genus 3.
- **Touching is the limit of the count, not of creation.** Inside a piece, mutual creation still separates most touching Fano atoms
  (blocks). It overcounts where two point-attached atoms create at each other in both directions.
- **Census 58's internal silence.** Its lines that share two points (a doubled square inside it) never create at each other. Native
  creation sees that plane piece inside the atom, but the block count then miscounts the atom.

## Checks

`check.py` (`result.json`; `detail.json` holds every space; about two hours with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | 720 single atoms | genus 1 everywhere; one piece through points everywhere; through interior points all but 76 census-58 atoms |
| 2 | 486 pairs | separated: 2 through interior points, located (408 of 408); touching: 1 through points (78 of 78) |
| 3 | 60 triples | separated: 3 and located in 8 of 12, the 4 others on the cube |
| 4 | 21 atoms on atoms | genus = atoms + 1; counts and blocks recorded |
| 5 | 32 three-fold classes | the count equals the genus in 10; blocks in 29 |

## What this does not establish

- **Proofs.** That plane glue never creates, that every Fano line is created from the glue, and that the glue side is the unique
  largest quiet set are computed, not proved.
- **Larger spaces.** Every space here has at most 26 points, since creation is exact by enumeration.
- **Blocks.** They are exploratory: recorded before evaluation but with no prediction, and with no proof of why they separate touching
  atoms.
- **Other non-planar braces.** The trisum of three cubes is met only once, in one census class.

## Novelty

- **New here.** The native count, its exhaustive test on small plane glue and on the census, and the blocks of mutual creation.
- **Classical.** Genus counts handles; here a process internal to the logic recovers that count, using no embedding. No comparable
  statement is known to us.
