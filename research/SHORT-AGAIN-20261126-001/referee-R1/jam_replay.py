"""Replay and trace the meeting's 3+ hearing with no waiting own knot."""

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from growth import Growth, build, first_difference, grow


STUDY = Path(__file__).resolve().parent.parent
A, B = 'g7:122@0', 'g7:112@0'
RECORD, MADE = 'REC-ONE-FEWER', 'ONE-FEWER'
WAIT, RETIRE = 'CANCEL-WAIT', 'CANCEL-RETIRE'
BAR = ('B', 2, -1)


def designations(run):
    names = {i: name for i, name in enumerate(run.names) if run.born[i] == 0}
    for row in run.rows:
        repeated = Counter()
        for birth in row.birth_records:
            parents = tuple(sorted(names[i] for i in birth.parents))
            name = ','.join(parents)
            if len(parents) == 1:
                names[birth.id] = f'offshoot({name})#{repeated[parents] + 1}'
                repeated[parents] += 1
            else:
                names[birth.id] = f'join({name})'
    return names


def trace(run, round_no):
    labels = designations(run)
    row = run.rows[round_no - 1]
    return {
        'members': {labels[u]: [row.owed[u], row.available[u], sorted(run.roles[u])] for u in row.available},
        'groups': [{'knots': sorted(labels[u] for u in group), 'kept': group in row.kept} for group in row.groups],
        'births': {labels[b.id]: [b.demand, b.fresh, sorted(run.roles[b.id])] for b in row.birth_records},
    }


def read(run, includes_mixed=False):
    if includes_mixed:
        return [sum('A' in run.roles[b.id] for b in row.birth_records) for row in run.rows]
    return [len(row.own_births) for row in run.rows]


def describe(whole, changed):
    heard = first_difference(whole, changed)
    count_with_a = next((r for r, (a, b) in enumerate(zip(read(whole, True), read(changed, True)), 1)
                        if a != b), None)

    def ancestry_read(run, row):
        return sorted((run.names[b.id], b.fresh, b.places) for b in row.birth_records if 'A' in run.roles[b.id])

    births_with_a = next((a.round for a, b in zip(whole.rows, changed.rows)
                          if ancestry_read(whole, a) != ancestry_read(changed, b)), None)
    return {
        'first difference by strict own births': heard,
        'first birth difference including every birth with receiver ancestry': births_with_a,
        'first count difference including every birth with receiver ancestry': count_with_a,
        'baseline strict own births': read(whole),
        'changed strict own births': read(changed),
        'baseline short by round': [row.a_short for row in whole.rows],
        'changed short by round': [row.a_short for row in changed.rows],
        'baseline short with receiver ancestry by round': [sum('A' in whole.roles[i] for i in row.short)
                                                          for row in whole.rows],
        'changed short with receiver ancestry by round': [sum('A' in changed.roles[i] for i in row.short)
                                                         for row in changed.rows],
    }


def observed_case(distance, join, ration, treatment, receiver=A, sender=B):
    suffix = {'meeting': '_meeting_sample', 'share': '_share_sample'}[join]
    if (distance, join) == (3, 'meeting'):
        suffix = '_meeting'
    path = STUDY / f'jam_d{distance}{suffix}.jsonl.gz'
    with gzip.open(path, 'rt') as stream:
        for line in stream:
            row = json.loads(line)
            if (row['A'], row['B'], row['law']) == (receiver, sender, [ration, treatment]):
                return row
    raise AssertionError((distance, join, ration, treatment))


def compare_record(record, whole, changed, name, limit):
    n = min(limit, record['rounds'])
    assert len(whole.rows) == n
    for key, field in [('births', 'births'), ('A members', 'a_members'), ('A short', 'a_short'),
                       ('A shortfall', 'a_shortfall'), ('shortfall', 'shortfall')]:
        assert [getattr(row, field) for row in whole.rows] == record[key][:n]
    assert read(whole) == record['own births'][:n]
    if limit == 12:
        assert whole.rows[-1].knots == record['knots']
        assert (whole.stop or 'rounds') == record['ended']
    target = next(c for c in record['changes'] if c['at'] == name)
    common = min(len(whole.rows), len(changed.rows))
    assert common == min(limit, target['rounds'])
    expected = target['heard']
    assert first_difference(whole, changed) == (expected if expected and expected <= common else None)
    if expected:
        assert read(changed) == target['own births with'][:limit]
        assert [row.a_short for row in changed.rows] == target['A short with'][:limit]
    return {'matched recorded baseline rounds': n, 'matched comparison horizon': common}


