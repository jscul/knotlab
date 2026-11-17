I am about to freeze a proof plan and predictions, and I would like a colleague's check of the analysis (gaps, false steps, a simpler
route) before I do. Please be concrete and brief (under 700 words).

Setting (as before). Addressed not-all-equal patterns: levels 0..N of binary addresses; orbits of at most 4 addresses partition each
level; an orbit's block (the orbit with its child orbits) holds all its knots; blocks meet only parent to child, so the depth-N system
P_N is a tree of blocks, with finitely many orbit types (a type fixes the types of the children). F[r][t] = assignments of a type-t
orbit that extend to r further levels; F[r] is constant for r >= r0. A step relation from an orbit to one child (other children
quantified into their feasible sets) depends only on the type and, through the feasible sets, on the remaining depth, which is
irrelevant once it is >= r0 ("saturated"). L_N(k, s) = least bond of P_N with a member at level k and one at level k + s (k = 3 here).

Plan, part 1: a normal form. Fix c. For a bond B of size <= c, take its skeleton S (the root-closed subtree of the orbit tree spanned by
B's orbits). Special orbits: those holding a member, branch points of S, orbits at level <= k (the top region), and orbits within the
bottom band (remaining depth < R, R = r0 + 1). Segments: maximal paths of S whose interior orbits are not special; their interiors are
saturated. A segment's effect on the projection onto B is the composite of its step relations; the state (current type, composite)
takes finitely many values, M; lengths of segments from a given start state to a given end state form an eventually periodic set
(threshold T, period dividing Q = lcm(1..M)). Replacing a segment by one with the same end type and composite, and moving the part of S
below it to the isomorphic place under the new end (same type, so isomorphic subtrees), keeps the projection onto the moved B, provided
no special orbit changes tier. Anchors: the top region, v (B's member at level k + s), and the bottom-band special orbits; their
levels must not change. On the tree spanned by the anchors, keep each edge's total length and move length (in multiples of Q) into one
segment per edge; push each branch point of the anchor tree upward (shorten the edge above it, lengthen each edge below it by the same
multiple of Q) until the edge above it is short. Result: a bond of the same size meeting levels k and k + s whose members all lie within
K(c) blocks of the top region, of v's orbit, or of a bottom-band orbit. Note the third end: a member near the bottom joined by a long
path cannot be moved without changing its tier.

Part 2: a dichotomy, as READ-RULE-20261114-001 proved for nested families: on each depth tier r = N - k - s (r < r0 separately, r >= r0
as one tier) and each residue of s modulo Q, L is eventually bounded or L >= s / (K' ) - const (linear). Proof: if a least bond at (s, N)
has a member-free stretch longer than T + Q on the path from the top to v, pump it by Q (s and N both + Q, r unchanged), so
L(s + Q) <= L(s); otherwise every stretch is short and |B| >= s / (T + Q + 1) - 1.

Corollaries I intend: "L <= c at every depth" is decidable for each c (a finite-state check over normal-form bonds); boundedness is
semi-decidable; nothing grows between bounded and linear.

Part 3 (computation, settle 13 patterns). They read L = 3, 4, 5, 5, 6, 6 for s = 1..6 (exact), and at depth 12 no bond of at most 6 at
s = 7, 8 (certified). Their bonds at s = 5, 6 lie in the top orbit, the lower orbit's two ancestors just below the top, and the lower
orbit; bonds of that shape (and with three ancestors) give nothing of at most 8 from s = 7. A run is checking for a bond of at most 7 at
s = 7, 8 (depth 12); a depth-13 run checks no bond of at most 6. Predictions I plan: a bond of 7 exists at s = 7, 8; it uses an orbit off
the line from the top orbit to v (your sibling or side-child shape); the 13 grow linearly (about one member per two levels), but this
epic will not prove it.

Questions: (a) Is part 1's anchor argument right, in particular pushing branch points upward, and members in subtrees that hang off the
anchor tree with no anchor? Is the third end (bottom band) genuinely needed, or can it be removed by an argument I am missing (for
example, reading the bottom band's effect as a relation on an orbit just above it)? (b) Is part 2 correct with two parameters (s, N)
pumped together, and does it need part 1 at all? (c) Is the decidability claim honest, given the constants? (d) Any prediction you would
change, or a cheaper discriminating computation for the 13?
