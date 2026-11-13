# A strict aggregate shortcut: four to three

The bounded supplement found an exact reduction in the minimum over **all**
eligible endpoint pairs: at depth two, the least ray-supported bond has four
members, while the true least unrestricted bond has three. The ray has no
cycle of knots. This resolves the aggregate question left unanswered by the
earlier fixed-pair examples; those records and their receipt are unchanged.

Evidence stage: exploratory exact relation certificates. Validation:
V1 separate-algorithm enumeration and SAT, plus canonical knotlab K1-K3.
Finite-flip sources at infinity remain unassessed.

## Census member and exact limit

The accepted LIMIT-ONLY input is
`artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only/sample_5.jsonl.gz`,
line 11064, rank five in the predeclared size/file order. It has one definition,
three ports, two own distinctions, three SELF calls and one NAE knot:

```text
D(a,b,c): own x,y
    D(c,a,x)       # first SELF: ray
    D(x,c,a)
    NAE(y,a,c)
    D(y,x,b)       # third SELF: shortcut below
```

Independent tuple-valued port-table iteration yields greatest fixed point
TOP, all eight states. This is an exact summary, not assumed free truncation:
given arbitrary a,b,c, choosing y=1-a satisfies the local knot, and every
child port state is admitted at TOP. This choice recursively extends each
finite-cut completion. No SELF passes through the original three ports, so
the usual limit and bottomless semantics agree by the accepted NEST-COUNT
result. Independent finite-depth iteration finds its first death at depth
four, reproducing the accepted genuine limit-only classification.

## Matched comparison over every eligible endpoint

The root has own x0,y0. The first ray child has ports (c,a,x0) and own x1,y1.
The second has ports (x0,c,x1) and own x2,y2. The exact ray cut imposes:

```text
NAE(y0,a,c)
NAE(y1,c,x0)
NAE(y2,x0,x1)
```

The endpoint set is all six pairs in `{a,b,c} × {x2,y2}`, exactly the stated
top-port/own-depth convention. The nine-variable ray cut has 216 allowed
assignments. All six two-member supports and all 33 distinct three-member
supports containing any eligible pair are full. Their complete tables and
an allowed-state completion for every row are retained. This excludes every
eligible ray bond of size at most three.

A ray bond of size four exists: in order `(c,x1,y1,y2)`, its projection is all
16 states except `0101` and `1010`. Each of its four single deletions is full.
Consequently the aggregate ray minimum is **exactly four**.

Expand the second ray copy's third SELF once. It is D(y2,x2,c), with own z,w,
so its knot is `NAE(w,y2,c)`. Every unexpanded call still receives the exact
greatest fixed point. The eleven-variable side-expanded cut has 624 allowed
assignments; its projection onto the nine ray variables equals the entire
ray-cut relation.

In order `(c,y2,w)`, the resulting bond allows exactly
`001,010,011,100,101,110`. All three single deletions are full. Each eligible
two-member endpoint support remains full by the unchanged ray projection.
Thus the true unrestricted aggregate minimum is **exactly three**, even when
arbitrary further branch supports are admitted: a bond of size two containing
an eligible pair could only be that pair, whose full table is already known.

The ray incidence has no cycle. The added side knot creates a cycle in the
larger meeting pattern; the verdict nevertheless comes from the allowed-state
tables and the canonical K1-K3 check, not that incidence cycle.

## Coverage and independent checks

`AGGREGATE_PLAN.md` was written before running. Its ceiling was the first 64
of 664 genuine branching one-definition limit-only members at depths one to
four, with explicit variable caps, stopping at the first strict aggregate
shortcut. The stop fired after reaching the fifth family:

- 18 family/depth cases: four ray cuts with cycles and fourteen without.
- 13 cases already had a direct three-member ray bond across eligible
  endpoints, precluding a strict reduction to three there.
- Five cases lacked any eligible ray bond of size two or three; 33
  one-side-copy cuts were read before finding the shortcut.
- No ray-variable or side-variable cap was reached. The largest attempted
  cuts had 13 ray variables or 15 side-expanded variables.
- Search time inside the producer, including corpus loading: 1.13 seconds.
  This excludes Python imports and agent/tool setup. One CPU process was used.

The verifier imports none of `aggregate.py` or the producer's semantic
functions. It uses the earlier independent tuple-valued fixed-point and
dictionary-assignment implementation. All **512** ray assignments and **2048**
side-cut assignments are checked against PySAT Glucose4 and the producer's
retained models. All agree, with 216 and 624 models respectively. The verifier
independently regenerates all 39 cheaper-ray-support tables, verifies every
single deletion, and feeds the two projected relations to the knotlab CLI.
Both pass K1, K2 and K3. The earlier side-free two-knot control is rechecked:
18 full assignments, a four-member projected bond with 14 allowed states,
full deletion tables, and knotlab acceptance.

The old receipt and every file whose digest it records are checked unchanged.
New outputs are `aggregate_coverage.json`, `aggregate_witness.json`,
`aggregate_verification.json`, `knotlab_aggregate_*.json`, and the separate
`aggregate_receipt.json` under the matching artifacts directory. No mutable
BOND-DEPTH inputs or process state were read.

## Replay and conclusion

From the repository root:

```bash
.venv/bin/python -B experiments/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches/aggregate.py
.venv/bin/python -B experiments/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches/verify_aggregate.py
```

This is an exact aggregate gap at a fixed depth in a genuine limit-only
census member, not only a hand fixture or a fixed-pair improvement. It
establishes that the ray restriction can alter the aggregate observable. It
does not show unbounded ray growth with bounded global bonds, establish an
asymptotic growth classification, estimate a frequency, assess native finite
flips, or derive arithmetic counting. The declared first-strict-example stop
condition fired, so the remainder of the bounded roster was not run.
