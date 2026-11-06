# Bounded scan: can hub-free gadgets imitate a hub?

Date 2026-10-24. Scope: one bounded idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and
enter claims only as cited hypotheses, never as admitted evidence.

## Question

Native networks put every variable in two knots. A hub puts one variable in three. Deciding native networks is easy for every knot
(`NATIVE-HARDNESS-20261024-001`), and approximate counting is settled for 28 knots and open for six (`NATIVE-APPROX-20261024-001`).
Can a hub-free gadget imitate a hub, a three-leg function concentrated on 000 and 111, strongly enough to matter for approximate
counting?

## Query families

- Gadgets realizing equality approximately in Holant problems; the equivalence of counting problems with Holant problems plus the
  ternary equality.
- Approximation dichotomies for bounded-degree counting with pins.
- Correlation decay and uniqueness for ferromagnetic two-spin systems on bounded-degree graphs.

## Sources and relevance

| Source | Relevance |
| --- | --- |
| [McQuillan, *Approximating Holant problems by winding*, arXiv:1301.2880](https://arxiv.org/abs/1301.2880) | Windable strictly terraced functions are closed under connected circuits (Theorem 4); a three-place function is windable exactly when F(x)F(x̄) is at most the sum of its three split products (Theorem 6). So every gadget of a windable knot has hub ratio at most √3. |
| [Dyer, Goldberg, Jalsenius and Richerby, *The complexity of approximating bounded-degree Boolean #CSP*, arXiv:0907.2663](https://arxiv.org/abs/0907.2663) | With pins and degree at least 6: exact if affine, #BIS-equivalent if implicational, otherwise no FPRAS unless NP = RP. A near-exact hub would carry an open knot into this regime. |
| [*Boolean approximate counting CSPs with weak conservativity, and implications for ferromagnetic two-spin*, arXiv:1804.04993](https://arxiv.org/abs/1804.04993) | Counting problems with relations F are equivalent to Holant problems with F and the ternary equality: the hub is exactly what separates the two. |
| [*Zeros of Holant problems: locations and algorithms*, arXiv:1807.09129](https://arxiv.org/abs/1807.09129) | Parallel-edge gadgets approximate weighted equalities [1, 0, μ] on two legs: rebalancing a wire is cheap, unlike a three-leg hub. |
| [*Approximability of the six-vertex model*, arXiv:1712.05880](https://arxiv.org/abs/1712.05880) | Hardness of approximation for a Holant problem with disequality edges, by reduction from maximum independent set on cubic graphs: the template a soft hub would feed. |
| Lyons (1989), on the Ising model on trees; Weitz (2006), correlation decay | On the binary tree the ferromagnetic Ising model orders only when tanh β > 1/2. A symmetric three-leg hub [a, b, b, a] placed on a cubic network passes deviations with factor (a − b)/(a + 3b) (scratch computation), so it reaches that threshold only when a/b > 5. |
| [Meng, Wang, Xia and Zheng, CCC 2025, arXiv:2502.05597](https://arxiv.org/abs/2502.05597) | Exact counting dichotomy for Boolean Holant problems with an odd-place signature; exact, not approximate. |

## Imported ideas and local discriminators

- **Exact hubs are excluded already.** Supports of native gadgets are co-independent (`SURFACE-GLUING-20261024-001B`, Lemmas 1–4),
  so they exclude at most half their tuples; the equality on three legs excludes six of eight.
- **Discriminator for the soft question.** The hub ratio min(F(000), F(111)) / max over the other six F(x), on every axis after
  complementing legs. Scoping (scratch, disclosed in ticket B's contract): open-knot gadgets reach about 1.21, not-all-equal 1.16 to
  1.33, Fibonacci exactly 1; compositions of the best hubs do not amplify.
- **A structural handle.** Exchanging the component of the difference graph that contains terminal 1 maps every diagonal pair whose
  difference does not link all three terminals onto an off-diagonal pair. Only linked pairs can push the ratio past √3.

## Overlaps and barriers

- No result on hub simulation for approximate counting of native (degree-two) networks was found in this bounded search. The
  degree-two regime is exactly where the bounded-degree classification stops.
- Barrier: a bound on the hub ratio over all gadgets is a closure property; McQuillan's windability is the known closure for the
  windable knots, and the six open knots are not windable.

## Effect on selection

- Ticket A: the settled knots and the exchange lemma (proof).
- Ticket B: a pre-registered search for strong hubs among the open knots (experiment).
- Ticket C: a bound on linked pairs for the open knots (proof attempt).

## Novelty status

- `known-overlap-found` for the windable bound (McQuillan) and for the impossibility of exact hubs (local, earlier epic).
- `no-overlap-in-bounded-search` for hub ratios of the open knots and the exchange lemma's use here.
