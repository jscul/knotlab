# TRUE-BOND code and bounded validation

The code is written, but the requested validation gate is **not fully passed**. The full 226-family computation was not run. All task writes are inside this `codex/` directory. BD, the study input, ticket records, and repository state were left read-only; no Git mutation was performed.

## Files and behavior

- `true_bond.py`: exact creator-owned `(F,G)` summaries; local forgetting from paired assignment masks; child composition; the three specified generic pruning rules; least-cost fixed-point iteration with side cap `L_ray(s)-2`; target and root requirements; ray checks. Environment bitsets implement exact existential enumeration. Equal intermediate summaries share the least cost. Closed generic tables and repeated ray layers are cached.
- `run_true.py`: requested CLI, default output `true_rates.jsonl`, append with file locking, and skip every already recorded index. `L` and `L_ray` always have 12 cells; uncomputed cells are `null`. All ray checks run before the slower true minima. Table size is the last **completed** generic fixed point, with per-depth sizes and closure rounds also retained.
- `sat_validation.py`: independent uniform CNF expansion and direct python-sat assumption checks, including all single deletions. Sound CNF-component, clause-support, UNSAT-core, and exact complement-symmetry pruning avoid some enumeration; the bond tests use no projected masks.
- `validate_true.py`: bounded checks and explicit diagnostics for both conflicting height readings. Its separate exact-cost multiplicity tables count labeled chosen sets, rather than assignments.
- `check_runner.py`: focused append, resume, worker-death, timeout, syntax, and cleanup checks. Scratch rows are removed after their results are retained in `validation.json`.
- `validation.json` and `smoke_true.jsonl`: detailed case records and five smoke rows. `true_rates.jsonl` has deliberately not been populated.

## Validation

**Direct SAT:** 33 cases were attempted: ten small study families at `s=1,2,3,h=2`, and candidate 914 at `s=1,2,3,h=3`. Fourteen completed the exact counts through their least size plus one; nineteen reached the five-second or 100,000-candidate bound. Partial sizes appear only in `observed_counts`, never as completed counts. Every requested DP count comparison is explicitly skipped for the height ambiguity. These are not passes.

The ten families were selected by uniform depth-five identity count, then call count, then index. In the table, `complete` means direct SAT reached least+1; `through k` means all sizes at most k were exhausted but the requested range was not. All corresponding requested DP comparisons remain skipped.

| Family | SAT s=1,h=2 | SAT s=2,h=2 | SAT s=3,h=2 |
|---:|---|---|---|
| 914 | complete | through 4 | through 4 |
| 709 | complete | complete | through 4 |
| 212 | complete | complete | through 3 |
| 911 | complete | complete | through 3 |
| 339 | complete | through 3 | through 3 |
| 475 | complete | through 3 | through 3 |
| 618 | complete | through 3 | through 3 |
| 769 | complete | through 3 | through 3 |
| 1148 | complete | through 3 | through 3 |
| 22 | complete | through 3 | through 3 |

Candidate 914 with `h=3`: `s=1` completed through size 4; `s=2` exhausted through size 4 and `s=3` through size 3, with the later size unfinished. Its designation as the requested smallest remains unresolved.

**Height diagnostic:** family 709, `s=1,h=2`, has direct-SAT counts `(size 3: 15, size 4: 305)`. The explicitly requested `uniform_depth` diagnostic reproduces `(15,305)`; `common_side_height` gives `(12,172)`. Neither reading is selected as the specification.

**Shortening:** family 911 at `s=2` has exact DP `L=3 < L_ray=4`. Direct SAT at `h=2` exhaustively finds **1 size-three bond and 14 size-four bonds**. Both explicit height diagnostics agree on this particular case. A size-three witness is top port 2, own distinction 1 of copy path `(0,0)`, and own distinction 1 of path `(0,0,2)`; SELF occurrences and own indices are zero-based. The latter is a side child of `C_2`. Direct SAT verifies constrainedness and every deletion. The DP also finds `L(3)=4 < L_ray(3)=5` for family 911, but its SAT enumeration did not finish; that second value is not promoted as an independently validated count result.

**Mutant:** literal `G_S := F_S`, including the empty choice, gives zero bonds in the 709 diagnostic. Direct SAT gives 15 size-three bonds. The explicit witness `{top0, top2, first own distinction of C_1}` is constrained and all three deletions are free. The mutant disagrees as required.

**Ray check:** **168/168 pass**, covering all `s=1..12` for 14 families: `22, 46, 212, 231, 296, 339, 475, 618, 709, 769, 911, 914, 1148, 1304`. Values agree with BD `run_family`; only its explicitly detected affine repeat may fill missing reference depths. This is not a claim that all 226 families were checked here; the runner checks each additional family when launched.

