You reviewed my earlier draft and proposed a straight-line macro grammar. I built it. Please review the frozen design below cold and briefly (at most ~400 words): flaws, anything settled by construction that I present as a test, wording that overclaims, and thresholds that should change. Be concrete.

LAW: not-all-equal on three-place knots (positive NAE-3-SAT). A pattern = set of distinct triples; dead = no NAE assignment.

LANGUAGE (frozen code): description = defs D_0..D_{r-1}, last is main. Def i: k>=3 ports, l>=0 locals, c>=1 calls; call = K (one triple on 3 distinct of the def's k+l variables), an earlier D_j (on k_j distinct variables), or SELF (only in k=3 defs). If SELF is used, a depth t>=1: depth 1 SELF=K, depth t SELF=def at depth t-1. Code: Elias gamma for r, k-2, l+1, c, t; callee uniform among allowed; args uniform ordered tuple of distinct variables. Weight of a description 2^-bits (fair coins); pattern weight = sum over its descriptions. Caps: r<=6, k<=6 (variant "wide": 8; variant "noself": no SELF), l<=6, c<=12, t<=6, expansion <=3000 knots; rejections counted per cause.

EXACT EVALUATION: each def's port relation by enumerating its k+l variables given callees' relations. For nested families (description minus t): iterate depth from SELF=NAE (finite truncations) until SELF relations repeat; fate = "at once" (dead at t=1), "a while" (alive at 1, first dead at T>=2), "forever". Infinite limit: iterate from SELF=TOP (SELF calls dropped) to the greatest fixed point; by compactness the infinite pattern is alive iff the fixed point's main relation is nonempty. Limit relation of each SELF def classified: none / three tied (1 complementary pair) / two tied (2) / knot (3 pairs; K1-K3 on 3 ports, cross-checked against our canonical checker on all 16 complement-closed relations: exactly the 3-pair ones are knots) / free (4). Port evaluation agrees with a SAT solver on every expanded pattern (smoke: 0 mismatches of 7,147).

SETTLED BY CONSTRUCTION (to be stated, not tested): short descriptions weigh more; ~94% of weight has <7 knots, always alive (m(3)=7, Fano smallest dead); every described pattern has primal treewidth <= k+l-1 <= 11 (13 wide) via the call tree; large patterns are all nested (depth costs ~2log t bits, size grows exponentially); a nested family's fate is decided within 16^(#SELF defs) depths, the limit within 4 steps; a flat language with only K calls is uniform given (n,m).

BASELINES (patterns with >=7 knots, n<=400): uniform with same n and m using every distinction (replace-one-knot chain from the pattern, 30 steps per knot, symmetric proposal); same degrees (switch chain, 20 steps/knot). Readings (n<=200): exact tie share of alive patterns (pairs equal-in-all or unequal-in-all states / C(n,2)), first 1500 eligible per worker; baselines' tie share on an alive draw (up to 5 redraws); minimal dead cores (reported).

DISCLOSED SMOKE (20k tries, seeds not reused): 405 paired patterns; dead share desc 0.027, uniform 0.059, degree 0.086; paired differences -0.032 [-0.054,-0.012] and -0.059 [-0.086,-0.035]; by knots 100+: 0.17 vs 0.42 vs 0.58. I did NOT look at ties or nested fates.

PREDICTIONS (registered run: 8 workers x 150k tries per variant, fresh seeds):
S1 desc dies less often than uniform at same (n,m): paired difference CI below 0 (replication of the smoke; expected in kind from bounded treewidth). Fail: CI reaches 0.
S2 same against degree-matched. Fail: CI reaches 0.
S3 (blind) alive desc patterns have a higher tie share than alive uniform ones of the same (n,m): paired CI above 0. Fail otherwise.
S4 (blind) among nested families (weighted), each fate (at once, a while, forever) has weight >= 1%. Fail if any < 1%.
S5 S1 holds in "wide" and "noself" (CI below 0 in each). Fail otherwise.
Reported: limit kinds, first-death depths, period, revivals, weight shares, core sizes, S1 by knot bins.

Purpose: test whether outcomes change with the weighting (vs uniform/growth weightings used before) and the owner's guess "simple realities are more common", with his picture of a knot holding a recurring pattern inside itself (SELF) and one variable touching many knots (shared args).
