# Advisor answer 1 (Fable 5.2, `claude -p --model claude-fable-5-2 --tools ""`)

**Advisor reply 1 (WALL-READ, before the freeze)**

Nothing here was run; all checks are by hand.

**Q1. Paired-start sketch: correct, with four gaps to close in the write-up.**
I re-derived it and it holds. Write m_t = N_t/2.

- **Base.** Blocks have size 2, so every clique of three or more is valid. The maximal cliques are the 2^n transversals (n ≥ 3), every candidate pair lies in one, and each point lies in 2^(n−1) = f.
- **Step.** B_v contains exactly one of each complementary pair of junctions, so it is a transversal of the new pairing, and B_v̄ is its complement. Two junctions are candidates iff they share a parent iff they are not complementary.
- **Numbers.** d = 2^(m_t − 1) − m_{t−1} matches your data: 8−3 = 5, 16−4 = 12, 2048−5 = 2043. The recurrence gives 10, 24, 4086.

Gaps:

- **(a) Distinctness of blocks.** B_u ≠ B_v needs a non-block transversal containing u and not v. For v ≠ ū there are 2^(m_t − 2) transversals through u and v̄, and at most m_{t−1} − 1 of them are blocks. This is the same inequality as pair coverage; say so. All blocks have size m_t, so distinct implies maximal.
- **(b) Monotonicity.** The induction needs 2^(m_t − 2) > m_{t−1} − 1 at every round. Carry "m_t > m_{t−1} and m_t ≥ 4" as the hypothesis. Then m_{t+1} ≥ 2^(m_t − 1) − m_t + 1 > m_t, since 2^(m−1) > 2m − 1 for m ≥ 4. Note that 2^(m−1) ≥ 2m + 1 fails at m = 4, so the naive version of this step breaks at n = 3, round 2.
- **(c) Round 1 separately.** Parent count is n, not m_{t−1}, and the blocks number 2n.
- **(d) "Never closes."** No group can hold all points, because partners are never candidates. But use = f everywhere, so the set of loose distinctions is empty. Check the closing clause's exact wording so that "one junction holding every loose distinction" is not vacuously true. The engine evidently does not close in rounds 1–3, but the proof should cite the clause.

Stalling is impossible after round 1 for any start, since open ≥ d by the rule. Also state whether a paired start with n ≥ 4 is realisable as a program start or only as an abstract state.

**Q2. The obstruction is sound but needs narrowing.**

- **Cover.** "Orbits ≤ |base|·(eΔ)^k" needs the deck group to act transitively on fibres (a regular cover), or else count clusters up to projection. For an irregular cover, deck orbits of vertices can be infinite.
- **Cluster size.** State it as: if round-t junctions inject, with bounded multiplicity or finitely many labels, into orbits of clusters of size s(t), then log N_t = O(s(t)). The paired start therefore forces s(t) ≥ c·N_{t−1}, with clusters as large as the previous stage. That rules out every linear or polynomial s(t), not only t + c.
- **Scope.** This is proved for paired starts and for any start with super-exponential counts. It is not proved "past the wall" in general. Start-03's counts through round 8 do not yet establish super-exponential growth.

Separately, 126 junctions on one 11-point support, over only 17 points, already shows that junctions are not determined by their support. That is independent evidence against set-valued readings and worth recording.

**Q3. Is the operator known?** I know no name for exactly this operator. Verify each of the following before citing; they are from memory.

- **Hypergraph language.** A valid set is a witness that the block hypergraph is not conformal (Berge: conformal means every clique of the 2-section lies in an edge). The new blocks are the stars, i.e. the dual hypergraph of the group family. So the rule is "dual of the non-conformal maximal cliques of the 2-section, plus leftover pairs".
- **Clique-graph language.** The cliques of K(G) are stars and non-stars. Your rule keeps the non-star ("non-Helly") ones. On a conformal (clique-Helly-like) stage it produces only pairs.
- **Sources.** Neumann-Lara 1978, "On clique-divergent graphs" (retraction theorem, O_n). Escalante 1973. Prisner, *Graph Dynamics* (1995). Szwarcfiter's survey on clique graphs (2003). Larrión, Neumann-Lara and Pizaña on expansive graphs and on clique divergence with polynomial growth. That last is relevant because divergence need not be iterated-exponential.

**Q4. Freeze (c), a witness-based lower bound, ahead of (a) and (b).**

Define the partnered number k_t as the largest k such that some 2k points of stage t have non-candidate graph exactly a perfect matching (an induced O_k).

- **Lemma (one line, rigorous).** Distinct transversals of these 2k points extend to distinct maximal cliques, since two transversals between them contain a partner pair. Each block is a clique and so holds at most one transversal. Hence groups at t+1 ≥ 2^(k_t) − (number of maximal blocks at t).
- **Cost.** A lower bound needs only a witness. Finding one is an induced-matching search in the complement, which is feasible at 386 points with ILP or greedy plus local search.
- **Forced check.** Round 8 has 28,064 groups, so 2^(k_7) ≤ 28,064 + B_7, which gives k_7 ≤ 14 or so. A larger witness means a bug.
- **Predictions to fix before looking.** k_t is nondecreasing over rounds 4–8. Set a threshold for k_8 that implies a round-9 count beyond the engine's reach.

Option (a) is the right theorem to aim at afterwards, with two cautions. The retraction must be of the block hypergraph: blocks map into blocks, and valid transversals stay valid. And the junctions from T and T̄ may share a parent outside the witness, so the pairing is not inherited automatically. That is exactly what a retraction supplies and an induced O_k does not. Offshoots also need handling.

Option (b) is unbiased but heavy-tailed on clique trees. Use it only as a secondary estimate, reported with spread, never as a count.

**Q5. Words.**

- **"Partnered"** (partnered start, partnered stage): points come in partners, and each is a candidate with all but its partner. Give "cocktail-party graph" once as the literature's name.
- **"Runaway growth"**: each count is about 2 to the power of half the previous one. Give "iterated exponential" once as the literature's name.

Check both against the glossary for collisions.

**Q6. Predictions.**

- **P1.** Compare the stall and closing verdicts and the down-closed blocks as well as the (parents, open) multisets. Include the two read explosive starts (merges of 9 and 781 points), since that is where a compact engine is most at risk. Fix the random generator and seed in the contract.
- **P2.** n = 3 through round 3 is already seen; list it as disclosed, not predicted. The fresh numbers are:
  - n = 4: counts 8, 16, 248. Round-1 junctions are (4 parents, open 124) × 16. Round-2 junctions have 8 parents, and their open count 2^123 − 8 is not computable by enumeration.
  - n = 5: counts 10, 32, 65,526. Round-1 junctions are (5, 32,763) × 32. Round-2 junctions have 16 parents.
  - Negative controls: open counts 2^(n−1) − 1 stall at round 1; 2^(n−1) + 1 gives exactly 2n offshoots.
- **P3.** A resource limit is not a scientific prediction. Replace it with the double count: the sum of round-7 open counts equals the sum of round-8 parent counts, offshoots included. Also predict that the round-8 groups number 28,064 with largest parent count 109, reproduced by an independent enumeration order.
- **P4.** "No stage is paired" is not risky at the density you report. Replace it with the k_t predictions above, and keep "no maximal block holds all live points through round 8".

**One inconsistency in item 3.** Density 0.36 and "each point misses 117 to 148 of 385" disagree. Those misses give a candidate density of about 0.66, so 0.36 looks like the non-candidate density. Fix this before the freeze.
