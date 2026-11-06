# Scoping for COPRIME-PAIRS-20261027-001D-E002 (diagnostics after E001; not evidence)

E001 (frozen, verdict **refuted**) failed only in A5's R4. In one of three path configurations, edge e₀'s solution set on the path
gadget differed from its single-edge set, while e₁'s equation values stayed constant. E001's R4 drew e₁'s private data at random,
off e₁'s own solution set. The clean-edge theorem claims locality only on the joint solution variety.

Diagnostics, post hoc:
- **A5, `diag_A5.py`, `diag_A5.log`.**
  - With e₁'s data on its single-edge solution set, e₀'s path sets equal the single-edge sets in 36 of 36 comparisons.
  - Off that set, they differ in 7 of 24.
- **A1, `diag_X1.py`, output in its docstring run.** On the variety, the zero-jump design gives 0 of 12 differences, and e₁'s
  equations vanish on every e₀ solution. The cumulative design gives 12 of 12 differences.
- **Normalizations.** Every vertex block reads 1 at its reading strand at every root character, in both gadgets, so the
  comparison is not a coordinate artifact.

E002 therefore tests the theorem's claim, locality on the variety, and keeps E001's off-variety failure as a control (X3).
