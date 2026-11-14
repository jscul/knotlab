# Relation-free bond locations

**Verdict: the residual 65 are not a proved middle-member mechanism.**

All 65 families were included in the small-depth panel. The SAT search uses the
permitted earlier referee code, exact usual-limit boundaries and no per-call
transfer relations or study TOP Python. Fresh code records allocating copies,
including side-subtree addresses, and rechecks every positive support with
MiniSat22, separately from the search backend.

The primary files contain 192 cells: {'exact_prefix': 185, 'timeout': 4, 'skipped_exponential_copy_estimate': 2, 'lower_bound_only': 1}. There are
159 globally exact size-three minima and
26 exact finite-prefix size-four minima.
Another 1 size-four prefix minimum follows by joining a completed
size-three exclusion with a separately verified endpoint-only size-four bond.
A size-three witness is globally least because every possible main-port/target-own
pair has already been exhausted, and a two-member support has no auxiliary
member that could hide outside the prefix. A size-four prefix minimum has no
such closure; an unsearched distant third member could in principle lower it.

| Family | Stratum | L(3), L(4), L(6) | Allocation depths in chosen depth-6 bond |
| --- | --- | --- | --- |
| `b192b55035ef` | I | 3, 3, 3 | [0, 5, 6] |
| `e116b187edca` | I | 3, 3, 3 | [0, 5, 6] |
| `fd60333c5872` | I | 3, 3, 3 | [0, 4, 6] |
| `5ad70189f383` | O | 4*, 4*, 4* | [0, 0, 3, 6] |
| `15c6dd3cfa20` | O | 3, 3, 3 | [0, 5, 6] |
| `5ceea39607cb` | O | 3, 4*, 4* | [0, 2, 5, 6] |
| `fea4933ecaf1` | O | 3, 3, 3 | [0, 0, 6] |

* means a finite-prefix minimum, not a global minimum proof.

Every row stores its actual IDs, allocating depth, address, signed difference
from the target level, and side-subtree attachment/descent if applicable.
The chosen primary witnesses have no side allocations; that is a property of
the returned witnesses, not an exclusion theorem for other least bonds.

**Block for the claimed necessity of middle members.** Independent word CNF
checks at depths 8,9,10,11,12,13,20,50 found root/target-allocation-only bonds
in `fea4933ecaf1`, `fd60333c5872`, and `5ceea39607cb`. The independent
`pinning_window_results_toponly.json` supplies complete eventual finite-Q
certificates (rather than extrapolating the finite word roster). In particular
`fea4933ecaf1` has eventual global least value 3 and allocations [0,0,s].

**Narrowing of what was tested.** The named numerical localisation window
depends on C and m!. Interior members at these tiny depths do not refute it.
The synthetic example in `localisation_audit.md` instead gives a genuinely
nonlocal least bond beyond its explicit threshold and also a local least bond.

**Preserved limits.** Case 62 at depth 6 was interrupted in two owned runs
after its solver overran a soft cell timeout; no result is inferred. The
completed rows survive. Remaining small cases used limited Glucose; an
interrupted call raises SearchTimeout, never an UNSAT verdict. Two high-branching
depth-6 cells were skipped by the predeclared copy-count estimate; two final
deep cells were not started. Other soft timeouts remain explicit in the JSON.
No interrupted/capped/missing cell is used as mathematical negative evidence.

See `middle_summary.json` for exact counts, all missing cells, retries, timing
and hashes; `middle_bonds_soft_timeout.py` preserves the byte-identical earlier
producer version for the first primary files. The code remains within the
requested referee directory; no network, Git mutation or publication was used.
