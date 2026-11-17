# Mixed not-all-equal knots on the weave: one broken bond per knot, matchings, and when they stay bipartite

Status: Proved

Ticket `WEAVE-MIX-20261117-001A`, 17 November 2026, by Claude. Epic `WEAVE-MIX-20261117-001`. `check.py` checks N1 to N4 by brute
force on 4 × 4 weaves with random arrangements; that is a check, not the proof.

## Words

- **An arrangement** gives each knot of the weave one of the four not-all-equal-class knots: excluding {p, p̄} for p = 000, 100,
  010 or 001, in place order.
- **Signs.** The knot reads the bond between two of its places as −1 when p agrees on them and +1 otherwise. A bond is
  **broken** for the knot when its two values violate its sign: equal under −1, different under +1.
- **Inconsistent bond.** A bond whose two knots give it different signs. I is the set of inconsistent bonds.

## Statements

- **N1. One broken bond per knot.** In every allowed state, each knot has exactly one broken bond.
- **N2. States are matchings.** Take the weave's knots as the vertices of the honeycomb, with an edge across each bond, and
  subdivide the edge of every inconsistent bond by a new vertex. Allowed states, up to flipping every value, correspond one to one
  to the perfect matchings of that graph whose broken-bond pattern closes up around the torus (one of four sectors; all of them on
  the endless weave):
  - a consistent bond broken for both its knots is a matched edge;
  - an inconsistent bond is broken for exactly one of its knots, and its new vertex is matched to that knot.
- **N3. A count per cell.** With i inconsistent bonds and u broken consistent bonds per cell, 2 = 2u + i, on average over a period.
  - More than two inconsistent bonds per cell empties the base.
  - An arrangement of period one has i = 0 or 2, since each knot's three signs multiply to −1, so the up and down knots differ on
    an even number of bonds.
- **N4. When the matching graph is bipartite.** On the endless weave, the subdivided graph is bipartite iff every distinction
  meets an even number of inconsistent bonds.
- **N5. Only I matters.** Two arrangements with the same inconsistent set have the same states up to flipping a set of
  distinctions (a gauge). So their spectra agree. This is checked here, and proved only as far as N2 makes the states depend on I
  and the matched-edge pattern.

## Proofs

**N1.** For p = 000 the three signs are −1. For the other three, flipping the one odd place turns two of the signs to +1. Either
way the three signs multiply to −1. In a state, the product over a knot's three bonds of (the bond's sign × the product of its
two ±1 values) is the product of the signs, since each value appears twice. A bond is broken exactly when that factor is −1. So
the number of broken bonds is odd: 1 or 3. Three broken bonds is the excluded pair, p or p̄. So the allowed states have exactly
one. ∎

**N2.** A consistent bond is broken for both its knots or for neither. An inconsistent bond is broken for exactly one, since its
two signs differ and its two values break exactly one of them. By N1 each knot is covered exactly once: by a matched edge, or by an
inconsistent bond's new vertex. Every new vertex is covered exactly once. So the broken-bond pattern is a perfect matching.

Conversely, a perfect matching names each bond broken or not. Values are rebuilt along any row of bonds, equal across a bond that
is broken under −1 or unbroken under +1, and different otherwise. They close up around each knot, since each knot then has exactly
one broken bond (by N1 the product condition holds). On the endless weave they are consistent. On the torus they are consistent
exactly when they close up around the two cycles. Two states give the same matching iff they differ by the global flip. ∎

**N3.** Count the pairs (knot, its broken bond). There are two knots per cell. A broken consistent bond counts twice, and an
inconsistent bond counts once in every state. So 2 = 2u + i per cell on average, and i ≤ 2. For period one, the up knot's three
signs and the down knot's three signs each multiply to −1. So the bonds where they differ are even in number: i = 0 or 2. ∎

**N4.** The graph is drawn on the plane with one face around each distinction: a hexagon of the six knots around it. Its length
is 6 plus the number of inconsistent bonds at that distinction, since each such edge was subdivided. A connected planar graph is
bipartite iff all its faces have even length. ∎

## Provenance

- **N1** is the classical frustration count: every triangle frustrated, one unsatisfied bond (Wannier; Blöte and Hilhorst), here
  in gauge-transformed form.
- **N2** is the Moessner–Sondhi mapping between frustrated Ising models and dimers, extended by subdivision to inconsistent bonds.
  Subdividing and contracting a degree-two vertex are standard matching moves.
- **N3 and N4** are elementary.
- **Phases of the matching graph.** For bipartite periodic graphs, Kenyon, Okounkov and Sheffield 2006 give frozen, liquid and
  gaseous phases. For non-bipartite planar ones, triangular-lattice dimers are a disordered Z₂ liquid (Fendley, Moessner and
  Sondhi 2002).
- **The advisor** gave the contraction picture, the parity criterion N4 and the "only I matters" count.
