# Pumping along blocks: a normal form with three ends, a bounded-or-linear dichotomy, and a product test

`TWO-ENDS-20261117-001A-P001`, epic `TWO-ENDS-20261117-001`, 2026-11-17. Written by Claude. The advisor model checked the plan before
the freeze and proposed three repairs and the product test (`research/TWO-ENDS-20261117-001/advisor/plan_answer.md`). Proof by hand,
not machine-checked. *Refereed* (TWO-ENDS-R1, `research/TWO-ENDS-20261117-001/referee-R1/report.md`): confirmed with fixes, no
Block; Theorem N's step 3 repaired for clusters, the corollary marked a sketch, the carried mode given both parts. Checks: `check.py`, with its result in `result.json`. The method is pumping finite semigroup states along words,
as for regular languages and tree automata, and as `READ-RULE-20261114-001` did for nested families. What is new here is the setting:
addressed patterns of finite depth, where the depth tiers pin a third end.

## Setting

The setting is that of Theorems W, K and K\* (`DIRECT-REACH-20261115-001B`, `KEEP-REACH-20261117-001A`, `CARRIER-20261117-001A`):
- addressed not-all-equal patterns whose orbits have at most four addresses;
- finitely many orbit types, where an orbit's type fixes its children's types;
- an orbit's **block** (the orbit with its child orbits) holds all its knots, and blocks meet only a block and the one above it.

Write P_N for the pattern of levels 0 to N, F[r][t] for the assignments of a type-t orbit that extend r further levels, r₀ for the
depth from which F[r] is constant, and R = r₀ + 1. L_N(k, s) is the least bond of P_N with a member at level k and one at level
k + s, and r = N − k − s.

