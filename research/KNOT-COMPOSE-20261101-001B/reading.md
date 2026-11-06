# The native-network reading

Ticket `KNOT-COMPOSE-20261101-001B`, 2026-11-01. Documentation; no new theorem.

## The gate

The repository's instructions admit two complete contacts as a native-network candidate only when they:
- pass every contact gate;
- coexist in one declared substrate;
- preserve endpoint identity;
- compose by a substrate-native law;
- retain composition under admitted restrictions, transports and recodings.

Observer-drawn graphs, larger common hubs and externally imposed composition are rejected.

## Item by item, for compositions of the knot's spaces

| Gate item | Status | Evidence |
| --- | --- | --- |
| Declared substrate | Cubic systems under the knot's law (not-all-equal on every line, any signs). | the program's definitions |
| The units | A knot's space minus a point acts as the knot (exactly not-all-equal, a complete three-place knot) on its three slots. Minus a line, it acts as equality on its three ports. | THREEFOLD-AMPLITUDE (point lemma); KNOT-COMPOSE A, Theorem 4(1) |
| Substrate-native law | Substitution across a 3-edge cut. It is computed from the law itself, exact, with amplitudes multiplying across the cut. No rule is imposed from outside. | THREEFOLD-AMPLITUDE (factorization) |
| Endpoint identity | Nontrivial tight cuts are 3-edge splice cuts, and the decomposition into pieces is recovered from the whole. | THREEFOLD-SPACES (splice calculus) |
| Persistence | Switching changes no count. Relabelling is harmless. The transpose is a recoding that maps knot's spaces to knot's spaces and exchanges every cut's knot side with its hub side. | THREEFOLD-AMPLITUDE; KNOT-COMPOSE A, Theorem 4(4) |
| No larger common hub | **Fails.** Every composition of knot's spaces passes through a hub, an equality on three channels. A composition joining knot to knot without a hub fails only for parity. | KNOT-COMPOSE A, Lemma 3 and Theorem 4 |

## Verdict

**What the gate allows.**
- The knot's selected spaces compose natively, but only as a network of knots joined by hubs.
- By the program's strict reading this is not a hub-free contact network.
- By the owner's decision of 2026-10-29 (hub laws are in scope; a network hub is an equality fan-out), it is a native network of knots
  with network hubs.

**Parity.** The hub-free alternative exists only for parity: two pieces accepting complementary parity cosets fail together knot to knot.
This matches the earlier results in which only parity survives hub-free composition:
- native patterns of patterns (GEOMETRY-LAW);
- native contradictions (NATIVE-HARDNESS);
- Pachner moves in three dimensions (HUB-DIMENSION);
- shared subdivision (SHARED-SUBDIVISION).

**Knot and hub as two sides.** The transpose exchanges them. Which part of a knot's space is the knot and which is the hub depends on
whether colours sit on points or on lines. Both readings are knot's spaces.

## In the owner's terms

- **Everything is relational.** The knot's spaces are relations of knots, and the relation between two knots is always mediated by a
  shared point. A direct relation between two knots, with no third thing, is possible only when the relation is parity, the law that
  hides one full bit.
- **What this says about emergence.** The knot's own topology is composed through hubs. Hub-free composition is linear.

## What remains open

- **Composed topology.** Whether hub-mediated networks of knots give native paths and separation is not addressed. That is the next step
  toward composed topology.
- **Larger cuts.** Cuts of four or more edges with a hub on one side, as in trisum glue, are not classified (A).

## Interest

**2/3** for the composed-topology question. It is the step the contact-first program needs after first emergence. The main uncertainty is
whether paths defined through network hubs can be native rather than observer-drawn.
