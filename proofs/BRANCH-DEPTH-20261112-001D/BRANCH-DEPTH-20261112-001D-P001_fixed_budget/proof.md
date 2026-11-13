# The depths reachable by a fixed bond budget

**Standard statement.** Fix a finite recursive presentation of Boolean
constraints with bounded finite port lists, fresh own distinctions in each
copy, and sharing only through the supplied arguments of calls. Fix the
branch obtained by repeatedly taking the designated first child. For a
given nonnegative integer \(k\), let \(B_k(n)\) say that the entire infinite pattern has
a finite bond of between three and \(k\) distinct variables containing a top
port and an own distinction of the branch's depth-\(n\) copy. Every finite
support in the pattern is eligible, including side branches and copies
beyond that target.

**Nearest known result.** NEST-COUNT A proves finite-state behavior for a
fixed window at the top and computes exact unmarked infinite port relations.
BONDS-AND-COUNT E proves increasing least bond size for one specified
branching pattern. Neither statement decides bounded observations whose
positions may be arbitrarily far away. Finite relation composition and
finite automata are classical ingredients. The proof here constructs the
needed finite state directly; it invokes no external logical
definability theorem or tree-automaton theorem as authority.

**Theorem.** For every fixed \(k\), the set
\(\{n\ge0:B_k(n)\}\) is effectively ultimately periodic. Its finite prefix,
periodic part, and the truth of \(\forall n\,B_k(n)\) are decidable from the
presentation and \(k\). An empty infinite relation gives the empty depth
set. Repeated port identities do not invalidate the construction.

The conclusion is about one fixed support budget. This proof supplies no
decision procedure for an unknown uniform budget
\(\exists k\,\forall n\,B_k(n)\).

## 1. Presentation, semantics, and the bond test

There are finitely many definition types. Type \(i\) has \(p_i\) formal
ports, a finite number of fresh own variables, finitely many local
constraints, and finitely many child calls. Each child's port is a specified
parent port or own variable. Own variables in distinct copies are different
identities. Distinct child insides meet only through their supplied ports.
This is the usual recursive-copy arrangement (the literature's rooted
derivation tree), not an additional native topology claim.

The first child is fixed by type; it is not chosen separately to improve the
answer at each depth. A type with no designated child has no later target
on that branch. Depth zero means the root copy itself. The same argument
allows a finite-state branch selection policy by adding its finite control
to the type. It does not cover a nonperiodic externally supplied sequence
of child choices.

Read the infinite system through all its satisfying joint states. Its port
relations \(G_i\) are exact: a port state is in \(G_i\) precisely when the
whole infinite copy extends it. These are computable greatest fixed points
by the admitted NEST-COUNT argument, using finite relation composition and
compactness. For a usual-limit presentation, first apply its admitted
pass-through correction. The implementation makes this preprocessing
explicit; it never substitutes finite-depth SELF termination for the
infinite relation.

For completeness, the same admitted argument applies to the finite
multi-type grammar used by one control. Start every type's unmarked port
relation at TOP and compose one more level. Monotonicity makes the finite
product of port relations descend to a fixed point. Its depth-\(h\) value
is the exact relation of the prefix with all further constraints omitted.
An infinite extension lies in every prefix relation. Conversely a port
state surviving all prefixes extends by the compactness argument already
used in NEST-COUNT. Thus the stable relation is exact even when different
types call each other; this invokes no additional external theorem.

For an actual support \(W\) of distinct variable identities, let \(R_W\) be
the exact projection of the infinite relation. A bond here requires

1. \(|W|\ge3\);
2. \(R_W\) is constrained as a whole (K1);
3. deleting any one variable from \(W\) gives the full relation (K2);
4. \(R_W\ne\varnothing\) (K3).

Single deletions suffice for all proper subsets, by further projection.
Minimal unshattered pairs, if any, are ties rather than bonds in this test.
Both an empty projected relation and a full projected relation are rejected.
The assertion concerns this finite-projection test, not finite-flip sources
at an infinite solution.

## 2. Exact profiles with finitely many named observations

Put \(m=\max(k-1,0)\), because at least one support variable must be a top
port. Use \(m\) observation labels. At a copy of type \(i\), an observation
label can name only a variable introduced in that copy or one of its
descendants, never one of its incoming port variables.

For a label subset \(J\), a profile is the exact relation on

