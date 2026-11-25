# Exact first-meeting projections

For each registered MOST trajectory, this calculation reads the actual first meeting of each eligible pair of parts. It checks the common distinction on each recorded route and projects the complete system after that meeting round. All actual knot rules appear in the conjunction, including the rules of retired knots. The visible places are one distinction held only at the first endpoint, one held only at the second endpoint, and the exact distinction (c) shared by the two roles. The program enumerates every such literal triple for every qualified route.

For each met or demand witness, (c) must occur in both of the witness's arms. For an actual cross take, the receiver's birth record must list (c) among the taken distinctions, and the opposing holder must have existed before the birth. The checker verifies these conditions against the digested producer support history. It emits separate incidence records for met and demand routes with disjoint arms. A first meeting without a pure opposite-endpoint route stays in the meeting count.

## Exact calculation

The not-all-equal solver receives two clauses per support, excluding the two constant words. It solves under one assumption word for each complementary pair on the visible places. Flipping every distinction preserves all not-all-equal rules, so a satisfiable result includes both words and an unsatisfiable result excludes both. The solver incrementally adds each round's rules and queries the prior stage before adding its next round. The complement argument applies separately to the two-place and three-place projections.

The even-parity method maintains a row basis over the field with two elements. For every nonempty subset of visible places, it checks whether the sum of those places belongs to the row space. These are exactly the linear equations valid on the visible projection. Every combination of visible values satisfying them extends to a solution of the full stage. The checker enumerates their bit mask directly. This gives a different implementation from the referee's reconstruction using the kernel.

Both methods cache each projected set of places within a complete stage. The emitted truth mask still follows the physical orientation of the endpoints, with indices (4a+2b+c). The receipt includes the exact earlier (ab) mask with indices (2a+b) if both distinctions existed before the meeting. The summary cross-tabulates truth classes by whether both earlier distinctions were jointly free, present with a restriction, or partly or wholly absent. This is a literal freedom test. Any claim about independently witnessed native recurrences needs evidence of the recurrences themselves.

## Reading the truth tables

The output retains the three pair projections. When the triple is constrained and every pair projection is full, it passes K1–K3. For the hub test, rejoin the (ac) and (bc) projections over their identical (c). A proper hub equals that join and has two informative arms. An arm is informative if its pair projection differs from the product of its single-place projections. A one-sided factorization has exactly one informative arm. The full relation, the empty relation, and the other constrained relations receive their own verdicts. The exact table also identifies constant or non-open roles.

The stock `knotlab check` command receives one exact CNF for every distinct observed mask. Each excluded word gives a clause that excludes just that word. The reported allowed table and the three knot-test flags are checked against the exact mask. The controls exercise joint parity and not-all-equal relations, a proper shared-(c) factorization, a one-sided factorization, a full relation, an empty relation, and split arms. One hundred small systems are additionally checked by exhaustive joint-state enumeration under both laws.

## Replay and receipts

`job.py` runs under the shared runner using the actual producer files. The runner configuration binds the frozen contract and source hashes. Each input support and event file is verified against its own digest. The literal archive and split-arm archive are streamed into content-addressed gzip files. Their SHA-256 digests cover the decompressed compact JSONL. The literal row order is `[case,kl,s,X,Y,t,route,w,u,v,c,a,b,mask,prior_ab_mask]`. Split-arm rows replace the last five fields with the two recorded arm sets. Each trajectory's wrapper names the growth rule.

`reconcile.py` checks each compressed receipt and compares its count and digest to the independent referee's reconstruction. It also compares the complete first-meeting and route keys, the split arms, and the literal-state counts. It reads the independent gzip members through their recorded offsets. The producer labels `group` and `demand group` correspond to the referee labels `met` and `demand`. Digest mismatches retain the first differing row. The stock canonical receipts are included with the reconciliation.

Run the targeted controls with the project virtual environment.

```sh
.venv/bin/python -B experiments/WIDENING-ROSTERS-20261125-001D/WIDENING-ROSTERS-20261125-001D-E001_links/projection/test_projection.py
```

## Result

| Test | Not-all-equal | Even parity |
| --- | ---: | ---: |
| MOST trajectories that matched independently | 205 | 205 |
| First meetings | 3,305 | 3,305 |
| Qualified routes | 301,387 | 301,387 |
| Split-arm routes | 37,371 | 37,371 |
| Complete literal occurrences | 34,906,524 | 34,906,524 |
| Full mask (255) | 34,906,524 | 34,906,524 |
| Both sides already existed and were jointly free | 324,062 | 324,062 |
| One side already existed | 5,991,106 | 5,991,106 |
| Neither side already existed | 28,591,356 | 28,591,356 |

Every qualified shared candidate was start-held. The literal occurrences come from 34,506,234 demand triples and 400,290 cross-take triples per law. Each allowed all eight words. The canonical command returned a full relation, with both binary arms full. The observed count of K1–K3 knots and proper hubs is zero.

The first-meeting census uses the complete reached prefix in each trajectory, including 32 guard-stopped trajectories per law. The run completed in 4 minutes 40 seconds. The maximum case took 192 seconds and used at most 250 MiB of case memory. The independent reconciliation took another 25 seconds. [Exact projection summary](../../../../artifacts/WIDENING-ROSTERS-20261125-001D/WIDENING-ROSTERS-20261125-001D-E001_links/projection/summary.json) · [Timing basis](../../../../artifacts/WIDENING-ROSTERS-20261125-001D/WIDENING-ROSTERS-20261125-001D-E001_links/projection/pre_run_timing.json)
