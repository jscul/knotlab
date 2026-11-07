# What screening gives the brace dictionary

Status: Proved (the contraction theorem, the block lemma for spaces built from Fano atoms, and the creating half of the touching rule
at distances one and two); the non-creating half and longer distances are computed

Ticket `TWO-BIT-SCREEN-20261105-001B`, 2026-11-05.

## Question

- **The dictionary.** BRACE-TREE found that, wherever only atoms join two lines, their native relation is fixed by their place in the
  tight-cut decomposition. That was 42,090 pairs with no exception, but it was computed.
- **The question.** With the screening lemmas of ticket A and HANDLE-LOCALITY B, how much of it becomes a theorem?

## Dependencies

- **`TWO-BIT-SCREEN-20261105-001A`.** The no-loss theorem: an intact Fano side attached at a line never removes creation.
- **`HANDLE-LOCALITY-20261103-001B`.** The screening lemma: a side that forces its ports onto one antipodal pair acts as a point for
  creation.
- **`HANDLE-LOCALITY-20261103-001A`.** The interface lemma: a knot space minus a line forces the line's points equal.
- **`BRACE-TREE-20261105-001A`.** The Fano plane's creation map is complete.
- **`BRACE-TREE-20261105-001B`.** Places, and the dictionary (`dict_lib.py`, `dictionary.json`).

## Setting

- **Fano trees.** These are spaces whose tight-cut decomposition has only Heawood braces, that is, spaces built from Fano atoms alone.
- **Places.** The place of an ordered pair of lines is as in BRACE-TREE B.
  - **Same atom.** Two lines in one atom.
  - **Different atoms.** The arrows read the cuts along the tree path: '>' when a cut is crossed from emitter to receiver, '<'
    against.
  - **Roles.** Each line has a role at its cut on the path: emitter, cut line or intact.
- **The chain of a pair.** For lines a, b in atoms A, B, the chain S_ab is the closures of the atoms on the tree path from A to B,
  glued at the path's cuts. For A = B it is the atom's closure, the Fano plane.
- **Creation.** "a creates at b" means that the removal of a creates a new knot at b for some far side, as in BRACE-TREE.

## 1. The contraction theorem (proved)

**Theorem.** Let a, b be lines of a Fano tree S.
- **(i)** If a creates at b in the chain S_ab, then a creates at b in S.
- **(ii)** Suppose every atom off the path hangs from it by cuts at which it emits toward the path. Then a creates at b in S only if it
  does in S_ab.

*Proof.* Contract the decomposition tree off the path, one leaf at a time. Each step removes a leaf atom L hanging at one cut, away
from a's and b's atoms. The space stays a Fano tree.
- **L lost a line there (it is attached at a point of its neighbour).**
  - Intact, L forces its three ports onto one antipodal pair (interface lemma), whatever the removal outside it.
  - By the screening lemma, creation at every gluing line outside L, after every removal outside L, equals creation with L replaced
    by that point.
- **L lost a point there (it is attached at a line).**
  - L is an intact Fano side at that line.
  - By ticket A's no-loss theorem, the space with L replaced by the line creates nothing that the space with L does not.
- **The conclusion.** Chaining the steps from S_ab back to S gives (i). Under (ii) every step is of the first kind, so each step is an
  equality. ∎

The theorem holds far side by far side.

## 2. The block lemma (proved)

**Corollary.** In a Fano tree, every line of an atom creates at every other line of that atom.

*Proof.* For two lines of one atom the chain is the Fano plane, whose creation map is complete (BRACE-TREE A). Apply 1(i). ∎

This proves BRACE-TREE's block lemma for atoms attached at a point, within Fano trees. BRACE-TREE had only computed it.

## 3. The dictionary at distances one and two

**The chains are all built.**
- **Two atoms (check 1).**
  - Every gluing of two Fano atoms at a cut is a knot space for exactly two twists of the cut: 7 base points, 7 atom lines and 6 port
    permutations.
  - The two twists differ by complementing the atom.
  - Complementing points and relabelling change no creation. So the 294 gluings with the standard twist are every two-atom chain.
- **Three atoms (check 3).**
  - The middle atom carries two atoms at a pair of its elements.
  - Up to symmetry of the Fano plane there are four kinds of pair: two points (siblings), two lines (co-receivers), and a point with a
    line through it or off it (chains).
  - Every pair of port permutations and two removed elements per end atom were built: 576 gluings.

**What the chains show (checks 2 and 3).** Every place has one relation in every chain, and it is the relation BRACE-TREE recorded:

