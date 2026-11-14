# Independent direct check and a path-quantifier counterexample

Scope: `EVERY-RAY-20261113-001`, referee R1, independent direct-enumeration
lane. This lane wrote only `direct_brute.py`, `direct_brute_results.json`
and this note. No producer Python under EVERY-RAY or REACH was read or
imported. There were no Git mutations, publication actions or lifecycle
changes. This is a same-task independent reimplementation, not external
replication or human review.

## Verdicts

- **Not a block — the new bounded numerical check.** Eighteen new
  several-definition sample families agree with the reported `L_path` in
  all 71 completely enumerable depth cells under the declared seven-member
  comparison rule (63 finite exact minima; eight no-bond-through-seven
  comparisons). All 18 were checked at depths
  1–3; 17 were also checked at depth 4. All 63 available uncarried-row
  comparisons agree. This does not validate an eventual classification.
- **Narrowing — coverage.** The 18 new families supplement the original
  22 several-definition G-brute families. They do not retroactively satisfy
  the original frozen panel's depth-to-preperiod-plus-period requirement.
  One extra depth-4 cell has 23 distinctions: all 81 paths are explicitly
  skipped; no depth-1–3 path is skipped.
- **Block — the single-infinite-path reading.** The explicit family below
  has `L_path(s)=3` at every depth and `L_path^unc(s)=4` at every depth
  `s>=3`, while the least endpoint bond along **each single infinite
  descending path tends to infinity**. Thus an eventual bound on the
  separately minimized finite-depth values does not supply one infinite
  path with bounded reach. This blocks that prose inference, not the
  mathematical definition or computed finite-depth values of `L_path`.
- **Block — comparing different targets.** For this same family the full
  all-branches unfolding, with members anywhere but the target fixed to the
  all-call-0 copy, has `L_true(s)=floor(s/3)+3`, exceeding
  `L_path(s)=3` from depth 3. Relaxing members while fixing a target is not
  comparable by inclusion to minimizing over different target copies.

## Direct-enumeration interface and coverage

The inputs were the mathematical specification and addendum, the description
language and LIMIT-STATE/BOND-DEPTH semantics, and JSON/JSONL sample and gate
records. The script imports only Python standard-library modules and NumPy.
It uses the original family definitions as data and independently:

1. adds the usual NAE clause to a selfholding definition with a pass-through
   call;
2. iterates the selfholding port relations down from the full relation to
   their greatest fixed point;
3. chooses the first selfholding definition reached in main's call-order
   expansion, inlines nonself macros with fresh locals, and summarizes other
   selfholding definitions by their greatest-fixed-point relations;
4. enumerates every entry and every continuing call, retaining distinct
   occurrences of duplicate calls;
5. enumerates all Boolean assignments of at most 22 distinctions, with
   nonchosen calls and final calls read as the fixed-point relation;
6. enumerates member sets in increasing size through seven, pruning only
   supersets of already established non-shattered sets, and explicitly
   verifies every single deletion of a reported minimum is full.

Members are main's distinctions and each chosen copy's own distinctions,
including inlined nonself locals. Endpoints are a port of main and an own
distinction of the target copy. A repeated actual argument denotes the same
distinction; no copy is made to replace that identity. The uncarried flag is
computed from final port identities, independently of any producer mask.

All six preparation quantities (`S`, main size/own count, recurring
size/own count, SELF-call count) matched the sample rows for all 18 families.
The 18 positions in the deterministic candidate order were
`0,1,3,4,5,8,9,11,13,14,16,17,20,23,24,27,30,44`.
The selection conservatively excludes all 152 keys appearing anywhere in
the original brute-panel JSON, including its exclusions, rather than only
its selected keys. There were 69 remaining several-definition candidates.
These are coverage examples, not a new random sample for estimating shares.

The run enumerated 1,564 paths and 20,573,984 complete assignment rows,
evaluating 1,198,504 member-set projections. It took 31.904 seconds and
used a process peak of 112,272 KiB. Sample classes were 12 bounded, two
growing, two none, and two unresolved; definition counts range from two to
five. The two growers' first four values are respectively `3,4,5,6` and
`4,5,6,7`. Exact keys, complete definitions, flattened call arguments,
constraints, copy identities, assignment counts and hashes, member
witnesses, deletion counts, row values, and skipped paths are in the JSON.
Small satisfying-assignment sets are also recorded in full.

