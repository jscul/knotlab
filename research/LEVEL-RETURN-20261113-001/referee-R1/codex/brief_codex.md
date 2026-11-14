# Independent recomputation and critique: LEVEL-RETURN-20261113-001

You are an independent referee's assistant. Recompute with **fresh code**.

## Rules for this task

- **Do not open or import any `.py` or `.c` under** `experiments/LEVEL-RETURN-20261113-001A/` or
  `proofs/LEVEL-RETURN-20261113-001B/`, nor `research/LEVEL-RETURN-20261113-001/summarize.py`. You may read their data (JSON, JSONL,
  CNF and LRAT proof files in `run3/` and `run_rigid3/`, `gates.json`, `result.json`), `research/LEVEL-RETURN-20261113-001/{level_return.md,
  preregistration.md, summary.json, advisor_design_*.md}`, ADDR-KNOTS's spec `research/ADDR-KNOTS-20261113-001/codex_spec.md`, and
  the earlier referee code `research/ADDR-KNOTS-20261113-001/referee-R1/codex/` (its fresh pattern builder and RUP checkers; reuse
  them).
- Write **only** inside `research/LEVEL-RETURN-20261113-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 60 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/LEVEL-RETURN-20261113-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

1. **An independent check of the refutations.** For a sample of the dead verdicts at levels 13 to 16 (all of the seven alternating
   patterns' dead levels, then others), rebuild the CNF yourself from the description (ADDR-KNOTS's spec) and check that it equals
   the CNF the proof refers to (up to clause order). Check each LRAT (or DRUP) proof with a checker that is **not** the study's:
   your own RUP checker that ignores hints, or the earlier referee's `check_rup_fast`. For every alive verdict in the sample, verify
   the model against every knot.
2. **R2, the all-level statements.** For #2 (address parity a state at every odd level ≥ 3) and #3 (first letter XOR last letter a
   state at every even level ≥ 2): check them directly at every level up to as high as is cheap (vectorised, for example to level 22
   or more), with knots on distinct images only and with the identity word among the placements as the description gives it. Then
   give your own all-level argument (for example a finite product automaton over the three runs and the state's automaton, written
   from scratch), and say whether the study's statement handles the identity word and knots dropped for coinciding images correctly.
3. **R4, "exactly two knots".** At even levels, count the knots of #2 that its parity violates, as far up as is cheap, and check they
   are exactly those at 0^(n−2)10 and 0^(n−2)11 of one placement. Say whether your product automaton proves it for all even n.
4. **R5, rigidity.** For #2's pattern with those two knots removed, at a few even levels (6 to 12 at least), decide whether its only
   states are parity and its complement (for example SAT with a blocking clause, certified). Check the implication "rigid at level n
   implies dead at level n" and whether rigidity at every even level could follow from a finite argument.
5. **Wording.** What is proved, what is certified to level 16, what is computed. Is anything stated beyond the levels read?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
