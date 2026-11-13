# Base 16: an exact downward family and the unrestricted gap

## Standard statement

Work on the already admitted base 16, in its sheared presentation: distinctions
are indexed by `(x,r) in Z^2`, and every translate of
`{(0,0),(0,1),(1,0)}` and `{(0,0),(0,2),(1,2)}` is constrained to be
not-all-equal. The indices present the supplied meeting pattern; they do not
define its bond distance. A finite support is free when every assignment to it
extends to an allowed state of the entire infinite base. A bond is a finite
support that is constrained, with every proper part free.

**Status: Partial for the assigned sharp unrestricted lower bound.** The new uniform
result proved below is an exact relation on the entire downward construction,
for every across-count and every along-count `k >= 2`. The sharp unrestricted lower
bound, allowing arbitrary support at arbitrary along-counts, remains open.

For `n >= 3`, put `y=-n`, `ell=floor((n-1)/2)`, and let

```text
D(n,k) = {(0,0)}
         union {(1,-2i): 0 <= i < ell}
         union {(0,y),(0,y+1)}                 if n is even,

D(n,k) = {(0,0)}
         union {(1,-2i): 0 <= i < ell}
         union {(0,y),(0,y+2)}                 if n is odd,

         with {(k,y)} added in either case.
```

All unions above have distinct members when `k >= 2`.

**Theorem 1 (exact downward relation).** For every `n >= 3` and `k >= 2`,
`D(n,k)` has `floor((n+1)/2)+3` members and is a bond of the *infinite* base.
In flip values `p_x(r)=c_x(r)+x mod 2`, its projection excludes exactly two
complementary assignments. They are described in Section 3. Every other
assignment has an explicit infinite extension using only two updates of the
flip values. Thus the least bond distance from `(0,0)` to `(k,-n)` is at most
`floor((n+1)/2)+2`. The theorem does not claim this upper bound is least.

**Theorem 2 (exact finite restriction).** Every assignment of allowed states on
an open rectangle whose across-count interval contains at least three rows
extends to an allowed state on the infinite base. Consequently, its induced
constraints decide the exact projection on any support it contains. This
lemma also applies to arbitrary mixed-along-count supports, but by itself
provides no bound on the size of their least bond.

## Nearest known result and actual change of scope

The accepted `ACROSS-FOLD-20261112-001A-P001` proves the upward heddles for every
positive across-count, and an optimality theorem when all supporting
distinctions but the far one have one along-count. Its downward family was
checked only at across-counts `-3` through `-10` and along-counts `5,8,11,20`.
Theorem 1 proves that whole family, determines its full allowed-state relation,
and lowers the uniform along-count threshold to 2. It supplies no smaller
bond and no proof of optimality among unrestricted supports.

Theorem 2 is a direct extension argument for this law. The lead suggested its
three-row folding form; this proof checks both ends and derives it from the
local constraints. Independently, this worker implemented the weaker
backward-closed finite-predecessor extension in Section 5. Neither adds a
primitive or an external theorem. External novelty is unassessed: these are
local mathematical results, with the usual finite-memory presentation of a
constraint system as background. There was no new outside evidence admission.

## 1. The flip-value rule

The accepted column rule says that consecutive columns `c,d` are allowed iff
`c(r)=c(r+1)` implies `d(r)!=c(r)`, and `c(r-2)=c(r)` implies `d(r)!=c(r)`.
After the coordinatewise bijection `p_x(r)=c_x(r)+x mod 2`, this is

```text
p_x(r)=p_x(r+1)  => p_(x+1)(r)=p_x(r),
p_x(r)=p_x(r-2)  => p_(x+1)(r)=p_x(r).
```

Equivalently, row `r` may change only when both of its supporting rows `r+1`
and `r-2` have the opposite value before the update. Arbitrary such changes
may occur together, because each condition refers only to the preceding
column. Keeping every value is always allowed. The flip-value bijection
preserves the free-set and K1--K3 verdicts; it is not a new law.

## 2. Exact restriction to a finite across-count interval

