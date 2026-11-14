# Independent relations and gap audit

Scope: `FREE-TARGET-20261114-001`, referee R1, independent relations lane.
The canonical K1–K3 test is unchanged. This is a finite-certificate audit and
a symbolic audit of the growth implication, not a fresh census or an exact
computation of the unrestricted least bond.

## Findings

**All per-call relations and semigroup decisions reproduce.** Fresh
standard-library code reconstructs all 161 relations for the frozen 66,
including the usual-limit greatest fixed point, nonrecursive inlining,
all SELF calls, every level of the product-set orbit, the least rectangular
length, and a recurring nonrectangular call word when no such length exists.
There are zero disagreements with the full-run and relation-gate records.
All 23 stored recurring call words have nonrectangular positive-length
prefixes and return to the same product after a cycle. Their `cycle_products`
are products **before** each cycle step; treating them as products after
each step would falsely flag four period-two records.

| Check | Fresh result |
| --- | ---: |
| Frozen families | 66 |
| SELF port relations | 161 |
| Finite rectangular length | 43 |
| Recurring nonrectangular product | 23 |
| Least r = 2, 3, 4, 5, 6 | 9, 14, 6, 9, 5 |
| Several definitions, all 66 | 13 |
| Several definitions, the 43 | 9 |
| Main differs from S, all 66 | 9 |
| Main differs from S, the 43 | 7 |
| Another self-holding definition, all 66 | 4 |
| Another self-holding definition, the 43 | 4 |

**The 43 growth conclusions survive, with a boundary qualification.** For
main = S the certified bound is `2 + floor(s/r)`. Under the census depth
convention `C_0 = main`, `C_1 = entry`, a wrapper main has only `s-1` tested
S transitions before the depth-s copy. The directly proved bound for those
seven growers is `2 + floor((s-1)/r)`. Their lower asymptotic rate remains
at least `1/r`.

I also checked the possible stronger first stretch, rather than assuming
the shift necessary from syntax alone: for every entry of each of the seven
wrapper growers, I composed its exact main-to-entry relation with every
length-`r-1` S product. **None of the seven has all these products
rectangular.** The least initial all-rectangular length from main is exactly
`r+1` in every case. The original displayed bound therefore has an unproved
first-stretch step for these seven fixtures. This does not assert that some
fixture's actual minimum violates the original numerical bound; the finite
certificate does not prove that bound there.

## Independent construction and controls

`relations_audit.py` imports only Python's standard library. It opens none
of the producer Python, `paths_dp.py`, or `reach_dp.py`. Its only data inputs
are the permitted EVERY-RAY sample records, frozen FREE-TARGET population,
relation/full-run JSON records, and the census family data. Exact input
digests are in `relations_audit.json`.

The usual modification adds NAE on a self-holding definition's ports when a
SELF call permutes those three ports. Starting every SELF relation at TOP,
direct assignment enumeration gives a descending fixed-point iteration.
Non-self-holding calls are freshly expanded, with fresh own distinctions;
calls to every self-holding type remain typed calls. An R_i is enumerated
with precisely the selected S call unconstrained and every other typed call
read by its exact fixed-point relation.

The independent semigroup iterates finite sets of packed Boolean relations
until the entire set repeats. Rectangularity is separately checked as the
Cartesian product of the two projections on the certifying products. A
second search finds a cycle in the finite automaton of nonrectangular prefix
products. The stored lassos are also replayed independently.

Controls include all 256 products of binary relations on two states,
set-based product comparison, closure under either rectangular factor,
proper non-full products, an empty product, identity and permutation
nonforgetting, a first rectangular power at two, a mixed-generator
nonforgetting choice, and deliberately false rectangular/recurrence claims
that reject. Erasing individual SELF side relations changes R_i in two
population families; the exact before/after records are retained.

The wrapper-boundary negative control uses only NAE rules and obeys the raw
description-language caps. Its recursive rule is described, after finite
inlining, by

```text
S(a,b,c): fresh u,v,h,t;
          NAE(a,u,h), t=a;
          SELF(b,u,v).
main(a,b,c): S(a,b,c).
```

The equality is implemented by a finite macro, not supplied as a new law:
six triples of the classical Fano pattern with the terminal triple removed
force its three terminals equal; quantifying the third terminal gives the
displayed equality. The JSON stores and enumerates the actual three-definition
NAE description, including that macro. The flat S body has 12 distinctions;
its exact limit port relation is TOP.

The unobserved port relation is `out_0 = in_1`, with the other outputs free,
so its least rectangular power is two. At depths `C_1,...,C_4`,
`a_2 = main.b` and `a_4 = u_2 = t_4`. Therefore
`{main.b, C_2.h, C_4.t}` allows exactly NAE, is a three-member bond, and
extends through every remaining copy. The unshifted expression at `s=4`
would require four members; the shifted expression requires three. This is
a counterexample to a **uniform wrapper-boundary theorem**, not a new
claim about which of the frozen 66 attain their certified bound.

