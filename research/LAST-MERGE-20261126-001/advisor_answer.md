# The advisor's answer, before the freeze

A colleague's view, checked before use. Model: the Fable model this host serves. [Question](advisor_question.md)

1. **Circularity.** T and K are two statistics of the same count series. The total count is the sum of the local-type counts, so "total never falls again" is close to "the total has settled," and K ≤ T+3 mostly says the parts settle within three rounds of the sum. With two fitted offsets joined by a max, a held-out pass is nearly guaranteed. The bound earns a test only if it predicts something sharper: (a) the point value K = T+3 on starts failing M+5, not an inequality; (b) which starts fail M+5, from a static criterion; (c) the slack distribution K − max(M+5, T+3) with a stated expected tightness. Also check now whether T+3 alone holds on the 1,509 starts that passed M+5. If it does, M is a red herring and the claim is just K ≤ T+3.

2. **Definition of T.** Write c_t for the total count and fix T = min{t : c_s ≤ c_{s+1} for all t ≤ s < 24}. Plateaus then count as non-falls. Two defects remain. A dip at round 22 gives T = 22 and a bound beyond the horizon, so it passes vacuously. And settling needs enough rounds past K to check: a degree ≤ D−1 polynomial is tested only by the D-th finite difference, which needs D+1 points, so K must be ≤ 24 − D (18 for six-knot starts) to be checked at all. Require that and treat censored starts as failures or exclude them explicitly. A sharper T: the first round after which no new local type appears. That is structural, not a monotonicity accident.

3. **Static T.** In the cluster picture, round t births are connected (t+1)-clusters. A finite tree-like component of size s contributes through round s−1 and contributes zero from round s, so the last drop lands at round s, not s−1. Your rule has an off-by-one that the +3 absorbs. Freeze T_static = s_max and check it against the observed T on the 47 you already have before touching the fresh sample. If T − s_max is a constant on all 47, you have the offset. If it varies, the static rule is wrong and the infinite part is not monotone. Better still: if the proved class really gives births as subtree clusters modulo cover symmetry, c_t is computable exactly from the map for all t ≤ 24, so K itself is predictable. Freeze that exact K_pred and test equality. A bound is a weaker claim than you can make.

4. **Failure modes.**
   - Slack: report the fraction of starts where K equals the bound, and a null rate from randomized T.
   - Horizon censoring as in item 2, with trivial interpolation passing as "settled."
   - Duplicates: the fresh sample may contain relabelings of earlier starts. Deduplicate by isomorphism class and by map type.
   - Unstratified sampling: 2% of starts are informative. Oversample large s_max and large M.
   - The two knot laws share each start, so they are not independent trials.
   - Dead types with all-zero counts trivially satisfy the polynomial test.
   - Pre-register the falsifier: one violation, or a rate.
