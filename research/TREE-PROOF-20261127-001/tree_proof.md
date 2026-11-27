# The cost of flipping two families' facts, and the tree it makes

`TREE-PROOF-20261127-001`, at the coordinator's request while `SELECTED-KNOTS-20261127-001`'s referee runs. A proof,
not refereed; each step is marked **proved** (here, from the engine's definitions) or **computed** (checked on records).

## Setting

A connected start S grows by ordinary parity growth (the canonical engine, the ordinary count), funded and not closing
through round t. Read the stage as the graph Γ_t whose points are its knots and one outside point U, with one link per
distinction (a shared distinction joins its two holders; a loose one joins its holder to U). Γ_S is S's own graph
without U. A **family** is a class of S's live knots (those holding a loose distinction), two joined when some knot
shares a distinction with each (the engine's candidate rule); L_A is family A's start knots with all their
descendants; λ_A is the parity of L_A's loose distinctions at round t (equal to A's start fact plus a sum of laws,
`THIRD-LAYER-20261126-001` referee R1, argument.md). The **distance** d(A, B) is the least number of links of Γ_S on a
route from a live knot of A to a live knot of B: a step count on the meeting pattern, not a bond distance. Write

  w_t(A, B) = d(A, B) + 2t + 2, and c_t(A, B) = the least size of an allowed change of the stage at round t that flips
  λ_A and λ_B and no other family's fact.

## Engine facts used

- **E1.** A birth takes one distinction from each of its parents, and each round takes every loose distinction of
  every live knot (asserted by the engine). *Engine fact; checked on every record read.*
- **E2.** The parents of a birth are pairwise candidates (a group is a set of pairwise candidates). *Engine fact, by
  the group rule.*
- **E3.** A birth with no fresh distinction is the only birth of its connected structure; so, while growth does not
  close, every birth has a fresh distinction. *Proved in `ERASURE-AND-CLOSING-SIGNS-20261121-001B` (closing law).*

**Lemma 1 (lineages are closed).** A birth's neighbours in Γ_t are its parents and its children, and all its parents
lie in one lineage. *Proved* (THIRD-LAYER referee R1, argument.md; also the draft of this thread): a birth holds its
inputs, shared with its parents, and its fresh distinctions, loose until its children take them; by E2 at round 1 its
parents are candidates, so one family, and at later rounds two parents with a common neighbour have a common parent.

## The theorem

**Theorem.** For every pair of families A, B, c_t(A, B) is the length of a shortest route from A to B in the complete
graph on the families with lengths w_t. In particular c_t(A, B) = d(A, B) + 2t + 2 unless some chain of families
A, C_1, ..., B is shorter, which can happen only while 2t + 2 is small against the distances (on the records, only at
round 0).

**Upper bound. Proved.** *Rising route:* from a live start knot a, a loose distinction of a is taken at round 1 by a
birth (E1), which has a fresh distinction (E3), taken at round 2 by a child, and so on: t + 1 distinctions from a to
one of L_a's loose distinctions at round t, each birth on the way holding exactly two of them. *Segment:* for families
C, D, take a shortest route of Γ_S from a live knot of C to a live knot of D (d links, no knot twice) and a rising
route at each end; the union meets every knot evenly, flips λ_C and λ_D (one loose distinction of each lineage) and no
other family's fact (the route uses no loose distinction), and has w_t(C, D) distinctions. *Chain:* the sum of the
segments along a chain of families from A to B is an allowed change flipping exactly λ_A and λ_B (each family inside the
chain is flipped twice), of size at most the chain's length. So c_t ≤ the shortest chain.

**Lemma 2 (no shortcut through births). Proved.** Every route of Γ_t − U between two start knots can be replaced by a
route of Γ_S that is no longer. *Proof.* By Lemma 1 a route that leaves the start goes up and comes down through births
of one lineage. At a highest birth b of such a stretch the route arrives from one parent b′ and leaves by another
parent b″. By E2, b′ and b″ are candidates: if they are births, their common neighbour is a common parent q (Lemma 1),
and replacing b′, b, b″ by b′, q, b″ keeps the length and lowers the stretch; if they are start knots, they share a
neighbour w in Γ_S, and b′, w, b″ is a route of Γ_S of the same length. Repeat until no birth is left. ∎

**Lower bound. Proved.** Let z be an allowed change of size c_t(A, B) flipping exactly λ_A and λ_B. Take away U: the
knots holding an odd number of z's loose distinctions are odd points of z's other links, an odd number of them in L_A
and in L_B and an even number in every other lineage. A set of links whose odd points are these splits into routes
pairing them up, sharing no link, and each odd point brings at least one loose distinction of z. Link the families of
the two ends of each route that joins two lineages: A and B are the only families meeting an odd number of these
routes, so they contain a chain of families from A to B. A route from a round-t birth of L_C to one of L_D comes down at
least t links to a start knot of C, crosses to a start knot of D in at least d(C, D) links (Lemma 2), and climbs at least
t links: at least d(C, D) + 2t, and with its two loose distinctions at least w_t(C, D). Summing over the chain,
|z| ≥ its length. ∎

**Computed.** All 6,839 pair costs recorded by `SELECTED-KNOTS-20261127-001`'s frozen runs equal the shortest chain;
the chain is shorter than d + 2t + 2 on exactly the three round-0 rows where that study's SK1 failed, and equal to it
on every other row ([`chain_check.py`](chain_check.py), [`chain_check.json`](chain_check.json)).

## Consequences

- **The cost of a set of families. Proved.** The least change flipping the sum of the facts of a proper set T of
  families is the least w_t(A, B) with A in T and B outside it: a chain leaving T has an edge leaving T, and that edge
  alone is a cheaper chain. (SK2, which held everywhere.)
- **The class facts at a scale. Proved.** At the scale k (any allowed change of at most k distinctions), a sum of
  family facts is kept exactly when T is a union of the clusters of families joined when d + 2t + 2 ≤ k; so they form a
  space of dimension the number of clusters less one. (SK3, which held everywhere.)
- **The tree. Proved.** As t grows at fixed k, the threshold k − 2t − 2 on d falls by two a round, and the clusters
  split along the single-linkage tree of the families by d: S's distances fix the tree, and the scale and the round only
  pick the level.

## Distance, the owner's premise, and the reading

- **Which distance.** d is a step count on the meeting pattern between families (the glossary's step counts, lesson
  7.3), not bond distance (lesson 2.4). But c_t is a distance between allowed states: the least number of distinctions
  in which two allowed states differ when they differ in exactly A's and B's facts. And c_t has the same clusters as
  w_t at every threshold (a chain of length at most k has every edge at most k), so **the tree is the single-linkage
  tree of distances between allowed states alone**, and for t large enough c_t − 2t − 2 returns d itself. This bears on
  the owner's premise that distance is the only form of information (A97): what growth selects at the second layer is
  read off distances, with nothing else supplied. The families themselves are read as the finest clusters.
- **Which reading the model would use.** None is needed for the tree: c_t is defined without a reading of a small
  change. A reading enters only to call some sums "class facts" at a round: the scale k is then a free resolution the
  model does not fix, and the shortest-change reading, which ties a shortest change through every distinction, hides
  the tree on most sampled rows (11 to 32 per cent show it, `SELECTED-KNOTS-20261127-001`). So the honest statement is
  that the model supplies the costs and their tree; which level counts as "the facts" is a reading, a scaffold.

## What is not covered

Growth that closes or stalls before round t (the rising routes need a fresh distinction at every birth; E3 gives it
only while growth does not close); the forbidding cuts (E3 fails: a birth that is not implied may get no fresh
distinction); capped group rules (E2 holds for every uncovered candidate pair, the built-binding referee found, but
not checked here); other laws.
