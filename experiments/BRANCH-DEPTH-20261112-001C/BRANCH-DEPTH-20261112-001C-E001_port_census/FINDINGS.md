# Which first branches forget their incoming values?

The inventory contains 664 sampled one-definition rules that die at a finite depth and have an allowed state in the usual infinite limit. Every one has at least two recursive calls. Use the first such call at each level. The target is a fresh distinction of that copy. A bond may use any finite collection of actual distinctions anywhere, including on side branches and beyond the target. In this record a knot-bond has at least three members. We report two-variable ties separately.

## Results

| Outcome among the 664 recorded rules | Count | What is established |
| --- | ---: | --- |
| Least size exactly three | 393 | A three-member bond reaches every positive depth. |
| Least size eventually exactly four | 39 | Size is at most four at every positive depth. At depth eight and beyond, three is excluded in every one of these records. |
| Least size grows linearly | 69 | At every positive depth a bond exists. Its minimum size is at least `1 + ceil(s/r)` and at most `s + 3`, with a rule-specific forgetting length `r`. |
| Linear lower bound only | 154 | Every existing bond at depth `s` obeys the same lower bound. The present construction leaves existence at every depth open. |
| Behavior at larger sizes unresolved | 9 | A three-member bond is absent at all sufficiently large depths. This study has no general rate for larger sizes in these nine. |

These are disjoint results on sampled **records**. They certify bounded size in 432 and linear growth with existence in 69. The uniform checks run to repetition of a finite mathematical state. No general frequency or exact growth coefficient is inferred. [Case-by-case outcomes](../../../artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/outcomes.json)

## Unobserved stretches

Use the accepted three-port usual-limit semantics. Sum over concrete local words, retaining NAE on the ports if a call passes the three ports through. Repeated existential restriction from the full port table gives the greatest fixed point. For an admitted local word, record its three input bits and the bits passed to its first recursive call. All other calls already have exact limit summaries. This is the relation for one unobserved level. Composition accounts for variables carried by identity. Its powers eventually repeat, and can be checked to the first repeat.

A power is rectangular when it is the product of its two projections. Then any incoming assignment realized on its left can be joined to any outgoing assignment realized on its right. Thus a minimal constrained set connecting the two sides cannot leave that entire stretch unobserved. Applying the argument successively forces the size bound. Of 219 rules with a rectangular power, only 175 have a power that is full on the original port-state space. In the other 44, some outgoing tuples disappear. All remaining tuples can still be combined independently. [General proof](../../../proofs/BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/proof.md)

| Least positive rectangular power | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 11 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Records | 28 | 83 | 36 | 41 | 17 | 5 | 1 | 8 |

## Chains that reach a fresh target

We enumerated transitions between port slots. A step can carry one variable by identity. It can also relate an incoming bit, a fresh outgoing bit and a distinct helping bit by one complement-closed three-variable bond. In the latter case we explicitly check that **every** admissible full incoming tuple gives exactly the same two-bit extension table as every other tuple with the same selected input bit. The helper may be a local of the copy or of a child off the specified branch. This condition proves the chain can be lifted through older variables and through the infinite side calls. A cycle containing a genuine three-variable step can end on such a step at every requested depth by starting at a suitable top port. Its projection is again a bond and costs at most one helper per level. The proof gives both the composition and lifting arguments. [Chain proof](../../../proofs/BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/proof.md)

There are 35 certificates using a cycle of length one, 16 using length two, and 14 using length three. In 34 of the 65 chosen certificates a helper belongs to a side child. The tested templates are sufficient conditions. Failing one of them gives no obstruction to a different upper construction.

## Three-member witnesses

For each of the 445 remaining rules, calculate the relation between the root and the target copy's port tuple by exact powers. Track which port occurrences still have the same identity as a root port. The pair of this identity map and the relation has a finite orbit. In every state of that orbit, search triples on the root, target copy, and, if required, one of its children. The projection conditions are exact for the whole infinite pattern, because every unopened child is summarized by its greatest fixed point. A different triple or top port can witness each depth.

