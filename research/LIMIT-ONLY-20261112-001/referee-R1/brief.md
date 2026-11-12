# Referee brief LIMIT-ONLY-R1 (from the coordinator, 2026-11-12, lean)

Epic `LIMIT-ONLY-20261112-001`, closed referee pending: pre-registration 041ec89b5, epic 0e1b37c53, goals and notebook fc18054f9,
correction df05c9913. Files: `preregistration.md`, `limit_only.md`, `DESIGN_NOTES.md`, `advisor_review_*.md`; code
`experiments/LIMIT-ONLY-20261112-001A/.../census.py` (imports SHORT-DESC's `dlang.py`); data `artifacts/.../{exhaustive,sample}_*.jsonl.gz`
and `summary.json`.

Claims (exact per family; census frozen):
- **G1, the gates.** L1 has 0 exceptions. L2 has 0 failures where the knot and its image compare (proved for up, down and equal).
- **E** (516,880 one-definition families):
  - none dies;
  - no family is down;
  - L2 fails in 1,320 incomparable families (1,296 fixed point outside the knot, 24 period above 1).
- **W** (223,261 families):
  - 1,341 live only in the limit (0.6%), which is 56% of the 2,381 that die (P4 held);
  - 38% are down and 62% incomparable (P3 failed);
  - limit kinds are 94% free, 5% knot and 0.6% tied;
  - 10 have no K (counted after the run);
  - L2 fails in 310 of 2,440 incomparable families (P2 held).
- **The logged correction.** "Allows", not "needs" (Not a block).

Points to check:
- **The limit notion.** Is it sound, given that compactness forbids "dead at every finite level, alive in the limit" under the usual
  definition?
- **The proofs.** The up and down proofs.
- **Exactness.** That E's "never dies" is exact.
- **The count.** The no-K count, made after the run.
- **Construction.** What the language settles by its own definition.
- **Known against new.**

Report: a verdict with every fix marked Block, Narrowing or Not a block. No Monitor tool.
