# Codex specification: the free-target bond on the every-path growers (FREE-TARGET-20261114-001A)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it. Write the
question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from the repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/` (CODEX below). Modify, move or delete
  no other file. Run no git command that changes anything.
- Use `.venv/bin/python -B`, at most 2 processes at a time and at most about 8 GB in total during your session. Touch no process
  you did not start.
- Use only repository material.
- **Use the shared runner** (`scripts/longrun.py`, read `docs/tooling/shared-runner.md`). Write `job.py` with `cases()`, `run()`
  and `setup()`, run the gates, `launch --prepare-only` and a 20-case smoke with `run --foreground --limit 20`, then stop. Do **not**
  launch the full run; the thread does.

## Inputs (read-only)

- **The population.** The 66 families whose over-paths class is `grows`. They are the rows of
  `experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample/G.jsonl`, each replaced by its row in
  `phase2.jsonl` when present, with `class_path == "grows"`. Their keys, `c`, `lambda_path` and `L_path` are given there. Freeze the
  66 keys in `CODEX/population.json` and report the count; if it is not 66, stop and say so.
- **The inlined family.** `experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/paths_dp.py` and
  the census's `reach_dp.py` (its `Preparation`: usual limit, limit relations G, flat bodies, S, entries, SELF calls). Reuse them.
- **The methods to generalize.**
  - `proofs/BRANCH-DEPTH-20261112-001A/BRANCH-DEPTH-20261112-001A-P001_forgetting/` (the gap argument).
  - `proofs/BRANCH-DEPTH-20261112-001D/BRANCH-DEPTH-20261112-001D-P001_fixed_budget/` (the fixed-size saturation).
  - `experiments/BRANCH-DEPTH-20261112-001C/BRANCH-DEPTH-20261112-001C-E001_port_census/` (its code and `FINDINGS.md`).
  - `experiments/TRUE-RATE-20261113-001A/*/codex/thread_carried_certificate.py`, a carried-port bound with a side member: the
    mechanism (2) must catch.
- `research/FREE-TARGET-20261114-001/preregistration.md` (the object, the settled facts, the gates).

## The object

L_any(s) is the least bond (minimal non-shattered set of the usual limit's allowed states) containing a port of main and an own
distinction of **some** copy at depth s, with members **anywhere** in the infinite pattern.

## Per family

1. **Per-call relations.** For each SELF call i of S (flat body), R_i is the boolean relation on (the copy's 3 port states, the
   child's 3 port states). Take the allowed assignments of S's flat block with NAE on knots and limit relations on every other
   self-holding call (every SELF call except i read as G[S]). Project to the ports and to call i's arguments. Record each R_i.
2. **The forgetting test, exact.** Let P_n be the set of products of n factors from {R_i} (relation composition). Iterate P_1,
   P_2, … until the sequence of sets repeats (it is eventually periodic). The test succeeds with r = the least n such that every
   relation in P_n is rectangular, meaning equal to the product of its two projections. Rectangularity then persists for all
   longer n; check this on the repeating part too. If no P_n in the repeat is all rectangular, record a **recurring non-rectangular
   word**: an eventually periodic sequence of calls, as (prefix, cycle), all of whose prefixes have non-rectangular products. One
   exists because non-rectangularity is closed under prefixes. Record r, or the word.
3. **The bounded certificate.** BRANCH-DEPTH's fixed-size saturation (proof D), generalized:
   - a choice of SELF call at each level, by a subset construction over the call-labelled graph;
   - members anywhere, so side subtrees are summarized by marked port tables with at most k marks;
   - fixed port arity; the target's depth untracked;
   - budgets k = 3, 4, 5.

   It certifies "bounded" only for an eventually periodic path (start the search from the recurring word of step 2 where there is
   one). Along that path a set of at most k members must be a **bond** at **every** depth from an onset: acceptance at each step of
   the cycle, minimality (every one-forgotten subset shattered), and a port of main and an own distinction of the target copy
   included. Record k, the path (prefix, cycle), the onset, and the witness (which members sit on the path, in side copies, and
   whether a top port is carried down the path by identity, A81).
4. **Verdict.**
   - `grows` if step 2 succeeds.
   - `bounded` if step 3 certifies.
   - `unresolved` otherwise, with its reason: cap, memory, or no certificate at k ≤ 5.

   A family certified both ways is a contradiction. Report it and mark the run invalid.

## Gates (in your session)

- **(a) Independent R_i.** Fresh code that shares nothing with steps 1 and 2 re-derives every R_i by direct enumeration of the
  flattened block and rechecks rectangularity of every product in the certifying P_r, on all 66.
- **(b) Witness check.** For every bounded certificate, at each depth from 1 to the onset plus two periods, unfold the pattern
  along the witness path. Read side subtrees below the witness's deepest side member by their limit relations. With a SAT solver,
  check that the witness is non-shattered, every one-forgotten subset is shattered, and the endpoints are present.
- **(c)** No family certified both ways.
- **(d) Mutant.** Drop one SELF call's side relation (read it as all-true) in 10 families and show at least one verdict or R_i
  changes.
- Controls on small synthetic relations for the semigroup and rectangularity code.

## The runner

`job.py`:
- `setup()` loads the census records and the 66 keys;
- `cases()` yields each key;
- `run()` returns the per-family record: c, the R_i in hex, r or the recurring word, the bounded certificate if any, the verdict,
  seconds, and the peak memory.

The thread will launch it with 2 workers, `--case-mem 7G`, `--mem-max 15G`, `--case-timeout 1800`, `--retry timeout,memory` and
`--runtime-max 20h`. Give the steps internal limits that fit 7 GB, so a case ends with a reason, not a kill.

`summarize.py CODEX/<run dir>` writes `summary.json`:
- verdict counts with Wilson 95% intervals over the 66;
- r against λ_path for the growers;
- k, onset, carried or side witnesses for the bounded;
- unresolved by reason;
- the gates.

## Outputs (in CODEX)

Your code, `population.json`, `gates.json` (every gate with every mismatch), the smoke's records, and `REPORT.md`. The report says
what you ran, the exact launch command for the thread, timings, memory, deviations, and "Ambiguities". Do not interpret results.
