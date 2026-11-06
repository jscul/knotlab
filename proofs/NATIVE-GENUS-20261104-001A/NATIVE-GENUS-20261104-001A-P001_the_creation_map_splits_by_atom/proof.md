# The creation map splits by atom

Status: Proved (the splitting lemma is proved for untouched atoms attached at a point and checked for untouched atoms attached at a line)

Ticket `NATIVE-GENUS-20261104-001A`, 2026-11-04.

## Question

A space with several atoms has a creation map: for each removal M and gluing line L, whether gluing a far side at L creates a new knot.
Does this map split into one part per atom?

## Dependencies

- **`HANDLE-LOCALITY-20261103-001A`.** The interface lemma: an intact atom offers its cut exactly the patterns of the vertex it replaced.
- **`HANDLE-LOCALITY-20261103-001B`.** The screening lemma, and the join method for exact creation.
- **`STRIP-RELAY-20261103-001A`.** The reduction lemma, proved for the transfer and the pipeline. Exact creation was compared there only on
  one small junction.
- **`RELAY-NET-20261104-001A`.** Its library, used here for the plane pieces and exact creation.

## Setting

- **Designs.** A design is a base (plane glue, or any knot space) with atoms attached at 3-edge cuts.
  - **An atom** is a census knot space, the Fano plane or census 58, with one element removed.
  - **Attached at a base point,** it loses a line. The line's three points replace the base point on its three lines, which become the
    atom's cut lines. The atom emits there.
  - **Attached at a base line,** it is split at one of its points. The base line's three points replace that point on the atom's three
    lines through it. The atom receives there.
- **The twist.** Each new incidence takes the sign under which an intact atom acts as the vertex it replaced: s(base line, point) +
  s(atom line, point).
- **Keys.** Every point and line keeps a key from build to build, so the space with any subset of the atoms can be compared with the full
  space entry by entry.
- **The creation map.** C(M, L) is defined for lines M ≠ L.
  - **Where L shows all six patterns** in the solutions of the space minus M, C(M, L) says whether splicing L into one of the four census
    far sides creates a new crossing knot of up to three points (join method, exact).
  - **Otherwise** C(M, L) counts as no creation.
- **Touching.** An entry touches an atom when M or L is one of that atom's lines, on the atom's side of its cut. The cut lines of an atom
  attached at a point lie on the base side.

## 1. The interface (checked for every element)

| Atom | Minus a line: ports take exactly the two constant patterns | Split at a point: exactly the six others |
| --- | --- | --- |
| The Fano plane | 7 of 7 lines | 7 of 7 points |
| Census 58 | 8 of 8 lines | 8 of 8 points |

- **The first column holds for every knot space.** Since the atom fails, every solution of the atom minus a line violates that line, so
  the line's literals are constant. Both constants occur by complement symmetry.
- **So an intact atom acts as the vertex it replaced.**
  - With the twist above, the three cut lines see one value, as they would see the point.
  - The base line's points see exactly the six patterns the line allowed.

## 2. The creation map does not depend on how L meets the far side (computed)

The far side is spliced at L by joining L's i-th point to the far side's i-th line through its removed point, so the order of L's points
could matter.

| Space | Cases | Union over far sides unchanged by all six orders | Census-6 far side alone unchanged |
| --- | --- | --- | --- |
| prism(4): Fano at a point and at the farthest line | 315 | 315 | 143 |
| prism(4): Fano at a point and at a line through it | 315 | 315 | 145 |
| The Fano plane with a Fano atom at a point | 156 | 156 | 42 |

- **The union is unchanged.** Taken over the four far sides, creation does not depend on the order (786 of 786).
- **One far side alone can change.** The census-6 far side alone does depend on it. The other three far sides alone do not.

## 3. The splitting lemma

**Statement.** In a design, C(M, L) equals the entry in the space that keeps only the atoms holding M or L.

**Proof for untouched atoms attached at a point.**
- **One bit crosses.** Let X be an atom attached at a point and holding neither M nor L. X is intact in the space minus M, so its ports
  take one constant pair (§1). So X's cut carries one bit.
- **Screening.** The screening lemma (HANDLE-LOCALITY B, §1) applies with P the side holding L. Creation at L equals creation on P's
  closure, which is the space with X replaced by its point.
- **Induction.** Collapsing X leaves the other atoms' cuts intact. Repeat for every untouched atom attached at a point. ∎