Fix `[a,b]` with `b-a >= 2`. For every integer `r`, define

```text
h(r) = r                                      if a <= r <= b,
       the member of {a,a+1,a+2} congruent to r mod 3  if r < a,
       the member of {b-2,b-1,b} congruent to r mod 3  if r > b.
```

For every `r`, each of `h(r+1)` and `h(r-2)` is one of
`h(r)+1,h(r)-2` *that lies in `[a,b]`*. To check the joins explicitly:
at `r=a`, both images equal `a+1`; at `r=a-1`, both equal `a`; at
`r=a-2`, both equal `a+2`; at `r=b`, both equal `b-2`; at `r=b+1`, both
equal `b-1`; and at `r=b+2`, both equal `b`. In the remaining cases either
both rows are inside, or the three-row congruence rule gives the assertion.
For intervals of exactly three rows the same list applies, with overlapping
cases agreeing.

Let a finite run of columns on `[a,b]` satisfy every constraint wholly
inside that interval. Set `p_x(r)=p_x(h(r))` outside it. Each constraint of the
extended columns is an already satisfied constraint at `h(r)`: its supporting
row is one of the two admitted supporting rows just checked. Thus the run
extends across all rows. Keep its first whole column to the left and its last
whole column to the right. Those updates are allowed. This proves Theorem 2.

In particular, finite-rectangle SAT success **and failure** are exact for its
contained observations here, because of this extension proof. Merely obtaining
SAT success in an arbitrary finite window, or failure in a finite periodic
model, would not establish that conclusion.

## 3. The exact relation of the downward family

Use flip values throughout this section. Write

```text
a_i = p_0(-2i), 0 <= i <= ell,
d_i = p_1(-2i), 0 <= i < ell,
v   = p_0(y),
w   = p_0(y+1) if n is even, p_0(y+2) if n is odd,
t   = p_k(y).
```

Only `a_0`, the `d_i`, `v,w,t` are observed. The other `a_i` are witnesses.
The local constraint at row `-2i` says

```text
a_i = a_(i+1) => d_i = a_i.                    (P)
```

Given `a_0,d_0,...,d_(ell-1)`, the possible last values `a_ell` are:

* a singleton `{d_(ell-1)}` precisely if
  `a_0 != d_0` and `d_(i-1) != d_i` for every `1 <= i < ell`;
* both values otherwise.

Proof: while the current `a_i` is fixed and differs from `d_i`, (P) forces
`a_(i+1)=d_i`. If they agree, either next value is allowed. Once both values
are possible, they remain possible at every later step, since taking
`a_i=d_i` permits either next value. This proves the description by induction.

Call the singleton condition `F`, and its forced value `q`. The exact two
excluded assignments are

```text
F holds, q=v=w, and t=1-v.                     (E)
```

There are exactly two: `a_0` fixes the entire alternating list of `d_i`, then
`v=w=q` and `t=1-q`; the other assignment complements every bit.

### Necessity

Under (E), (P) forces `a_ell=v`. The three consecutive rows `y,y+1,y+2` of
column 0 therefore all have value `v`, in either parity of `n`. Each member
of this triple has an equal supporting member within the triple: the first
two use the row one above and the last uses the row two below. All three
keep value `v` in every later column by induction. Hence `t=1-v` is impossible.

### Sufficiency: an explicit extension for every other assignment

Choose a path `a_0,...,a_ell` satisfying (P). When `t!=v`, choose
`a_ell=1-v` if possible; if it is impossible, `a_ell=v` is forced and `w!=v`
because (E) does not hold. Thus, whenever `t!=v`, the bottom triple
`p_0(y),p_0(y+1),p_0(y+2)` is not monochromatic.

Fill column 0 with these `a_i` and the observed `v,w`. Whenever
`a_i!=d_i`, set `p_0(-2i+1)=d_i`. These extra rows are distinct and lie above
the bottom triple, so no prescribed assignment conflicts. Give every other
row the value `1-v`; in particular rows `y-1,y-2` have that value.

