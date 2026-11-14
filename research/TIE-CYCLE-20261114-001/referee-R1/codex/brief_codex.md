# Independent recomputation and critique: TIE-CYCLE-20261114-001

You are an independent referee's assistant. The study's code is the thread's own, so a fresh implementation is the independent
check.

## Rules for this task

- **Do not open or import any `.py` under** `experiments/TIE-CYCLE-20261114-001A/`. You may read its `heldout.json`,
  `research/TIE-CYCLE-20261114-001/{tie_cycle.md, preregistration.md, advisor_review_answer.md}`, the earlier referee code and data
  under `research/FORGET-RULE-20261114-001/referee-R1/codex/` and `research/CENSUS-FORGET-20261114-001/referee-R1/codex/` (fresh
  per-call relations, exact semigroup decisions, and the census recount; reuse them), CENSUS-FORGET's
  `full/results.jsonl` (data only), the census records `families.jsonl.gz`, and the input modules.
- Write **only** inside `research/TIE-CYCLE-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 60 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/TIE-CYCLE-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check

1. **Theorem I.** Check the proof (rectangular relations form an ideal; every long word in a finite semigroup has an idempotent
   factor, by Ramsey or Simon factorisation), and say whether it is the classical fact that a Rees quotient S/I is nilpotent iff
   every idempotent of S lies in I. Say whether "0 violations on 12,759" is a test or settled by construction of the code.
2. **Ties, fresh.** Define a tie as the study does (an end port always equal or opposite to the same start port along a word) and
   compute, for every census first-ray grower, whether a tie cycle exists, by your own code. Check: no family with a tie cycle
   forgets; ties beyond identity (forced through knots, no port passed unchanged) number 5 in training and 1 held out; the 53
   capped families with a tie cycle (and that this agrees with the earlier referee's finding that all 66 capped are non-forgetting).
3. **Orders and labels.** Classify every non-rectangular idempotent of the families with no tie cycle that do not forget, by your
   own definition of the study's order type (a one-way order between the top's class and the deep copy's class, no value carried),
   tie and parity. Recount 44 of 45 held out (and 52 of 55 in training), the one tie-free parity, and how mixed families are counted.
   Is the classification proved, or verified on the data only?
4. **The chains.** 2,097 of 2,097 held-out chains without a tie cycle forget (FORGET-RULE had 2,096 of 2,096 on its own split).
   Check the chain definition against the corrected counting filter (one SELF occurrence in S and in main, finite helpers and
   wrappers allowed) and the split sizes.
5. **Wording.** "Almost always by identity", "an order ... nothing is carried", and the scope of any growth reading (copies of S
   reached through S calls, per the earlier referees).

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
