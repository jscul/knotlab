# Correlations between distant parts under not-all-equal: held by the whole, or read at a knot?

Epic `NAE-WEIGHTS-20261127-001`, at the coordinator's pick (direction 2 of `NAE-LAYER-20261127-001`, whose referee is
running). A check by the thread, not registered; computed. The sections down to "Frozen" were committed before the run.

## The question

Under not-all-equal nothing is kept by small changes and the only exact relations are compositions that rings and growth
erase (`NAE-LAYER-20261127-001`, referee pending). A weighting of the allowed states can still give distant
distinctions a correlation. Is such a correlation a fact held by the whole, or is it read at a single knot? The weighting
is a scaffold: the equal weighting of allowed states is the advisor's ([answer](../ONE-STATEMENT-20261127-001/advisor/answer_nae.md), 1(c));
the swap is the weighting by one round's completions, which the growth itself supplies.

## Frozen

**Predictions (the advisor's)** ([`weights.py`](weights.py)).
- **W1.** On every tree-shaped census start, for every pair of distinctions, the mean of the product of their signs under
  the equal weighting is exactly the product, over the knots on the route between them, of −1/(2^(a−1) − 1), a each
  knot's places.
- **W1r.** On SIGNED-COUNT's rings, the two routes' products divided by one plus the ring's own product reproduce the
  exact means −15/41, −33/95 (with the far edit) and −3/13.
- **W2.** On every tree-shaped census start, sign products of even size carried on disjoint sets of knots are exactly
  independent under the equal weighting.
- **W3.** The ring of four with one loose distinction per knot has even parity of its four shared distinctions in 50 of
  its 82 states.

**Read under the other weighting** (completions after one round): W1 and W2 on the same starts, no prediction.

**How the answer will be given.** If W1 and W2 hold, a correlation between distant parts is the product of each knot's
own factor along the route: no single knot reads it, but it carries nothing beyond the knots' own factors (the chain is
a Markov chain), so it is held by the route only in the weak sense. Whether the swap of weighting keeps that is the test
of the scaffold.

## What was found ([`weights.json`](weights.json))

**Under the equal weighting.**
- **W1 held exactly:** on all 761 pairs of distinctions of the 15 tree-shaped census starts, the mean product of signs
  is the product of −1/(2^(a−1) − 1) over the knots on the route.
- **W1r held exactly:** the route formula gives −15/41, −33/95 and −3/13 on SIGNED-COUNT's rings, their exact means.
- **W3 held:** 50 of the ring of four's 82 states have even ring parity.
- **W2 failed as frozen:** 351 of 7,445 pairs of sign products on disjoint knot sets are not independent. Read after
  the run: on starts of three-place knots only, every pair of products carried on distinctions that only the two sets'
  own knots hold is independent (252 of 252); the 27 failures there use a distinction that a knot outside both sets also
  holds; and every start with a knot of four or more places has failures even inside (52), since such a knot couples
  all its places at once (its law has a term on four of them, not only on pairs).

**Under the other weighting** (each state weighted by its completions after one round): the route formula holds on 6
of 453 pairs and independence on 294 of 2,680 (five starts do not grow). The births of the round join loose
distinctions of different knots, so they add couplings the start does not have.

**So, is a correlation between distant parts held by the whole?** Under the equal weighting, on starts with no ring and
three-place knots, it is no single knot's, but it is exactly the product of each knot's own factor along the route:
the chain holds nothing beyond its knots' factors, and separated parts are independent. That is the weak sense of
"held by the whole", the same as the composed relations of `NAE-LAYER-20261127-001`. Rings add the loop's own term
(the route formula over both routes, normalised), and a knot of four or more places carries a joint term of its own,
a fact read at that one knot. Under the growth's own weighting the picture changes entirely: the result is about the
equal weighting, a scaffold, not about the model.

**Not run.** Starts with rings past SIGNED-COUNT's two; later rounds; other weightings.
