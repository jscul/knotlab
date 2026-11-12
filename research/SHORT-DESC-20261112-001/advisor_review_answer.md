**Flaws**

- **"Large patterns are all nested" is false as stated.** Plain def-calling-def with r=6, c=12 reaches 12^6 knots with no SELF, and a single SELF call per body grows linearly in t, not exponentially. The noself variant will have 100+ knot patterns, so drop or reword this.
- **"Limit within 4 steps" holds only for one SELF def.** Stacked SELF defs each shrink only after the ones below settle, so the bound is 4·(#SELF defs).
- **Fate labels ignore revivals.** Dead-at-1-then-alive is filed as "at once" and alive–dead–alive as "a while". Either define fates by first death explicitly, or add "eventually always dead" versus "recurrently alive", which the cycle already gives you.
- **Counts need reconciling.** If about 6% of weight has ≥7 knots, 20k tries should give about 1,200 eligible patterns, not 405. State where the rest went (rejections, n>400), since that selection conditions every S-test.
- **Define n.** If unused ports or locals count, the baselines inherit isolated variables, which deflates their tie share and dead share mechanically.

**Settled or near-settled but presented as tests**

- **S3 is close to guaranteed.** Most paired patterns sit far below the uniform threshold, where the uniform tie share is essentially 0. A body with several K calls on ≤12 variables forces ties locally, so any nonzero mean passes. Test against the degree-matched baseline too, or restrict to a density bin where uniform patterns have ties.
- **S4 is not really blind.** "At once" means the t=1 pattern is dead, and your smoke already puts dead weight at roughly 0.06 × 0.027 ≈ 0.2% of descriptions. So "at once ≥ 1%" probably fails for reasons you have already seen.
- **"Forever implies limit alive" is by construction.** The K-truncation contains the TOP-truncation at each depth. Only the converse (finite all dead, limit alive) is empirical, so report that cell.
- **"~94% of weight has <7 knots" is a measurement, not a construction.** Label it so.
- **S5-noself is mostly S1 again.** By weight, most S1 patterns likely have no SELF.

**Overclaims**

- **The purpose statement.** S1–S3 compare structure at matched (n,m) drawn from your own size distribution. They do not test "outcomes change with the weighting" against the earlier weightings, and "simple realities are more common" is the 2^-bits definition, not a finding.
- **"Uniform … using every distinction."** This is fine only if the 30 steps per knot are shown to mix; report a dead share at 30 versus 60 steps. Do the same for the switch chain, where degree-matched dying more than uniform deserves a mixing check.

**Thresholds**

- **S1/S2:** with about 24k pairs the pooled CI will exclude 0 trivially. Register a per-bin criterion instead: CI below 0 in each knot bin ≥30, and an effect size floor (say ≤ −0.01 pooled).
- **S4:** condition on families with ≥7 knots at t=1 for "at once", or lower that fate to 0.1%. Keep 1% for the other two.
- **S3:** require a difference ≥ 0.005 absolute, not just >0, and report the share of patterns with any tie.
