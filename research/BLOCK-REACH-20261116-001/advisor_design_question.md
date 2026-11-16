Advisor: design review before freezing (under 700 words; concrete; say what you checked and point out gaps).

Setting: as in DIRECT-REACH-20261115-001 (research/DIRECT-REACH-20261115-001/direct_reach.md; proof
proofs/DIRECT-REACH-20261115-001B/.../proof.md). Addressed NAE patterns placed by automaton maps; the maps' orbits split each level;
the block of an orbit (orbit with its children) holds every knot placed at the orbit; blocks meet only parent to child; with orbits of
at most four addresses there are finitely many block types, feasible sets F_r (by remaining depth r) stabilise at r0, and exact
projections are computed block by block. L_N(k, s) = least bond of the depth-N pattern meeting level k and level k + s (members anywhere).
Of the LEVEL-REACH census's alive descriptions, 786 have orbits of at most four addresses: 42 direct (proved bounded at every depth),
43 half-rate [3,3,4,4], 399 rulers [3,4,5,6] (the hypertree theorem covers the acyclic ones; the cyclic ones are open, backlog B180),
294 other, 8 undecided.

Prior result to reuse: BRANCH-DEPTH-20261112-001A (proofs/BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/proof.md):
on one branch split into groups with a finite interface, if T^r = dom × ran (rectangular), then every finite minimal constrained set
with members introduced at group 0 and at group s has at least 1 + ceil(s/r) members, arbitrary side support allowed (splicing lemma).

Plan.
(1) Theorem F. Along a descending path of orbits O_k, O_(k+1), ..., group j holds O_(k+j) and the side subtrees of O_(k+j-1)'s other
children; the interface is the orbit's assignment; the group relation is the block step (orbit assignment to child-orbit assignment,
the block's knots holding, every other child's subtree feasible with F at the right remaining depth). Group relations vary with type
and remaining depth, but the splicing lemma needs only that each window of r consecutive groups composes to a rectangular relation.
If every r-window of every type path, at every remaining depth (F_0..F_r0), is rectangular, then L_N(k, s) >= 1 + ceil(s/r) for every
s and every N >= k + s. A target outside the top orbit's subtree: the path goes up to the lowest common orbit at level b < k and down;
the top member then lies in a side subtree of the first down-step, and the down part has k + s - b - 1 >= s groups, so the bound holds.
Exploratory, stabilised F only: half-rate r = 2 (19) or 3 (24); rulers r = 1 (228), 2 (152), 3 (19); other r = 1 (283), 2 (8), 3 (1),
none (2); undecided r = 3 (6), none (2); direct never forget (42). So among small orbits, every description that forgets grows at every
depth, and of the 46 that never forget, 42 are proved bounded; 4 are open (profiles [3,4,4,4], [3,4,5,5], two partly undecided).
(2) Run the full check (all remaining depths, both path cases), split the rulers into acyclic and cyclic, and gate: no census depth-9
value below the bound (1,288 descriptions); the composed relations against SAT projections of the whole pattern on a sample.
(3) Upper bounds are not attempted at every depth here (the fixed-size reachability of BRANCH-DEPTH-20261112-001D, adapted to marked
block tables, is the next study); state rates as "at least 1/r at every depth".
Predictions to freeze: P1 the full check gives the exploratory r for at least 40 of the 43 half-rate; P2 at least 90% of the
small-orbit cyclic rulers have r <= 3; P3 every small-orbit description with a census profile that rises within s = 1..4 forgets
(r exists).

Questions: Is Theorem F's transfer from one fixed relation to type- and depth-varying windows sound, and is my group/interface
choice right (in particular that the rest of the pattern above O_k is group 0 with interface O_k, and the up-then-down case)? Is
"rectangular on all of Q" what I need, or only on reachable assignments? Should the bound count the target's group (is it
1 + ceil(s/r) or better)? Are the predictions sensible or settled by construction? Anything cheap that would give upper bounds now?
