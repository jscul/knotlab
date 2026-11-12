Review this frozen design cold and briefly (at most ~350 words): flaws, anything settled by construction presented as a test, overclaiming wording, thresholds to change. Be concrete.

CONTEXT. NAE on three-place knots. Prior epic: a description language (straight-line macros; SELF lets a 3-port definition hold its own pattern inside each of its knots, depth t; depth 1 SELF = knot). A referee found 98.1% of nested families are "monotone at the knot": F(knot) ⊇ knot (the definition, with SELF read as a knot, allows on its ports at least what a knot allows), which by monotonicity settles that they live at every depth. Owner asks: (a) is a distinction at one level bonded to ones many levels away through a few others, and does that grow, hold or die with level; (b) two variants: inner patterns share distinctions with the outside only through the holding knot ("knot": SELF only in 3-port definitions) vs directly ("direct": SELF only in 4-6-port definitions; the holding knot = first three arguments, extra arguments shared directly).

DESIGN. Families sampled by the prior code (fair coins), strata: constraining (some SELF definition has F(knot) not ⊇ knot) and monotone. Read each family at the largest depth t<=12 with <=60 distinctions; keep if alive, n>=8, a level-0 distinction in a knot, and distinctions at level >=4. Level = number of SELF substitutions above the call that created the distinction. One random level-0 distinction u; up to 2 random v per level s>=1. Read: steps apart d (knot-graph distance) and least bond L containing u and v, exact up to size 5 over all distinctions (bond = inclusion-minimal set whose allowed joint states are not all; frozen exact reader), else "none within five". Baseline: uniform pattern with same n, m (replace-one-knot chain, alive), one pair at each nested pair's d. Quotas per worker: 60 constraining, 30 monotone; 8 workers per variant. Plumbing run (seed not reused) looked only at sizes and timing.

SETTLED (stated, not tested): steps apart are set by the substitution; Berge-acyclic patterns have L = d+2 (proved earlier), a control; tied port relations force ties at every level below; monotone families' allowed states on outer distinctions only widen with depth, constraining ones narrow.

PREDICTIONS.
P1 control: no violation of L=d+2 (within the cap) in Berge-acyclic patterns.
P2 monotone families follow the steps: pairs with d<=3 bonded within five >= 85%; pairs with d>=4 (or unreachable) <= 10%.
P3 constraining families carry influence beyond the steps: share of d>=4 pairs bonded within five >= 0.10, and constraining minus monotone CI (bootstrap over families) above 0.
P4 constraining: influence holds with level: share bonded within five at levels>=4 minus level 1 >= -0.10 (CI lower end not required).
Reported: by level (bonded, median d, ruler L=d+2, shortcut L<d+2, ties L=2), by d nested vs uniform, direct minus knot (far share, deep share).

Is anything here settled by construction (e.g., P3 forced by ties that the constraining stratum's definition already implies)? Is P4's form sensible? Anything cheap missing?
