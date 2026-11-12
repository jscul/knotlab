# Referee brief LIMIT-STATE-R1 (from the coordinator, 2026-11-12, lean)

**The epic.** `LIMIT-STATE-20261112-001`, closed referee pending: pre-registration 9a97fb05e, epic 1a31d8231, goals and notebook
f0dd73906.

**Files.**
- `preregistration.md`, `limit_state.md`, `advisor_review_*.md`.
- The code is `experiments/LIMIT-STATE-20261112-001A/.../census.py`. It reads LIMIT-ONLY's `sample_*.jsonl.gz` and imports `dlang.py`.
- The data is `artifacts/.../runs_*.jsonl` and `summary.json`.

**Claims** (exact per family; census frozen):
- **The usual limit.** 894 genuine families reproduced. The thread splits them by pass-through call as 812 without and 82 with,
  against the referee's 821 and 73; the total agrees.
- **Gates.** The restriction lemma holds at every dead depth read, and every finite part read is alive.
- **Loose.** 87% are loose.
- **Single.** Of the 801 families read, 800 branch. "Single" (exactly one all-equal call at each of depths T to T+2) is possible in
  3 (P1 failed). A single ray is possible in 2 (P2 failed). No loose branching family allows single (0 of 702).
- **Calls.** The median number of calls per depth is 64, 256 and 1,296.

**Points to check.**
- The depth indexing of calls against the lemma, and the parent links.
- Whether "exactly one per depth" already fails at depth T alone.
- The difference in the pass-through split.
- Whether "must spread" is settled by the definition rather than by the patterns.

**Report.** Send the verdict, with every fix marked Block, Narrowing or Not a block.