The seven-member censoring rule is explicit: "no bond through seven" agrees
with a row value above seven; it alone is not proof of absence at all sizes.
For example, a whole full relation has no bond at any size, while a
non-full relation may merely have no small endpoint bond. The JSON records
which reason occurred for each path.

As a separate check, all 18 independently computed fixed points agree with
the permitted description-language evaluator's `depth_sequence(TOP)` and
`relations` outputs. That evaluator was not used to produce the brute
results. Input hashes and the final implementation hash are recorded in
`integrity_checks`.

Controls distinguish three kinds of repetition. The archive generator uses
distinct arguments **within** each individual call. Duplicate SELF calls
**across** calls occur in selected families 9, 30 and 44. Arguments shared
between different calls are preserved throughout. A synthetic NAE relation
on arguments `(0,0,1)` has a two-member bond, while its distinct-argument
version has a three-member bond; duplicate side-call occurrences preserve
the relation; and a free endpoint is not made dependent by a disjoint local
NAE. Deliberately wrong numerical values are rejected. An additional full
SELF-family control with within-call repetition is recorded below.

Reproduction, one process at a time, from the repository root:

```text
.venv/bin/python -B research/EVERY-RAY-20261113-001/referee-R1/codex/direct_brute.py --depth 4
.venv/bin/python -B research/EVERY-RAY-20261113-001/referee-R1/codex/direct_brute.py --fixtures --depth 5
.venv/bin/python -B research/EVERY-RAY-20261113-001/referee-R1/codex/direct_brute.py --lassos --depth 4
```

The first command creates the primary result. The later commands append
their respective independent checks to that same JSON.

## The explicit path-quantifier counterexample

One three-port definition, with own distinctions `x` and `y`, has calls

```text
K(port1,x,y)
SELF(port2,port0,y)       # call 0
SELF(port0,x,y)           # call 1
```

Its exact description key is

```json
[[3,2,[["K",[1,3,4]],["SELF",[2,0,4]],["SELF",[0,3,4]]]]]
```

There is no pass-through call. The full three-port relation is a fixed
point: for any ports, choose `x!=y`. It is consequently the greatest fixed
point. All side calls impose no restriction. A selected finite path thus
has exactly one NAE constraint per copy:

```text
NAE(a_i,x_i,y_i),
```

where `x_i,y_i` are fresh and `a_i` is a previously existing distinction.
The following argument uses a classical auxiliary constraint-incidence
forest, whose components each start at one of main's three ports. It is
an accounting device for Boolean relations, with no native-topology claim.

### Lemma: least endpoint bond equals ancestry height plus two

Suppose each NAE constraint adds two fresh distinctions to one existing
distinction. Let an own distinction `v` have ancestry height `h`, counting
the constraints from its component's main port `p` through the constraint
that introduced `v`. Then the least minimal non-shattered set containing
a main port and `v` has `h+2` members.

**Lower bound, including arbitrary extra-branch members.** Fix any minimal
non-shattered set `W` containing both endpoints and an assignment to `W`
that has no extension. Such an inconsistency in a constraint-incidence
forest has a finite propagation certificate. This fact can be checked
directly, without a completeness theorem: recursively pass the set of
feasible values, one of `empty`, `{0}`, `{1}`, or `{0,1}`, from each
component toward an arbitrary root. A variable takes the intersection of
its pin, if assigned, and the messages from its other constraints. A NAE
constraint forces its third variable only when its other two branches
force the same value; it then forces the opposite value. In all other
nonempty cases its message is full. An empty message is either an earlier
empty branch or a clash between two singleton requirements, possibly one
being a pin. These recursive messages exactly characterize extension,
since different branches share no other distinction.

Trace a clash, choosing only the requirements needed for it. Each selected
NAE constraint has degree three in this certificate. Each internal,
unpinned distinction has degree two: one requirement is opposed to
another at the clash, or a forcing requirement is passed to the next
constraint. Each remaining distinction is a pinned leaf. At a variable
with several forcing branches, one forcing branch suffices for a value
and two opposed branches suffice for a clash, so extra branches never
need to be retained. The absence of incidence cycles prevents two
certificate branches from identifying a further distinction.

For `m` selected constraints, `u` internal degree-two distinctions, and `l`
pinned leaves, counting incidences and using that the certificate is a
tree gives

```text
3m = 2u+l,
3m = m+u+l-1,
therefore l=m+2.
```