\[
 (\text{the }p_i\text{ formal ports},\ \text{the labels in }J)
\]

obtained by assigning the labels injectively to finitely many such introduced
variables. Labels record prescribed observation values. They add no
constraint to the unobserved variables. Let \(\mathcal P_i(J)\) be the set
of all profiles obtainable this way, at arbitrary finite observation depth.
In particular
\(\mathcal P_i(\varnothing)=\{G_i\}\).

There are finitely many possible profiles: a relation on \(p_i+|J|\)
Boolean coordinates has \(2^{2^{p_i+|J|}}\) possible truth tables. It remains
to show that the exact obtainable profiles, rather than an approximation,
are effectively enumerable.

### Composition

Choose a subset of labels to assign injectively to the current copy's own
variables. Partition the remaining labels among its child copies. For each
child use one profile with exactly its assigned labels. Conjoin the local
constraints with those child relations after substituting the actual
arguments. Equate each locally assigned label with the value of its chosen
own variable. Project away the unobserved own variables.

This is a finite calculation on Boolean truth tables. The partition is
disjoint because fresh variables in different child insides are different
identities. Observations of an ancestor's variable are never assigned a new
label in a descendant: that identity is already represented through the
actual port argument wherever it occurs again.

### Least closure

Start with \(\{G_i\}\) at the empty label set and the empty family at every
nonempty label set. Repeatedly add every composite profile just described.
The process stops because it only adds elements from finite sets.

Every added profile comes from an actual finite placement of labels, in
the finitely many witnessed child constructions and the current own
variables. For each row admitted by the composite relation, all remaining
subcopies can be filled using their exact \(G_i\). An empty profile is
retained as the exact relation of its placement; it asserts no allowed row.

Conversely, take any finite placement of observations in a whole infinite
copy. The finitely many copies where these variables are introduced have
finitely many ancestors. Cut immediately below this finite collection.
Every unobserved remaining subcopy is exactly summarized by \(G_i\).
Composing upwards gives the placement's exact profile after finitely many
closure stages. Therefore this least closure is exactly
\(\mathcal P_i(J)\).

This is the key step that permits arbitrary side branches and arbitrarily
deep auxiliary observations. It supplies no a priori depth cutoff on their
placement.

## 3. A finite recurrence for the target depth

Give label zero a distinguished role: it must name an own variable of the
designated branch's depth-\(n\) copy. For every type \(i\) and label set
\(J\ni0\), let \(\mathcal Q_i^n(J)\) be the family of exact profiles with
that requirement. The other labels can name any distinct introduced
variables anywhere in the copy.

The initial family \(\mathcal Q_i^0(J)\) is computed by one composition:
label zero is assigned to an own variable of the current copy, other
labels can be assigned locally or to child profiles in \(\mathcal P\).
If the current type has no own variables, this initial family is empty.

For the next depth, assign no target label locally. Give the first child
the labels including zero and a profile from its \(\mathcal Q^n\) family.
Give all side children arbitrary profiles from \(\mathcal P\). Other labels
can also be assigned to current own variables. Perform the same exact
composition and collect every resulting relation. A missing first child
gives the empty family.

Consequently the whole finite vector satisfies

\[
 \mathcal Q^{n+1}=F(\mathcal Q^n)
\]

for one effectively constructed deterministic map \(F\). Exactness follows
by splitting any finite observation placement into current own observations,
first-child observations, and side-child observations. At depth zero,
the descendants *beyond* the target use \(\mathcal P\), not an empty
continuation. At greater depths, all side children at all ancestors also use
\(\mathcal P\).

Each vector component is a subset of a finite set of truth tables. Thus
iteration eventually repeats. Store the first occurrence of each vector;
the first repetition supplies its preperiod and period. This is an exact
termination criterion, not a classifier applied to a finite depth sample.

For example, if there are \(d\) types and at most \(b\) ports, a deliberately
loose upper bound on the number of vector states is

\[
 2^{\,d\,2^m\,2^{\,2^{b+m}}}.
\]

The bound is only a finiteness bound. No practical complexity claim is made.

## 4. Root acceptance, identities, and absence

At the root, take a profile in \(\mathcal Q^n_{\rm root}(J)\). Choose a
nonempty subset of its *actual distinct* top-port identities so that the
total support size is between three and \(k\). Include their values as
observation coordinates and existentially forget the other ports. Check
K1–K3 on that projected truth table. This is a finite acceptance test.

