# Every row singles out the contradictory class, on the 8- and 10-line glues

Status: Proved (exhaustive computation on two glues; rows read from the class of the glue without their line by SWITCH-PROOF's
theorem; the tie argument in result 3)

Ticket `CONTRA-READ-20261108-001A`, 2026-11-08.

## Question

- **Where it came from.** SWITCH-COMPLETE found that creation between glue lines does not tell switching classes apart in general,
  but that on both glues it computed, the one class without solutions, the class whose plain spaces are three-fold, has a glue block
  no other class shares. Is that an accident of two glues, and how does creation read it?
- **The test.** On the same two glues, compare each row on its own: row a is creation with line a removed, at every other line. By
  SWITCH-PROOF's theorem it depends only on the signing's class on the glue without a.

## Dependencies

- **`SWITCH-COMPLETE-20261108-001A` and `-001B`.** The glues, the classes as fundamental-cycle parities, and the observation.
- **`SWITCH-PROOF-20261108-001A`.** The theorem behind reading a row from the class on the glue without its line, and the signed glue's
  creation map.
- **`TRISUM-READ-20261107-001A`.** The glues and the engine.

## Setting

- **The contradictory class.** A signed glue allows an assignment of its points when every line's three literals are not all equal.
  The contradictory class is a switching class with no allowed assignment.
- **Tied points.** In the glue without line a, a's three points are tied when they show only two complementary patterns, so each
  point's value fixes the other two.
- **Degenerate gluings.** An entry (a, b) is degenerate when the glue without a does not show all six not-all-equal patterns of b's
  literals, so no far side can be glued at b.

## Results

1. **One contradictory class (check 1).** On each glue exactly one class has no solution: the class of the generator's Pfaffian
   signing, whose plain edge-atom spaces are three-fold.
2. **Every row singles it out (check 2).** For every line a of both glues, no other class of the glue without a has the contradictory
   class's row a: one row, creation with one line removed, already recognizes the contradictory class's restriction.
3. **The removed line stays tied (check 2).** In the glue without a, a's three points are tied for the contradictory class and for no
   other class.
   - **Why only there.** If they were tied for another class, signing line a to make its literals equal on both patterns would give a
     second class without solutions.
   - **Why there.** Every assignment allowed without a must break line a, since the whole glue allows none; so a's literals are equal
     in every such assignment.
4. **How a row reads the tie (check 3).** In the contradictory class's row at a, every line b sharing two points with a is degenerate:
   two of b's points are tied, so b's literals miss some of the six patterns. At the lines that share two points with no other line,
   the degenerate entries alone single the class out; elsewhere the knots that far sides add finish the job.

## Reading

- **Creation reads the contradiction.** Removing any one line of the contradictory space leaves that line behind as a tie of its
  three points, and creation at the other lines reads the tie.
- **This complements SWITCH-COMPLETE.** Creation is blind to many classes, those where nothing creates among them, but not to the
  contradictory one.
- **Doctrine.** Everything here is invariant under relabeling lines and points; the spanning tree only names the classes.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Classes without solutions | one per glue, the Pfaffian class |
| 2 | Every row of every line against all classes of the glue without it | the contradictory row is never shared; the removed line tied only there |
| 3 | Degenerate gluings | two-point partners degenerate; at lines without one, degeneracy alone singles the class out |

## What this does not establish

- **Other glues.** Only the 8- and 10-line glues; ticket B goes one size past.
- **A proof.** Why a row recognizes the tie is shown only where degeneracy alone does it; in general it is computed.
- **Uniqueness of the contradictory class** is computed on these glues, not proved for every glue.

## Novelty

- **New here.** The recognition, and how degenerate gluings carry it.
- **Classical.** Switching classes (Zaslavsky); Pfaffian signings and three-fold spaces as in the program's earlier work.