Every member of `W` must occur among these pinned leaves. Otherwise the
certificate would already contradict a proper subset of `W`, contradicting
the minimal non-shattering condition. Thus `|W|=m+2`. The certificate
contains `p` and `v`, so it contains their unique incidence path and its
`h` constraints. Hence `m>=h` and `|W|>=h+2`. Choosing members in other
branches cannot improve this bound. A main port outside `v`'s component
cannot occur in a minimal set, because its independent component could
be forgotten without removing the obstruction.

**Upper bound.** Retain the `h` constraints on that unique path. Select its
two endpoint distinctions and the third, off-path distinction from each
constraint. This gives `h+2` distinct members. All constraints outside the
path can be extended for every value of their single attaching distinction,
so they do not change this projection. For one NAE constraint the boundary
relation omits exactly two complementary assignments. Appending the next
NAE constraint and quantifying its shared path distinction again omits
exactly two complementary assignments: the previous forbidden word forces
the shared value, and the new pair of equal boundary values forces its
opposite. This is an induction on the number of path constraints. Every
single deletion is full, because the two forbidden words disagree at
every coordinate. There is an allowed state. The selected `h+2` members
therefore are a minimal non-shattered set, proving the lemma.

### Every single infinite path has unbounded ancestry height

Index copies from `C_0`; let `w_i` choose the call making `C_i` from
`C_{i-1}`. Write `P_i^j` for port `j` of `C_i`. The substitutions are

```text
w_i=0: (P_i^0,P_i^1,P_i^2)=(P_{i-1}^2,P_{i-1}^0,y_{i-1}),
w_i=1: (P_i^0,P_i^1,P_i^2)=(P_{i-1}^0,x_{i-1},y_{i-1}).
```

The constraint in copy `i` attaches at `a_i=P_i^1`. If `w_i=1`, its
constraint parent is `i-1`. If `w_i=0` and the previous zero occurred at
index `q>=2`, its parent is `q-2`. The first zero attaches directly to
main's port 0; the special case `q=1` attaches directly to main's port 2.
Those are only finitely many direct attachments.

Apart from those exceptions, write the parent index as `f(i)`. For every
fixed infinite word, `f(i)` tends to infinity. If it has finitely many
zeros, eventually `f(i)=i-1`. If it has infinitely many zeros, the previous
zero index tends to infinity on zero steps, and again `f(i)=i-1` on one
steps. The ancestry heights obey `h_i=1+h_{f(i)}`. Each bounded-height
set is finite, by induction on the height: direct-root attachments are
finite, and `f(i)` eventually exceeds every member of the finite set of
smaller heights. Thus `h_i` tends to infinity. By the lemma, the least
endpoint bond along that one infinite path tends to infinity. This holds
for every infinite word, with no periodicity assumption.

### The minimum separately at each depth stays bounded

For each depth `s`, choose the finite word `1^(s-1)0`. Its final NAE
constraint attaches directly to main's port 0, so it has a three-member
endpoint bond. No smaller bond exists by the lemma. Therefore
`L_path(s)=3` for every `s>=1`.

For `s>=3`, choose `1^(s-2)01`. The final two constraints attach first to
main's port 0 and then to the first one's fresh `x`, so the endpoint bond
has four members. The final ports are
`(y_{s-3},x_{s-1},y_{s-1})`, containing no port of main. A three-member
endpoint bond would have to be the target copy's single NAE constraint,
which would place a main port among that copy's ports. Thus no uncarried
three-member bond exists, and `L_path^unc(s)=4` for every `s>=3`.

All 62 finite words of lengths 1–5 were also directly enumerated, and
every finite path's result agrees with the independent ancestry formula
through the seven-member cap. Their depth minima are `3,3,3,3,3`; the
uncarried minima are absent, absent, `4,4,4`. The originally suggested
suffix `00` is not a uniform witness: `1^(s-2)00` has minima `4,5,6`
at depths 3,4,5. The suffix `01` is the correct moving witness.

Consequently the quantifiers cannot be exchanged:

```text
for every depth s, some finite path has a bond of size <=B
```

does not entail

```text
some single infinite path has endpoint bonds eventually bounded by B.
```

The finite witnesses above postpone a decisive call as the requested
depth increases. They do not converge to a bounded infinite witness.

## The full all-branches unfolding does not shorten this fixed target

