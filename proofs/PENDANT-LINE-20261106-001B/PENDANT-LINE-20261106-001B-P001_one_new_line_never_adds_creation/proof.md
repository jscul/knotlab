# One new line never adds creation

Status: Proved (from ticket A's two-round rule, with every local configuration checked exhaustively)

Ticket `PENDANT-LINE-20261106-001B`, 2026-11-06.

## Question

- **The pendant-line statement (TWO-BIT-SCREEN A).** Add one new point b to a near side, on one new not-all-equal line through two of
  its points. Does creation stay the same?
- **Known.**
  - **The no-loss half (proved).** No knot avoiding b changes its status.
  - **The other half.** Whether a new knot can appear through b was computed (117,344 cases) but not proved.
  - **The obstructions.** It is neither local nor a consequence of the knots alone.
- **Why it matters.** By TWO-BIT-SCREEN A's reduction, this is all that remained of the two-bit screening lemma for Fano sides.

## Dependencies

- **`PENDANT-LINE-20261106-001A`.** The two-round rule and the local engine (`local_lib.py`).
- **`TWO-BIT-SCREEN-20261105-001A`.** The no-loss half for pendant lines, and `screen_lib.py`.

## Setting

- **The two systems.** Σ is a near side, and Σ⁺ is Σ with b added on the line (b, s + σ, u + τ), for any two points s, u and any
  signs.
- **The rest.** The gluing line ℓ shows six patterns, and the far side is one of the four census far sides.

## Theorem

**If Σ has no new knot at ℓ and the far side, then Σ⁺ has none.** With the no-loss half, creation in Σ⁺ equals creation in Σ, and the
new knots avoiding b are the same.

*Proof.*
- **The rule decides the new knots.** By ticket A's theorem applied to Σ⁺, a crossing knot through b is new exactly when the
  two-round rule does not reach it.
- **The verdict is local.** The rule's verdict on a knot through b depends only on the projection onto four groups of classes:
  - the gluing line Y;
  - b's line, through s and u;
  - the knot's other near class, if any;
  - its far classes.

  The projection includes b, determined by s and u. That is a local configuration, with s and u near classes or points of Y, at
  most one further class, and one or two far classes.
- **The hypothesis is local too.** If Σ has no new knot, every crossing knot of Σ⁺ that avoids b is reached. Such knots are Σ's, with
  the same verdicts, since the rule's verdict on them never involves b. In particular, every crossing knot avoiding b in that local
  configuration is reached.
- **Check 1.** On every local configuration, if every crossing knot avoiding b is reached, every crossing knot through b is reached.
- **The degenerate cases.**
  - **s tied to u.** b is tied to s (when their literals always agree) or free of everything (when they always differ). Either way
    no new knot appears through b.
  - **s or u tied to a point of Y or to the other class.** These configurations are among the smaller shapes checked. ∎

## The local check

**Shapes.** The new line's two points:
- both near classes, with one further class;
- one on the gluing line (either sign), with one further class;
- both on the gluing line (all signs).

Each shape is taken with one or two far classes of each far side. Every complement-closed near relation that shows the line's six
patterns is enumerated.

**What it found.**
- **No counterexample.**
- **Not vacuous.** Many configurations have a knot through b that is not reached. In each of them some knot avoiding b is not reached
  either, so Σ itself creates there.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Exhaustive local implication (1,330 shape tasks over the four far sides) | 347,149,320 non-degenerate configurations, none a counterexample; 770,840 have a knot through b not reached, and each also has one avoiding b not reached |
| 2 | Corroboration on census and random near sides with a random pendant line | 22,856 cases, creation and the knots avoiding b unchanged in all |

## What this does not establish

- **Two or three new lines.** A point on two or three new lines through a line's points can create (TWO-BIT-SCREEN A, check 5); the
  theorem is sharp.
- **Other far sides, and knots of more than three points.**

## Novelty

- **New here.** The theorem and its proof.
- **What it closes.** It completes the two-bit screening lemma for Fano sides (ticket C).
