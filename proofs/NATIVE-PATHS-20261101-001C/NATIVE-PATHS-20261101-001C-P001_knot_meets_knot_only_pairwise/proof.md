# Knot meets knot only pairwise: failure is invariant exactly under cuts

Status: Proved

Ticket `NATIVE-PATHS-20261101-001C`, 2026-11-01.

## Question

- **What B left open.** Ticket B left cuts of four or more edges unclassified.
- **The remaining candidate.** B named one remaining candidate for a native path between the parts of a knot's space: a cut across which
  a knot meets a knot, with no hub.
- **What complementarity allows.** Two sides that both accept knots can fail together only as complementary parity cosets
  (`KNOT-COMPOSE-20261101-001A`, Lemma 3).
- **The question here.** Does any knot's space have such a cut with three or more edges?

## Dependencies

- **`NATIVE-PATHS-20261101-001A`.**
  - The setting.
  - The four facts about side relations.
  - The signed Seymour bound: a connected cubic signed system that is not colourable is minimally so.
  - Through A, `KNOT-COMPOSE-20261101-001A` Lemma 3 (complementarity).
- **`THREEFOLD-SPACES-20261030-001A`.** Theorem 1: a connected cubic system is not 2-colourable iff its incidence matrix is
  sign-nonsingular (SNS).
- **`THREEFOLD-AMPLITUDE-20261030-001A`.** Lemma 1(i): in a matching covered bipartite graph, the cycles π Δ π′ between perfect matchings
  span the cycle space, so its Pfaffian signings form one switching class.

## Setting

- **The space.** H is a knot's space, with incidence graph B(H). B(H) is connected, cubic and bipartite. Every edge lies in a perfect
  matching, so B(H) is matching covered and has no bridge.
- **Twists.** For a set t of incidences, H^t is the signed system in which every incidence in t reads its point's colour exchanged.
- **Cocycles.** A *cocycle* is an edge set ∂(S): the edges with exactly one end in S, for some vertex set S.
- **Knots on channels.** A relation on k channels *is a knot* when it is non-empty and constrained, and every (k − 1)-place projection
  is full. This is K1–K3, with the channels as variables.

## Theorem

1. **The twist criterion.** H^t is not colourable iff t is a cocycle of B(H).
2. **Knot meets knot only pairwise.** If both sides of a nontrivial k-edge cut of H accept knots on the k channels, then k = 2.

**Consequences.**
- **Two known facts as special cases.**
  - The atom lemma is the case |t| = 1: a single edge of a bridgeless graph is never a cocycle.
  - Item 2 of A agrees: inside a 2-edge cut the only cocycles are ∅ and the cut itself.
- **The parts meet in three ways.**
  - Knot meets knot only across two channels, as two-place parity (A, item 2).
  - Across three channels, a knot meets a hub (A, item 3).
  - Across more channels, never knot against knot.
- **So B's candidate does not exist.** No cut of a knot's space carries a hub-free meeting of knots on three or more channels.

## Proof

**Item 1, a cocycle keeps the failure (switching).**
- Let t = ∂(S) and let c colour H^t. Put c′(p) = c(p) ⊕ [p ∈ S].
- At an incidence (L, p), H^t's line L reads c(p) ⊕ [(L, p) ∈ t]. Since [(L, p) ∈ t] = [L ∈ S] ⊕ [p ∈ S], this equals c′(p) ⊕ [L ∈ S].
- So every line reads its c′ values, all exchanged or none, and not-all-equal does not see the exchange. Then c′ colours H, which is
  impossible.

**Item 1, a failure forces a cocycle.** Suppose H^t is not colourable.
- **M_t is SNS.** Let M_t be its signed incidence matrix, with entry (−1)^[e ∈ t] at each incidence e. Every real matrix M′ with the same
  sign pattern is nonsingular.
  - If M′x = 0 for some x ≠ 0, colour the points with x > 0 by 0 and those with x < 0 by 1. Colour the rest by a colouring of the lines
    that avoid the support of x; it exists because H^t is minimally non-colourable (A).
  - A line meeting the support has nonzero signed terms of both signs, so it reads both values. This colours H^t, a contradiction.
- **M_∅ is SNS** (THREEFOLD-SPACES A, Theorem 1).
- **One sign for every matching.** In an SNS pattern every nonzero term of the determinant has one sign.
  - The term of a perfect matching π is sgn(π) for M_∅ and sgn(π)(−1)^|π ∩ t| for M_t.
  - So |π ∩ t| has the same parity for every perfect matching π.
- **So t is a cocycle.**
  - The cycles π Δ π′ span the cycle space (THREEFOLD-AMPLITUDE A, Lemma 1(i)), so every cycle meets t evenly.
  - A set meeting every cycle evenly is a cocycle (the cut space is the orthogonal complement of the cycle space). ∎