## Gap proof with members anywhere

Fix any chosen depth-s S copy and its chain of ancestors. Assign each actual
distinction one origin: the copy where it was introduced. A variable passed
as a port retains that origin; its later appearances never create additional
members. Each group along the chosen chain contains its own fresh distinctions
and all branches leaving the chain there. Fresh distinctions introduced
arbitrarily far down such a branch belong to that group for this argument.

Consider r consecutive S groups with no selected member originating in
them. Projecting their unselected own distinctions and all unselected branch
subsystems gives exactly the product of the corresponding R_i. If that
product is rectangular, take a realizing infinite state for an arbitrary
assignment of the selected members above the stretch and another for the
selected members below it. Their actual incoming and outgoing tuples belong
to the respective projections of that product. Rectangularity supplies a
middle assignment connecting those particular tuples. Exact side relations
and fresh local identities let the assignments be combined into a full
allowed state.

Both selected parts are nonempty: they include the root port and the
depth-s own distinction, respectively. Each proper part of a bond is free.
The combination therefore makes the whole selected support free,
contradicting its being a bond. Thus every such stretch must own a selected
member. This argument permits support in any branch and below the target;
it never assumes prefix-only support.

For main = S, use the disjoint stretches of factors
`[0,r)`, `[r,2r)`, ..., ending before or at the target's incoming tuple.
The root port lies at the initial boundary and was not introduced by any
of these factors. The target's own distinction was introduced in `C_s`,
after the factors being counted. There must therefore be one **additional**
member in each of `floor(s/r)` stretches, giving

```text
|B| >= 2 + floor(s/r).
```

For main != S, the first certified stretches instead begin at `C_1`,
giving `floor((s-1)/r)` counted stretches. The main-to-entry factor cannot
be treated as an S factor, even when it is an identity relation.

This explains why the sharpening differs from the older general theorem's
`1 + ceil(s/r)`: that theorem allowed its first endpoint to be introduced
inside group zero. Here the first endpoint is a port on the incoming
boundary. Boundary language must refer to this unique-origin allocation;
the statement that a boundary-port member never serves either adjacent
stretch is too broad without declaring where that identity was introduced.

## Shared identities and all target types

Numeric calls do not create global variables, and distinct calls have fresh
own distinctions. Any identity shared between a branch above a stretch and
a copy below it must be present in every intervening argument tuple.
An identity persisting from the incoming to outgoing tuple forces their
corresponding bits equal. Because the nonempty NAE system is complement
closed, both bit values occur, so this equality makes the relation
nonrectangular. It cannot be silently lost by this test. Rectangularity is
therefore a valid obstruction to a carried-identity bypass.

All eligible fresh distinctions at increasing depth in this population are
introduced by S copies or by nonrecursive definitions expanded within an
S block. The only other self-holding definitions are:

- In sorted population row 0, definition 1 has zero own distinctions and
  calls SELF on `[2,0,1]`, `[1,2,0]`, `[0,2,1]`, with K constraints and
  zero-own nonrecursive calls. Its usual-limit relation is NAE.
- In sorted population row 1, definition 0 is the zero-own single
  pass-through SELF `[0,2,1]`, with usual-limit relation NAE.
- In sorted population row 2, definition 0 is the zero-own single
  pass-through SELF `[1,2,0]`, with usual-limit relation NAE.
- In sorted population row 3, definition 0 is the zero-own single
  pass-through SELF `[2,0,1]`, with usual-limit relation NAE.

The sorted row convention is `population_index_sorted` in the JSON, which
also records the complete keys and flat bodies. Each of these four types
has zero own distinctions **after** inlining as well. Its descendants
therefore supply no additional eligible own target. Their constraints are
included in G when R_i is formed. This is why checking only repeated S
calls covers the free target for these 66; it is not a general theorem for
families with other recursive types that introduce fresh distinctions.

## Unbranched families and prefix support

The chain-count lane independently identified a necessary qualification:
the census L_ray permits support only through its closing target copy,
whereas L_any permits support below the target. A unique chain does not
make these feasible sets equal by definition.

Growth is rescued without asserting equality. For any finite admissible
bond B to depth s, let d be the greatest origin depth of its members.
Then `d >= s`, and the same B is admissible for prefix-only L_ray(d), since
it contains a root port and an own member at its deepest origin. Thus

```text
inf_{d >= s} L_ray(d) <= L_any(s) <= L_ray(s).
```

