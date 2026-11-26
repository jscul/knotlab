"""Repeat the design-note gate and the dated object searches from the repository root."""
from pathlib import Path
import json
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STUDY = HERE.parent.name
QUERIES = (
    'share of births altered per round two patterns mark damage spreading local growth',
    'fraction of changed births between a growth and a marked growth',
    'how many births change marks joint births mixed table index pairs',
    'earliest changed birth one fewer seven generator cap three switch receiver',
    'ring leftovers cyclic order lap weight local counts',
)
EARLIER = {
    'TWO-PATTERNS-20261126-001': 'Marks and moves in the two-pattern comparison',
    'SHORT-AGAIN-20261126-001': 'Release of the two-generator jam',
    'SWITCH-RECEIVERS-20261126-001': 'Switch of the receiver with three mutually sharing knots',
    'INFLUENCE-CONE-20261120-001': 'Earliest changed birth or fresh count',
    'ORDINARY-DYNAMICS-20261120-001': 'Separate descent of funded parts',
    'RING-GROWTH-20261118-001': 'Ring counts and equal growth rates',
    'RING-IN-BALANCE-20261123-001': 'Local counts on rings and the parity closing exception',
    'DOUBLE-IDENT-20261119-001': 'Which details of a start determine its growth',
}


def track(*args):
    return subprocess.run([sys.executable, '-B', 'scripts/track.py', *args], cwd=ROOT,
                          capture_output=True, text=True)


def search(argument):
    result = track('objects', *argument, '--until', '2026-11-26', '--exclude', STUDY, '--limit', '8', '--json')
    result.check_returncode()
    return [r['id'] for r in json.loads(result.stdout)['index']]


def main():
    start = perf_counter()
    sample = search([QUERIES[0]])
    print(f'One dated search took {perf_counter()-start:.3f} seconds.')
    gate = track('objects-gate', str(HERE.parent/'README.md'))
    data = {
        'design file': '../README.md', 'gate return code': gate.returncode,
        'gate message': (gate.stdout + gate.stderr).strip(),
        'searches (curated index identifiers in returned order)': {
            q: sample if i == 0 else search([q]) for i, q in enumerate(QUERIES)},
        'direct searches of known predecessors': {
            title: search(['--epic', epic]) for epic, title in EARLIER.items()},
    }
    (HERE/'prior_work.json').write_text(json.dumps(data, indent=2) + '\n')


if __name__ == '__main__':
    main()