The same `h+2` lemma holds in the full infinite unfolding of this fixture,
with finite bond members allowed anywhere. Every copy still contributes
one NAE on one already existing anchor and two fresh own distinctions;
neither port sharing nor another branch introduces a constraint on two
existing distinctions. For any finite member set, take the finite
ancestral closure of its creating constraints, including the other
distinctions in those constraints. Its depth decreases on ancestry, so
the closure is finite. Every satisfying assignment of that closure
extends to the full unfolding: process remaining copies by depth and set
their two fresh own distinctions to `(0,1)`. This satisfies their NAE for
either value of the old anchor. Consequently the infinite projection is
exactly the finite closure's projection. Every finite non-shattering
obstruction therefore has the finite propagation certificate counted
above. Extra-branch members cannot defeat its `h+2` lower bound, and the
unique ancestry constraint path supplies the same upper bound.

There is also no finite-support source obstruction to these finite
projections. Each such completion has only finitely many clauses whose own
pair is not opposite. Given any distinction, take a finite ancestral
closure containing its creating constraint, if any, and all those
nonopposite clauses. Complement every distinction in its component of
that finite closure. All internal NAEs are preserved by complementation;
every outside NAE still has its unchanged opposite own pair. This finite
change flips the requested distinction. Thus every allowed finite
projection assignment has a global completion where every distinction
admits a finite-support flip. This is an existence statement about such
completions, not a claim that every arbitrary global state has this
property.

For the target copy reached by `s` repetitions of call 0, the ancestry
heights satisfy `h_0=h_1=h_2=1` and `h_s=h_{s-3}+1` for `s>=3`.
Therefore, with the target fixed to that copy and members allowed
anywhere in the full unfolding,

```text
L_true_fixed0(s) = h_s+2 = floor(s/3)+3,
L_path(s) = 3.
```

At depth 3 these are 4 and 3 respectively. At every fixed target, allowing
more member locations can only reduce that target's minimum. Minimizing
over different target copies changes a different restriction, so it does
not give `L_true_fixed0 <= L_path`. This counterexample uses one exact
family and does not depend on matching sparse BRANCH records.

## Full SELF control with within-call repeated arguments

The synthetic family is

```json
[[3,2,[["K",[0,1,3]],["K",[0,3,4]],["SELF",[3,3,0]],["SELF",[3,4,1]]]]]
```

Its independently computed greatest fixed point is full. Each of its
14 paths through depths 1–3 is alive. Choosing call 0 makes a child's first
NAE `NAE(u,u,x)`, forcing `x=1-u`; replacing the repeated argument by a
fresh identity would change the relation. The exact path minima are:

```text
depth 1: 0:3, 1:4
depth 2: 00:3, 01:4, 10:4, 11:5
depth 3: 000:3, 001:4, 010:4, 011:5,
         100:4, 101:5, 110:5, 111:6
```

Thus its min-over-paths values are `3,3,3`. This is an additional control
outside the archive's distinct-within-call sampling rule, not an archive
observation.

An exact scan of all 600 distinct final sample keys finds no SELF tuple
with a repeated argument within the tuple. Twenty-seven sampled
definitions contain duplicate SELF tuples across calls. Thus within-call
repetition is tested by the synthetic family rather than attributed to
the sampled archive.

## Independent check of the lead's fixed-word calculations

The `lasso_crosscheck` section reads only the lead's JSONL output as data:
definition key, entry, prefix, repeated period, finite values, and port
masks. It does not read or import the lead's implementation or interpret
the encoded DP vectors. The chosen words are independently flattened and
their complete assignments and minimal member sets enumerated. The finite
calculation and identity masks are compared separately. This is a bounded
cross-check of the lead's fixed-word calculations; it does not itself
verify the repeated-vector certificate for arbitrary depth.

Ten certified mixed-path families were selected by smallest depth-4
distinction count, then row order and key (row orders
`0,1,2,5,6,8,10,12,14,15`). All 40 finite values and all 40 exact port
masks agree. The full synthetic within-call-repeat family is retained
under this same JSON section. This secondary computation took 0.217
seconds.

The uniform counterexample argument above is a symbolic derivation in this
note, not a machine-formalized proof. The 62-word fixture check tests its
finite formula but does not establish the infinite quantifier by itself.
External novelty was not assessed. The findings establish neither a new
native topology claim nor any complexity-class, physical or ontological
claim.