**Item 2.** Let ∂(X), with edge set F, be a nontrivial k-edge cut whose two sides both accept knots.
- **The sides are complementary parity cosets.**
  - By complementarity each side has at least 2^(k−1) states.
  - The sides are disjoint, because H is not colourable. So each has exactly 2^(k−1) states and is a parity coset, and they are
    complementary: R_X = E and R_X̄ = Ē.
- **Twisting cut edges.**
  - Twisting a set T ⊆ F exchanges what the slot side reads on the channels in T. So H^T is colourable iff (R_X ⊕ t) ∩ R_X̄ ≠ ∅, where t
    is T's indicator.
  - For T of even size, E ⊕ t = E is disjoint from Ē, so H^T is not colourable. By item 1, every even subset of F is a cocycle; in
    particular every pair.
- **Suppose k ≥ 3.** Fix e₁ ∈ F.
  - **Each other cut edge is a bridge of B − e₁.** B − e₁ is connected, and each {e₁, e_j} = ∂(S_j) disconnects B.
  - **They lie in series.** Every bridge of B − e₁ separates the two ends of e₁, since B is bridgeless. So B − F consists of k blobs in
    cyclic order: consecutive blobs are joined by one edge of F, and there are no other edges between blobs.
  - **The shores must alternate.** Each blob lies in one shore, and every edge of F joins the two shores, so the shores alternate around
    the cycle of blobs.
  - **Contradiction.** For odd k this is impossible. For even k ≥ 4, each shore holds at least two blobs with no edge between them, so it
    is disconnected. Either way it contradicts nontriviality, so k = 2. ∎

The proof of item 1 uses only that H is a connected cubic signed system that is not colourable. So the criterion holds for signed
knot's spaces too, with t read relative to H's own signs.

## Checks

`check.py` (`result.json`, about 250 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | The twist criterion on every twist pattern of every nontrivial 2- and 3-edge cut of the ten knot's spaces. | 1568 patterns: 432 cocycles stay non-colourable, 1136 others become colourable |
| 2 | The twist criterion on 60 random incidence sets and 60 random cocycles ∂(S) per space. | 1200/1200 |
| 3 | Side relations at every nontrivial 2- and 3-edge cut of the ten spaces, and at every nontrivial 4-edge cut of Fano, the chains of 2 and 3, and the 3-cycle. Both sides are knots exactly at the 2-edge cuts. | 40 two-edge (both knots), 176 three-edge (2/6), 234 four-edge (6/10 or 6/6) |
| 4 | Controls off the knot's spaces. | pass |

**The controls.**
- A colourable system stays colourable under the empty twist (a cocycle).
- The colourable even cycle of four Fano blocks becomes non-colourable when one junction is twisted, which is not a cocycle.

**The 4-edge cuts in these spaces.** They are not new interfaces.
- Each shore holds a vertex carrying two cut edges: one incidence and its two ends, or the like.
- The sides accept 6 and 10 states. In the 3-cycle, twelve cuts have 6 and 6.
- Neither side is ever a knot on the four channels.

## Reading

This section is interpretation, kept apart from the theorem.

- **Failure lives on cuts.** A knot's space keeps failing under a twist pattern exactly when that pattern is a coboundary, so the
  failure depends only on the pattern's class modulo cuts.
- **What the law reads.** For each pattern it reads one bit: whether the pattern's holonomy vanishes around every cycle.
- **An earlier echo.** This matches the earlier finding that free contact keeps one H¹ class per loop (HOLES-COHOMOLOGY).
- **The 2-versus-3 boundary.** Inside the knot's spaces, a hub-free meeting of knots is always two-place.
  - Two-place parity is the 2-clause level, which the owner's framing excludes from loops and topology.
  - So three-place emergence never passes from one part to another without a hub.
  - Hence no native path made of knots exists between the parts of a knot's space.

## What this does not establish

- **Other meetings across four or more channels.** Sides that are not both knots are not classified. An example would be a hub on one
  side with more channels.
- **Larger cuts in larger spaces.** Only the four small spaces were enumerated at four edges. Item 2 covers every size and every space,
  but only for knot against knot.

## Novelty

- **Classical.**
  - Sign-nonsingularity (Seymour 1974; Brualdi–Shader).
  - Pfaffian signings and their uniqueness up to switching for matching covered bipartite graphs (Lovász–Plummer; Little).
  - Item 1 is a direct consequence of these, and its folklore risk is high.
- **New here.**
  - Item 2, which turns the criterion into a statement about which interfaces a knot's space can carry.
  - The reading.
