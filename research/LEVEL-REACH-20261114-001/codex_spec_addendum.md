# Codex specification addendum (LEVEL-REACH-20261114-001A), 2026-11-14

The first hand-off was stopped by its two-hour runtime limit at 04:47 UTC, after G-brute (300 of 300), G-pattern (200 of 200) and
G-tree passed and before G-mono, G-cert and the smoke finished. No pilot or registered case has run. The rules of `codex_spec.md` hold.

**Continue from your files in CODEX; do not start over.** Finish what remains: G-mono, G-cert, the 20-case smoke through the shared
runner, `gates.json` (all gates, with the final source hashes) and `REPORT.md` (launch commands for the pilot `pop=P` and the
registered run `pop=R`, per-case times, an estimate at 6 workers). Then stop.

Answers to your two ambiguities:
1. **E_R's lists** use the same rule as E_P: r = 1 + gamma, capped at 9, from the list's own seed `f"20261123-{s}-{a}-{j}"`.
2. **Processes.** The ceiling counts runner workers, not the runner's parent and not each worker's one solver or checker subprocess
   at a time. Use 3 workers for the smoke.
