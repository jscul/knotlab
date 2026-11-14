"""Summarize only this lane's fresh depth results, never study summary code."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
path = HERE / 'depth_results.jsonl'
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
by_stratum = defaultdict(list)
by_case = defaultdict(list)
seen = set()
duplicates = []
numeric_lower = []
numeric_higher = []
for row in rows:
    key = (row['case'], row['N'], row['s'])
    if key in seen:
        duplicates.append(key)
    seen.add(key)
    by_stratum[row['stratum']].append(row)
    by_case[row['case']].append(row)
    fresh = row['result']['L']
    old = row['study_N9']
    if isinstance(fresh, int) and isinstance(old, int):
        if fresh < old:
            numeric_lower.append({'case': row['case'], 'N': row['N'], 's': row['s'], 'old': old, 'fresh': fresh})
        if fresh > old:
            numeric_higher.append({'case': row['case'], 'N': row['N'], 's': row['s'], 'old': old, 'fresh': fresh})


def profile(group):
    numeric = [r for r in group if isinstance(r['result']['L'], int)]
    return {'queries': len(group), 'exact': sum(bool(r['result']['exact']) for r in group),
            'numeric': len(numeric), 'numeric_equal_N9': sum(r['result']['L'] == r['study_N9'] for r in numeric),
            'outcomes': dict(Counter(str(r['result']['L']) for r in group)),
            'undecided_reasons': dict(Counter(r['result'].get('reason') for r in group if r['result']['L'] == 'undecided'))}


complete = []
for case, group in by_case.items():
    if len(group) == 8 and all(r['result']['exact'] and r['result']['L'] == r['study_N9'] for r in group):
        complete.append({'case': case, 'stratum': group[0]['stratum']})
versions = {}
for row in rows:
    key = json.dumps(row['loaded_source_sha256'], sort_keys=True)
    versions[key] = row['loaded_source_sha256']
summary = {'requested_descriptions': 16, 'requested_queries': 128,
           'rows': len(rows), 'unique_cells': len(seen), 'duplicates': duplicates,
           'by_stratum': {k: profile(v) for k, v in by_stratum.items()},
           'overall': profile(rows), 'numeric_lower_than_N9': numeric_lower,
           'numeric_higher_than_N9': numeric_higher, 'fully_preserved_eight_query_profiles': complete,
           'loaded_source_versions': list(versions.values()),
           'on_disk_source_changed_during_run': any(r['loaded_source_sha256'] != r['source_sha256_at_output'] for r in rows),
           'query_seconds_total': sum(r['result']['stats'].get('seconds', 0) for r in rows),
           'peak_rss_mb': max(r['peak_rss_mb'] for r in rows),
           'depth_results_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'nonclaims': ['Timeouts do not establish persistence or a change.',
                         'Depth results are exact SAT-based recomputation when marked exact; no new independent LRAT certificates are exported.',
                         'The chained sample is purposive, balanced by N9 incidence forest status and filtered by N9 width; direct/slow controls are separate strata. This is not a prevalence estimate.']}
(HERE / 'depth_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
print(json.dumps(summary, sort_keys=True))
