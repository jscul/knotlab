# A branching limit-only family with least bond size three at every depth

**Standard statement.** Take the labelled one-definition member at accepted
LIMIT-ONLY sample 2, line 25697, with first-SELF branch fixed as below. For
each integer s>=1, minimize the size of a bond over all three top ports, both
fresh own distinctions of the depth-s copy on that branch, and **every finite
support in the entire infinite pattern**, including side copies and levels
beyond s. The resulting minimum is exactly three for every s.

**Nearest known result.** Accepted BONDS-AND-COUNT leaf E proves bounds growing
linearly in s for this same endpoint/support convention in sample 5, line
11064. Its first-SELF map is (a,b,c)->(c,a,x), which forgets its incoming port
values after three unobserved copies. The present member has a different
first-SELF map and a retained top port in its local NAE at every depth. The
argument below is a direct exact projection, not a general classification or
a field-level novelty claim.

## Exact input and limit

The first member is exactly:

```text
D(a,b,c): own x,y
    D(x,a,c)       [first SELF: selected branch]
    D(y,c,b)
    D(b,y,x)
    NAE(a,c,y)
```

The source is
`artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only/sample_2.jsonl.gz:25697`.
There are three recursive children, each using distinct arguments. None passes
through all three original ports. The usual limit therefore agrees with the
bottomless semantics by the accepted NEST-COUNT result. This condition is
checked directly rather than inferred from the raw `limit_only` flag.

The exact greatest fixed point on ports is TOP, all eight triples. Indeed,
for arbitrary incoming a,b,c, choose y=1-a and x arbitrarily. The local NAE
holds, and all three child port triples are in TOP. Thus the one-step image of
TOP is TOP; since no larger relation exists, it is the greatest fixed point.
Repeating this rule provides an infinite extension of every port triple.
The finite family uses NAE on unexpanded calls instead; direct exact port
iteration first yields the empty relation at depth four and then remains
empty. The member is consequently genuinely limit-only under the admitted
usual-limit semantics.

Write x_i,y_i for the two own distinctions of the first-branch copy C_i,
with the root C_0. Its ports are

```text
C_0: (a,b,c)
C_1: (x_0,a,c)
C_i: (x_{i-1},x_{i-2},c)   for i>=2.
```

The exact constraints on any first-branch initial segment through C_s are

```text
NAE(a,c,y_0),
NAE(x_{i-1},c,y_i)   for 1<=i<=s.
```

All other recursive calls have the exact TOP port summary. This is not free
truncation: TOP was just proved to be the exact summary. Every legal
assignment on the displayed segment extends to the whole pattern. Fill each
off-branch subtree independently from its already assigned port triple, and
extend the first-branch tail by the same TOP rule. Different subtree interiors
are fresh and share only the supplied names.

## A three-member bond at every depth

For each s>=1 select

\[
W_s=\{c,x_{s-1},y_s\}.
\]

These three identities are distinct, and y_s is a fresh own distinction of
the required depth-s copy. Their exact relation is NAE. One inclusion follows
from the local constraint at C_s. Conversely, prescribe any nonconstant
triple on these three variables. Choose a arbitrarily and y_0=1-a. For every
other ray level i, choose y_i=1-c, with unused x_i arbitrary. The prescribed
x_{s-1} appears in the displayed ray constraints only at C_s, so these choices
cause no conflict. All displayed constraints hold and the exact TOP summaries
extend this assignment to the entire pattern.

In order (c,x_{s-1},y_s), the allowed table is therefore exactly
`001,010,011,100,101,110`. It is nonempty and non-full; every one-variable
deletion gives the full two-variable table. Thus W_s satisfies K1, K2 and K3
and is a bond of size three. This proves the uniform upper bound without
restricting the support available to the minimization.

## Every eligible pair is free: the unrestricted lower bound

In fact any prescribed triple of top-port values and any prescribed value
of either x_s or y_s has an extension for s>=1.

- To prescribe x_s, take y_0=1-a and y_i=1-c at every positive displayed
  level. All x_i other than the prescribed x_s are arbitrary. Every local
  NAE is satisfied.
