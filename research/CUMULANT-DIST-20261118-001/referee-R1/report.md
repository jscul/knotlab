# Referee report CUMULANT-DIST-R1 (fresh code, no Codex)

**Verdict: Block on one reading, confirmed independently. "δ = steps apart on every knot tree" is false. The rest is confirmed
with fixes.**
- **The Block.** The owner logged it in d6ef076cb (proof D6). The referee checked the mechanism with its own code:
  - **The identity holds on actual bases.** κ_S = κ_(N+2)(coin)·(−1/3)^(N+k) at (N, k) = (2, 1), (4, 1), (2, 2), (4, 2) and (6, 1).
  - **The cumulants of a fair coin** are the tangent numbers with signs: 1, −2, 16, −272, 7,936, −353,792, ….
  - **32 hung knots is the first hub that wins.** log₃|κ_(N+2)| − 2N is −1.44 at N = 30, then +0.075 at N = 32 and +1.70 at N = 34.
- **Everything else reproduces with fresh code.** That includes:
  - the parity theorem;
  - every knot tree in the study's range, and every seven-knot tree under one law, one size past;
  - the split line;
  - the weave patch's three shortcut pairs.
- **The owner's flags.**
  - **D1's connectivity step:** the statement is true, but the hypothesis needs a one-line fix (§1).
  - **The search bound steps + 2:** sound (§2).
  - **The weave patch's edge effects:** confirmed. On a patch of radius 3 the three pairs read τ, and 22 others, all within one step of the new edge, read below it (§3).
  - **Novelty:** the reductions are classical, and the functional was not found in a targeted search (§5).
  - **The headline "one distance reads both":** not fair as a general statement. A scoped version is in §4.

## What holds (recomputed; `referee_cumulant.py`)

The referee wrote its own states, moments and cumulants. The cumulants use the partition formula, not the study's recursion, and
the search is its own.

| Part | Referee's result | Study |
| --- | --- | --- |
| Parity bases, 300 random (own seed), 6 to 9 distinctions | 0 of 7,619 pairs differ from least circuit − 2; triangle inequality holds on all 33,636 triples | 0 of 7,450 |
| Knot trees, every shape to five knots × every parity/not-all-equal assignment, six knots pure (shapes 1, 1, 2, 4, 8, 19) | 380 bases, 19,730 pairs, 0 differ from steps apart | the same |
| One size past: every seven-knot tree (48 shapes), pure parity and pure not-all-equal | 96 bases, 10,080 pairs, 0 differ | — |
| Split line of eight | rotation maps the states; δ from one end 0.26, 0.63, 1.26, 3.26, 1.26, 0.63, 0.26 | the same |
| Weave patch, radius 2 (5,112 states) | 3 pairs with δ < τ: (−1,1)–(1,−1) 4.88 → 3.10; (0,0)–(0,2) and (0,0)–(2,0) 3.99 → 3.18 | the same |
| Chain grid 4 × 4, loose distinctions kept and allowed in the sets (40 distinctions, sets to four) | 0 of 120 pairs below τ; largest τ 3.17 < 4, so larger sets cannot matter | δ = τ, sets of grid distinctions only |

- **D0 (invariance, the clamp, one knot) is right.** A betweenness knot has |C| = 1/3 on all three pairs.
- **D3 extends from chains to every tree.** The path's η's are independent of the branches, so δ ≤ steps apart on every mixed knot tree. That upper bound is what D6 shows is not the truth.
- **D4 is right**, on a complement-closed tree, given the separation.
- **D5 is right.** The switching rotation carries the split line's 2m states to themselves.
- **The chain grid holds without its restriction.** The study searched only sets of grid distinctions. With the loose distinctions allowed into the sets, the result is unchanged.

## 1. D1's connectivity step (the owner's flag; Not a block)

- **The statement is true.** If κ_S ≠ 0, then the code's matroid restricted to S is connected.
- **The argument proves something weaker.** Its hypothesis is "A, B with no dual codeword meeting both".
  - The contrapositive then gives only "some dual codeword meets both parts".
  - A dual codeword inside S that meets A and B can be a disjoint union of circuits, each on one side. Then the restriction is not
    connected.
  - Codewords reaching outside S are irrelevant.