**Factorisation (Theorem W, CARRIER's Lemma P).** For a set B of addresses, let S be the set of orbits that hold a member of B or lie
above one (closed toward the root). The projection of P_N onto B is read from S alone:
- every orbit of S below level N satisfies its block, with each child orbit outside S only required to be in F at its remaining depth;
- every orbit of S at level N satisfies its own knots.

So the projection onto B is unchanged by any change of S that keeps every orbit's type, every child relation, and the remaining depth
of every orbit at which F is read below r₀.

## Lemma S (segments)

Call an orbit **saturated** when its level is at most N − R. Its children then have remaining depth at least r₀, and its step to a
child is a relation fixed by its type and the child: the child's assignment is related to the orbit's when the orbit's block allows
both, with every other child in F[r₀]. The **state** of a downward path of saturated orbits is
(first type, current type, composite of its steps).

*There are finitely many states, M. The set of states reached in exactly ℓ steps is ultimately periodic in ℓ, with threshold T and
period Q. So for two states p, q, the lengths of paths from p to q form a set Λ(p, q) with x ∈ Λ ⇔ x + Q ∈ Λ for every x ≥ T.*

*Proof.* Each composite is a relation between two sets of at most 16 assignments, and the types are finitely many. The set reached
in ℓ + 1 steps is a function of the set reached in ℓ steps, so the sequence of sets repeats from its first repeat. ∎

For the 13 mutants of 8db5da810c00 (5 distinct patterns) this is small: 8db5da810c00-73 has M = 88, T = 5, Q = 2 (`composite.json`).

## Segments and moves

Call an orbit of S **special** when it lies in the **top region** (level at most k), in the **bottom band** (level above N − R),
holds a member of B, or has at least two children in S. With |B| = c there are at most 2c − 1 special orbits outside the top region
and the band. A **segment** runs from a child of a special orbit, through orbits that are not special, to the next special orbit.
Its interior orbits are saturated.

*A move* replaces a segment by another path from the same child (advisor: so two segments leaving one branch point stay apart), with
the same end type and composite, and carries the part of S below the segment's end to the matching place below the new end. Same
type means the same subtree up to the depth. Its length can be any element of the segment's set Λ. By the factorisation, the
projection onto the carried B is unchanged as long as no orbit at which F is read changes tier. All moves below shift parts of S up,
or keep them, except new interior orbits. Those lie above an end that does not move. Moving an orbit up keeps it saturated.

## Theorem N (a normal form with three ends)

*Let B be a bond of P_N with at most c members, one at level k and one, v, at level k + s. Then P_N has a bond with as many members,
one at level k and one at level k + s, each member of which lies within K = 11c³(T + Q) + k + R blocks of:*
- *the top region;*
- *the orbit of the member at level k + s;*
- *or an orbit of the bottom band.*

*Proof.* The **anchors** are:
- the top region;
- v's orbit;
- the special orbits of the bottom band.

Their levels must not change. The anchor tree A is the union of the paths from the top region to the anchors. An **edge** of A runs
between two consecutive nodes that are anchors or branch points of A. Its segments are separated by special orbits whose other
branches hold no anchor.

1. **Off the anchor tree.** A segment whose subtree holds no anchor is shortened by a multiple of Q to a length below T + Q, when it
   is at least T + Q long. Its subtree moves up and stays saturated, since it holds no band orbit.
2. **Along each edge of A.** Shorten every segment of length at least T + Q to below T + Q, by multiples of Q. Lengthen the lowest
   such segment by the total. Then the edge's length is kept, and every point above the lowest long segment moves up while every point
   below it stays (advisor's repair: length passes only between segments at least T long). Afterwards each edge has at most one segment
   of length at least T + Q.
3. **Clusters of nodes of A, from the top down** (*repaired after the referee, TWO-ENDS-R1*). Call an edge of A **short** when all
   its segments are shorter than T. A **cluster** is a maximal set of nodes of A joined by short edges. It has at most 2c nodes, so its
   diameter is below 2c·2c·T.
   - **A cluster holding an anchor** does not move. Each of its nodes is within 4c²T blocks of that anchor.
   - **Any other cluster** C has every edge that leaves it downward holding a segment of length at least T. A short one would bring
     its lower node into C, and the leaves of A are anchors. If C's edge from above holds a segment of length at least T + Q, shorten
     that edge by a multiple of Q to below T + Q, and lengthen the lowest segment of length at least T on each edge leaving C downward
     by the same amount. Every anchor keeps its level, C moves up rigidly, and C ends within 2c(T + Q) blocks of the cluster above it.

   The first draft moved one branch point at a time. The referee showed that two branch points joined by a short edge, each with
   long edges below, could then each be "near" only the other, with no bound. Taken from the top down, every cluster is anchored or
   within 2c(T + Q) + 4c²T blocks of the cluster above it, and there are at most 2c clusters. So every node of A lies within
   2c(2c(T + Q) + 4c²T) ≤ 10c³(T + Q) blocks of an anchor, for c ≥ 2. The repaired step has not been re-refereed.
4. **The members.** A member on an edge of A lies on one side of the edge's only long segment, so it is within 2c(T + Q) blocks of an
   end of the edge. A member off A lies in a subtree whose segments are all short. With step 3, every member is within 10c³(T + Q) + 2c(T + Q) + k + R ≤ K
   blocks of an anchor.

Every move keeps types, child relations and tiers, so the carried set is a bond of P_N of the same size. It keeps a member at level k,
in the top region, which no move touches, and v's image at level k + s. ∎

*The third end.* A member in the bottom band joined to the rest by a long path cannot move: its tier would change. Neither the advisor
nor this proof removes it. L is not monotone in N either: a bond of P_N stays constrained in P_{N+1}, but its least sub-bond may miss
a level.

## Theorem D (bounded or linear, for each depth tier)

*Fix r ≥ 0 and a residue ρ modulo Q, and let f(s) = L_{k+s+r}(k, s) for s ≡ ρ, W = T + Q + 1, and n(s) = min(s − 1, s + r − R).
Either f is eventually constant, or f(s) ≥ (⌊n(s)/W⌋ + 3)/2 for every s ≡ ρ.*

*Proof.* Take a least bond B at (s, N), with N = k + s + r. Suppose W consecutive levels strictly between k and k + s, all saturated,
hold no special orbit (advisor: pump a window of levels, not one segment).
1. Every orbit of S at those levels lies on a segment crossing the whole window, and these crossings are disjoint paths.
2. Lengthen each crossing by Q. This is allowed, since each is longer than T.
3. Everything below the window moves down by Q, and N grows by Q, so every tier below is kept. Everything above stays saturated: the
   window is at least R levels above the bottom.

So f(s + Q) ≤ f(s).

Otherwise the special orbits meet every run of W of the n(s) levels. They number at most 2|B| − 3: at most |B| − 2 members strictly
between the two levels, and at most |B| − 1 branch points. So |B| ≥ (⌊n(s)/W⌋ + 3)/2.

Suppose f(s₁) < (⌊n(s₁)/W⌋ + 3)/2 for some s₁. Then a window exists at s₁, so f(s₁ + Q) ≤ f(s₁). The bound grows with s, so the same
holds at s₁ + Q and onward, and f is non-increasing from s₁ along the residue, hence eventually constant. ∎

So nothing grows between bounded and linear, on each depth tier and residue, as s grows. Boundedness over every (s, N) also
involves N growing at fixed s, which Lemma R treats separately. The theorem does not need Theorem N (advisor).

## Lemma R (depth)

*If L_N(k, s) = c and r ≥ R + (2c − 1)W + W, then L_{N+Q}(k, s) ≤ c.*

*Proof.* At most 2c − 1 special orbits lie strictly between level k + s and the band. So some W consecutive saturated levels there
hold none. Lengthen the crossings as in Theorem D. Level k + s stays, and N grows by Q. ∎

## Corollary (decidable in principle; proof sketch)

*For each c, whether L_N(k, s) ≤ c for every s ≥ 1 and N ≥ k + s is decidable (a sketch: the reduction below is outlined, not
carried out).*

*Proof sketch.* By Theorem N, it is enough to consider bonds whose members lie within K of the three ends. Between the ends run long
paths whose states lie in the periodic part of Lemma S. Whether such a bond exists then depends only on:
- the clusters at the ends, finitely many up to type;
- the residues of the path lengths modulo Q;
- the tiers, which Lemma R reduces to finitely many.

Each case is a finite computation. ∎

No feasible bound is claimed in general: M can be as large as the number of types times 2^256. Boundedness itself is
semi-decidable, by searching for a c that passes.

## Theorem G (the product test)

*Suppose every saturated composite of exactly ℓ₀ steps is a product: every pairing of its two projections occurs. Then
L_N(k, s) ≥ (⌊n/ℓ₀⌋ + 3)/2 with n = min(s − 1, s + r − R), at every depth.*

*Proof.* A product composed with any relation is a product, so every longer composite is one too. If ℓ₀ consecutive saturated levels
strictly between k and k + s hold no special orbit of a bond B, then the crossings are disjoint paths with product composites. The
projection onto B then factorises:
- the part above the window, with u;
- the part below, with v.

Both parts are proper subsets of B, hence free, so B would be free. So the special orbits meet every run of ℓ₀ of the n levels, and
the count is that of Theorem D. ∎

**Computed** (`run_composite.py`, `composite.json`):
- On the census's 786 small-orbit descriptions alive at every depth, the product test holds for exactly the 740 that forget (139 distinct patterns of the 181). Each
  passes it with ℓ₀ at most its forgetting length plus 1, so Theorem G reproves their growth, at a lower rate than Theorem F's
  1 + ⌈s/r⌉. The 46 that
  never forget (42 patterns) all fail it.
- It fails for all 25 open descriptions of KEEP-REACH (10 patterns). For the 13 mutants of 8db5da810c00 (5 patterns) the reason
  is one non-product composite (8db5da810c00-73: 2 of 43 periodic states, one per parity), along an orbit type whose children are
  both of its own type. It has two parts (narrowed after the referee, TWO-ENDS-R1, by SAT at depth 11):
  - **the all-equal link:** an all-equal upper orbit forces the lower orbit all equal, alternating with each step;
  - **the split link:** a split lower orbit (0011 or 1100) forces the upper orbit to be split.

  Every other composite on the periodic part is a product.
- A bond across a long stretch must use that mode *(superseded by `MODE-BOND-20261117-001`: the mode lies in components that
  never meet level 3, so no bond meeting level 3 crosses a long stretch; the 13 grow linearly)*. Stems of depth 0 to 2 hold no bond of any size at s = 7 and 8 at depth 12.
- The least bonds found at s = 7 and 8 avoid it. For the pattern of 8db5da810c00-73 and -79 (one pattern) at depth 12 they have 7 members (certified), all on the
  lower member's line of orbits, which never enters the self-similar type, with gaps of at most two levels.

## Dependencies

- `DIRECT-REACH-20261115-001B`: Theorem W, the tree of blocks and the factorisation.
- `CARRIER-20261117-001A`: Lemma P and Theorem K\*.
- `READ-RULE-20261114-001A`: the pumping dichotomy for nested families, the model for Theorem D.
