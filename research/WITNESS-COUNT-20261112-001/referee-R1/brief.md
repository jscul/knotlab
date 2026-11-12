# Referee brief WITNESS-COUNT-R1 (from the coordinator, 2026-11-12, lean)

**The epic.** `WITNESS-COUNT-20261112-001`, closed referee pending: pre-registration 6be19d282, amendment 92403fb31, epic df821f984,
goals and notebook 17ba9a9e0.

**Files.** The code is `experiments/WITNESS-COUNT-20261112-001A/.../census.py`, which imports LIMIT-STATE's census and `dlang.py`.
The data is `artifacts/.../runs_*.jsonl` and `summary.json`.

**Claims** (exact per family; census frozen; the amended code grows a bounded totalizer by doubling):
- **The gate.** A_t and B_t are lower bounds on w_t, with 0 violations.
- **P1 failed.** w = B at T+1 and T+2 in 69 of 593 one-definition families.
- **P2 failed.** One state attains all three least counts in 107 of 798.
- **Reported.**
  - w_T: 1 (418), 2 (213), 3 (68) and so on.
  - Median w/N: 0.025, 0.031 and 0.033.
  - Laws: fixed share 733, between 61, constant 3.
  - 9.6% of the witnesses at t+1 sit inside a depth-t witness.
  - 4 families need a single witness per depth, 9 have A = 1 but w ≥ 2, and A = w in 15 of 205 multi-definition families.

**Points to check.**
- B's recursion and the totalizer search (rhs indexing, bound check).
- The joint query, and that the amendment changed memory only.
- If cheap, where the excess over B comes from: distinctions shared between copies, or again by construction.

**Report.** Send the verdict.