**Untouched atoms attached at a line.**
- **The solutions are unchanged.** Such an atom's split excludes exactly the constant pair (§1). So, by the join lemma, the rest of the space
  has the solutions it would have with the line restored.
- **Creation is not covered.** The cut carries a line's six patterns, more than one bit, so the screening lemma does not apply. Creation is
  checked below. It also matches HANDLE-LOCALITY B's observation that an intact atom attached at a line never changes creation outside
  it, which was left unexplained there.

**Exact check (13 designs).** Every entry was compared with the space keeping only the touched atoms: 5,130 entries, no disagreement.
- **Nontrivial comparisons.** 4,102 of them are with a space where at least one atom was collapsed. The other 1,028 touch every atom.
- **Designs with an atom attached at a line.** Seven, including two receivers sharing a point, an emitter touching a receiver, and a
  receiver on the Fano plane.
- **Plane glue alone never creates** in any of the eleven plane designs.

| Design | Points | Neither line in an atom | One atom | Two atoms |
| --- | --- | --- | --- | --- |
| prism(4): Fano at a point + at the farthest point | 20 | 56 | 252 | 72 (full) |
| prism(4): Fano at a point + at the farthest line | 20 | 42 | 254 | 84 (full) |
| prism(4): Fano at a line + at the farthest disjoint line | 20 | 30 | 252 | 98 (full) |
| prism(4): Fano at two lines sharing a point | 20 | 30 | 252 | 98 (full) |
| prism(4): Fano at two points of one line | 20 | 56 | 252 | 72 (full) |
| prism(4): Fano at a point + at a line through it (touching) | 20 | 42 | 254 | 84 (full) |
| prism(5): census 58 at a point + at the farthest line | 24 | 72 | 368 | 112 (full) |
| prism(5): Fano at a point + census 58 minus line 3 at the farthest point | 23 | 90 | 332 | 84 (full) |
| cube: Fano at three points | 22 | 12 | 234 | 216 |
| prism(4): Fano at two points + at a line off both | 26 | 42 | 368 | 240 |
| The Fano plane: Fano at a point | 13 | 42 | 114 (full) | — |
| The Fano plane: Fano at a point + at a line off it | 19 | 30 | 228 | 84 (full) |
| Census 58: Fano at a point | 14 | 56 | 126 (full) | — |

"Full" marks entries that touch every atom of the design, compared with the full space itself.

## Consequences

- **Halos split.** A removal in atom X creates at base-side lines exactly as it would with X alone: its halo is X's own. Two atoms'
  halos can overlap as sets of lines, but each line of the map belongs to one removal, so to one atom.
- **Sites split.** A removal in the base creates at the lines of atom X exactly as it would with X alone.
- **Atoms interact only through entries where one holds M and the other holds L.**
- **On plane glue, atoms attached at a line have no halo.** In every plane design their removals create at no base-side line, against 4 to
  7 lines for atoms attached at a point (check 4). This is HANDLE-LOCALITY B's "a handle attached at a line never creates outside
  itself". On the Fano plane as base they do create at its lines (6), which are creative themselves.

## Reading

- **Native selection sees each atom one at a time.** Whatever it creates involves at most the two atoms holding the removal and the
  gluing line. Every other atom behaves exactly like the vertex it replaced.
- **This is a statement about the logic, not about a picture.** Collapsing is the interface lemma: an intact atom passes its cut exactly a
  point's pattern or a line's pattern.

## Checks

`check.py` (`result.json`, about nine minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Interface for both atoms at every element | 15 of 15 removed lines, 15 of 15 split points |
| 2 | Order of the gluing line's points | the union over far sides is unchanged in 786 of 786 cases; census 6 alone is not |
| 3 | Splitting, exact, on 13 designs | 5,130 entries, no disagreement; plane glue alone never creates |
| 4 | Halos per atom | 3 to 7 base-side lines for atoms at a point, none for atoms at a line |

## What this does not establish

- **Exact creation for untouched atoms attached at a line, in general.** It is checked on seven designs, not proved.
- **That plane glue never creates.** This is computed here and in HANDLE-EMERGENCE, not proved.
- **Other atoms.** Only the Fano plane and census 58 are used as atoms.

## Novelty

- **New here.** The splitting lemma for spaces with several atoms (a corollary of the interface and screening lemmas), the order
  independence of the creation map, and the exact checks.
- **Classical analogue.** Splitting along one-bit separations, as for 2-sums of matroids.
