Please review this frozen-to-be design cold and briefly (at most ~450 words): flaws, anything settled by construction that I present as a test, wording that overclaims, thresholds or predictions that should change. Be concrete.

CONTEXT. Law: not-all-equal on three-place knots. Nested families come from a straight-line macro language (defs D_0..D_{r-1}, last is main; a 3-port def may call SELF; earlier defs callable). A family's weight is 2^-bits of its description minus the depth (assumption A79). 223,261 nested draws (124,572 distinct families) from 1.2M tries, regenerated exactly from the earlier census's seeds (0 mismatches). Fates: forever 220,880 draws; dies at some depth with a dead usual limit 1,487; dies at every... "limit-only" (dies at some finite depth, usual limit lives) 894. Earlier work, on the 664 one-def limit-only families only: least ray bond L_ray(s) (least minimal non-shattered set among the ray's own distinctions containing a top port and an own distinction of copy C_s, in the usual limit's states, side SELF calls replaced by the limit relation) is a fixed-length shortest path in a finite graph; Karp's minimum cycle mean λ on the trimmed graph gives L_ray(s) >= λ(s - t); an exact residue test (lcm of zero-cycle lengths) decides eventual boundedness. Result there: 226 grow (λ>0), >=361 bounded, 12 no ray bond at large depths.

QUESTION. Across all nested draws: what share by weight (draw share = Monte Carlo estimate of the weighting) and by count (distinct families) has L_ray growing, bounded, or absent; does it differ by fate?

GENERALISATION to multi-def families: inline every non-self-holding def. Ray def S = main if self-holding, else the callee of main's first (inline order) call to a self-holding def. C_1 = the copy of main's first call to S; C_{j+1} = S's first SELF call in C_j; every other self-holding call is a side branch with its usual-limit relation. Start block = main (W must contain a port of main, k up to 6), middle and closing = S.

SETTLED BEFORE THE RUN (measured on the draws; no ray bond, proofs one line each): usual limit dead 0.67%; main reaches no copy 5.83%; S has no own distinctions after inlining (all copies live on the top three) 52.6%; every own distinction of S lies in no knot, no side call with a non-TOP relation, and not in the ray call 2.37%. Total 61.4% of weight. Computed: 38.6% of weight, 60,081 distinct families. Timing pilot (200 one-def computed families, I looked only at time and graph size): all complete, median 0.14 s, max 17 s.

CLASSES for computed families: grows (complete graph, λ>0; ray-only lower bound); bounded (exact test positive; transfers to the true bond); zero mean but not eventually bounded; no ray bond at large depths (no cycle in trimmed graph); unresolved (caps: 300k nodes, 300 s, block size V<=12).

REPORTING: shares two-sided: lower = Wilson lower of class/N, upper = Wilson upper of (class+unresolved)/N. "Typical" only if lower > 1/2, "rare" only if upper < 1%.

PREDICTIONS (blind):
P1 among computed forever families with a ray bond at large depths, bounded is typical by weight.
P2 growth is not rare among computed forever families: lower >= 5% by weight.
P3 the limit-only cell grows more often than computed forever families: weight-share difference >= 10 points, bootstrap CI above 0 with unresolved assigned adversarially.
GATES: reproduce the earlier λ, completeness and exact-test certificates on the 664; SAT brute force agrees at s=1,2,3 on 200 random computed families (>=100 multi-def); inlined port relations equal the census's per-def relations.
