"""Check concrete projected relations with the canonical command."""

import itertools
import json
import subprocess
import sys

from knot_counts import HERE


def words(size):
    return [''.join(word) for word in itertools.product('01', repeat=size)]


def check(label, variables, allowed, expected):
    cnf = '; '.join(' '.join(f'~{name}' if bit == '1' else name for name, bit in zip(variables, word))
                    for word in words(len(variables)) if word not in allowed)
    cli = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf, '--loops', *variables[:-1],
           '--contact', variables[-1], '--json']
    result = json.loads(subprocess.check_output(cli, text=True))
    assert set(result['allowed']) == set(allowed), result
    assert (result['binding'], result['loss_on_erasure'], result['coexistence']) == expected, result
    return {'case': label, 'cnf': cnf, **result}


def main():
    data = json.loads((HERE / 'knot_replay.json').read_text())
    failure = data['failed_knots'][0]['relation']
    assert failure['places'] == [100, 106, 114, 115, 116]
    parent = data['nearest_passing_parent'][0]['relation']
    failed_names = [f'd{d}' for d in failure['places']]
    return [
        check('the five-place join in its grown pattern', failed_names, failure['allowed_words'], (True, False, True)),
        check('the same join read with only its own parity rule', failed_names,
              [word for word in words(5) if word.count('1') % 2 == 0], (True, True, True)),
        check('one parent in the same grown pattern', [f'd{d}' for d in parent['places']], parent['allowed_words'],
              (True, True, True)),
        check('four-place not-all-equal with two additional words forbidden', ['a', 'b', 'c', 'd'],
              [word for word in words(4) if word not in {'0000', '1111', '0011', '1100'}], (True, True, True)),
    ]


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
