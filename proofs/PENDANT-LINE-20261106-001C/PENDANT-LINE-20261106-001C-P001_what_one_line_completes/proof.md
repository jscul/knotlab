# What one line completes

Status: Proved (consequences of tickets A and B with TWO-BIT-SCREEN-20261105-001A and B)

Ticket `PENDANT-LINE-20261106-001C`, 2026-11-06.

## Dependencies

- **`PENDANT-LINE-20261106-001B`.** One new line never adds creation, through ticket A's two-round rule.
- **`TWO-BIT-SCREEN-20261105-001A`.**
  - **No-loss theorem.** An intact Fano side never removes creation, and new knots off it are the closed space's.
  - **Reduction.** The other half of the lemma follows from the pendant-line statement.
- **`TWO-BIT-SCREEN-20261105-001B`.** The contraction theorem, and every gluing of two atoms (294) and of three atoms in a chain
  (576), each place with one relation.
- **`HANDLE-LOCALITY-20261103-001B`.** The one-bit screening lemma.

Throughout, "creation" is the creation map's: knots of up to three points against the four census far sides.

## 1. The two-bit screening lemma (proved)

**Theorem.** Let an intact Fano side R stand in for a line L0 of a space S, attached with the twist under which it acts as L0. Let N̂
be S with L0 restored. Then at every removal and gluing line outside R, and for every far side:
- **(i) Off the side.** The new knots that avoid R's hidden points are those of N̂.
- **(ii) Through the side.** A new knot through a hidden point occurs only where N̂ has a new knot.
- **So** creation in S equals creation in N̂: the side acts as its line for creation, as it does for solutions.

*Proof.*
- **(i)** This is TWO-BIT-SCREEN A's no-loss theorem.
- **(ii) The reduction.** By TWO-BIT-SCREEN A's reduction, if N̂ has no new knot, every crossing knot through a hidden point b is a
  knot of a pendant system: N̂ with b on one new line through two ports. Such knots are generated in S if they are generated there.
- **(ii) The pendant system.** By ticket B, the pendant system has no new knot. ∎

## 2. The splitting lemma, for both kinds of atom (proved)

**In any space, an intact Fano atom can be contracted to its element without changing creation at removals and gluing lines outside
it.** This holds whether the atom is attached at a point (emitting) or at a line (receiving).
- **Attached at a point.** This is HANDLE-LOCALITY B's screening lemma: the atom forces its ports onto one antipodal pair.
- **Attached at a line.** This is item 1.
- **What was open.** NATIVE-GENUS proved the point case and checked the line case. The line case is now proved.

## 3. Contraction is exact in Fano trees (proved)

**In a space built from Fano atoms alone, a line a creates at a line b exactly when a creates at b in the chain of their atoms.** The
chain is the closures of the atoms on the tree path between them, glued at the path's cuts.

*Proof.*
- **Each step is now an equality.** TWO-BIT-SCREEN B's contraction contracts the tree off the path one leaf at a time.
  - Leaves attached at a point were already equality steps, by the screening lemma.
  - Leaves attached at a line were no-loss steps, and by item 1 they are equality steps too. ∎

## 4. The touching rule at distances up to two (proved)

**In every Fano tree:**
- **Different atoms.** Take lines a and b in different atoms at most two apart. Then a creates at b exactly when b touches its atom's
  cut toward a's atom: b lies on the receiving cut there, or b's atom emits there.
- **One atom.** Lines of one atom create at each other.

*Proof.*
- **The chains.** By item 3, the relation equals the relation in the chain.
- **Every chain is computed.** For two atoms the chains are the 294 gluings, and for three atoms the 576 gluings. Up to relabelling and
  complementing points, these are all of them (TWO-BIT-SCREEN B, check 1).
- **They follow the rule.** At every place of every one of them, the relation is the touching rule's (check 2). ∎

**What this means for the brace dictionary.**
- **A theorem up to distance two.** The dictionary between atoms at most two apart is now a theorem, non-creation included.
- **Cut directions.** Every cut between two atoms is read in its direction.
  - The emitter's lines and the receiver's cut lines create at each other.
  - The receiver's intact lines create at the emitter's, never the reverse.
- **Siblings and co-receivers.**
  - Siblings are mutual.
  - For co-receivers, cut lines are mutual, intact lines create one way at the other's cut lines, and intact lines are silent with
    each other.
  - Downstream lines follow the same rule.

## 5. What is left

- **Distance three.** All 18 places on the 16 four-atom paths computed follow the touching rule (check 2). Not every four-atom gluing
  was built, so distance three is computed, not proved.
- **The source rule.** It reads relations at every distance. So "the tree can be recovered from creation by a short rule" now rests on
  one gap: a transfer along chains of four or more atoms.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Cited checks: ticket A's local verification has no violation; ticket B's has no counterexample; TWO-BIT-SCREEN A's no-loss and reduction checks and TWO-BIT-SCREEN B's chain checks passed | pass |
| 2 | The touching rule re-derived from TWO-BIT-SCREEN B's recorded place tables | every place agrees |

## Novelty

- **New here.** Items 1 to 4, which complete what TWO-BIT-SCREEN reduced to the pendant-line statement.
