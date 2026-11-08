# Is bond distance the only native spacing?

Epic `BOND-CHAIN-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it comes from.** The selected next step of `CRYSTAL-UP-20261108-001`, backlog B4 of the goals doc (G1, question 9),
  started on 2026-11-08 with the coordinator's agreement: the first challenge of A12, that bond distance (the size of the least
  knot through two distinctions, minus one) is a law's own spacing.
- **The alternatives.** Chain distance: the fewest knots in a chain from one distinction to the other, each sharing a
  distinction with the next (counted in knots), or the fewest distinctions in such a chain's union (counted in distinctions).
- **Frozen before anything ran** (the epic's objective). A12 is confirmed for a class of laws if on it every chain measure either
  collapses or equals bond distance up to a constant; it is overturned if some law has a chain measure that is a non-degenerate
  spacing and changes a dimension or circle shape that bond distance reads.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **On parity laws chains add nothing.** If two non-parallel distinctions are joined by a chain of knots, a knot inside the chain's union contains both (matroid connectivity). So counted in knots every joined pair is one step apart, and counted in distinctions the chain gives back bond distance. Every law measured for space so far is a parity law or composes the same way. | proved | A |
| 2 | **Off parity laws the measures part exactly at gates.** Of the 1,156 laws of two three-place knots sharing one distinction, a knot joins the far ends exactly when no single value of the shared distinction satisfies both knots; in the 72 gated laws none does. Chains of single clauses are spanned by a knot exactly when they chain as implications. | proved (exhaustive) | B |
| 3 | **A law where only the chain measure sees a line.** The NAND thread, clauses not(s(t−1) ∧ a(t) ∧ s(t)), has no knot beyond its clauses: bond distance sees separate clauses, while chain distance counts one step per clause, a number line. With the signs of an implication (the atom thread) the same chain is a line for both. | proved | B |

## Answer

**By the frozen test A12 is overturned as a universal statement:** in the NAND thread a chain measure reads a line where bond
distance reads none. It holds wherever knots compose across their shared distinctions, which includes every parity law and every
law the program has measured for space, so no published result changes. What decides between the measures is the foundation's
own contact rule: "two independent A-k and B-k relations make k a common hub, not one touch between A and B; shared variable
identity alone is insufficient" (`AGENTS.md`). At a gate one value of the shared distinction satisfies both knots and no knot crosses
it. Bond distance follows that rule; chain distance does not. A38 replaces A12: spacing is read
through knots that compose, and a chain through a gate is a hub, not space.

## Reading

**Interpretation, not a theorem.**
- **Space needs composition.** A line of knots is a line of space only if each meeting composes into a knot across it. In clause
  chains this is the arrow of implication: a distinction concluded by one clause and assumed by the next carries the bond; read with
  the same sign on both sides it is a switch that turns both clauses off.
- **Parity laws are the clean case.** Their knots are a matroid's circuits, so any two knots that meet compose; that is why bond
  distance and chains never part there.
- **Hubs are in scope** (the owner, 2026-10-29). The NAND thread is a hub chain with a natural count; whether hub chains build any
  shape of their own is a separate question, not one about contact.

## Literature and provenance

- **Sources.** Matroid connectivity (Whitney 1935; Oxley, *Matroid Theory*, Proposition 4.1.2); the pure-literal idea, a variable
  that satisfies every constraint it occurs in (Davis and Putnam 1960).
- **Classification.** Known-with-delta: both ingredients are classical; their use to split the program's two measures, and the
  gate criterion on three-place knots, were not found.

## Workspace assumptions

- **Challenged.** A12: Overturned as a universal statement by its frozen test (the NAND thread); it holds on parity and gate-free
  laws.
- **Added.** A38, the reading that replaces it: spacing is read through knots that compose (bond distance); a chain through a gate
  is a common hub, not space. It rests on the foundation's hub rule.
- **Rechecked.** Everything under A12's Rests on it was measured on parity laws (the gauge and Tseitin lattices, Ledrappier's axis,
  the periodic and pinwheel parity laws, the product of threads) or on the atom thread, which is gate-free: no claim changes.

## Ratio

Since the epic opened:
- **Substantive.** Two proved results (A, B).
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — challenge A12 with chain measures | **Status:** Successful | Decided by the frozen test: overturned in general, holds where knots compose |
| Local direction — native measures of spacing | Practically exhausted | Chains either add nothing or count hubs |
| Broader exploration — G1 lines | Known alternatives | Two bits per tile (B8); edge labels (A35); hub chains |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | Its measure now rests on a theorem for parity laws and on the hub rule elsewhere |

**Corrections:** none. **Goals:** a G1 checkpoint (capability gained); B4's A12 part taken and closed; no goal change.
**Assumptions:** A12 overturned as a universal statement by its frozen test; A38 added (Assumed) in its place.

- **What is left open.** Whether gate chains, which are hub networks, build shapes of their own worth calling space, and how
  many hidden bits per tile the pinwheel needs.
- **The missing bridge to G1.** A law that chooses its own dimension; this epic secures the ruler, not the space.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two bits per tile, products first (backlog B8) | 2/3 — Substantial | 2/3 — Testable | Products of two one-bit decorations, with their four-label law computed, against the crystal list (rhombus, bricks, dominoes, the mixed-orientation crystals) → a product no crystal escapes, or none | Selected · awaiting go-ahead |
| 2 | Edge labels, as in Radin's rules (A35's challenge) | 2/3 — Substantial | 1/3 — Stated | An edge substitution with one bit per edge against the same crystals → one that excludes them all, or none | Alternative · deferred |
| 3 | Hub chains in two dimensions | 1/3 — Incremental | 2/3 — Testable | A plane of gated knots: chain balls' growth and circle shape → a hub shape, or the grid drawn in | Alternative · deferred |
| 4 | Dimension three on crystallizations (G2) | 1/3 — Incremental | 1/3 — Stated | Laws beyond one bit per edge on gems of lens spaces → an invariant past mod-2 cohomology | Alternative · deferred |

1. **Two bits, products first.**
   - **Payoff 2.** One bit per tile never forces the pinwheel; two bits is the next count of the plane's price of roundness, and a
     product that no crystal escapes would bound it at two.
   - **Concreteness 2.** A product of two one-bit decorations is a decoration on four labels; its law comes from the same labelled
     closure, and the crystals and the independent check exist (`CRYSTAL-UP-20261108-001B`).
   - **Uncertainty.** Whether products are the right family: a forcing two-bit decoration need not be a product.
   - **Status.** Bound: one epic. Not started: the coordinator decides.
2. **Edge labels.** Tests whether the count depends on where the bits sit; the edge substitution must be defined first.
3. **Hub chains.** A hub network has a natural count, but the grid it lives on is drawn, so the payoff is small.
4. **Dimension three.** One-bit laws on triangulations are classified; beyond them classical answers are expected.
