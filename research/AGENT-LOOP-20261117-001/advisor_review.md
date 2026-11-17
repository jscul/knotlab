# Advisor review of the draft design

Epic `AGENT-LOOP-20261117-001`, 2026-11-17.
- **How it was asked.** The advisor model (`claude -p --model claude-fable-5-2 --tools "" --output-format json`; the reply's
  `modelUsage` names `claude-fable-5-2`) was given the earlier studies' results, the coordinator's request and the second draft
  cold ([advisor_prompt_draft2.txt](advisor_prompt_draft2.txt)).
- **Its verdict** was "freeze with changes"; it called points 1 to 6 blocking. Its reply is kept verbatim
  ([advisor_reply.md](advisor_reply.md)).
- **Below:** its points, checked here, and what changed.

| Point | Taken? | Change |
| --- | --- | --- |
| 1. M1 was outside the decision rule, though the coordinator made carry against restart the first comparison | yes | two frozen verdicts, memory (M1) first and loop (M2, M3) second |
| 2. The rule was incomplete and two labels were wrong: M3 without M2 fell into "no mechanism gain", and M2 on one family with M3 on another read "the agent adds nothing"; seeds disagreeing had no outcome | yes | loop readings 1 to 6 per family, from the measures in which M2 and M3 hold on the same family; every test on a cell reads "holds", "seeds disagree", "fails", "no room" or "bound" |
| 3. M2 and M3 used different budgets, and readings 1 and 2 combined them | yes, in a stronger form | every test uses one budget per measure: in flips the per-flip budget (M2 = DrCf/Dr), in work EARN-BUDGET's rule (M2 = DrC/Dr); the other budget's ratios are context |
| 4. M3 confounds the base searcher with use of the reshaped pattern | yes | M3 relabelled "the agent under the loop beats Novelty+ under the loop"; M4, the interaction (DrCf/Dr) ÷ (GNf/NOV), added and reserved for "uses the reshaped pattern better"; stated that Dr trained on `rand` 2.1 only |
| 5. The per-flip budget is fair in flips only; M3 in work fails by construction under it; SL's budget unstated | yes | M3 in work is DrC/GN under EARN-BUDGET's rule; SL's round budget stated (3 × 50 × n′) |
| 6. Censoring unspecified | yes | capped runs enter at the cap; a ratio with more than 10% capped runs in either arm is a bound, and no test holds on it |
| 7. Room was checked on the first cell only, sat at the threshold on local under the per-flip budget, ignored rebuild counts, and the measure was unclear | yes | room checked per cell and per budget for both seeds; P6 added for local per-flip room; rebuilds and flips after the first rebuild per rebuild reported; M1 read in both measures, each under its budget |
| 8. M1 was asymmetric and had forking paths; "carry hurts" may be the carry rule's out-of-training memory; P6 too high | yes | "hurts" at ≥ 1.11 with the lower end above 1; one budget per measure; "budget-dependent" mark when the other budget passes the opposite way; the possible cause stated in the outcome text; the memory prediction lowered from 70% to 50% |
| 9. Calibration leaks into the family verdict; the block family was added after seeing the agent ahead; a new window of a calibrated family is a weak "untouched" | yes | the first cell's verdict is the headline and the second cells are replication; the choice of block after the calibration and the weak reading are stated; both drafts kept with their hashes. An untouched family was not added: none exists in the generator without new code |
| 10. The statistic was underspecified; P9 should use process CPU | partly | the statistic stated exactly. It is kept as the ratio of cell medians, the line's convention since SLOW-LOOP, so that results compare across the four studies, rather than the median of per-instance ratios suggested. CPU is the run's thread CPU time around the whole run, probes and rebuilds included |
| 11. Most predictions were near-certain and would inflate the score; P2 and P4 against the reading line | yes | C1 to C5 marked as checks and not scored; the block line's reading 2 set to about 50%, consistent with P1 and P3 |
| 12. GNco only under EARN-BUDGET's rule; seed agreement for "no room" and "hurts" | yes | both stated |

Not used after the results.
