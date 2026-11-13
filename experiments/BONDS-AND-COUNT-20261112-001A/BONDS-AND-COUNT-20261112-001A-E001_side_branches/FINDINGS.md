# Side branches can strictly shorten a bond

Scope: `BONDS-AND-COUNT-20261112-001`, leaf A. Evidence stage: exploratory;
exact finite relation certificates, with V1 separate-algorithm checks. This
identity is not a confirmatory experiment or a promoted proof family.

## Result

For the same top distinction and depth-one own distinction of a genuine
branching, limit-only census member, the least ray-supported bond has four
members and the true unrestricted least bond has three. The ray has no cycle
of knots. The shortcut uses one own distinction of a side copy.

This is a same-pair result. The minimum over all six eligible top/depth-one
endpoint pairs is three under both support choices, so this example does not
change the preregistered minimum over endpoint pairs. No asymptotic growth
claim or rarity claim follows.

## Input and exact limit semantics

The primary member is accepted `LIMIT-ONLY` corpus file
`artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only/sample_2.jsonl.gz`,
line 25697, with one definition, three ports, two own distinctions, and four
calls. Write its ports as a,b,c and own distinctions as x,y:

```text
D(a,b,c):
    D(x,a,c)       # first SELF: the ray
    D(y,c,b)       # second SELF
    D(b,y,x)      # third SELF
    NAE(a,c,y)
```

There is no pass-through SELF on the three original ports. Thus the usual
limit and the bottomless pattern agree by the accepted NEST-COUNT result.
Scalar port-table iteration independently finds greatest fixed point TOP:
all eight port states are admitted. This is exact, not free truncation by
assumption. Indeed, given any a,b,c, choosing y=1-a satisfies the local knot;
every child port state is admitted at TOP. This also gives a direct recursive
extension of every finite-cut state to the unexpanded calls. In the finite
family with holding knots at the cutoff, the first empty relation is at depth
four, independently reproducing the accepted corpus's limit-only label.

The root copy has own distinctions x0,y0. Its first child is
D(x0,a,c), with own x1,y1. Following the second SELF of that child gives
D(y1,c,a), with own z,w. The compared endpoints are a and y1. The exact cuts
therefore impose:

```text
ray cut:       NAE(a,c,y0), NAE(x0,c,y1)
side expansion adds:       NAE(y1,a,w)
```

Every other call has its exact TOP limit relation. Shared names retain their
identity. The ray cut has seven variables and 72 allowed assignments. The
side-expanded cut has nine variables and 208 assignments. Projecting its
allowed assignments onto the seven ray variables gives exactly the ray-cut
relation. The two ray knots share only c; their incidence relation has no
cycle. The side expansion adds a cycle of knots, which is not mistaken for a
knot verdict: the claimed bonds are checked on their projected allowed states.

## The certificate

Ray bond: variables in order `(a,x0,y0,y1)`. Its allowed table is all 16 states
except `0101` and `1010`. Every single deletion is full on its three remaining
variables. The pair `(a,y1)` and all five three-member ray supports containing
that pair are full. These six tables exclude every cheaper ray bond.

Unrestricted bond: variables in order `(a,y1,w)`. Its allowed table is exactly
`001,010,011,100,101,110`. Each single deletion is full on two variables.
The pair `(a,y1)` is full, excluding the only two-member support containing
both endpoints. Thus the unrestricted minimum is exactly three, not merely an
upper bound from a searched finite cut. An arbitrary side support outside the
cut cannot give a bond smaller than that pair.

The ray argument also survives allowing supports beyond the endpoint level.
The complete ray has precisely the knots
`NAE(a,c,y0)` and `NAE(x[j-1],c,y[j])` for j>=1. Every knot shares only c with
the other knots; all other distinctions in different knots are fresh. Any
three-member support containing a and y1 leaves at least one private partner
in one of those two knots free, or leaves both partners free if its third
member belongs to another knot. Its projection is full. The exhibited
four-member support remains a bond. This is an explanatory argument for this
one explicit ray, not a theorem about all nested families.

`verification_acyclic.json` retains the full projected tables, single-deletion
tables, and one finite-cut completion for every allowed state. Exact TOP
extension justifies those completions as states of the whole pattern. The
canonical knotlab CLI reports K1, K2 and K3 true for both displayed bonds.
This establishes the relational verdict; finite-flip sources at infinity were
not assessed. No native-source conclusion is asserted.

For the aggregate endpoint observable, `(c,x0,y1)` is already a three-member
ray bond. All six eligible endpoint-pair projections are full. Hence both
aggregate minima are exactly three. The verification file records those six
tables and that aggregate witness.

## Search, controls and independence

The immutable accepted corpus supplies 664 genuine branching one-definition
limit-only members. Descriptions were ordered by number of own distinctions,
body-call count, corpus filename and line; the search stops at the first
strict shortcut with a finite ray minimum. This is not a new exhaustive
description census, and the order is not a probability distribution.

The unrestricted first probe found a 4-to-3 shortcut in the first member,
`sample_0.jsonl.gz:7436`; its ray contains cycles. That small secondary witness
is retained in `witness.json` and `verification.json`. The explicit no-cycle
search excluded it, tried the next member (`sample_1.jsonl.gz:9241`) at depths
one, two and three without finding a three-member shortcut, and found the
primary witness in the third member at depth one. Its two-local, four-call
body is at the smallest size represented among these eligible corpus members;
no claim of globally shortest description is made.

Producer `compare.py` uses vectorized integer-state enumeration. Verifier
`verify.py` does not import it: it independently rebuilds the substitutions,
iterates tuple-valued port relations, enumerates Boolean assignments with
Python dictionaries, and compares all finite-cut assignments with PySAT
Glucose4. Both cuts agree assignment for assignment. It also verifies the
absence of incidence cycles by component counts, rather than the producer's
union-find implementation. Independence is V1: both scripts were authored in
this task. The canonical knotlab checker supplies an additional maintained
implementation, not external review or V2 independent authorship.

A side-free control of two NAE knots sharing one distinction has 18 full
assignments, a four-member projected bond with 14 allowed states, and full
single deletions. Scalar enumeration, SAT and knotlab agree on that control.

The first executable shortcut arrived after 0.96 seconds inside the initial
producer run; the no-cycle search took 0.71 seconds to its witness. These
figures include loading the accepted corpus, but exclude agent/tool setup and
Python import. Work before signal was necessary support for exact
projection. The producer reports process high-water RSS 523836 KiB; table
sizes actually used were at most 13 variables in the bounded prior attempts.
Execution used one CPU process, no accelerator, and compact JSON outputs.

## Replay and limits

From the repository root:

```bash
.venv/bin/python -B experiments/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches/compare.py
.venv/bin/python -B experiments/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches/verify.py
.venv/bin/python -B experiments/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches/compare.py --acyclic
.venv/bin/python -B experiments/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches/verify.py --acyclic
```

Outputs are under the matching `artifacts/` experiment directory. Verification
invokes `PYTHONPATH=tools ... -m knotlab check --cnf ... --json`; the exact
commands and variable maps are saved in `knotlab_*.json`.

The declared strict-shortcut stop condition fired. The evidence refutes an
unqualified equality between ray and unrestricted same-pair minima in this
language. It does not exhibit unbounded ray growth with bounded unrestricted
bonds, change the family-wide minimum here, classify the 664 families, assess
finite flips, derive arithmetic counting, or establish a global lower bound.
No mutable BOND-DEPTH results, process state or partial runs were read.
