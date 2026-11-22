# Matched search of knot growth

The [contract](contract.json) specifies the proposal weighting, comparison, and resource windows. The immutable calibration record lives under this experiment's artifact directory. Each search repeat resets both arms. The diversity arm keeps one proposal per occupied early bin and supplies a one-token edit of a representative on three out of four proposals while its archive is occupied.

Development calibration admitted 128 starts in 623 attempts from the development partition and added public controls read from their archived traces. The frozen dictionary contains eight parity and ten not-all-equal signatures. Three published source identities occur under the proposal weighting and are excluded from both search and fresh evaluation.

The first development smoke used a 2,048-proposal secondary safety ceiling. It stopped nine of twenty diversity arms and zero of twenty independent arms at that ceiling. Raising it to 16,384 in both arms left the CPU and growth limits as declared. All forty arms in the next smoke reached the CPU boundary. The raw checker passed twenty paired development records with zero literal disagreements. Both smoke records and the calibration attempts remain in the artifact directory.

## Reproduce the run

Run from the repository root. After the coordinating task releases the sealed run, supply the exact independent R1 report path as `research_review`. The shared runner retains one raw result per paired repeat. Its foreground fallback uses the same frozen job configuration and measured process CPU windows.

```bash
growth_exp=experiments/GROWTH-STATISTICS-20261121-001B/GROWTH-STATISTICS-20261121-001B-E001_search
growth_out=artifacts/GROWTH-STATISTICS-20261121-001B/GROWTH-STATISTICS-20261121-001B-E001_search
read -r growth_review_sha _ < <(sha256sum "$research_review")

.venv/bin/python -B scripts/longrun.py launch "$growth_exp/job.py" \
  --out "$growth_out/sealed-search" --unit growth-statistics-search \
  --workers 4 --case-timeout 10 --case-mem 384M --mem-max 4G \
  --param mode=search --param "r1=$research_review" --param "r1_sha256=$growth_review_sha"
.venv/bin/python -B scripts/longrun.py wait --out "$growth_out/sealed-search"

.venv/bin/python -B "$growth_exp/summarize.py" "$growth_out/sealed-search/results.jsonl" \
  "$growth_out/search-summary.json" --phase search --gzip-copy "$growth_out/search-results.jsonl.gz"

.venv/bin/python -B scripts/longrun.py launch "$growth_exp/job.py" \
  --out "$growth_out/sealed-validation" --unit growth-statistics-validation \
  --workers 1 --case-timeout 10 --case-mem 384M --mem-max 4G \
  --param mode=validation --param "r1=$research_review" --param "r1_sha256=$growth_review_sha" \
  --param "search_summary=$growth_out/search-summary.json"
.venv/bin/python -B scripts/longrun.py wait --out "$growth_out/sealed-validation"
```

The parser accepts the original JSONL and its gzip copy with the same raw content digest. Regenerating timed search yields the same proposal streams within corresponding prefixes. The CPU time used by a proposal and the number of completed proposals may vary across executions.
