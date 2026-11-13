# Referee brief TRUE-BOND-R1 (from the coordinator, 2026-11-13, lean, Codex-assisted, small load)

**The epic.** `TRUE-BOND-20261113-001`, closed referee pending: pre-registration and spec 3709fddce, epic 2d3d83a7d, goals and
notebook ac408946a.

**Independence.** The study's code is Codex-written, so the recheck uses fresh code without the study's codex/ folder. Another
census was running, so the load was kept small.

**The question.** On the 226 families whose ray bond grows linearly, does the growth survive side branches?

**Claims** (computed):
- **The gate.** It passed under the uniform-depth truncation the owner settled on.
- **The runs.** 37 done, 163 timeout, 18 memory, 6 incomplete ray, 2 errors.
- **P1 failed.** At least 62 families are shortened.
- **P3 held on the 37** (L12 > L6). All 75 reaching depth 8 or more grow.
- **P2 undecided.**
- **Some deficits grow:** 0, 1, 1, 2, 2, 3, 3 in four families.

**Points to check.**
- The truncation convention, timeouts and the cost cap L_ray − 2.
- Whether the 37 are a biased subset, and the 2 errors.
- That nothing is worded as holding at all depths or as typical.

**Report.** Send the verdict, with fixes marked Block, Narrowing or Not a block.
