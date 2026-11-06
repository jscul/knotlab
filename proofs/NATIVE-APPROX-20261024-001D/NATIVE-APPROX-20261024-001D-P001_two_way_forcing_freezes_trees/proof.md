# Two-way forcing freezes native trees

Status: Proved

Ticket `NATIVE-APPROX-20261024-001D`, 2026-10-24.

**What it uses:**
- the knot axioms as used throughout the program: no two excluded tuples of a knot are adjacent (K2), and every pair of places of a
  knot takes all four values;
- from `NATIVE-APPROX-20261024-001A-P001`: the knots excluding three tuples are a parity class minus one tuple; six of them are the
  open knots;
- from `NATIVE-APPROX-20261024-001C-E001` (refuted): the observation explained here, used only in a consistency check;
- background, cited: Weitz's correlation-decay method (2006), whose hypothesis is decay uniform over boundary conditions (strong
  spatial mixing).

## Standard statement

**Setting.**
- **Native trees.** A native tree of a knot R without pins has knots joined by edges into a tree.
  - One edge, the *root edge*, has a free end. Every other free end is a *boundary leaf*.
  - Every knot has its *parent edge*, towards the root edge, at one place, and two *child places*.
- **Width.** Boundary values give every leaf a value. The *root marginal* is the fraction of consistent assignments in which the root
  edge is 1. The *width* of a tree is the largest minus the smallest root marginal over all boundary values.
- **One-way and two-way places.** A place s of R is *two-way* when the excluded tuples of R take both values at s. Otherwise it is
  *one-way*: all excluded tuples take one value u there.
- **Two-way forcing.** R is *two-way forcing* when all three of its places are two-way.

**Theorem 1 (freezing).**
- **(a)** Let R be two-way forcing. On every native tree of R without pins, and for each value v, some boundary values force the root
  edge to v: every consistent assignment has the root edge equal to v, and one exists. So every such tree has width 1.
- **(b)** Let s be a one-way place of R, with value u. On every native tree whose root edge sits at place s of the root knot, every
  boundary, hard or soft, gives P(root edge = u) ≤ 1/2. So such trees have width at most 1/2, at every depth.
- **So** R freezes every native tree without pins exactly when it is two-way forcing.

**Proposition 2 (census).** Exactly 14 of the 34 knots are two-way forcing:
- the four knots excluding an antipodal pair (not-all-equal and its relabellings);
- the eight knots excluding three tuples: the six open knots and the two no-lone-value knots;
- the two parity knots.

The other 20 have a one-way place:
- the eight single clauses, where every place is one-way;
- the twelve knots excluding a pair at distance two, at the place where the pair agrees.

**Corollary 3 (decay uniform over pins fails).**
- **The networks.** Pinning the boundary leaves turns a native tree into a native network with pins. So for each two-way forcing knot
  and every distance L there are native networks in which pins at distance L from an edge decide that edge completely, either way.
- **What fails.** The influence of boundary pins does not decay with distance uniformly over the pins. It fails for all 14 knots,
  including the six open knots. Correlation-decay schemes that need this decay, such as Weitz's method, do not apply to them in their
  standard form.
- **Not a hardness signal.** The 14 knots include not-all-equal, which has an approximation scheme by winding (given McQuillan), and
  the parity and no-lone-value knots, which count exactly.

**Corollary 4 (the refutation of ticket C).**
- **The prediction could not hold.** Ticket C predicted decay for the six open knots on native trees, from a probe that used only the
  boundaries all 0, all 1 and all free. Theorem 1(a) shows that without pins every tree has width 1.
- **The controls line up with the census.** The controls that persisted in ticket C are two-way forcing. The ones that decayed have a
  one-way place.

**Reading.**
- **Freezing does not separate the six.** It marks 14 knots, and the six open knots are those among them that are neither windable
  nor topological. Since freezing is shared with knots that are easy to count, it is not what keeps them open.
- **Both standard routes stop at the six.**
  - Winding fails because they are not windable (ticket A).
  - Decay uniform over pins fails because they are two-way forcing (Theorem 1).
- **K2 used the other way round.** In ticket A, K2 bounded the weight near an excluded tuple. Here it makes an excluded tuple's
  neighbour across place s allowed, so the values of t at the other two places force place s.

## Nearest known result

- **The obstruction is classical.** Hard boundary conditions that determine the root of a tree are the standard obstruction to strong
  spatial mixing, for example for parity constraints and for proper colourings with few colours. Weitz's method needs strong spatial
  mixing.
