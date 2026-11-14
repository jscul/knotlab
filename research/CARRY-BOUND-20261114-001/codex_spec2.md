# Codex follow-up: resolve the eight questions (CARRY-BOUND-20261114-001A)

You are computing, not designing. Same rules as `research/CARRY-BOUND-20261114-001/codex_spec.md` (write only in CODEX =
`experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/`, no git, `.venv/bin/python -B`, at most 2
processes and about 8 GB, the shared runner, no full run, no P1–P5 on the population). Read the pre-registration's last section,
"Addendum: Codex's implementation questions, resolved before the full run", which answers your REPORT.md's A1 to A8. Implement
exactly those answers:

1. A1: Q_0 = one start state per S-call of a wrapper main; U(s) the minimum over all; G2's contexts from every start.
2. A2: dead = not live, live = the least fixed point seeded by knot occurrences (and arguments at live positions of a call). The
   synthetic dead-carriage control must now pass (G certifies; no window bound through the dead coordinate).
3. A3: the brute-force gate for wrappers too, with the stated depth and leaf convention; fill the skipped places of the first 50.
4. A4: the P3 scalar with "every unbounded residue"; enable it in `summarize.py`.
5. A5: syntactic sample cells for every I family, as stated.
6. A6: exclusive attribution by priority B, widened B, tie, other, per residue; the family takes the lowest-priority reading needed.
7. A7: in gate c, search G2 up to the family's census r.
8. A8: re-prepare `window_full`, `paths_full` and `direct_full` with `--retry timeout,memory,crashed` (3 workers, 600 s, 3G per
   case, MemoryMax 12G, `--prepare-only`), so that the frozen job hashes match the final code.

Then rerun the gates (all of a to e and the four synthetic controls) and a fresh 20-case smoke in a new directory, update the source
manifest, and rewrite REPORT.md's gate table and commands. If any gate still fails, say exactly why and stop. Add any new question
under "Ambiguities" rather than resolving it.
