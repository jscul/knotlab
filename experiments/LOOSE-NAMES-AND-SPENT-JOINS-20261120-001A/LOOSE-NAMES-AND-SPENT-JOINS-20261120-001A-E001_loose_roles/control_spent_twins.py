"""Deductive follow-up on the fixed tables after the spent-input result."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations

from control_measure import OUTPUT, WEIGHTS, read, save
from control_role_rows import signed_table


def revisit(n, measurement, weighting):
    screen = measurement['screen']
    loose = set(screen['actual_loose'])
    old_false = set(screen['surviving_false'])
    total = measurement['total']
    signs = signed_table(n, total, measurement['disagreement_counts'])
    exclusion = []
    for option in screen['predictions']:
        if option['rejections']:
            continue
        mark = option['name']
        for a, b in combinations(option['inputs'], 2):
            if weighting == 'inherited' and signs[a][b] >= 0:
                continue
            if all(signs[a][z] == signs[b][z] for z in range(n) if z not in (a, b)):
                assert mark not in loose, (weighting, option, a, b)
                assert mark in old_false
                exclusion.append({'candidate': mark, 'alleged_input_twins': (a, b),
                                  'signed_correlation': str(Fraction(signs[a][b], total))})
                break
    remaining = old_false - {p['candidate'] for p in exclusion}
    return {'actual_loose': len(loose), 'entering_false': sorted(old_false),
            'excluded': exclusion, 'remaining_false': sorted(remaining)}


def panel(population):
    findings = []
    summary = {}
    for age in (1, 2):
        tallies = {w: Counter() for w in WEIGHTS}
        for draw in population['draws']:
            if len(draw['stages']) < age:
                continue
            stage = draw['stages'][age - 1]
            for w, measurement in stage['weights'].items():
                if 'unread' in measurement:
                    tallies[w]['unread'] += 1
                    continue
                result = revisit(stage['width'], measurement, w)
                findings.append(dict(draw=draw['draw'], age=age, weighting=w, **result))
                tally = tallies[w]
                tally['observed_draws'] += 1
                tally['actual_loose_indices'] += result['actual_loose']
                for tag, field in (('entering_false', 'entering_false'), ('excluded', 'excluded'),
                                   ('remaining_false', 'remaining_false')):
                    tally[f'draws_with_{tag}'] += bool(result[field])
                    tally[f'{tag}_indices'] += len(result[field])
        summary[age] = tallies
    return dict(summary=summary, findings=findings)


def main():
    panels = read(OUTPUT / 'control_panels.json.gz')['nae']
    selection = read(OUTPUT / 'control_target.json')
    target_width = selection['selected_key'][0]
    output = dict(scope='Deduction on the same earlier observations. No new draws.',
                  rule={'uniform': 'equal exterior rows',
                        'inherited': 'equal exterior rows and strictly negative mutual signed correlation'},
                  prior_panel_sha256=sha256((OUTPUT / 'control_panels.json.gz').read_bytes()).hexdigest(),
                  target={w: revisit(target_width, selection['weights'][w], w) for w in WEIGHTS},
                  panels={name: panel(v) for name, v in panels.items()})
    save(OUTPUT / 'control_spent_twins.json', output)
    for name, groups in output['panels'].items():
        print(name, groups['summary'], flush=True)
    print('target', output['target'], flush=True)


if __name__ == '__main__':
    main()
