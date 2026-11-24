"""B3's share of ticket A's A4, rerun with the engine (no result file of ticket A is read): Ring(n, 3), n = 5, 7, 9,
under the 70 laws of engine.a4_laws() (the list of ticket A's pre-registration), R = 16, cut off past 6,000 knots.
For every return giving parts off: the members of the copy and whether each waited in the round of the return
(deviations.md B4).  Evidence for P3.  Writes b3_a4.json."""
from bref import E, has_waiting, log, resources, run_record, write

R = 16
CAP = 6000


def main():
    out = {'runs': {}}
    for n in (5, 7, 9):
        for law in E.a4_laws():
            run = E.Run(E.ring(n, 3), law, R, knot_cap=CAP)
            rec = run_record(run, keep_all_off=True)
            rec.update({'start': 'Ring(%d,3)' % n, 'n': n, 'law_name': law.name(), 'law': law.to_dict(),
                        'waiting_law': has_waiting(law)})
            key = 'Ring(%d,3)|%s' % (n, law.name())
            out['runs'][key] = rec
            log(key, rec['kind'], 'rounds', rec['rounds_done'], 'knots', rec['knots'], 'off-returns',
                rec['n_off_returns'], 'cut' if rec['cut_off'] else '')
    out['resources'] = resources()
    write('b3_a4.json', out)


if __name__ == '__main__':
    main()
