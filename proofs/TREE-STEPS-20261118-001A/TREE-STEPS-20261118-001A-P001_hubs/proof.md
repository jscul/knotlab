# Hubs and the irreducible distance: what is proved

Ticket `TREE-STEPS-20261118-001A`, 18 November 2026. Checked by ticket B's gates and frozen run
(`experiments/TREE-STEPS-20261118-001B/TREE-STEPS-20261118-001B-E001_trees/`). Referee pending. H1 and the counterexample are the
advisor's (claude-fable-5-2), checked here; K1 to K4 are the thread's.

Notation as in `CUMULANT-DIST-20261118-001A`: spins s = (−1)^value under the uniform weighting; κ_S the joint cumulant;
δ(x, y) = min over S ∋ x, y with κ_S ≠ 0 of (|S| − 2) + τ(κ_S), τ(k) = max(0, −log₃ |k|). On a knot tree the uniform weighting is
the tree process rooted at any distinction: each knot draws its two other distinctions given the first, independently of the rest
(not-all-equal: s_b = s_a r_b, s_c = s_a r_c, (r_b, r_c) uniform on the three allowed pairs; parity: s_b = s_a ε, s_c = ε with ε a
fair coin); every subtree's number of completions is the same for both values of its root, by induction.

## H1. The hub identity (advisor)

If σ is a uniform ±1 and u₁, …, u_n are independent of σ and of each other, with means μ_i, then
κ(σu₁, …, σu_n) = κ_n(σ) ∏ μ_i: by independence the moment of any block is E[σ^{|B|}] ∏_{i∈B} μ_i, the moment of the variables
μ_iσ, and κ(μ₁σ, …, μ_nσ) = ∏ μ_i κ_n(σ). For a not-all-equal knot hung on x with both other distinctions b, c in S, condition on
σ = s_x: the conditional covariance of s_b and s_c is constant, so blocks holding both drop out of Brillinger's law of total
cumulance, and b, c act as two independent copies with mean −1/3 each. A parity knot hung on x has E[s_b s_c | σ] = σ, one exact
copy for two distinctions. ∎ (Gate: the identity on four small hubs.)

## H2. The threshold

The cumulants of a fair coin are |κ_{2j}(σ)| = 1, 2, 16, 272, 7936, … (the tangent numbers; κ_odd = 0). Take x with a path of
k not-all-equal knots to y, and 2j copies of σ hung on x as in H1, each costing one distinction and a factor 1/3 (not-all-equal), or
two distinctions per copy (parity). Then κ_S = κ_{2j+2}(σ)·(−1/3)^{2j+k} and

δ(x, y) ≤ 2j + max(0, 2j + k − log₃ |κ_{2j+2}(σ)|),

below k exactly when log₃ |κ_{2j+2}(σ)| > 4j. Computed exactly (gate), the least such 2j is 32: log₃ |κ₃₄(σ)| = 64.0752. So a hub
shortcuts only with at least 32 copies: sixteen not-all-equal knots on one distinction with both other distinctions in S, or
thirty-two parity knots, and then only for k ≥ 33 − (the hub's slack). A hub on a distinction lying in at most fifteen knots
cannot shortcut this way. ∎ (Nested hubs, copies feeding copies through a shared knot, are not covered by H2.)

## The irreducible-set distance

Call S ∋ x, y **irreducible** when κ_S ≠ 0 and κ_T = 0 for every T with {x, y} ⊆ T ⊊ S, and let

δ_K(x, y) = min over irreducible S of (|S| − 2) + τ(κ_S).

It is the cumulant form of the knot test's K2: the set is bound as a whole, and no smaller set holding the pair is. Like δ it is read
from the states alone and is invariant under renaming and under switching values. Always δ_K ≥ δ.

## K1. A correlated pair is its own irreducible set

If C(x, y) ≠ 0 then κ_{xy} = C ≠ 0, so every S ⊋ {x, y} contains the binding set {x, y} and is not irreducible. So
δ_K(x, y) = τ(C(x, y)). ∎ So δ_K is the count's τ on every not-all-equal base where pairs correlate (the weave, the chain grid,
split grids alike), with no four-set repair (`CUMULANT-DIST-20261118-001`'s weave patch: δ_K = τ there).

## K2. Parity bases

On a base cut out by parity knots, κ_S ≠ 0 forces the dual matroid on S to be connected (`CUMULANT-DIST-20261118-001A`, D1), so x and
y lie on a circuit C ⊆ S, with κ_C = ±1. If S ≠ C, then C is a smaller binding set holding the pair and S is not irreducible. A
circuit is irreducible: its proper subsets carry no dual codeword, so their spins are independent and their cumulants vanish. So
the irreducible sets through x and y are exactly the circuits through them, and δ_K = δ = bond distance − 1. ∎

## K3. δ_K ignores hubs

Every set S of H2 contains {x, y}, which binds (C = (−1/3)^k ≠ 0 on the not-all-equal path). So S is not irreducible. More
generally, on a mixed path the set T₀ = {x, y} ∪ {third distinction of each parity knot on the path} binds
(κ_{T₀} = (−1/3)^a, `CUMULANT-DIST-20261118-001A`, D3), so no set strictly containing T₀ is irreducible. ∎

## K4. δ_K = steps apart on

- **not-all-equal trees**: K1 and τ = steps apart (`DISTANCE-ORDER-20261117-001`);
- **parity trees**: K2 and D2;
- **mixed trees whose path from x to y has no parity knot**: then C(x, y) = (−1/3)^k ≠ 0 (the path's relative factors are
  independent with mean −1/3), and K1 applies. ∎

**Open: mixed trees whose path has a parity knot** (then C(x, y) = 0). Sketch, not a proof: by the parity-branch lemma (a parity knot
in the smallest subtree holding S with a branch missing S splits S into independent parts, so κ_S = 0), every parity knot met by an
irreducible S has all three branches occupied; one expects the irreducible S to be the minimal such covers, with κ_S = ±(−1/3)^ν, ν
the not-all-equal knots touched oddly, and |S| − 2 at least the number of parity knots in its subtree, giving δ_K ≥ k. The step not
yet proved is that a minimal cover has no proper subset with nonzero moment (so that κ_S = m_S) and the accounting of not-all-equal
knots touched evenly. Computed in ticket B.
