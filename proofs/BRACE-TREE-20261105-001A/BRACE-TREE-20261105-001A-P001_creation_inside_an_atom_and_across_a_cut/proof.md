# Creation inside an atom and across a cut

Status: Proved (the block lemma for atoms attached at a line is proved; the rest is exact computation)

Ticket `BRACE-TREE-20261105-001A`, 2026-11-05.

## Question

Native creation separates handles that plane glue keeps apart (NATIVE-GENUS B). Where atoms touch, does it still see each atom as a
whole, and does it see which way the cut between them faces?

## Dependencies

- **`NATIVE-GENUS-20261104-001A`.** The creation map, the splitting lemma and `genus_lib.py`.
- **`HANDLE-LOCALITY-20261103-001A/B`.** The interface lemma (a knot space minus a line forces that line's points to the constant pair)
  and the screening lemma (one bit across a cut reduces creation to the closure).
- **`THREEFOLD-GRAMMAR-20261030-001A`.** The tight-cut decomposition (`grammar_lib.decompose`).

## Terms

- **The native relation of two lines a and b.** It is *mutual* when removing either creates at the other, *one-way* when only one
  direction creates, and *silent* when neither does.
- **The decomposition.** The tight cuts split a space into braces (`brace_lib.braces`).
  - A brace lost a line at a cut when its contracted vertex there is a line: it emits there.
  - A brace lost a point when its contracted vertex is a point: it receives there.
- **Cut lines.** A receiving brace's cut lines are its three lines through that point; its other lines are intact.

## 1. The Fano plane alone (exact)

- **Complete.** Every removal creates at every other line, so the 21 pairs of lines are all mutual and the seven lines form one block.
- **By far side.** Of the 42 ordered entries, the Fano far side creates at 42, census 58 at 42, census 6 at 14, K4^(3) at none.
- **Census 58 for contrast.** Its three pairs of lines sharing two points, (0, 2), (1, 6) and (3, 7), are silent. Of its other 25 pairs,
  12 are mutual, 12 one-way and one silent.

## 2. The block lemma for atoms attached at a line (proved)

**Statement.** Let a Fano atom Y be attached at a line l of the rest R of a space (Y is the Fano plane split at a point, and receives).
For any two lines M, L of Y, removing M creates at L exactly as in the Fano plane.

**Proof.**
- **R forces its ports.** With Y collapsed to l, the space is R plus l, and it fails, since Y acts as l (interface lemma). So R is a
  knot space minus the line l, and its solutions take l's points to the constant pair: one bit crosses the cut.
- **R is untouched.** Neither M nor L lies in R.
- **Screening.** The screening lemma (HANDLE-LOCALITY B, §1) then says that creation at L, with M removed, equals creation on Y's closure
  minus M. Y's closure is Y with its point restored: the Fano plane. ∎

**Corollary.** By §1, the lines of an atom attached at a line form one block in every space.

**Checked** on the 6 designs with such an atom: 42 of 42 entries equal the Fano plane's, each time.

## 3. Atoms attached at a point (computed)

- **The obstacle.** For an atom X attached at a point, the rest lost a point. It acts as the line X lost, but it passes the cut a line's
  six patterns rather than one bit, so the screening lemma does not apply. This is the unproved half of NATIVE-GENUS A's splitting
  lemma.
- **Checked.** On all 10 designs with such an atom, 30 of 30 entries equal the Fano plane's, and the atom's six lines form one block.

## 4. Across a cut between two atoms (computed)

- **The spaces.** The 12 designs and every three-fold space up to 19 points (21 spaces), with 17 cuts between two Heawood braces.
- **The pairs.** For each cut, every line a of the emitting atom against every line b of the receiving atom:

| b | Pairs | Relation |
| --- | --- | --- |
| a cut line of the receiver | 294 | mutual, every time |
| an intact line of the receiver | 382 | one-way, every time: b creates at a, a never creates at b |

- **Reading.** Creation runs one way across a cut, against its direction. The receiving atom's lines create at the emitter's, but a
  removal in the emitter cannot create inside the receiver, except at the receiver's lines through the shared point.

## 5. Lines sharing two points (computed)

- **Silent every time.** Two lines sharing two points (a doubled square) never create at each other, in either direction: 40 of 40
  pairs in the same spaces, plus census 58's three pairs alone.
- **What that matches.** A doubled square is plane glue, and plane glue never creates.

## Reading

- **Atoms are blocks.** Each Fano atom's lines create at one another in both directions, wherever the atom sits, so native creation sees
  it whole. For atoms attached at a line this is a theorem.
- **Cuts have a direction.** Across a cut, creation is mutual only at the receiver's cut lines and one-way elsewhere, from the receiver
  toward the emitter. So native creation reads which side of a cut lost a point.
- **Doubled squares are silent.** Native creation sees glue inside a space as silence.
- **Doctrine.** These are relations between lines, read from creation; no distance or orientation in space is assumed.

## Checks

`check.py` (`result.json`, about five minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The Fano plane and census 58 alone | Fano: 21 of 21 pairs mutual; census 58: its three doubled pairs silent |
| 2 | Atoms attached at a line | 6 designs, 42 of 42 entries equal to the Fano plane's each |
| 3 | Atoms attached at a point | 10 designs, 30 of 30 entries equal to the Fano plane's each |
| 4 | Across a cut | 17 cuts: cut lines mutual (294 of 294), intact lines one-way (382 of 382) |
| 5 | Lines sharing two points | 40 of 40 pairs silent |

## What this does not establish

- **Atoms attached at a point, in general.** Their block property and the one-way rule are computed, not proved.
- **Atoms that are not Fano planes.** Census 58 is itself a single brace of another kind; its lines are not one block.
- **Larger spaces.** Every space here has at most 20 points.

## Novelty

New here: the native relations and their exact values inside atoms, across cuts and at doubled squares. The block lemma for atoms
attached at a line is a corollary of the screening and interface lemmas.