**Implementation checks:** all five independent SAT fixtures and all seven focused runner checks pass. The latter include a deliberately killed worker, a deliberately stuck worker, two-worker execution, and byte-for-byte resume preservation. No owned child was left running.

## Smoke performance and resource estimate

The runner was invoked with `--smax 12 --workers 1 --seconds-limit 60`; the default worker address-space ceiling was 1024 MiB. Four random indices were drawn with `random.Random(20261113)` from the study set excluding candidate 914: `296,46,1304,231`. Candidate 914 is the conditional smallest under the validation-cost ranking. All five finished their ray checks through 12 and hit the time limit during true-minimum work. The explicit `timeout` rows preserve reached values and nulls.

| Family | Seconds | Peak RSS MiB | True depths reached | Completed generic table size |
|---:|---:|---:|---:|---:|
| 914 | 60.001 | 263.387 | 10 | 5935 |
| 296 | 60.001 | 326.047 | 6 | 3495 |
| 46 | 60.002 | 207.605 | 5 | 413 |
| 1304 | 60.001 | 345.125 | 5 | 313 |
| 231 | 60.002 | 392.375 | 3 | 1803 |

Observed peak RSS is 207.6–392.4 MiB per worker (mean 306.9 MiB) within these 60-second probes. Larger fixed points may require more. The runner defaults to a 1024 MiB **address-space** limit per worker, which is distinct from measured RSS, and records `memory_limit` if allocation fails.

All completion times are censored, so there is **no defensible finite estimate for completing all depths of all 226 families**. A plug-in extrapolation of the censored 60-second sample gives at least about **3.77 worker-hours** (about 1.26 hours with three perfectly balanced workers); this is an extrapolated lower estimate, not a rigorous population bound or completion forecast. With the runner's default 1100-second ceiling, 226 attempts budget about **69.1 worker-hours**, or about **23.0 hours at three workers**, plus launch and cleanup overhead, and may still return incomplete rows. Three workers plus the coordinator respect the four-process ceiling; three default workers budget up to 3 GiB address space plus the coordinator. These estimates describe attempts, not successful completion.

## Reproduction and deviations

Use the repository root and `.venv/bin/python -B`:

```sh
.venv/bin/python -B experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex/run_true.py --workers 1 --only 914 296 46 1304 231 --smax 12 --seconds-limit 60 --output smoke_true.jsonl
.venv/bin/python -B experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex/validate_true.py --case-seconds 5 --candidate-limit 100000
.venv/bin/python -B experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex/check_runner.py
```

The smoke command skips its existing five rows on replay. For a new bounded rehearsal, use a fresh `--output` basename inside CODEX. Resume deliberately skips **every** existing index, including timeout/error rows and smaller-smax runs, as requested. Use a fresh output to retry those cases. Invalid JSONL and a missing final newline are rejected without appending. The runner accepts `--workers 1..3`; the coordinator counts toward the process ceiling.

An initial rehearsal exposed a checkpoint/SIGALRM race before producing any row. Child alarms were removed. The parent now supervises and reaps its own workers, detects worker death, drains a result that arrives during exit, and guards child registration against interruption. These resource fixes passed the focused checks. The production DP core used for the five smoke measurements is unchanged by the later literal-mutant and supervisor fixes.

The requested full count-comparison gate is left incomplete, rather than changing the finite object or silently expanding the production cap. Independent SAT resource cutoffs and the conditional smallest selection are additional limits. No ticket lifecycle, contract, prediction, repository navigation, or publication record was changed. All commands were foreground, individually bounded below 20 minutes, and all task-owned processes have finished.

## Ambiguities

1. **Height:** Should finite validation use all copies through uniform depth `D=s+h`, or a common `h`-level generic table at every ray copy? Uniform depth needs side table `T_(D-j)` at `C_j`. The 709 diagnostic proves the distinction changes counts. The required comparison is skipped pending this answer.
2. **Counting cap:** May the validation-only multiplicity table use side cap `(least+1)-2` to count through least+1 when that exceeds `L_ray-2`? Production retains the exact specified cap. Diagnostic count budgets are explicit and are not silently substituted for the production table.
3. **Smallest:** Which size ordering defines the smallest family: description length, own count, SELF count, or truncation identity count? Family 914 was measured as a conditional candidate under the stated validation-cost ranking; its requested designation is skipped.

These records validate bounded code behavior and retain incomplete evidence; they do not discharge a theorem or establish the registered predictions for the 226-family study.
