"""Ask the canonical checker for the minimum's actual projected four distinctions."""

import argparse
import json
import os
from itertools import product
from pathlib import Path
from subprocess import check_output
from time import perf_counter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PYTHON = ROOT / '.venv' / 'bin' / 'python'
TICKET = HERE.parent.name
DATA = ROOT / 'artifacts' / TICKET / (TICKET + '-E001_closures')
NAMES = 'abcdefghij'


def check(rows, signs, terminal):
    clauses = []
    for support, sign in zip(rows, signs, strict=True):
        for word in product((0, 1), repeat=len(support)):
            if sum(word) % 2 != sign:
                clauses.append(' '.join(('~' if bit else '') + NAMES[i] for i, bit in zip(support, word)))
    used = set().union(*rows)
    command = [str(PYTHON), '-B', '-m', 'knotlab', 'check', '--cnf', ';'.join(clauses),
               '--loops', *[NAMES[i] for i in terminal[:-1]], '--contact', NAMES[terminal[-1]],
               '--witnesses', *[NAMES[i] for i in sorted(used - set(terminal))], '--json']
    result = json.loads(check_output(command, env=dict(os.environ, PYTHONPATH=str(ROOT/'tools')), cwd=ROOT))
    return {key:result[key] for key in ['allowed', 'binding', 'loss_on_erasure', 'coexistence', 'is_knot']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    start = perf_counter()
    minimum = json.loads((DATA/'panels_witnesses.json').read_text())['whole']
    rows = minimum['after_rows']
    terminal = rows[-1]
    assert rows == [[1,6,7,8], [2,3,4,8], [0,3,6,9], [4,5,7,9], [0,1,2,5]]
    cases = [('even_whole', rows, [0,0,0,0,0], 0),
             ('reversed_whole', rows, [0,0,0,0,1], None),
             ('odd_in_isolation', [terminal], [1], 1),
             ('older_equations_only', rows[:-1], [0,0,0,0], 0),
             ('one_older_and_closing_sign_odd', rows, [1,0,0,0,1], 1)]
    checks = {}
    for label, rules, signs, parity in (cases[:1] if args.pilot else cases):
        observed = check(rules, signs, terminal)
        words = {''.join(str(x) for x in bits) for bits in product((0,1), repeat=4)
                 if sum(bits)%2 == parity}
        assert set(observed['allowed']) == words and observed['is_knot'] == bool(words)
        checks[label] = observed
    elapsed = perf_counter() - start
    output = 'allowed_pilot.json' if args.pilot else 'allowed.json'
    (HERE/output).write_text(json.dumps(dict(checks=checks, elapsed_seconds=elapsed), indent=2) + '\n')
    print(len(checks), 'projected relations,', round(elapsed, 3), 'seconds')


if __name__ == '__main__':
    main()
