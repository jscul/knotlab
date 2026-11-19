# Question for the advisor (DOUBLE-IDENT-20261119-001, before freezing the statement)

You have no tools. Answer only from this text; check the argument and say where it fails.

**Background (you checked all three).** RING-IDENT, CHAIN-IDENT and RELAY-IDENT prove, for the cheapest parity growth of a start
whose knot graph K is connected and *simple*, under (S3) no round-1 group of three and (S4) no two knots with two common
neighbours: round t's junctions are the clusters of t + 1 points of the relayed extended cover (X⁺: blocks N(w) ∩ live, s = open − d
pendant points per live knot with R(open) = 0/1/2 rays; a relay point with two rays on each finite piece when there are two or more
pieces), with parents = R*, loose = |∂|; plus the dimension of tree starts.

**The extension: multigraphs.** In the touch census, 92% of arrangements have two knots sharing two (sometimes three or four)
distinctions. Claim (Lemma M): the growth reads K only through (i) for each knot w (live or not), the set of its live K-neighbours,
and (ii) for each live knot, its open count (places − shared, shared counted with multiplicity). Reason:
- Round 0's neighbour relation is "share a distinction", a set relation; multiplicity changes no candidate, valid set or group.
- A knot's loose distinctions are open = places − shared; which loose bit it gives is immaterial.
- From round 1 on, a new junction shares exactly one bit with each parent, and its other bits are fresh; so all later structure is
  parent-based and multiplicity never re-enters.
- The implied test ("takes every loose distinction") depends only on counts; and it equals GF(2) implication for a connected
  presentation, because the sum of the equations of a set S of junctions is S's loose bits plus its boundary shared bits, so only S =
  everything (or a whole component) sums to loose bits only — unchanged by multiple shared bits between two junctions.

**What simplicity was used for, and the fixes.**
- CHAIN-IDENT's claim that a non-live knot is isolated (true for simple K) fails: with multiplicity a dead knot can have live
  neighbours and is then a common neighbour (its block N(w) ∩ live stays), though it is never a point of X⁺. d_k must be computed
  from the actual live candidates. Nothing in the proofs needs dead knots isolated.
- (S6′) at least two loose distinctions was automatic for simple K; with multiplicity a start can hold exactly one (for example a
  live knot of open 1 whose neighbours are all dead). Then its one offshoot is implied, gets d = 0, and the growth closes at round 1.
- (S3) and (S4) are read on live knots, with common neighbours counted among all knots.

**Evidence so far.** On the touch census's tree-shaped arrangements with double touches, the dimension prediction agrees on 3,980 of
4,012; the 32 others are exactly the starts holding one loose distinction. The full per-round comparison (parents, fresh) on all
26,441 arrangements in the class is running.

**Questions.**
1. Is Lemma M sound? Is there any place a doubled distinction could matter (for instance a junction neighbour relation through two
   bits, the GF(2) argument, or the floor at round 0 if sizes are bare)?
2. Are the proofs' other uses of "simple" covered (girth via (S3)/(S4) on live knots, components via even walks, the finite-piece
   claims)? Is anything else needed, for example for a dead knot that is a common neighbour of two live knots in a cycle?
3. What does three shared distinctions do, beyond making knots dead and enabling the one-loose case?
4. Predict the share of the census in the class, and one risky outcome of the full comparison.
