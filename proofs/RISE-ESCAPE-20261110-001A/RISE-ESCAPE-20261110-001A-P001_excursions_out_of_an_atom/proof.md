# Excursions out of a piece

Status: Proved by hand (E1); the excursion search is computed (`check.py` check 2, run `rise-escape-a1b`, 8.4 minutes). Pre-registered in
`research/RISE-ESCAPE-20261110-001/preregistration.md`. A first launch (`rise-escape-a1`) was stopped after four minutes with no row
written, for speed; the restarted search computes the same quantities, the unbounded component first.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, and an atom (a Fano or torus atom) a piece (Intuitions guide, Glossary). The mathematics is
unchanged; the earlier text is in git history.

## E1 (proved)

At the genus-2 floor there is no violated knot and no even face (`ATOM-LAYERS-20261110-001` theorem 1), so a learner that holds the state
still has no step, whatever rise it would accept. Checked on all 15 floor states.

## The excursion search (computed)

With the law fixed, from each of the 15 genus-2 floor states (two pieces, one at l0 and one at distance 1, 2 or 3; K_2 and K_3), every state
reached by single flips with W at most one unit above the floor (W ≤ 3; on genus 2 W = 2E − 1 is odd), searched breadth first to 200,000
states, unbounded excursion length first:

- **No floor state ever puts the unit in the other piece or at the upper level.** On K_2 five of the six components are complete (173,664 to
  195,264 states) and in every one the unit sits only inside the piece it settled in or at that piece's junction faces. The sixth K_2
  component and all nine K_3 components stopped at the cap with the same result.
- One K_3 row reports the other piece reached at k = 2: there the unit started at a junction, so no home piece was defined and the target
  included the unit's own piece. Read post hoc, the faces it reached were that piece's and its junction's only.

So a one-unit rise does not let the unit leave: on K_2, exhaustively, the trap is a wall at this height, not a barrier of one unit.

## Against the pre-registration

E1 held. E2 and E3 failed: no escape at any k, including unbounded.

## A reading, not checked

With the law fixed the unit never changes piece. In `GROW-HANDLE-20261110-001` a piece acts as its knot in one class and is transparent in
the others; after learning resolved the first piece's pair, the first piece is transparent and the second still acts as its knot. Which piece
holds the floor unit may be fixed by the law's class, so that only a change of law, learning at a rise where violated knots appear, could
move it (backlog B79).

## Scope

K_2 and K_3 with two Fano pieces (A48), the law fixed, state flips of A50 with a rise of one unit, the weight of A49.
