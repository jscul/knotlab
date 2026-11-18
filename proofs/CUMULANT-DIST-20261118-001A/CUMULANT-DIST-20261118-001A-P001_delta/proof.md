# The cumulant distance: what is proved

Ticket `CUMULANT-DIST-20261118-001A`, 18 November 2026. Checked by ticket B's gates and frozen run
(`experiments/CUMULANT-DIST-20261118-001B/CUMULANT-DIST-20261118-001B-E001_delta/`). Referee pending. D1 to D5 were proposed by the
advisor (claude-fable-5-2) before the freeze and checked here.

Notation. A base is a set of allowed states of n distinctions, weighted uniformly; spins s = (−1)^value. For a set S, m_S =
E[∏_{v∈S} s_v] and κ_S is the joint cumulant, defined by m_S = Σ over partitions of S of ∏ κ_B. The cumulant distance is

δ(x, y) = min over S ∋ x, y with κ_S ≠ 0 of (|S| − 2) + τ(κ_S),  τ(k) = max(0, −log₃ |k|).

## D0. Basic properties

- **Invariance.** Renaming distinctions permutes the sets. Flipping one distinction's values multiplies every moment, and so
  every cumulant, of a set containing it by −1. So δ is invariant under renaming and under switching values. ∎
- **Complement-closed bases** (flipping every value keeps the states): odd moments vanish, so odd cumulants vanish and
  κ_{xy} = C(x, y), the pair correlation. ∎
- **The clamp.** |κ_S| can exceed 1: on {0000, 1111}, κ₄ = 1 − 3 = −2. With the clamp δ ≥ |S| − 2 ≥ 0, and a search may stop once
  |S| − 2 reaches the best value found. ∎
- **One knot, one step.** A parity knot has κ_{abc} = ±1 and every pair at 0, so δ = 1 on its pairs. A not-all-equal (or
  betweenness) knot has C = −1/3 (+1/3) on its pairs, so δ = 1. ∎

## D1. Parity bases: δ is bond distance minus one (advisor)

On a base cut out by parity knots (a linear code), m_S = ±1 when S is a dual codeword (a sum of checks) and 0 otherwise.
- If S splits into two parts A, B with no dual codeword meeting both, the spins of A and of B are independent, so κ_S = 0. So
  κ_S ≠ 0 forces the dual matroid restricted to S to be connected, and in a connected matroid every two elements lie on a common
  circuit inside S. So |S| ≥ (least circuit through x and y).
- A circuit (an inclusion-minimal dual codeword) has no proper subset with a nonzero moment, so its cumulant is its moment, ±1.
So δ(x, y) = (least circuit through x and y) − 2, or ∞ when none. A circuit is exactly a set on which the states form a parity knot
(constrained as a whole, every proper subset free), so this is bond distance minus one. ∎ (Gate: circuits equal knot sets on 40
random bases; P1: 7,450 pairs of 300 random bases.)

## D2. Parity knot trees: δ = steps apart (advisor)

On a tree of parity knots (each knot shares at most one distinction with the rest of a path), let x and y be k knots apart. The sum
of the k path knots' checks has support x, y and the third distinction of each path knot, k + 2 in all; a proper sub-sum leaves a
shared distinction at its boundary, outside the support, so the support is a circuit. Every codeword through x and y uses every
path knot, so no smaller circuit exists. By D1, δ = k. ∎

## D3. Mixed chains: the exact identity and the upper bound (advisor)

On a chain of knots, each parity or not-all-equal, with x and y at its ends, let η_j be the product of the two shared spins of
knot j. The η_j are independent of one another and of s_x; for a parity knot η_j is the spin of its third distinction p_j, for a
not-all-equal knot E[η_j] = −1/3. For S = {x, y} ∪ {p_j : knot j parity}, the only block with a nonzero moment is S itself, so
κ_S = m_S = (−1/3)^a, a the number of not-all-equal knots. So δ ≤ (b) + a = k, b the number of parity knots. ∎ (P3: all 62 chains
to five knots, exact.) The matching lower bound (δ = k) is computed (P2), not proved, for mixed and not-all-equal trees beyond the
four-sets of D4.

