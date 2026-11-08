# A hanging side K4^(3) without a line hides the contradiction

Status: Proved (from PENDANT-LINE A's locality of creation, a finite lemma on the side over all 512 signings and six local
lemmas over all one- and two-point relations; the prediction confirmed at 16 failing lines)

Ticket `CUT-HIDE-20261108-001A`, 2026-11-08.

## Question

- **Where it came from.** CONTRA-PROOF found that one row of creation between glue lines reads the removed line's tie on every
  3-connected glue tested, and fails exactly at the lines lying in a two-vertex cut of the incidence graph. Every failing cut had a
  side that is K4^(3) without a line. Why does such a cut hide the tie?
- **The answer sought.** A theorem: at such a cut, the contradictory class and one other class have the same row, and only the first
  ties the removed line's points.

## Dependencies

- **`CONTRA-PROOF-20261108-001A`.** The random glues, their two-vertex cuts and failing lines (`glues.json`).
- **`CONTRA-READ-20261108-001A`.** Rows of creation between glue lines and the tie (`contra_lib.py`).
- **`PENDANT-LINE-20261106-001A` and `CHAIN-TRANSFER-20261106-001A`.** Creation at a gluing line Y is decided by local relations: Y with
  one near point, or Y with two. A far side creates at Y exactly when some such relation that is not degenerate creates
  (`transfer_lib.verdict_from_masks`), so creation is the union over the relations that occur.
- **`SWITCH-PROOF-20261108-001A`.** The signed glue's creation map.

## Setting

- **The glue.** H is a connected cubic glue: n points and n lines, each line on three points, each point on three lines. A signing
  allows an assignment when every line's three literals are not all equal. κ is a switching class without solutions, and line a is
  such that the restriction of κ to H − a has solutions.
- **The cut.** Lines a and a' form a two-line cut: removing both disconnects H's incidence graph into two sides.
- **Counting incidences.** Each side has one more point than lines, and a and a' meet it in three points together. So a meets one side
  S in one point x0 and a' meets S in two points y and z; a meets the other side B in two points and a' meets B in one point u.
- **The hanging side.** In H − a, S meets the rest only at y and z, through a'. Here S is K4^(3) without a line: four points c, x0, y,
  z and the three lines {c, x0, y}, {c, x0, z}, {c, y, z} through the centre c. Then c and x0 lie on no other line of H − a.

## Theorem

**Let H, κ, a, a' and S be as above, with S K4^(3) without a line. Let τ be κ's restriction to H − a and σ the class of H − a obtained
from τ by changing the sign of a' at y. Then τ and σ have the same row of creation at every gluing line of H − a, τ ties a's three
points and σ does not. So one row at a cannot tell the classes that tie a's points from those that do not.**

*Proof.*

1. **The side alone (check 1).** Over all 512 signings of S's nine incidences, the signings of one switching class make S's own lines
   tie x0, y and z, with y and z showing two patterns and c free given the other three. Every other signing leaves y and z free (all
   four pairs occur) and x0 not a function of them.
2. **τ makes S rigid.** Every assignment allowed by τ breaks line a, since κ allows none, so a's literals are equal in every one and a's
   points are tied. Let p be a point of a in B. If S's signing were not in the rigid class, some two solutions of S would agree on y and
   z and differ at x0. The solutions of B show both values of u (they are closed under complementing), so both solutions of S extend
   by one and the same assignment of B; x0 would then change while p stays fixed, and x0 and p would not be tied. So S is rigid in τ.
3. **Coupled and decoupled.** In the rigid class y and z are tied, so on a' their literals are always equal or always different, and
   changing a''s sign at y swaps the two cases. When they differ, a' holds for every assignment and S is independent of B (decoupled).
   When they are equal, a' forces u's literal to differ from them, so u is tied to y (coupled). τ is coupled, since a decoupled S would
   leave x0 independent of p. So σ is decoupled, and σ does not tie a's points: x0 is independent of B. S's own signing is the same in
   τ and σ, so S is rigid in both.
4. **The assignments.** In σ the allowed assignments are every allowed assignment of S with every allowed assignment of B. In τ they
   are every allowed assignment of B, with x0, y and z set from u and c free. Both project onto B as B's own solutions.
5. **Lines of S and a'.** Each line of S contains two of x0, y and z, and a' contains y and z. These are tied in both classes, so
   every such gluing line misses some of its six patterns: degenerate in both.
6. **Lines of B.** For a gluing line Y inside B, compare the local relations that occur (check 2 gives the lemmas used).
   - **Near points of B.** Their relations with Y are projections of B's solutions, the same in both classes.
   - **In σ.** Points of S are independent of B. Alone, a point of S is free and creates nothing (L1). Paired with a point of B it
     adds nothing to that point (L2). Two points of S together are independent of Y and create nothing (L3).
   - **In τ.** The centre c is independent of everything (L1, L2, L3 as before). x0, y and z are tied to u. If u lies on Y they are
     tied to Y and degenerate (L5). Otherwise each is u complemented or not, so its relations are u's (L6), and u is itself a near
     point in both classes; a pair of two of them, or one of them with u, is a tied pair and adds nothing to one point alone (L4).
   So the same creation occurs at Y in both classes.
7. **Every gluing line is one of these.** With a removed, every line of H − a lies in S or in B, or is a'. So the rows are equal. ∎

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The side alone, all 512 signings | one class of 64 rigid; all others leave y, z free and x0 not a function of them |
| 2 | Local lemmas L1 to L6, all 27 one-point and 3,375 two-point relations | all hold |
| 3 | The prediction on CONTRA-PROOF's 16 failing lines | rigid, coupled; the flip keeps the row and breaks the tie, at all 16 |

## Reading

- **Why the cut hides the contradiction.** The contradiction runs through the cut: the removed line's tie reaches its far point x0
  only through the rigid side and the other cut line. One sign on that line decides whether the side is coupled or free, and creation
  at every gluing line is blind to that sign, since the rigid side's lines are degenerate either way and its points add nothing that
  u does not.
- **Beyond the theorem.** The two failing lines whose hanging side has six points behave the same way (check 3), but the proof's step 5
  needs every line of the side to be degenerate, which only K4^(3) without a line guarantees.

## What this does not establish

- **Other hanging sides.** Only K4^(3) without a line is covered; the two six-point sides are computed.
- **3-connected glues.** Nothing here proves that one row reads the tie where there is no two-vertex cut.

## Novelty

- **New here.** The theorem and its proof.
- **Classical.** Two-vertex cuts and decomposition of graphs along them.