Every accepted relation witnesses an eligible support. Conversely, given
any eligible bond \(W\), choose one of its target own variables for label
zero. Assign its other non-top variables distinct labels. There are at most
\(k-1\) of them in total. Section 2 includes their finite placement and
Section 3 includes its target requirement. The root acceptance test also
includes exactly the chosen top variables. Hence it accepts \(W\).

Actual argument maps are part of the syntax. If two child formal ports
receive the same variable, substitute that same actual value in both
positions when evaluating its relation. This is a diagonal restriction of
the formal port relation, not a new independent observation. The same
argument identity is used in every child receiving it. Fresh own variables
remain different identities even when they happen to have equal values.
At a root with aliased formal ports, impose its diagonal equalities and
choose only one representative per actual identity when counting support.
Thus repeated ports and a persistent top variable moving between port slots
are handled without confusing identity with equal values.

If the global relation is empty, every attainable root projection is empty
and fails K3. If the target copy is absent, or introduces no own variable,
the appropriate \(\mathcal Q\) family is empty. If a local target is bound
only to variables in a component independent of the top, a support adding
a top port fails K2. None of these cases is reported as a bond.

Acceptance is a function of the finite vector \(\mathcal Q^n\). Its
accepted depths are therefore ultimately periodic, with computable prefix
and period. To decide existence at every depth, check the finite prefix
and one complete cycle. For a convention starting at depth one rather than
zero, omit just the depth-zero answer.

## 5. Fixed versus unknown budget

Applying the procedure separately to \(k=3,4,\ldots\) semidecides a positive
answer to \(\exists k\,\forall n\,B_k(n)\): a successful fixed-budget run
eventually finds it. There is no stopping criterion here for the negative
case. This proof establishes neither a general decision procedure nor an
undecidability theorem for that unknown-budget question.

Also distinguish \(\forall n\,\exists k\,B_k(n)\). The admitted branching
benchmark has a finite bond at every depth and least size increasing
linearly, so it satisfies this statement while failing
\(\exists k\,\forall n\,B_k(n)\). Its separate depth proof remains the
authority for the uniform increasing lower and upper bounds.

## 6. Executable controls and the accepted branching benchmark

The implementation uses strict local NAE triples, arbitrary finite calls,
and exact integer truth tables. It saturates unrestricted observation
profiles, then iterates target vectors to their first repeated state.
It requires support size at least three. No corpus census is run.

The default support budget is three:

| Control | Exact accepted depths | Purpose |
| --- | --- | --- |
| Persistent top identity | All \(n\ge0\) | A top identity is carried indefinitely; three-place bonds persist |
| Forgetting first child | \(0,1\) | Merely having local NAE constraints does not keep a top connection |
| Repeated child port identity | All \(n\ge0\) | Repeated arguments are substituted consistently |
| Empty infinite relation | None | An empty limit cannot provide a bond |
| Finite first branch | Only \(0\) | No target copy exists after the leaf |
| Root without own variables | All \(n\ge1\) | Root-depth absence differs from all-positive-depth existence |
| Side-child witnesses | \(0,1,2\) | Required auxiliary observations lie after the target and off its branch |
| Admitted BONDS-AND-COUNT E family | \(0,1,2\) | Exact fixed-budget decision on a genuine branching limit-only rule |
| Alternating two-type grammar | Even \(n\) | A proper period-two depth set; both types have local binding |

The side-child control is

    D(a,b,c): introduce x; call first D(b,c,x) and side S(a,x,b).
    S(p,q,r): introduce y; impose NAE(p,q,y); no children.

At depths zero, one, and two, the target \(x\) has a three-place bond with
the appropriate top port and the side child's \(y\), introduced one depth
later. No constraint lies entirely on the first branch; incorrectly
omitting side constraints makes its depth-zero answer false. This matched
control tests a substantive endpoint difference.

The period-two control is a finite two-type grammar, explicitly outside
the one-definition census. Both types preserve their three ports and
impose NAE on them. Type A introduces \(x,y\), imposes NAE(\(a,x,y\)), and
calls B; type B introduces \(u,v,w\), imposes NAE(\(u,v,w\)), and calls A.
At A copies the fresh targets bind with top \(a\). The fresh B variables
form a local NAE relation in a component independent of every top variable,
so adding a top variable cannot give a minimal bond. The exact target-vector
orbit has preperiod zero and period two. Aliasing all three root ports
makes the explicit root NAE relation empty and gives no accepted depth.

