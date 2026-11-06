# Bounded scan: twists in three dimensions

Date 2026-10-25. Scope: a short idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and enter
claims only as cited hypotheses, never as admitted evidence.

## Question

Symmetric edge-bit laws see a closed three-manifold only through |H¹(M; Z₂)| (`HUB-DIMENSION-20261024-001A`), and the Fibonacci rule
needs a negative weight (`HUB-DIMENSION-20261024-001B`). The six open knots are the Fibonacci knot with a twist
(`NATIVE-APPROX-20261024-001B`). Do twisted, ordered rules let bits see more, or remove the sign?

## Sources and relevance

| Source | Relevance |
| --- | --- |
| Dijkgraaf and Witten (1990), group cohomology and ordered triangulations | State sums on ordered triangulations; with a finite group and no cocycle they count homomorphisms π₁(M) → G, with a nontrivial Z₂ cocycle they need signs. With one bit per edge the group is Z₂. |
| Turaev and Viro (1992) | State sums from 6j-symbols; the Fibonacci data contain the gauge-invariant entry −1/φ. |
| [Smith, Golan and Ringel, *Intrinsic sign problems in topological quantum matter*, arXiv:2005.05343](https://arxiv.org/abs/2005.05343) | Criteria under which no local basis makes a topological phase sign-free. |
| [Velenich, Chamon, Cugliandolo and Kovrizhin, arXiv:0911.1132](https://arxiv.org/abs/0911.1132) | The Fibonacci string net has a sign problem in its natural basis. |

## Discriminators

- **Counting laws.** An exhaustive census of laws with any triangle rule read in vertex order and any tetrahedron rule, possibly
  depending on orientation, under the ordered 2–3 and 1–4 moves (ticket A). Scoping with a SAT solver: 354 surviving laws, exactly the
  seven symmetric laws wherever the triangle rule contains what they need; none uses orientation.
- **Positive weights.** For the Fibonacci and twisted Fibonacci supports, whether positive Turaev–Viro-form weights exist, and on which
  supports (ticket B). Scoping: some identities have positive terms on one side only, so full support is impossible; the consistent
  supports are constants and parity classes.

## Novelty status

- `known-overlap-found` for the invariants themselves (Dijkgraaf–Witten for Z₂).
- `no-overlap-in-bounded-search` for the census of ordered Boolean edge laws and the support classification.