For the first update, set the observed rung rows to `d_i`. Every rung that
changes has both its supporting rows equal to `d_i`: row `-2i-2` by (P),
and row `-2i+1` by construction. Other rows may stay fixed. If `t=v`, keep
row `y` fixed forever, which is always allowed.

If `t!=v`, there are two cases:

1. If the middle row `y+1` already has value `1-v`, change row `y` in the
   first update. Its two supporting rows are `y+1,y-2`, both `1-v`.
2. Otherwise that middle row has value `v`, and the top row `y+2` has
   value `1-v`. Change the middle row in the first update, using supporting
   rows `y+2,y-1`, both `1-v`. Change row `y` in the second update, using
   rows `y+1,y-2`, now both `1-v`.

These changes do not meet any rung observation: the last rung lies at `y+4`
for even `n`, or `y+3` for odd `n`. Keep every other row fixed. Keep column
0 for all negative along-counts and column 2 for every along-count at least
2. This is an allowed state of the full infinite base, carries every observed
bit, and has the required `t` at every `k>=2`. This proves sufficiency.

### Bond, erasure, and both signs

The exact relation is nonempty and constrained, so K3 and K1 hold. Its two
excluded assignments complement every variable. After deleting any one
variable, each pattern on the remaining variables has two extensions and at
most one can be excluded, since the two excluded assignments disagree on
every retained variable. Therefore every deletion is full: K2 holds and
`D(n,k)` is a bond. The executable check supplies the exact finite relation
to `knotlab.check_knot`, with the far distinction as contact; it also invokes
the public `python -m knotlab check` command on a matched five-variable case.

Counting the support gives `floor((n+1)/2)+3` in both parities, proving
Theorem 1. Translation and swapping the two endpoints give the same upper
bound for `(0,0)` and `(-k,n)` for `k>=2`. The accepted upward heddles supply
the bound for `(k,n)` when `k>=floor((n+1)/2)+1`, and translation supplies
that bound for `(-k,-n)` in that range. These are upper bounds for least
bond distance. No reflection of the law is assumed.

## 4. Why the sharp unrestricted lower bound has not followed

The accepted core lemma describes observations at a *single* along-count.
For observations at several along-counts, two changes can place incompatible
requirements on an unobserved row. An empty pair of across-counts is therefore
not an automatic separator.

For example, in flip values the support

```text
{(0,0),(1,0),(0,3),(1,3)}
```

excludes exactly `0110` and its complement in the displayed order. The first
change `p_0(0)=0,p_1(0)=1` requires `p_0(1)=1`; the opposite change
`p_0(3)=1,p_1(3)=0` requires `p_0(1)=0`. They cannot coexist. Every other
pattern extends, as the exact rectangle computation checks. This is a
four-member bond despite having no observed row at across-count 1 or 2.
It refutes the naive empty-gap separation premise, not the desired lower
bound at far along-counts (its along-count difference is only one).

The mixed-support searches recorded in `result.json` have exact infinite-state
semantics by Theorem 2. They cover only their named finite boxes; absence of
a smaller bond there does not bound supports outside them. The accepted
upward and negative finite families are positive controls. The known
short-range four-member bonds at `(2,4)` ensure that a search for a smaller
bond can actually return one.

The completed general searches found no four-member bond joining `(0,0)` to
`(5,3)` with helpers in `[-1,6] x [-3,6]`, and no five-member bond joining it
to `(5,5)` with helpers in `[-1,6] x [-2,7]`. The latter tested 23,408 signed
prefixes and classified 1,036 candidate supports exactly. The short-range
control at `(2,4)` returned four four-member bonds. These are finite-box
outcomes, not a sharp unrestricted lower bound.

A second attack removed two helpers from the downward family and added one
at mixed along-counts, seeking to save one member. At `n=5,7`, `k=5,11`,
the extra helper included negative along-counts down to `-16`, both original
observation counts, and positive counts up to `32`; its across-count ranged
from `-n-2` to `3`. Of 4,314 distinct candidate supports, 4,182 were free
and 132 already had a constrained proper part; none was a smaller bond.
These counts sum the four independently declared finite cases in the result.