For the admitted branching benchmark, the budget-three run uses 27
unrestricted profiles and stops after five closure rounds; its target
vector has preperiod three and period one. The budget-four run uses 389
profiles and six closure rounds; its accepted depths are exactly \(0\)
through \(4\), with preperiod five and period one. These are **existence
decisions** for each budget. Combined with the predecessor's upper bound
\(\lceil n/2\rceil+2\), they give

\[
 L(3)=L(4)=4,\qquad L(5)=L(6)=5.
\]

The budget-three exclusion gives the lower bound four at depths three and
four, and budget-four existence attains it. Budget-four exclusion gives
the lower bound five at depths five and six, and the admitted upper
construction attains five. No value at a later depth is inferred by
extrapolating these numbers.

An independent code path expands the simple controls to a finite
observation horizon and closes the remaining calls with their directly
known exact port relations. It uses SAT projections over concrete variable
identities and independently checks their proper projections. This agrees
at target depths zero through three. That finite check is a control on the
implementation; the full unrestricted result comes from saturated profiles
and the proof above. The canonical knotlab CLI independently accepts NAE
and rejects both the empty and full three-variable relations.

The usual-limit control starts with a pure port pass-through SELF call.
The admitted preprocessing changes its port relation from TOP (mask 255)
to NAE (mask 126). Neither mode supplies a bond to its unused own variable.
An intentionally insufficient resource cap raises an exception without a
decision.

## 7. Use and resource boundary

Run the complete bounded replay:

    .venv/bin/python -B proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/check.py --write-result

Use a single fixture and budget:

    .venv/bin/python -B proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/check.py --fixture branching_depth --k 4

The public function is

    decide_dlang(definitions, budget=3, max_profiles=100000,
                 usual_limit=True, max_states=10000)

It returns the exact orbit after completed saturation and a repeated target
vector. The every_depth field includes depth zero; every_positive_depth
checks all depths starting at one, including any recurrence of the initial
state in the cycle. The designated branch is the first SELF call in the supplied body
order, repeated thereafter. Earlier-definition calls are side subpatterns.
For the one-definition corpus this is precisely the intended first
recursive branch. The usual-limit pass-through correction is enabled by
default; selecting bottomless semantics is explicit.

The batch CLI accepts a JSON list of records containing an id and defs:

    .venv/bin/python -B proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/check.py --batch-json /absolute/path/input.json --k 3

Each resource-limited case returns resource-limit rather than a false
answer. A single record or raw definition list can be passed with
--definitions-json. These operations do not run the control suite.

At three ports and budget three, even one profile can be an arbitrary
32-bit truth table; the loose theoretical space includes \(2^{32}\)
different profiles per label component. The small completed controls do
not imply that all 664 corpus rules, or all remaining rules, fit a practical
budget. This leaf does not repeat that census. Counts and measured timings
for the retained controls are in result.json; no wall-clock timeout is used
as a scientific verdict.

## 8. Evidence and scope

Status: **Proved**, as a uniform theorem with finite implementation
validation. The primary epistemic class is uniform-family-theorem; the
bounded executable controls are a finite-instance-classification. Source
contribution is zero: the construction uses the already declared recursive
syntax, allowed-state semantics, and exact unmarked port relations. It
adds no new law or observational oracle.

Validation is V1, separate algorithms in one task: exact profile algebra
and a concrete SAT expansion/projection path. The canonical knotlab
controls use the existing checker. These are not external replication or
a formal-kernel proof of the uniform theorem. External novelty is
candidate local delta; the general finite-state ingredients are classical.

A separate coherent alias control repeatedly imposes a prototype
NAE(\(a,b,y_i\)) and passes \(a,b\) unchanged, with all root ports assigned
the same actual identity. Both values of that identity extend, and every
\(y_i\) is its complement. There are two global states and many two-variable
ties, but no bond of three or more variables. The test rejects every
depth. This checks alias counting and the distinction between ties and
bonds without relying on an empty limit.

The theorem settles fixed \(k\), including unrestricted finite auxiliaries.
It leaves the unknown-budget decision problem, practical corpus feasibility,
and finite-flip source classification open. Those are scope limits, not
missing lemmas in the stated fixed-budget theorem.
