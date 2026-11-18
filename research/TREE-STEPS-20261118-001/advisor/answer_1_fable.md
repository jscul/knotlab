<!-- modelUsage: claude-fable-5-2 -->

**Verdict: the lower bound δ(x, y) ≥ k is false in general.** Your worry about tangent numbers is exactly the mechanism. The explicit counterexample below is a pure-NAE tree with 48 knots, k = 33 and |S| = 34, far beyond your exhaustive range. This is from analysis only; nothing was run.

## Check of (i)–(iii)

- **(i)** Correct. Every spin is s_root^e times a monomial in independent innovations, with e ∈ {0,1}.
- **(ii)** Correct. Rooting at x, a subset T ⊆ S has nonzero moment only if s_x and every parity ε_j appear to an even power, which forces T = ∅ or T = S. So κ_S = m_S = (−1/3)^a.
- **(iii)** Correct (Brillinger's law of total cumulance). If w ∈ S, its own block {w} has d = 1.
- **The "i.e." restatement** is stronger than δ ≥ k. Because of the max(0, ·), δ ≥ k only requires |κ_S| ≤ 3^{|S|−2−k} for sets with |S| − 2 < k. That weaker statement is the one that fails.

## 1. Counterexample

**Lemma.** Let σ be uniform ±1, and u_1, …, u_n mutually independent and independent of σ, with means μ_i. Then κ(σu_1, …, σu_n) = κ_n(σ) · ∏ μ_i.

*Proof.* The joint cumulant depends only on the moments m_B for B ⊆ {1..n}. By independence, m_B = E[σ^{|B|}] ∏_{i∈B} μ_i. These are exactly the moments of the variables Y_i = μ_i σ. So κ(σu_1, …, σu_n) = κ(μ_1σ, …, μ_nσ) = ∏ μ_i · κ_n(σ) by multilinearity. ∎

Since log cosh t = Σ κ_n t^n/n! and its derivative is tanh t, |κ_{2j}(σ)| = T_j, the tangent numbers 1, 2, 16, 272, 7936, …

**Construction (all knots NAE).**
- A path x = v_0, …, v_k = y through k NAE knots.
- N further NAE knots attached at x, with b_i one child of the i-th.
- S = {x, y, b_1, …, b_N}, so |S| = N + 2.

Root at x and write σ = s_x. Then s_{b_i} = σ r_i and s_y = σ R, where R is the product of the path-child factors. All these factors come from distinct knots, so they are independent, each with mean −1/3. By the Lemma (taking u = 1 for x):

κ_S = κ_{N+2}(σ) · (−1/3)^{N+k}, which is nonzero for N even.

Hence

δ(x, y) ≤ N + max(0, k + N − log_3 T_{(N+2)/2}).

When the max is positive this equals k − (log_3 T_{(N+2)/2} − 2N). So δ < k as soon as T_{(N+2)/2} > 9^N.

**Threshold.** The ratio T_{n+1}/T_n ≈ 2n(2n+1)·4/π² exceeds 81 from n = 7 on, and the accumulated deficit is recovered at n = 17, i.e. N = 32:

- T_17 = 3729407703720529571097509625856 ≈ 3.7294·10^30
- 3^64 = 3433683820292512484657849089281 ≈ 3.4337·10^30

These values are from memory. They agree with the asymptotic T_n ≈ 2(2n−1)!(2/π)^{2n}, which gives 3.729·10^30, but please recompute them from the tanh series. At n = 16 the inequality fails (8.71·10^27 against 3^60 = 4.24·10^28).

So log_3 T_17 ≈ 64.075. With N = 32 and any k ≥ 33:

**δ(x, y) ≤ k − 0.075 < k.**

The margin is thin at N = 32. With N = 34 and k ≥ 35 it is comfortable: T_18/3^68 ≈ 6.47, so δ ≤ k − 1.70.

## 2. Smallest instance in this family

- **Self-contained version:** k = 33 and N = 32 gives 65 knots, 131 variables, |S| = 34, δ ≤ 32.925 against k = 33.
- **Compact version, 48 knots (97 variables):** put the hub at an interior path variable w = v_i and attach 15 extra NAE knots {w, b_i, c_i}. Take S = {x, y, p_i, p_{i+1}, all b_i, c_i}, where p_i and p_{i+1} are the off-path variables of the two path knots at w. Again |S| = 34.
  - Conditional on s_w, every singleton has E[·|s_w] = d·s_w, with ∏ d = (−1/3)^{65}.
  - Any two-element block inside one side has conditional covariance even in s_w (global flip symmetry), hence constant, and it drops out.
  - By (iii), κ_S = κ_34(σ)(−1/3)^{65}, giving the same δ ≤ 32.925.
- **Minimality:** N = 32 and k = 33 are the minimum for this hub family. I have not proved that no other mechanism gives a smaller counterexample.
- **Asymptotics:** the gap is unbounded. Taking N with log_3 T_{(N+2)/2} ≥ k + N gives δ ≤ N, and log_3 T ~ N log_3 N, so δ(x, y) = O(k / log k). δ is not even linearly comparable to steps apart.
- **Parity pairs:** a parity knot at the hub gives κ(b, c | s_w) = s_w, an exact copy of s_w for two variables. This has the same cost of 9 per copy and the same threshold.

## What is provable

Call the off-path part through p_j the branch of path knot j.

- **A. A parity path knot whose branch misses S forces κ_S = 0.** Root at v_{j−1}. Then s_{v_j} = s_{v_{j−1}} ε_j, and ε_j is uniform, independent, and used nowhere else in S. So the S-variables on the y-side are independent of those on the x-side, and the mixed cumulant vanishes.
- **B. Pure parity trees: δ = k.** By A, S meets all k disjoint branches, so |S| ≥ k + 2.
- **C. |S| = 2.** κ = m_xy, which is (−1/3)^k if the path is all NAE and 0 otherwise.
- **D. |S| = 3.** Means vanish, so κ = m_xyz.
  - If z hangs off (or is) a path variable w, the three are conditionally independent given s_w with E[·|s_w] = d·s_w, so m = d_x d_y d_z E[s_w³] = 0.
  - If z lies in the branch of knot j, m = d_x d_y d_z · E[s_{v_{j−1}} s_{v_j} s_{p_j}]. This is 0 for an NAE knot. For a parity knot it has absolute value at most 3^{−(k−1)}, and 0 if another parity knot lies on the path.
  - Either way the bound holds.
- **E. What I could not prove.** The case |S| ≥ 4 for mixed or NAE trees. It can only hold up to some threshold below 34.

**Where a general proof breaks.** In (iii), the factor κ_r(s_w) grows factorially, while each extra variable buys only a factor 3 of slack and costs at best 1/3 in d. That is a net 9 per copy of s_w, against a growth ratio of about r²·4/π² per two copies. Any leaf-removal or covering induction has to bound that coefficient by 1, which is false. Your checks up to 6 knots pass because T_j < 81^{j−1} for small j.

## 3. Literature (from memory, unverified)

- **Pairwise case.** For pure NAE, −log_3 |m_xy| = k is the classical additive tree metric of the symmetric binary (CFN) model. See Pearl and Tarsi (1986), Steel's log-det distance (1994), Erdős–Steel–Székely–Warnow, and the "information distance" of Choi, Tan, Anandkumar and Willsky (JMLR 2011).
- **Closest to your setting.** Zwiernik and Smith, "Tree cumulants and the geometry of binary tree models" (Bernoulli 2012), and Zwiernik's L-cumulants and his book *Semialgebraic Statistics and Latent Tree Models*. They replace the full partition lattice by tree-induced partitions so that the quantities factorise over edges. That is precisely what removes the tangent-number growth of classical cumulants.
- **Related.** Classical cumulants here are the Ursell functions of a tree Ising-type model, and (iii) is Brillinger's formula.
- **Your statement itself.** I do not know of the hypertree parity/NAE statement "δ = steps apart" in print. With classical cumulants it is false as stated.

**Suggested repair (unproven).** Define δ with tree or L-cumulants, or restrict S to {x, y} plus at most one variable per path-knot branch. Both exclude the hub mechanism, but I have not proved the lower bound for either.
