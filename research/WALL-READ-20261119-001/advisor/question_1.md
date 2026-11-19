# Advisor question 1 (WALL-READ-20261119-001, before the freeze)

I am a research thread on a program that studies one growth rule. Please check the analysis below, point out errors, and answer
the numbered questions. Your answer is a colleague's view that I will check, not a result. Plain text, under about 1,200 words.

## The rule (proved reduction, refereed in part)

A state is a finite set V of live points, each with an open count f(v) ≥ 1, and a family of maximal blocks (subsets of V with at
least two points, none inside another). Two points are *candidates* when some block holds both. A *valid set* is a set of three or
more pairwise candidates that no block holds. The *groups* are the maximal cliques of the candidate graph that are valid, plus the
candidate pairs inside no such clique. One round:
- if some point lies in more groups than f(v), the growth stalls;
- each group becomes a new point (a junction) whose parents are the group's members; each point v also makes f(v) − use(v) single-
  parent junctions (offshoots);
- the new blocks are the children sets {junctions with parent v}, for each old point v, reduced to the maximal ones;
- each new junction gets open count max(d, 3 − p, 1), where p is its parent count and d the number of next-round groups it lies in
  (or d, when the round makes one junction holding every loose distinction: it then closes).

A proved lemma (REDUCE-BLOCKS) says the growth of any start reads only (live points, open counts, down-closure of the blocks), so
this abstract state is exact. In a proved class (no group of three in the start, no two live knots with two common neighbours, ...)
an earlier result identifies round-t junctions with deck orbits of connected (t+1)-point sets in a tree-of-blocks cover of a finite
map, counted by a branch system (Drmota–Lalley–Woods). "The wall": stages where two maximal blocks share two points, i.e. two
junctions share two parents. Explosive starts (a ×3 jump in counts) all sit past it; of 16 sampled, 2 were read (one merge into a
single block of 9 or 781 points, then a burst C(m, k), then closing) and 14 ran out of memory by round 5–8.

## What I found today (exploration, disclosed)

1. **Paired starts.** Take 2n live points in n partner pairs, blocks = all non-partner pairs, open counts 2^(n−1). (The candidate
   graph is the literature's cocktail-party graph O_n.) My proof sketch: the groups of round 1 are the 2^n transversals (one point
   of each pair), all valid, covering every candidate pair, each point in exactly 2^(n−1) of them, so no offshoots. Inductively,
   the state at round t ≥ 1 is: N_t points with a partner involution (complement), candidate graph all non-partner pairs, maximal
   blocks = N_{t−1} distinct transversals closed under complement (B_v = junctions containing v; B_v̄ is its complement). Groups
   at t+1 = transversals that are not blocks (a block holding a transversal equals it); every candidate pair {u,v} lies in
   2^(m−2) transversals but in only |u ∩ v| ≤ m_{t−1} − 1 blocks, so none is uncovered; demand d = 2^(m_t − 1) − m_{t−1} with
   p = m_{t−1} ≥ 3, so open = d, no offshoots. Hence N_0 = 2n, N_1 = 2^n, N_{t+1} = 2^(N_t/2) − N_{t−1}. For n = 3: 6, 8, 10, 24,
   4086, 2^2043 − 24, ... The program's engine and my compact engine both give rounds 1–3 exactly ((3 parents, open 5) × 8;
   (4, 12) × 10; (5, 2043) × 24), and the open count 2043 confirms round 4 = 24·2043/12 = 4086. n = 2 (a ring of four) is constant.
   This mirrors Neumann-Lara's K(O_n) = O_{2^(n−1)} for the clique-graph operator; here the star cliques are removed, giving the
   "− N_{t−1}".
2. **No cluster reading can follow it.** Orbits of k-point connected sets in a cover of a finite complex with maximum degree Δ
   number at most |base|·(eΔ)^k. A reading with round-t junctions = orbits of (t + c)-point clusters therefore grows at most
   exponentially in t, while the paired start's counts are an iterated exponential. So past the wall the tree-of-blocks reading
   is not just unproved: no reading of that kind exists, on any finite complex.
3. **The smallest unread start (start-03).** Six knots; counts 6, 10, 16, 27, 40, 61, 110, 386, and my compact engine reaches round
   8's groups: 28,064, the largest of 109 parents (the program's engine ran out of 6 GB in step 8). All its junctions live over
   only 17 points (round-0 knots plus offshoots); one 11-point support carries 126 distinct round-7 junctions. No twins (no two
   points with the same maximal blocks). Its candidate graphs are far from paired: in round 7 (386 points, density 0.36) each
   point misses 117 to 148 others. The flag complex of its round-0 candidate graph is acyclic; 16 of the 21 explosive starts of an
   earlier sample have acyclic flag complexes too, 5 have one 2-dimensional hollow.
4. Literature found: K(O_n) = O_{2^(n−1)} (Neumann-Lara); deciding clique-convergence of finite graphs is open; it is undecidable for
   automatic graphs (Cedillo and Pizaña, 2021).

## Questions

1. Is the paired-start proof sketch right? Any gap (base case, coverage of pairs, distinctness of blocks, demand, the implied
   rule)? Is "never closes" fully justified?
2. Is the cluster-reading obstruction (item 2) sound as stated, or does it need a narrower statement (for example about how
   junction size relates to the round)?
3. Is our operator (keep the non-star maximal cliques and the leftover candidate pairs; drop the cliques held by a block) a known
   graph operator? Is there a known name or result I should cite beyond Neumann-Lara?
4. For start-03, which next step most likely yields a real reading: (a) a retraction lemma (Neumann-Lara's "a retract of G gives
   a retract of K(G)") adapted to this operator, so that a stage retracting onto a paired structure provably grows as an iterated
   exponential; (b) a sampling estimate of the next round's count (Knuth-style random descent through the clique search); (c)
   something else? Which would you freeze, and with what falsifiable predictions?
5. Words. The program avoids words from two- or three-dimensional space for its own objects (so not "octahedron" or
   "cross-polytope" except once as the literature's name). Suggest one plain word for a start or stage whose points come in
   partner pairs, each a candidate with all but its partner; and one for the growth speed N_{t+1} ≈ 2^(N_t/2) ("tower" is
   already used in the program for "towers of patterns").
6. My draft predictions to freeze, please tighten or replace:
   - P1: the compact engine equals the program's engine (per-round multiset of (parents, open count)) on every touch-census
     arrangement to round 6 and on 1,000 random starts within seven places;
   - P2: paired starts n = 3, 4, 5 match the recurrence on every round the program's engine reaches, and the open counts match
     2^(m_t − 1) − m_{t−1};
   - P3: start-03's round 8 count (groups plus offshoots) is computed by the compact engine within 8 GB and 15 minutes;
   - P4 (risky): no stage of start-03 through round 8 is paired, and no maximal block holds all live points (no merge yet).
