"""Separate the public pair observation from the archive's physical reference."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PRIOR = 'LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A'
ARCHIVE = ROOT / 'artifacts' / PRIOR / (PRIOR + '-E001_loose_roles')
DRAW_HASH = '50f6399c8dc8a2c02ed880263386b15a7833e7608a64f0ecf38cf48f3b22860d'
ROLE_HASH = 'de777a15d07372849c00fbd743e11ca4a651dd1053b5af28116b0408e3a5b81f'


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')
    return sha256(path.read_bytes()).hexdigest()


def main():
    draw_path, role_path = ARCHIVE / 'control_panels.json.gz', ARCHIVE / 'control_spent_twins_all_signs.json'
    assert sha256(draw_path.read_bytes()).hexdigest() == DRAW_HASH
    assert sha256(role_path.read_bytes()).hexdigest() == ROLE_HASH
    with gzip.open(draw_path, 'rt') as stream:
        draws = json.load(stream)['nae']['explosive']['draws']
    roles = json.loads(role_path.read_text())['panels']['explosive']['draws']
    by_draw = {trial['draw']: trial for trial in draws}
    assert set(by_draw) == set(range(1, 33))
    eligible = []
    for record in sorted(roles, key=lambda entry: (entry['age'], entry['draw'])):
        index, age = record['draw'], record['age']
        if by_draw[index]['attempts'][age - 1] == 'births' and record['remaining_false']:
            eligible.append((index, age, record['remaining_false']))
    index, age, false_indices = eligible[0]
    trial = by_draw[index]
    stage = trial['stages'][age - 1]
    actual_loose = [x for x in range(stage['width']) if sum(x in h for h in stage['rows']) == 1]
    assert not set(false_indices).intersection(actual_loose)
    digests = {}
    for weighting in ('inherited', 'uniform'):
        row = stage['weights'][weighting]
        exact = [str(Fraction(count, row['total'])) for count in row['disagreement_counts']]
        assert len(exact) == stage['width'] * (stage['width'] - 1) // 2
        digests[weighting] = write(OUT / f'target_{weighting}.json', exact)
    result = dict(selection_order='age then original draw, ascending', draw=index, age=age,
                  eligible_by_age={a: sum(x[1] == a for x in eligible) for a in (1, 2)},
                  survived_spent_indices=false_indices, source=trial['source_rows'], source_draw=trial['indexed_pattern'],
                  width=stage['width'], stage=stage['rows'], limits=stage['limits'], loose=actual_loose,
                  next_status=stage['next_status'], next_count=stage['next_count'], profile=stage['profile'],
                  source_permutation=trial['source_permutation'], table_sha256=digests)
    write(OUT / 'reference.json', result)
    print(index, age, stage['width'], false_indices, digests)


if __name__ == '__main__':
    main()