- **The local content** is:
  - the exact form for knots: an equivalence, with the bound 1/2 at a one-way place;
  - the census of the 34 knots;
  - the explanation of ticket C's refutation.
- **Novelty:** elementary and new to the program; folklore risk high.

## Proof

### Theorem 1(a)

Induction on the tree, from the leaves upwards.
- **Leaves.** A boundary leaf can be given either value.
- **A knot.** Let a knot have its parent edge at place s. Suppose each child subtree can be forced to either value by values of its own
  leaves. Fix v.
  - Since s is two-way, some excluded tuple t has t_s = 1 − v.
  - Force the two children to the values of t at the other two places. The subtrees have disjoint leaves, so both can be forced
    together.
  - The tuple with 1 − v at s and these child values is t, which is excluded. So the parent edge cannot be 1 − v.
  - The tuple with v at s is adjacent to t, so it is allowed by K2. Combining consistent assignments of the two subtrees gives one with
    the parent edge equal to v.
- **The root.** The root edge is forced to v. ∎

### Theorem 1(b)

- **Allowed tuples.** All excluded tuples take the value u at s, so every tuple with 1 − u at s is allowed.
- **The root knot.** Under any boundary, let the two child subtrees give weights A_a and B_b to their edges taking values a and b.
  These are counts, or weighted counts for a soft boundary. Write Z_w for the weight with the root edge equal to w.
  - Every tuple with 1 − u at s is allowed, so Z₁₋ᵤ = Σ_{a,b} A_a B_b.
  - Z_u = Σ_{a,b} [the tuple with u at s and values a, b is allowed] A_a B_b, which is at most Z₁₋ᵤ.
- **Conclusion.** P(root edge = u) = Z_u / (Z_u + Z₁₋ᵤ) ≤ 1/2. The total is positive because every pair of child values extends to
  an allowed tuple. The root marginal stays on one side of 1/2, so the width is at most 1/2. ∎

### Proposition 2

- **One excluded tuple.** Every place takes a single value on it.
- **Two.** By K2 the excluded tuples are not adjacent, so they lie at distance two or three.
  - At distance two they agree at one place, which is one-way.
  - At distance three (an antipodal pair) they differ at every place.
- **Three.** The excluded set is a parity class minus one tuple (ticket A). In a parity class each place takes each value twice, so
  removing one tuple leaves both values at every place.
- **Four.** A parity class: both values at every place.
- **The count.** The 34 knots are 8 single clauses, 12 pairs at distance two, 4 antipodal pairs, 8 knots excluding three tuples and 2
  parity knots. So 4 + 8 + 2 = 14 are two-way forcing. ∎

### Corollaries 3 and 4

- **(3)** A native tree whose leaves are pinned is a native network with pins. Theorem 1(a) gives two pinnings at distance L with root
  marginals 0 and 1.
- **(4)** Theorem 1(a) applies to every tree that ticket C drew without pins. Ticket C's rows agree:
  - width 1 on every tree, at every depth from 4 to 16, for its 11 two-way forcing knots;
  - median width below 10⁻⁶ at depth 16 for its 3 controls with a one-way place. ∎

## Checks

`check.py` uses the standard library only (seed 20261024). It confirms:
- **Proposition 2** by enumeration:
  - 14 two-way forcing knots, in the three families;
  - 20 with a one-way place;
  - the six open knots among the 14.
- **The counting method.** Exact integer counts on trees equal brute-force enumeration on 204 random small trees with random boundaries.
- **Theorem 1(a).** On 2,100 random trees, irregular and up to depth 10, the construction forces the root edge to each value, by exact
  counts. Brute force confirms 1,826 of these 4,200 forcings, on the trees with at most seven knots.
- **Theorem 1(b).** At every one-way place, P(root edge = u) ≤ 1/2 on:
  - 11,904 hard boundaries, exhaustive on random trees up to depth 3;
  - 432 soft boundaries, with exact fractions, on trees up to depth 8.
- **Ticket C.** Its bound rows agree with Corollary 4.

**Controls.**
- **The construction can be refused.** It is refused at every one-way place for the forbidden value.
- **K2 is used.** For a relation that violates K2 but has three two-way places (excluding 000, 001, 110 and 111), the construction
  produces boundary values with no consistent assignment at all.

## What this does not show

- **Whether the six open knots can be approximated.** Freezing rules out one method, not every method: not-all-equal freezes and is
  approximable.
- **Decay for the 20 knots with a one-way place**, on all trees or with pins. Ticket C's random trees suggest it for three of them.
- **Trees with pins inside.** Theorem 1 is about trees without pins; ticket C measured decay at pin probability 0.2.