| Place | Relation |
| --- | --- |
| Same atom, any roles | mutual |
| Neighbours: emitter's line with the receiver's cut line | mutual |
| Neighbours: receiver's intact line to the emitter's line | one-way, intact → emitter |
| Two apart, downstream ('>>' or '<<'): emitter's line with a cut line | mutual |
| Two apart, downstream: intact line to emitter's line | one-way, intact → emitter |
| Two apart, siblings ('><'): the two emitters' lines | mutual |
| Two apart, co-receivers ('<>'): cut line with cut line | mutual |
| Two apart, co-receivers: intact line to the other's cut line | one-way, intact → cut line |
| Two apart, co-receivers: intact line with intact line | silent |

**One rule says it all: the touching rule (check 6).**
- **The rule.** Between different atoms, a removal creates at a line exactly when that line touches its atom's cut toward the
  removal.
- **What touching means.** The line lies on the receiving cut, or its atom emits there. Every line of an emitting atom meets the
  removed line, so it touches.
- **The removed line's role never matters.** Open and open give mutual; intact and open give one-way, toward the open line; intact
  and intact give silence.
- **Where it holds.** Every place of every chain computed, at distances up to three: all 36 places, none off the rule.

**Theorem (creating entries).** In every Fano tree, a removal in one atom creates at every line of another atom at most two apart
that touches its atom's cut toward the removal.
- **The pairs covered.** In the table's terms: both directions of each mutual pair, and the listed direction of each one-way pair.

*Proof.* Each holds in every chain (checks 2 and 3). Apply 1(i). ∎

**The non-creating entries.** These are the reverse of each one-way entry, and silence between co-receivers' intact lines.
- **Where they are known.** They hold in every chain. So they hold in every Fano tree where 1(ii) applies, and in the four 25-point
  trees checked (check 4).
- **In general.** They follow from ticket A's lifting conjecture, which would make each contraction step an equality.

## 4. Larger spaces (computed)

- **Four 25-point Fano trees (check 4).** Three atoms each, on a Fano plane: a star, depth two through emitters, depth two through
  receivers, and a mixed tree. Together they hold 2,148 pairs at most two apart, 530 of them in one atom.
  - At every pair of lines in atoms at most two apart, the creation the chain shows is present, as the theorem requires.
  - The relation equals the chain's in every pair, non-creating entries included.
  - Lines of one atom are mutual.
- **Four-atom paths (check 5).** Every direction of the three cuts, with two port permutations: 16 paths. At distance three each of the
  18 places has one relation. It agrees with BRACE-TREE at the four places BRACE-TREE has, and with the touching rule at all 18.
  - **What this is evidence for.** A transfer along chains. It proves nothing beyond the computed spaces.

## 5. Where the source rule stands

- **What the rule reads.** It keeps a block of mutual creation when one of its lines is blind to everything the others are blind to.
  That needs, at every distance, both which pairs create and which do not.
- **What is now proved, for Fano trees.**
  - Every atom's lines are pairwise mutual.
  - Every line that touches its cut toward a removal at most two atoms away receives creation from it.
  - The cut directions are read correctly wherever 1(ii) applies.
- **What is missing.**
  - **The lifting conjecture.** It is needed for non-creation in general.
  - **A transfer along chains.** It is needed for atoms three or more apart, where the chain grows without bound.
- **So.** "The tree can be recovered from creation by a short rule" remains a computed statement (BRACE-TREE C: 157 of 157 spaces). It
  now rests on two named, sharper gaps instead of the whole dictionary.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Two twists per gluing, related by complementing the atom | all 294 gluings |
| 2 | Two-atom chains: one relation per place, as in BRACE-TREE | 294 gluings |
| 3 | Three-atom chains: one relation per place, as in BRACE-TREE | 576 gluings |
| 4 | Four 25-point Fano trees: chain creation present; relations equal | 2,148 of 2,148 pairs; 530 same-atom pairs mutual |
| 5 | Four-atom paths: one relation per place at distance three | 16 paths, 18 places |
| 6 | The touching rule on every chain | all 36 places (8 in two-atom, 18 in three-atom, 36 in four-atom tables), none off the rule |

## What this does not establish

- **Non-creation** in general Fano trees. It rests on ticket A's lifting conjecture.
- **Distance three and beyond**, except on the computed paths.
- **Spaces with plane glue.** A plane piece reached as a leaf attached at a line is a two-bit side that ticket A does not cover.

## Novelty

- **New here.**
  - The contraction theorem.
  - The proof of the block lemma for Fano trees.
  - The exhaustive chains.
- **Classical analogue.** Contracting the leaves of a tight-cut decomposition is Lovász's.
