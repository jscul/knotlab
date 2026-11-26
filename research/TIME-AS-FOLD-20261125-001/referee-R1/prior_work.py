"""Repeat the frozen searches and retain references for the comparisons of credit."""
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
study = here.parent.name
prereg = Path('research', study + 'A', 'preregistration.md')
tracking = [sys.executable, '-B', 'scripts/track.py']
section = (root / prereg).read_text().split('## Prior work in the program\n')[1].split('\n## ')[0]
registered = re.findall(r'track\.py objects "([^"]+)"', section)
assert len(registered) == 3
queries = [*registered, 'two children per tick', 'two pulses broken clock supplied start']
gate = subprocess.run(tracking + ['objects-gate', str(prereg)], cwd=root, text=True, capture_output=True, check=True)
searches = []
for query in queries:
    cmd = tracking + ['objects', query, '--until', '2026-11-25', '--exclude', study, '--json']
    result = json.loads(subprocess.check_output(cmd, cwd=root, text=True))
    searches.append({'query': query, 'highest_three_indexed': [
        {'id': r['id'], 'object': r['object'], 'record': r['record']} for r in result['index'][:3]
    ]})
print(json.dumps({'gate': gate.stdout.strip(), 'searches': searches}, indent=2))
