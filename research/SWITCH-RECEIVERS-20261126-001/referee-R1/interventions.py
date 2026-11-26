"""Check the claimed cutoff at additional distances with the same marked sender."""
import argparse
import json
from pathlib import Path
import time

from growth import grow, mutual_three

HERE = Path(__file__).resolve().parent
TWO_LOOSE = 'g3:22@0'


def compared(left, right):
    return {
        'through': min(len(left), len(right)),
        'first_count': next((i for i, (x, y) in enumerate(zip(left, right), 1)
                             if x.own_births != y.own_births), None),
        'first_strict': next((i for i, (x, y) in enumerate(zip(left, right), 1)
                              if x.own_signature != y.own_signature), None),
    }


def one(k, d, *, rounds=16, bound=3000, marks=None):
    start = mutual_three(k - 2)
    law = f'CAP-{k}'
    settings = {'rounds': rounds, 'bound': bound}
    baseline = grow(start, TWO_LOOSE, d, law, **settings)
    stub = grow(start, 'stub', d, law, **settings)
    trials = []
    for t0 in (range(d + 2) if marks is None else marks):
        marked = grow(start, TWO_LOOSE, d, law, mark_after=t0, **settings)
        trials.append({'mark_after': t0, 'first_round_with_mark': t0 + 1,
                       'against_unmarked': compared(baseline, marked),
                       'against_stub': compared(stub, marked)})
    return {'cap': k, 'steps': d, 'round_limit': rounds, 'knot_limit': bound, 'unmarked_against_stub': compared(baseline, stub), 'trials': trials}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true', help='same 16 rounds and 3,000 knots, one distance per cap')
    opts = parser.parse_args()
    start_time = time.monotonic()
    rows = [one(k, d) for k in range(3, 8) for d in ((3,) if opts.pilot else (2, 3, 4, 5))]
    last_cell = one(7, 5, rounds=11, bound=16000, marks=(2,) if opts.pilot else range(7))
    output = {'raised_bound_for_last_cell': last_cell, 'round_limit': 16, 'knot_limit': 3000, 'seconds': round(time.monotonic() - start_time, 3), 'rows': rows}
    if not opts.pilot:
        (HERE / 'interventions.json').write_text(json.dumps(output, indent=2) + '\n')
    for row in rows:
        print(row['cap'], row['steps'], 'baseline', row['unmarked_against_stub'],
              'changed', [(t['mark_after'], t['against_unmarked']['first_strict'], t['against_unmarked']['through'],
                           t['against_stub']['first_strict']) for t in row['trials']])
    print('seconds', output['seconds'])
