# Creation is decided at the gluing line

Status: Proved (a reduction to local configurations, with every local configuration checked exhaustively)

Ticket `PENDANT-LINE-20261106-001A`, 2026-11-06.

## Question

- **Background (TWO-BIT-SCREEN).**
  - **The open half.** Whether one new point on one new line can add creation was the last open half of the two-bit screening lemma.
  - **A computed fact.** Eliminating only through the gluing line's points reaches every crossing knot the closure reaches. This held
    on about 2 million generated crossing classes.
- **The question.** Which crossing knots does the closure reach, stated explicitly?

## Dependencies

- **`TWO-BIT-SCREEN-20261105-001A`.** The closure as a tetrahedron rule (its item 1), and `screen_lib.py`.
- **`HANDLE-LOCALITY-20261103-001B`.** The join method and the creation map's far sides (`join_lib.py`).
- **`HANDLE-EMERGENCE-20261102-001B`.** The join lemma.
- **`SPLICE-TREE-20261102-001C`.** Tie classes and the elimination closure (`elim_lib.py`).

## Setting

- **Near side.** Any complement-closed set of assignments on the near points that shows the gluing line ℓ's six patterns; in
  particular, the solutions of a space minus a removal. Y is the set of ℓ's three points.
- **Far side.** One of the four census far sides (K4^(3), census 6, the Fano plane, census 58), split at a point and attached at Y.
- **Knots.**
  - **Classes.** Knots are triples of tie classes, minimal constrained sets of at most three points.
  - **The base.** The base is the set of non-crossing knots.
  - **The closure.** The closure is the least set containing the base in which every four classes with two triples in the set have all
    their knot triples in it (TWO-BIT-SCREEN A, item 1).
- **Shapes.** Write c, c′ for far classes, x, w for near classes off Y, and y, z for Y classes. Every crossing triple has one of three
  shapes: {c, x, y}, {c, x, w} and {c, c′, x}.
- **Base knots used below.**
  - **Far knots** {c, y, z}: the far side's knots through two Y classes.
  - **Near knots** {x, y, z} and {x, w, y}.

## The two-round rule

- **Round one.** {c, x, y} is reached when it is a knot and some z on Y makes {c, y, z} a far knot and {x, y, z} a near knot. The near
  side and the far side meet at the pair {y, z}.
- **Round two.**
  - **Pairs.** {c, x, w} is reached when it is a knot and x and w share a point y with {c, x, y} and {c, w, y} reached in round one.
  - **Two far classes.** {c, c′, x} is reached when it is a knot and some y on Y gives two of these: the far knot {c, c′, y}, and
    {c, x, y}, {c′, x, y} reached in round one.

## Theorem

**The crossing knots in the closure are exactly the knots the two-round rule reaches.**

*Proof.*
- **The rule lies in the closure.** Each rule is one step of the tetrahedron rule.
  - **Round one** uses the four classes {c, x, y, z}. The base knots {c, y, z} and {x, y, z} both contain y and z, so the triple
    avoiding z, {c, x, y}, is added.
  - **Pairs** use {c, x, w, y}. {c, x, y} and {c, w, y} both contain y, which gives {c, x, w}.
  - **Two far classes** use {c, c′, x, y}. Two of its triples through y give {c, c′, x}.
- **The closure lies in the rule.** Let S be the rule together with the base. It is enough to show that S is closed under the
  tetrahedron rule: for four classes Q with two triples in S, every crossing knot triple of Q is in the rule. Then the closure, the
  least closed set containing the base, lies in S.
  - **Locality.**
    - **Status is local.** Whether a triple of Q is a knot, in the base or reached by the rule is decided by the projection of the
      splice onto Q's classes and Y. Knots are decided by their own three classes, and the rule names only knots among Q ∪ Y.
    - **The projection is a join.** That projection is the join, over Y, of two parts. One is the near side's projection onto Y and
      Q's near classes. The other is the far side's projection onto Y and Q's far classes.
  - **No degeneracy.**
    - **Classes are untied.** Distinct classes are untied.
    - **Far classes stay separate.** No far point is determined by Y (check 2). The far side meets the near side only through Y. So no
      far class is tied to a near point, and the far classes are as in check 2.
  - **The literal frame.**
    - **Signs.** Complementing Y's points gives ℓ zero signs.
    - **The far side.** The far side the creation map splices in is then the zero-sign gadget, or that gadget with every far point
      complemented (check 1).
    - **Why that is enough.** Complementing points changes no constrained set.
  - **The configurations to check.**
    - **Size.** A four-set with a crossing triple has k ≥ 1 near classes off Y and m ≥ 1 far classes, with k + m ≤ 4: (3, 1), (2, 2)
      or (1, 3).
    - **Smaller ones.** A configuration with fewer near classes is the projection of one with more: add a free class, which is
      untied and changes no other status.
  - **Check 3.** On every local configuration of these sizes, no step of the tetrahedron rule produces a crossing knot outside the
    rule.
    - **The near relations.** Every complement-closed near relation on Y and three further classes showing the six patterns:
      16,581,375 of them.
    - **The far configurations.** Every far class, pair and triple of the four far sides.
    - **The total.** 348,376,032 configurations, 346,754,982 of them non-degenerate. ∎

## Corollaries

1. **Two rounds.** The closure reaches each of its crossing knots within two rounds.
2. **Gluing-line locality.** Each rule step eliminates a class of Y. So elimination through Y alone reaches everything, which is the
   computed fact behind this ticket.
3. **What a new knot is.** A crossing knot is new exactly when its near and far parts fail to meet through the gluing line:
   - for {c, x, y}, no z makes both {c, y, z} and {x, y, z} knots;
   - for {c, x, w}, x and w share no round-one point.
4. **Creation is local.** Creation at (M, ℓ), a new knot for some far side, is decided by the knots among Y, two further near classes
   and the far classes. These are a handful of classes at the gluing line.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The literal frame: for each sign pattern of ℓ, the spliced far side is the zero-sign gadget or its far-complement | 8 of 8 for every far side |
| 2 | Far classes: none tied to Y; each value excludes a subcube (or nothing) | K4^(3) 3 classes, census 6 5, Fano 6, census 58 7 (one free of Y) |
| 3 | Exhaustive local verification | 0 violations; equals the longer switch rule everywhere; each part switched off gives violations (round one 109,045,340; pairs 3,591,800; two far 13,872) |
| 4 | The local engine on real splices | 59,304 triples and 3,492 crossing knots, all equal to the closure's |
| 5 | The rule on census and random near sides | 201,655 crossing classes agree; elimination through Y alone generates all 184,074 generated ones |

## What this does not establish

- **Other far sides.** The argument is general, but its local check is per far side, and only the four census far sides used by the
  creation map are covered.
- **Knots of more than three points.** These are not covered, matching the creation map.

## Novelty

- **New here.** The two-round rule and its proof, and the reading that creation is decided at the gluing line.
- **Method.** Reducing a closure on a large system to the closure of finitely many local configurations is standard for finite
  verification; we know of no prior statement of these results.
