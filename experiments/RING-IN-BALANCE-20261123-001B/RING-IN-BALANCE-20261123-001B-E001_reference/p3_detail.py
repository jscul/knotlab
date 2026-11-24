"""P3 over the census in full detail: every census run with a return giving parts off is computed again with the engine
(job.py's parameters), with every such return listed, and its compact record is checked to be identical to the census
record.  For each return: rounds, size of the returning part, parts off, whether every member of the copy waited in
the round of the return, whether the part is ring-like (a cycle of met pairs) and whether it is the ring itself
(ring-like with every member holding the same h and k).  Writes p3_census_detail.json."""
from census_io import law_view, load_census
from bref import E, census_stars, log, resources, run_record, write
import job

LAWS = dict((n, l) for n, l in (('ordinary', E.ORDINARY), ('two', E.TWO_ADDED), ('three', E.THREE_ADDED)))


def main():
    census, state = load_census()
    if census is None:
        raise SystemExit('census not complete: ' + state)
    todo = []
    for s in census['starts']:
        if s.get('set_aside') or s.get('timeout'):
            continue
        for lname in LAWS:
            v = law_view(s, lname)
            if v is not None and v['n_off'] > 0:
                todo.append((s, lname))
    log('runs with a return giving parts off:', len(todo))
    out = {'runs': [], 'mismatches': []}
    for s, lname in todo:
        c = s['laws'][lname]
        rounds = c['rounds_completed'] if c.get('not_completed') else job.R
        S = E.from_stars(census_stars(s['g'], s['loose']))
        run = E.Run(S, LAWS[lname], rounds, knot_cap=job.CAP)
        rr = run_record(run, keep_all_off=True)
        mine = job.compact_run(rr)
        ref = dict(law_view(s, lname))
        ref.pop('ord', None)
        if mine != ref:
            out['mismatches'].append({'g': s['g'], 'loose': s['loose'], 'law': lname})
        rets = []
        for d in rr['off_all']:
            sh = d['shape']
            uniform = len(set(zip(sh['h'], sh['k']))) == 1
            rets.append({'s': d['s'], 't': d['t'], 'size': d['part_size'], 'n_off': d['n_off'],
                         'off_sizes': d['off_sizes'], 'copy_all_waited': d['copy_all_waited'],
                         'copy_n_waited': d['copy_n_waited'], 'y_all_waited': d['y_all_waited_in_s'],
                         'ring_like': d['ring_like'], 'ring_itself': d['ring_like'] and uniform,
                         'h': sh['h'], 'k': sh['k'], 'metsets': sh['metset_sizes']})
        out['runs'].append({'g': s['g'], 'n': s['n'], 'loose': s['loose'], 'dead': s['dead'],
                            'members': s['members'], 'law': lname, 'returns': rets})
    out['n_runs'] = len(out['runs'])
    out['n_mismatches'] = len(out['mismatches'])
    out['resources'] = resources()
    log('done; mismatches with the census records:', out['n_mismatches'])
    write('p3_census_detail.json', out)


if __name__ == '__main__':
    main()
