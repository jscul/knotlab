"""Replay the stronger inherited spent-input condition on the frozen draws."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations

from control_measure import OUTPUT, read, save
from control_role_rows import signed_table


def inspect(measurement, width, earlier):
    screen = measurement['screen']
    loose = set(screen['actual_loose'])
    already_excluded = {row['candidate'] for row in earlier['excluded']}
    candidates = set(earlier['entering_false'])
    assert candidates == set(screen['surviving_false'])
    total = measurement['total']
    signs = signed_table(width, total, measurement['disagreement_counts'])
    negative = set()
    extra = []
    for option in screen['predictions']:
        if option['rejections']:
            continue
        twin_pairs = [(a, b) for a, b in combinations(option['inputs'], 2)
                      if all(signs[a][z] == signs[b][z] for z in range(width) if z not in (a, b))]
        if not twin_pairs:
            continue
        x = option['name']
        assert x not in loose and x in candidates
        if any(signs[a][b] < 0 for a, b in twin_pairs):
            negative.add(x)
        else:
            a, b = twin_pairs[0]
            extra.append({'candidate': x, 'alleged_input_twins': (a, b),
                          'mutual_correlation': str(Fraction(signs[a][b], total))})
    assert negative == already_excluded
    residual = candidates - negative - {row['candidate'] for row in extra}
    return {'actual_loose': len(loose), 'earlier_residual': earlier['remaining_false'],
            'additional_exclusions': extra, 'remaining_false': sorted(residual)}


def panel(physical, earlier):
    previous = {(row['draw'], row['age']): row for row in earlier['findings'] if row['weighting'] == 'inherited'}
    counts = {a: Counter({k: 0 for k in ('additional_exclusions', 'draws_with_additional_exclusions',
                                         'remaining_false_indices', 'draws_with_remaining_false')})
              for a in (1, 2)}
    records = []
    for draw in physical['draws']:
        for stage in draw['stages']:
            a = stage['age']
            result = inspect(stage['weights']['inherited'], stage['width'], previous[draw['draw'], a])
            records.append(dict(draw=draw['draw'], age=a, **result))
            counts[a]['draws'] += 1
            counts[a]['true_loose_indices_retained'] += result['actual_loose']
            for field, count, occurrences in (
                ('earlier_residual', 'earlier_residual_indices', 'draws_with_earlier_residual'),
                ('additional_exclusions', 'additional_exclusions', 'draws_with_additional_exclusions'),
                ('remaining_false', 'remaining_false_indices', 'draws_with_remaining_false'),
            ):
                counts[a][count] += len(result[field])
                counts[a][occurrences] += bool(result[field])
    return {'summary': counts, 'draws': records}


def main():
    path = OUTPUT / 'control_spent_twins.json'
    old = read(path)
    raw_path = OUTPUT / 'control_panels.json.gz'
    prior_sha = sha256(path.read_bytes()).hexdigest()
    raw_sha = sha256(raw_path.read_bytes()).hexdigest()
    assert raw_sha == old['prior_panel_sha256']
    data = read(raw_path)['nae']
    panels = {name: panel(v, old['panels'][name]) for name, v in data.items()}
    save(OUTPUT / 'control_spent_twins_all_signs.json',
         {'weighting': 'inherited', 'post_proof': True, 'prior_negative_replay_sha256': prior_sha,
          'fixed_draws_sha256': raw_sha, 'panels': panels})
    for name, result in panels.items():
        print(name, result['summary'], flush=True)


if __name__ == '__main__':
    main()
