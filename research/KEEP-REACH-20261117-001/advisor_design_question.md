Advisor: design review before freezing (under 500 words; say what you checked; point out gaps; propose a proof idea if you see one).

Setting: addressed NAE patterns placed by automaton maps; blocks of orbits (orbit + children) meet only parent to child (Theorem W,
DIRECT-REACH-20261115-001B); with orbits of at most four addresses, finitely many types; exact joints of two orbits at every depth.
Forgetting (BLOCK-REACH-20261116-001A, Theorem F): if every composition of r consecutive block steps (orbit to child orbit, other
children's subtrees feasible) is rectangular, L_N(k, s) >= 1 + ceil(s/r) at every depth. On the census's 786 small-orbit descriptions:
740 forget (grow), 46 never forget (closure of the sets of window compositions repeats with no rectangular stage); 42 of the 46 are
direct (bounded, proved). Exploratory, disclosed: the other 4 have a bond inside two orbits (exact joint; any size; meeting both) at
every s up to 24 at stable depth, of sizes 4, 4, 5, 6 (census profiles [3,4,4,4], [3,4,5,5], partly undecided). So on the census:
forgetting <=> unbounded.

Plan. Theorem K: from the exact joints (the refereed every-depth pair-state routine, with the property "least bond of any size
inside the two orbits meeting both"), L_N(k, s) <= that value at every depth and every s; eventually periodic. Run on all 786 (every
depth tier) and on a fresh held-out sample of random descriptions (my own fair-coin sampler, s in 1..3, 1..4 placements of slot
triples), to test Conjecture C: for small-orbit patterns, never forgetting implies a two-orbit bond at every distance (so bounded), and
hence bounded reach <=> some relation between two orbits never forgets. Gates: consistency with W (ties -> 2, three-member -> 3);
least_cross_bond against brute force on random relations; no two-orbit bound below a census depth-9 value; forgetting with r implies no
two-orbit bond for s >= r (by construction).
Predictions to freeze: P1 every one of the 46 has a two-orbit bond at every s and every depth tier; P2 in the fresh sample, no
small-orbit description never forgets and lacks a two-orbit bond at some large s (zero counterexamples).

Questions: (1) Is there a proof of Conjecture C? Never forgetting means the finite semigroup of window compositions has a
non-rectangular idempotent (classical: TIE-CYCLE's Theorem I); is it automatically realized in the full pattern (Up/Down feasible
sets could cut it to a rectangle)? And does a non-product joint of two orbits always contain a bond meeting both (minimal constrained
with every proper subset free), or can every cross-dependency pass through a constrained part of one orbit? (2) Is my "never forget"
(rectangularity on all of Q) the right notion, or should forgetting be read on the values states actually take at the cuts? (3)
Anything that would make the random sample's test sharper (where would a counterexample live)?
