Advisor review before freezing predictions (under 600 words, concrete; say what you'd change). Setting as in your earlier design answer (addressed patterns with knots within a level or joining a level to the next; top = level 3, target = level 3+s, s=1..4; N=9; exact least bonds by an implicit-hitting-set search over implied clauses, certified; k_max=10; undecided cell).

Exploratory pilot (held-out seeds, 247 of 998 descriptions, stopped for time): outcomes no join 29, no bond (top and target disconnected) 52, ruler L(s)=s+2 i.e. (3,4,5,6) 116, constant bounded (3,3,3,3) 5, rigid-like (2,2,2,2) 5, other 10 (e.g. (3,3,4,4); (3,>10,>10,>10)), undecided 22, dead 3. By relative activity class: finitary 125 (ruler 65, no bond 45, no join 14), exponential 114 (ruler 51, other 10, rigid 5, bounded 4, undecided 20, no bond 7, dead 3), bounded 3, polynomial 0. Every least bond found lies within levels <= its target (572 of 572; no member below the target was needed). Time per description: median 1 s, 90th percentile 617 s.

Registered run as I plan to freeze it: W_R the first 2,000 fair-coin draws (seed 20261121) plus E_R lists (every s=2 automaton x 5, 1,000 s=3 automata x 2) kept only where the relative class is bounded or polynomial, 1,288 distinct descriptions; budget 150 s per (description, s); every refutation's CNF and proof kept with hashes.

Predictions I plan to freeze (fails-if in brackets):
Q1 ruler typical: among alive joined descriptions with every L decided and a bond at s=1, at least 70% by weight have L(s) = s+2 at every s [below 70%].
Q2 rigid-like rare: at most 10% of the same set has L=2 at every s [above 10%].
Q3 no overshoot: every least bond found lies within levels <= target [any bond needs a member below its target].
Q4 class difference: the non-ruler share (rigid-like, constant bounded, other) is higher in the exponential class than in the finitary class, with a 95% cluster-bootstrap interval (by automaton class) excluding 0 [interval includes 0 or reversed].
Q5 bounded and polynomial classes (from E_R): their ruler share is at least the exponential class's [lower, interval excluding 0].
Questions: (1) are these sound, or settled by construction (e.g. is the ruler forced whenever a tree-like vertical placement is present and horizontal placements cannot shorten across levels)? (2) is "growing to depth N" honest given L is monotone non-increasing in N? (3) anything to add for John's question "does the top bind the deep levels, and is that typical"?
