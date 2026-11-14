# Independent recomputation and critique: CENSUS-FORGET-20261114-001

You are an independent referee's assistant. The study reuses FREE-TARGET's forgetting test (agent-written) through a thin wrapper,
so your checks must use **fresh code**. You may reuse the earlier referee's own fresh code in
`research/FREE-TARGET-20261114-001/referee-R1/codex/` (for example `relations_audit.py`, `direct_bonds.py`), which is independent of
the study.

## Rules for this task

- **Do not open or import any `.py` under** `experiments/FREE-TARGET-20261114-001A/` or `experiments/CENSUS-FORGET-20261114-001A/`.
  You may read their JSON/JSONL data (`full/`, `reading.json`, `job.json`), `research/CENSUS-FORGET-20261114-001/{census_forget.md,
  preregistration.md, advisor_review_answer.md}`, FREE-TARGET's referee report and code named above, the census records
  `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz` and
  `experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz`, EVERY-RAY's sample rows
  (data only), and the input modules (dlang, LIMIT-STATE's census).
- Write **only** inside `research/CENSUS-FORGET-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 60 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/CENSUS-FORGET-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Background from FREE-TARGET's referee (read its report)

The gap argument is sound for targets that are copies of the ray definition S; 2 + ⌊s/r⌋ holds when main = S and 2 + ⌊(s−1)/r⌋ for
wrappers; it does not automatically cover targets in copies of **another recursive definition with its own distinctions**; and
"L_any = L_ray by construction" for chains is false (members below the target), replaced by inf_{d≥s} L_ray(d) ≤ L_any(s) ≤ L_ray(s).

## Points to check (in order of value)

1. **The 657 single-call families with other self-holding calls (538 certified).** For each, determine after inlining whether any
   other self-holding definition reachable from S or main has own distinctions (so that its copies are deep targets). Count them.
   For several such certified families, compute exactly, by direct satisfiability with no relation code, the least bond from a top
   port to an own distinction of **any** copy at depth s (including copies of those other definitions, if the object's wording
   includes them) for small s, and say whether it stays bounded or respects the certified lower bound. State plainly which
   families the certificate covers.
2. **Fresh verdicts on a sample.** For about 120 families stratified by stratum (c ≥ 2, the 657, chains) and verdict (certified,
   certified non-forgetting, capped), recompute R_i and the semigroup decision yourself and compare with `full/` results.
3. **The chains.** The stated chain criterion ("one definition, one SELF call, no other self-holding call") against the counted
   5,190 families and 5,633 draws; the literal one-definition count; whether the claim uses L_any = L_ray; how many counted chains
   have depths with no ray bond.
4. **The headline shares.** Recompute 7,251 of 13,279 draws (54.6%), 1,618 of 7,646, 1,080 of 6,989, 538 of 657, 3.25% of 223,261,
   and the Wilson intervals, from the records; check that "undecided, almost all certified non-forgetting" is not worded as bounded,
   and that the 224 limit-only growers (none certified) are reported correctly.

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
