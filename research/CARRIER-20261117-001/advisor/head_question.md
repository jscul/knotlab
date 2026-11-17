I am testing a conjecture about how far a top level's influence reaches in a tree-structured constraint system, and I would like a
colleague's view on two things: the analysis (is my sharpened conjecture plausible, trivial, or likely false, and how could each
direction be proved) and a word.

Setting. Addressed not-all-equal patterns: binary addresses, levels n = 0..N (level n has 2^n addresses), three-place not-all-equal
constraints ("knots") placed by finite automaton maps on addresses. Orbits (sets of at most 4 addresses at one level, under the
placement's maps) partition each level; the child orbits of an orbit partition its children. Every knot lies in the block of some orbit
(the orbit with its children), and blocks meet only parent to child, so the system is a tree of blocks with finitely many orbit types.
Projections onto any orbit, or onto two orbits, are computed exactly by message passing, at every depth (feasible sets stabilise after
r0 levels; pair states along a descent are eventually periodic). A bond is a minimal constrained set of variables (constrained: some
assignment of it is not allowed; every proper subset free). L_N(k, s) is the least size of a bond of the depth-N system that contains a
variable at level k and one at level k + s. Bounded reach: L_N(k, s) bounded over all s and N >= k + s.

Known (proved). Theorem K: if a bond inside two orbits (one at level k, one at level k + s) containing a variable of each exists at
every s and every depth, its size bounds the reach. Theorem F': if for some r every pair projection of an orbit at level j >= k and a
descendant orbit r levels below is a product (every pairing of the two marginals allowed), then L >= 1 + ceil(s/r) (splicing). Lemma E:
a missing pair (x, y) with both sides "exposed" (each the only assignment of its orbit with its values on some free subset) gives a
bond inside the two orbits. Conjecture C' was: bounded exactly when a two-orbit bond from level k exists at every distance.

New computations (exact, every depth, depth-11 readings certified by SAT with LRAT):
1. Two patterns (bace53f8f952-147 and -111) have no two-orbit bond from level 3 past s = 2 at depth tiers r >= 1 (r = N - k - s),
   yet a bond inside the top orbit O_u and the block of O_v (O_v with its children at level k + s + 1) exists at every s and every
   depth: 4 members (one at level k, one at k + s, two at k + s + 1) for r >= 1 or 2, and a two-orbit bond of 5 at r = 0 or 1. So they
   are bounded at every depth and C' fails as stated. The dependence between the two orbits was "unexposed"; the children expose it.
2. Thirteen mutants of 8db5da810c00 have top pair projections that become products from s = 5 on (while deeper pair projections never
   do), and no orbit-and-block bond past s = 4. One of them reads L_11 = L_13 = 3, 4, 5, 5, 6, 6 for s = 1..6 (certified). Its least
   bonds at s = 5 and 6 lie on one line of orbits: two addresses of the top orbit A_0 (level 3), one of A_1 (level 4), two of A_2
   (level 5), all ancestors of O_v, and one address of O_v at level 3 + s. A computation of the least bond inside A_0 ∪ A_1 ∪ A_2 ∪ O_v
   (A_1, A_2 = O_v's ancestors at levels k + 1, k + 2) reproduces 6 at s = 5, 6 at depth 11; the every-depth run is going.
3. Ten others (9 mutants of ca1efb37ad88, 1 of bace53f8f952) have no two-orbit and no orbit-and-block bond past s = 4; their top pair
   projections stay non-product at every s, with every missing pair unexposed; the certified search cannot decide s = 5, 6 within
   900 s.

Sharpened conjecture (call it C*): the reach from level k is bounded exactly when, for some fixed d and e, a bond inside "the top
orbit with O_v's ancestors at levels k+1..k+d" together with "O_v's subtree to depth e" (containing a variable at level k and one at
level k + s) exists at every s and every depth. The "if" direction is Theorem K's argument for exact projections. Questions:
(a) Is the "only if" direction plausible? A bounded family of bonds of size <= c across distance s has a gap of length >= s/c between
    occupied levels; could a bounded family need a middle cluster far from both ends, or could pumping on the periodic pair states
    move every middle cluster to an end? What is the cleanest proof idea, or the likeliest counterexample shape?
(b) The growth side: Theorem F' uses products between single orbits. Is the right growth hypothesis "the pair projection of the head
    (top orbit plus d ancestors) and orbits r levels below the head becomes a product for every d", and does splicing still work with
    a head?
(c) A word for the object "the top orbit together with the lower orbit's ancestor orbits at the next d levels". The glossary already
    has: orbit, block (an orbit with its children, holding its knots), descent (a block followed down the levels, addresses extended
    letter by letter, letters eventually periodic), pair projection, product, two-orbit bond, exposed, unexposed dependence, bond, tie.
    Words from a space of two or three dimensions (edge, surface, lattice, ...) are not allowed for our own objects; one word per
    meaning, one meaning per word; "chain" is already used elsewhere (a chain of implications, a chain grid), "hidden" and "joint" are
    taken. Please propose one word or short phrase, and say what it clashes with.
Please be concrete and brief (under 600 words).
