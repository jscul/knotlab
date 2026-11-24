"""Run 6: Ring(5, 3) under (RATION-4, CANCEL-OFFSHOOT) and (RATION-4, CANCEL-RETIRE), 12 rounds, cut off past
20,000 knots: the parts of seven and nine members that return, described (deviations.md C13): each sameness class with
its count, first (s, t), members with h and k, inclusion-maximal met sets with their common knots, the parts given off,
whether it copies itself, and the births of one period that descend from it.  Writes run6.json and run6_trace.txt."""
import os
from collections import Counter

from cpcommon import E, OUT, log, part_detail, part_shape, resources, shape_key, write

R = 12
CAP = 20000
LAWS = (E.Law('RATION-4', 'CANCEL-OFFSHOOT'), E.Law('RATION-4', 'CANCEL-RETIRE'))


def period_trace(run, s, t, Y):
    labels = {u: 0 for u in Y}
    anc = dict(run.ancestry(s, labels))
    rows = []
    for tt in range(s + 1, t + 1):
        prev = set(anc[tt - 1])
        rec = run.records[tt - 1]
        bs = [b for b in rec['births'] if any(p in prev for p in b['parents'])]
        rt = run.rosters[tt]
        parts = sorted({rt.part_of[x] for x in anc[tt]})
        rows.append({'round': tt,
                     'short': [u for u in rec['short'] if u in prev],
                     'cancelled': [g for g in rec['cancelled'] if set(g) & prev],
                     'waiting': [u for u in rec['waiting'] if u in prev],
                     'retired': [u for u in rec['retired'] if u in prev],
                     'births': [{'id': b['id'], 'kind': b['kind'], 'parents': b['parents'], 'D': b['D'], 'f': b['f']}
                                for b in bs],
                     'parts_after': [{'members': list(rt.parts[j]), 'shape': part_shape(rt, rt.parts[j])}
                                     for j in parts]})
    return rows


def describe(run):
    rets = [r for r in run.find_returns() if r['part_size'] in (7, 9)]
    classes = []          # (rep s, rep Y, record)
    for r in rets:
        ros = run.rosters[r['s']]
        Y = tuple(r['part'])
        sh = part_shape(ros, Y)
        cls = None
        for c in classes:
            if c['shape_key'] == shape_key(sh) and run.cache.same(run.rosters[c['s']], tuple(c['Y']), ros, Y):
                cls = c
                break
        rt = run.rosters[r['t']]
        same_off = [run.cache.same(ros, Y, rt, tuple(P)) for P in r['off_parts']]
        if cls is None:
            cls = {'shape_key': shape_key(sh), 'shape': sh, 's': r['s'], 'Y': list(Y), 'count': 0,
                   'periods': Counter(), 'n_off': Counter(), 'off_shapes': Counter(), 'copies': 0,
                   'first': {'s': r['s'], 't': r['t'], 'period': r['period'], 'detail': part_detail(run, r['s'], Y),
                             'returned_as': part_detail(run, r['t'], r['same_part']),
                             'off': [dict(part_detail(run, r['t'], P), shape=part_shape(rt, P), same_as_Y=sm)
                                     for P, sm in zip(r['off_parts'], same_off)],
                             'trace': period_trace(run, r['s'], r['t'], Y)}}
            classes.append(cls)
        cls['count'] += 1
        cls['periods'][r['period']] += 1
        cls['n_off'][r['n_off']] += 1
        for P, sm in zip(r['off_parts'], same_off):
            cls['off_shapes'][shape_key(part_shape(rt, P)) + (' [same]' if sm else '')] += 1
        cls['copies'] += int(any(same_off))
    for c in classes:
        for k in ('periods', 'n_off', 'off_shapes'):
            c[k] = {str(a): b for a, b in sorted(c[k].items())}
    return rets, classes


def text(law, run, classes, lines):
    lines.append('=' * 100)
    lines.append('Ring(5, 3) under %s: %d rounds, %d knots; returns of parts of 7 or 9 members: %d, in %d sameness '
                 'classes' % (law.name(), run.rounds_done, run.S.n_knots, sum(c['count'] for c in classes),
                              len(classes)))
    for c in classes:
        f = c['first']
        lines.append('-- class %s: %d returns, periods %s, parts off %s, copies itself in %d' % (
            c['shape_key'], c['count'], c['periods'], c['n_off'], c['copies']))
        lines.append('   first: after round %d, returns at %d' % (f['s'], f['t']))
        lines.append('   members (id, h, k): %s' % f['detail']['members'])
        lines.append('   met sets: %s' % ['%s via %s' % (m['members'], m['common_knots']) for m in f['detail']['met_sets']])
        lines.append('   returned as: %s; met sets %s' % (f['returned_as']['members'],
                                                          [m['members'] for m in f['returned_as']['met_sets']]))
        for o in f['off']:
            lines.append('   part given off: %s %s%s' % (shape_key(o['shape']), o['members'],
                                                       ' [same as Y]' if o['same_as_Y'] else ''))
        lines.append('   parts off over all returns of this class: %s' % c['off_shapes'])
        for row in f['trace']:
            lines.append('   round %d: short %s, cancelled %s, waiting %s, retired %s' % (
                row['round'], row['short'], row['cancelled'], row['waiting'], row['retired']))
            for b in row['births']:
                lines.append('      birth %d %s parents %s D=%d f=%d' % (b['id'], b['kind'], b['parents'], b['D'],
                                                                         b['f']))
            lines.append('      parts after: %s' % ['%s %s' % (p['members'], shape_key(p['shape']))
                                                    for p in row['parts_after']])


def main():
    out = {'R': R, 'cap': CAP, 'runs': {}}
    lines = ['Run 6 of COPYING-PARTS-20261123-001A-E001: the returning parts of seven and nine members on Ring(5, 3) '
             'under RATION-4.', 'Shapes: n members, sorted h, sorted k, sorted sizes of the inclusion-maximal met sets.']
    for law in LAWS:
        run = E.Run(E.ring(5, 3), law, R, knot_cap=CAP)
        rets, classes = describe(run)
        all_rets = run.find_returns()
        out['runs'][law.name()] = {
            'rounds_done': run.rounds_done, 'cut_off': run.cut_off, 'knots': run.S.n_knots, 'kind': run.kind(),
            'n_returns': len(all_rets), 'return_sizes': dict(sorted(Counter(r['part_size'] for r in all_rets).items())),
            'n_returns_7_or_9': len(rets), 'classes': classes,
            'trace': [{k: row[k] for k in ('round', 'members', 'parts', 'births', 'n_knots') if k in row}
                      for row in run.trace()]}
        text(law, run, classes, lines)
        log(law.name(), 'rounds', run.rounds_done, 'knots', run.S.n_knots, 'returns', len(all_rets), 'sizes',
            out['runs'][law.name()]['return_sizes'], '7/9:', len(rets), 'classes',
            [(c['shape_key'], c['count'], c['periods'], c['copies']) for c in classes])
    with open(os.path.join(OUT, 'run6_trace.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    out['resources'] = resources()
    write('run6.json', out)


if __name__ == '__main__':
    main()