Consequently, **if** inherited evidence establishes that L_ray is finite
at every sufficiently large depth and that
`L_ray(d) = lambda*d + O(1)` uniformly there, with `lambda > 0`, then
`L_any(s) = lambda*s + O(1)`. This is a conditional rate-transfer lemma,
not an all-depth existence certificate supplied by the chain count. It
does not prove per-depth equality. A monotonicity lemma, if separately
established, would justify equality; it has not been assumed here.

The census lane reports 15 chain rows containing the INF sentinel, with
12 having a sentinel after depth 20. A `grows` class and the chain count
alone therefore do not certify the required all-depth existence premise.
Those records require their own existence/residue evidence or a corrected
classification before an eventual-every-depth rate can be transferred.
The inequality above remains valid with absent bonds read as infinity;
it does not fill those absent depths by itself.

## Read-only review of the fresh direct SAT audit

I reviewed the parent's `direct_bonds.py`; I did not replay producer gates
or duplicate its family searches. The signed-cube SAT problem expresses a
support of at most k with one selected root port and one selected target.
Each discovered full model excludes precisely the compatible signed cubes.
UNSAT of that problem exhausts the remaining eligible cubes. A constrained
proper support excludes all of its supersupports because none can be
minimal. The greedy deletion routine is valid by downward closure of free
sets, and it checks every assignment of each retained one-deletion support.
The clause-support pruning also respects minimality and previously
exhausted smaller sizes. The positive and negative synthetic controls in
`direct_controls.json` exercise these distinctions, including a constrained
but nonminimal support that must reject.

The final read-only review covers `direct_bonds.py` at SHA256
`3b7695896949d90e995b552d81ed1fe5a57d6cc85eaad69fb4a0045c50c76b2d`.
Its bitset model profiles preserve the earlier coverage test: for each
requested assignment, the candidate model mask starts with exactly the
known model indices, and intersects each variable's positive or negative
profile. A nonzero result is an already witnessed full extension. A zero
result still invokes the instance SAT solver, so this optimization supplies
no unproved missing-state verdict.

The preferred prefix pools are used only to find a positive witness of
the current size. Every smaller size has already been globally exhausted
over all unfolded distinctions. A failed preferred scan continues to the
global signed-cube search at the same size. A found support is minimized
and every one-deletion projection is checked before return. Thus a
restricted pool supplies neither a negative conclusion nor an unjustified
minimum. I found no new correctness issue in these two changes.

I also read `validate_direct_search.py` (SHA256
`fc75b5fa9db258bc7c447a59d86fb047ab150bbdc92e4e2611460e29241cb5c1`)
and its stored `direct_validation.json`. The reference oracle enumerates
all full states and then all eligible subsets independently of SAT and
CEGAR. All 45 stored comparisons agree, including absent bonds and minima
2, 3, 4 and 5. The records exercise positive preferred scans after lower
global exhaustion, as well as full negative searches. This review inspected
the code and records; it did not rerun family cases.

The all-copies CNF with G on cutoff calls has the exact allowed-state
projection onto its explicit distinctions. Therefore every returned minimal
witness is a whole-limit bond. The **minimum search is exhaustive only over
members inside that explicit cutoff**. Agreement of two halos is finite
evidence, not a proof that still deeper support cannot improve the minimum.
Timeouts retain lower bounds only from completely exhausted sizes; one
underlying instance-SAT call has no internal interruption, so the requested
seconds are a soft deadline rather than an absolute wall-clock guarantee.

I found and reported one generic target-depth bug in an earlier version
(SHA256 `319e920a562eb225fbab317de8eb9f06e87e301d714bf9a1e5d7e676ab964e20`):
a numeric nonrecursive helper immediately under a nonrecursive main was
assigned depth one, although its own distinctions belong to flattened main
at depth zero. The nine present wrapper families call S directly, so this
specific defect does not affect those fixtures. The final version above
repairs this with `recursive_context`: finite helpers before recursive
entry stay at depth zero, the first self-holding entry is at depth one,
and finite helpers inside a recursive copy retain its depth. The focused
helper/entry regression in `direct_validation.json` passes and checks both
the origin depths and target-set membership. The reported defect is closed.
No positive claim here depends on the pre-repair unfolding behavior.

## Validation and limits

Run from the repository root:

```text
.venv/bin/python -B research/FREE-TARGET-20261114-001/referee-R1/codex/relations_audit.py
```

The audit is one compute process, approximately 1–2 seconds and 42 MB peak
RSS. The JSON records actual elapsed time and peak RSS from the final run.
Validation is V2: an independently authored same-task reimplementation and
symbolic argument, performed by an AI subagent, not human review or external
replication. The infinite-support quantifier is discharged by the splicing
argument, not by finite enumeration. This lane does not re-prove the
inherited L_path existence/rate certificates, decide the 23 nonforgetting
families, establish any exact unrestricted minimum, or assess external
novelty.