- To prescribe y_s, take y_0=1-a, y_i=1-c for 1<=i<s, and
  x_{s-1}=1-c. That last choice makes the constraint at C_s hold for either
  prescribed y_s. Choose the remaining x_i arbitrarily.

Again the unexpanded calls extend by their exact TOP relation. Therefore all
six eligible two-member endpoint supports are full, at every positive depth.
No such pair is a bond. Any support containing both distinct endpoints has
at least two members; a support with two members would have to be that pair.
Consequently no arbitrary off-branch or deeper choice can yield size two.
Together with W_s this proves the **exact unrestricted aggregate minimum
L(s)=3 for all s>=1**. This does not claim to compute every individual
endpoint-pair minimum.

## Retaining a port alone is insufficient

A second actual genuinely limit-only member, from the same accepted sample
file at line 16375, supplies a matched control:

```text
E(a,b,c): own x,y
    E(x,y,c)       [first SELF]
    E(b,x,c)
    E(b,y,c)
    NAE(a,y,x)
    E(b,a,x)
```

Its exact greatest fixed point is also TOP: choose y=1-a and x freely. No
SELF passes through all three original ports. Its finite NAE-capped family
first dies at depth four. Along its first branch the same top c is retained
in the third port at every depth, so its raw port transfer is never a full
relation between arbitrary incoming and outgoing port triples.

Nevertheless the third port occurs in no local NAE, and every child call
either retains it only in the third slot or omits it. Induction over every
finite call address proves that the original top c occurs in **no actual NAE
constraint anywhere**. Flipping it alone preserves every allowed state.
For a finite support containing c, its projection is the Cartesian product
of the full c bit with its projection after c is forgotten. If it is full,
K1 fails; if it is non-full, the non-full relation remains after forgetting
c and K2 fails. Hence **no bond can contain this retained top c**. This is a
specific-port control, not a claim about that family's aggregate minimum
over its other two top ports.

## K1-K3 and finite changes are separate

The all-depth bond result concerns exact projections of allowed states.
It does not imply that these bonds are native at every infinite solution.
There is an explicit negative control. In the main family, set c=1 and set
all other ray variables to zero. Each displayed NAE is (0,1,0), so this ray
assignment extends to the entire pattern through the exact TOP summaries.
For every positive i the constraint involving c has private pair
{x_{i-1},y_i}, both zero. These pairs are disjoint. Any state differing from
this one with c changed to zero must change at least one member of each of
infinitely many disjoint pairs. No change of finitely many variables can
flip c there. Thus the K1-K3 bond verdict supplies no universal finite-flip
source assertion. The checker validates finite prefixes of this obstruction;
the infinitary conclusion is the disjoint-pair argument.

In the control family, by contrast, the retained top c can always be flipped
alone because it occurs in no constraint, yet belongs to no bond. Retention,
the relational bond verdict and the finite-change source condition therefore
remain distinct. No native-at-infinity positive claim is made.

## Validation and scope

Run `.venv/bin/python -B proofs/BRANCH-DEPTH-20261112-001B/BRANCH-DEPTH-20261112-001B-P001_bounded_depth/check.py`.
The checker binds the immutable corpus rows, computes both greatest fixed
points and complete finite-depth orbits, and reconstructs the actual first
SELF substitutions. Scalar enumeration through depth four checks the exact
NAE projections, single-deletion tables and the full projection on all three
top ports plus either own target. SAT checks the same surfaces through depth
twelve. Canonical knotlab CLI checks W_s at depths one, two, five and twelve,
with a full-relation negative control. The checker also tests the ignored-port
argument on every literal/call, and checks the finite private-change lower
bounds for the frozen-c source control.

Validation is V1: the symbolic proof and the checker use separate arguments
inside the same task, with scalar enumeration, SAT and the maintained knotlab
checker as controls. The all-depth theorem rests on the explicit extension
and pair-freedom proofs, not an extrapolation of the tested depths.

This gives two contrasting fixed first-branch behaviours among actual
genuinely limit-only members: the accepted previous family's minimum grows
linearly, while this member's minimum is constantly three. There is no
frequency, typicality, arithmetic-counting, field-novelty, physical or
native-at-an-infinite-solution inference.
