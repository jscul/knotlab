# Referee brief ROW-NEST-R1 (from the coordinator, 2026-11-12, light check)

**The epic.** `ROW-NEST-20261112-001`, closed referee pending: pre-registration 47e0312fe, epic f22364e64, goals and notebook
f2c4ce722.

**Files.** The code is `experiments/ROW-NEST-20261112-001A/.../census.py` (self-contained, pysat). The data is `artifacts/.../runs_*.jsonl`
and `summary.json`.

**The setting.** Exhaustive over the 1,024 window-1 NAE rules: the first row has 3 distinctions, rows grow by one, the bottom row
is closed by knots on consecutive triples, and depths run from 1 to 40.

**Claims.**
- **Q2 held.** No rule has an unexplained alive(t) or first-row relation T_t.
- **Q3 failed.** There is no harmony, that is, no period of 2 or more.
  - Life is constant in 910 rules and eventually constant in 114.
  - T_t is constant in 787 and eventually constant in 237. It last changes at depth 1 (186), 2 (43) or 3 (8).
  - Given at least one knot, 96% of the weight has constant life and 92% a constant T_t.
  - 126 rules are dead at depth 40, all with five or more knots (7% of the weight given at least one knot).

**Points to check.**
- The construction: relative positions and dropped end knots.
- The closing row as the analogue of the depth-1 knot.
- The period classifier.
- Mainly, whether the rule class is too narrow to show counting by its own definition.

**Report.** Send the verdict.
