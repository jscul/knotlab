"""Look up earlier measurements and read the earlier one-step census directly."""
import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
EARLIER = 'TWO-PATTERNS-20261126-001'
STUDY = 'SHORT-AGAIN-20261126-001'
SAME_RECEIVER = 'g7:122@0'
QUERIES = ['switch', 'cap', 'demand four', 'cone', 'receiver cap demand four cone switch',
           'own births sender receiver site cap', 'funded growth receiver cone changes loose count']


def look_up(query):
    command = [sys.executable, '-B', 'scripts/track.py', 'objects', query, '--until',
               '2026-11-26', '--exclude', STUDY, 'SWITCH-RECEIVERS-20261126-001', '--limit', '20', '--json']
    result = json.loads(subprocess.check_output(command, cwd=ROOT))
    return {key: [row['id'] for row in result[key]] for key in ['index', 'other_epics']}


def previous_census(limit):
    archive = ROOT / 'research' / EARLIER / 'census/census_runs.jsonl.gz'
    cases = defaultdict(dict)
    with gzip.open(archive, 'rt') as stream:
        for line in islice(stream, limit):
            row = json.loads(line)
            if row.get('join') != 'meeting' or row.get('law', [''])[0] != 'CAP-3':
                continue
            for own, other in [('A','B'), ('B','A')]:
                if row[own] != SAME_RECEIVER:
                    continue
                sender = row[other]
                reading = row['reads'][own]
                first = next((r for r, births in enumerate(reading['own births'], 1) if births != r + 2), None)
                count_at_site = int(sender.split(':')[1].split('@')[0][int(sender.split('@')[1])])
                entry = {'rounds':row['rounds'], 'leaves':first, 'site_loose':count_at_site,
                         'own_births':reading['own births'], 'first_vs_stub':reading['stub']}
                by_sender = cases[row['law'][1]]
                if sender in by_sender:
                    assert by_sender[sender] == entry
                by_sender[sender] = entry
    tables = {}
    for treatment, cases_by_sender in cases.items():
        tally = Counter((v['site_loose'], v['leaves']) for v in cases_by_sender.values())
        tables[treatment] = {f'loose={k[0]}, round={k[1]}':v for k,v in tally.items()}
    return {'cases':cases, 'counts':tables}


if __name__ == '__main__':
    options = argparse.ArgumentParser()
    options.add_argument('--pilot',action='store_true')
    args = options.parse_args()
    result = {'queries':{q:look_up(q) for q in (QUERIES[:1] if args.pilot else QUERIES)},
              'previous_one_step_meetings':previous_census(1000 if args.pilot else None),
              'receiver':'Three mutually sharing knots with one, two and two loose distinctions, sited at the first.'}
    if args.pilot:
        print('pilot complete')
    else:
        (OUT / 'earlier_records.json').write_text(json.dumps(result,indent=2)+'\n')
        print(result['previous_one_step_meetings']['counts'])
