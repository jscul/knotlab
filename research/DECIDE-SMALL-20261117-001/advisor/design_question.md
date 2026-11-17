Before freezing a design and predictions I would like a colleague's check (a missing test, a flawed stop rule, a better sample, which
outcome you expect). Please be concrete and brief (under 500 words).

Setting (as before): addressed not-all-equal patterns from a finite automaton (s in {1,2,3} states, output flips, transitions) and
1 to 4 placements (triples of slots); orbits of at most 4 addresses ("small orbits"), a tree of blocks with finitely many types.
L_N(3, s) = least bond meeting level 3 and level 3 + s. Tools now available, each proved:
 T1 forgetting on all assignments along blocks -> L grows (>= 1 + ceil(s/r)).
 T2 a two-orbit bond (top orbit, lower orbit) at every s and depth tier -> bounded (every-depth routine).
 T3 forgetting on the values states actually take -> grows.
 T4 bonds inside the top orbit with the lower orbit's block, or inside a stem of depth 2 (top orbit plus the lower orbit's ancestors
    at the next two levels) and the lower orbit, at every s and tier -> bounded.
 T5 the product test along joined children only (children that share a knot with the parent) on the component of level 3: every
    l0-step composite a product -> grows linearly.
On KEEP-REACH's 2,380 fresh and mutated small-orbit descriptions (583 distinct patterns) these decide everything: T1 244 patterns, T2
most bounded ones, T3 6, T4 5, T5 5. The census's 786 small-orbit descriptions (181 patterns) are decided by T1 and T2 (139 + 42).

Plan: a fresh sample with KEEP-REACH's fair-coin sampler and a new seed, 10,160 draws (10 times its 1,016), keep small-orbit
descriptions alive at every depth, deduplicate to distinct patterns by the clause set at depth 9 before any test, then run T1, T2, T5,
T3, T4 in draw order, stopping at the first pattern that none decides (all tests completed; a timeout is recorded as such and the run
continues). That pattern becomes the object of study.

Questions: (a) is a test missing that is cheap and natural (stems of depth 3, two-block bonds, a decorated test)? (b) Is dedup by the
clause set at depth 9 safe, or can two descriptions agree at depth 9 and differ deeper (should I use the window-tree type structure
instead, or depth 12)? (c) Is the stop rule sound (e.g. a pattern undecided only because T4's cap of 8 members is too small)? (d)
Predictions I plan: the toolkit decides every distinct pattern (55%); distinct patterns are 25-60% of the kept descriptions; at least
90% of distinct patterns grow by T1; T3 + T4 + T5 decide at most 2% together. What would you change?
