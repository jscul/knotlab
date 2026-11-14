"""Render the stage-1 handoff from preserved gate and shared-runner records."""
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gates import latest_records, mono_records


def duration(seconds):
    return f'{seconds / 3600:.2f} h' if seconds >= 3600 else f'{seconds / 60:.2f} min'


def locked_seconds(result):
    """Count each executed proof receipt once, including reused certificates."""
    seen = set()
    total = result['union'].get('seconds', 0)
    for row in result['levels']:
        for bond in [row.get('anywhere', {}), row.get('target_restricted', {})] + row.get('per_target', []):
            ref = bond.get('certificate', {}).get('refutation')
            if ref is None:
                continue
            identity = (ref['cnf_sha256'], ref['proof_sha256'], ref['seconds'])
            if identity not in seen:
                seen.add(identity)
                total += ref['seconds']
    return total


def build():
    gates = json.loads((HERE / 'gates.json').read_text())
    records = latest_records(HERE / 'smoke' / 'results.jsonl')
    mono = mono_records()
    populations = {p: json.loads((HERE / 'prepared' / f'population_{p}.json').read_text()) for p in ('P', 'R')}
    ok = [r for r in records if r['status'] == 'ok']
    assert gates['all_passed'] and len(ok) == len(records) == 20
    order = {item['id']: i for i, item in enumerate(populations['P']['keys'])}
    records.sort(key=lambda r: order[r['case']])
    times = [r['seconds'] for r in ok]
    mean = statistics.mean(times)
    locked_mean = statistics.mean(locked_seconds(r['result']) for r in ok)
    mono_times = [r['result']['N9']['seconds'] for r in mono if r['status'] == 'ok']
    state = json.loads((HERE / 'smoke' / 'state.json').read_text())
    lines = [
        '# LEVEL-REACH-20261114-001A — stage 1', '',
        'All five gates passed; the required shared-runner smoke finished 20/20 cases with three workers. '
        'This continuation resumed G-mono from 31/50 completed cases and preserved its earlier evidence. '
        'The finite controls were repeated after a memory-lifecycle correction. '
        'No full pilot or registered run was started. Stage 1 stops here.', '',
        '## Implementation and continuation', '',
        '`job.py` supplies setup/cases/run. `population.py` builds both deterministic populations and retains '
        'attempts, rejections, placement ranks and memberships; cases deduplicate normalized keys. '
        '`pattern.py` builds the stated unions; `reference.py` is the independent scalar implementation.', '',
        '`search.py` searches forbidden partial assignments in increasing support size and tests every assignment '
        'of every maximal proper subset. Exact cardinality SAT and correction sets supply the general fallback. '
        '`compiled_search.py` optionally compiles a low-width formula by binary variable elimination; width and gate '
        'caps fall back to the general search. An incidence-forest optimization supplies the tree control. '
        'A `> 10` result requires exhausted exact SAT search, rather than failure to find a candidate. '
        'All support exclusions are local to their query; original-formula SAT checks candidate assignments.', '',
        '`L_target` restricts support membership while retaining the full N-level formula. '
        '`L_N`, `L_target` and all per-target queries share one 300-second deadline per (key,s). '
        'Timed-out searches report `undecided`; L is undefined for dead/undecided unions. '
        'Histograms include every target, with nonnumeric outcomes retained.', '',
        '`certificates.py` uses the permitted LEVEL-RETURN certifier and CaDiCaL 2.1.2. '
        'Every reported bond has a checked unanchored LRAT refutation and checked states for all assignments '
        'of all maximal proper subsets. Proof files are checked on disk and deleted; hashes, sizes and checker '
        'responses remain, together with packed state witnesses. Replay binds each assignment and support '
        'to the exact checked CNF hash. The locally compiled `lrat_check` uses the copied permitted C source. '
        'Every case removes its own work directory at entry and exit.', '',
        'Exact search rules, certificate rules and budgets were preserved during this continuation. '
        'The addendum-authorized E_R list construction was added in `population.py`; rebuilding P matched its predecessor '
        'manifest exactly. All 2,320 E_R lists were independently replayed from their own seeds, including '
        'gamma values and combination ranks. Reporting and aggregate checks were updated for final coverage '
        'and source accounting.', '',
        'A confirmed lifecycle defect in `SearchEngine.close()` retained completed engines through timer and '
        'compiler callbacks until cyclic garbage collection. The correction cancels/joins the timer, clears '
        'its reference and detaches the compiler before deleting the solver. Tiny weak-reference checks '
        'verified immediate reclamation with compilation enabled and disabled. This fixes a demonstrated '
        'retention problem; it does not establish that retention explained every byte of the observed peaks. '
        'The exact pre-cleanup source and original finite-gate files remain in '
        '`validation_history/before_close_cleanup/`. G-brute (including the general fallback), G-pattern '
        'and G-tree were repeated after that correction.', '',
        'A subsequent 3G failure showed that lifecycle cleanup alone was insufficient. Optional witness '
        'memoization is now bounded: at most 512 append-only checked models, 20,000 SAT-cache entries and '
        '1,024 projection-cache entries. SAT/projection caches use LRU eviction; misses recompute exact '
        'answers, and returned witness lists are not mutated. Every actual satisfying state still reaches '
        'query-local IHS correction generation after the global model pool fills. All query-local correction '
        'and exclusion conditions remain intact. Forced-small-cap controls checked 80 SAT answers and 15 '
        'projections against independent enumeration and verified retained-witness immutability. '
        'These bounds can change timing, witnesses and which queries are undecided within 300 seconds; '
        'they do not change the mathematical search rules. They do not bound native solver or query-local '
        'IHS memory. `memo_bounds_provenance.json` records the limits and controls; the pre-bound source '
        'and finite controls remain in `validation_history/before_memo_bounds/`. All three finite gates '
        'were repeated again on the bounded source in `bounded_controls/`.', '',
        'The generic IHS also now encodes a selected-support exclusion with one presence clause instead '
        'of its exponential expansion over signs. Three clauses per domain variable make presence exactly '
        'equivalent to either signed selector being selected. Cardinality still counts signed selectors '
        'only; its auxiliary IDs start after all presence IDs. Both initial and learned exclusions use '
        'the equivalent encoding. 1,620 independent assignment/cardinality checks passed. These are '
        'candidate-query auxiliaries, with no change to the input pattern or original-state certificates. '
        '`presence_encoding_provenance.json` records the checks, and the preceding source is archived '
        'under `validation_history/before_presence_encoding/`. `final_encoding_controls/` repeats all '
        'three finite gates on the composed final source; the last affected retry and required smoke '
        'also use that source.', '',
        '`continuation_provenance.json` records predecessor code and completed-gate digests. '
        '`execution_source_hashes.json` binds the runtime modules before resumed execution; '
        'the retry source receipts bind those modules and their filtering wrappers. '
        '`final_execution_source_hashes.json` binds the final bounded-memoization source. The intermediate '
        'cleanup retries and final bounded retry each have their own source receipt. '
        '`gates.json` verifies those digests and records final Python/C/binary hashes, input hashes, '
        'runner manifests, population manifests and result-file digests. Shared-runner `job_sha` binds '
        'the entry module; the separate execution receipt binds its imported runtime modules. '
        'The 31 predecessor mono records retain their original entry-module hash; P and all scientific '
        'search rules are unchanged. Earlier successful G-mono results retain their archived source identity; '
        'the resource corrections do not alter those completed mathematical results. Failed attempts remain '
        'visible but are superseded only by a successful retry of the same key.', '',
        '## Populations', '',
        '| Population | Accepted weighted draws / attempts | Panel lists | Distinct keys |',
        '|---|---:|---:|---:|',
    ]
    for pop in populations.values():
        summary = pop['summary']
        lines.append(f"| {pop['population']} | {summary['weighted_accepted']} / {summary['weighted_attempts']} | "
                     f"{summary['panel_lists_accepted']} / {summary['panel_lists']} | {summary['distinct_keys']} |")
    lines += ['', 'Both complete deterministic manifests are in `prepared/population_{P,R}.json`. '
              'Preparing R builds descriptions only and runs no registered scientific case.', '',
              '## Gates', '', '| Gate | Result | Evidence |', '|---|---|---|']
    descriptions = {
        'G-brute': '300 tiny descriptions; all 32,768 states and all 16,384 supports through size 7 per case; '
                   '294 alive cases, 588 size comparisons, 6 dead fates',
        'G-pattern': '200 random keys, each at N=9 and N=10 plus cycling boundary depths; 564 scalar comparisons',
        'G-tree': 's=1..4: L_N = L_target = 3,4,5,6; all certificates checked',
        'G-mono': f"{gates['gates']['G-mono']['case_count']}/50 pilot keys alive at N=10; "
                  f"{gates['gates']['G-mono']['numeric_comparisons']} numeric comparisons, no L_10 > L_9",
        'G-cert': f"{gates['gates']['G-cert']['smoke_ok']}/20 smoke cases; "
                  f"{gates['gates']['G-cert']['bonds_replayed']} reported bond occurrences and "
                  f"{gates['gates']['G-cert']['proper_projection_states_replayed']} proper-projection state witnesses replayed; "
                  'both corruption controls rejected',
    }
    for name in ('G-brute', 'G-pattern', 'G-tree', 'G-mono', 'G-cert'):
        lines.append(f"| {name} | {'PASS' if gates['gates'][name]['passed'] else 'FAIL'} | {descriptions[name]} |")
    lines += ['', 'G-mono uses the first 50 distinct pilot keys whose N=10 unions are alive, '
              'as recorded in `mono_selection.json`; only pairs with two numeric sizes enter the inequality check. '
              'Nonnumeric outcomes and every comparison remain in `gates.json` and the raw runner records. '
              'The G-cert controls in the final-source tree gate flip one pinned state value and replace '
              'one effective LRAT hint with a nonexistent clause ID. These checks reject those mutations; '
              'they do not claim that every corruption is detected. The gates validate bounded computations, '
              'not a general monotonicity theorem or a complexity claim.', '',
              'Memory-limited original G-mono attempts remain in `mono_gate/results.jsonl` and '
              '`gates.json`; the table below records each one. Retry wrappers delegate to unchanged '
              '`mono_job.run`, preserving the 300-second search budgets and 2,700-second case timeout. '
              '`mono_retry` reruns the first failed case with a 3G cap alongside the original two workers '
              '(2G+2G+3G allowances). After the original runner exits, `mono_remaining_retry` reruns '
              'the second memory failure with one 4G worker; `mono_additional_retry` handles the third '
              'case. Intermediate 4G/3G attempts and the later cleanup-source 3G failure are preserved '
              'in their raw result files and the tables below. The final 700620 case uses the cleanup '
              'source with a 4G cap. The final 0758 case runs once in `mono_bounded_retry/` on the bounded '
              'source, with a 3500M cap, only after the previous runner has exited. Aggregation accepts '
              'only those named substitutions and keeps all preceding failures. Simultaneous worker '
              'allowances are at most 7G before the final phase, then 4G+3500M (7,596 MiB) plus small '
              'runner parents, within approximately 8G. Finite rechecks used one 512M worker only when '
              'that also fit the envelope. The smoke starts after all gate runners finish.', '',
              '| Original memory-limited case | Seconds | Peak MiB |', '|---|---:|---:|']
    for failed in gates['gates']['G-mono']['retained_original_attempt_failures']:
        lines.append(f"| `{failed['case']}` | {failed['seconds']:.3f} | {failed['peak_rss_mb']:.3f} |")
    lines += ['', '| Intermediate retry failure | Seconds | Peak MiB |', '|---|---:|---:|']
    for failed in gates['gates']['G-mono']['retained_retry_attempt_failures']:
        lines.append(f"| `{failed['case']}` | {failed['seconds']:.3f} | {failed['peak_rss_mb']:.3f} |")
    lines += ['',
              '## Smoke timings', '',
              'The first 20 distinct P keys ran through `scripts/longrun.py run --foreground --limit 20` '
              'with three workers, a 1,800-second case timeout, 2G per case and an 8G aggregate setting. '
              'No case was retried or replaced.', '',
              '| P key index | Case | Status | Seconds | Peak MiB |',
              '|---:|---|---|---:|---:|']
    for r in records:
        lines.append(f"| {order[r['case']]} | `{r['case']}` | {r['status']} | {r['seconds']:.3f} | {r['peak_rss_mb']:.1f} |")
    lines += ['', f"Mean {mean:.3f} s; median {statistics.median(times):.3f} s; "
              f"range {min(times):.3f}–{max(times):.3f} s; sum {sum(times):.3f} s. "
              f"Runner peak memory: {state['peak_rss_mb']:.1f} MiB. "
              'Per-case wall times include certification, lock waiting and runner accounting. '
              'Full records are retained in `smoke/results.jsonl`.', '',
              '## Six-worker estimates', '',
              f"Using the smoke mean, ideal work-sharing time is mean × distinct keys / 6: "
              f"**{duration(mean * len(populations['P']['keys']) / 6)} for P** and "
              f"**{duration(mean * len(populations['R']['keys']) / 6)} for R**. "
              'These are conditional extrapolations, not measured six-worker runs.', '',
              f"The within-budget launch commands below use one worker. At that worker count, the same "
              f"arithmetic gives {duration(mean * len(populations['P']['keys']))} for P and "
              f"{duration(mean * len(populations['R']['keys']))} for R, before allowing for population differences.", '',
              f"The implementation conservatively serializes external solver/checker work with one file lock. "
              f"Measured locked work averages approximately {locked_mean:.3f} s per smoke case."]
    lines += [f"That gives conditional serial-work estimates of {duration(locked_mean * len(populations['P']['keys']))} for P "
              f"and {duration(locked_mean * len(populations['R']['keys']))} for R. "
              'This counts each executed refutation receipt once even when its certificate is reused. '
              'The larger of ideal work-sharing time and serial-work time is a more cautious planning estimate.', '',
              f"For comparison, the 50 alive G-mono keys have mean N=9 compute time "
              f"{statistics.mean(mono_times):.3f} s; transferring that mean gives "
              f"{duration(statistics.mean(mono_times) * len(populations['P']['keys']) / 6)} for P and "
              f"{duration(statistics.mean(mono_times) * len(populations['R']['keys']) / 6)} for R. "
              'This second estimate is also conditional and excludes runner dispatch. '
              'Both samples come from early W_P keys; neither measures E_P/E_R costs or registered-population '
              'tail behavior. Budget exhaustion, shared-machine load and certificate contention can change '
              'the realized wall time. Use the pilot to revise the registered estimate.', '',
              '## Exact launch commands for the thread', '',
              'Run from `/home/jscul/p-vs-np-contact-first`. The following commands are recorded for the thread; '
              'they were not executed here. Observed pre-cleanup gate memory failures make the smoke\'s 2G cap unsuitable '
              'as a general provisioning guarantee. These launch commands reserve 4G per case with one worker '
              'and a 6G total allocation, within the stated worker and approximately-8G limits. The six-worker '
              'timing figures above are conditional throughput extrapolations: six 4G cases plus the parent '
              'would need 25G, exceeding this runner\'s 16G maximum.', '',
              '```sh',
              'CODEX=experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex',
              '# Full exploratory pilot (P):',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/job.py" --out "$CODEX/pilot" \\',
              '  --unit lr-reach-pilot --workers 1 --case-timeout 1800 --case-mem 4G --mem-max 6G \\',
              '  --param pop=P',
              '# Full registered population (R), after the pilot and any frozen size-cut decision:',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/job.py" --out "$CODEX/registered" \\',
              '  --unit lr-reach-registered --workers 1 --case-timeout 1800 --case-mem 4G --mem-max 6G \\',
              '  --param pop=R',
              '```', '',
              'The R command builds all 4,399 currently specified distinct keys. No post-pilot size cut is '
              'implemented or silently assumed. Registration, the full pilot and the registered launch remain '
              'with the thread.', '',
              'The stage-1 smoke configuration was already prepared in the first handoff; this continuation '
              'used its existing `smoke/job.json` and ran:', '', '```sh',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/mono_gate" --foreground',
              '# One-case memory retry (separate terminal while the original gate continues):',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/mono_retry_job.py" --out "$CODEX/mono_retry" \\',
              '  --unit lr-reach-mono-retry --workers 1 --case-timeout 2700 --case-mem 3G --mem-max 4G \\',
              '  --param pop=P --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/mono_retry" --foreground',
              '# After the original runner exits; ids are the remaining named memory failures:',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/mono_remaining_retry_job.py" --out "$CODEX/mono_remaining_retry" \\',
              '  --unit lr-reach-mono-remaining-retry --workers 1 --case-timeout 2700 --case-mem 4G --mem-max 6G \\',
              '  --param pop=P --param ids=' + ','.join(r['case'] for r in mono if r['run_directory'] == 'mono_remaining_retry') + ' --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/mono_remaining_retry" --foreground',
              '# The older additional 3G attempt also failed; after preserving it, its config became 4G/retry memory.',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/mono_additional_retry" --foreground',
              '# After mono_retry exits; the remaining 4G worker may still be active:',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/mono_remaining_retry_job.py" --out "$CODEX/mono_additional_retry" \\',
              '  --unit lr-reach-mono-additional-retry --workers 1 --case-timeout 2700 --case-mem 3G --mem-max 4G \\',
              '  --param pop=P --param ids=' + ','.join(r['case'] for r in mono if r['run_directory'] == 'mono_additional_retry') + ' --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/mono_additional_retry" --foreground',
              '# After the 4G failure, the same output\'s config was preserved, then set to 3G with retry=["memory"].',
              '# The corrected-source retry used the same case and case timeout:',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/mono_remaining_retry" --foreground',
              '# Final-source finite controls:',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/controls_job.py" --out "$CODEX/final_controls" \\',
              '  --unit lr-reach-final-controls --workers 1 --case-timeout 300 --case-mem 512M --mem-max 2G --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/final_controls" --foreground',
              '# Final bounded-memoization controls:',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/controls_job.py" --out "$CODEX/bounded_controls" \\',
              '  --unit lr-reach-bounded-controls --workers 1 --case-timeout 300 --case-mem 512M --mem-max 2G --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/bounded_controls" --foreground',
              '# Final equivalent support-encoding controls:',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/controls_job.py" --out "$CODEX/final_encoding_controls" \\',
              '  --unit lr-reach-final-encoding-controls --workers 1 --case-timeout 300 --case-mem 512M --mem-max 2G --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/final_encoding_controls" --foreground',
              '# Once the older 0758 runner is final, the single fresh bounded-source retry:',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/mono_bounded_retry_job.py" --out "$CODEX/mono_bounded_retry" \\',
              '  --unit lr-reach-mono-bounded-retry --workers 1 --case-timeout 2700 --case-mem 3500M --mem-max 5G \\',
              '  --param pop=P --param ids=0758783d31dde76fe9f2f1e3f17d2f8c077710f5fdd6a8d478363a186001d00b --prepare-only',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/mono_bounded_retry" --foreground',
              '# After all gate runners finish:',
              '.venv/bin/python -B scripts/longrun.py run --out "$CODEX/smoke" --foreground --limit 20',
              '.venv/bin/python -B "$CODEX/gates.py" aggregate',
              '.venv/bin/python -B "$CODEX/finalize_report.py"',
              '```', '',
              'For a new smoke output directory, its preparation command is:', '', '```sh',
              '.venv/bin/python -B scripts/longrun.py launch "$CODEX/job.py" --out "$CODEX/smoke" \\',
              '  --unit lr-reach-smoke --workers 3 --case-timeout 1800 --case-mem 2G --mem-max 8G \\',
              '  --param pop=P --prepare-only',
              '```', '',
              '## Ambiguities', '',
              'Both first-handoff ambiguities were resolved by the 2026-11-14 addendum:', '',
              '1. E_R uses `r = min(1 + gamma(list_rng)[0], 9)` with each list\'s own '
              '`random.Random(f"20261123-{s}-{a}-{j}")`; placements follow on that same RNG stream.',
              '2. The process ceiling counts runner workers, excluding the runner parent and each worker\'s '
              'one solver/checker subprocess at a time. The smoke used three workers. '
              'G-mono used two original workers, then bounded memory retries, and did not overlap the smoke.', '',
              'No unresolved ambiguity remains. The explicit term-triple sampler in `codex_spec.md` '
              'continues to govern weighting.', '']
    (HERE / 'REPORT.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    build()
