# Where one row reads the removed line's tie

Status: Proved (exhaustive computation on 19 random glues, redrawn from their seeds, and on seven trisum glues; the local lemma
exhaustive over all 27 relations)

Ticket `CONTRA-PROOF-20261108-001A`, 2026-11-08.

## Question

- **Where it came from.** On the seven trisum glues of 8 to 12 lines, one row of creation between glue lines singles out the
  contradictory class: with line a removed, a's three points are tied in that class and in no other, and the row reads the tie
  (CONTRA-READ). The coordinator approved a proof attempt.
- **The cheapest discriminator first.** Before proving it for every glue, test it on glues that are not trisum glues: random connected
  cubic glues that have a class without solutions.

## Dependencies

- **`CONTRA-READ-20261108-001A` and `-001B`.** The rows, the tie, and `contra_lib.py`.
- **`SWITCH-PROOF-20261108-001A`.** The theorem behind reading a row from the class of the glue without its line.
- **`PENDANT-LINE-20261106-001A`.** Creation decided at the gluing line, by local relations on the line and one or two near points.

## Setting

- **The statement under test (G).** For a glue H and a line a, one row reads the tie when no class of H − a that ties a's points shares
  its row with a class that does not.
- **Two-vertex cuts.** A line lies in a two-vertex cut when removing it and one other vertex disconnects the glue's incidence graph.

## Results

1. **The glues (check 1).** Drawn at random with fixed seeds: of 3,000, 1,500 and 800 connected cubic glues of 8, 9 and 10 lines, 94,
   18 and 3 have a class without solutions; the first 10, 6 and 3 are kept. Each has exactly one class without solutions. Eight
   have incidence graphs of connectivity 2, eleven of connectivity 3.
2. **G holds exactly away from two-vertex cuts (check 2).** On every glue, one row fails to read the tie at exactly the lines lying in
   a two-vertex cut: 16 lines, two on each glue of connectivity 2, and none on the glues of connectivity 3. At those lines nothing
   creates anywhere in the tied class's row or in the row colliding with it: every gluing is degenerate, or (on the 10-line glues, at
   one line) adds no new knot.
3. **The cuts (check 3).** Each such cut is a pair of lines whose two sides each have one more point than lines, and one side is
   always K4^(3) without a line: three lines on four points, all through one point. Removing one of the two cut lines leaves the sides
   so rigid that almost no gluing line shows all six patterns, in the tied class and in another.
4. **K4^(3) under the tie is not a general lemma (check 4).** In every tied class's row, on the 19 random glues and on six of the
   seven trisum glues, the K4^(3) far side creates at no line meeting the removed line in exactly one point. On the 12-line trisum
   glue of seed 1 it does, for 8 of its 12 removed lines, and one row still reads the tie there (CONTRA-READ's stress test).
5. **That silence is not the whole mechanism (check 5).** On a glue of connectivity 3 where G holds, some classes are told apart from
   the tied one neither by K4^(3) at such a line nor by their degenerate entries, but by other entries.
6. **A local lemma (check 6, exhaustive).** Over all 27 complement-closed relations on a gluing line's literals and one near point, no
   single point makes K4^(3) create (it needs a pair of near points), and a relation is degenerate exactly when the point is tied to
   a point of the gluing line. So the points tied to the removed line's points are never witnesses at a line through one of them.

## Reading

- **No proof for every glue: the statement is false there.** The counterexamples are glues with two-vertex cuts, where removing a
  line leaves both sides rigid.
- **The conjecture to prove.** On glues whose incidence graph is 3-connected, one row reads the removed line's tie. It held on all
  18 such glues tested, the trisum glues included.
- **No local shortcut.** K4^(3)'s silence under the tie, which explains the reading on the 8- and 10-line glues, fails on a 12-line
  trisum glue where the reading still holds. The local lemma removes the tied points as witnesses but does not decide the rest.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The random glues, drawn again from their seeds | 19 glues, one class without solutions each; connectivity 2 for 8, 3 for 11 |
| 2 | Every row of every line against all classes of the glue without it | G fails exactly at the 16 lines in two-vertex cuts, where nothing creates |
| 3 | The cuts | pairs of lines; each side has one more point than lines; one side is K4^(3) without a line |
| 4 | K4^(3) under the tie, random and trisum glues | silent on 25 of 26 glues; on the 12-line glue of seed 1 it creates for 8 of 12 removed lines |
| 5 | The certificate | not sufficient on a glue of connectivity 3 |
| 6 | Local relations of one near point | none makes K4^(3) create; degenerate exactly when tied to the gluing line |

## What this does not establish

- **A proof.** The conjecture for 3-connected glues is computed, not proved, and K4^(3)'s silence is false in general.
- **Larger or structured glues.** Random glues of 8 to 10 lines only, plus the trisum glues of CONTRA-READ.

## Novelty

- **New here.** The counterexamples at two-vertex cuts, the refined conjecture, and the local lemma.
