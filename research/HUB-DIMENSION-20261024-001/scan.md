# Bounded scan: what bits see of a three-manifold

Date 2026-10-24. Scope: one bounded idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and
enter claims only as cited hypotheses, never as admitted evidence.

## Question

Native gluing builds surfaces (`SURFACE-GLUING-20261024-001`). A three-manifold needs more than pairwise sharing. What is known about
counting labellings of a triangulation's edges, and which counts are three-manifold invariants?

## Query families

- Pachner moves for singular and simplicial triangulations.
- Dijkgraaf–Witten invariants for finite abelian groups; counting flat connections.
- Turaev–Viro invariants for the Fibonacci category; sign problems of non-abelian string-nets.
- The census of one-tetrahedron triangulations.

## Sources and relevance

| Source | Relevance |
| --- | --- |
| Pachner (1991); Matveev and Piergallini for singular triangulations | Any two triangulations of a closed three-manifold are related by 2–3 and 1–4 moves and their inverses, so a count that changes by a fixed factor under each move gives an invariant after normalization. |
| Dijkgraaf and Witten (1990) | For a finite group G, labellings of edges by G that are flat on triangles count homomorphisms from the fundamental group. For the group with two elements this is the mod-2 first cohomology, up to a factor per vertex. |
| Turaev and Viro (1992) | State sums with labels on edges, weights per edge, per triangle and per tetrahedron (6j symbols), and per vertex; for the Fibonacci category these weights involve the golden ratio. |
| [Velenich, Chamon, Cugliandolo, Kovrizhin, arXiv:0911.1132](https://arxiv.org/abs/0911.1132) | Fibonacci string-nets have off-diagonal elements of mixed sign: a sign problem attributed to interference. |
| [Smith, Golan, Ringel, arXiv:2005.05343](https://arxiv.org/abs/2005.05343) | Intrinsic sign problems in topological field theories: when exchange statistics do not form complete sets of roots of unity, no sign-free local model exists. |
| Burton's census (Regina) | One-tetrahedron closed orientable triangulations: the sphere (two of them), L(4,1) and L(5,2). |

## Imported ideas and local discriminators

- **Hubs are forced.** Labels on edges are shared by every triangle around the edge. Labels on faces, shared by exactly two
  tetrahedra, give a native network whose graph is the dual graph.
- **Discriminator for A.** The local move identities can be checked for every symmetric law of bits on edges: sixteen triangle rules
  times 2,048 tetrahedron rules. Explicit move sequences on small singular triangulations certify global failure.
- **Discriminator for B.** With Turaev–Viro-form weights, the move identities are polynomial equations; test whether any real solution
  is non-negative.

## Overlaps and barriers

- **Classical overlaps.** Parity counting is classical (Dijkgraaf–Witten for the two-element group). The Fibonacci sign problem is
  known in physics as a sign problem of string-nets.
- **Local contribution.** A census of all symmetric bit laws, and an elementary algebraic certificate of the sign. No census of
  Boolean edge laws under Pachner moves was found in the bounded search.

## Effect on selection

- Ticket A: the census, parity and the blindness of native networks.
- Ticket B: the Fibonacci sign.

## Novelty status

- `known-overlap-found` for parity and for the Fibonacci sign problem in its physical form.
- `no-overlap-in-bounded-search` for the census and for the algebraic certificate.
