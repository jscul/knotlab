# Independent forest theorem audit

**Verdict:** Theorem A** is sound as its two clauses are stated. T1 supplies exactly the finite, disconnected, all-support result that A** needs. The summary requires narrowing: absence of a descending chain does not imply absence of a bond. No blocking defect in the uniform theorem argument was found.

Scope: referee lane of epic `RULER-LEVEL-20261114-001`. Only this directory was written. No forbidden producer Python was opened, imported or run; no network or Git mutation was used. The incidence representation here is a device for checking the supplied unsigned NAE constraints, not evidence for a native-contact claim.

## Findings and exact source lines

The A** source is `proofs/RULER-LEVEL-20261114-001A/RULER-LEVEL-20261114-001A-P001_forest_ruler/proof.md`. The T1 source is `proofs/RANDOM-FATES-20261112-001B/RANDOM-FATES-20261112-001B-P001_no_cycle_and_four_consecutive/proof.md`.

| Classification | Source | Finding and fix |
| --- | --- | --- |
| **Narrowing** | `research/RULER-LEVEL-20261114-001/ruler_level.md:14–16` | “Exactly where the knots form no cycle” incorrectly suggests necessity; that same note reports cyclic rulers at lines 19–21. “There is no bond otherwise” is also false if “otherwise” means no descending chain. Replace with A**'s exact two clauses, or the complete formula below. The explicit counterexample below has a path, no descending chain, and reach 5 across two levels. |
| **Not a block** | A**:18–27 | These clauses do not themselves assert the false converse. They are correct but leave the path-without-descending-chain case unstated. The complete formula resolves this case without a new hypothesis or method. |
| **Not a block** | A**:13–14 | The meeting wording is sufficient under the level-span assumption. Consecutive knots must share a distinction at the intermediate level; the two successive shared distinctions inside an internal knot have different levels. Nonconsecutive chain knots have disjoint level ranges. Thus the chain is an actual simple incidence path, not merely a succession of pairwise intersections at one distinction. For clarity write “for i ≥ 2, the i-th knot shares a distinction at level k+i−1 with the preceding knot.” |
| **Not a block** | T1:27–31, 93–101 | State “distinct vertices u,v”, equivalently d ≥ 1. If u=v, the asserted d+2 is not the right statement. A** already guarantees distinct endpoints because s ≥ 1. The d=1 case is explicitly handled by S=K1. |
| **Narrowing** | A**:57–59 and `ruler_level.md:27,34` | Keep the census qualifier. The fact that the enumerated acyclic cases have only the observed outcomes does not classify all possible forest patterns: detours give other finite reaches. Acyclicity universally excludes dead patterns by the leaf lemma; it cannot guarantee that a particular algorithm avoids `undecided`. The direct/other exclusions in this census also use the observed chain/path facts. This lane did not recompute the census. |

No `Block` finding applies to A** or to T1 for distinct endpoints.

## Complete across-level statement

Let V_j be the addresses at level j. For a finite unsigned 3-uniform Berge-acyclic pattern whose knots span at most one level step, put

`D_k(s) = min { d(u,v) : u in V_k, v in V_(k+s), u and v in the same component }`,

where d counts knots on the incidence path. If that set is empty, no bond crosses the two levels. Otherwise

`L_k(s) = D_k(s) + 2`.

For every connected pair the lower bound is T1, with all bond supports allowed. Conversely T1 constructs a bond of size d(u,v)+2 for a minimizing pair, so minimizing over pairs is legitimate. In particular D_k(s) ≥ s. Equality holds exactly when an s-knot descending chain exists: the level increments along an s-knot path summing to s must all be +1. Hence A**'s ruler clause is equivalent to D_k(s)=s. If a path exists but no descending chain does, then D_k(s)>s and the finite reach is strictly greater than s+2.

## Exact counterexample to “no bond otherwise”

Take all binary addresses of lengths 0 through N=3. All unmentioned addresses are isolated. The three unsigned NAE knots are

`{'0','00','01'}, {'00','10','11'}, {'10','000','001'}`.

The middle knot is within level 2. The incidence pattern is a path with three knots. From level k=1 to level 3, s=2, the two cross-level knots do not meet, so no two-knot descending chain exists. The minimum incidence path has three knots and

`L_1(2) = 5`.

The crossing bond is `{'0','01','11','000','001'}`. In that order the assignment `(0,0,1,0,0)` has no extension: the first knot forces `00=1`, the second forces `10=0`, and the last is then all zero. Every proper projection of this five-member set is full. Complete truth-table enumeration finds exactly 54 states and six bonds on the seven active distinctions; this is the only bond crossing levels 1 and 3. The eight remaining addresses are free isolated coordinates, and adding a free coordinate to a non-full support cannot make it minimal. The full 15-address universe was also tested directly by both inherited exact SAT engines, with all level-1 and level-3 addresses allowed as endpoints; both return 5.

## T1 proof audit

