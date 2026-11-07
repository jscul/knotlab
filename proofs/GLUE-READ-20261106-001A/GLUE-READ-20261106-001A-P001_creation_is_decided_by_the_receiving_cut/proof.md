# Creation is decided by the receiving cut

Status: Proved (an exhaustive finite check over every port relation and every deeper relation; the census test is computed)

Ticket `GLUE-READ-20261106-001A`, 2026-11-06.

## Question

- **Background (CHAIN-TRANSFER A).** Along chains of Fano atoms, a removal leaves the ports of every cut beyond it free, and the receiving
  atom alone decides creation. That gives the touching rule.
- **What glue changes.** In BRACE-TREE C's census, the touching rule fails at 2,829 of the 21,660 pairs of atom lines with plane glue between.
- **The question.** What decides creation at an atom when the parts between do not leave its ports free?

## Dependencies

- **`CHAIN-TRANSFER-20261106-001A`.** The profile machinery and the closed last atom (`transfer_lib.py`).
- **`PENDANT-LINE-20261106-001A`.** The two-round rule: creation is an OR over local configurations at the gluing line.
- **`CHAIN-TRANSFER-20261106-001B` and `C`.** Exact creation rows (`tree_lib.py`) and the census builders (`read_lib.py`).
- **`BRACE-TREE-20261105-001C`.** The fresh census.

## Setting

- **The atom.** B is a Fano atom with its other elements present (closed), meeting the rest of a space at one cut. Beyond the cut lies a
  removal.
- **The port relation.** R is the set of literal patterns that the removal's side allows on the cut's three ports.
- **Deeper relations.** These are the side's relations on the ports together with one or two further points.
- **Roles.** At the cut, B emits (it lost a line there) or receives (it lost a point there). A receiver's cut lines pass through the lost
  point; its other lines are intact.

## Theorem (the receiving-cut law)

**Whether the removal creates at a line of B depends only on R:**
- **B emits at the cut.** Every line of B receives creation exactly when R allows the three ports to be equal.
- **B receives there.**
  - A cut line receives exactly when R does not force the other two ports equal.
  - An intact line receives exactly when R tells the ports apart, that is, when R is not invariant under permuting them.

**Deeper points never decide.** They can only add far sides at a line that already receives.

*Proof.*

1. **Locality at the line.** By PENDANT-LINE A, creation at b is an OR over local configurations: b's three points together with one or two
   further near points.
2. **Two kinds of further point.**
   - Points of B, ports included, give the configurations of B alone with R.
   - Points beyond the cut enter only through the side's deeper relations, joined over the ports, as in CHAIN-TRANSFER A.
3. **Both bounds.**
   - **Lower bound.** Any far side with port relation R yields at least B's own configurations. These depend only on R.
   - **Upper bound.** Its deeper relations all project onto R, and there are finitely many such relations: after canonical forms, 2 to 41
     singles and 5 to 6,959 pairs, depending on R. Feeding all of them at once bounds any far side from above.
4. **The bounds agree (check 1).** In all 8,190 cases (15 port relations, every closed last atom: lost element, port permutation, line),
   the two bounds give the same verdict on creation. So every far side gives B's own verdict.
5. **The native statement (check 2).** That verdict is the stated one in all 8,190 cases. ∎

## The table (check 2)

| Patterns the removal's side allows | Emitter's lines | Receiver's cut lines | Receiver's intact lines |
| --- | --- | --- | --- |
| all eight (free) | receive | receive | silent |
| not all equal | silent | receive | silent |
| all equal | receive | silent | silent |
| all but one non-constant pair | receive | receive | receive |
| two ports tied, the third free (e.g. 000/001/110/111) | receive | the tied ports' lines receive, the free port's not | receive |
| two ports opposite, the third free (e.g. 001/010/101/110) | silent | receive | receive |
| one port opposite two tied ones (e.g. 001/110) | silent | the tied ports' lines receive, the odd one's not | receive |

## Reading

- **Free and not-all-equal sides give the touching rule at a receiver.** An emitter needs its ports allowed equal.
- **Through Fano atoms the side is always free** (CHAIN-TRANSFER A), so the touching rule holds there.
- **Glue changes the side's relation.** Creation then follows the table. This explains every deviation of the census.
- **What an intact line feels.** It receives creation exactly when the far side distinguishes the ports of its cut. A symmetric side,
  free, not-all-equal or all-equal, leaves it silent.

## The census (check 4, computed)

- **The test.** In BRACE-TREE C's 111 fresh spaces, take every removal anywhere (in an atom or in glue) and every line of a Fano atom not
  holding it. Replace the removal's side of the facing cut by the relation it shows on the points it shares with the atom's side.
- **The result.** Creation is unchanged at all 47,550 pairs.
  - **Beyond the theorem.** This keeps each receiving atom's real other branches, glue included, so it tests the law beyond the closed
    setting.
  - **The relations met.** Free on three points; six patterns; four on three points; four on two points (two ports are one point, so they
    are tied).

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Every deeper relation at once against the atom alone, for every port relation and closed last atom | 8,190 of 8,190 unchanged; far sides added in 504, all at lines already receiving |
| 2 | The native statement | 8,190 of 8,190 |
| 3 | Free ports give the touching rule | 546 of 546 |
| 4 | Computed: the census, every removal and atom line | 47,550 of 47,550 pairs unchanged |

## What this does not establish

- **Atoms whose other branches do not act as their elements.** The theorem assumes the atom is closed. Check 4 covers real spaces, but only
  by computation.
- **Which relation glue presents.** See ticket B.
- **Other far sides, and knots of more than three points.**

## Novelty

- **New here.** The law and its native statement.
- **Method.** Bounding an OR over local configurations by feeding every compatible relation at once is a standard finite argument.