The simplest proposed serial composition of the opposed-change obstruction
also failed as a mechanism: after eliminating the event at across-count 3,
the two outer events at across-counts 0 and 6 are free. Exact checks of
`{(0,0),(1,0),(t,6),(t+1,6)}` give all 16 patterns for
`t=0,2,4,8,16,32`. A middle event may remain unchanged, which removes the
opposed-change restriction. This is a concrete rejected shortcut mechanism;
it does not exclude other mixed-time compositions.

**First remaining gap:** a sharp lower-bound invariant for a minimal constrained
support with observations at arbitrary along-counts, which survives the
opposed-change example and assumes no bounded range of supporting along-counts.
Neither the single-along-count core lemma nor exact finite extension proves
that invariant. The next mathematical discriminator is such an invariant or
a strict smaller bond in the far-along-count regime, with no restriction to
one supporting column. The new downward theorem resolves the unproved
construction arm, while leaving that main question partial.

## 5. Independent finite-predecessor encoding

For a finite support, start at its latest along-count and include all of each
output's three predecessor sites: `(x-1,r)`, `(x-1,r+1)`, `(x-1,r-2)`, stopping
at the earliest along-count of an observation. Encode both flip constraints
at each included output. Any satisfying assignment extends: choose all
unassigned values in the first column arbitrarily, and at each later column
keep every site outside this predecessor-closed set fixed from the preceding
column. Inside it, all predecessors are present and its constraints hold.
Keep entire columns before and after. This proves an exact projection by a
different finite restriction from Theorem 2. `Cone` implements this encoding;
`Rectangle` encodes the original NAE constraints and then changes signs.
Their relations are compared on the focused controls and mixed supports.

## 6. Infinite-source condition and safe conclusion

K1--K3 is established for these projected relations. Uniform native-source
status is **not** established. In fact, the state `p_x(r)=v` everywhere is an
allowed state and no variable in it changes under a finite change of the
whole infinite system. If a finite change existed, choose its least changed
along-count. Its preceding whole column is still uniformly `v`, so every row
is pinned and no change at that least column is legal, a contradiction.
Every variable is therefore end-supplied at that state in the adopted source
reading. The constructions above witness open values across allowed states;
they do not turn this infinite relation into a native knot at every solution.
There is no new claim of physical structure, complexity separation, or a
canonical metric.

## 7. Validation and disposition

`check.py --write` replays the exact relation and constructive witnesses at
both parities, checks every deletion through K1--K3 on finite representatives,
checks the three-row extension at both boundaries, compares the two exact
encodings, replays upward and earlier downward controls, and rejects an
overstatement at `k=1` and the proposed empty-gap separator. The prose proves
the all-`n`, all-`k>=2` statement; finite checks do not supply that quantifier.
The focused replay covers 66 downward instances (`n=3..24`, `k=2,3,11`)
and validates 392,892 explicit infinite extensions, 670 allowed strip-word
pairs at the folding boundaries, and 14 comparisons of the two exact
encodings. Search records remain distinct from this replay; their functions
can be rerun through `--search4`, `--search5`, and `--attack`.

Validation class: V1, hand proof with separately derived same-task finite
encodings and explicit construction checks. This is not external replication
or a trusted-kernel formalization. Primary epistemic class:
`uniform-family-theorem` for Theorems 1--2; secondary
`finite-instance-classification` for the mixed-support search. Source
contribution: 0. The decisive substrate and update rule are inherited.
External novelty: unassessed. Blocker class for the original target:
`substantive-near-miss`; no authority or runtime dependency blocks it.

The family remains Partial for the sharp unrestricted target. The useful surviving
result is the exact downward bond relation for every `n>=3,k>=2`, together
with an exact finite-restriction lemma. A continuation should seek the missing
arbitrary-support invariant or an actual smaller bond, rather than treating
more finite negative cases as a proof of optimality.