Of the 370 records with a three-member witness at every positive depth, 363 use only the target copy and root, and seven of the certificates use a child of the target. The independent check replays 1,867 positive triple tables, including transient phases. All four distinct recorded masks pass the knot checker. A free triple and a triple with a constrained proper part fail it. Among all 445 rules tested here, 20 have a two-variable tie at every positive depth, including six without the all-depth triple certificate from this search. A tie does not pass the three-variable knot gate.

## Full test at size three and four-member certificates

The 370 immediately certified triples leave 75 nonrectangular cases. We ran the fixed-size procedure from leaf D on those 75 with budget three. It permits the third distinction to be at **any finite position** in the infinite pattern. The set of depths is computed to the exact repetition of its finite state. An additional 23 records admit a three-member bond at every positive depth. The other 52 eventually admit none. In these 52 the last positive depth at which a three-member bond was found is at most seven. The largest of these 75 fixed-size computations stored 10,832 unrestricted profiles. [Fixed-size theorem](../../../proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/proof.md) · [Exact per-case depth sets](../../../artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/fixed_three.json)

An additional four-member test opens either the target with one child, or its parent with the target as its first child. Combine the certificates phase by phase with the earlier triples. This gives an upper bound of four at every positive depth in 57 of the 75. Among them 18 were also settled at size three by the unrestricted procedure, leaving 39 genuinely different cases. Each of these 39 eventually has least size exactly four. In sample 0, line 4582, let y_s be the target local with index 4. The projection of (a,b,c,y_s) excludes exactly 0011 and 1100 at odd depths, and exactly 0010 and 1101 at even depths, in the written order. All one-variable deletions are free. A separately written SAT calculation agrees through depth 29, and the finite orbit proves the two tables repeat. In that record no three-member bond reaches beyond depth two, so the exact least size is four from depth three onward. The separate verifier replays 636 positive four-member projections. All thirteen distinct four-member tables pass the canonical test. [Four-member certificates](../../../artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/four_members.json)

## Ports that never occur in a constraint

A port is unused in a copy if the actual variable it receives occurs in no knot in that copy or any descendant. Compute this by starting at slots used in a local knot, then repeatedly propagating use back through each child argument list. There are only three slots. The resulting set contains exactly the slots that can reach a knot after finitely many calls. A pass-through knot, when present under the usual limit, must be included.

An unused occurrence can be dropped from the interface at that copy. A variable tied to observations on the earlier side is harmless in a port unused on the later side, since no later constraint can inspect that value. A selected root variable with this property everywhere is a free factor and belongs to no bond. After these slots are removed, the retained interfaces still contain every dependency necessary for gluing allowed states and for testing the exact lifts. In four further records the reduced port relation forgets after one or two levels, and an independently checked chain reaches the target at every depth in each. These four lie outside the 219 cases before reduction. This gives 223 linear lower bounds, and raises the number with matching order and existence from 65 to 69. [Unused-slot and chain certificates](../../../artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/silent_ports.json)

## Replay

Run the following from the workspace root. The generators rebuild the exact tables. The profile computation uses the repository Python environment. The verifier independently reads the source, enumerates tuple-valued assignments, replays the explicit witnesses and their recurrence periods, and tests the negative controls. The fixed-size saturation has its own controls in leaf D.

```sh
p=experiments/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census
python3 -B "$p/census.py" --write
python3 -B "$p/endpoints.py"
python3 -B "$p/chains.py"
python3 -B "$p/four_members.py"
python3 -B "$p/silent_ports.py"
.venv/bin/python -B "$p/fixed_three.py" --workers 6
python3 -B "$p/combine.py"
python3 -B "$p/verify.py"
```

All eight source file digests are in the [port tables](../../../artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/port_tables.json). The files contain 223,261 sampled records and eight metadata lines. Of 976 one-definition candidate records, 312 have an empty usual limit. The two algorithms recover the same remaining 664 and recheck their reported first finite deaths. [Three-member certificates](../../../artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/endpoint_tables.json) · [Chain certificates](../../../artifacts/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/chains.json)
