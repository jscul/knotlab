# Independent forest audit interface

- Scope: bounded referee lane inside epic `RULER-LEVEL-20261114-001`; no lifecycle or source changes.
- Question: does T1 give the exact least bond, searched over all supports, for every distinct pair in a finite unsigned 3-uniform incidence forest; and does A** apply correctly across levels?
- Branch and evidence stage: code analysis, exploratory independent validation of a symbolic claim. These finite checks cannot prove the uniform theorem.
- Inputs: the allowed proof/notes text; the preceding independent referee's `fresh_search.py`, `fresh_pattern.py`, and `brute_audit/brute_supports.py` for cross-checks. Fresh tests construct triples directly, without any producer builder.
- Forbidden inputs: every Python file under the current epic's `exploratory/`, the current proof family, and `experiments/LEVEL-REACH-20261114-001A/`; especially producer `pattern.py`. No network, Git mutation, or peer-task inspection.
- Primary observable: cardinality of the smallest inclusion-minimal non-full projection containing a distinct pair, or crossing two designated levels; `none` if no such support exists. Distance counts knot nodes on the incidence path.
- Comparators: independent complete truth-table support enumeration; inherited exact cardinality-SAT search; inherited brute SAT support enumeration and direct truth tables on small fixtures.
- Controls: one knot, paths, high-degree shared distinctions, disconnected patterns and isolates, within-level detours, duplicate-triple deduplication, two knots sharing two distinctions, and a Berge cycle. Malformed repeated-member triples reject.
- Resource ceiling: one compute worker, case memory 1 GiB, runner memory 2 GiB, each command below 20 minutes, no accelerator. All generated outputs remain in this directory.
- First executable signal: the within-level detour has a path without a descending chain and exact finite reach 5 across two levels.
- Stop rule: return exact counterexamples and a source-line audit; stop and report if the independent engines disagree or a forest violates T1. No new scientific target or producer repair.
- Nonclaims: no new theorem from enumeration, external replication, native-contact inference from the incidence representation, or assessed external novelty. Unmentioned addresses are isolated free coordinates and cannot enter a minimal non-full support.
