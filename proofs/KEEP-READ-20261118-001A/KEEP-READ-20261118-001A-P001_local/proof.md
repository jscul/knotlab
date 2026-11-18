# The move's own knots cannot tell keeping from raising

Status: Proved

Ticket `KEEP-READ-20261118-001A`, 18 November 2026, by Claude. Epic `KEEP-READ-20261118-001`. Written before the run.

## Words

As in `KNOT-SWITCH-20261118-001A` and `PICK-TWO-20261118-001A`. A move is one knot set of a KF3 option; an extension may have
several. A **tier** is what a reading may look at: the move's own knots (tier 0); the presented knots within one or two steps of
the move's old distinctions (tiers 1, 2; a step joins a distinction to a knot holding it); or the betweenness that the states imply
among the move's old distinctions (the closure tier, local in what it names, global in how it is derived). A **picture** is what the
tier shows, with the new distinction, the move's knots and each middle marked; two moves look alike at a tier when their pictures
are isomorphic.

## Statements

- **R1. At tier 0, keeping and raising look alike.** The corner knot set {B(x, r, y), B(c, x, r), B(c, y, r)} fills a cell when the
  splits separating c from x and from y cross, and raises the orders by one when they are nested
  (`PICK-TWO-20261118-001A`, S4; `NEVER-NEST-20261118-001A`, N5). Both are the same three knots with the same middles. So no rule
  reading only a move's own knots accepts exactly the fills that keep two orders.
- **R2. The best rule at a tier.** Call a picture class clean if none of its moves raises. A rule reading a tier can accept an
  extension only through a knot set it accepts. It accepts no raising extension only if every knot set it accepts lies in a clean
  class. So it accepts exactly the extensions that keep two orders only if every such extension has a knot set in a clean class.
  The fraction of extensions keeping two orders that have one (the **clean-witness fraction**) bounds every rule at that tier from
  above, and the rule "accept the clean classes" attains it. An exact local reading at the tier exists, on the bases met, exactly
  when the fraction is 1. The same holds with SEED's acceptance in place of "keeps two orders".

## Proofs

**R1.**
- *The knots.* Both fills use B(x, r, y), B(c, x, r) and B(c, y, r), where c differs from x on one split t₁ and from y on one split
  t₂. Their old distinctions and middles correspond by x ↦ x, c ↦ c, y ↦ y.
- *If t₁ and t₂ cross,* r is the empty cell, and two orders are kept (N5).
- *If they are nested in one chain,* r makes them cross, and λ rises by one at a full grid (S4).
- *The bases exist.* The raising case occurs along a row of any full grid with a chain of two splits. The keeping case needs an
  empty cell at a corner, as in the new row after a subdivision (on a full grid such a corner lands on an occupied cell, a copy;
  wording corrected after the referee). ∎

**R2.**
- *Exactness needs a clean witness.* A rule reading a tier decides each knot set by its picture alone, so it treats a whole picture
  class alike. If it accepts a class containing a raising move, it accepts a raising extension. So an exact rule accepts only clean
  classes, and then it accepts an extension that keeps two orders only if that extension has a knot set in a clean class.
- *Accepting every clean class attains the bound.* It accepts no raising extension, and it accepts every extension that keeps two
  orders and has a clean witness. ∎

## What this leaves to the computation

The clean-witness fraction at tiers 1, 2 and the closure tier on the bases SEED with knot-local moves reaches, and whether any of
them is 1.

## Provenance

Local. The advisor proposed R2's measure (the best rule over picture classes), the closure tier, and the warning that on small
bases a radius-two ball covers most of the base.
