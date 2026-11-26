# Referee review record

| Responsibility | Evidence | Reconciliation |
| --- | --- | --- |
| Held-out counts | held_counts.json | Checked against the frozen thresholds and the common-round comparison. |
| Independent growth | growth_replay.json and growth_law_spread.json | Round records and stop conditions compared with the archived runs. |
| Two birth traces and the unlinked argument | trace_births.json and trace_controls.json | Compared both first-round multisets and the distinguishing births. |
| Later profiles and matched swaps | posthoc_recount.py and later_regrow_check.py | Final counts and qualifications are in report.md. |
| Replication and controls | replication_counts.json | Read with the fresh 400-run replay in gate_replay_counts.json. |
