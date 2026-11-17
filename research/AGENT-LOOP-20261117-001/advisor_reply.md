**Verdict: freeze with changes.** The design is honest about its calibration, but the decision rule does not answer the coordinator's question as posed, and three tests can produce a misleading label.

1. **M1 is outside the decision rule.** The coordinator made carry against restart the first comparison; the draft puts it "beside the rule".
   - **Change:** make the verdict two-part, a memory verdict (M1) first and a loop verdict (M2, M3) second, both frozen as primary.

2. **The rule is incomplete and two labels are wrong.**
   - M3 holding without M2 falls into reading 4, "no mechanism gain".
   - M2 in work on local plus M3 in flips on block falls into reading 3, "the agent adds nothing over Novelty+", which is false.
   - There is no outcome for seeds disagreeing.
   - **Change:** report a full grid of M2 × M3 × {flips, work} × family, each cell "holds", "fails" or "seeds disagree". Require M2 and M3 on the same family for "every part pays".

3. **M2 and M3 use different budgets.** M2 is DrC/Dr under EARN-BUDGET's rule, where the agent buys about 5 times the proofs per flip. M3 is under the per-flip budget. Readings 1 and 2 combine them.
   - **Change:** make DrCf/Dr the primary M2 and keep DrC/Dr as context.

4. **M3 confounds the base searcher with use of the reshaped pattern.** On block, Dr alone needs about 7·10^4 flips and Novelty+ alone rarely solves. DrCf/GNf ≤ 0.9 can hold with no interaction at all.
   - **Change:** either relabel M3 as "the agent under the loop beats Novelty+ under the loop", or add the interaction test (DrCf/Dr) ÷ (GNf/F) and reserve "uses the reshaped pattern better" for that.
   - **Change:** state whether Dr was trained on local or block patterns at these windows.

5. **The per-flip budget is fair in flips only.** In work the agent pays about 240 + 150 per flip against 50 + 150, so M3 in work fails by construction. That is why P5 is 3% and reading 1 is effectively unreachable.
   - **Change:** read M3 in flips under the per-flip budget and M3 in work under the proportional rule (DrC/GN), where each arm spends the same share of its work on proofs. Otherwise say plainly that work-M3 is structurally closed.
   - **Change:** state SL's budget, which has no fast work to multiply.

6. **Censoring is unspecified.** Novelty+ on block mostly hits the cap, which was itself chosen from calibration. F, R and possibly GNf are then bounds, not ratios.
   - **Change:** freeze the rule: capped runs enter at the cap, any ratio with more than 10% capped runs in either arm is reported as a bound, and no test "holds" on one.

7. **The room rule has four gaps.**
   - It checks the first cell only, while the family verdict also needs a second cell. Check it per cell and per budget.
   - Calibration room under the per-flip budget on local is 0.51 and 0.64, at the threshold. P7 covers only EARN-BUDGET's rule, so local M1 under the per-flip budget may flip between "read" and "no room" on noise. Add a prediction or raise the threshold.
   - Room is measured on the restart arm's own outcome. Also report the number of rebuilds and the flips between them, since restart wipes memory at every rebuild.
   - The memory verdict says "read in flips", but the test table says flips and work separately. Pick one.

8. **M1 is asymmetric and has forking paths.**
   - "Helps" needs ≤ 0.9 and an interval; "hurts" needs only the interval. Make them symmetric (≥ 1.11).
   - Calibration on block gave 1.09–1.10 under one budget and 0.90–0.91 under the other. Name one primary budget for M1 (per-flip, to match point 3). Pre-state that opposite signs across budgets read as "budget-dependent", not as a memory result.
   - "Carry hurts" may reflect the carry rule putting merged ages and counts out of the agent's training distribution. Say so in the outcome text.
   - P6 at 70% looks high: 50 instances can resolve a 10% effect that four instances already showed. I would put it at 45–50%.

9. **Calibration leaks into the family verdict.** The second cells are the calibration cells, on fresh instances, so half of "holds on a family" is already known. The block family was added after seeing 0.52–0.58 there, which makes reading 2 at 55% largely a preview.
   - **Change:** report the first-cell verdict on its own as the headline and the second cells as replication, and state in the report that block was chosen after seeing the agent ahead.
   - **Change:** commit or hash the first draft so the changes can be audited.
   - A new window of a calibrated family is a weak reading of "a pattern untouched". Say that, or add one untouched family as a context cell.

10. **The statistic is underspecified.**
    - **Change:** define each ratio as the median over instances of the per-instance ratio of geometric means, bootstrapped over instances.
    - **Change:** for P9, use process CPU time including proofs, since six workers on a shared runner make wall time noisy.

11. **The predictions are mostly near-certain.** P1, P7, P8, P11 and P12 restate calibration or gates and will inflate the score.
    - **Change:** mark them as checks and score calibration on P2–P6, P9 and P10.
    - P2 and P4 are not independent of the "reading 2 at 55%" line. P2 ∧ P4 implies about 40–55%, so check they agree.

12. **Minor.** GNco is compared under EARN-BUDGET's rule only, which is fine if stated. Nothing in the draft says whether the seed-agreement rule applies to "no room" and "hurts".

Points 1–6 are blocking; with them fixed, either outcome is interpretable.
