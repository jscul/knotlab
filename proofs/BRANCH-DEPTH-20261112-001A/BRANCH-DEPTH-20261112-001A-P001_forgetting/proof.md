# A sufficient forgetting test, and what it cannot decide

## Standard statement

Consider a nonempty set of assignments to an infinite constraint system
decomposed along one specified recursive branch into successive groups.
Assume a fixed finite tuple of interface variables separates consecutive
groups, that all shared identities are represented there, and that each
unobserved group has the same exact binary relation `T` on interface values.
If a positive power `T^r` is the product of its two projections, every finite
minimal non-shattered set containing a variable owned at group 0 and one owned
at group `s` has at least `1+ceil(s/r)` members. This applies to arbitrary
finite supports, including off-branch variables and variables beyond `s`.

The converse and endpoint existence do not follow. Explicit NAE examples
below have the same nonforgetting port relation and respectively exact linear
growth or a three-member endpoint bond at every depth. Another example has a
full port relation and nontrivial knots, but no root endpoint bond.

## Nearest known result and local delta

Composition of finite relations by Boolean matrices is classical; see
[Chajda and Länger, *Compositions and decompositions of binary relations*](https://arxiv.org/abs/2111.06282).
The full-positive-power special case belongs to the classical primitive-matrix
theory of [Wielandt (1950)](https://link.springer.com/article/10.1007/BF02230720).
The separation argument is elementary existential elimination. No matrix or
separation theorem is claimed as field novelty, and no outside theorem is
needed in the proof: the composition, gluing, and finite-orbit arguments are
given here.

The accepted `BONDS-AND-COUNT-20261112-001E` proves the `r=3` full-power case
for one particular three-port branching rule. `NEST-COUNT-20261112-001A`
proves finite-state facts about the port relations, and supplies NAE
presentations of complement-closed Boolean relations. The present local delta
is the explicit arbitrary-support theorem for a merely rectangular power,
which need not cover all root tuples, and the controls separating this
sufficient test from a converse or an existence claim. Here *rectangular*
has its classical relation meaning, a product of two sets, not a spatial
meaning. Field-level novelty is unassessed; classification: known-with-delta.

## 1. Exact interface assumptions

Fix groups `B_0,B_1,...` on the specified branch. A group may contain a whole
infinite side subtree. Each individual variable has one introduction group;
the initial ports belong to group 0. Observing a carried variable prescribes
it once at that group, not again at every occurrence of its name.

Let the interface between `B_(i-1)` and `B_i` be a tuple with value in a fixed
finite set `Q`. Equalities caused by shared variable identity are part of the
interface semantics. A group has an incoming and outgoing tuple. For given
tuple values, its exact relation includes them iff its other variables can
be assigned, with all its side calls satisfied. Witnesses in distinct groups
can be combined whenever their interface assignments agree. In particular,
no further shared variable is hidden outside these tuples. Actual infinite
assignments exist. Their allowed incoming tuples at the root may be a proper
subset of `Q` and may include tuples never reachable farther down.

For every group with no selected variable introduced there, its relation is
the same `T subset Q x Q`. Prescriptions on variables introduced earlier are
still carried through the interface; they are not removed by calling a group
empty. These hypotheses, rather than clause incidence or a chosen order of
evaluation, are the scientific interface needed by the theorem.

Write `T^r` for exact existential composition of `r` copies of `T`. Suppose

```text
T^r = A x B,       A=dom(T^r), B=ran(T^r), r>=1.             (R)
```

Because an infinite state exists, this product is nonempty. Neither `A=B`
nor `A=B=Q` is required.

## 2. The arbitrary-support lower bound

**Splicing lemma.** Let groups `i,...,i+r-1` own no selected variable. Suppose
a finite support has selected variables on both sides. If both parts are
free separately, their union is free.

For any prescribed assignment to the union, take an infinite realizing
state `alpha` for the left part and `beta` for the right part. Their actual
trajectories through these `r` groups show that `alpha`'s incoming value lies
in `A` and `beta`'s outgoing value lies in `B`. By (R) those two particular
values can be connected. Keep the prefix of `alpha`, the suffix of `beta`,
and choose witnesses for the intervening groups. The exact interface
assumptions make these assignments compatible. No selected variable is
introduced in the intervening groups. Any selected identity that persists
through them is accounted for in their incoming and outgoing tuples. Thus
all observations hold together. This proves the lemma.

**Theorem 1.** If a bond contains an endpoint introduced at group 0 and another
introduced at group `s`, its size is at least `1+ceil(s/r)`.

A bond cannot have `r` consecutive empty groups strictly between occupied
groups: the splicing lemma would combine arbitrary assignments on its two
nonempty proper parts, making the whole support free. List occupied group
indices from 0 through `s`. Successive differences are at most `r`; therefore
at least `1+ceil(s/r)` groups are occupied. Each owns at least one distinct
selected variable. Variables selected beyond `s`, or arbitrarily deep inside
a side call, do not evade this proof: they remain in the right-hand part of
the splice or in their unique introducing group. This is a uniform lower
bound over every finite support, not a bounded-window result.

The theorem is conditional on a bond existing. In the general minimal
non-shattered-set terminology it also covers constrained singletons and
two-variable ties; neither is automatically a canonical logical knot.

**Smaller hypothesis for a particular cut.** It is enough that `T^r` contain
every pair consisting of an incoming value of an actual infinite state and
an outgoing value of an actual infinite state at that cut. This condition is
exactly what is needed to splice their fixed boundary values. It may be
weaker than (R), for example after unreachable interface states are removed.
It is a criterion for this splicing operation, not a necessary condition for
growth of bonds. The examples below disprove the latter inference.

## 3. A finite recognition bound

If `|Q|=N`, there are `2^(N*N)` binary relations on it. The sequence
`T,T^2,...` is obtained by repeatedly composing on the right with `T`.
If a relation repeats, all later powers repeat the same finite cycle.
Consequently, if any positive power is a nonempty product of its projections,
the first such power is at most `2^(N*N)`. Enumerating until the first
repetition decides this sufficient criterion. It also records whether and
when a power is the full `Q x Q`; the two answers need not agree.

For example, on three states take `0->1`, `1->2`, `2->2`. Its second power is
`{0,1,2} x {2}`, whereas no power is full on all three states. Infinite
continuations exist from each root state, but only state 2 is seen after
two groups. This is a positive control for using the two actual projections
instead of requiring every root tuple to remain reachable. The finite-orbit
bound is deliberately coarse and classical; it is not a new primitive-matrix
exponent bound.

## 4. An additional sufficient upper certificate

Fix an incoming slot `j`, an outgoing slot `l` that is a fresh own variable
of this group, and a distinct helper `v` introduced inside this group (possibly
in a side call, but not an incoming port). For **every admissible
full incoming tuple** `p`, require the exact table of `(out_l,v)` to be
`{(b,c): R(p_j,b,c)}`, where the same complement-closed three-variable
K1--K3 relation `R` works for all `p`. Outgoing tuples in this table must
be admissible for the continuing branch. Call this a genuine link `j->l`.
It supplies lifting for every full incoming tuple, not just after the other
ports are quantified away. Spectator ports may carry old helpers, but cannot
invalidate that premise. The fresh output and new distinct helper cannot
alias an earlier selected variable.

A neutral carry `j->l` means the outgoing variable in slot `l` is literally
the incoming variable in slot `j`, and every admissible input tuple has at
least one admissible exit. It observes no helper and adds no new relation.
The starting root bit must be free; this holds for every coordinate of a
nonempty complement-closed root relation, but is not automatic for an
arbitrary root restriction.

**Composition lemma.** Two complement-closed Boolean K1--K3 relations sharing
exactly one variable compose, after that variable is quantified away, to
another such relation. Each forces the shared bit on some assignment to its
other variables: otherwise its whole relation would be full. Its projection
on those other variables is full, so forcing never means no allowed value.
Complement closure supplies forcing assignments for both values. Choose
incompatible forced values from the two relations to prove binding. For
erasure, omit a variable on either side, prescribe all remaining bits, and
choose a shared value allowed by the opposite side. K2 on the erased side
supplies the missing bit for that value. Coexistence follows likewise, and
complement closure is preserved. Three-variable inputs yield at least four
variables; this does not assert a lower-arity knot.

**Upper certificate.** Suppose the finite directed choices of uniform links
and neutral carries contain a cycle with at least one genuine link. If any
root port may be the starting endpoint, then at every site `s>=0` a bond
contains a root port and a fresh own variable at that site and has size at
most `s+3`.

For each `s`, rotate the cycle's starting slot so the step at site `s` is
genuine. Follow its choices from site 0 to `s`. Compress neutral carries,
which keep the same physical identity. With `h` genuine links, observe the
starting bit, one helper per link, and the last fresh output: `h+2<=s+3`
variables. Consecutive relations share only the carried bit; the composition
lemma makes their projected chain a knot. Its projection is exact: choose
an admissible root tuple with the prescribed starting bit, lift each link
for the full tuple actually reached, choose an exit at each carry, and
extend the admissible last tuple to the infinite remainder. This realizes
every chain-allowed pattern. Every actual state satisfies the link relations,
giving the reverse inclusion. Helpers in side calls beyond the target depth
are permitted by the support convention.

Rotation uses the choice of **any** starting root port. With a fixed starting
port the argument only covers reachable target phases, absent a separate
phase-adjustment argument. A carry-only cycle supplies no fresh target.
Combining this upper certificate with Theorem 1 proves linear growth when
both tests hold. The exact marked local tables supply information absent
from `T` alone; the statement is not a general converse.

## 5. Controls in the NAE recursive language

Every call below has three distinct ports, fresh own variables, one specified
recursive child, and no pass-through of all original ports. Thus its usual
limit has the same local constraints as its bottomless pattern. Extra fresh
ports used only to keep arity three are independent and cannot lie in a bond.
Every root triple extends; this can be checked constructively in each case.

### 5.1 Forgetting, with exact growing endpoint bonds

Let `D(q,t,v)` introduce `q',t',v',z`, constrain `NAE(q,q',z)`, and call
`D(q',t',v')`. Its unobserved relation is full on three-bit ports, so `r=1`.
After ignoring unused free ports, its variables are `q_0,q_1,...` and
`z_0,z_1,...`, with `NAE(q_i,q_(i+1),z_i)` for every `i>=0`.

For every `s>=0` the least bond containing `q_0` and either prescribed own
target `z_s` or `q_(s+1)` has exactly `s+3` members. The support

```text
{q_0,z_0,...,z_s,q_(s+1)}                                  (C_s)
```

attains that size. Eliminating the internal `q` variables in this chain of
NAE triples excludes exactly two complementary words, by the accepted
chain argument; direct enumeration below independently replays it. Each
single deletion is full, so K1--K3 hold.

For the lower bound, if `z_i` is unobserved at any `i<s` (or at `i<=s` for
target `q_(s+1)`), existentially choosing that leaf makes `q_i,q_(i+1)`
independent. The full system then factors into a part containing `q_0` and
one containing the target. Minimality of a bond is impossible across such
a product. Thus `z_0,...,z_s` and `q_0` are mandatory. These `s+2` variables
alone are free: choose successive `q` values forward to meet each observed
`z_i`. At least one more variable is needed, and (C_s) supplies it. Extra
observations farther along cannot improve this argument.

### 5.2 Nonforgetting, with the same exact growth

Let `D(h,q,t)` introduce `q',t',z`, constrain `NAE(q,q',z)`, and call
`D(h,q',t')`. Its exact port relation is

```text
T((h,q,t),(H,Q,V)) iff H=h.                                (H)
```

Every power remains (H), which is not rectangular. The variable `h` is one
shared identity, unused in every constraint. The rest is exactly the chain
above, so its endpoint minimum is still `s+3`. No bond can contain `h`: since
it is an independent free variable, deleting it preserves any constraint on
the rest. Thus nonforgetting can hide an irrelevant persistent port while
the other component has genuine growing endpoint bonds.

### 5.3 The identical nonforgetting relation, with bounded bonds

Instead constrain `NAE(h,u,z)` with fresh `u,z` at each call, and again call
`D(h,q',t')` on fresh `q',t'`. The unobserved port relation is exactly the
same (H). But `{h,u_s,z_s}` is a three-member bond at every depth: its
projection is precisely NAE, while every pair is free. Every other copy
extends independently for the prescribed `h`. This proves that (H) alone
cannot distinguish exact linear growth from uniformly bounded endpoint bonds.

### 5.4 Forgetting and nontrivial knots, but no endpoint bond

Let `D(q,t,v)` introduce six fresh variables `q',t',v',u,w,z`, constrain
`NAE(u,w,z)`, and call `D(q',t',v')`. Its port relation is full, exactly as
in 5.1. Each group contains a three-member knot, but the root ports are
independent of every constraint in the infinite system. Any constrained
support containing one has a constrained proper part after that port is
deleted. There is therefore no bond connecting a root port to a deep own
variable. Forgetting supplies a lower bound when a bond exists, not existence.

## 6. A positive certificate and two obstructions to misusing it

**Theorem 2 (free interfaces).** Let `U,V` be finite sets of actual variables.
If each is free but `U union V` is constrained, it contains a bond of size
at most `|U union V|` with a variable in `U\V` and one in `V\U`.

Choose an inclusion-minimal constrained subset of their finite union. It is
a bond. It cannot be contained in either free set, giving the two claimed
exclusive endpoints. This proves the theorem. It does not require `U,V` to
be disjoint, and does not create duplicate variables for a carried identity.
If the resulting support has fewer than three members, report a unary
constraint or a pair tie, not a canonical logical knot.

For fixed-width interfaces this is a bounded-size positive certificate.
Applying it at arbitrarily deep interfaces gives arbitrarily deep *port*
endpoint bonds only after the variable identities are checked. It gives an
own-variable endpoint at an exact depth only if that introduction depth is
known. Otherwise a bounded port-age lemma or an explicit relation to a fresh
local is still required. No such additional claim is assumed here.

**Carried identity control.** In (H), take input names `(h,q,t)` and output
names `(h,Q,V)`. The matrix is nonrectangular, but its projection onto the
five-variable physical union is full. Its missing matrix entries merely
assign the same identity two different values. Theorem 2 correctly rejects
this as a cross-bond certificate. Discarding that identity to make the matrix
full would also be unsound for the bounded example in 5.3.

**Internally constrained control.** Let `U` be four bits with every word except
`0000,1111`, and let `z` be another free bit. From their product remove only
`(0011,0)` and `(1100,1)`. This relation is complement-closed, and so has an
NAE-three-place presentation by the admitted NEST-COUNT P3b. Its binary
relation between the allowed `U` words and `z` is genuinely nonrectangular,
with disjoint physical identities. Nevertheless, every support containing
`z` and at most three bits of `U` is full: after omitting any root bit each
removed word has a retained alternative. The only bond is `U` itself. There
is no cross-bond. Thus genuine nonrectangular coupling still does not imply
a bond when the individual interfaces are not free. This is checked by
enumerating all subsets and all projection tables, not by a syntax test.

## 7. Checks, scope, and remaining question

`check.py --write` compares set-based and packed-bit composition over every
binary relation on at most three states, checks rectangular and full powers
separately, replays the accepted three-step example, and checks splicing and
the occupancy inequality on finite representatives. It computes the NAE
chain projections, tests all deletions, calls knotlab on arity-three-or-more
examples, and runs the public knotlab CLI. The positive certificate, physical
identity control, internally constrained control, and a separately labeled
pair-tie control can all fail their asserted tests. The complement-closed
composition lemma is checked on every pair of knots of arities three and
four; without complement closure two valid atoms compose to a full relation,
which is a matched negative control. A shift-register example checks cycle
rotation and neutral carries, and an averaged spectator table is rejected
when its per-input lifting fails.

The all-support theorem and exact all-depth control minima are hand proofs;
the finite checks do not supply their quantifiers. Validation: V1, separately
derived same-task finite algorithms and hand reasoning, without human or
external replication. Primary class: uniform-family-theorem; secondary:
exact-obstruction-or-countermodel. No new carrier, external authority,
finite-flip source, metric, or frequency result is supplied.

The declared implication and its converse/existence tests are settled at this
scope. A necessary-and-sufficient classification of endpoint behavior requires
more than the unobserved relation `T`: the examples show it must account for
actual variable identities, admissible internal projections, and how observed
locals depend on the ports. No general growth-or-bounded dichotomy is claimed.
