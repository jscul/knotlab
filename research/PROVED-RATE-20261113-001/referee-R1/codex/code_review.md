# Fresh reconstruction code review

Scope: `epic PROVED-RATE-20261113-001`, referee-R1. This is a separate
source-review lane within the same task. It is advisory code-analysis evidence,
not an independent empirical replay or a theorem about the underlying families.

**Result: no demonstrated semantic defect** in the requested operations.
Reviewed `recompute.py` SHA-256
`7a6ebb724574a8ed00f66d930b8c6f19c691c05e8085233a2e456cfcb4b9705a`
against the frozen `../../codex_spec.md` and the permitted BOND-DEPTH
`census.py`. The forbidden study implementation and its logs were not read,
imported, or executed. No family computations or synthetic controls were
duplicated in this lane; the lead owns those checks.

| Operation | Review evidence |
| --- | --- |
| Bitset advance (`recompute.py:80`) | An outer bit at position `R` represents membership of interface mask `R` in the original frozenset. `make_images` takes the union of table images over the set bits of `R`. Removing one item of `W` and enumerating all remaining assignments yields exactly the original forget-one tables after their duplicate assignments are removed. Taking unions over these tables preserves both clauses of the original update of `Gf`. |
| Greatest fixed point (`recompute.py:139`) | The map existentially enumerates local assignments while enforcing every `K` and every `SELF` call. It is monotone in the boundary relation. Iterating from all eight port states is descending and terminates at its greatest fixed point. The middle relation omits only the first `SELF`; the closing relation enforces it as well. The permitted BOND-DEPTH file delegates its limit calculation to `depth_sequence`; that helper's implementation was outside this review's reading boundary. |
| Start and close (`recompute.py:155`) | Starts range over precisely the subsets containing a port; middle subsets include the empty subset; closing subsets are nonempty and local. Closing operations are ordered by cardinality, so the first accepting cost is the minimum. `(F & 1)` means that `F` contains interface mask **zero**, exactly the frozen `0 in F'` condition. If the incoming `Gf` already contains zero, every table preserves that empty image, so the early rejection in `close` is sound. |
| Reachability and trimming (`recompute.py:190`) | Breadth-first enumeration begins with all start states. Thus reverse reachability from finite-close nodes gives exactly the required reachable and co-reachable restriction. The two iterative DFS passes implement Kosaraju on that restriction. A non-singleton SCC is cyclic, and a singleton is admitted only with a self-loop. |
| Exact cycle means (`recompute.py:263`) | Each cyclic SCC is isolated before the integer length DP. Initializing length zero at every state gives the standard all-sources form of Karp's minimum-over-states, maximum-over-shorter-lengths expression. Singleton SCCs directly minimize self-loop costs. All ratios and the final minimum use `Fraction`; floats are output only. The finite sentinel exceeds possible path costs at the declared graph cap and these block cardinalities. |
| Empty-subset cycles (`recompute.py:280`) | Subsets are ordered by cardinality, so row zero is precisely the unique zero-cost empty-subset action. The explicit assertion checks this invariant. Functional-cycle enumeration over the full reachable graph, followed by selection of the cycles reached from trimmed nodes, implements the frozen `bounded_all` condition. A cycle outside the trimmed set cannot pass the finite-close test. |
| Exact eventual bound (`recompute.py:319`) | Every zero-cost cycle consists of empty-subset steps. With `P` their productive lengths' least common multiple, visiting a productive zero-cycle state permits insertion of any multiple of `P` at zero extra cost. Product reachability tracks state, middle-length residue, and whether such a visit occurred, retaining arbitrary entry and exit paths. One accepting representative for every residue therefore gives the reported finite threshold and uniform cost bound. Conversely, bounded-cost arbitrarily long accepting walks must contain a zero-cost cycle because positive costs are integers. A missing residue rules out eventual boundedness; a product-size gate returns `None`, not a false result. |
| Depth indexing (`recompute.py:370`) | The start layer is closed before its first middle step. Therefore the first replay entry is depth `s=1`, and entry `s` uses exactly `s-1` middle steps. The residue calculation uses middle length `n` and correctly reports depth `n+1`. |

The label `bounded_all` follows the specification's sufficient-cycle condition.
By itself it guarantees a bound after access to a suitable cycle, rather than
proving that every earlier depth has a finite accepting value. Any claim about
all depths must also check those finitely many earlier depths. This is an
interpretation caveat, not a discrepancy in the implementation of the frozen
Boolean rule.

Validation in this lane: Python 3.13 AST parsing passed using the repository
`.venv/bin/python -B`; no bytecode or experiment outputs were created. The
review did not independently exercise the algorithms. Resource failures from
the referee remain failures, rather than evidence of agreement.

Reviewer `CODEX_THREAD_ID`: `01a1d322-109a-7f71-9ef6-37cb021f88ec`.
