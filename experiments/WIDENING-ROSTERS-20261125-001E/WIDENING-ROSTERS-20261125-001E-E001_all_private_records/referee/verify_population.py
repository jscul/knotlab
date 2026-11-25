"""Rebuild the frozen weights from the independent earlier first-meeting records."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys

from check import Stage
from driver import ROOT, compact, physical_key, read_supports, requests


D_FAMILY = Path('WIDENING-ROSTERS-20261125-001D/WIDENING-ROSTERS-20261125-001D-E001_links')
D_SOURCE = ROOT / 'experiments' / D_FAMILY
D_ARTIFACT = ROOT / 'artifacts' / D_FAMILY / 'referee'


def verify():
    sys.path.insert(0, str(D_SOURCE / 'referee'))
    from referee import CENSUS, STARTS, grow, raw_start, read_json

    case_plan = {case['id']: case for case in read_json(D_SOURCE / 'cases.json')}
    named = read_json(STARTS)
    census = read_json(CENSUS)
    events = defaultdict(list)
    event_file = D_ARTIFACT / 'first_meetings.jsonl.gz'
    with gzip.open(event_file, 'rt', encoding='utf-8') as source:
        for line in source:
            row = json.loads(line)
            if row['rule'] == 'MOST':
                events[row['case'], row['kl']].append(row)
    observed = Counter()
    literal_counts = Counter()
    for (case_id, law), meeting_rows in events.items():
        case = case_plan[case_id]
        supports, _, _, _ = grow(raw_start(case['start'], named, census), case, 'MOST', law)
        stage_hashes = {}
        for event in meeting_rows:
            t = event['t']
            if t not in stage_hashes:
                # Row order identifies the knots; places within a row are an unordered set.
                raw = compact([sorted(row) for row in supports[t].places])
                stage_hashes[t] = hashlib.sha256(raw).hexdigest()
            for route in event['routes']:
                u, v = sorted((route['u'], route['v']))
                for c in route['contacts']:
                    observed[law, stage_hashes[t], u, v, c] += 1
                    literal_counts[law] += len(route['a']) * len(route['b'])

    expected = {physical_key(row): row['count'] for row in requests()}
    if observed != expected:
        delta = observed - Counter(expected)
        missing = Counter(expected) - observed
        raise ValueError(f'physical cohort differs: {len(delta)} excess and {len(missing)} missing keys; '
                         f'first excess {next(iter(delta), None)}; first missing {next(iter(missing), None)}')
    e_literals = Counter()
    e_occurrences = Counter()
    systems = {}
    for (law, system, u, v, c), count in expected.items():
        if system not in systems:
            systems[system] = Stage(read_supports(system))
        roles = systems[system].roles(u, v, c)
        e_literals[law] += count * len(roles.a) * len(roles.b)
        e_occurrences[law] += count
    d_summary = read_json(D_ARTIFACT / 'summary.json')['by_rule_and_knot_law']
    for law, count in e_literals.items():
        if count != literal_counts[law] or count != d_summary[f'MOST/{law}']['literal_occurrences']:
            raise ValueError(f'weighted literal coverage disagreement under {law}')
    return {'physical_keys': len(expected), 'distinct_support_stages': len(systems),
            'physical_occurrences_by_law': e_occurrences,
            'weighted_literal_coverage_by_law': e_literals,
            'older_event_sha256': hashlib.sha256(event_file.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as target:
        json.dump(result, target, indent=2)
        target.write('\n')
    print(json.dumps(result, separators=(',', ':')))