- **The fix.** Make the hypothesis "no circuit inside S meets both A and B", that is, A | B is a separator of the restriction.
  - Then every dual codeword inside S splits along A | B. The code's projection to S is the product of its projections to A and
    to B, so the spins of A and of B are independent and κ_S = 0.
  - That is exactly the needed contrapositive.
  - The rest of D1 is right:
    - a circuit's proper subsets have zero moment, so κ = ±1;
    - a circuit is a parity knot;
    - so δ = bond distance − 1.

## 2. The trees' search bound, steps + 2 (the owner's flag; sound)

- **Why the bound is safe.** D3's set has value steps apart on every tree (§ What holds). A set of size s has value at least
  s − 2, so it can lower δ below steps apart only when s ≤ steps + 1.
- **What was searched.** The study searched every set of distinctions holding x and y up to steps + 2. The referee searched to
  steps + 1, falling back to steps + 2 only to confirm the attained value.
- **So within the computed range, the result is exact.**
- **The bound would also catch the hub.** That shortcut uses |S| = N + 2 = 34 with k ≥ 33, so |S| ≤ k + 1. The computed trees miss
  it only because they are small: five to seven knots, against 65.

## 3. The weave patch's edge effects (the owner's flag)

- **The study's three shortcut pairs are small-patch effects.** The referee recomputed the radius-3 patch (37 distinctions,
  51 knots, 4,123,166 states; `referee_cumulant_weave.json`).
  - **The three pairs read τ there:** (−1,1)–(1,−1) has C −0.087, (0,0)–(0,2) and (0,0)–(2,0) have −0.110. That gives
    δ = τ = 2.23 and 2.01, with no four-set below.
  - **The endless value** along a row at distance 2 is C = −0.193.
- **The effect moves outward with the edge.** `referee_cumulant_weave3.json` searched every set of four for each of the 246 pairs
  with τ > 2. Sets of four are the only ones that can shortcut them, and the search is exact below δ = 4.
  - 22 pairs read below τ.
  - Every one has a distinction within one step of the edge. Their radii are (1, 3) for 6, (2, 2) for 5, (2, 3) for 6 and (3, 3)
    for 5.
  - Their correlations nearly cancel, with τ from 4.1 to 7.8.
- **Why this is a boundary effect.** On the endless weave, C ≈ a r^(−1/2) cos(Q·r) never cancels. The study's "below τ only where a
  pair's correlation nearly cancels" is right, and the near-cancellation comes from the boundary.
- **A wording point.** "The weave's three shortcut pairs sit at the patch edge" is loose. (−1,1)–(1,−1) joins two sites one step
  from the centre. On a patch of radius 2 every site is within one step of the edge.

## 4. The Block, and the scoped statement (the coordinator's request)

- **The mechanism is right.**
  - If σ is a fair coin and u₁, …, u_n are independent of σ and of each other, then every block's moment is E[σ^|B|]∏μ_i. So
    κ(σu₁, …, σu_n) = κ_n(σ)∏μ_i.
  - In a not-all-equal tree rooted at x, a child b of a knot hung on x has s_b = s_x·r with E r = −1/3, independent of everything
    else, and s_y = s_x·R with E R = (−1/3)^k.
  - The coin's cumulants grow factorially, so with N = 32 hung knots and a path of k ≥ 33:
    δ ≤ 32 + (32 + k − 64.0752) = k − 0.075.
  - Letting the hub grow with k gives δ = O(k / log k).
  - Parity hubs do not help, because a parity child's u has mean 0.
- **The correct scoped statement.**
  - **Proved:** δ = bond distance − 1 on every parity base, and δ = steps apart on every parity knot tree. δ ≤ steps apart on every
    knot tree under any mixture (D3, on trees).
  - **Computed:** δ = steps apart on every knot tree to five knots under every mixture and to six under one law (the study), and
    to seven under one law (the referee). Also τ on a 4 × 4 chain-grid patch, loose distinctions included.
  - **False in general:** on not-all-equal trees with a hub, from 32 knots hung on one distinction (65 knots in all).
  - **Open:** where between seven and 65 knots, and under which bound on knots per distinction, steps apart stops. Nested or spread
    hubs are not covered by the single-hub threshold. TREE-STEPS, the next review, takes this up.
