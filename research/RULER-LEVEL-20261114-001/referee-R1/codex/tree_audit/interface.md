# Independent audit interface

Owner: Codex tree-audit lane of RULER-LEVEL-20261114-001, 2026-11-15.

- Question: does Theorem A's one-placement construction always have its stated upper/lower uniqueness, acyclicity, connectedness and descending chains, and does an independent exact search agree with its stated reach on fresh finite cases?
- Branch/stage: code analysis; independent referee checks, no theorem inferred from sampling.
- Inputs: the proof and note, LEVEL-REACH's written specification, its prior independent referee's `fresh_pattern.py`, `fresh_search.py`, and `brute_audit/brute_supports.py`; the inherited referee address actions imported by these modules.
- Forbidden inputs: producer Python under this epic's exploratory directory, its proof family, and LEVEL-REACH's experiment family. No network. No Git mutations.
- Generation: seed `tree-referee-R1-fresh-20261115`; uniformly choose 1..5 states, each swap bit and successor, and three registered word indices; one plain, one append-0, one append-1 term. These are fresh tests, not the producer's original samples and not a population estimate.
- Outputs: exact descriptions, patterns' hashes/counts, structural property verdicts, independent exact-search records, malformed controls and runtime/resource data.
- Structural observable: full construction properties, checked through the classical incidence graph (the literature's graph on distinctions and knots), source-knot counts and explicit parent/child relations.
- Search observable: least minimal non-shattered support meeting each designated level; all distinctions at levels 0..N remain eligible. The inherited independent search has no forest/ruler shortcut.
- Controls: wrong tree-type constructions, two knots sharing a pair, a longer cycle with only single overlaps, disconnected and missing-parent patterns, and exact truth-table checks on tiny patterns.
- Decision: any failed positive property or exact disagreement is a defect to inspect; a control must be rejected by its applicable structural gate. An undecided search remains undecided.
- Resource ceiling: one compute process, RLIMIT_AS 2.3 GiB, native solvers in-process, fixed per-call search budgets; each invocation under 20 minutes. No subprocesses or network calls in the audit script.
- First signal: one fresh tree description at N=4,5,6; structural checks and exact searches with a small cap.
- Stop: finish the requested bounded referee tests; do not extend the scientific scope or repair producer files.
- Nonclaims: sampling is not a uniform proof, no census recount, no external novelty certification, no native contact/metric/complexity claim added.
