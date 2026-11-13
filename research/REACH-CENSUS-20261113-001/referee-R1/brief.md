# Referee brief REACH-CENSUS-R1 (from the coordinator, 2026-11-13, lean, Codex-assisted)

**The epic.** `REACH-CENSUS-20261113-001`: commits 5605bec51, 3e7c1e0ef, beabed341, 2b2cde04c, and G3 folded in at edfca63ce.
The study's code is Codex-written, so the recheck uses fresh code without the study's codex/ folder.

**Claims** (computed):
- **Over 223,261 draws.** 58.4% of the weight has no depth by construction, and 79.8% no ray bond at large depths.
- **Where a ray bond persists.** It is bounded in about 70% and grows in about 30%. P1, P2 and P3 held.
- **The logged correction** (Narrowing): growth along the first ray is not growth with depth. 131 of 224 growers are bounded along
  the last-call ray.

**Points to check.**
- The multi-definition path. G3 finished 139 of 150; the 11 largest did not.
- The crash and the rerun.
- The 813 unresolved draws.
- Settled by construction, including the 70/30 split.
- Count against weight, and one-sided bounds.
- Whether the Narrowing should be a Block.

**Addendum** (from another thread). On the last-call ray, 99 of the 131 bounded families carry a top port by identity. How should
the Narrowing be worded?