- **Is "one distance reads both" fair?** No, as a general headline. It is fair as follows: "one distance is bond distance − 1 on
  parity bases (proved), steps apart on small knot trees under either law and their mixtures (computed), and τ on a chain-grid
  patch. Large not-all-equal hubs shorten it, and it ignores the value convention."
  - On not-all-equal bases it agrees with τ only where pairs dominate. Patch edges and large hubs undercut it.
  - The four predictions that held are the B200 content. The five misses are as the note describes: one coding slip (P4) and four
    informative.

## 5. Novelty and known results (the owner's flag; John's folklore rule)

- **Known, and correctly cited:**
  - **Connected information** (Schneidman, Still, Berry and Bialek, Phys. Rev. Lett. 91, 238701, 2003) measures the entropy a set
    loses beyond its (k − 1)-marginals. Its canonical example is parity, all of whose information sits at the top order.
  - **−log|C|** is the classical additive tree metric (Cavender–Farris; the information distance of latent-tree learning, Choi,
    Tan, Anandkumar and Willsky). δ = τ = steps apart on not-all-equal trees is that metric, which DISTANCE-ORDER already had.
  - **Matroid connectivity** (Tutte) carries the parity theorem.
  - **The coin's cumulants are the tangent numbers** (log cosh). That is classical, and it is the mechanism of the Block. The note
    should cite it with D6.
- **Searched.** Two targeted searches found no distance of this form: the least over sets of (|S| − 2) − log|κ_S|, clamped. The
  nearest relatives are joint-cumulant interaction measures (Lancaster's and Streitberg's, over set partitions) and connected
  information.
- **What the program adds:** one functional that reproduces bond distance on parity bases and τ on small not-all-equal trees, and
  the switching reading of split lines. The note's "known results" paragraph is fair. It should add the tangent-number growth and
  the hub, now that D6 rests on them.

## 6. Smaller points (Not a block)

- **The triangle inequality.** It is not shown in general. It held on every triple of the referee's 300 parity bases.
- **P4.** The coding slip is real: the pairs on each side were put in the exponent. D4 as stated holds, by hand, and the study's
  post hoc check agrees.
- **P8.** The advisor's cap was wrong. The antipode is 2 + log₃ 4, as the study found and the referee recomputed.

## Fixes for the thread (listed for the owner, not folded in)

1. **The Block is confirmed** (owner's correction d6ef076cb). Use the scoped statement of §4 wherever "steps apart on every knot
   tree" or "one distance reads both" appears. **Block (already logged).**
2. **The headline.** Read "one distance reads both" with the scope of §4. On not-all-equal bases it is τ only where pairs
   dominate, and patch edges and hubs undercut it. **Narrowing.**
3. **D1's connectivity step.** The hypothesis should be "no circuit inside S meets both parts". **Not a block.**
4. **The weave patch.** Add the radius-3 result: the three pairs read τ, and 22 near-edge pairs shortcut instead. Reword "sit at
   the patch edge". **Not a block.**
5. **The chain grid.** The result holds with the loose distinctions allowed into the sets. Say so, or keep the restriction
   stated. **Not a block.**
6. **Known results.** Cite the tangent numbers (log cosh) beside D6. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, proofs D0 to D6, and `cumlib.py` and `run.py`;
  - checked D0 to D6 by hand;
  - wrote `referee_cumulant.py` (states, partition-formula cumulants, the search, every part) and `referee_hub.py` (the coin's
    cumulants and the hub identity on actual bases).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
- **The literature:** two web searches for the novelty check.

## Files

- **`referee_cumulant.py`.**
- **`referee_cumulant_linear.json`, `_trees.json`, `_trees7.json`, `_split.json` and `_chain.json`.**
- **`referee_cumulant_weave.json`:** radius 2 and six pairs at radius 3.
- **`referee_cumulant_weave3.json`:** every radius-3 pair with τ > 2.
- **`referee_hub.py` and `referee_hub.txt`.**

Reproduce, from `research/CUMULANT-DIST-20261118-001/referee-R1/`:

```sh
for p in linear trees trees7 weave chain split; do ../../../.venv/bin/python -B referee_cumulant.py $p > referee_cumulant_$p.json; done
for i in 0 1 2 3 4 5; do ../../../.venv/bin/python -B referee_cumulant.py weave3 $i 6 > w3_$i.json; done
../../../.venv/bin/python -B referee_cumulant.py weave3_merge w3_*.json > referee_cumulant_weave3.json
../../../.venv/bin/python -B referee_hub.py > referee_hub.txt
```