| Source lines | Audit |
| --- | --- |
| T1:11,13–21 | Unsigned NAE and 3-uniformity are explicit. The no-cycle definition includes two knots sharing two distinctions and is equivalent to incidence-forest acyclicity. The steps-apart count is exactly the number of knot nodes along the incidence path, not the number of incidences. |
| T1:27–31 | Explicitly finite, permits several components, and quantifies over vertex sets whose every proper subset is unrestricted. No restriction to a preselected path support is present. |
| T1:47–50 | Removing a knot with a private unobserved distinction preserves extendibility because that distinction can always be reset to satisfy NAE. Other constraints are unchanged. |
| T1:55–57 | A furthest knot in a finite incidence tree has at least two private distinctions. Iteration establishes a state in every component, including a single knot; isolated distinctions are independently free. |
| T1:59–65 | Each part outside the minimal span meets it in at most one distinction; two meetings would make an incidence cycle. Rooted leaf removal avoids all observed distinctions. Components disjoint from the span are separately satisfiable. This also handles T({w}) using the explicitly retained distinction w. |
| T1:67–81 | A bond cannot occupy multiple independent components: each component part is a proper, hence full, projection and their product is full. A span-leaf distinction omitted from a bond lets the knot be removed; in a leaf this leaves a smaller constrained subset, and internally it separates the failing assignment into one of two proper parts. Thus all span-degree-1 distinctions belong to the bond. The one-knot case is explicitly covered. |
| T1:83–92 | A connected span of t knots has 2t+1 distinctions and total excess incidence t−1; at least t+2 distinctions have span degree 1. For any bond holding u,v, its span contains their d-knot path, giving |S| ≥ t+2 ≥ d+2. This applies to all possible bond supports, including supports outside the endpoint path and beyond a queried level. Complement closure plus existence makes single distinctions free. The pair and faithful-triple consequences follow. |
| T1:93–101 | The unique path has distinct link and off-path distinctions; otherwise there is an incidence cycle. Its d+2 leaf distinctions have the displayed nonextendible alternating assignment. Removing any one frees a variable in one path knot: propagate from both ends and then choose it. All assignments on that deletion extend, and the span lemma extends to the whole finite forest. This proves minimality, not only non-fullness. For d=1 the knot itself has all proper projections full. |

## A** proof audit

| Source lines | Audit |
| --- | --- |
| A**:10–14 | Finiteness follows from addresses through finite N. Use a set of three-member knots; duplicate occurrences impose the same constraint and must be deduplicated before incidence testing. A repeated-member triple is outside the assumptions. |
| A**:18–20 | Both conditional clauses are valid for all components. They are not an exhaustive dichotomy unless an additional fact rules out detours. |
| A**:22–24 | T1 has exactly the required finite-forest, unrestricted-support and disconnected-component scope. No connectedness or fullness assumption was silently added. |
| A**:24–27 | Every knot changes level by at most one, so every cross-level path uses at least s knots. The stated descending chain is an s-knot path, so it attains the lower bound. Minimizing the pairwise T1 formula proves s+2. No monotonicity in N is needed. |

## Independent computation

`job.py` derives models directly from unsigned NAE triples, then enumerates minimal non-full supports with exact truth-table column bitsets. Incidence checking, all-pair distances and literal descending-chain tests are separate fresh logic. No forest theorem shortcut enters bond calculation. `crosscheck_job.py` then applies the inherited cardinality-SAT existence circuit and brute support/projection methods, without importing producer code.

- Every labelled forest on seven distinctions, including isolates: **1,156 patterns, 24,276 distinct pairs, 5,530 bonds**, no violation of T1, satisfiability, no-tie or faithful-triple claims. There can be at most three knots on seven distinctions, so enumeration through three knots is complete.
- **120 random forests on 5–13 distinctions**: 4,474 pair minima and 423 level queries, no T1, complete-formula or descending-chain-equivalence violation. These include 77 patterns with multiple components, 75 with within-level knots, and two path-without-descending-chain level queries.
- The inherited exact cardinality-SAT search independently agrees on **all 423 random level queries**. The earlier direct truth-table enumerator agrees on the **complete bond families of 20 small random patterns**. All 11 controls agree across exact engines.
- Positive controls cover one knot, two- and three-knot paths, a distinction in four knots, disconnected components, isolates, within-level detours, and nonmonotone endpoint paths. A duplicate triple is deduplicated without changing semantics. A repeated-member triple rejects.
- Negative controls: two distinct knots sharing two distinctions reject incidence-forest membership and **violate** the T1 pair formula (the two private distinctions have distance 2 but no bond). A three-knot Berge cycle also rejects forest membership; it happens to satisfy the pair formula, illustrating that acyclicity is a sufficient hypothesis, not a necessary one.

All runs used the required `.venv/bin/python -B` via `scripts/longrun.py`, one compute worker, 1 GiB per case and 2 GiB runner ceiling. Sixteen cases finished in roughly 1.4 aggregate case seconds; peak observed memory was under 30 MiB. These are V2 same-task independent reimplementation checks, not external replication or a substitute for the symbolic proof.

## Prior-work note and artifacts

Unverified own-knowledge background only: tree-structured constraint elimination is a likely nearest classical setting, but that general method does not by itself establish the NAE-specific exact d+2 minimal-support count. A** is an elementary application of T1 and the integer-level bound; it should not claim an independent general theorem advance. No external novelty search was performed, and T1's exact external novelty remains unassessed in this lane.

Raw results: `run/results.jsonl` and `crosscheck_run/results.jsonl`. Digest-bound compact result: `results.json`, rebuilt by `summarize.py`. The runner configurations bind both executable jobs by SHA-256. `interface.md` records scope and exclusions. All retained outputs are small audit evidence; no disposable source copies or build trees were created.
