# The brace dictionary

Status: Proved (exact computation; the prediction fixed in advance is refuted as stated and holds where the tree alone joins the atoms)

Ticket `BRACE-TREE-20261105-001B`, 2026-11-05.

## Question

Native creation between two lines is mutual, one-way or silent (ticket A). Is that relation determined by where the two lines sit in the
tight-cut decomposition? And can the decomposition be read back from native creation alone?

## Dependencies

- **`BRACE-TREE-20261105-001A`.** Native relations, `brace_lib.py`, and the rules inside atoms and across a single cut.
- **`NATIVE-GENUS-20261104-001A/B`.** The creation map, the native count, and the census of three-fold spaces up to 22 points.
- **`THREEFOLD-GRAMMAR-20261030-001A`.** The tight-cut decomposition.

## The place of a pair (fixed before evaluation)

For an ordered pair of lines (a, b) in braces A and B (`dict_lib.Tree.place`):
- **The same brace.** Its type, and each line's role: a *cut line* lies on a cut where its brace receives, an *intact* line does not.
- **Different braces.** Their types, and the arrows along the tree path from A to B: `>` crosses a cut in its direction (from emitter to
  receiver), `<` against it. Also the kinds of braces in between (atom or glue), and each line's role at the cut its brace has on the
  path (emitter, cut line or intact).

**The prediction.** For pairs of atom lines, and for pairs of glue lines, the native relation is a function of the place. Pairs of an
atom line and a glue line are recorded without a prediction, since halos depend on the glue's faces.

**The spaces.** All 50 were computed exactly (every ordered pair of lines):
- the 32 three-fold spaces up to 22 points;
- 18 trees of Fano atoms on the Fano plane, on census 58 and on the prism over an 8-cycle. These cover one to three atoms at points and
  lines, chains, two and three atoms hanging from one atom, and receivers fed by one atom.

## 1. The prediction is refuted as stated

| Pairs | Places | Places with one relation | Pairs | Pairs in such places |
| --- | --- | --- | --- | --- |
| Two atom lines | 82 | 51 | 14,534 | 13,174 |
| Two glue lines | 16 | 10 | 490 | 304 |
| An atom line and a glue line (no prediction) | 70 | 32 | 3,018 | 838 |

## 2. Where the tree decides (all 21 places)

Classifying the braces in between by their type, the split is clean:
- **Same, adjacent, or through atoms only.** The relation is a function of the place at every one of these 21 places (10,074 pairs).
- **Through plane glue.** 36 of 69 places have one relation (3,268 of 4,460 pairs). Every mixed atom-atom place has a doubled square or a
  plane piece between the two atoms.

**The rules.**

| The two lines | Arrows | Pairs | Relation |
| --- | --- | --- | --- |
| Same atom, any roles | — | 4,568 | mutual |
| An emitter's line and a downstream receiver's cut line | `>`, `>>`, `>>>` | 840, 162, 36 | mutual |
| An emitter's line and a downstream receiver's intact line | `>`, `>>`, `>>>` | 1,100, 204, 48 | one-way: the receiver's line creates at the emitter's |
| Two atoms emitting into a common atom | `><` | 432 | mutual |
| Cut lines of two receivers fed by one atom | `<>` | 54 | mutual |
| A cut line and an intact line of two such receivers | `<>` | 72 + 72 | one-way, toward the cut line |
| Intact lines of two such receivers | `<>` | 96 | silent |

Mirror images (arrows reversed, roles swapped) carry the mirror relation.

**Reading.**
- **Direction.** Creation into an atom from upstream reaches only its cut lines. Its intact lines see everything upstream, one way.
- **Siblings and co-receivers.** Siblings (atoms emitting into a common atom) see each other fully. Co-receivers (atoms fed by one atom)
  meet only through their cut lines.

## 3. Glue is silent

- **Plane glue.** Lines of plane pieces and doubled squares never create at each other: 306 of 306 pairs.
- **The exception.** It comes only through a non-Fano handle: in the census class whose glue is the trisum of three cubes, 6 of the 8
  plane-glue pairs whose path crosses the trisum brace create.
- **Census 58** is itself a single brace of a third kind ('other'), and its lines carry every relation.

## 4. Cuts are read in their direction

- **All 50 cuts** between two atoms in these spaces read one way. Every pair of an emitter line and an intact receiver line is one-way,
  from the receiver toward the emitter.
- **So** native creation alone tells which side of each such cut lost a point.

## 5. A reconstruction, fixed here for ticket C

**The source rule** (`dict_lib.source_blocks`):
- **Blocks.** Within each piece of the creative part, take the maximal blocks of mutual creation.
- **Blind sets.** A line a is blind to c when c creates at a and a does not create at c.
- **Keeping.** Keep a block when one of its lines is blind to every line that any other line of the block is blind to.

**Why it should work, from the rules of §2.**
- **Spurious blocks are dropped.** When two atoms hang from one atom, their lines are mutual, so their union with a shared cut line is
  an extra block. Their blind sets (their footprints on the common atom) are incomparable, so that block has no source.
- **Real blocks are kept.** An atom's block has a source: its emitter lines when it sits above receivers, any line otherwise.

**On these 50 spaces.**
- **Without a non-Fano brace (47 spaces).** Kept blocks equal the Heawood braces, and the genus, in all 47. The plain block count
  manages 42: it overcounts by one or more where atoms hang from a common atom.
- **With a non-Fano brace (3 spaces).** Census 58 with a Fano atom, twice, and the trisum class: the rule fails, giving 6, 4 and 8 for
  genus 2, 2 and 3.

## Checks

`check.py` (`result.json`, `dictionary.json`; about twelve minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The dictionary over every ordered pair | 82 atom-atom places (51 with one relation), 16 glue-glue (10), 70 atom-glue (32) |
| 2 | Where the tree decides | 21 of 21 places joined through atoms only have one relation (10,074 pairs) |
| 3 | Glue is silent | 306 of 306 plane-glue pairs silent; through a non-Fano handle, 6 of 8 pairs create |
| 4 | Cut directions | 50 of 50 cuts between two atoms read one way |
| 5 | The source rule | Heawood braces = genus on 47 of 47 spaces without a non-Fano brace |

## What this does not establish

- **Proofs.** The rules are computed, not proved, beyond ticket A's lemma for atoms attached at a line.
- **Through plane glue.** The relation there depends on more than the tree: which cut lines face each other across a doubled square.
- **Non-Fano handles.** Census 58 and the trisum brace carry relations the place does not determine, and the source rule miscounts them.
- **Fresh spaces.** The source rule was found on these spaces; ticket C tests it on fresh ones.

## Novelty

New here: the dictionary, the rules for chains, siblings and co-receivers, native cut directions, and the source rule.