def ring_sender_control(rounds):
    ration = 'JOIN-FEWER'
    whole = grow(build('source', 'ring', 3), ration, WAIT, rounds, 1500, trace=True)
    changed = grow(build('source', 'ring', 3, change=('B', 0, -1)), ration, WAIT, rounds, 1500, trace=True)
    observed = observed_case(3, 'meeting', ration, WAIT, 'source', 'ring')
    return {
        **compare_record(observed, whole, changed, 'bB0', rounds),
        'first difference': first_difference(whole, changed),
        'baseline receiver short and members': [[r.a_short, r.a_members] for r in whole.rows],
        'changed receiver short and members': [[r.a_short, r.a_members] for r in changed.rows],
        'baseline ring own births': [len(r.b_births) for r in whole.rows],
        'changed ring own births': [len(r.b_births) for r in changed.rows],
    }


def check(rounds, only_exception):
    arms = [
        ('exception', 2, 'meeting', RECORD, WAIT, None, BAR, 'bB2'),
        ('same change under the made ration', 2, 'meeting', MADE, WAIT, None, BAR, 'bB2'),
        ('opposite sign at the same knot', 2, 'meeting', RECORD, WAIT, None, ('B', 2, 1), 'B2'),
        ('short knots retire', 2, 'meeting', RECORD, RETIRE, None, BAR, None),
        ('cap of three', 2, 'meeting', 'CAP-3', WAIT, None, BAR, 'bB2'),
        ('cap of five', 2, 'meeting', 'CAP-5', WAIT, None, BAR, None),
        ('other receiver joining knot', 2, 'meeting', RECORD, WAIT, 1, BAR, None),
        ('shared distinction at two steps', 2, 'share', RECORD, WAIT, None, BAR, None),
        ('one more link knot', 3, 'meeting', RECORD, WAIT, None, BAR, 'bB2'),
        ('three more link knots', 5, 'meeting', RECORD, WAIT, None, BAR, 'bB2'),
        ('shared distinction at three steps', 3, 'share', RECORD, WAIT, None, BAR, 'bB2'),
    ]
    out = {'receiver': A, 'sender': B, 'round limit': rounds, 'knot bound': 1500, 'arms': {}}
    for label, distance, join, ration, treatment, site, change, recorded in arms[:1] if only_exception else arms:
        whole = grow(build(A, B, distance, join, site_a=site), ration, treatment, rounds, 1500, trace=True)
        changed = grow(build(A, B, distance, join, site_a=site, change=change),
                       ration, treatment, rounds, 1500, trace=True)
        result = describe(whole, changed)
        result['configuration'] = {'d': distance, 'join': join, 'ration': ration, 'treatment': treatment,
                                   'alternative receiver joining knot': site, 'change': change}
        if recorded:
            row = observed_case(distance, join, ration, treatment)
            result.update(compare_record(row, whole, changed, recorded, rounds))
        if label == 'exception':
            assert result['first difference by strict own births'] == 3
            assert (whole.rows[2].a_short, changed.rows[2].a_short) == (0, 0)
            assert (whole.rows[1].a_short, changed.rows[1].a_short) == (1, 1)
            result['unchanged trace, first three rounds'] = [trace(whole, r) for r in range(1, 4)]
            result['barred trace, first three rounds'] = [trace(changed, r) for r in range(1, 4)]
            patched = Growth(build(A, B, 2, change=BAR), RECORD, WAIT, trace=True)
            assert patched.step()
            birth = next(b for b in patched.rows[0].birth_records if len(b.parents) == 3 and patched.roles[b.id] == {'B'})
            assert (birth.demand, birth.fresh) == (1, 0)
            patched.mark(birth.id)
            patched.run(rounds, 1500)
            result['changed arm giving that one three-parent birth one loose distinction'] = describe(whole, patched)
        out['arms'][label] = result
    if not only_exception:
        out['barring the ring joining knot under JOIN-FEWER'] = ring_sender_control(rounds)
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, choices=range(3, 13), default=12)
    parser.add_argument('--only-exception', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    results = check(args.rounds, args.only_exception)
    if args.output:
        args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
    for label, arm in results['arms'].items():
        print(label, arm['first difference by strict own births'])