## D4. Not-all-equal trees: no four-set shortcut (advisor)

On a complement-closed tree, if one distinction w separates {x, u} from {y, v} (on every path), then even functions of the two
sides are independent given nothing, so m_{xuyv} = m_{xu} m_{yv}, and κ₄ = −m_{xy} m_{uv} − m_{xv} m_{uy} = −2(−1/3)^(d(x,y) + d(u,v))
(the two cross sums are equal through w). So 2 + τ(κ₄) = 2 − log₃ 2 + d(x, y) + d(u, v) > d(x, y), and a four-set never beats
the pair. ∎ (Post hoc check, all 491 separated four-sets on chains of three to five knots; the frozen P4 code used the pairs on each
side instead of the cross pairs and failed; see the note.)

## D5. Switching obstruction (advisor)

The split line of m points has states the cuts {0, …, c} and complements and the two all-equal states. The map i → i + 1 for
i < m − 1, with the last point sent to 0 and its values flipped, carries the states to themselves. So, up to switching values, the
line is a ring of m: its two ends are as near as any two neighbours, and every switching-invariant reading (|C|, every |κ_S|, δ)
folds its L1. ∎ (P8: the map and the invariance of every |κ_S| with |S| ≤ 4 hold on m = 8; δ reads the ring of eight: 0.26, 0.63,
1.26 at ring distance 1, 2, 3 and 3.26 at the antipode.)

## D6. The general tree claim is false (added on 18 November 2026; the advisor's counterexample, checked)

- **Lemma.** If σ is a uniform ±1 and u₁, …, u_n are independent of σ and of each other, with means μ_i, then
  κ(σu₁, …, σu_n) = κ_n(σ) ∏ μ_i. Proof: by independence the moment of a block B is E[σ^{|B|}] ∏_{i∈B} μ_i, which are the
  moments of the variables μ_iσ; cumulants are functions of moments, and κ(μ₁σ, …, μ_nσ) = ∏ μ_i κ_n(σ) by multilinearity. ∎
- **Counterexample.** In the tree process rooted at x (σ = s_x), take a path of k not-all-equal knots from x to y and N further
  not-all-equal knots on x, with b_i a child of hung knot i. Then s_{b_i} = σ r_i and s_y = σR with r_i, R independent of σ and of
  each other, of means −1/3 and (−1/3)^k. By the lemma, κ_{{x, y, b₁, …, b_N}} = κ_{N+2}(σ)(−1/3)^{N+k}. Since
  |κ_{2j}(σ)| = 2^{2j}(2^{2j} − 1)|B_{2j}|/(2j) (the tangent numbers; B Bernoulli), log₃ |κ₃₄(σ)| = 64.0752 > 64, so for N = 32 and
  k ≥ 33, δ(x, y) ≤ 32 + (32 + k − 64.0752) = k − 0.0752 < k. ∎ (Checked: the identity on the bases at (N, k) = (2, 1), (4, 1),
  (2, 2); the tangent numbers exactly.)
- So D3's upper bound is the truth only on trees without such hubs; the lower bound holds on every parity tree (D2) and is computed
  on every tree to five knots.

## Not proved here

δ = steps apart on not-all-equal and mixed trees without large hubs (computed to five knots mixed and six pure; false in general by D6); δ = τ on the chain grid
(computed on a 4 × 4 patch; the bound route through Aizenman's tree bound is a sketch, with the bubble 2.99 ≤ 4.5); whether a
switching-invariant reading recovers a split grid's L1 in two orders (no switching equivalence takes a corner's neighbour to the
far corner on 3 × 3, 3 × 4, 4 × 4, so the full structure distinguishes them, while |C| and the triangle products do not).
